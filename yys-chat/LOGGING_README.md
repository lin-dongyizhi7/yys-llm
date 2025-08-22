# yys-chat 训练日志与监控功能

## 🚀 新增功能概览

训练脚本现在包含详细的日志记录和系统监控功能，让你能够：

- 📊 实时监控训练进度和系统资源
- 📝 记录详细的训练过程信息
- 🔍 快速定位训练中的问题
- 📈 分析训练性能和资源使用

## 📁 日志文件结构

训练完成后，输出目录将包含以下文件：

```
models/your_role/
├── training.log          # 详细训练日志
├── monitor.log           # 系统资源监控日志
├── training_summary.txt  # 训练总结报告
├── meta.json            # 训练元数据
├── logs/                # TensorBoard 日志目录
│   └── yys-Mentor-20241222-143022/
└── [模型文件...]
```

## 🔍 日志内容详解

### 1. training.log - 训练过程日志

包含以下详细信息：

#### 系统信息
```
============================================================
训练开始 - 系统信息
============================================================
Python 版本: 3.10.0
PyTorch 版本: 2.3.1
CUDA 可用: True
CUDA 版本: 12.1
GPU 数量: 1
GPU 0: NVIDIA GeForce RTX 4090 (24.0 GB)
系统内存: 32.0 GB
可用内存: 28.5 GB
============================================================
```

#### 模型信息
```
模型信息:
  基础模型: LlamaForCausalLM
  词表大小: 32000
  最大长度: 2048
  总参数: 1,500,000,000
  可训练参数: 8,388,608
  参数压缩比: 0.56%
  LoRA 配置 base_model:
    r: 16
    alpha: 32
    dropout: 0.05
    target_modules: ['q_proj', 'v_proj']
```

#### 数据集信息
```
正在加载数据集: data/yys/train.jsonl
原始数据集大小: 3361 个样本
数据集格式化完成
文本长度统计:
  平均长度: 245.3 字符
  最大长度: 1024 字符
  最小长度: 89 字符
```

#### 训练配置
```
训练配置:
  总步数: 5040
  Warmup 步数: 504
  每 epoch 步数: 1680
```

#### 训练进度
```
2024-12-22 14:30:25 - INFO - {'loss': 2.4567, 'learning_rate': 0.0002, 'epoch': 0.12, 'step': 200}
2024-12-22 14:30:45 - INFO - {'loss': 2.1234, 'learning_rate': 0.0002, 'epoch': 0.24, 'step': 400}
...
```

### 2. monitor.log - 系统资源监控

每 10 秒记录一次系统状态：

```
[2024-12-22 14:30:25] CPU: 45.2% | 内存: 78.5% (25.1GB/32.0GB) | 磁盘: 65.2% | 运行时间: 0:05:30 | GPU: 12.5GB/18.2GB
[2024-12-22 14:30:35] CPU: 52.1% | 内存: 79.1% (25.3GB/32.0GB) | 磁盘: 65.2% | 运行时间: 0:05:40 | GPU: 12.8GB/18.5GB
[2024-12-22 14:30:45] CPU: 48.7% | 内存: 79.8% (25.5GB/32.0GB) | 磁盘: 65.2% | 运行时间: 0:05:50 | GPU: 13.1GB/18.8GB
```

### 3. training_summary.txt - 训练总结报告

```
================================================================================
训练总结报告
================================================================================
生成时间: 2024-12-22 15:45:30
输出目录: models/yys_mentor

训练日志摘要:
----------------------------------------
2024-12-22 14:30:22 - INFO - 训练开始 - 系统信息
2024-12-22 14:30:25 - INFO - 模型信息:
2024-12-22 15:45:28 - INFO - 训练完成!

模型文件检查:
----------------------------------------
找到 3 个模型文件:
  adapter_model.bin: 45.2 MB
  adapter_config.json: 0.0 MB
  tokenizer.json: 0.0 MB

找到 2 个配置文件:
  meta.json
  training_args.json
```

## 🛠️ 使用方法

### 方法 1: 使用增强版训练脚本

```powershell
# 使用带监控的训练脚本
.\scripts\train_with_monitor.ps1 -Dataset ".\data\yys\train.jsonl" -Role "Mentor" -OutputDir ".\models\yys_mentor" -Epochs 3 -Quant "none"
```

### 方法 2: 直接使用 Python 脚本

