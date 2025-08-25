/**
 * 数独图片识别工具
 * 用于从图片中识别数独网格和数字
 */

export interface RecognitionResult {
  success: boolean;
  board?: number[][];
  error?: string;
  confidence?: number;
}

export interface GridDetectionResult {
  corners: [number, number][];
  gridSize: { width: number; height: number };
  success: boolean;
}

export interface DigitRecognitionResult {
  digit: number;
  confidence: number;
  position: { row: number; col: number };
}

export class SudokuImageRecognizer {
  private canvas: HTMLCanvasElement;
  private ctx: CanvasRenderingContext2D;

  constructor() {
    this.canvas = document.createElement('canvas');
    this.ctx = this.canvas.getContext('2d')!;
  }

  /**
   * 从图片文件识别数独
   * @param imageFile 图片文件
   * @returns 识别结果
   */
  async recognizeFromFile(imageFile: File): Promise<RecognitionResult> {
    try {
      const image = await this.loadImage(imageFile);
      return await this.recognizeSudoku(image);
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : '图片识别失败'
      };
    }
  }

  /**
   * 从图片URL识别数独
   * @param imageUrl 图片URL
   * @returns 识别结果
   */
  async recognizeFromUrl(imageUrl: string): Promise<RecognitionResult> {
    try {
      const image = await this.loadImageFromUrl(imageUrl);
      return await this.recognizeSudoku(image);
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : '图片识别失败'
      };
    }
  }

  /**
   * 加载图片文件
   * @param file 图片文件
   * @returns HTMLImageElement
   */
  private loadImage(file: File): Promise<HTMLImageElement> {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = (e) => {
        const img = new Image();
        img.onload = () => resolve(img);
        img.onerror = () => reject(new Error('图片加载失败'));
        img.src = e.target?.result as string;
      };
      reader.onerror = () => reject(new Error('文件读取失败'));
      reader.readAsDataURL(file);
    });
  }

  /**
   * 从URL加载图片
   * @param url 图片URL
   * @returns HTMLImageElement
   */
  private loadImageFromUrl(url: string): Promise<HTMLImageElement> {
    return new Promise((resolve, reject) => {
      const img = new Image();
      img.onload = () => resolve(img);
      img.onerror = () => reject(new Error('图片加载失败'));
      img.src = url;
    });
  }

  /**
   * 识别数独
   * @param image 图片元素
   * @returns 识别结果
   */
  private async recognizeSudoku(image: HTMLImageElement): Promise<RecognitionResult> {
    try {
      // 设置画布尺寸
      this.canvas.width = image.width;
      this.canvas.height = image.height;

      // 绘制图片到画布
      this.ctx.drawImage(image, 0, 0);

      // 1. 检测数独网格
      const gridResult = await this.detectSudokuGrid();
      if (!gridResult.success) {
        return {
          success: false,
          error: '无法检测到数独网格，请确保图片包含清晰的数独表格'
        };
      }

      // 2. 提取网格区域
      const gridImage = this.extractGridRegion(gridResult);

      // 3. 分割为9x9的单元格
      const cells = this.splitIntoCells(gridImage, gridResult.gridSize);

      // 4. 识别每个单元格的数字
      const board = await this.recognizeDigits(cells);

      // 5. 验证数独数据的有效性
      if (!this.validateSudokuBoard(board)) {
        return {
          success: false,
          error: '识别结果不符合数独规则，请检查图片质量'
        };
      }

      return {
        success: true,
        board,
        confidence: 0.85 // 示例置信度
      };

    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : '图片处理失败'
      };
    }
  }

  /**
   * 检测数独网格
   * @returns 网格检测结果
   */
  private async detectSudokuGrid(): Promise<GridDetectionResult> {
    try {
      // 获取图像数据
      const imageData = this.ctx.getImageData(0, 0, this.canvas.width, this.canvas.height);
      
      // 转换为灰度图像
      const grayscale = this.convertToGrayscale(imageData);
      
      // 边缘检测
      const edges = this.detectEdges(grayscale);
      
      // 霍夫变换检测直线
      const lines = this.detectLines(edges);
      
      // 检测网格交点
      const intersections = this.findGridIntersections(lines);
      
      // 找到最大的矩形网格
      const grid = this.findLargestGrid(intersections);
      
      if (grid) {
        return {
          success: true,
          corners: grid.corners,
          gridSize: grid.size
        };
      }
      
      return {
        success: false,
        corners: [],
        gridSize: { width: 0, height: 0 }
      };
      
    } catch (error) {
      console.error('网格检测失败:', error);
      return {
        success: false,
        corners: [],
        gridSize: { width: 0, height: 0 }
      };
    }
  }

  /**
   * 转换为灰度图像
   * @param imageData 图像数据
   * @returns 灰度图像数据
   */
  private convertToGrayscale(imageData: ImageData): Uint8ClampedArray {
    const data = imageData.data;
    const grayscale = new Uint8ClampedArray(data.length / 4);
    
    for (let i = 0; i < data.length; i += 4) {
      const r = data[i];
      const g = data[i + 1];
      const b = data[i + 2];
      // 使用加权平均法转换为灰度
      grayscale[i / 4] = Math.round(0.299 * r + 0.587 * g + 0.114 * b);
    }
    
    return grayscale;
  }

  /**
   * 边缘检测（使用Sobel算子）
   * @param grayscale 灰度图像
   * @returns 边缘图像
   */
  private detectEdges(grayscale: Uint8ClampedArray): Uint8ClampedArray {
    const width = this.canvas.width;
    const height = this.canvas.height;
    const edges = new Uint8ClampedArray(grayscale.length);
    
    // Sobel算子
    const sobelX = [-1, 0, 1, -2, 0, 2, -1, 0, 1];
    const sobelY = [-1, -2, -1, 0, 0, 0, 1, 2, 1];
    
    for (let y = 1; y < height - 1; y++) {
      for (let x = 1; x < width - 1; x++) {
        let gx = 0, gy = 0;
        
        // 应用Sobel算子
        for (let ky = -1; ky <= 1; ky++) {
          for (let kx = -1; kx <= 1; kx++) {
            const pixel = grayscale[(y + ky) * width + (x + kx)];
            const kernelIndex = (ky + 1) * 3 + (kx + 1);
            gx += pixel * sobelX[kernelIndex];
            gy += pixel * sobelY[kernelIndex];
          }
        }
        
        // 计算梯度幅值
        const magnitude = Math.sqrt(gx * gx + gy * gy);
        edges[y * width + x] = Math.min(255, magnitude);
      }
    }
    
    return edges;
  }

  /**
   * 检测直线
   * @param edges 边缘图像
   * @returns 检测到的直线
   */
  private detectLines(edges: Uint8ClampedArray): Array<{ rho: number; theta: number }> {
    // 简化的霍夫变换实现
    const lines: Array<{ rho: number; theta: number }> = [];
    const width = this.canvas.width;
    const height = this.canvas.height;
    
    // 这里实现简化的直线检测
    // 实际应用中可以使用更复杂的霍夫变换算法
    
    return lines;
  }

  /**
   * 找到网格交点
   * @param lines 检测到的直线
   * @returns 交点坐标
   */
  private findGridIntersections(lines: Array<{ rho: number; theta: number }>): [number, number][] {
    // 计算直线交点
    const intersections: [number, number][] = [];
    
    // 这里实现交点计算逻辑
    
    return intersections;
  }

  /**
   * 找到最大的矩形网格
   * @param intersections 交点坐标
   * @returns 网格信息
   */
  private findLargestGrid(intersections: [number, number][]): { corners: [number, number][]; size: { width: number; height: number } } | null {
    // 这里实现最大矩形网格检测逻辑
    
    return null;
  }

  /**
   * 提取网格区域
   * @param gridResult 网格检测结果
   * @returns 网格图像
   */
  private extractGridRegion(gridResult: GridDetectionResult): ImageData {
    // 这里实现网格区域提取逻辑
    return this.ctx.getImageData(0, 0, this.canvas.width, this.canvas.height);
  }

  /**
   * 分割为9x9的单元格
   * @param gridImage 网格图像
   * @param gridSize 网格尺寸
   * @returns 单元格图像数组
   */
  private splitIntoCells(gridImage: ImageData, gridSize: { width: number; height: number }): ImageData[] {
    const cells: ImageData[] = [];
    const cellWidth = Math.floor(gridSize.width / 9);
    const cellHeight = Math.floor(gridSize.height / 9);
    
    for (let row = 0; row < 9; row++) {
      for (let col = 0; col < 9; col++) {
        const x = col * cellWidth;
        const y = row * cellHeight;
        const cellImage = this.ctx.getImageData(x, y, cellWidth, cellHeight);
        cells.push(cellImage);
      }
    }
    
    return cells;
  }

  /**
   * 识别数字
   * @param cells 单元格图像数组
   * @returns 数独棋盘
   */
  private async recognizeDigits(cells: ImageData[]): Promise<number[][]> {
    const board: number[][] = Array(9).fill(null).map(() => Array(9).fill(0));
    
    for (let i = 0; i < cells.length; i++) {
      const row = Math.floor(i / 9);
      const col = i % 9;
      
      try {
        const digit = await this.recognizeSingleDigit(cells[i]);
        board[row][col] = digit;
      } catch (error) {
        console.warn(`无法识别单元格 [${row}, ${col}] 的数字:`, error);
        board[row][col] = 0; // 设为空格
      }
    }
    
    return board;
  }

  /**
   * 识别单个数字
   * @param cellImage 单元格图像
   * @returns 识别出的数字
   */
  private async recognizeSingleDigit(cellImage: ImageData): Promise<number> {
    try {
      // 这里可以集成OCR服务或机器学习模型
      // 目前返回一个示例实现
      
      // 1. 预处理图像（去噪、二值化等）
      const processed = this.preprocessCellImage(cellImage);
      
      // 2. 特征提取
      const features = this.extractFeatures(processed);
      
      // 3. 数字分类（这里使用简化的规则）
      const digit = this.classifyDigit(features);
      
      return digit;
      
    } catch (error) {
      console.error('数字识别失败:', error);
      return 0; // 返回空格
    }
  }

  /**
   * 预处理单元格图像
   * @param cellImage 单元格图像
   * @returns 预处理后的图像
   */
  private preprocessCellImage(cellImage: ImageData): ImageData {
    // 图像预处理：去噪、二值化、归一化等
    const processed = new ImageData(cellImage.width, cellImage.height);
    
    // 这里实现预处理逻辑
    
    return processed;
  }

  /**
   * 提取特征
   * @param processedImage 预处理后的图像
   * @returns 特征向量
   */
  private extractFeatures(processedImage: ImageData): number[] {
    // 特征提取：边缘、轮廓、纹理等
    const features: number[] = [];
    
    // 这里实现特征提取逻辑
    
    return features;
  }

  /**
   * 数字分类
   * @param features 特征向量
   * @returns 分类结果
   */
  private classifyDigit(features: number[]): number {
    // 数字分类：使用机器学习模型或规则
    // 这里使用简化的规则分类
    
    // 示例：基于特征向量的简单分类
    if (features.length === 0) return 0;
    
    // 这里实现分类逻辑
    
    return 0; // 默认返回空格
  }

  /**
   * 验证数独棋盘的有效性
   * @param board 数独棋盘
   * @returns 是否有效
   */
  private validateSudokuBoard(board: number[][]): boolean {
    // 检查行
    for (let row = 0; row < 9; row++) {
      const seen = new Set<number>();
      for (let col = 0; col < 9; col++) {
        const digit = board[row][col];
        if (digit !== 0) {
          if (seen.has(digit)) return false;
          seen.add(digit);
        }
      }
    }
    
    // 检查列
    for (let col = 0; col < 9; col++) {
      const seen = new Set<number>();
      for (let row = 0; row < 9; row++) {
        const digit = board[row][col];
        if (digit !== 0) {
          if (seen.has(digit)) return false;
          seen.add(digit);
        }
      }
    }
    
    // 检查3x3宫格
    for (let blockRow = 0; blockRow < 3; blockRow++) {
      for (let blockCol = 0; blockCol < 3; blockCol++) {
        const seen = new Set<number>();
        for (let row = blockRow * 3; row < (blockRow + 1) * 3; row++) {
          for (let col = blockCol * 3; col < (blockCol + 1) * 3; col++) {
            const digit = board[row][col];
            if (digit !== 0) {
              if (seen.has(digit)) return false;
              seen.add(digit);
            }
          }
        }
      }
    }
    
    return true;
  }

  /**
   * 清理资源
   */
  dispose(): void {
    this.canvas.remove();
  }
}

