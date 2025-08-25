import React from "react";
import "./GameControls.css";

interface GameControlsProps {
  isNoteMode: boolean;
  onToggleNoteMode: () => void;
  onClearSelection: () => void;
  onResetGame: () => void;
  onClearAllNotes: () => void;
}

const GameControls: React.FC<GameControlsProps> = ({
  isNoteMode,
  onToggleNoteMode,
  onClearSelection,
  onResetGame,
  onClearAllNotes,
}) => {
  return (
    <div className="game-controls">
      <h3>游戏控制</h3>

      <button
        className={`control-button note-mode ${isNoteMode ? "active" : ""}`}
        onClick={onToggleNoteMode}
      >
        <span className="button-icon">✏️</span>
        <span className="button-text">
          {isNoteMode ? "笔记模式开启" : "笔记模式关闭"}
        </span>
      </button>

      <button
        className="control-button clear-selection"
        onClick={onClearSelection}
      >
        <span className="button-icon">🚫</span>
        <span className="button-text">清除选择</span>
      </button>

      <button className="control-button reset-game" onClick={onResetGame}>
        <span className="button-icon">🔄</span>
        <span className="button-text">重置游戏</span>
      </button>

      <button className="control-button clear-notes" onClick={onClearAllNotes}>
        <span className="button-icon">🗑️</span>
        <span className="button-text">清除所有笔记</span>
      </button>

      <div className="keyboard-hints">
        <h4>键盘快捷键</h4>
        <div className="hint-item">
          <span className="key">1-9</span>
          <span className="description">输入数字</span>
        </div>
        <div className="hint-item">
          <span className="key">N</span>
          <span className="description">切换笔记模式</span>
        </div>
        <div className="hint-item">
          <span className="key">Delete</span>
          <span className="description">清除格子</span>
        </div>
      </div>
    </div>
  );
};

export default GameControls;
