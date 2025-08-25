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

    @staticmethod
    def _idx_to_rc(idx: int) -> Tuple[int, int]:
        r = idx // 9
        c = idx % 9
        return r, c

    @staticmethod
    def _allowed_digits_for_cell(givens_row: torch.Tensor, givens_col: torch.Tensor, givens_box: torch.Tensor,
                                 pred_row: torch.Tensor, pred_col: torch.Tensor, pred_box: torch.Tensor,
                                 r: int, c: int, given_val: int) -> torch.Tensor:
        """
        返回长度10的布尔向量(0/1 float)，1表示该token允许；这里将0（空）也屏蔽。
        若该位置是题面给定(given_val>0)，仅允许该数字。
        否则允许1..9中未在同一行、列、宫出现的数字。
        """
        mask = torch.zeros(10, dtype=torch.float32, device=givens_row.device)
        if given_val > 0:
            mask[given_val] = 1.0
            return mask
        # 收集已出现的数
        used = torch.zeros(10, dtype=torch.bool, device=givens_row.device)
        # 行/列/宫中来自题面与已预测的数字
        for d in range(1, 10):
            if givens_row[r, d] or pred_row[r, d]:
                used[d] = True
            if givens_col[c, d] or pred_col[c, d]:
                used[d] = True
        b = (r // 3) * 3 + (c // 3)
        for d in range(1, 10):
            if givens_box[b, d] or pred_box[b, d]:
                used[d] = True
        # 允许未使用的1..9
        for d in range(1, 10):
            if not used[d]:
                mask[d] = 1.0
        return mask

    def generate_with_constraints(self, src_tokens: torch.Tensor, max_len: int = 81) -> torch.Tensor:
        """
        约束解码：逐步生成，每步屏蔽与题面和当前部分预测冲突的数字（行/列/宫），并屏蔽token=0。
        src_tokens: [B, 81]
        返回: [B, 81]
        """
        device = src_tokens.device
        B = src_tokens.size(0)
        # 初始化解序列，以0作为BOS
        ys = torch.zeros(B, 1, dtype=torch.long, device=device)

        # 预处理题面给定的计数表 one-hot 统计: [B, 9(or 10)]
        # 我们使用维度10，索引1..9有效
        givens_row = torch.zeros(B, 9, 10, dtype=torch.bool, device=device)
        givens_col = torch.zeros(B, 9, 10, dtype=torch.bool, device=device)
        givens_box = torch.zeros(B, 9, 10, dtype=torch.bool, device=device)
        given_vals = src_tokens.view(B, 9, 9)
        for b in range(B):
            for r in range(9):
                for c in range(9):
                    v = int(given_vals[b, r, c].item())
                    if v > 0:
                        givens_row[b, r, v] = True
                        givens_col[b, c, v] = True
                        box_idx = (r // 3) * 3 + (c // 3)
                        givens_box[b, box_idx, v] = True

        # 预测中已放置的数字统计
        pred_row = torch.zeros_like(givens_row)
        pred_col = torch.zeros_like(givens_col)
        pred_box = torch.zeros_like(givens_box)

        # 维护一个当前预测棋盘
        pred_board = torch.zeros(B, 81, dtype=torch.long, device=device)

        for t in range(max_len):
            logits = self.forward(src_tokens, ys)  # [B, t+1, vocab]
            step_logits = logits[:, -1, :]        # [B, vocab]

            # 计算该位置的(r,c)与题面给定
            r, c = self._idx_to_rc(t)
            given_here = given_vals[:, r, c]  # [B]

            # 构造掩码
            masks = torch.zeros(B, 10, dtype=torch.float32, device=device)
            for b in range(B):
                gval = int(given_here[b].item())
                masks[b] = self._allowed_digits_for_cell(
                    givens_row[b], givens_col[b], givens_box[b],
                    pred_row[b], pred_col[b], pred_box[b],
                    r, c, gval
                )

            # 将不允许的token置为 -inf
            disallow = (masks < 0.5)
            step_logits = step_logits.masked_fill(disallow, float('-inf'))

            # 选取下一个token
            next_token = torch.argmax(step_logits, dim=-1, keepdim=True)  # [B,1]

            # 更新预测棋盘与计数
            for b in range(B):
                v = int(next_token[b, 0].item())
                pred_board[b, t] = v
                if v > 0:
                    pred_row[b, r, v] = True
                    pred_col[b, c, v] = True
                    box_idx = (r // 3) * 3 + (c // 3)
                    pred_box[b, box_idx, v] = True

            ys = torch.cat([ys, next_token], dim=1)

        return ys[:, 1:]

    def generate(self, src_tokens: torch.Tensor, max_len: int = 81) -> torch.Tensor:
        # 默认使用带约束的生成，避免行/列/宫内重复
        return self.generate_with_constraints(src_tokens, max_len=max_len)


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
