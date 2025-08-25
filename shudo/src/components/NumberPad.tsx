import React from 'react';
import './NumberPad.css';

interface NumberPadProps {
  onNumberClick: (number: number) => void;
  numberCounts: number[];
  selectedNumber: number | null;
}

const NumberPad: React.FC<NumberPadProps> = ({
  onNumberClick,
  numberCounts,
  selectedNumber
}) => {
  const handleNumberClick = (number: number) => {
    // 先调用父组件的数字输入处理
    onNumberClick(number);
  };

  return (
    <div className="number-pad">
      <h3>数字按钮</h3>
      <div className="number-grid">
        {[1, 2, 3, 4, 5, 6, 7, 8, 9].map(number => (
          <button
            key={number}
            className={`number-button ${selectedNumber === number ? 'selected' : ''}`}
            onClick={() => handleNumberClick(number)}
            disabled={numberCounts[number - 1] === 0}
          >
            <span className="number">{number}</span>
            <span className="count">剩余: {numberCounts[number - 1]}</span>
          </button>
        ))}
      </div>
    </div>
  );
};

export default NumberPad;
