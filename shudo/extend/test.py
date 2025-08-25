import argparse
import json
import os
from typing import List

import torch

from model import SudokuTransformer, board_to_tokens, tokens_to_board
from solver import solve_backtrack

Board = List[List[int]]


def load_board(path: str) -> Board:
    with open(path, 'r', encoding='utf-8') as f:
        obj = json.load(f)
    if isinstance(obj, dict) and 'data' in obj:
        return obj['data']
    # 兼容数据集一行json
    if isinstance(obj, dict) and 'input' in obj and 'data' in obj['input']:
        return obj['input']['data']
    raise ValueError('不支持的JSON格式，应为 {"data": 9x9} 或数据集条目格式')


def save_board(path: str, board: Board):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump({'data': board}, f, ensure_ascii=False, indent=2)


def predict_with_model(model_path: str, board: Board, device: str = 'cuda' if torch.cuda.is_available() else 'cpu', use_backtrack: bool = True) -> Board:
    model = SudokuTransformer()
    model.load_state_dict(torch.load(model_path, map_location=device))
    model.to(device)
    model.eval()

    src_tokens = board_to_tokens(board).unsqueeze(0).to(device)  # [1, 81]

    with torch.no_grad():
        pred_tokens = model.generate(src_tokens, max_len=81)[0].cpu()  # [81]

    pred_board = tokens_to_board(pred_tokens)

    # 若需要，用题面覆盖+回溯补全
    if use_backtrack:
        for r in range(9):
            for c in range(9):
                if board[r][c] != 0:
                    pred_board[r][c] = board[r][c]
        solve_backtrack(pred_board)

    return pred_board


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--model', required=True, default='models/sudoku_transformer.pt', help='已训练模型权重路径，如 models/sudoku_transformer.pt')
    ap.add_argument('--input', required=True, help='题面JSON文件，格式 {"data": 9x9} 或数据集条目')
    ap.add_argument('--output', default='', help='可选，保存解到该路径（JSON）')
    ap.add_argument('--no_backtrack', action='store_true', help='不使用回溯补全')
    args = ap.parse_args()

    board = load_board(args.input)
    solved = predict_with_model(args.model, board, use_backtrack=not args.no_backtrack)

    print('预测解:')
    for r in range(9):
        print(' '.join(str(x) for x in solved[r]))

    if args.output:
        os.makedirs(os.path.dirname(args.output) or '.', exist_ok=True)
        save_board(args.output, solved)
        print('已保存到:', args.output)


if __name__ == '__main__':
    main()
