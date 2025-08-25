import React from 'react';
import './SudokuBoard.css';
import SudokuCell from './SudokuCell';

interface SudokuBoardProps {
  board: number[][];
  notes: number[][][];
  selectedCell: [number, number] | null;
  highlightedNumber: number | null;
  onCellClick: (row: number, col: number) => void;
}

const SudokuBoard: React.FC<SudokuBoardProps> = ({
  board,
  notes,
  selectedCell,
  highlightedNumber,
  onCellClick
}) => {
  const isHighlighted = (row: number, col: number): boolean => {
    if (!highlightedNumber) return false;
    
    // 只高亮相同数字的格子
    return board[row][col] === highlightedNumber;
  };

  const isSelected = (row: number, col: number): boolean => {
    return selectedCell !== null && selectedCell[0] === row && selectedCell[1] === col;
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

  return (
    <div className="sudoku-board">
      {board.map((row, rowIndex) => (
        <div key={rowIndex} className="board-row">
          {row.map((cell, colIndex) => (
            <SudokuCell
              key={`${rowIndex}-${colIndex}`}
              value={cell}
              notes={notes[rowIndex][colIndex]}
              isSelected={isSelected(rowIndex, colIndex)}
              isHighlighted={isHighlighted(rowIndex, colIndex)}
              isInSameRow={isInSameRow(rowIndex, colIndex)}
              isInSameCol={isInSameCol(rowIndex, colIndex)}
              isInSameBox={isInSameBox(rowIndex, colIndex)}
              isInitial={false} // 这里可以根据需要判断是否为初始值
              onClick={() => onCellClick(rowIndex, colIndex)}
            />
          ))}
        </div>
      ))}
    </div>
  );
};

export default SudokuBoard;
