import time
import psutil
import threading
from pathlib import Path
from datetime import datetime, timedelta

class TrainingMonitor:
    """训练过程监控器"""
    
    def __init__(self, log_file: Path, interval: int = 10):
        self.log_file = log_file
        self.interval = interval  # 监控间隔（秒）
        self.running = False
        self.start_time = None
        self.monitor_thread = None
        
    def start(self):
        """开始监控"""
        self.running = True
        self.start_time = time.time()
        self.monitor_thread = threading.Thread(target=self._monitor_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        
    def stop(self):
        """停止监控"""
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join()
    
    def _monitor_loop(self):
        """监控循环"""
        while self.running:
            try:
                self._log_status()
                time.sleep(self.interval)
            except Exception as e:
                print(f"监控错误: {e}")
    
    def _log_status(self):
        """记录当前状态"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 系统资源使用
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # GPU 信息（如果可用）
        gpu_info = ""
        try:
            import torch
            if torch.cuda.is_available():
                gpu_memory_allocated = torch.cuda.memory_allocated(0) / 1024**3
                gpu_memory_reserved = torch.cuda.memory_reserved(0) / 1024**3
                gpu_info = f" | GPU: {gpu_memory_allocated:.2f}GB/{gpu_memory_reserved:.2f}GB"
        except:
            pass
        
        # 运行时间
        if self.start_time:
            elapsed = time.time() - self.start_time
            elapsed_str = str(timedelta(seconds=int(elapsed)))
        else:
            elapsed_str = "N/A"
        
        status_line = (
            f"[{timestamp}] "
            f"CPU: {cpu_percent:5.1f}% | "
            f"内存: {memory.percent:5.1f}% ({memory.used/1024**3:6.1f}GB/{memory.total/1024**3:6.1f}GB) | "
            f"磁盘: {disk.percent:5.1f}% | "
            f"运行时间: {elapsed_str}"
            f"{gpu_info}"
        )
        
        # 写入日志文件
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(status_line + '\n')
        
        # 控制台输出
        print(status_line)

def create_training_summary(output_dir: Path, logger):
    """创建训练总结报告"""
    summary_file = output_dir / "training_summary.txt"
    
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("训练总结报告\n")
        f.write("=" * 80 + "\n")
        f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"输出目录: {output_dir}\n\n")
        
        # 检查日志文件
        log_file = output_dir / "training.log"
        if log_file.exists():
            f.write("训练日志摘要:\n")
            f.write("-" * 40 + "\n")
            with open(log_file, 'r', encoding='utf-8') as log:
                lines = log.readlines()
                # 提取关键信息
                for line in lines:
                    if any(keyword in line for keyword in [
                        "训练开始", "训练完成", "错误", "ERROR", "WARNING", "系统信息", "模型信息"
                    ]):
                        f.write(line.strip() + "\n")
        
        # 检查模型文件
        f.write("\n模型文件检查:\n")
        f.write("-" * 40 + "\n")
        model_files = list(output_dir.glob("*.bin")) + list(output_dir.glob("*.safetensors"))
        if model_files:
            f.write(f"找到 {len(model_files)} 个模型文件:\n")
            for file in model_files:
                size_mb = file.stat().st_size / 1024**2
                f.write(f"  {file.name}: {size_mb:.1f} MB\n")
        else:
            f.write("未找到模型文件\n")
        
        # 检查配置文件
        config_files = list(output_dir.glob("*.json")) + list(output_dir.glob("*.yaml"))
        if config_files:
            f.write(f"\n找到 {len(config_files)} 个配置文件:\n")
            for file in config_files:
                f.write(f"  {file.name}\n")
    
    logger.info(f"训练总结报告已保存到: {summary_file}")
    return summary_file

# 使用示例
if __name__ == "__main__":
    # 这个脚本通常作为模块导入使用
    print("TrainingMonitor 模块已加载")
    print("使用方法:")
    print("1. 在训练脚本中导入: from train_monitor import TrainingMonitor")
    print("2. 创建监控器: monitor = TrainingMonitor(log_file)")
    print("3. 开始监控: monitor.start()")
    print("4. 停止监控: monitor.stop()")
