/**
 * 批量数独生成器使用示例
 * 展示如何使用 BatchSudokuGenerator 类
 */

import { BatchSudokuGenerator, BatchGenerationConfig } from '../utils/batchSudokuGenerator';
import { SudokuGenerator } from '../utils/sudokuGenerator';

// 示例 1: 使用默认配置生成 100 个数独
export async function generateDefaultBatch() {
  console.log('🚀 开始生成默认批次数独...');
  
  const result = await BatchSudokuGenerator.generateBatch();
  
  if (result.success) {
    console.log('✅ 生成成功:', result.message);
    console.log('📁 生成的文件:', result.generatedFiles);
  } else {
    console.error('❌ 生成失败:', result.message);
    console.error('错误详情:', result.errors);
  }
  
  return result;
}

// 示例 2: 自定义配置生成数独
export async function generateCustomBatch() {
  console.log('🚀 开始生成自定义批次数独...');
  
  const config: Partial<BatchGenerationConfig> = {
    count: 50,                    // 生成 50 个数独
    difficulties: [               // 只生成简单和困难难度
      SudokuGenerator.DIFFICULTIES[0],  // 简单
      SudokuGenerator.DIFFICULTIES[3]   // 专家
    ],
    imageSize: 600,               // 图片尺寸 600x600
    backgroundColor: '#F5F5F5',   // 浅灰色背景
    textColor: '#2C3E50',        // 深蓝色文字
    lineColor: '#34495E'          // 深色网格线
  };
  
  const result = await BatchSudokuGenerator.generateBatch(config);
  
  if (result.success) {
    console.log('✅ 自定义生成成功:', result.message);
    console.log('📁 生成的文件:', result.generatedFiles);
  } else {
    console.error('❌ 自定义生成失败:', result.message);
    console.error('错误详情:', result.errors);
  }
  
  return result;
}

// 示例 3: 生成预览图片
export function generatePreviewExample() {
  console.log('🖼️ 生成预览图片示例...');
  
  // 生成一个数独
  const sudoku = SudokuGenerator.generate();
  
  // 生成预览图片
  const previewDataUrl = BatchSudokuGenerator.generatePreviewImage(sudoku.board, {
    imageSize: 400,
    backgroundColor: '#FFFFFF',
    textColor: '#000000',
    lineColor: '#333333'
  });
  
  console.log('✅ 预览图片生成成功');
  console.log('📊 数独难度:', sudoku.difficulty.name);
  console.log('🖼️ 预览图片 data URL:', previewDataUrl.substring(0, 100) + '...');
  
  // 可以将预览图片显示在页面上
  return {
    sudoku,
    previewDataUrl
  };
}

// 示例 4: 批量生成不同难度的数独
export async function generateDifficultyBasedBatch() {
  console.log('🚀 开始生成基于难度的批次数独...');
  
  const difficulties = SudokuGenerator.DIFFICULTIES;
  const countPerDifficulty = 25; // 每个难度生成 25 个
  
  for (const difficulty of difficulties) {
    console.log(`📊 生成 ${difficulty.name} 难度的数独...`);
    
    const config: Partial<BatchGenerationConfig> = {
      count: countPerDifficulty,
      difficulties: [difficulty],
      imageSize: 800,
      backgroundColor: '#FFFFFF',
      textColor: '#000000',
      lineColor: '#333333'
    };
    
    const result = await BatchSudokuGenerator.generateBatch(config);
    
    if (result.success) {
      console.log(`✅ ${difficulty.name} 难度生成成功:`, result.message);
    } else {
      console.error(`❌ ${difficulty.name} 难度生成失败:`, result.message);
    }
  }
}

// 示例 5: 在 React 组件中使用
export function useBatchGenerator() {
  const generateBatch = async (config?: Partial<BatchGenerationConfig>) => {
    try {
      const result = await BatchSudokuGenerator.generateBatch(config);
      return result;
    } catch (error) {
      console.error('批量生成出错:', error);
      return {
        success: false,
        message: `生成失败: ${error}`,
        generatedFiles: [],
        errors: [(error as Error).message]
      };
    }
  };
  
  const generatePreview = (board: number[][], config?: Partial<BatchGenerationConfig>) => {
    return BatchSudokuGenerator.generatePreviewImage(board, config);
  };
  
  return {
    generateBatch,
    generatePreview
  };
}

// 如果直接运行此文件，执行示例
if (typeof window !== 'undefined') {
  // 在浏览器环境中，可以绑定到全局对象供控制台使用
  (window as any).BatchSudokuExamples = {
    generateDefaultBatch,
    generateCustomBatch,
    generatePreviewExample,
    generateDifficultyBasedBatch,
    useBatchGenerator
  };
  
  console.log('📚 批量数独生成器示例已加载到 window.BatchSudokuExamples');
  console.log('💡 使用方法:');
  console.log('  - BatchSudokuExamples.generateDefaultBatch()');
  console.log('  - BatchSudokuExamples.generateCustomBatch()');
  console.log('  - BatchSudokuExamples.generatePreviewExample()');
  console.log('  - BatchSudokuExamples.generateDifficultyBasedBatch()');
}
