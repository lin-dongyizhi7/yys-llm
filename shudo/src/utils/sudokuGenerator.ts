/**
 * 数独生成器
 * 提供完整的数独游戏生成功能，包括多种难度级别
 */

export interface SudokuDifficulty {
  name: string;
  cellsToRemove: number;
  description: string;
}

export interface GeneratedSudoku {
  board: number[][];
  solution: number[][];
  difficulty: SudokuDifficulty;
}

export class SudokuGenerator {
  private static readonly BOARD_SIZE = 9;
  private static readonly BOX_SIZE = 3;
  
  // 预定义的难度级别
  public static readonly DIFFICULTIES: SudokuDifficulty[] = [
    { name: '简单', cellsToRemove: 30, description: '适合初学者，有较多提示数字' },
    { name: '中等', cellsToRemove: 40, description: '平衡的挑战性，适中的提示数量' },
    { name: '困难', cellsToRemove: 50, description: '较高挑战性，较少的提示数字' },
    { name: '专家', cellsToRemove: 60, description: '极高挑战性，最少的提示数字' }
  ];

  /**
   * 生成一个完整的数独游戏
   * @param difficulty 难度级别，默认为中等
   * @returns 包含数独板、解答和难度信息的对象
   */
  public static generate(difficulty: SudokuDifficulty = this.DIFFICULTIES[1]): GeneratedSudoku {
    // 首先生成一个完整的解答
    const solution = this.generateCompleteSolution();
    
    // 然后根据难度移除一些数字
    const board = this.createPuzzle(solution, difficulty.cellsToRemove);
    
    return {
      board,
      solution,
      difficulty
    };
  }

  /**
   * 生成一个完整的数独解答
   * @returns 9x9的完整数独解答
   */
  private static generateCompleteSolution(): number[][] {
    const board = Array(this.BOARD_SIZE).fill(null).map(() => Array(this.BOARD_SIZE).fill(0));
    
    // 使用回溯算法生成完整的数独
    this.solveSudoku(board);
    
    return board;
  }

  /**
   * 使用回溯算法解决数独
   * @param board 数独板
   * @returns 是否成功解决
   */
  private static solveSudoku(board: number[][]): boolean {
    for (let row = 0; row < this.BOARD_SIZE; row++) {
      for (let col = 0; col < this.BOARD_SIZE; col++) {
        if (board[row][col] === 0) {
          // 随机打乱数字顺序，增加生成的随机性
          const numbers = this.shuffleArray([1, 2, 3, 4, 5, 6, 7, 8, 9]);
          
          for (const num of numbers) {
            if (this.isValidMove(board, row, col, num)) {
              board[row][col] = num;
              
              if (this.solveSudoku(board)) {
                return true;
              }
              
              board[row][col] = 0;
            }
          }
          return false;
        }
      }
    }
    return true;
  }

  /**
   * 检查在指定位置放置数字是否有效
   * @param board 数独板
   * @param row 行索引
   * @param col 列索引
   * @param num 要放置的数字
   * @returns 是否有效
   */
  private static isValidMove(board: number[][], row: number, col: number, num: number): boolean {
    // 检查行
    for (let c = 0; c < this.BOARD_SIZE; c++) {
      if (board[row][c] === num) return false;
    }
    
    // 检查列
    for (let r = 0; r < this.BOARD_SIZE; r++) {
      if (board[r][col] === num) return false;
    }
    
    // 检查3x3宫格
    const boxRow = Math.floor(row / this.BOX_SIZE) * this.BOX_SIZE;
    const boxCol = Math.floor(col / this.BOX_SIZE) * this.BOX_SIZE;
    
    for (let r = boxRow; r < boxRow + this.BOX_SIZE; r++) {
      for (let c = boxCol; c < boxCol + this.BOX_SIZE; c++) {
        if (board[r][c] === num) return false;
      }
    }
    
    return true;
  }

  /**
   * 从完整解答创建谜题
   * @param solution 完整解答
   * @param cellsToRemove 要移除的数字数量
   * @returns 谜题板
   */
  private static createPuzzle(solution: number[][], cellsToRemove: number): number[][] {
    const board = solution.map(row => [...row]);
    const totalCells = this.BOARD_SIZE * this.BOARD_SIZE;
    
    // 确保不会移除太多数字
    const actualCellsToRemove = Math.min(cellsToRemove, totalCells - 17);
    
    // 随机选择要移除的格子
    const positions = this.generateRandomPositions(totalCells, actualCellsToRemove);
    
    for (const pos of positions) {
      const row = Math.floor(pos / this.BOARD_SIZE);
      const col = pos % this.BOARD_SIZE;
      board[row][col] = 0;
    }
    
    return board;
  }

  /**
   * 生成随机位置数组
   * @param total 总位置数
   * @param count 需要的随机位置数
   * @returns 随机位置数组
   */
  private static generateRandomPositions(total: number, count: number): number[] {
    const positions = Array.from({ length: total }, (_, i) => i);
    const result: number[] = [];
    
    for (let i = 0; i < count; i++) {
      const randomIndex = Math.floor(Math.random() * positions.length);
      result.push(positions[randomIndex]);
      positions.splice(randomIndex, 1);
    }
    
    return result;
  }

  /**
   * 打乱数组顺序
   * @param array 要打乱的数组
   * @returns 打乱后的数组
   */
  private static shuffleArray<T>(array: T[]): T[] {
    const shuffled = [...array];
    for (let i = shuffled.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
    }
    return shuffled;
  }

