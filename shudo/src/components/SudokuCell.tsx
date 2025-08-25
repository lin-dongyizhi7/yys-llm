import React from 'react';
import './SudokuCell.css';

interface SudokuCellProps {
  value: number;
  notes: number[];
  isSelected: boolean;
  isHighlighted: boolean;
  isInSameRow: boolean;
  isInSameCol: boolean;
  isInSameBox: boolean;
  isInitial: boolean;
  onClick: () => void;
}

const SudokuCell: React.FC<SudokuCellProps> = ({
  value,
  notes,
  isSelected,
  isHighlighted,
  isInSameRow,
  isInSameCol,
  isInSameBox,
  isInitial,
  onClick
}) => {
  const getCellClassName = (): string => {
    let className = 'sudoku-cell';
    
    if (isSelected) {
      className += ' selected';
    } else if (isHighlighted) {
      className += ' highlighted';
    } else if (isInSameRow || isInSameCol || isInSameBox) {
      className += ' related';
    }
    
    if (isInitial) {
      className += ' initial';
    }
    
    return className;
  };

  const renderContent = () => {
    if (value > 0) {
      return (
        <span className="cell-value">
          {value}
        </span>
      );
    } else if (notes.length > 0) {
      return (
        <div className="cell-notes">
          {[1, 2, 3, 4, 5, 6, 7, 8, 9].map(num => (
            <span
              key={num}
              className={`note-number ${notes.includes(num) ? 'active' : ''}`}
            >
              {notes.includes(num) ? num : ''}
            </span>
          ))}
        </div>
      );
    }
    return null;
  };

  return (
    <div
      className={getCellClassName()}
      onClick={onClick}
    >
      {renderContent()}
    </div>
  );
};

export default SudokuCell;
