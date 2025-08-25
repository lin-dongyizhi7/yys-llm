/*
 * @Author: 凛冬已至 2985956026@qq.com
 * @Date: 2025-08-25 08:50:34
 * @LastEditors: 凛冬已至 2985956026@qq.com
 * @LastEditTime: 2025-08-25 14:54:59
 * @FilePath: \my-llm\shudo\src\App.tsx
 * @Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
 */
import React, { useState } from 'react';
import './App.css';
import HomePage from './views/HomePage';
import SudokuGame from './components/SudokuGame';
import { SudokuGenerator, SudokuDifficulty } from './utils';

export type GameMode = 'manual' | 'generate';

function App() {
  const [gameMode, setGameMode] = useState<GameMode | null>(null);
  const [initialBoard, setInitialBoard] = useState<number[][] | null>(null);
  const [selectedDifficulty, setSelectedDifficulty] = useState<SudokuDifficulty | null>(null);

  const handleModeSelect = (mode: GameMode, difficulty?: SudokuDifficulty) => {
    setGameMode(mode);
    if (mode === 'generate') {
      // 生成指定难度的数独游戏
      const generatedBoard = generateSudoku(difficulty);
      setInitialBoard(generatedBoard);
      setSelectedDifficulty(difficulty || null);
    } else {
      // 手动模式，创建空白板
      setInitialBoard(createEmptyBoard());
      setSelectedDifficulty(null);
    }
  };

  const handleBackToHome = () => {
    setGameMode(null);
    setInitialBoard(null);
  };

  const createEmptyBoard = (): number[][] => {
    return Array(9).fill(null).map(() => Array(9).fill(0));
  };

  const generateSudoku = (difficulty?: SudokuDifficulty): number[][] => {
    // 使用新的数独生成器生成指定难度的数独
    const generatedSudoku = SudokuGenerator.generate(difficulty);
    return generatedSudoku.board;
  };

  return (
    <div className="App">
      {gameMode === null ? (
        <HomePage onModeSelect={handleModeSelect} />
      ) : (
        <SudokuGame 
          mode={gameMode}
          initialBoard={initialBoard!}
          difficulty={selectedDifficulty}
          onBackToHome={handleBackToHome}
        />
      )}
    </div>
  );
}

export default App;
