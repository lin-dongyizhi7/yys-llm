from typing import List, Tuple, Optional

Board = List[List[int]]


def find_empty(board: Board) -> Optional[Tuple[int, int]]:
    for r in range(9):
        for c in range(9):
            if board[r][c] == 0:
                return r, c
    return None


def is_valid(board: Board, row: int, col: int, n: int) -> bool:
    if any(board[row][x] == n for x in range(9)):
        return False
    if any(board[x][col] == n for x in range(9)):
        return False
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
    for n in range(1, 10):
        if is_valid(board, r, c, n):
            board[r][c] = n
            if solve_backtrack(board):
                return True
            board[r][c] = 0
    return False


def solved(board: Board) -> bool:
    return find_empty(board) is None
