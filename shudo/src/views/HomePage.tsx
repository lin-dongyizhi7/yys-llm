import React, { useState } from "react";
import "./HomePage.css";
import { GameMode } from "../App";
import { SudokuGenerator, SudokuDifficulty, BatchSudokuGenerator, BatchGenerationConfig } from "../utils";

interface HomePageProps {
  onModeSelect: (mode: GameMode, difficulty?: SudokuDifficulty) => void;
}

const HomePage: React.FC<HomePageProps> = ({ onModeSelect }) => {
  const [showDifficultySelection, setShowDifficultySelection] = useState(false);
  const [showBatchGeneration, setShowBatchGeneration] = useState(false);
  const [batchConfig, setBatchConfig] = useState<Partial<BatchGenerationConfig>>({
    count: 50,
    difficulties: SudokuGenerator.DIFFICULTIES,
    imageSize: 800,
    backgroundColor: '#FFFFFF',
    textColor: '#000000',
    lineColor: '#333333'
  });
  const [isGenerating, setIsGenerating] = useState(false);
  const [generationProgress, setGenerationProgress] = useState<string>('');
  const [generationResult, setGenerationResult] = useState<any>(null);

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
    setShowBatchGeneration(false);
    setGenerationResult(null);
  };

  const handleBatchGenerateMode = () => {
    setShowBatchGeneration(true);
  };

  const handleBatchGenerate = async () => {
    if (!batchConfig.count || batchConfig.count <= 0) {
      alert('请输入有效的生成数量');
      return;
    }

    setIsGenerating(true);
    setGenerationProgress('🚀 开始批量生成数独...');
    setGenerationResult(null);

    try {
      // 模拟进度更新
      const progressInterval = setInterval(() => {
        setGenerationProgress(prev => {
          if (prev.includes('生成中')) {
            return prev + '.';
          }
          return prev + ' 生成中';
        });
      }, 500);

      const result = await BatchSudokuGenerator.generateBatch(batchConfig);
      
      clearInterval(progressInterval);
      setGenerationResult(result);
      
      if (result.success) {
        setGenerationProgress('✅ 批量生成完成！');
      } else {
        setGenerationProgress('❌ 批量生成失败');
      }
    } catch (error) {
      setGenerationProgress('❌ 生成过程中出现错误');
      console.error('批量生成错误:', error);
    } finally {
      setIsGenerating(false);
    }
  };

  const handleConfigChange = (key: keyof BatchGenerationConfig, value: any) => {
    setBatchConfig((prev: Partial<BatchGenerationConfig>) => ({
      ...prev,
      [key]: value
    }));
  };

  const handleDifficultyToggle = (difficulty: SudokuDifficulty) => {
    setBatchConfig((prev: Partial<BatchGenerationConfig>) => {
      const currentDifficulties = prev.difficulties || [];
      const isSelected = currentDifficulties.some((d: SudokuDifficulty) => d.name === difficulty.name);
      
      if (isSelected) {
        return {
          ...prev,
          difficulties: currentDifficulties.filter((d: SudokuDifficulty) => d.name !== difficulty.name)
        };
      } else {
        return {
          ...prev,
          difficulties: [...currentDifficulties, difficulty]
        };
      }
    });
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

  if (showBatchGeneration) {
    return (
      <div className="home-page">
        <h1 className="title">批量生成数独</h1>
        <div className="batch-generation">
          <h2>配置生成参数</h2>
          
          <div className="config-section">
            <h3>生成数量</h3>
            <input
              type="number"
              min="1"
              max="1000"
              value={batchConfig.count || 50}
              onChange={(e) => handleConfigChange('count', parseInt(e.target.value) || 50)}
              className="config-input"
              disabled={isGenerating}
            />
            <span className="config-hint">建议数量: 1-1000</span>
          </div>

          <div className="config-section">
            <h3>难度选择</h3>
            <div className="difficulty-checkboxes">
              {SudokuGenerator.DIFFICULTIES.map((difficulty) => {
                const isSelected = batchConfig.difficulties?.some(d => d.name === difficulty.name) || false;
                return (
                  <label key={difficulty.name} className="difficulty-checkbox">
                    <input
                      type="checkbox"
                      checked={isSelected}
                      onChange={() => handleDifficultyToggle(difficulty)}
                      disabled={isGenerating}
                    />
                    <span className="checkbox-label">
                      {difficulty.name} ({difficulty.description})
                    </span>
                  </label>
                );
              })}
            </div>
          </div>

          <div className="config-section">
            <h3>图片设置</h3>
            <div className="image-config">
              <div className="config-row">
                <label>图片尺寸:</label>
                <select
                  value={batchConfig.imageSize || 800}
                  onChange={(e) => handleConfigChange('imageSize', parseInt(e.target.value))}
                  disabled={isGenerating}
                  className="config-select"
                >
                  <option value={600}>600x600</option>
                  <option value={800}>800x800</option>
                  <option value={900}>900x900</option>
                  <option value={1200}>1200x1200</option>
                </select>
              </div>
              
              <div className="config-row">
                <label>背景颜色:</label>
                <input
                  type="color"
                  value={batchConfig.backgroundColor || '#FFFFFF'}
                  onChange={(e) => handleConfigChange('backgroundColor', e.target.value)}
                  disabled={isGenerating}
                  className="config-color"
                />
              </div>
              
              <div className="config-row">
                <label>文字颜色:</label>
                <input
                  type="color"
                  value={batchConfig.textColor || '#000000'}
                  onChange={(e) => handleConfigChange('textColor', e.target.value)}
                  disabled={isGenerating}
                  className="config-color"
                />
              </div>
              
              <div className="config-row">
                <label>网格线颜色:</label>
                <input
                  type="color"
                  value={batchConfig.lineColor || '#333333'}
                  onChange={(e) => handleConfigChange('lineColor', e.target.value)}
                  disabled={isGenerating}
                  className="config-color"
                />
              </div>
            </div>
          </div>

          <div className="action-buttons">
            <button
              className="generate-button"
              onClick={handleBatchGenerate}
              disabled={isGenerating || !batchConfig.difficulties?.length}
            >
              {isGenerating ? '生成中...' : '🚀 开始生成'}
            </button>
            
            <button
              className="back-button"
              onClick={handleBackToModes}
              disabled={isGenerating}
            >
              ← 返回模式选择
            </button>
          </div>

          {generationProgress && (
            <div className="generation-progress">
              <p>{generationProgress}</p>
            </div>
          )}

          {generationResult && (
            <div className="generation-result">
              <h3>生成结果</h3>
              <div className={`result-message ${generationResult.success ? 'success' : 'error'}`}>
                {generationResult.message}
              </div>
              
              {generationResult.success && (
                <div className="result-details">
                  <p>📁 生成文件数: {generationResult.generatedFiles.length}</p>
                  <p>💾 文件已下载到浏览器默认下载目录</p>
                  <p>📂 建议将文件移动到 shudo/data/ 目录下</p>
                </div>
              )}
              
              {generationResult.errors.length > 0 && (
                <div className="result-errors">
                  <h4>错误详情:</h4>
                  <ul>
                    {generationResult.errors.map((error: string, index: number) => (
                      <li key={index}>{error}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}
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
          <button className="mode-button batch" onClick={handleBatchGenerateMode}>
            <h3>批量生成</h3>
            <p>批量生成大量数独数据，支持JSON和图片导出</p>
          </button>
        </div>
      </div>
    </div>
  );
};

export default HomePage;
