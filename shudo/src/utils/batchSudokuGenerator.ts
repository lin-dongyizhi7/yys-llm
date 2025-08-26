/**
 * 批量数独数据生成器
 * 生成数独 JSON 文件和 PNG 图片，用于训练和测试
 */

import { SudokuGenerator, GeneratedSudoku, SudokuDifficulty } from './sudokuGenerator';

export interface BatchGenerationConfig {
  count: number;
  difficulties: SudokuDifficulty[];
  outputDir: string;
  imageSize: number;
  cellPadding: number;
  lineWidth: number;
  backgroundColor: string;
  textColor: string;
  lineColor: string;
}

export interface GenerationResult {
  success: boolean;
  message: string;
  generatedFiles: string[];
  errors: string[];
}

export class BatchSudokuGenerator {
  private static readonly DEFAULT_CONFIG: BatchGenerationConfig = {
    count: 100,
    difficulties: SudokuGenerator.DIFFICULTIES,
    outputDir: 'data',
    imageSize: 900,
    cellPadding: 10,
    lineWidth: 2,
    backgroundColor: '#FFFFFF',
    textColor: '#000000',
    lineColor: '#333333'
  };

  /**
   * 批量生成数独数据
   * @param config 生成配置
   * @returns 生成结果
   */
  public static async generateBatch(config: Partial<BatchGenerationConfig> = {}): Promise<GenerationResult> {
    const finalConfig = { ...this.DEFAULT_CONFIG, ...config };
    const result: GenerationResult = {
      success: true,
      message: '',
      generatedFiles: [],
      errors: []
    };

    try {
      console.log(`🚀 开始批量生成 ${finalConfig.count} 个数独...`);
      
      // 创建输出目录
      const jsonDir = `${finalConfig.outputDir}/json`;
      const imageDir = `${finalConfig.outputDir}/image`;
      
      await this.ensureDirectory(jsonDir);
      await this.ensureDirectory(imageDir);

      // 生成数独数据
      const sudokus: GeneratedSudoku[] = [];
      for (let i = 0; i < finalConfig.count; i++) {
        const difficulty = finalConfig.difficulties[i % finalConfig.difficulties.length];
        const sudoku = SudokuGenerator.generate(difficulty);
        sudokus.push(sudoku);
      }

      // 保存 JSON 文件
      const jsonFiles = await this.saveJsonFiles(sudokus, jsonDir);
      result.generatedFiles.push(...jsonFiles);

      // 生成并保存图片
      const imageFiles = await this.generateImages(sudokus, imageDir, finalConfig);
      result.generatedFiles.push(...imageFiles);

      result.message = `✅ 成功生成 ${finalConfig.count} 个数独！\nJSON文件: ${jsonFiles.length} 个\n图片文件: ${imageFiles.length} 个`;
      console.log(result.message);

    } catch (error) {
      result.success = false;
      result.message = `❌ 批量生成失败: ${error}`;
      result.errors.push(error.toString());
      console.error(result.message);
    }

    return result;
  }

  /**
   * 确保目录存在
   * @param dirPath 目录路径
   */
  private static async ensureDirectory(dirPath: string): Promise<void> {
    try {
      // 在浏览器环境中，我们无法直接创建目录
      // 这里只是记录日志，实际目录创建需要在 Node.js 环境中进行
      console.log(`📁 确保目录存在: ${dirPath}`);
    } catch (error) {
      console.warn(`⚠️ 无法创建目录 ${dirPath}: ${error}`);
    }
  }

  /**
   * 保存 JSON 文件
   * @param sudokus 数独数据数组
   * @param outputDir 输出目录
   * @returns 生成的文件路径数组
   */
  private static async saveJsonFiles(sudokus: GeneratedSudoku[], outputDir: string): Promise<string[]> {
    const files: string[] = [];
    
    for (let i = 0; i < sudokus.length; i++) {
      const sudoku = sudokus[i];
      const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
      const filename = `${timestamp}-${sudoku.difficulty.name}-${i + 1}.json`;
      const filepath = `${outputDir}/${filename}`;
      
      const jsonData = {
        data: sudoku.board,
        solution: sudoku.solution,
        difficulty: sudoku.difficulty.name,
        generatedAt: new Date().toISOString()
      };

      try {
        // 在浏览器环境中，我们使用下载方式保存文件
        await this.downloadJsonFile(jsonData, filename);
        files.push(filepath);
        console.log(`💾 保存 JSON: ${filename}`);
      } catch (error) {
        console.error(`❌ 保存 JSON 失败 ${filename}: ${error}`);
      }
    }

    return files;
  }

