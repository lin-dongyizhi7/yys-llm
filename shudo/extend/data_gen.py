import json
import os
import random
from typing import List, Tuple

Board = List[List[int]]

TRAIN_DATA_DIR = os.path.join(os.path.dirname(__file__), 'trainData')
os.makedirs(TRAIN_DATA_DIR, exist_ok=True)

# 基础工具

def find_empty(board: Board) -> Tuple[int, int] | None:
    for r in range(9):
        for c in range(9):
            if board[r][c] == 0:
                return r, c
    return None


def is_valid(board: Board, row: int, col: int, n: int) -> bool:
    # 行
    if any(board[row][x] == n for x in range(9)):
        return False
    # 列
    if any(board[x][col] == n for x in range(9)):
        return False
    # 宫
    br = (row // 3) * 3
    bc = (col // 3) * 3
    for r in range(br, br + 3):
        for c in range(bc, bc + 3):
            if board[r][c] == n:
                return False
    return True


def solve_backtrack(board: Board) -> bool:
    empty = find_empty(board)
    if not empty:
        return True
    r, c = empty
    nums = list(range(1, 10))
    random.shuffle(nums)
    for n in nums:
        if is_valid(board, r, c, n):
            board[r][c] = n
            if solve_backtrack(board):
                return True
            board[r][c] = 0
    return False


def generate_full_board() -> Board:
    board = [[0 for _ in range(9)] for _ in range(9)]
    solve_backtrack(board)
    return board


def remove_cells(board: Board, removal_count: int) -> Board:
    puzzle = [row[:] for row in board]
    positions = [(r, c) for r in range(9) for c in range(9)]
    random.shuffle(positions)
    count = 0
    for r, c in positions:
        if count >= removal_count:
            break
        if puzzle[r][c] != 0:
            backup = puzzle[r][c]
            puzzle[r][c] = 0
            # 可选：验证唯一解（此处略，保证速度）。
            count += 1
            # 如果需要唯一解，可在此做解数独计数回溯
    return puzzle


def generate_pair(removal_count: int = 50) -> Tuple[Board, Board]:
    full = generate_full_board()
    puzzle = remove_cells(full, removal_count)
    solution = [row[:] for row in full]
    return puzzle, solution


def save_dataset(num_samples: int = 1000, prefix: str = 'train'):
    """
    生成 num_samples 条数据，保存为 jsonl：每行 {'input': {data: 9x9}, 'target': {data: 9x9}}
    """
    out_path = os.path.join(TRAIN_DATA_DIR, f'{prefix}_sudoku.jsonl')
    with open(out_path, 'w', encoding='utf-8') as f:
        for i in range(num_samples):
            removal_count = random.randint(30, 60)
            puzzle, solution = generate_pair(removal_count)
            rec = {
                'input': { 'data': puzzle },
                'target': { 'data': solution },
            }
            f.write(json.dumps(rec, ensure_ascii=False) + '\n')
    return out_path

if __name__ == '__main__':
    path = save_dataset(num_samples=200, prefix='train')
    print('saved:', path)
