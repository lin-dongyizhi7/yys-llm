# Sudoku Transformer 训练脚手架（extend）

本目录提供使用 PyTorch 的 Encoder-Decoder Transformer 进行数独求解的最小可用训练脚手架，支持：
- 训练数据自动生成（Python实现，与前端生成思路一致：先满盘回溯，后挖空）
- 交叉熵损失的监督训练
- 回溯搜索快速验证推断结果（可选）

## 目录结构
- `requirements.txt`：Python依赖
- `data_gen.py`：数据生成器（生成 jsonl 数据）
- `solver.py`：回溯搜索求解器（用于验证）
- `model.py`：Encoder-Decoder Transformer 模型与序列化工具
- `train.py`：训练与快速评估脚本
- `trainData/`：训练数据输出目录（运行时自动创建）

## 安装依赖
```bash
# 建议使用 Python 3.10+
cd shudo/extend
python -m venv .venv
. .venv/Scripts/activate  # Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## 生成训练数据
```bash
python data_gen.py  # 默认生成 200 条到 trainData/train_sudoku.jsonl
```
可修改 `data_gen.py` 末尾的参数：
- `num_samples`: 生成条目数量
- `removal_count`: 挖空数量（影响难度）
- `prefix`: 输出文件前缀

数据格式为 jsonl，每行：
```json
{"input": {"data": [[...9x9...]]}, "target": {"data": [[...9x9...]]}}
```
`input` 为题面（0 表示空），`target` 为完整解。

## 训练
```bash
python train.py --mode train --epochs 5 --batch_size 64 --lr 3e-4 \
  --model_path sudoku_transformer.pt --data_prefix train_sudoku.jsonl
```
会在每个 epoch 结束保存权重。

## 快速评估（含回溯验证）
```bash
python train.py --mode eval --model_path sudoku_transformer.pt --eval_n 20 \
  --data_prefix train_sudoku.jsonl
```
- 模型会自回归生成 81 位解序列
- 若结果中有 0（未预测出），则将题面数字覆盖回去，再调用回溯补全
- 输出 “solved or backtracked”的统计

## 设计说明
- 序列化：将 9x9 棋盘展平成长度 81 的序列，token ∈ {0..9}
- 训练目标：decoder 预测目标解序列（交叉熵损失）
- 生成：自回归，从起始符（0）开始预测 81 步

## 后续优化方向
- 更强的数据生成（唯一解校验、难度控制）
- 更强的模型结构（相对位置编码、掩码约束、GNN/Transformer混合）
- 训练目标改进（约束感知的损失，或 policy + value ）
- 联合强化学习（环境=数独，奖励=解成+最少步）

## 注意
- 本脚手架为教学/原型用途，未做极致性能优化
- 如需大规模训练，请考虑更高效的数据管道与多卡策略
