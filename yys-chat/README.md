## yys-chat：角色风格中文对话微调与服务

面向中文对话场景，支持给定某个“角色”的对话样本进行 LoRA/QLoRA 微调，保存为可复用的角色适配器，并在本地以命令行或 Gradio 网页聊天界面调用。可管理多个角色，并在界面中切换使用。支持在回复中加入少量表情以增强拟人感。

### 功能概览
- 角色数据准备与格式校验（JSONL）
- 基于 Hugging Face Transformers + TRL + PEFT 的 LoRA/QLoRA 微调
- 多角色模型注册与管理（`models/roles.json`）
- 本地推理（命令行）与 Gradio 聊天界面（下拉选择角色）
- 中文优先，支持添加表情

### 快速开始（Windows PowerShell）
1) 创建并激活虚拟环境
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2) 安装依赖
```powershell
pip install -r requirements.txt
```

3) 准备数据（示例已提供）
- 将你的角色对话数据放到 `data/raw/`，格式见下文或参考 `data/sample/role_mentor.jsonl`。
- 运行预处理：
```powershell
python .\src\data\preprocess.py --input .\data\raw\role_mentor.jsonl --role Mentor --output .\data\processed\mentor.jsonl --val_ratio 0.02
```

4) 训练 LoRA/QLoRA 适配器
```powershell
python .\src\train\train_lora.py --base_model Qwen\Qwen2-1.5B-Instruct --dataset .\data\processed\mentor.jsonl --role Mentor --output_dir .\models\mentor --epochs 3 --batch_size 2 --lr 2e-4 --cutoff_len 2048 --quant 4bit
```
成功后会将角色登记到 `models/roles.json` 中，便于后续调用。

5) 本地聊天（Gradio）
```powershell
python .\src\serve\app.py --share false --port 7860
```
浏览器打开 `http://127.0.0.1:7860`，在界面左侧选择角色后开始对话。

### 数据格式
- 单文件 JSONL，每行一个样本：
```json
{"role": "Mentor", "dialog": [{"from": "user", "text": "早上好"}, {"from": "assistant", "text": "早上好，今天也要元气满满哦~ 😊"}]}
```
- `dialog` 必须是严格的轮次对话，`from` 仅支持 `user` 与 `assistant`。

### 常见模型与建议
- 入门与快速试跑：`Qwen/Qwen2-1.5B-Instruct`（中文友好，显存较友好）。
- 如果显存紧张，建议 `--quant 4bit` 以使用 QLoRA；需安装 bitsandbytes。

### 兼容性提示
- Windows 下 `bitsandbytes` 可能需要 NVIDIA CUDA 环境；若无法安装，可使用 `--quant none` 并降低 batch size。

### 脚本速用
PowerShell 脚本位于 `scripts/`：
- `prepare_data.ps1`：数据预处理
- `train_role.ps1`：启动训练
- `serve.ps1`：启动 Web 界面

### 目录结构
```
yys-chat/
  ├─ data/
  │  ├─ raw/
  │  ├─ processed/
  │  └─ sample/
  ├─ models/
  │  └─ roles.json
  ├─ scripts/
  └─ src/
     ├─ data/
     ├─ serve/
     ├─ train/
     └─ utils/
```

### 许可
仅供学习研究，请遵守基础模型与依赖库的各自许可条款。