  /**
   * 验证数独板是否有效
   * @param board 数独板
   * @returns 是否有效
   */
  public static isValidBoard(board: number[][]): boolean {
    // 检查行
    for (let row = 0; row < this.BOARD_SIZE; row++) {
      const rowNumbers = new Set<number>();
      for (let col = 0; col < this.BOARD_SIZE; col++) {
        if (board[row][col] !== 0) {
          if (rowNumbers.has(board[row][col])) return false;
          rowNumbers.add(board[row][col]);
        }
      }
    }
    
    // 检查列
    for (let col = 0; col < this.BOARD_SIZE; col++) {
      const colNumbers = new Set<number>();
      for (let row = 0; row < this.BOARD_SIZE; row++) {
        if (board[row][col] !== 0) {
          if (colNumbers.has(board[row][col])) return false;
          colNumbers.add(board[row][col]);
        }
      }
    }
    
    // 检查3x3宫格
    for (let boxRow = 0; boxRow < this.BOARD_SIZE; boxRow += this.BOX_SIZE) {
      for (let boxCol = 0; boxCol < this.BOARD_SIZE; boxCol += this.BOX_SIZE) {
        const boxNumbers = new Set<number>();
        for (let r = boxRow; r < boxRow + this.BOX_SIZE; r++) {
          for (let c = boxCol; c < boxCol + this.BOX_SIZE; c++) {
            if (board[r][c] !== 0) {
              if (boxNumbers.has(board[r][c])) return false;
              boxNumbers.add(board[r][c]);
            }
          }
        }
      }
    }
    
    return true;
  }

  /**
   * 检查数独是否已解决
   * @param board 数独板
   * @returns 是否已解决
   */
  public static isSolved(board: number[][]): boolean {
    // 检查是否有空格
    for (let row = 0; row < this.BOARD_SIZE; row++) {
      for (let col = 0; col < this.BOARD_SIZE; col++) {
        if (board[row][col] === 0) return false;
      }
    }
    
    // 检查是否有效
    return this.isValidBoard(board);
  }

  /**
   * 获取数独的难度评估
   * @param board 数独板
   * @returns 难度评估信息
   */
  public static getDifficultyAssessment(board: number[][]): {
    filledCells: number;
    emptyCells: number;
    estimatedDifficulty: string;
  } {
    let filledCells = 0;
    let emptyCells = 0;
    
    for (let row = 0; row < this.BOARD_SIZE; row++) {
      for (let col = 0; col < this.BOARD_SIZE; col++) {
        if (board[row][col] === 0) {
          emptyCells++;
        } else {
          filledCells++;
        }
      }
    }
    
    let estimatedDifficulty = '未知';
    if (emptyCells <= 30) estimatedDifficulty = '简单';
    else if (emptyCells <= 40) estimatedDifficulty = '中等';
    else if (emptyCells <= 50) estimatedDifficulty = '困难';
    else estimatedDifficulty = '专家';
    
    return {
      filledCells,
      emptyCells,
      estimatedDifficulty
    };
  }

  /**
   * 生成一个对称的数独（移除的格子保持对称）
   * @param difficulty 难度级别
   * @returns 对称的数独游戏
   */
  public static generateSymmetric(difficulty: SudokuDifficulty = this.DIFFICULTIES[1]): GeneratedSudoku {
    const solution = this.generateCompleteSolution();
    const board = solution.map(row => [...row]);
    
    const totalCells = this.BOARD_SIZE * this.BOARD_SIZE;
    const actualCellsToRemove = Math.min(difficulty.cellsToRemove, totalCells - 17);
    
    // 生成对称的移除位置
    const positions = this.generateSymmetricPositions(actualCellsToRemove);
    
    for (const pos of positions) {
      const row = Math.floor(pos / this.BOARD_SIZE);
      const col = pos % this.BOARD_SIZE;
      board[row][col] = 0;
    }
    
    return {
      board,
      solution,
      difficulty
    };
  }

  /**
   * 生成对称的移除位置
   * @param count 要移除的格子数量
   * @returns 对称的位置数组
   */
  private static generateSymmetricPositions(count: number): number[] {
    const positions: number[] = [];
    const center = Math.floor(this.BOARD_SIZE / 2);
    
    // 生成对称的位置对
    for (let row = 0; row < center; row++) {
      for (let col = 0; col < this.BOARD_SIZE; col++) {
        if (positions.length >= count) break;
        
        const pos1 = row * this.BOARD_SIZE + col;
        const pos2 = (this.BOARD_SIZE - 1 - row) * this.BOARD_SIZE + (this.BOARD_SIZE - 1 - col);
        
        if (Math.random() < 0.5) {
          positions.push(pos1);
          if (positions.length < count && pos1 !== pos2) {
            positions.push(pos2);
          }
        }
      }
    }
    
    // 处理中间行（如果还有位置需要填充）
    if (positions.length < count) {
      for (let col = 0; col < center; col++) {
        if (positions.length >= count) break;
        
        const pos1 = center * this.BOARD_SIZE + col;
        const pos2 = center * this.BOARD_SIZE + (this.BOARD_SIZE - 1 - col);
        
        if (Math.random() < 0.5) {
          positions.push(pos1);
          if (positions.length < count && pos1 !== pos2) {
            positions.push(pos2);
          }
        }
      }
    }
    
    return positions.slice(0, count);
  }
}