  /**
   * 下载 JSON 文件
   * @param data 要保存的数据
   * @param filename 文件名
   */
  private static async downloadJsonFile(data: any, filename: string): Promise<void> {
    const jsonString = JSON.stringify(data, null, 2);
    const blob = new Blob([jsonString], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    URL.revokeObjectURL(url);
  }

  /**
   * 生成并保存图片
   * @param sudokus 数独数据数组
   * @param outputDir 输出目录
   * @param config 配置
   * @returns 生成的文件路径数组
   */
  private static async generateImages(sudokus: GeneratedSudoku[], outputDir: string, config: BatchGenerationConfig): Promise<string[]> {
    const files: string[] = [];
    
    for (let i = 0; i < sudokus.length; i++) {
      const sudoku = sudokus[i];
      const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
      const filename = `${timestamp}-${sudoku.difficulty.name}-${i + 1}.png`;
      const filepath = `${outputDir}/${filename}`;
      
      try {
        const imageBlob = await this.generateSudokuImage(sudoku.board, config);
        await this.downloadImageFile(imageBlob, filename);
        files.push(filepath);
        console.log(`🖼️ 生成图片: ${filename}`);
      } catch (error) {
        console.error(`❌ 生成图片失败 ${filename}: ${error}`);
      }
    }

    return files;
  }

  /**
   * 生成数独图片
   * @param board 数独板
   * @param config 配置
   * @returns 图片 Blob
   */
  private static async generateSudokuImage(board: number[][], config: BatchGenerationConfig): Promise<Blob> {
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d')!;
    
    canvas.width = config.imageSize;
    canvas.height = config.imageSize;
    
    // 设置背景
    ctx.fillStyle = config.backgroundColor;
    ctx.fillRect(0, 0, config.imageSize, config.imageSize);
    
    const cellSize = (config.imageSize - config.lineWidth * 4) / 9;
    
    // 绘制网格线
    ctx.strokeStyle = config.lineColor;
    ctx.lineWidth = config.lineWidth;
    
    // 绘制细线（3x3宫格内的线）
    for (let i = 0; i <= 9; i++) {
      const x = config.lineWidth * 2 + i * cellSize;
      ctx.lineWidth = (i % 3 === 0) ? config.lineWidth * 2 : config.lineWidth;
      ctx.beginPath();
      ctx.moveTo(x, config.lineWidth * 2);
      ctx.lineTo(x, config.imageSize - config.lineWidth * 2);
      ctx.stroke();
    }
    
    for (let i = 0; i <= 9; i++) {
      const y = config.lineWidth * 2 + i * cellSize;
      ctx.lineWidth = (i % 3 === 0) ? config.lineWidth * 2 : config.lineWidth;
      ctx.beginPath();
      ctx.moveTo(config.lineWidth * 2, y);
      ctx.lineTo(config.imageSize - config.lineWidth * 2, y);
      ctx.stroke();
    }
    
    // 绘制数字
    ctx.fillStyle = config.textColor;
    ctx.font = `${cellSize * 0.6}px Arial`;
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    
    for (let row = 0; row < 9; row++) {
      for (let col = 0; col < 9; col++) {
        const value = board[row][col];
        if (value !== 0) {
          const x = config.lineWidth * 2 + col * cellSize + cellSize / 2;
          const y = config.lineWidth * 2 + row * cellSize + cellSize / 2;
          ctx.fillText(value.toString(), x, y);
        }
      }
    }
    
    // 转换为 Blob
    return new Promise((resolve) => {
      canvas.toBlob((blob) => {
        resolve(blob!);
      }, 'image/png');
    });
  }

  /**
   * 下载图片文件
   * @param blob 图片 Blob
   * @param filename 文件名
   */
  private static async downloadImageFile(blob: Blob, filename: string): Promise<void> {
    const url = URL.createObjectURL(blob);
    
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    URL.revokeObjectURL(url);
  }

  /**
   * 生成单个数独的图片（用于预览）
   * @param board 数独板
   * @param config 配置
   * @returns 图片的 data URL
   */
  public static generatePreviewImage(board: number[][], config: Partial<BatchGenerationConfig> = {}): string {
    const finalConfig = { ...this.DEFAULT_CONFIG, ...config };
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d')!;
    
    canvas.width = finalConfig.imageSize;
    canvas.height = finalConfig.imageSize;
    
    // 设置背景
    ctx.fillStyle = finalConfig.backgroundColor;
    ctx.fillRect(0, 0, finalConfig.imageSize, finalConfig.imageSize);
    
    const cellSize = (finalConfig.imageSize - finalConfig.lineWidth * 4) / 9;
    
    // 绘制网格线
    ctx.strokeStyle = finalConfig.lineColor;
    ctx.lineWidth = finalConfig.lineWidth;
    
    // 绘制细线（3x3宫格内的线）
    for (let i = 0; i <= 9; i++) {
      const x = finalConfig.lineWidth * 2 + i * cellSize;
      ctx.lineWidth = (i % 3 === 0) ? finalConfig.lineWidth * 2 : finalConfig.lineWidth;
      ctx.beginPath();
      ctx.moveTo(x, finalConfig.lineWidth * 2);
      ctx.lineTo(x, finalConfig.imageSize - finalConfig.lineWidth * 2);
      ctx.stroke();
    }
    
    for (let i = 0; i <= 9; i++) {
      const y = finalConfig.lineWidth * 2 + i * cellSize;
      ctx.fillStyle = finalConfig.backgroundColor;
      ctx.lineWidth = (i % 3 === 0) ? finalConfig.lineWidth * 2 : finalConfig.lineWidth;
      ctx.beginPath();
      ctx.moveTo(finalConfig.lineWidth * 2, y);
      ctx.lineTo(finalConfig.imageSize - finalConfig.lineWidth * 2, y);
      ctx.stroke();
    }
    
    // 绘制数字
    ctx.fillStyle = finalConfig.textColor;
    ctx.font = `${cellSize * 0.6}px Arial`;
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    
    for (let row = 0; row < 9; row++) {
      for (let col = 0; col < 9; col++) {
        const value = board[row][col];
        if (value !== 0) {
          const x = finalConfig.lineWidth * 2 + col * cellSize + cellSize / 2;
          const y = finalConfig.lineWidth * 2 + row * cellSize + cellSize / 2;
          ctx.fillText(value.toString(), x, y);
        }
      }
    }
    
    return canvas.toDataURL('image/png');
  }
}
