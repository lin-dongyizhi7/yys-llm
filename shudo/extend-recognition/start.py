#!/usr/bin/env python3
"""
数独识别系统启动脚本
提供菜单式的操作选择
"""

import os
import sys
import subprocess


def print_banner():
    """打印系统横幅"""
    print("=" * 60)
    print("🎯 数独图像识别系统")
    print("=" * 60)
    print("基于YOLOv8-nano和轻量级CNN的数独识别解决方案")
    print("支持MNIST预训练和数独数据集微调")
    print("=" * 60)


def print_menu():
    """打印主菜单"""
    print("\n📋 主菜单")
    print("1. 🧪 系统测试")
    print("2. 🚀 快速演示")
    print("3. 🎯 单张图像识别")
    print("4. 📁 批量识别")
    print("5. 🔄 交互式识别")
    print("6. 🏋️  训练模型")
    print("7. 📊 性能评估")
    print("8. 📖 查看帮助")
    print("9. 🚪 退出")
    print("-" * 60)


def run_command(command, description):
    """运行命令"""
    print(f"\n🔄 {description}")
    print(f"执行命令: {command}")
    print("-" * 40)
    
    try:
        result = subprocess.run(command, shell=True, check=True)
        print(f"✅ {description} 完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} 失败: {e}")
        return False
    except KeyboardInterrupt:
        print(f"⏹️  {description} 被用户中断")
        return False


def test_system():
    """测试系统"""
    print("\n🧪 系统测试")
    print("正在测试各个组件的功能...")
    
    if run_command("python test_system.py", "系统测试"):
        print("\n✅ 系统测试完成！")
    else:
        print("\n❌ 系统测试失败，请检查错误信息")


def quick_demo():
    """快速演示"""
    print("\n🚀 快速演示")
    print("演示数独识别功能...")
    
    if run_command("python quick_start.py --mode demo", "快速演示"):
        print("\n✅ 快速演示完成！")
    else:
        print("\n❌ 快速演示失败，请检查错误信息")


def single_recognition():
    """单张图像识别"""
    print("\n🎯 单张图像识别")
    
    # 检查训练数据
    image_dir = "trainData/image"
    if not os.path.exists(image_dir):
        print(f"❌ 训练数据目录不存在: {image_dir}")
        return
    
    # 获取可用的图像文件
    image_files = [f for f in os.listdir(image_dir) if f.endswith('.png')]
    if not image_files:
        print("❌ 未找到测试图像")
        return
    
    print(f"找到 {len(image_files)} 张图像")
    print("前5张图像:")
    for i, img in enumerate(image_files[:5]):
        print(f"  {i+1}. {img}")
    
    try:
        choice = input("\n请选择图像编号 (1-5) 或输入完整路径: ").strip()
        
        if choice.isdigit() and 1 <= int(choice) <= 5:
            image_path = os.path.join(image_dir, image_files[int(choice)-1])
        else:
            image_path = choice
        
        if os.path.exists(image_path):
            print(f"正在识别: {image_path}")
            command = f"python inference.py --mode single --image_path \"{image_path}\""
            run_command(command, "单张图像识别")
        else:
            print(f"❌ 图像文件不存在: {image_path}")
            
    except KeyboardInterrupt:
        print("\n⏹️  操作被用户中断")


def batch_recognition():
    """批量识别"""
    print("\n📁 批量识别")
    print("对训练数据目录中的所有图像进行识别...")
    
    command = "python inference.py --mode batch --image_dir trainData/image"
    if run_command(command, "批量识别"):
        print("\n✅ 批量识别完成！")
    else:
        print("\n❌ 批量识别失败，请检查错误信息")


def interactive_recognition():
    """交互式识别"""
    print("\n🔄 交互式识别")
    print("进入交互式模式，可以输入任意图像路径进行识别...")
    
    command = "python inference.py --mode interactive"
    run_command(command, "交互式识别")


def train_model():
    """训练模型"""
    print("\n🏋️  模型训练")
    print("选择训练模式:")
    print("1. MNIST预训练")
    print("2. 数独数据集微调")
    print("3. 完整训练流程")
    
    try:
        choice = input("\n请选择训练模式 (1-3): ").strip()
        
        if choice == "1":
            command = "python train.py --mode mnist --mnist_epochs 5"
            run_command(command, "MNIST预训练")
        elif choice == "2":
            command = "python train.py --mode sudoku --sudoku_epochs 10"
            run_command(command, "数独数据集微调")
        elif choice == "3":
            command = "python train.py --mode both --mnist_epochs 5 --sudoku_epochs 10"
            run_command(command, "完整训练流程")
        else:
            print("❌ 无效选择")
            
    except KeyboardInterrupt:
        print("\n⏹️  操作被用户中断")


def evaluate_performance():
    """性能评估"""
    print("\n📊 性能评估")
    print("评估数独识别系统的性能...")
    
    command = "python sudoku_recognizer.py"
    if run_command(command, "性能评估"):
        print("\n✅ 性能评估完成！")
    else:
        print("\n❌ 性能评估失败，请检查错误信息")


def show_help():
    """显示帮助信息"""
    print("\n📖 帮助信息")
    print("=" * 60)
    
    print("\n🔧 系统要求:")
    print("- Python 3.7+")
    print("- PyTorch 2.0+")
    print("- OpenCV 4.8+")
    print("- 其他依赖见 requirements.txt")
    
    print("\n📁 目录结构:")
    print("- trainData/image/: 数独图像")
    print("- trainData/json/: 数独标注")
    print("- models/: 训练好的模型")
    
    print("\n🚀 快速开始:")
    print("1. 安装依赖: pip install -r requirements.txt")
    print("2. 运行测试: python test_system.py")
    print("3. 快速演示: python quick_start.py")
    
    print("\n📚 详细文档:")
    print("- README.md: 完整使用说明")
    print("- 训练: python train.py --help")
    print("- 推理: python inference.py --help")
    
    print("\n💡 使用建议:")
    print("- 首次使用建议先运行系统测试")
    print("- 训练前确保有足够的训练数据")
    print("- 推理时可以使用预训练模型提高准确率")


def main():
    """主函数"""
    print_banner()
    
    while True:
        try:
            print_menu()
            choice = input("请选择操作 (1-9): ").strip()
            
            if choice == "1":
                test_system()
            elif choice == "2":
                quick_demo()
            elif choice == "3":
                single_recognition()
            elif choice == "4":
                batch_recognition()
            elif choice == "5":
                interactive_recognition()
            elif choice == "6":
                train_model()
            elif choice == "7":
                evaluate_performance()
            elif choice == "8":
                show_help()
            elif choice == "9":
                print("\n👋 感谢使用数独识别系统！")
                break
            else:
                print("❌ 无效选择，请输入1-9之间的数字")
                
        except KeyboardInterrupt:
            print("\n\n👋 程序被用户中断，再见！")
            break
        except Exception as e:
            print(f"\n❌ 程序出现错误: {str(e)}")
            print("请检查系统配置或联系技术支持")
        
        input("\n按回车键继续...")


if __name__ == "__main__":
    main()
