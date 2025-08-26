/**
 * 难度选择功能测试
 */

import { SudokuGenerator, SudokuDifficulty } from '../utils/sudokuGenerator';

export function testDifficultySelection() {
  console.log('🧪 测试难度选择功能...\n');
  
  try {
    // 测试1: 生成不同难度的数独
    console.log('📊 测试1: 生成不同难度的数独');
    SudokuGenerator.DIFFICULTIES.forEach(difficulty => {
      const sudoku = SudokuGenerator.generate(difficulty);
      const filledCells = sudoku.board.flat().filter(cell => cell !== 0).length;
      const emptyCells = 81 - filledCells;
      
      console.log(`✅ ${difficulty.name}:`);
      console.log(`   - 描述: ${difficulty.description}`);
      console.log(`   - 预期空格: ${difficulty.cellsToRemove}`);
      console.log(`   - 实际空格: ${emptyCells}`);
      console.log(`   - 实际提示数字: ${filledCells}`);
      console.log(`   - 有效性: ${SudokuGenerator.isValidBoard(sudoku.board) ? '✅ 通过' : '❌ 失败'}`);
      console.log('');
    });
    
    // 测试2: 验证难度评估
    console.log('📈 测试2: 验证难度评估');
    SudokuGenerator.DIFFICULTIES.forEach(difficulty => {
      const sudoku = SudokuGenerator.generate(difficulty);
      const assessment = SudokuGenerator.getDifficultyAssessment(sudoku.board);
      
      console.log(`✅ ${difficulty.name}:`);
      console.log(`   - 预期难度: ${difficulty.name}`);
      console.log(`   - 评估难度: ${assessment.estimatedDifficulty}`);
      console.log(`   - 空格数量: ${assessment.emptyCells}`);
      console.log(`   - 提示数量: ${assessment.filledCells}`);
      console.log('');
    });
    
    // 测试3: 性能测试
    console.log('⚡ 测试3: 性能测试');
    const startTime = performance.now();
    const iterations = 20;
    
    for (let i = 0; i < iterations; i++) {
      const randomDifficulty = SudokuGenerator.DIFFICULTIES[Math.floor(Math.random() * SudokuGenerator.DIFFICULTIES.length)];
      SudokuGenerator.generate(randomDifficulty);
    }
    
    const endTime = performance.now();
    const averageTime = (endTime - startTime) / iterations;
    
    console.log(`✅ 生成 ${iterations} 个不同难度的数独平均耗时: ${averageTime.toFixed(2)}ms`);
    
    console.log('\n🎉 难度选择功能测试完成！');
    return true;
    
  } catch (error) {
    console.error('❌ 测试过程中出现错误:', error);
    return false;
  }
}

// 如果直接运行此文件，执行测试
if (typeof window === 'undefined') {
  // Node.js 环境
  testDifficultySelection();
}