```powershell
# 直接运行训练脚本
python .\src\train\train_lora.py --base_model Qwen/Qwen2-1.5B-Instruct --dataset .\data\yys\train.jsonl --role Mentor --output_dir .\models\yys_mentor --epochs 3 --batch_size 2 --lr 2e-4 --cutoff_len 2048 --quant none
```

### 方法 3: 集成监控器

```python
from src.train.train_monitor import TrainingMonitor, create_training_summary

# 创建监控器
monitor = TrainingMonitor(log_file=output_dir / "monitor.log", interval=10)
monitor.start()

try:
    # 执行训练
    trainer.train()
finally:
    # 停止监控
    monitor.stop()
    
    # 创建训练总结
    create_training_summary(output_dir, logger)
```

## 📊 监控指标说明

### CPU 使用率
- 显示当前 CPU 使用百分比
- 帮助判断训练是否充分利用计算资源

### 内存使用
- 显示系统内存使用情况
- 包括已用内存、总内存和使用百分比
- 帮助判断是否需要调整批次大小

### GPU 内存 (如果可用)
- 显示 GPU 已分配和已保留的内存
- 帮助优化模型加载和训练配置

### 磁盘使用
- 监控磁盘空间使用情况
- 确保有足够空间保存模型和日志

### 运行时间
- 显示训练已运行的时间
- 帮助估算总训练时间

## 🔧 自定义配置

### 调整监控间隔

```python
# 每 5 秒监控一次
monitor = TrainingMonitor(log_file, interval=5)

# 每 30 秒监控一次
monitor = TrainingMonitor(log_file, interval=30)
```

### 自定义日志级别

```python
# 在 train_lora.py 中修改
logging.basicConfig(
    level=logging.DEBUG,  # 改为 DEBUG 获取更详细信息
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[...]
)
```

### 添加自定义监控指标

```python
def _log_status(self):
    # 添加网络 I/O 监控
    net_io = psutil.net_io_counters()
    network_info = f" | 网络: ↑{net_io.bytes_sent/1024**2:.1f}MB ↓{net_io.bytes_recv/1024**2:.1f}MB"
    
    # 添加到状态行
    status_line += network_info
```

## 🚨 故障排除

### 常见问题

1. **日志文件过大**
   - 调整监控间隔
   - 定期清理旧日志文件

2. **监控影响性能**
   - 增加监控间隔
   - 在低负载时进行监控

3. **GPU 监控失败**
   - 检查 CUDA 安装
   - 确认 PyTorch 版本兼容性

### 性能优化建议

- 监控间隔建议设置为 10-30 秒
- 在训练高峰期可以减少监控频率
- 使用 SSD 存储日志文件以提高 I/O 性能

## 📈 日志分析工具

### 使用 Python 分析日志

```python
import re
from pathlib import Path

def analyze_training_log(log_file):
    """分析训练日志"""
    with open(log_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 提取损失值
    loss_pattern = r"'loss': ([\d.]+)"
    losses = re.findall(loss_pattern, content)
    losses = [float(x) for x in losses]
    
    print(f"总训练步数: {len(losses)}")
    print(f"最终损失: {losses[-1]:.4f}")
    print(f"损失变化: {losses[0]:.4f} -> {losses[-1]:.4f}")
    
    return losses

# 使用示例
losses = analyze_training_log("models/yys_mentor/training.log")
```

### 使用 PowerShell 快速查看

```powershell
# 查看最近的训练状态
Get-Content ".\models\yys_mentor\training.log" -Tail 20

# 查看系统监控
Get-Content ".\models\yys_mentor\monitor.log" -Tail 10

# 搜索错误信息
Get-Content ".\models\yys_mentor\training.log" | Select-String "ERROR|WARNING|Exception"
```

## 🎯 最佳实践

1. **定期检查日志**
   - 训练开始后立即检查日志确认配置正确
   - 训练过程中定期查看监控日志
   - 训练完成后分析总结报告

2. **合理设置参数**
   - 根据系统资源调整批次大小
   - 监控 GPU 内存使用，避免 OOM
   - 设置合适的日志记录频率

3. **备份重要日志**
   - 保存成功的训练日志作为参考
   - 记录失败的训练日志用于问题分析
   - 定期清理旧的日志文件

---

通过这些增强的日志和监控功能，你可以更好地了解训练过程，快速定位问题，并优化训练配置！🚀
