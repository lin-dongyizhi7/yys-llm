#!/usr/bin/env python3
"""
数独识别推理脚本
使用训练好的模型进行数独图像识别
"""

import os
import argparse
import cv2
import numpy as np
import json
import time
from typing import Optional, Tuple
import matplotlib.pyplot as plt
from sudoku_recognizer import SudokuRecognizer


def load_models(detector_model_path: Optional[str] = None,
                recognizer_model_path: Optional[str] = None) -> SudokuRecognizer:
    """
    加载训练好的模型
    
    Args:
        detector_model_path: 检测器模型路径
        recognizer_model_path: 识别器模型路径
        
    Returns:
        初始化好的数独识别器
    """
    print("正在加载模型...")
    
    # 检查模型文件是否存在
    if recognizer_model_path and not os.path.exists(recognizer_model_path):
        print(f"警告: 识别器模型文件不存在: {recognizer_model_path}")
        print("将使用随机初始化的模型")
        recognizer_model_path = None
    
    if detector_model_path and not os.path.exists(detector_model_path):
        print(f"警告: 检测器模型文件不存在: {detector_model_path}")
        print("将使用默认的YOLOv8-nano模型")
        detector_model_path = None
    
    # 初始化识别器
    recognizer = SudokuRecognizer(detector_model_path, recognizer_model_path)
    
    print("模型加载完成！")
    return recognizer


def recognize_single_image(recognizer: SudokuRecognizer, image_path: str,
                         output_dir: str = "inference_results") -> bool:
    """
    识别单张数独图像
    
    Args:
        recognizer: 数独识别器
        image_path: 图像路径
        output_dir: 输出目录
        
    Returns:
        是否识别成功
    """
    print(f"\n正在识别图像: {image_path}")
    
    # 检查图像文件是否存在
    if not os.path.exists(image_path):
        print(f"错误: 图像文件不存在: {image_path}")
        return False
    
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)
    
    # 记录开始时间
    start_time = time.time()
    
    try:
        # 识别数独
        sudoku, confidences, grid = recognizer.recognize_from_image(image_path)
        
        if sudoku is None:
            print("识别失败")
            return False
        
        # 计算处理时间
        processing_time = time.time() - start_time
        
        # 保存识别结果
        result = {
            'image_path': image_path,
            'processing_time': processing_time,
            'recognized_sudoku': sudoku.tolist(),
            'confidences': confidences.tolist(),
            'average_confidence': float(np.mean(confidences))
        }
        
        # 生成输出文件名
        base_name = os.path.splitext(os.path.basename(image_path))[0]
        result_path = os.path.join(output_dir, f"{base_name}_result.json")
        
        with open(result_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        # 保存检测到的网格
        if grid is not None:
            grid_path = os.path.join(output_dir, f"{base_name}_grid.png")
            cv2.imwrite(grid_path, grid)
        
        # 可视化结果
        viz_path = os.path.join(output_dir, f"{base_name}_visualization.png")
        recognizer.visualize_recognition(image_path, viz_path)
        
        print(f"识别完成！")
        print(f"处理时间: {processing_time:.3f}秒")
        print(f"平均置信度: {np.mean(confidences):.3f}")
        print(f"识别结果:\n{sudoku}")
        print(f"结果已保存到: {output_dir}")
        
        return True
        
    except Exception as e:
        print(f"识别过程中出现错误: {str(e)}")
        return False


def batch_inference(recognizer: SudokuRecognizer, image_dir: str,
                   output_dir: str = "batch_inference_results") -> None:
    """
    批量推理
    
    Args:
        recognizer: 数独识别器
        image_dir: 图像目录
        output_dir: 输出目录
    """
    print(f"\n开始批量推理，图像目录: {image_dir}")
    
    # 检查目录是否存在
    if not os.path.exists(image_dir):
        print(f"错误: 图像目录不存在: {image_dir}")
        return
    
    # 获取所有图像文件
    image_extensions = ['.png', '.jpg', '.jpeg', '.bmp', '.tiff']
    image_files = [f for f in os.listdir(image_dir) 
                   if any(f.lower().endswith(ext) for ext in image_extensions)]
    
    if not image_files:
        print(f"在目录 {image_dir} 中未找到图像文件")
        return
    
    print(f"找到 {len(image_files)} 张图像")
    
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)
    
    # 批量处理
    successful_count = 0
    total_count = len(image_files)
    
    for i, image_file in enumerate(image_files):
        print(f"\n处理图像 {i+1}/{total_count}: {image_file}")
        
        image_path = os.path.join(image_dir, image_file)
        
        if recognize_single_image(recognizer, image_path, output_dir):
            successful_count += 1
    
    # 输出统计信息
    print(f"\n批量推理完成！")
    print(f"成功识别: {successful_count}/{total_count}")
    print(f"成功率: {100 * successful_count / total_count:.1f}%")


def interactive_mode(recognizer: SudokuRecognizer) -> None:
    """
    交互式模式
    
    Args:
        recognizer: 数独识别器
    """
    print("\n进入交互式模式")
    print("输入 'quit' 退出")
    
    while True:
        # 获取用户输入
        user_input = input("\n请输入图像路径或命令: ").strip()
        
        if user_input.lower() in ['quit', 'exit', 'q']:
            print("退出交互式模式")
            break
        
        if user_input.lower() == 'help':
            print("可用命令:")
            print("  help - 显示帮助信息")
            print("  quit/exit/q - 退出")
            print("  <图像路径> - 识别指定图像")
            continue
        
        # 检查是否为有效路径
        if not os.path.exists(user_input):
            print(f"错误: 文件不存在: {user_input}")
            continue
        
        # 检查是否为图像文件
        image_extensions = ['.png', '.jpg', '.jpeg', '.bmp', '.tiff']
        if not any(user_input.lower().endswith(ext) for ext in image_extensions):
            print(f"错误: 不是有效的图像文件: {user_input}")
            continue
        
        # 识别图像
        print(f"正在识别: {user_input}")
        success = recognize_single_image(recognizer, user_input)
        
        if success:
            print("识别完成！")
        else:
            print("识别失败")