/**
 * 创建数独图片识别器实例
 * @returns 识别器实例
 */
export function createSudokuRecognizer(): SudokuImageRecognizer {
  return new SudokuImageRecognizer();
}

/**
 * 简化的图片识别函数（用于快速测试）
 * @param imageFile 图片文件
 * @returns 识别结果
 */
export async function quickRecognize(imageFile: File): Promise<RecognitionResult> {
  const recognizer = createSudokuRecognizer();
  try {
    const result = await recognizer.recognizeFromFile(imageFile);
    return result;
  } finally {
    recognizer.dispose();
  }
}

/**
 * 使用 tesseract.js 的快速OCR识别：将整张图均匀切分为9x9并识别单元格
 * 适用于图片较为标准且网格基本对齐的情况
 */
export async function quickRecognizeOCR(imageFile: File): Promise<RecognitionResult> {
  try {
    // 动态导入，避免对未使用场景的额外体积影响
    const Tesseract: any = (await import('tesseract.js')).default;

    // 复用本模块的图片加载逻辑
    const loader = new SudokuImageRecognizer();
    try {
      const image = await (loader as any).loadImage(imageFile);

      // 创建工作画布
      const canvas = document.createElement('canvas');
      const ctx = canvas.getContext('2d')!;
      canvas.width = image.width;
      canvas.height = image.height;
      ctx.drawImage(image, 0, 0);

      const board: number[][] = Array(9)
        .fill(null)
        .map(() => Array(9).fill(0));

      const cellWidth = Math.floor(canvas.width / 9);
      const cellHeight = Math.floor(canvas.height / 9);

      // 逐格识别
      for (let row = 0; row < 9; row++) {
        for (let col = 0; col < 9; col++) {
          const x = col * cellWidth;
          const y = row * cellHeight;

          // 为该格子创建单独canvas，做简单的二值化增强
          const cellCanvas = document.createElement('canvas');
          const cellCtx = cellCanvas.getContext('2d')!;
          cellCanvas.width = cellWidth;
          cellCanvas.height = cellHeight;

          const cellImageData = ctx.getImageData(x, y, cellWidth, cellHeight);
          const data = cellImageData.data;
          // 简单二值化
          for (let i = 0; i < data.length; i += 4) {
            const r = data[i];
            const g = data[i + 1];
            const b = data[i + 2];
            const v = 0.299 * r + 0.587 * g + 0.114 * b;
            const bw = v > 180 ? 255 : 0;
            data[i] = data[i + 1] = data[i + 2] = bw;
          }
          cellCtx.putImageData(cellImageData, 0, 0);

          // 使用OCR识别单字符数字
          const { data: ocr } = await Tesseract.recognize(cellCanvas, 'eng', {
            tessedit_char_whitelist: '0123456789',
            // psm 10: Treat the image as a single character
            // 通过 config string 传入
            // tesseract.js 接收 config 也可放在第三参对象中
            // 这里组合方式兼容常见用法
            classify_bln_numeric_mode: 1,
            psm: 10
          });

          const text = (ocr && ocr.text ? ocr.text : '').trim();
          const digit = /^[0-9]$/.test(text) ? parseInt(text, 10) : 0;
          board[row][col] = isNaN(digit) ? 0 : digit;
        }
      }

      return {
        success: true,
        board,
        confidence: 0.7
      };
    } finally {
      loader.dispose();
    }
  } catch (error) {
    return {
      success: false,
      error: error instanceof Error ? error.message : 'OCR识别失败'
    };
  }
}
