/*
 * @Author: 凛冬已至 2985956026@qq.com
 * @Date: 2025-08-25 08:51:24
 * @LastEditors: 凛冬已至 2985956026@qq.com
 * @LastEditTime: 2025-08-25 14:15:52
 * @FilePath: \my-llm\shudo\src\components\SudokuGame.tsx
 * @Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
 */
import React, { useState, useEffect, useCallback, useRef } from "react";
import "./SudokuGame.css";
import { GameMode } from "../App";
import { SudokuDifficulty } from "../utils";
import SudokuBoard from "./game-ui/SudokuBoard";
import NumberPad from "./game-ui/NumberPad";
import GameControls from "./game-control/GameControls";
import Timer from "./game-control/Timer";
import ImportDialog from "./game-control/ImportDialog";

interface SudokuGameProps {
  mode: GameMode;
  initialBoard: number[][];
  difficulty?: SudokuDifficulty | null;
  onBackToHome: () => void;
}

const SudokuGame: React.FC<SudokuGameProps> = ({
  mode,
  initialBoard,
  difficulty,
  onBackToHome,
}) => {
  const [board, setBoard] = useState<number[][]>(initialBoard);
  const [notes, setNotes] = useState<number[][][]>(
    Array(9)
      .fill(null)
      .map(() =>
        Array(9)
          .fill(null)
          .map(() => [])
      )
  );
  const [selectedCell, setSelectedCell] = useState<[number, number] | null>(
    null
  );
  const [isNoteMode, setIsNoteMode] = useState<boolean>(false);
  const [highlightedNumber, setHighlightedNumber] = useState<number | null>(
    null
  );
  const [isEditing, setIsEditing] = useState<boolean>(false);
  const [gameTime, setGameTime] = useState<number>(0);
  const [isGameActive, setIsGameActive] = useState<boolean>(true);
  // 新增：手动模式下的游戏状态
  const [isManualModeActive, setIsManualModeActive] = useState<boolean>(false);
  // 新增：导入对话框状态
  const [isImportDialogOpen, setIsImportDialogOpen] = useState<boolean>(false);
  // 新增：测试导入对话框状态
  const [isTestDialogOpen, setIsTestDialogOpen] = useState<boolean>(false);
  // 使用useRef创建初始格子标识常量，确保在游戏开始后永不改变
  const initFlagRef = useRef<number[][]>();
  
  // 只在游戏开始时计算一次initFlag，之后永不改变
  if (!initFlagRef.current) {
    console.log("🎯 游戏开始，初始化initFlag");
    initFlagRef.current = initialBoard.map(row => 
      row.map(cell => cell > 0 ? 1 : 0)
    );
  }
  
  const initFlag = initFlagRef.current!;

  // 调试输出：游戏开始时的信息
  useEffect(() => {
    console.log("🎮 数独游戏开始!");
    console.log("📊 游戏模式:", mode);
    console.log("🎯 难度级别:", difficulty?.name || "未设置");
    console.log("📋 初始数独面板:");
    console.table(initialBoard);
    console.log("🔢 初始数字统计:");
    const initialCounts = initialBoard.flat().filter((num) => num > 0).length;
    console.log(`   总数字数量: ${initialCounts}`);
    console.log(`   空格数量: ${81 - initialCounts}`);
    console.log("🎨 颜色系统说明:");
    console.log("   🖤 黑色: 初始数字 (不可修改)");
    console.log("   🔵 蓝色: 用户填入数字 (可修改)");
    console.log("   🔴 红色: 冲突数字 (错误提示)");
    console.log("⌨️ 键盘快捷键:");
    console.log("   1-9: 输入数字");
    console.log("   N: 切换笔记模式");
    console.log("   Delete/Backspace: 清除格子");
    console.log("🔧 调试信息已启用，请查看控制台输出");
    
    // 显示初始格子标识
    console.log("🏷️ 初始格子标识 (initFlag):");
    console.table(initFlag);
    console.log("   📝 1 = 初始格子，0 = 空格");
    
    // 验证initFlag与initialBoard的一致性
    let isConsistent = true;
    for (let row = 0; row < 9; row++) {
      for (let col = 0; col < 9; col++) {
        const expectedFlag = initialBoard[row][col] > 0 ? 1 : 0;
        if (initFlag[row][col] !== expectedFlag) {
          isConsistent = false;
          console.error(`🚨 不一致: 格子 [${row}, ${col}]`);
          console.error(`   initialBoard: ${initialBoard[row][col]} -> 期望flag: ${expectedFlag}`);
          console.error(`   initFlag: ${initFlag[row][col]}`);
        }
      }
    }
    console.log(`✅ initFlag一致性验证: ${isConsistent ? '通过' : '失败'}`);
  }, [mode, difficulty, initialBoard]);

  // 调试输出：定期显示游戏状态
  useEffect(() => {
    const interval = setInterval(() => {
      if (isGameActive && gameTime > 0 && isManualModeActive) {
        const filledCells = board.flat().filter((num) => num > 0).length;
        const initialCells = initFlag.flat().reduce((sum: number, flag: number) => sum + flag, 0);
        const userFilledCells = filledCells - initialCells;
        const emptyCells = 81 - filledCells;

        console.log("📊 游戏状态监控:");
        console.log(`   游戏时间: ${gameTime} 秒`);
        console.log(`   已填数字: ${filledCells}`);
        console.log(`   初始数字: ${initialCells}`);
        console.log(`   用户填入: ${userFilledCells}`);
        console.log(`   剩余空格: ${emptyCells}`);
        console.log(`   完成进度: ${((filledCells / 81) * 100).toFixed(1)}%`);
      }
    }, 180000); // 每3分钟输出一次状态

    return () => clearInterval(interval);
  }, [isGameActive, gameTime, board, isManualModeActive]);

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
    // 在手动模式下，如果游戏还没开始，允许编辑所有格子
    if (mode === 'manual' && !isManualModeActive) {
      console.log(`🖱️ 手动模式编辑: 点击格子 [${row}, ${col}]`);
      setSelectedCell([row, col]);
      setIsEditing(false);
      return;
    }

    console.log(`🖱️ 点击格子: [${row}, ${col}]`);
    console.log(`   当前值: ${board[row][col] || "空"}`);
    console.log(
      `   是否为初始数字: ${initFlag[row][col] === 1 ? "是" : "否"}`
    );

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
      console.log("❌ 没有选中的格子，无法输入数字");
      return;
    }

    const [row, col] = selectedCell;
    console.log(`🔢 输入数字: ${number} 到格子 [${row}, ${col}]`);
    console.log(`   当前格子值: ${board[row][col] || "空"}`);
    
    // 在手动模式下，如果游戏还没开始，允许编辑所有格子
    if (mode === 'manual' && !isManualModeActive) {
      console.log(`   手动模式编辑: 允许编辑所有格子`);
      if (isNoteMode) {
        // 笔记模式
        console.log("📝 笔记模式操作");
        const newNotes = [...notes];
        const cellNotes = [...newNotes[row][col]];

        if (cellNotes.includes(number)) {
          // 如果数字已存在，移除它
          newNotes[row][col] = cellNotes.filter((n) => n !== number);
          console.log(`   移除笔记: ${number}`);
        } else {
          // 添加新笔记
          newNotes[row][col] = [...cellNotes, number].sort();
          console.log(`   添加笔记: ${number}`);
        }

        setNotes(newNotes);
        console.log(`   当前笔记: [${newNotes[row][col].join(", ")}]`);
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
      return;
    }

    console.log(
      `   是否为初始数字: ${initFlag[row][col] === 1 ? "是" : "否"}`
    );
    console.log(`   笔记模式: ${isNoteMode ? "开启" : "关闭"}`);

    // 检查是否为初始数字（不可编辑）
    if (initFlag[row][col] === 1) {
      console.log("❌ 不能编辑初始数字");
      return;
    }

    if (isNoteMode) {
      // 笔记模式
      console.log("📝 笔记模式操作");
      const newNotes = [...notes];
      const cellNotes = [...newNotes[row][col]];

      if (cellNotes.includes(number)) {
        // 如果数字已存在，移除它
        newNotes[row][col] = cellNotes.filter((n) => n !== number);
        console.log(`   移除笔记: ${number}`);
      } else {
        // 添加新笔记
        newNotes[row][col] = [...cellNotes, number].sort();
        console.log(`   添加笔记: ${number}`);
      }

      setNotes(newNotes);
      console.log(`   当前笔记: [${newNotes[row][col].join(", ")}]`);
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
  const handleKeyPress = useCallback(
    (event: KeyboardEvent) => {
      if (!selectedCell) {
        console.log("⌨️ 键盘输入: 没有选中的格子");
        return;
      }

      const key = event.key;
      console.log(`⌨️ 键盘输入: ${key}`);

      if (key >= "1" && key <= "9") {
        console.log(`   数字键: ${key}`);
        handleNumberInput(parseInt(key));
      } else if (key === "Delete" || key === "Backspace") {
        const [row, col] = selectedCell;
        console.log(`   删除键: 清除格子 [${row}, ${col}]`);
        
        // 在手动模式下，如果游戏还没开始，允许编辑所有格子
        if (mode === 'manual' && !isManualModeActive) {
          const newBoard = [...board];
          newBoard[row][col] = 0;
          setBoard(newBoard);
          setHighlightedNumber(null);

          // 清除笔记
          const newNotes = [...notes];
          newNotes[row][col] = [];
          setNotes(newNotes);
          console.log(`   格子已清除`);
          return;
        }

        // 检查是否为初始数字（不可编辑）
        if (initFlag[row][col] === 1) {
          console.log("❌ 不能编辑初始数字");
          return;
        }

        const newBoard = [...board];
        newBoard[row][col] = 0;
        setBoard(newBoard);
        setHighlightedNumber(null);

        // 清除笔记
        const newNotes = [...notes];
        newNotes[row][col] = [];
        setNotes(newNotes);
        console.log(`   格子已清除`);
      } else if (key === "n" || key === "N") {
        const newNoteMode = !isNoteMode;
        console.log(`   笔记模式切换: ${newNoteMode ? "开启" : "关闭"}`);
        setIsNoteMode(newNoteMode);
      } else {
        console.log(`   未识别的按键: ${key}`);
      }
    },
    [selectedCell, board, notes, isNoteMode, mode, isManualModeActive, initFlag]
  );

  // 监听键盘事件
  useEffect(() => {
    document.addEventListener("keydown", handleKeyPress);
    return () => {
      document.removeEventListener("keydown", handleKeyPress);
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
    console.log("✅ 选择已清除");
  };

  // 重置游戏
  const resetGame = () => {
    console.log("🔄 重置游戏");
    console.log("📋 恢复初始数独面板:");
    console.table(initialBoard);
    console.log("🧹 清空所有笔记");
    console.log("⏱️ 重置计时器");

    // 使用原始initialBoard重置，确保与initFlag一致
    setBoard([...initialBoard]);
    setNotes(
      Array(9)
        .fill(null)
        .map(() =>
          Array(9)
            .fill(null)
            .map(() => [])
        )
    );
    clearSelection();
    setGameTime(0);
    
    // 重置手动模式状态
    if (mode === 'manual') {
      setIsManualModeActive(false);
    }

    console.log("✅ 游戏重置完成");
    console.log("🔍 验证重置后的状态:");
    console.log(`   initFlag中的初始格子数量: ${initFlag.flat().reduce((sum: number, flag: number) => sum + flag, 0)}`);
    console.log(`   当前board中的数字数量: ${board.flat().filter((num) => num > 0).length}`);
  };

  // 清除所有笔记
  const clearAllNotes = () => {
    console.log("🗑️ 清除所有笔记");
    console.log("📊 当前笔记统计:");
    let totalNotes = 0;
    notes.forEach((row, rowIndex) => {
      row.forEach((cellNotes, colIndex) => {
        if (cellNotes.length > 0) {
          totalNotes += cellNotes.length;
          console.log(
            `   格子 [${rowIndex}, ${colIndex}]: [${cellNotes.join(", ")}]`
          );
        }
      });
    });
    console.log(`   总笔记数量: ${totalNotes}`);

    setNotes(
      Array(9)
        .fill(null)
        .map(() =>
          Array(9)
            .fill(null)
            .map(() => [])
        )
    );
    console.log("✅ 所有笔记已清除");
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
    console.log(`⏸️ 游戏状态切换: ${newGameState ? "继续" : "暂停"}`);
    console.log(`   当前游戏时间: ${gameTime} 秒`);
    setIsGameActive(newGameState);
  };

  // 手动模式：完成创建按钮点击处理
  const handleFinishCreation = () => {
    console.log("🎯 手动模式：完成创建，开始游戏");
    console.log("📋 当前数独面板:");
    console.table(board);
    
    // 计算当前填入的数字数量
    const filledCells = board.flat().filter((num) => num > 0).length;
    console.log(`   已填入数字: ${filledCells}`);
    
    // 更新初始格子标识，将当前所有有数字的格子标记为初始格子
    const newInitFlag = board.map(row => 
      row.map(cell => cell > 0 ? 1 : 0)
    );
    
    // 更新ref中的initFlag
    if (initFlagRef.current) {
      initFlagRef.current = newInitFlag;
    }
    
    // 激活手动模式游戏
    setIsManualModeActive(true);
    
    console.log("✅ 手动模式游戏已激活");
    console.log("🔒 当前所有数字已锁定为初始数字");
  };

  // 处理导入数据
  const handleImport = (importedBoard: number[][]) => {
    console.log("📥 导入数独数据");
    console.log("📋 导入的数独面板:");
    console.table(importedBoard);
    
    // 更新棋盘
    setBoard([...importedBoard]);
    
    // 清空笔记
    setNotes(
      Array(9)
        .fill(null)
        .map(() =>
          Array(9)
            .fill(null)
            .map(() => [])
        )
    );
    
    // 清除选择
    clearSelection();
    
    // 如果游戏已经开始，重置为创建阶段
    if (isManualModeActive) {
      setIsManualModeActive(false);
      console.log("🔄 导入后重置为创建阶段");
    }
    
    console.log("✅ 数独数据导入完成");
  };

  // 测试导入：仅填充当前空格，不覆盖已有或initFlag为1的格子
  const handleTestImport = (importedBoard: number[][]) => {
    console.log("🧪 测试导入开始");
    console.log("📋 测试导入的数独面板:");
    console.table(importedBoard);

    // 基础校验 9x9
    const isValidSize =
      Array.isArray(importedBoard) &&
      importedBoard.length === 9 &&
      importedBoard.every((row) => Array.isArray(row) && row.length === 9);
    if (!isValidSize) {
      console.error("❌ 测试导入失败：JSON必须为9x9数组");
      setIsTestDialogOpen(false);
      return;
    }

    const newBoard = board.map((row) => [...row]);
    const newNotes = notes.map((row) => row.map((cell) => [...cell])) as number[][][];
    let filledCount = 0;

    for (let r = 0; r < 9; r++) {
      for (let c = 0; c < 9; c++) {
        const canFill = board[r][c] === 0 && initFlag[r][c] !== 1;
        const val = importedBoard[r][c];
        if (canFill && typeof val === "number" && val > 0 && val <= 9) {
          newBoard[r][c] = val;
          newNotes[r][c] = [];
          filledCount++;
        }
      }
    }

    setBoard(newBoard);
    setNotes(newNotes);
    setIsTestDialogOpen(false);

    console.log(`✅ 测试导入完成：填充了 ${filledCount} 个空格`);
  };

  return (
    <div className="sudoku-game">
      <div className="game-header">
        <button className="back-button" onClick={onBackToHome}>
          ← 返回首页
        </button>
        <h1>数独游戏</h1>
        
        {/* 手动模式下显示完成创建按钮或计时器 */}
        {mode === "manual" ? (
          !isManualModeActive ? (
            <div className="manual-mode-controls">
              <button 
                className="import-button"
                onClick={() => setIsImportDialogOpen(true)}
              >
                📁 导入
              </button>
              <button 
                className="import-button"
                onClick={() => setIsTestDialogOpen(true)}
              >
                🧪 测试
              </button>
              <button 
                className="finish-creation-button"
                onClick={handleFinishCreation}
              >
                ✅ 完成创建
              </button>
            </div>
          ) : (
            <Timer isActive={isGameActive} onTimeUpdate={handleTimeUpdate} />
          )
        ) : (
          <Timer isActive={isGameActive} onTimeUpdate={handleTimeUpdate} />
        )}
        
        <div className="mode-indicator">
          {mode === "manual"
            ? isManualModeActive ? "手动模式 - 游戏中" : "手动模式 - 创建中"
            : `自动生成 - ${difficulty?.name || "中等"}`}
        </div>
      </div>

      <div className="game-container">
        <SudokuBoard
          board={board}
          notes={notes}
          selectedCell={selectedCell}
          highlightedNumber={highlightedNumber}
          initialBoard={initialBoard}
          initFlag={mode === "manual" && !isManualModeActive ? 
            Array(9).fill(null).map(() => Array(9).fill(0)) : // 手动模式创建阶段，所有格子都可编辑
            initFlag // 游戏开始后，使用正常的初始格子标识
          }
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
              console.log(`📝 切换笔记模式: ${newNoteMode ? "开启" : "关闭"}`);
              setIsNoteMode(newNoteMode);
            }}
            onClearSelection={clearSelection}
            onResetGame={resetGame}
            onClearAllNotes={clearAllNotes}
          />
        </div>
      </div>

      <div className="game-instructions">
        <h3>游戏说明：</h3>
        {mode === "manual" && !isManualModeActive ? (
          <ul>
            <li>手动模式：点击格子选择，然后点击数字按钮填入数字</li>
            <li>按 N 键或点击笔记按钮切换笔记模式</li>
            <li>笔记模式下可以添加多个数字作为提示</li>
            <li>可以点击"导入"按钮上传JSON或图片文件</li>
            <li>完成数独创建后，点击"完成创建"按钮开始游戏</li>
            <li>使用键盘 1-9 输入数字，Delete 清除</li>
          </ul>
        ) : (
          <ul>
            <li>点击格子选择，然后点击数字按钮填入</li>
            <li>按 N 键或点击笔记按钮切换笔记模式</li>
            <li>笔记模式下可以添加多个数字作为提示</li>
            <li>点击已填入数字的格子会高亮相同数字</li>
            <li>使用键盘 1-9 输入数字，Delete 清除</li>
          </ul>
        )}
      </div>

      {/* 导入对话框 */}
      <ImportDialog
        isOpen={isImportDialogOpen}
        onClose={() => setIsImportDialogOpen(false)}
        onImport={handleImport}
      />

      {/* 测试导入对话框：仅填充空格 */}
      <ImportDialog
        isOpen={isTestDialogOpen}
        onClose={() => setIsTestDialogOpen(false)}
        onImport={handleTestImport}
      />
    </div>
  );
};

export default SudokuGame;
