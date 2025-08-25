import torch
import torch.nn as nn
from typing import Tuple

# 将9x9棋盘编码为序列(81)，token=0..9，其中0表示空

class PositionalEncoding(nn.Module):
    def __init__(self, d_model: int, max_len: int = 200):
        super().__init__()
        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2).float() * (-torch.log(torch.tensor(10000.0)) / d_model))
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        self.register_buffer('pe', pe.unsqueeze(0))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x: [B, T, D]
        x = x + self.pe[:, :x.size(1)]
        return x

class SudokuTransformer(nn.Module):
    def __init__(self, vocab_size: int = 10, d_model: int = 256, nhead: int = 8, num_layers: int = 6, dim_feedforward: int = 512):
        super().__init__()
        self.vocab_size = vocab_size
        self.d_model = d_model

        self.src_embed = nn.Embedding(vocab_size, d_model)
        self.tgt_embed = nn.Embedding(vocab_size, d_model)
        self.pos_enc = PositionalEncoding(d_model, max_len=100)

        self.transformer = nn.Transformer(d_model=d_model, nhead=nhead, num_encoder_layers=num_layers,
                                          num_decoder_layers=num_layers, dim_feedforward=dim_feedforward, batch_first=True)
        self.out = nn.Linear(d_model, vocab_size)

    def forward(self, src_tokens: torch.Tensor, tgt_tokens: torch.Tensor) -> torch.Tensor:
        # src_tokens, tgt_tokens: [B, T]
        src = self.pos_enc(self.src_embed(src_tokens))
        tgt = self.pos_enc(self.tgt_embed(tgt_tokens))

        # 生成因果mask给decoder
        T = tgt_tokens.size(1)
        causal_mask = torch.triu(torch.ones(T, T, device=tgt_tokens.device) * float('-inf'), diagonal=1)

        out = self.transformer(src, tgt, tgt_mask=causal_mask)
        logits = self.out(out)  # [B, T, vocab]
        return logits

    def generate(self, src_tokens: torch.Tensor, max_len: int = 81) -> torch.Tensor:
        # 自回归生成解序列
        B = src_tokens.size(0)
        ys = torch.zeros(B, 1, dtype=torch.long, device=src_tokens.device)  # 从0 token开始（可用作起始符）
        for _ in range(max_len):
            logits = self.forward(src_tokens, ys)
            next_token = torch.argmax(logits[:, -1, :], dim=-1, keepdim=True)
            ys = torch.cat([ys, next_token], dim=1)
        return ys[:, 1:]


def board_to_tokens(board) -> torch.Tensor:
    # board: list[list[int]] 9x9 -> tensor [81]
    seq = []
    for r in range(9):
        for c in range(9):
            v = board[r][c]
            seq.append(v)
    return torch.tensor(seq, dtype=torch.long)


def tokens_to_board(tokens: torch.Tensor):
    # tokens: [81]
    out = [[0 for _ in range(9)] for _ in range(9)]
    idx = 0
    for r in range(9):
        for c in range(9):
            out[r][c] = int(tokens[idx].item())
            idx += 1
    return out
