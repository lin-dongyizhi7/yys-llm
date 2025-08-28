#!/usr/bin/env python3
"""
数独识别系统快速启动脚本
提供简单的使用示例和测试功能
"""

import os
import sys
import argparse
from sudoku_recognizer import SudokuRecognizer


def test_system():
    """测试系统基本功能"""
    print("=" * 50)
    print("数独识别系统测试")
    print("=" * 50)
    
    # 检查训练数据
    image_dir = "trainData/image"
    json_dir = "trainData/json"
    
    if not os.path.exists(image_dir):
        print(f"错误: 训练数据目录不存在: {image_dir}")
        return False
    
    if not os.path.exists(json_dir):
        print(f"错误: 标注数据目录不存在: {json_dir}")
        return False
    
    # 获取测试图像
    image_files = [f for f in os.listdir(image_dir) if f.endswith('.png')]
    if not image_files:
        print("错误: 未找到测试图像")
        return False
    
    test_image = os.path.join(image_dir, image_files[0])
    print(f"使用测试图像: {test_image}")
    
    try:
        # 初始化识别系统
        print("\n1. 初始化识别系统...")
        recognizer = SudokuRecognizer()
        
        # 测试识别
        print("\n2. 测试数独识别...")
        sudoku, confidences, grid = recognizer.recognize_from_image(test_image)
        
        if sudoku is not None:
            print("✓ 识别成功！")
            print(f"识别结果:\n{sudoku}")
            print(f"平均置信度: {np.mean(confidences):.3f}")
            
            # 测试可视化
            print("\n3. 测试可视化功能...")
            recognizer.visualize_recognition(test_image, "test_visualization.png")
            print("✓ 可视化完成")
            
            return True
        else:
            print("✗ 识别失败")
            return False
            
    except Exception as e:
        print(f"✗ 测试过程中出现错误: {str(e)}")
        return False


def demo_recognition():
    """演示识别功能"""
    print("=" * 50)
    print("数独识别演示")
    print("=" * 50)
    
    # 初始化识别系统
    recognizer = SudokuRecognizer()
    
    # 设置路径
    image_dir = "trainData/image"
    json_dir = "trainData/json"
    
    if not os.path.exists(image_dir):
        print(f"错误: 训练数据目录不存在: {image_dir}")
        return
    
    # 获取前几张图像进行演示
    image_files = [f for f in os.listdir(image_dir) if f.endswith('.png')][:3]
    
    for i, image_file in enumerate(image_files):
        print(f"\n演示 {i+1}: {image_file}")
        print("-" * 30)
        
        image_path = os.path.join(image_dir, image_file)
        
        # 识别
        sudoku, confidences, grid = recognizer.recognize_from_image(image_path)
        
        if sudoku is not None:
            print("识别结果:")
            for row in sudoku:
                print(" ".join(map(str, row)))
            print(f"置信度: {np.mean(confidences):.3f}")
        else:
            print("识别失败")
        
        print()


def interactive_demo():
    """交互式演示"""
    print("=" * 50)
    print("交互式数独识别演示")
    print("=" * 50)
    print("输入图像路径进行识别，输入 'quit' 退出")
    
    recognizer = SudokuRecognizer()
    
    while True:
        try:
            user_input = input("\n请输入图像路径: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("退出演示")
                break
            
            if not os.path.exists(user_input):
                print(f"文件不存在: {user_input}")
                continue
            
            if not any(user_input.lower().endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.bmp']):
                print("不是有效的图像文件")
                continue
            
            print(f"正在识别: {user_input}")
            sudoku, confidences, grid = recognizer.recognize_from_image(user_input)
            
            if sudoku is not None:
                print("识别成功！")
                print("结果:")
                for row in sudoku:
                    print(" ".join(map(str, row)))
                print(f"置信度: {np.mean(confidences):.3f}")
            else:
                print("识别失败")
                
        except KeyboardInterrupt:
            print("\n退出演示")
            break
        except Exception as e:
            print(f"错误: {str(e)}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='数独识别系统快速启动')
    parser.add_argument('--mode', type=str, default='test',
                       choices=['test', 'demo', 'interactive'],
                       help='运行模式')
    
    args = parser.parse_args()
    
    if args.mode == 'test':
        success = test_system()
        if success:
            print("\n✓ 系统测试通过！")
        else:
            print("\n✗ 系统测试失败！")
    
    elif args.mode == 'demo':
        demo_recognition()
    
    elif args.mode == 'interactive':
        interactive_demo()
    
    else:
        print("无效的运行模式")
        parser.print_help()


if __name__ == "__main__":
    # 添加必要的导入
    import numpy as np
    
    main()
