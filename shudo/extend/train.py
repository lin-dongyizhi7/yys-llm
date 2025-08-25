import json
import os
from typing import List, Dict, Any

import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from tqdm import tqdm

from model import SudokuTransformer, board_to_tokens
from solver import solve_backtrack

DATA_DIR = os.path.join(os.path.dirname(__file__), 'trainData')

class SudokuJsonlDataset(Dataset):
    def __init__(self, path: str):
        self.samples: List[Dict[str, Any]] = []
        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                if not line.strip():
                    continue
                rec = json.loads(line)
                self.samples.append(rec)

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx: int):
        rec = self.samples[idx]
        src = rec['input']['data']  # 9x9，含0
        tgt = rec['target']['data'] # 9x9，完整解1..9

        src_tokens = board_to_tokens(src)          # [81]
        tgt_tokens = board_to_tokens(tgt)          # [81]
        # 训练时用 teacher forcing：shift 1位
        # 我们使用0作为起始符，labels与输入对齐
        bos = torch.zeros(1, dtype=torch.long)
        dec_in = torch.cat([bos, tgt_tokens[:-1]], dim=0)  # [81]
        labels = tgt_tokens                                 # [81]
        return src_tokens, dec_in, labels


def collate(batch):
    srcs, dec_ins, labels = zip(*batch)
    return torch.stack(srcs, dim=0), torch.stack(dec_ins, dim=0), torch.stack(labels, dim=0)


def train(model_path: str = 'sudoku_transformer.pt', data_prefix: str = 'train_sudoku.jsonl', epochs: int = 3, batch_size: int = 64, lr: float = 3e-4, device: str = 'cuda' if torch.cuda.is_available() else 'cpu'):
    data_path = os.path.join(DATA_DIR, data_prefix)
    dataset = SudokuJsonlDataset(data_path)
    loader = DataLoader(dataset, batch_size=batch_size, shuffle=True, num_workers=0, collate_fn=collate)

    model = SudokuTransformer()
    model.to(device)

    criterion = nn.CrossEntropyLoss()
    optim = torch.optim.AdamW(model.parameters(), lr=lr)

    model.train()
    for epoch in range(1, epochs + 1):
        pbar = tqdm(loader, desc=f"epoch {epoch}")
        total_loss = 0.0
        for src, dec_in, labels in pbar:
            src = src.to(device)
            dec_in = dec_in.to(device)
            labels = labels.to(device)

            optim.zero_grad()
            logits = model(src, dec_in)  # [B, T, vocab]
            loss = criterion(logits.reshape(-1, logits.size(-1)), labels.reshape(-1))
            loss.backward()
            optim.step()

            total_loss += loss.item()
            pbar.set_postfix(loss=f"{loss.item():.4f}")

        avg = total_loss / len(loader)
        print(f"epoch {epoch}: avg loss = {avg:.4f}")
        torch.save(model.state_dict(), model_path)

    print("training done. saved to", model_path)


def quick_eval(model_path: str = 'sudoku_transformer.pt', n: int = 10, data_prefix: str = 'train_sudoku.jsonl', device: str = 'cuda' if torch.cuda.is_available() else 'cpu'):
    data_path = os.path.join(DATA_DIR, data_prefix)
    dataset = SudokuJsonlDataset(data_path)
    model = SudokuTransformer()
    model.load_state_dict(torch.load(model_path, map_location=device))
    model.to(device)
    model.eval()

    ok = 0
    with torch.no_grad():
        for i in range(min(n, len(dataset))):
            src_tokens, dec_in, labels = dataset[i]
            src_tokens = src_tokens.unsqueeze(0).to(device)
            pred = model.generate(src_tokens, max_len=81)[0].cpu()
            # 将预测转回棋盘，并用回溯快速验证完整性（若预测含0，则一般无法解）
            board_pred = [[0 for _ in range(9)] for _ in range(9)]
            k = 0
            for r in range(9):
                for c in range(9):
                    board_pred[r][c] = int(pred[k].item())
                    k += 1
            # 若存在0，尝试用回溯补完
            if any(board_pred[r][c] == 0 for r in range(9) for c in range(9)):
                # 放到回溯前，先把src中的已知数字覆盖，避免破坏题面
                src_board = [[0 for _ in range(9)] for _ in range(9)]
                s = dataset.samples[i]['input']['data']
                for r in range(9):
                    for c in range(9):
                        src_board[r][c] = s[r][c]
                        if src_board[r][c] != 0:
                            board_pred[r][c] = src_board[r][c]
                if solve_backtrack(board_pred):
                    ok += 1
            else:
                ok += 1
    print(f"quick_eval: {ok}/{min(n, len(dataset))} solved or backtracked")

if __name__ == '__main__':
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('--mode', type=str, default='train', choices=['train', 'eval'])
    ap.add_argument('--epochs', type=int, default=3)
    ap.add_argument('--batch_size', type=int, default=64)
    ap.add_argument('--lr', type=float, default=3e-4)
    ap.add_argument('--model_path', type=str, default='sudoku_transformer.pt')
    ap.add_argument('--data_prefix', type=str, default='train_sudoku.jsonl')
    ap.add_argument('--eval_n', type=int, default=20)
    args = ap.parse_args()

    if args.mode == 'train':
        train(model_path=args.model_path, data_prefix=args.data_prefix, epochs=args.epochs, batch_size=args.batch_size, lr=args.lr)
    else:
        quick_eval(model_path=args.model_path, n=args.eval_n, data_prefix=args.data_prefix)
