import gradio as gr
import json
import subprocess
import threading
import time
import psutil
from pathlib import Path
from datetime import datetime

# 项目根目录
ROOT_DIR = Path(__file__).resolve().parents[2]

class TrainingController:
    """训练控制器"""
    
    def __init__(self):
        self.process = None
        self.is_running = False
        self.logs = []
        self.start_time = None
        
    def start_training(self, base_model, dataset, role, epochs, batch_size, lr, quant):
        """启动训练"""
        if self.is_running:
            return "已有训练任务正在运行", self.logs
        
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
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            self.is_running = True
            self.start_time = datetime.now()
            self.logs = [f"[{datetime.now().strftime('%H:%M:%S')}] 训练启动: {role}"]
            
            # 启动日志监控线程
            threading.Thread(target=self._monitor_logs, daemon=True).start()
            
            return f"✅ 训练已启动！角色: {role}", self.logs
            
        except Exception as e:
            return f"❌ 启动失败: {str(e)}", self.logs
    
    def stop_training(self):
        """停止训练"""
        if self.process and self.is_running:
            self.process.terminate()
            self.is_running = False
            self.logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] 训练已停止")
            return "训练已停止", self.logs
        return "没有正在运行的训练", self.logs
    
    def _monitor_logs(self):
        """监控训练日志"""
        while self.process and self.process.poll() is None:
            try:
                line = self.process.stdout.readline()
                if line:
                    line = line.strip()
                    if line:
                        timestamp = datetime.now().strftime('%H:%M:%S')
                        self.logs.append(f"[{timestamp}] {line}")
                        # 限制日志数量
                        if len(self.logs) > 200:
                            self.logs = self.logs[-100:]
            except:
                break
        
        # 训练完成
        if self.process:
            return_code = self.process.wait()
            self.is_running = False
            
            if return_code == 0:
                self.logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ 训练完成！")
            else:
                self.logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ 训练失败，退出码: {return_code}")
    
    def get_status(self):
        """获取训练状态"""
        if not self.is_running:
            return "空闲", self.logs
        
        if self.start_time:
            elapsed = datetime.now() - self.start_time
            elapsed_str = str(elapsed).split('.')[0]  # 去掉微秒
            return f"运行中 ({elapsed_str})", self.logs
        
        return "运行中", self.logs

# 创建训练控制器实例
training_controller = TrainingController()
