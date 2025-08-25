import React from "react";
import "./SudokuBoard.css";
import SudokuCell from "./SudokuCell";

interface SudokuBoardProps {
  board: number[][];
  notes: number[][][];
  selectedCell: [number, number] | null;
  highlightedNumber: number | null;
  initialBoard: number[][];
  initFlag: number[][];
  onCellClick: (row: number, col: number) => void;
}

const SudokuBoard: React.FC<SudokuBoardProps> = ({
  board,
  notes,
  selectedCell,
  highlightedNumber,
  initialBoard,
  initFlag,
  onCellClick,
}) => {
  const isHighlighted = (row: number, col: number): boolean => {
    if (!highlightedNumber) return false;

    // 只高亮相同数字的格子
    return board[row][col] === highlightedNumber;
  };

  const isSelected = (row: number, col: number): boolean => {
    return (
      selectedCell !== null &&
      selectedCell[0] === row &&
      selectedCell[1] === col
    );
  };

  const isInSameRow = (row: number, col: number): boolean => {
    return selectedCell !== null && selectedCell[0] === row;
  };

  const isInSameCol = (row: number, col: number): boolean => {
    return selectedCell !== null && selectedCell[1] === col;
  };

  const isInSameBox = (row: number, col: number): boolean => {
    if (!selectedCell) return false;

    const selectedBoxRow = Math.floor(selectedCell[0] / 3);
    const selectedBoxCol = Math.floor(selectedCell[1] / 3);
    const currentBoxRow = Math.floor(row / 3);
    const currentBoxCol = Math.floor(col / 3);

    return selectedBoxRow === currentBoxRow && selectedBoxCol === currentBoxCol;
  };

  // 检测数字冲突
  const hasConflict = (row: number, col: number): boolean => {
    const value = board[row][col];
    if (value === 0) return false;

    // 检查行冲突
    for (let c = 0; c < 9; c++) {
      if (c !== col && board[row][c] === value) return true;
    }

    // 检查列冲突
    for (let r = 0; r < 9; r++) {
      if (r !== row && board[r][col] === value) return true;
    }

    // 检查3x3宫格冲突
    const boxRow = Math.floor(row / 3) * 3;
    const boxCol = Math.floor(col / 3) * 3;
    for (let r = boxRow; r < boxRow + 3; r++) {
      for (let c = boxCol; c < boxCol + 3; c++) {
        if ((r !== row || c !== col) && board[r][c] === value) return true;
      }
    }

    return false;
  };

  return (
    <div className="sudoku-board">
      {board.map((row, rowIndex) => (
        <div key={rowIndex} className="board-row">
          {row.map((cell, colIndex) => {
            // 使用initFlag判断是否为初始格子，确保与SudokuGame中的逻辑一致
            const isInitialCell = initFlag[rowIndex][colIndex] === 1;
            
            return (
              <SudokuCell
                key={`${rowIndex}-${colIndex}`}
                value={cell}
                notes={notes[rowIndex][colIndex]}
                isSelected={isSelected(rowIndex, colIndex)}
                isHighlighted={isHighlighted(rowIndex, colIndex)}
                isInSameRow={isInSameRow(rowIndex, colIndex)}
                isInSameCol={isInSameCol(rowIndex, colIndex)}
                isInSameBox={isInSameBox(rowIndex, colIndex)}
                isInitial={isInitialCell}
                isConflict={hasConflict(rowIndex, colIndex)}
                onClick={() => onCellClick(rowIndex, colIndex)}
              />
            );
          })}
        </div>
      ))}
    </div>
  );
};

export default SudokuBoard;
