/*
 * @Author: 凛冬已至 2985956026@qq.com
 * @Date: 2025-08-25 08:52:31
 * @LastEditors: 凛冬已至 2985956026@qq.com
 * @LastEditTime: 2025-08-25 11:21:02
 * @FilePath: \my-llm\shudo\src\components\NumberPad.tsx
 * @Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
 */
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
