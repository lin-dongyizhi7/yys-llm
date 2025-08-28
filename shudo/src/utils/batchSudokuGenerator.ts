/**
 * 批量数独数据生成器
 * 生成数独 JSON 文件和 PNG 图片，并打包为压缩包下载
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
  zipBlob?: Blob;
  zipFilename?: string;
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

      // 使用统一的时间戳和索引生成文件名
      const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
      
      // 保存 JSON 文件到内存
      const jsonFiles = await this.generateJsonFiles(sudokus, jsonDir, timestamp);
      result.generatedFiles.push(...jsonFiles.map(f => f.path));

      // 生成图片到内存
      const imageFiles = await this.generateImages(sudokus, imageDir, finalConfig, timestamp);
      result.generatedFiles.push(...imageFiles.map(f => f.path));

      // 创建压缩包
      const zipResult = await this.createZipPackage(jsonFiles, imageFiles, finalConfig);
      if (zipResult.success) {
        result.zipBlob = zipResult.blob;
        result.zipFilename = zipResult.filename;
        result.message = `✅ 成功生成 ${finalConfig.count} 个数独！\nJSON文件: ${jsonFiles.length} 个\n图片文件: ${imageFiles.length} 个\n📦 已打包为压缩文件: ${zipResult.filename}`;
      } else {
        throw new Error('压缩包创建失败');
      }

      console.log(result.message);

    } catch (error) {
      result.success = false;
      result.message = `❌ 批量生成失败: ${(error as Error).message}`;
      result.errors.push((error as Error).message);
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
   * 生成 JSON 文件到内存
   * @param sudokus 数独数据数组
   * @param outputDir 输出目录
   * @param timestamp 统一的时间戳
   * @returns 生成的文件信息数组
   */
  private static async generateJsonFiles(sudokus: GeneratedSudoku[], outputDir: string, timestamp: string): Promise<Array<{path: string, content: string, filename: string}>> {
    const files: Array<{path: string, content: string, filename: string}> = [];
    
    for (let i = 0; i < sudokus.length; i++) {
      const sudoku = sudokus[i];
      const filename = `${timestamp}-${sudoku.difficulty.name}-${i + 1}.json`;
      const filepath = `${outputDir}/${filename}`;
      
      const jsonData = {
        data: sudoku.board,
        solution: sudoku.solution,
        difficulty: sudoku.difficulty.name,
        generatedAt: new Date().toISOString()
      };

      try {
        const jsonContent = JSON.stringify(jsonData, null, 2);
        files.push({
          path: filepath,
          content: jsonContent,
          filename: filename
        });
        console.log(`💾 生成 JSON: ${filename}`);
      } catch (error) {
        console.error(`❌ 生成 JSON 失败 ${filename}: ${error}`);
      }
    }

    return files;
  }

  /**
   * 生成图片到内存
   * @param sudokus 数独数据数组
   * @param outputDir 输出目录
   * @param config 配置
   * @param timestamp 统一的时间戳
   * @returns 生成的文件信息数组
   */
  private static async generateImages(sudokus: GeneratedSudoku[], outputDir: string, config: BatchGenerationConfig, timestamp: string): Promise<Array<{path: string, blob: Blob, filename: string}>> {
    const files: Array<{path: string, blob: Blob, filename: string}> = [];
    
    for (let i = 0; i < sudokus.length; i++) {
      const sudoku = sudokus[i];
      const filename = `${timestamp}-${sudoku.difficulty.name}-${i + 1}.png`;
      const filepath = `${outputDir}/${filename}`;
      
      try {
        const imageBlob = await this.generateSudokuImage(sudoku.board, config);
        files.push({
          path: filepath,
          blob: imageBlob,
          filename: filename
        });
        console.log(`🖼️ 生成图片: ${filename}`);
      } catch (error) {
        console.error(`❌ 生成图片失败 ${filename}: ${error}`);
      }
    }

    return files;
  }

  /**
   * 创建压缩包
   * @param jsonFiles JSON文件信息
   * @param imageFiles 图片文件信息
   * @param config 配置
   * @returns 压缩包结果
   */
  private static async createZipPackage(
    jsonFiles: Array<{path: string, content: string, filename: string}>,
    imageFiles: Array<{path: string, blob: Blob, filename: string}>,
    config: BatchGenerationConfig
  ): Promise<{success: boolean, blob?: Blob, filename?: string, error?: string}> {
    try {
      // 动态导入 JSZip
      const JSZip = await this.loadJSZip();
      const zip = new JSZip();

      // 创建目录结构
      const jsonFolder = zip.folder('json');
      const imageFolder = zip.folder('image');

      // 添加 JSON 文件到 json 文件夹
      jsonFiles.forEach(file => {
        if (jsonFolder) {
          jsonFolder.file(file.filename, file.content);
        }
      });

      // 添加图片文件到 image 文件夹
      imageFiles.forEach(file => {
        if (imageFolder) {
          imageFolder.file(file.filename, file.blob);
        }
      });

      // 添加说明文件
      const readmeContent = this.generateReadmeContent(jsonFiles, imageFiles, config);
      zip.file('README.txt', readmeContent);

      // 生成压缩包
      const zipBlob = await zip.generateAsync({ type: 'blob' });
      const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
      const zipFilename = `sudoku-batch-${timestamp}-${config.count}个.zip`;

      return {
        success: true,
        blob: zipBlob,
        filename: zipFilename
      };

    } catch (error) {
      console.error('创建压缩包失败:', error);
      return {
        success: false,
        error: (error as Error).message
      };
    }
  }

  /**
   * 生成说明文件内容
   * @param jsonFiles JSON文件信息
   * @param imageFiles 图片文件信息
   * @param config 配置
   * @returns 说明文件内容
   */
  private static generateReadmeContent(
    jsonFiles: Array<{path: string, content: string, filename: string}>,
    imageFiles: Array<{path: string, blob: Blob, filename: string}>,
    config: BatchGenerationConfig
  ): string {
    const timestamp = new Date().toLocaleString('zh-CN');
    
    return `数独批量生成数据包
====================

生成时间: ${timestamp}
生成数量: ${config.count} 个
图片尺寸: ${config.imageSize}x${config.imageSize} 像素

文件结构:
--------
json/          - JSON 数据文件 (${jsonFiles.length} 个)
image/         - PNG 图片文件 (${imageFiles.length} 个)

文件命名规则:
------------
所有文件使用统一的时间戳和索引，确保 JSON 和图片文件名完全对应。

例如:
- json/2024-01-15T10-30-45-简单-1.json
- image/2024-01-15T10-30-45-简单-1.png

这两个文件包含同一个数独的数据和图片。

JSON 文件格式:
--------------
{
  "data": [9x9数独板],
  "solution": [9x9完整解答],
  "difficulty": "难度级别",
  "generatedAt": "生成时间"
}

使用说明:
--------
1. 解压此压缩包到任意目录
2. JSON 文件可用于程序导入或数据分析
3. PNG 图片可用于打印、分享或图像识别
4. 每个 JSON 文件都有对应的同名 PNG 图片

注意事项:
--------
- 所有数独都经过有效性验证
- 图片使用自定义样式生成
- 文件按难度和生成顺序命名
- 建议将文件移动到项目的 data/ 目录下

生成工具: 数独批量生成器 v1.0
`;
  }

  /**
   * 动态加载 JSZip 库
   * @returns JSZip 类
   */
  private static async loadJSZip(): Promise<any> {
    try {
      // 尝试从 CDN 加载 JSZip
      if (typeof window !== 'undefined' && !(window as any).JSZip) {
        await this.loadScript('https://cdnjs.cloudflare.com/ajax/libs/jszip/3.10.1/jszip.min.js');
      }
      
      if ((window as any).JSZip) {
        return (window as any).JSZip;
      }
      
      throw new Error('JSZip 库加载失败');
    } catch (error) {
      throw new Error(`无法加载 JSZip 库: ${(error as Error).message}`);
    }
  }

  /**
   * 动态加载脚本
   * @param src 脚本URL
   * @returns Promise
   */
  private static loadScript(src: string): Promise<void> {
    return new Promise((resolve, reject) => {
      const script = document.createElement('script');
      script.src = src;
      script.onload = () => resolve();
      script.onerror = () => reject(new Error(`Failed to load script: ${src}`));
      document.head.appendChild(script);
    });
  }

  /**
   * 下载压缩包
   * @param blob 压缩包 Blob
   * @param filename 文件名
   */
  public static async downloadZipFile(blob: Blob, filename: string): Promise<void> {
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
