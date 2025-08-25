import React, { useState } from 'react';
import './App.css';
import HomePage from './components/HomePage';
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
