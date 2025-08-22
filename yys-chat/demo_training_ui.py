#!/usr/bin/env python3
"""
yys-chat 训练界面演示脚本
演示如何使用训练界面启动模型训练
"""

import subprocess
import time
from pathlib import Path

def demo_simple_ui():
    """演示简单训练界面"""
    print("🚀 启动简单训练界面...")
    print("=" * 50)
    
    # 启动简单界面
    try:
        process = subprocess.Popen([
            "python", "src/train/simple_train_ui.py"
        ])
        
        print("✅ 简单训练界面已启动")
        print("🌐 在浏览器中打开: http://localhost:7861")
        print("🔄 按 Ctrl+C 停止演示")
        
        # 等待用户中断
        try:
            process.wait()
        except KeyboardInterrupt:
            print("\n⏹️ 停止演示")
            process.terminate()
            
    except Exception as e:
        print(f"❌ 启动失败: {e}")

def demo_advanced_ui():
    """演示高级训练界面"""
    print("🚀 启动高级训练界面...")
    print("=" * 50)
    
    # 启动高级界面
    try:
        process = subprocess.Popen([
            "python", "src/train/advanced_train_ui.py"
        ])
        
        print("✅ 高级训练界面已启动")
        print("🌐 在浏览器中打开: http://localhost:7861")
        print("🔄 按 Ctrl+C 停止演示")
        
        # 等待用户中断
        try:
            process.wait()
        except KeyboardInterrupt:
            print("\n⏹️ 停止演示")
            process.terminate()
            
    except Exception as e:
        print(f"❌ 启动失败: {e}")

def check_environment():
    """检查环境"""
    print("🔍 检查训练环境...")
    print("=" * 50)
    
    # 检查 Python
    try:
        result = subprocess.run(["python", "--version"], capture_output=True, text=True)
        print(f"✅ Python: {result.stdout.strip()}")
    except:
        print("❌ Python 未找到")
        return False
    
    # 检查依赖
    dependencies = ["gradio", "torch", "transformers", "peft", "trl"]
    for dep in dependencies:
        try:
            result = subprocess.run(["python", "-c", f"import {dep}"], capture_output=True)
            if result.returncode == 0:
                print(f"✅ {dep}: 已安装")
            else:
                print(f"❌ {dep}: 未安装")
        except:
            print(f"❌ {dep}: 检查失败")
    
    # 检查数据集
    data_files = list(Path("data").rglob("*.jsonl"))
    if data_files:
        print(f"✅ 数据集: 找到 {len(data_files)} 个 .jsonl 文件")
        for file in data_files[:3]:  # 显示前3个
            print(f"   - {file}")
    else:
        print("❌ 数据集: 未找到 .jsonl 文件")
    
    # 检查模型目录
    models_dir = Path("models")
    if models_dir.exists():
        model_dirs = [d for d in models_dir.iterdir() if d.is_dir()]
        print(f"✅ 模型目录: 找到 {len(model_dirs)} 个模型")
        for model_dir in model_dirs[:3]:  # 显示前3个
            print(f"   - {model_dir.name}")
    else:
        print("✅ 模型目录: 将自动创建")
    
    print("=" * 50)
    return True

def main():
    """主函数"""
    print("🎯 yys-chat 训练界面演示")
    print("=" * 50)
    
    # 检查环境
    if not check_environment():
        print("❌ 环境检查失败，请先安装依赖")
        return
    
    # 选择界面
    print("请选择要演示的训练界面:")
    print("1. 简单训练界面 (基础功能)")
    print("2. 高级训练界面 (完整功能)")
    print("3. 退出")
    
    while True:
        try:
            choice = input("\n请输入选择 (1-3): ").strip()
            
            if choice == "1":
                demo_simple_ui()
                break
            elif choice == "2":
                demo_advanced_ui()
                break
            elif choice == "3":
                print("👋 再见！")
                break
            else:
                print("❌ 无效选择，请输入 1-3")
                
        except KeyboardInterrupt:
            print("\n👋 再见！")
            break
        except Exception as e:
            print(f"❌ 错误: {e}")

if __name__ == "__main__":
    main()
