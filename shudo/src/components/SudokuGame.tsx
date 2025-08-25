import React, { useState, useEffect, useCallback } from 'react';
import './SudokuGame.css';
import { GameMode } from '../App';
import { SudokuDifficulty } from '../utils';
import SudokuBoard from './SudokuBoard';
import NumberPad from './NumberPad';
import GameControls from './GameControls';

interface SudokuGameProps {
  mode: GameMode;
  initialBoard: number[][];
  difficulty?: SudokuDifficulty | null;
  onBackToHome: () => void;
}

const SudokuGame: React.FC<SudokuGameProps> = ({ mode, initialBoard, difficulty, onBackToHome }) => {
  const [board, setBoard] = useState<number[][]>(initialBoard);
  const [notes, setNotes] = useState<number[][][]>(Array(9).fill(null).map(() => 
    Array(9).fill(null).map(() => [])
  ));
  const [selectedCell, setSelectedCell] = useState<[number, number] | null>(null);
  const [isNoteMode, setIsNoteMode] = useState<boolean>(false);
  const [highlightedNumber, setHighlightedNumber] = useState<number | null>(null);
  const [isEditing, setIsEditing] = useState<boolean>(false);

  // 计算每个数字的剩余个数
  const getNumberCounts = useCallback(() => {
    const counts = Array(9).fill(9);
    for (let row = 0; row < 9; row++) {
      for (let col = 0; col < 9; col++) {
        if (board[row][col] > 0) {
          counts[board[row][col] - 1]--;
        }
      }
    }
    return counts;
  }, [board]);

  // 处理格子点击
  const handleCellClick = (row: number, col: number) => {
    setSelectedCell([row, col]);
    setIsEditing(false);
    
    // 如果点击的是有数字的格子，高亮相同数字
    if (board[row][col] > 0) {
      setHighlightedNumber(board[row][col]);
    } else {
      setHighlightedNumber(null);
    }
  };

  // 处理数字输入
  const handleNumberInput = (number: number) => {
    if (!selectedCell) return;
    
    const [row, col] = selectedCell;
    
    if (isNoteMode) {
      // 笔记模式
      const newNotes = [...notes];
      const cellNotes = [...newNotes[row][col]];
      
      if (cellNotes.includes(number)) {
        // 如果数字已存在，移除它
        newNotes[row][col] = cellNotes.filter(n => n !== number);
      } else {
        // 添加新笔记
        newNotes[row][col] = [...cellNotes, number].sort();
      }
      
      setNotes(newNotes);
    } else {
      // 正常模式
      if (board[row][col] === number) {
        // 如果点击相同数字，清除格子
        const newBoard = [...board];
        newBoard[row][col] = 0;
        setBoard(newBoard);
        setHighlightedNumber(null);
      } else {
        // 填入新数字
        const newBoard = [...board];
        newBoard[row][col] = number;
        setBoard(newBoard);
        setHighlightedNumber(number);
        
        // 清除该格子的笔记
        const newNotes = [...notes];
        newNotes[row][col] = [];
        setNotes(newNotes);
      }
    }
    
    // 高亮相同数字的格子
    setHighlightedNumber(number);
  };

  // 处理键盘输入
  const handleKeyPress = useCallback((event: KeyboardEvent) => {
    if (!selectedCell) return;
    
    const key = event.key;
    if (key >= '1' && key <= '9') {
      handleNumberInput(parseInt(key));
    } else if (key === 'Delete' || key === 'Backspace') {
      const [row, col] = selectedCell;
      const newBoard = [...board];
      newBoard[row][col] = 0;
      setBoard(newBoard);
      setHighlightedNumber(null);
      
      // 清除笔记
      const newNotes = [...notes];
      newNotes[row][col] = [];
      setNotes(newNotes);
    } else if (key === 'n' || key === 'N') {
      setIsNoteMode(!isNoteMode);
    }
  }, [selectedCell, board, notes, isNoteMode]);

  // 监听键盘事件
  useEffect(() => {
    document.addEventListener('keydown', handleKeyPress);
    return () => {
      document.removeEventListener('keydown', handleKeyPress);
    };
  }, [handleKeyPress]);

  // 清除选择
  const clearSelection = () => {
    setSelectedCell(null);
    setHighlightedNumber(null);
    setIsEditing(false);
  };

  // 重置游戏
  const resetGame = () => {
    setBoard(initialBoard);
    setNotes(Array(9).fill(null).map(() => Array(9).fill(null).map(() => [])));
    clearSelection();
  };

  // 清除所有笔记
  const clearAllNotes = () => {
    setNotes(Array(9).fill(null).map(() => Array(9).fill(null).map(() => [])));
  };

  return (
    <div className="sudoku-game">
      <div className="game-header">
        <button className="back-button" onClick={onBackToHome}>
          ← 返回首页
        </button>
        <h1>数独游戏</h1>
        <div className="mode-indicator">
          {mode === 'manual' ? '手动模式' : `自动生成 - ${difficulty?.name || '中等'}`}
        </div>
      </div>

      <div className="game-container">
        <SudokuBoard
          board={board}
          notes={notes}
          selectedCell={selectedCell}
          highlightedNumber={highlightedNumber}
          onCellClick={handleCellClick}
        />
        
        <div className="game-sidebar">
          <NumberPad
            onNumberClick={handleNumberInput}
            numberCounts={getNumberCounts()}
            selectedNumber={highlightedNumber}
          />
          
          <GameControls
            isNoteMode={isNoteMode}
            onToggleNoteMode={() => setIsNoteMode(!isNoteMode)}
            onClearSelection={clearSelection}
            onResetGame={resetGame}
            onClearAllNotes={clearAllNotes}
          />
        </div>
      </div>

      <div className="game-instructions">
        <h3>游戏说明：</h3>
        <ul>
          <li>点击格子选择，然后点击数字按钮填入</li>
          <li>按 N 键或点击笔记按钮切换笔记模式</li>
          <li>笔记模式下可以添加多个数字作为提示</li>
          <li>点击已填入数字的格子会高亮相同数字</li>
          <li>使用键盘 1-9 输入数字，Delete 清除</li>
        </ul>
      </div>
    </div>
  );
};

export default SudokuGame;