def compare_with_ground_truth(recognizer: SudokuRecognizer, image_path: str,
                             json_path: str, output_dir: str = "comparison_results") -> bool:
    """
    与真实标签比较
    
    Args:
        recognizer: 数独识别器
        image_path: 图像路径
        json_path: JSON标注路径
        output_dir: 输出目录
        
    Returns:
        是否比较成功
    """
    print(f"\n正在比较识别结果与真实标签...")
    
    # 检查文件是否存在
    if not os.path.exists(image_path):
        print(f"错误: 图像文件不存在: {image_path}")
        return False
    
    if not os.path.exists(json_path):
        print(f"错误: JSON标注文件不存在: {json_path}")
        return False
    
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        # 识别数独
        sudoku, confidences, grid = recognizer.recognize_from_image(image_path)
        
        if sudoku is None:
            print("识别失败，无法进行比较")
            return False
        
        # 读取真实标签
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            ground_truth = np.array(data['data'])
        
        # 计算准确率
        mask = ground_truth != 0  # 只计算有数字的位置
        if np.any(mask):
            accuracy = np.mean(sudoku[mask] == ground_truth[mask])
            print(f"识别准确率: {accuracy:.3f}")
        else:
            accuracy = 0.0
            print("没有数字可以比较")
        
        # 创建比较可视化
        fig, axes = plt.subplots(1, 3, figsize=(18, 6))
        
        # 原始图像
        original = cv2.imread(image_path)
        original_rgb = cv2.cvtColor(original, cv2.COLOR_BGR2RGB)
        axes[0].imshow(original_rgb)
        axes[0].set_title('原始图像')
        axes[0].axis('off')
        
        # 真实标签
        axes[1].imshow(np.zeros((9, 9)), cmap='gray')
        axes[1].set_title('真实标签')
        for i in range(9):
            for j in range(9):
                digit = ground_truth[i, j]
                if digit != 0:
                    axes[1].text(j, i, str(digit), ha='center', va='center', 
                                fontsize=12, color='blue', weight='bold')
        axes[1].set_xticks(range(9))
        axes[1].set_yticks(range(9))
        axes[1].grid(True, alpha=0.3)
        
        # 识别结果
        axes[2].imshow(np.zeros((9, 9)), cmap='gray')
        axes[2].set_title(f'识别结果 (准确率: {accuracy:.3f})')
        for i in range(9):
            for j in range(9):
                digit = sudoku[i, j]
                confidence = confidences[i, j]
                
                # 检查是否正确
                is_correct = (ground_truth[i, j] == 0) or (sudoku[i, j] == ground_truth[i, j])
                color = 'green' if is_correct else 'red'
                
                axes[2].text(j, i, str(digit), ha='center', va='center', 
                            fontsize=12, color=color, weight='bold')
        axes[2].set_xticks(range(9))
        axes[2].set_yticks(range(9))
        axes[2].grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # 保存比较结果
        base_name = os.path.splitext(os.path.basename(image_path))[0]
        comparison_path = os.path.join(output_dir, f"{base_name}_comparison.png")
        plt.savefig(comparison_path, dpi=300, bbox_inches='tight')
        
        # 保存详细结果
        result = {
            'image_path': image_path,
            'json_path': json_path,
            'ground_truth': ground_truth.tolist(),
            'recognized_sudoku': sudoku.tolist(),
            'confidences': confidences.tolist(),
            'accuracy': accuracy,
            'average_confidence': float(np.mean(confidences))
        }
        
        result_path = os.path.join(output_dir, f"{base_name}_comparison_result.json")
        with open(result_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print(f"比较结果已保存到: {output_dir}")
        
        return True
        
    except Exception as e:
        print(f"比较过程中出现错误: {str(e)}")
        return False


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='数独识别推理')
    parser.add_argument('--mode', type=str, default='single',
                       choices=['single', 'batch', 'interactive', 'compare'],
                       help='推理模式')
    parser.add_argument('--image_path', type=str, help='单张图像路径')
    parser.add_argument('--image_dir', type=str, help='图像目录路径')
    parser.add_argument('--json_path', type=str, help='JSON标注路径（用于比较模式）')
    parser.add_argument('--detector_model', type=str, help='检测器模型路径')
    parser.add_argument('--recognizer_model', type=str, help='识别器模型路径')
    parser.add_argument('--output_dir', type=str, default='inference_results',
                       help='输出目录')
    
    args = parser.parse_args()
    
    # 加载模型
    recognizer = load_models(args.detector_model, args.recognizer_model)
    
    if args.mode == 'single':
        if not args.image_path:
            print("错误: 单张图像模式需要指定 --image_path")
            return
        recognize_single_image(recognizer, args.image_path, args.output_dir)
    
    elif args.mode == 'batch':
        if not args.image_dir:
            print("错误: 批量模式需要指定 --image_dir")
            return
        batch_inference(recognizer, args.image_dir, args.output_dir)
    
    elif args.mode == 'interactive':
        interactive_mode(recognizer)
    
    elif args.mode == 'compare':
        if not args.image_path or not args.json_path:
            print("错误: 比较模式需要指定 --image_path 和 --json_path")
            return
        compare_with_ground_truth(recognizer, args.image_path, args.json_path, args.output_dir)
    
    else:
        print("错误: 无效的推理模式")
        parser.print_help()


if __name__ == "__main__":
    main()
