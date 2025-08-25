/*
 * @Author: 凛冬已至 2985956026@qq.com
 * @Date: 2025-08-25 08:51:24
 * @LastEditors: 凛冬已至 2985956026@qq.com
 * @LastEditTime: 2025-08-25 10:44:12
 * @FilePath: \my-llm\shudo\src\components\SudokuGame.tsx
 * @Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
 */
import React, { useState, useEffect, useCallback } from 'react';
import './SudokuGame.css';
import { GameMode } from '../App';
import { SudokuDifficulty } from '../utils';
import SudokuBoard from './SudokuBoard';
import NumberPad from './NumberPad';
import GameControls from './GameControls';
import Timer from './Timer';

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
  const [gameTime, setGameTime] = useState<number>(0);
  const [isGameActive, setIsGameActive] = useState<boolean>(true);
  const [initialBoardState, setInitialBoardState] = useState<number[][]>(initialBoard);

  // 调试输出：游戏开始时的信息
  useEffect(() => {
    console.log('🎮 数独游戏开始!');
    console.log('📊 游戏模式:', mode);
    console.log('🎯 难度级别:', difficulty?.name || '未设置');
    console.log('📋 初始数独面板:');
    console.table(initialBoard);
    console.log('🔢 初始数字统计:');
    const initialCounts = initialBoard.flat().filter(num => num > 0).length;
    console.log(`   总数字数量: ${initialCounts}`);
    console.log(`   空格数量: ${81 - initialCounts}`);
    console.log('🎨 颜色系统说明:');
    console.log('   🖤 黑色: 初始数字 (不可修改)');
    console.log('   🔵 蓝色: 用户填入数字 (可修改)');
    console.log('   🔴 红色: 冲突数字 (错误提示)');
    console.log('⌨️ 键盘快捷键:');
    console.log('   1-9: 输入数字');
    console.log('   N: 切换笔记模式');
    console.log('   Delete/Backspace: 清除格子');
    console.log('🔧 调试信息已启用，请查看控制台输出');
  }, [mode, difficulty, initialBoard]);

  // 调试输出：定期显示游戏状态
  useEffect(() => {
    const interval = setInterval(() => {
      if (isGameActive && gameTime > 0) {
        const filledCells = board.flat().filter(num => num > 0).length;
        const initialCells = initialBoardState.flat().filter(num => num > 0).length;
        const userFilledCells = filledCells - initialCells;
        const emptyCells = 81 - filledCells;
        
        console.log('📊 游戏状态监控:');
        console.log(`   游戏时间: ${gameTime} 秒`);
        console.log(`   已填数字: ${filledCells}`);
        console.log(`   初始数字: ${initialCells}`);
        console.log(`   用户填入: ${userFilledCells}`);
        console.log(`   剩余空格: ${emptyCells}`);
        console.log(`   完成进度: ${((filledCells / 81) * 100).toFixed(1)}%`);
      }
    }, 180000); // 每3分钟输出一次状态

    return () => clearInterval(interval);
  }, [isGameActive, gameTime, board, initialBoardState]);

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
    console.log(`🖱️ 点击格子: [${row}, ${col}]`);
    console.log(`   当前值: ${board[row][col] || '空'}`);
    console.log(`   是否为初始数字: ${initialBoardState[row][col] !== 0 ? '是' : '否'}`);
    
    setSelectedCell([row, col]);
    setIsEditing(false);
    
    // 如果点击的是有数字的格子，高亮相同数字
    if (board[row][col] > 0) {
      setHighlightedNumber(board[row][col]);
      console.log(`   高亮数字: ${board[row][col]}`);
    } else {
      setHighlightedNumber(null);
      console.log(`   清除高亮`);
    }
  };

  // 处理数字输入
  const handleNumberInput = (number: number) => {
    if (!selectedCell) {
      console.log('❌ 没有选中的格子，无法输入数字');
      return;
    }
    
    const [row, col] = selectedCell;
    console.log(`🔢 输入数字: ${number} 到格子 [${row}, ${col}]`);
    console.log(`   当前格子值: ${board[row][col] || '空'}`);
    console.log(`   是否为初始数字: ${initialBoardState[row][col] !== 0 ? '是' : '否'}`);
    console.log(`   笔记模式: ${isNoteMode ? '开启' : '关闭'}`);
    
    if (isNoteMode) {
      // 笔记模式
      console.log('📝 笔记模式操作');
      const newNotes = [...notes];
      const cellNotes = [...newNotes[row][col]];
      
      if (cellNotes.includes(number)) {
        // 如果数字已存在，移除它
        newNotes[row][col] = cellNotes.filter(n => n !== number);
        console.log(`   移除笔记: ${number}`);
      } else {
        // 添加新笔记
        newNotes[row][col] = [...cellNotes, number].sort();
        console.log(`   添加笔记: ${number}`);
      }
      
      setNotes(newNotes);
      console.log(`   当前笔记: [${newNotes[row][col].join(', ')}]`);
    } else {
      // 正常模式
      if (board[row][col] === number) {
        // 如果点击相同数字，清除格子
        console.log(`   清除格子 (点击相同数字)`);
        const newBoard = [...board];
        newBoard[row][col] = 0;
        setBoard(newBoard);
        setHighlightedNumber(null);
      } else {
        // 填入新数字
        console.log(`   填入新数字`);
        const newBoard = [...board];
        newBoard[row][col] = number;
        setBoard(newBoard);
        setHighlightedNumber(number);
        
        // 清除该格子的笔记
        const newNotes = [...notes];
        newNotes[row][col] = [];
        setNotes(newNotes);
        console.log(`   清除笔记`);
      }
    }
    
    // 高亮相同数字的格子
    setHighlightedNumber(number);
    console.log(`   高亮数字: ${number}`);
  };

  // 处理键盘输入
  const handleKeyPress = useCallback((event: KeyboardEvent) => {
    if (!selectedCell) {
      console.log('⌨️ 键盘输入: 没有选中的格子');
      return;
    }
    
    const key = event.key;
    console.log(`⌨️ 键盘输入: ${key}`);
    
    if (key >= '1' && key <= '9') {
      console.log(`   数字键: ${key}`);
      handleNumberInput(parseInt(key));
    } else if (key === 'Delete' || key === 'Backspace') {
      const [row, col] = selectedCell;
      console.log(`   删除键: 清除格子 [${row}, ${col}]`);
      const newBoard = [...board];
      newBoard[row][col] = 0;
      setBoard(newBoard);
      setHighlightedNumber(null);
      
      // 清除笔记
      const newNotes = [...notes];
      newNotes[row][col] = [];
      setNotes(newNotes);
      console.log(`   格子已清除`);
    } else if (key === 'n' || key === 'N') {
      const newNoteMode = !isNoteMode;
      console.log(`   笔记模式切换: ${newNoteMode ? '开启' : '关闭'}`);
      setIsNoteMode(newNoteMode);
    } else {
      console.log(`   未识别的按键: ${key}`);
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
    if (selectedCell) {
      console.log(`🚫 清除选择: 格子 [${selectedCell[0]}, ${selectedCell[1]}]`);
    }
    setSelectedCell(null);
    setHighlightedNumber(null);
    setIsEditing(false);
    console.log('✅ 选择已清除');
  };

  // 重置游戏
  const resetGame = () => {
    console.log('🔄 重置游戏');
    console.log('📋 恢复初始数独面板:');
    console.table(initialBoardState);
    console.log('🧹 清空所有笔记');
    console.log('⏱️ 重置计时器');
    
    setBoard(initialBoardState);
    setNotes(Array(9).fill(null).map(() => Array(9).fill(null).map(() => [])));
    clearSelection();
    setGameTime(0);
    
    console.log('✅ 游戏重置完成');
  };

  // 清除所有笔记
  const clearAllNotes = () => {
    console.log('🗑️ 清除所有笔记');
    console.log('📊 当前笔记统计:');
    let totalNotes = 0;
    notes.forEach((row, rowIndex) => {
      row.forEach((cellNotes, colIndex) => {
        if (cellNotes.length > 0) {
          totalNotes += cellNotes.length;
          console.log(`   格子 [${rowIndex}, ${colIndex}]: [${cellNotes.join(', ')}]`);
        }
      });
    });
    console.log(`   总笔记数量: ${totalNotes}`);
    
    setNotes(Array(9).fill(null).map(() => Array(9).fill(null).map(() => [])));
    console.log('✅ 所有笔记已清除');
  };

  // 处理计时器更新
  const handleTimeUpdate = (time: number) => {
    // 每分钟输出一次时间更新日志
    if (time % 60 === 0 && time > 0) {
      const minutes = Math.floor(time / 60);
      console.log(`⏱️ 游戏时间: ${minutes} 分钟`);
    }
    setGameTime(time);
  };

  // 暂停/继续游戏
  const toggleGamePause = () => {
    const newGameState = !isGameActive;
    console.log(`⏸️ 游戏状态切换: ${newGameState ? '继续' : '暂停'}`);
    console.log(`   当前游戏时间: ${gameTime} 秒`);
    setIsGameActive(newGameState);
  };

  return (
    <div className="sudoku-game">
      <div className="game-header">
        <button className="back-button" onClick={onBackToHome}>
          ← 返回首页
        </button>
        <h1>数独游戏</h1>
        <Timer 
            isActive={isGameActive}
            onTimeUpdate={handleTimeUpdate}
        />
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
          initialBoard={initialBoardState}
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
            onToggleNoteMode={() => {
              const newNoteMode = !isNoteMode;
              console.log(`📝 切换笔记模式: ${newNoteMode ? '开启' : '关闭'}`);
              setIsNoteMode(newNoteMode);
            }}
            onClearSelection={clearSelection}
            onResetGame={resetGame}
            onClearAllNotes={clearAllNotes}
            onTogglePause={toggleGamePause}
            isPaused={!isGameActive}
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
