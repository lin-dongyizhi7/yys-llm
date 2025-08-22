import gradio as gr
import json
import subprocess
import threading
import time
import os
from pathlib import Path
from datetime import datetime
import psutil

# 项目根目录
ROOT_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT_DIR / "data"
MODELS_DIR = ROOT_DIR / "models"

class TrainingManager:
    """训练管理器"""
    
    def __init__(self):
        self.current_training = None
        self.training_process = None
        self.training_logs = []
        self.is_training = False
        
    def start_training(self, base_model, dataset, role, output_dir, epochs, batch_size, lr, cutoff_len, quant):
        """启动训练"""
        if self.is_training:
            return "已有训练任务正在运行，请等待完成。"
        
        # 验证参数
        if not base_model or not dataset or not role or not output_dir:
            return "请填写所有必需的参数。"
        
        # 检查数据集是否存在
        dataset_path = Path(dataset)
        if not dataset_path.exists():
            return f"数据集文件不存在: {dataset}"
        
        # 创建输出目录
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # 构建训练命令
        cmd = [
            "python", str(ROOT_DIR / "src" / "train" / "train_lora.py"),
            "--base_model", base_model,
            "--dataset", str(dataset_path),
            "--role", role,
            "--output_dir", str(output_path),
            "--epochs", str(epochs),
            "--batch_size", str(batch_size),
            "--lr", str(lr),
            "--cutoff_len", str(cutoff_len),
            "--quant", quant
        ]
        
        try:
            # 启动训练进程
            self.training_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            self.is_training = True
            self.training_logs = []
            self.current_training = {
                "start_time": datetime.now(),
                "role": role,
                "output_dir": str(output_path),
                "status": "运行中"
            }
            
            # 启动日志监控线程
            threading.Thread(target=self._monitor_training, daemon=True).start()
            
            return f"训练已启动！角色: {role}, 输出目录: {output_dir}"
            
        except Exception as e:
            return f"启动训练失败: {str(e)}"
    
    def _monitor_training(self):
        """监控训练进程"""
        while self.training_process and self.training_process.poll() is None:
            try:
                line = self.training_process.stdout.readline()
                if line:
                    line = line.strip()
                    if line:
                        self.training_logs.append(line)
                        # 限制日志数量
                        if len(self.training_logs) > 1000:
                            self.training_logs = self.training_logs[-500:]
            except:
                break
        
        # 训练完成
        if self.training_process:
            return_code = self.training_process.wait()
            self.is_training = False
            
            if return_code == 0:
                self.current_training["status"] = "完成"
                self.current_training["end_time"] = datetime.now()
            else:
                self.current_training["status"] = "失败"
                self.current_training["end_time"] = datetime.now()
    
    def stop_training(self):
        """停止训练"""
        if self.training_process and self.is_training:
            self.training_process.terminate()
            self.is_training = False
            return "训练已停止"
        return "没有正在运行的训练任务"
    
    def get_training_status(self):
        """获取训练状态"""
        if not self.current_training:
            return "无训练任务", []
        
        status = self.current_training["status"]
        if self.is_training:
            status = "运行中"
        
        return status, self.training_logs[-50:]  # 返回最近50行日志
    
    def get_system_info(self):
        """获取系统信息"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # GPU 信息
            gpu_info = "不可用"
            try:
                import torch
                if torch.cuda.is_available():
                    gpu_memory_allocated = torch.cuda.memory_allocated(0) / 1024**3
                    gpu_memory_reserved = torch.cuda.memory_reserved(0) / 1024**3
                    gpu_info = f"{gpu_memory_allocated:.2f}GB / {gpu_memory_reserved:.2f}GB"
            except:
                pass
            
            return {
                "CPU": f"{cpu_percent:.1f}%",
                "内存": f"{memory.percent:.1f}% ({memory.used/1024**3:.1f}GB/{memory.total/1024**3:.1f}GB)",
                "磁盘": f"{disk.percent:.1f}%",
                "GPU": gpu_info
            }
        except Exception as e:
            return {"错误": str(e)}

def get_available_datasets():
    """获取可用的数据集"""
    datasets = []
    if DATA_DIR.exists():
        for file in DATA_DIR.rglob("*.jsonl"):
            datasets.append(str(file.relative_to(ROOT_DIR)))
    return datasets

def get_available_models():
    """获取可用的基础模型"""
    return [
        "Qwen/Qwen2-1.5B-Instruct",
        "Qwen/Qwen2-7B-Instruct", 
        "Qwen/Qwen2-14B-Instruct",
        "microsoft/DialoGPT-medium",
        "sshleifer/tiny-gpt2"
    ]

def get_training_history():
    """获取训练历史"""
    history = []
    if MODELS_DIR.exists():
        for model_dir in MODELS_DIR.iterdir():
            if model_dir.is_dir():
                meta_file = model_dir / "meta.json"
                if meta_file.exists():
                    try:
                        with open(meta_file, 'r', encoding='utf-8') as f:
                            meta = json.load(f)
                            history.append({
                                "角色": meta.get("role", "未知"),
                                "基础模型": meta.get("base_model", "未知"),
                                "完成时间": meta.get("completed_at", "未知"),
                                "训练时间": f"{meta.get('training_time', 0)/3600:.2f}小时",
                                "状态": "完成"
                            })
                    except:
                        pass
    return history

# 创建训练管理器实例
training_manager = TrainingManager()

def create_training_interface():
    """创建训练界面"""
    
    with gr.Blocks(title="yys-chat 模型训练", theme=gr.themes.Soft()) as interface:
        gr.Markdown("# 🚀 yys-chat 模型训练界面")
        gr.Markdown("配置训练参数，启动 LoRA/QLoRA 微调训练")
        
        with gr.Row():
            with gr.Column(scale=2):
                # 训练配置区域
                with gr.Group("📋 训练配置"):
                    base_model = gr.Dropdown(
                        choices=get_available_models(),
                        value="Qwen/Qwen2-1.5B-Instruct",
                        label="基础模型",
                        info="选择要微调的基础模型"
                    )
                    
                    dataset = gr.Dropdown(
                        choices=get_available_datasets(),
                        value="data/yys/train.jsonl",
                        label="训练数据集",
                        info="选择训练数据文件"
                    )
                    
                    role = gr.Textbox(
                        value="Mentor",
                        label="角色名称",
                        info="为训练的角色指定一个名称"
                    )
                    
                    output_dir = gr.Textbox(
                        value="models/yys_mentor",
                        label="输出目录",
                        info="模型和日志的保存位置"
                    )
                
                with gr.Group("⚙️ 训练参数"):
                    with gr.Row():
                        epochs = gr.Slider(
                            minimum=1, maximum=10, value=3, step=1,
                            label="训练轮数", info="完整的训练周期数"
                        )
                        batch_size = gr.Slider(
                            minimum=1, maximum=8, value=2, step=1,
                            label="批次大小", info="每步处理的样本数"
                        )
                    
                    with gr.Row():
                        lr = gr.Slider(
                            minimum=1e-5, maximum=1e-3, value=2e-4, step=1e-5,
                            label="学习率", info="模型参数更新的步长"
                        )
                        cutoff_len = gr.Slider(
                            minimum=512, maximum=4096, value=2048, step=128,
                            label="最大长度", info="输入序列的最大长度"
                        )
                    
                    quant = gr.Radio(
                        choices=["none", "4bit", "8bit"],
                        value="none",
                        label="量化方式",
                        info="none: 不使用量化, 4bit/8bit: 使用 QLoRA"
                    )
                
                with gr.Row():
                    start_btn = gr.Button("🚀 开始训练", variant="primary", size="lg")
                    stop_btn = gr.Button("⏹️ 停止训练", variant="stop", size="lg")
                
                status_text = gr.Textbox(
                    label="训练状态",
                    interactive=False,
                    lines=2
                )
            
            with gr.Column(scale=1):
                # 系统监控区域
                with gr.Group("📊 系统监控"):
                    system_info = gr.JSON(
                        label="系统资源",
                        value=training_manager.get_system_info()
                    )
                    
                    refresh_btn = gr.Button("🔄 刷新", size="sm")
                
                # 训练历史区域
                with gr.Group("📚 训练历史"):
                    history_table = gr.Dataframe(
                        headers=["角色", "基础模型", "完成时间", "训练时间", "状态"],
                        datatype=["str", "str", "str", "str", "str"],
                        label="已完成训练",
                        value=get_training_history()
                    )
                    
                    refresh_history_btn = gr.Button("🔄 刷新历史", size="sm")
        
        # 训练日志区域
        with gr.Group("📝 训练日志"):
            with gr.Row():
                log_display = gr.Textbox(
                    label="实时日志",
                    lines=20,
                    max_lines=30,
                    interactive=False,
                    show_copy_button=True
                )
            
            with gr.Row():
                clear_log_btn = gr.Button("🗑️ 清空日志", size="sm")
                export_log_btn = gr.Button("💾 导出日志", size="sm")
        
        # 事件处理
        def start_training_wrapper():
            result = training_manager.start_training(
                base_model.value,
                dataset.value,
                role.value,
                output_dir.value,
                int(epochs.value),
                int(batch_size.value),
                float(lr.value),
                int(cutoff_len.value),
                quant.value
            )
            return result
        
        def stop_training_wrapper():
            return training_manager.stop_training()
        
        def update_status():
            status, logs = training_manager.get_training_status()
            log_text = "\n".join(logs) if logs else "暂无日志"
            return status, log_text
        
        def refresh_system_info():
            return training_manager.get_system_info()
        
        def refresh_history():
            return get_training_history()
        
        def clear_logs():
            training_manager.training_logs.clear()
            return ""
        
        def export_logs():
            if not training_manager.training_logs:
                return "没有日志可导出"
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"training_logs_{timestamp}.txt"
            log_content = "\n".join(training_manager.training_logs)
            
            # 这里可以添加文件下载功能
            return f"日志已准备导出: {filename}\n共 {len(training_manager.training_logs)} 行"
        
        # 绑定事件
        start_btn.click(
            start_training_wrapper,
            outputs=status_text
        )
        
        stop_btn.click(
            stop_training_wrapper,
            outputs=status_text
        )
        
        refresh_btn.click(
            refresh_system_info,
            outputs=system_info
        )
        
        refresh_history_btn.click(
            refresh_history,
            outputs=history_table
        )
        
        clear_log_btn.click(
            clear_logs,
            outputs=log_display
        )
        
        export_log_btn.click(
            export_logs,
            outputs=status_text
        )
        
        # 自动更新状态
        interface.load(update_status, outputs=[status_text, log_display])
        
        # 定时更新
        status_text.change(
            update_status,
            outputs=[status_text, log_display],
            every=5  # 每5秒更新一次
        )
        
        system_info.change(
            refresh_system_info,
            outputs=system_info,
            every=10  # 每10秒更新一次
        )
    
    return interface

def main():
    """主函数"""
    interface = create_training_interface()
    interface.launch(
        server_name="0.0.0.0",
        server_port=7861,
        share=False,
        show_error=True
    )

if __name__ == "__main__":
    main()
