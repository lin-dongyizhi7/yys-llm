/**
 * 数独生成器测试文件
 * 用于验证生成器的各种功能
 */

import { SudokuGenerator, SudokuDifficulty } from './sudokuGenerator';

// 测试数独生成器的基本功能
export function testSudokuGenerator() {
  console.log('🧪 开始测试数独生成器...');
  
  try {
    // 测试1: 生成不同难度的数独
    console.log('\n📊 测试1: 生成不同难度的数独');
    SudokuGenerator.DIFFICULTIES.forEach(difficulty => {
      const sudoku = SudokuGenerator.generate(difficulty);
      console.log(`✅ ${difficulty.name}: 生成了 ${sudoku.board.flat().filter(cell => cell !== 0).length} 个数字`);
      
      // 验证生成的数独是否有效
      const isValid = SudokuGenerator.isValidBoard(sudoku.board);
      console.log(`   - 有效性检查: ${isValid ? '✅ 通过' : '❌ 失败'}`);
      
      // 验证解答是否正确
      const isSolutionValid = SudokuGenerator.isValidBoard(sudoku.solution);
      console.log(`   - 解答有效性: ${isSolutionValid ? '✅ 通过' : '❌ 失败'}`);
    });
    
    // 测试2: 验证数独解答
    console.log('\n🔍 测试2: 验证数独解答');
    const sudoku = SudokuGenerator.generate();
    const isSolved = SudokuGenerator.isSolved(sudoku.solution);
    console.log(`✅ 完整解答验证: ${isSolved ? '通过' : '失败'}`);
    
    // 测试3: 难度评估
    console.log('\n📈 测试3: 难度评估');
    const assessment = SudokuGenerator.getDifficultyAssessment(sudoku.board);
    console.log(`✅ 难度评估: ${assessment.estimatedDifficulty}`);
    console.log(`   - 已填格子: ${assessment.filledCells}`);
    console.log(`   - 空格子: ${assessment.emptyCells}`);
    
    // 测试4: 对称数独生成
    console.log('\n🔄 测试4: 对称数独生成');
    const symmetricSudoku = SudokuGenerator.generateSymmetric();
    console.log(`✅ 对称数独生成成功`);
    
    // 测试5: 边界情况
    console.log('\n⚠️ 测试5: 边界情况');
    const emptyBoard = Array(9).fill(null).map(() => Array(9).fill(0));
    const isValidEmpty = SudokuGenerator.isValidBoard(emptyBoard);
    console.log(`✅ 空白板验证: ${isValidEmpty ? '通过' : '失败'}`);
    
    const isSolvedEmpty = SudokuGenerator.isSolved(emptyBoard);
    console.log(`✅ 空白板解答状态: ${isSolvedEmpty ? '已解答' : '未解答'}`);
    
    console.log('\n🎉 所有测试完成！');
    return true;
    
  } catch (error) {
    console.error('❌ 测试过程中出现错误:', error);
    return false;
  }
}

// 测试数独生成性能
export function testPerformance() {
  console.log('\n⚡ 性能测试开始...');
  
  const startTime = performance.now();
  const iterations = 10;
  
  for (let i = 0; i < iterations; i++) {
    SudokuGenerator.generate();
  }
  
  const endTime = performance.now();
  const averageTime = (endTime - startTime) / iterations;
  
  console.log(`✅ 生成 ${iterations} 个数独平均耗时: ${averageTime.toFixed(2)}ms`);
  return averageTime;
}

// 测试数独的唯一性
export function testUniqueness() {
  console.log('\n🎲 唯一性测试开始...');
  
  const sudokus = new Set<string>();
  const iterations = 20;
  
  for (let i = 0; i < iterations; i++) {
    const sudoku = SudokuGenerator.generate();
    const boardString = sudoku.board.flat().join('');
    sudokus.add(boardString);
  }
  
  const uniqueness = (sudokus.size / iterations) * 100;
  console.log(`✅ 生成 ${iterations} 个数独，唯一性: ${uniqueness.toFixed(1)}%`);
  
  return uniqueness;
}

// 运行所有测试
export function runAllTests() {
  console.log('🚀 运行数独生成器完整测试套件\n');
  
  const results = {
    basic: testSudokuGenerator(),
    performance: testPerformance(),
    uniqueness: testUniqueness()
  };
  
  console.log('\n📋 测试结果汇总:');
  console.log(`   - 基本功能: ${results.basic ? '✅ 通过' : '❌ 失败'}`);
  console.log(`   - 性能测试: ✅ 完成`);
  console.log(`   - 唯一性测试: ✅ 完成`);
  
  return results;
}

// 如果直接运行此文件，执行所有测试
if (typeof window === 'undefined') {
  // Node.js 环境
  runAllTests();
}
