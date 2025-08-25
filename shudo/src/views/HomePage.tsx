import React, { useState } from "react";
import "./HomePage.css";
import { GameMode } from "../App";
import { SudokuGenerator, SudokuDifficulty } from "../utils";

interface HomePageProps {
  onModeSelect: (mode: GameMode, difficulty?: SudokuDifficulty) => void;
}

const HomePage: React.FC<HomePageProps> = ({ onModeSelect }) => {
  const [showDifficultySelection, setShowDifficultySelection] = useState(false);

  const handleManualMode = () => {
    onModeSelect("manual");
  };

  const handleGenerateMode = () => {
    setShowDifficultySelection(true);
  };

  const handleDifficultySelect = (difficulty: SudokuDifficulty) => {
    onModeSelect("generate", difficulty);
  };

  const handleBackToModes = () => {
    setShowDifficultySelection(false);
  };

  if (showDifficultySelection) {
    return (
      <div className="home-page">
        <h1 className="title">选择难度</h1>
        <div className="difficulty-selection">
          <h2>选择数独难度</h2>
          <div className="difficulty-buttons">
            {SudokuGenerator.DIFFICULTIES.map((difficulty) => (
              <button
                key={difficulty.name}
                className={`difficulty-button ${difficulty.name.toLowerCase()}`}
                onClick={() => handleDifficultySelect(difficulty)}
              >
                <h3>{difficulty.name}</h3>
                <p>{difficulty.description}</p>
                <div className="difficulty-info">
                  <span className="cells-info">
                    提示数字: {81 - difficulty.cellsToRemove}
                  </span>
                  <span className="empty-info">
                    空格: {difficulty.cellsToRemove}
                  </span>
                </div>
              </button>
            ))}
          </div>
          <button className="back-button" onClick={handleBackToModes}>
            ← 返回模式选择
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="home-page">
      <h1 className="title">数独游戏</h1>
      <div className="mode-selection">
        <h2>选择游戏模式</h2>
        <div className="mode-buttons">
          <button className="mode-button manual" onClick={handleManualMode}>
            <h3>手动模式</h3>
            <p>自己填写初始数字，创建自定义数独</p>
          </button>
          <button className="mode-button generate" onClick={handleGenerateMode}>
            <h3>自动生成</h3>
            <p>系统自动生成数独游戏，可选择难度</p>
          </button>
        </div>
      </div>
    </div>
  );
};

export default HomePage;
