import gradio as gr
import json
import subprocess
import threading
from pathlib import Path
from datetime import datetime

# 项目根目录
ROOT_DIR = Path(__file__).resolve().parents[2]

def get_datasets():
    """获取可用数据集"""
    data_dir = ROOT_DIR / "data"
    datasets = []
    if data_dir.exists():
        for file in data_dir.rglob("*.jsonl"):
            datasets.append(str(file.relative_to(ROOT_DIR)))
    return datasets

def start_training(base_model, dataset, role, epochs, batch_size, lr, quant):
    """启动训练"""
    output_dir = f"models/{role.lower()}"
    
    # 构建命令
    cmd = [
        "python", str(ROOT_DIR / "src" / "train" / "train_lora.py"),
        "--base_model", base_model,
        "--dataset", dataset,
        "--role", role,
        "--output_dir", output_dir,
        "--epochs", str(epochs),
        "--batch_size", str(batch_size),
        "--lr", str(lr),
        "--cutoff_len", "2048",
        "--quant", quant
    ]
    
    try:
        # 启动训练
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        
        return f"✅ 训练已启动！\n角色: {role}\n输出目录: {output_dir}\n进程ID: {process.pid}"
    except Exception as e:
        return f"❌ 启动失败: {str(e)}"

def create_interface():
    """创建训练界面"""
    
    with gr.Blocks(title="yys-chat 训练界面", theme=gr.themes.Soft()) as interface:
        gr.Markdown("# 🚀 yys-chat 模型训练")
        gr.Markdown("配置参数并启动 LoRA/QLoRA 微调训练")
        
        with gr.Row():
            with gr.Column(scale=2):
                # 训练配置
                with gr.Group("📋 训练配置"):
                    base_model = gr.Dropdown(
                        choices=[
                            "Qwen/Qwen2-1.5B-Instruct",
                            "Qwen/Qwen2-7B-Instruct",
                            "microsoft/DialoGPT-medium",
                            "sshleifer/tiny-gpt2"
                        ],
                        value="Qwen/Qwen2-1.5B-Instruct",
                        label="基础模型"
                    )
                    
                    dataset = gr.Dropdown(
                        choices=get_datasets(),
                        value="data/yys/train.jsonl",
                        label="训练数据集"
                    )
                    
                    role = gr.Textbox(
                        value="Mentor",
                        label="角色名称"
                    )
                
                # 训练参数
                with gr.Group("⚙️ 训练参数"):
                    with gr.Row():
                        epochs = gr.Slider(1, 10, 3, step=1, label="训练轮数")
                        batch_size = gr.Slider(1, 8, 2, step=1, label="批次大小")
                    
                    with gr.Row():
                        lr = gr.Slider(1e-5, 1e-3, 2e-4, step=1e-5, label="学习率")
                        quant = gr.Radio(["none", "4bit", "8bit"], value="none", label="量化方式")
                
                # 控制按钮
                start_btn = gr.Button("🚀 开始训练", variant="primary", size="lg")
                status_output = gr.Textbox(label="状态", lines=3, interactive=False)
            
            with gr.Column(scale=1):
                # 快速开始
                with gr.Group("🚀 快速开始"):
                    gr.Markdown("**推荐配置:**")
                    gr.Markdown("- 模型: Qwen2-1.5B-Instruct")
                    gr.Markdown("- 数据集: data/yys/train.jsonl")
                    gr.Markdown("- 角色: Mentor")
                    gr.Markdown("- 轮数: 3")
                    gr.Markdown("- 量化: none (CPU训练)")
                
                # 训练历史
                with gr.Group("📚 训练历史"):
                    history_btn = gr.Button("🔄 查看历史", size="sm")
                    history_output = gr.JSON(label="已完成训练")
        
        # 事件绑定
        start_btn.click(
            start_training,
            inputs=[base_model, dataset, role, epochs, batch_size, lr, quant],
            outputs=status_output
        )
        
        def get_history():
            models_dir = ROOT_DIR / "models"
            history = []
            if models_dir.exists():
                for model_dir in models_dir.iterdir():
                    if model_dir.is_dir():
                        meta_file = model_dir / "meta.json"
                        if meta_file.exists():
                            try:
                                with open(meta_file, 'r', encoding='utf-8') as f:
                                    meta = json.load(f)
                                    history.append({
                                        "角色": meta.get("role", "未知"),
                                        "基础模型": meta.get("base_model", "未知"),
                                        "完成时间": meta.get("completed_at", "未知")[:19],
                                        "训练时间": f"{meta.get('training_time', 0)/3600:.2f}h"
                                    })
                            except:
                                pass
            return history
        
        history_btn.click(get_history, outputs=history_output)
        
        # 页面加载时获取历史
        interface.load(get_history, outputs=history_output)
    
    return interface

if __name__ == "__main__":
    interface = create_interface()
    interface.launch(server_port=7861, share=False)
