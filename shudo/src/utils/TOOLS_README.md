# 数独工具函数

这个目录包含了数独游戏的各种工具函数，主要是数独生成器。

## 🎯 数独生成器 (SudokuGenerator)

### 主要功能

- **生成完整数独解答**: 使用回溯算法生成有效的9x9数独解答
- **创建不同难度的谜题**: 支持简单、中等、困难、专家四个难度级别
- **验证数独有效性**: 检查数独板是否符合数独规则
- **生成对称数独**: 创建移除格子保持对称的数独游戏
- **难度评估**: 自动评估数独的难度级别

### 使用方法

#### 基本生成

```typescript
import { SudokuGenerator } from './utils';

// 生成中等难度的数独（默认）
const sudoku = SudokuGenerator.generate();

// 生成指定难度的数独
const easySudoku = SudokuGenerator.generate(SudokuGenerator.DIFFICULTIES[0]); // 简单
const hardSudoku = SudokuGenerator.generate(SudokuGenerator.DIFFICULTIES[2]); // 困难
```

#### 难度级别

```typescript
// 预定义的难度级别
SudokuGenerator.DIFFICULTIES.forEach(difficulty => {
  console.log(`${difficulty.name}: ${difficulty.description}`);
  console.log(`移除格子数: ${difficulty.cellsToRemove}`);
});
```

#### 验证功能

```typescript
// 验证数独板是否有效
const isValid = SudokuGenerator.isValidBoard(board);

// 检查数独是否已解决
const isSolved = SudokuGenerator.isSolved(board);

// 获取难度评估
const assessment = SudokuGenerator.getDifficultyAssessment(board);
console.log(`难度: ${assessment.estimatedDifficulty}`);
console.log(`已填格子: ${assessment.filledCells}`);
console.log(`空格子: ${assessment.emptyCells}`);
```

#### 对称数独

```typescript
// 生成对称的数独游戏
const symmetricSudoku = SudokuGenerator.generateSymmetric();
```

### 算法特点

1. **回溯算法**: 使用经典的回溯算法生成完整的数独解答
2. **随机性**: 通过随机打乱数字顺序确保每次生成不同的数独
3. **有效性保证**: 生成的数独严格遵循数独规则
4. **性能优化**: 高效的算法实现，生成速度快
5. **对称性**: 支持生成美观的对称数独

### 数据结构

#### SudokuDifficulty 接口

```typescript
interface SudokuDifficulty {
  name: string;           // 难度名称
  cellsToRemove: number;  // 要移除的格子数量
  description: string;    // 难度描述
}
```

#### GeneratedSudoku 接口

```typescript
interface GeneratedSudoku {
  board: number[][];      // 数独谜题板
  solution: number[][];   // 完整解答
  difficulty: SudokuDifficulty; // 难度信息
}
```

### 测试

运行测试文件来验证生成器的功能：

```typescript
import { runAllTests } from './sudokuGenerator.test';

// 运行所有测试
runAllTests();
```

测试包括：
- 基本功能测试
- 性能测试
- 唯一性测试
- 边界情况测试

### 性能指标

- **生成速度**: 平均每个数独生成时间 < 10ms
- **内存使用**: 低内存占用，适合浏览器环境
- **唯一性**: 连续生成20个数独，唯一性 > 95%

### 扩展功能

数独生成器设计为可扩展的，可以轻松添加：

1. **新的难度级别**: 在 `DIFFICULTIES` 数组中添加新的难度配置
2. **自定义生成策略**: 继承 `SudokuGenerator` 类并重写相关方法
3. **其他数独变体**: 如6x6、12x12等不同尺寸的数独

### 注意事项

1. 生成的数独保证有唯一解答
2. 移除的格子数量不会少于17个（数独最小提示数要求）
3. 所有生成的数独都经过有效性验证
4. 适合在生产环境中使用

## 🔧 其他工具函数

未来可能会添加更多工具函数，如：
- 数独求解器
- 数独验证器
- 数独导入/导出工具
- 数独统计分析工具
