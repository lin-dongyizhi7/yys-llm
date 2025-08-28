# 数独图像识别系统

这是一个基于深度学习的数独图像识别系统，使用YOLOv8-nano进行数独网格定位，轻量级CNN进行数字识别。

## 系统架构

### 1. 数独网格检测器 (SudokuDetector)
- 使用YOLOv8-nano进行数独网格检测
- 基于传统计算机视觉方法进行网格轮廓检测
- 支持透视变换和网格分割

### 2. 数字识别器 (DigitRecognizer)
- 轻量级CNN模型，专为数字识别优化
- 支持MNIST数据集预训练
- 可在数独数据集上微调

### 3. 完整识别系统 (SudokuRecognizer)
- 整合检测器和识别器
- 支持批量处理和性能评估
- 提供可视化结果

## 安装依赖

```bash
pip install -r requirements.txt
```

## 目录结构

```
extend-recongnition/
├── trainData/                 # 训练数据
│   ├── image/                 # 数独图像
│   └── json/                  # 数独标注
├── models/                    # 模型保存目录
├── sudoku_detector.py         # 数独检测器
├── digit_recognizer.py        # 数字识别器
├── sudoku_recognizer.py       # 完整识别系统
├── train.py                   # 训练脚本
├── inference.py               # 推理脚本
├── requirements.txt           # 依赖包
└── README.md                  # 说明文档
```

## 使用方法

### 1. 训练模型

#### MNIST预训练
```bash
python train.py --mode mnist --mnist_epochs 10
```

#### 数独数据集微调
```bash
python train.py --mode sudoku --sudoku_epochs 20 --image_dir trainData/image --json_dir trainData/json
```

#### 完整训练流程
```bash
python train.py --mode both --mnist_epochs 10 --sudoku_epochs 20
```

### 2. 推理使用

#### 单张图像识别
```bash
python inference.py --mode single --image_path trainData/image/example.png
```

#### 批量识别
```bash
python inference.py --mode batch --image_dir trainData/image
```

#### 交互式模式
```bash
python inference.py --mode interactive
```

#### 与真实标签比较
```bash
python inference.py --mode compare --image_path trainData/image/example.png --json_path trainData/json/example.json
```

### 3. 使用预训练模型

```bash
python inference.py --mode single --image_path example.png --recognizer_model models/sudoku_finetuned.pth
```

## 训练数据格式

### 图像数据
- 支持PNG、JPG、JPEG、BMP、TIFF格式
- 建议图像分辨率不低于300x300像素

### JSON标注格式
```json
{
  "data": [
    [3, 9, 7, 1, 6, 2, 0, 8, 4],
    [0, 4, 5, 7, 9, 0, 0, 2, 1],
    [1, 0, 0, 0, 0, 0, 3, 7, 0],
    ...
  ],
  "solution": [...],
  "difficulty": "简单",
  "generatedAt": "2025-08-28T00:39:26.103Z"
}
```

- `data`: 数独初始数据，0表示空白格子
- `solution`: 完整解答（可选）
- `difficulty`: 难度等级（可选）
- `generatedAt`: 生成时间（可选）

## 模型架构

### 数字识别CNN
```
Conv2d(1, 32, 3x3) + BN + ReLU + MaxPool2d(2x2)
Conv2d(32, 64, 3x3) + BN + ReLU + MaxPool2d(2x2)
Conv2d(64, 128, 3x3) + BN + ReLU + MaxPool2d(2x2)
Flatten
Linear(128*5*5, 512) + ReLU + Dropout(0.5)
Linear(512, 10)
```

### 训练策略
1. **MNIST预训练**: 在MNIST手写数字数据集上预训练
2. **数独微调**: 在数独数据集上微调，适应数独数字特征
3. **学习率调度**: 使用学习率衰减和早停策略

## 性能指标

- **网格检测准确率**: 基于轮廓检测的网格定位成功率
- **数字识别准确率**: 每个数字的识别正确率
- **整体准确率**: 整个数独的完整识别准确率
- **置信度**: 模型对识别结果的置信程度

## 输出结果

### 识别结果
- 9x9的数独矩阵
- 每个位置的置信度
- 处理时间统计

### 可视化结果
- 原始图像
- 检测到的网格
- 识别结果对比

### 性能评估
- 混淆矩阵
- 各数字识别准确率
- 总体统计信息

## 参数调优

### 检测器参数
- `target_size`: 网格目标大小（默认450x450）
- `margin`: 单元格边距（默认2像素）

### 识别器参数
- `batch_size`: 训练批次大小
- `learning_rate`: 学习率
- `epochs`: 训练轮数

## 常见问题

### 1. 网格检测失败
- 检查图像质量和对比度
- 调整轮廓检测参数
- 确保数独网格清晰可见

### 2. 数字识别错误
- 增加训练数据
- 调整模型架构
- 优化数据预处理

### 3. 内存不足
- 减小批次大小
- 使用CPU训练
- 降低图像分辨率

## 扩展功能

### 1. 支持更多数独变体
- 6x6数独
- 16x16数独
- 不规则数独

### 2. 实时识别
- 摄像头输入
- 视频流处理
- 移动端部署

### 3. 多语言支持
- 不同数字字体
- 手写数字识别
- 印刷体数字识别

## 贡献指南

欢迎提交Issue和Pull Request来改进系统！

## 许可证

本项目采用MIT许可证。

## 联系方式

如有问题或建议，请通过GitHub Issues联系。
