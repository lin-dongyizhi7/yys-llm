#!/usr/bin/env python3
"""
数独识别系统测试脚本
测试各个组件的功能
"""

import os
import sys
import numpy as np
import cv2
from sudoku_detector import SudokuDetector
from digit_recognizer import DigitRecognizer
from sudoku_recognizer import SudokuRecognizer


def test_detector():
    """测试数独检测器"""
    print("=" * 50)
    print("测试数独检测器")
    print("=" * 50)
    
    detector = SudokuDetector()
    
    # 检查训练数据
    image_dir = "trainData/image"
    if not os.path.exists(image_dir):
        print(f"错误: 训练数据目录不存在: {image_dir}")
        return False
    
    # 获取测试图像
    image_files = [f for f in os.listdir(image_dir) if f.endswith('.png')]
    if not image_files:
        print("错误: 未找到测试图像")
        return False
    
    test_image = os.path.join(image_dir, image_files[0])
    print(f"测试图像: {test_image}")
    
    try:
        # 测试检测
        grid, cells = detector.detect_sudoku(test_image)
        
        if grid is not None and cells is not None:
            print("✓ 网格检测成功")
            print(f"网格大小: {grid.shape}")
            print(f"单元格数量: {len(cells)}x{len(cells[0])}")
            
            # 保存检测结果
            cv2.imwrite("test_grid.png", grid)
            print("✓ 检测结果已保存到 test_grid.png")
            
            return True
        else:
            print("✗ 网格检测失败")
            return False
            
    except Exception as e:
        print(f"✗ 检测器测试错误: {str(e)}")
        return False


def test_recognizer():
    """测试数字识别器"""
    print("\n" + "=" * 50)
    print("测试数字识别器")
    print("=" * 50)
    
    recognizer = DigitRecognizer()
    
    # 创建测试数据
    test_cell = np.random.randint(0, 255, (28, 28), dtype=np.uint8)
    
    try:
        # 测试单个数字识别
        digit, confidence = recognizer.recognize_digit(test_cell)
        
        print("✓ 数字识别成功")
        print(f"识别结果: {digit}")
        print(f"置信度: {confidence:.3f}")
        
        return True
        
    except Exception as e:
        print(f"✗ 识别器测试错误: {str(e)}")
        return False


def test_full_system():
    """测试完整系统"""
    print("\n" + "=" * 50)
    print("测试完整数独识别系统")
    print("=" * 50)
    
    # 检查训练数据
    image_dir = "trainData/image"
    json_dir = "trainData/json"
    
    if not os.path.exists(image_dir) or not os.path.exists(json_dir):
        print("错误: 训练数据目录不存在")
        return False
    
    # 获取测试图像
    image_files = [f for f in os.listdir(image_dir) if f.endswith('.png')]
    if not image_files:
        print("错误: 未找到测试图像")
        return False
    
    test_image = os.path.join(image_dir, image_files[0])
    print(f"测试图像: {test_image}")
    
    try:
        # 初始化完整系统
        system = SudokuRecognizer()
        
        # 测试识别
        sudoku, confidences, grid = system.recognize_from_image(test_image)
        
        if sudoku is not None:
            print("✓ 完整系统识别成功")
            print(f"识别结果:\n{sudoku}")
            print(f"平均置信度: {np.mean(confidences):.3f}")
            
            # 测试可视化
            system.visualize_recognition(test_image, "test_full_system.png")
            print("✓ 可视化完成")
            
            return True
        else:
            print("✗ 完整系统识别失败")
            return False
            
    except Exception as e:
        print(f"✗ 完整系统测试错误: {str(e)}")
        return False


def test_data_loading():
    """测试数据加载"""
    print("\n" + "=" * 50)
    print("测试数据加载")
    print("=" * 50)
    
    image_dir = "trainData/image"
    json_dir = "trainData/json"
    
    if not os.path.exists(image_dir):
        print(f"错误: 图像目录不存在: {image_dir}")
        return False
    
    if not os.path.exists(json_dir):
        print(f"错误: JSON目录不存在: {json_dir}")
        return False
    
    # 统计文件数量
    image_files = [f for f in os.listdir(image_dir) if f.endswith('.png')]
    json_files = [f for f in os.listdir(json_dir) if f.endswith('.json')]
    
    print(f"图像文件数量: {len(image_files)}")
    print(f"JSON文件数量: {len(json_files)}")
    
    if len(image_files) == 0:
        print("✗ 未找到图像文件")
        return False
    
    if len(json_files) == 0:
        print("✗ 未找到JSON文件")
        return False
    
    # 检查文件对应关系
    image_names = {os.path.splitext(f)[0] for f in image_files}
    json_names = {os.path.splitext(f)[0] for f in json_files}
    
    matched = image_names.intersection(json_names)
    print(f"匹配的文件对数量: {len(matched)}")
    
    if len(matched) > 0:
        print("✓ 数据加载测试通过")
        return True
    else:
        print("✗ 没有匹配的图像和JSON文件")
        return False


def main():
    """主测试函数"""
    print("数独识别系统测试")
    print("=" * 50)
    
    tests = [
        ("数据加载", test_data_loading),
        ("数独检测器", test_detector),
        ("数字识别器", test_recognizer),
        ("完整系统", test_full_system)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"✗ {test_name}测试出现异常: {str(e)}")
            results.append((test_name, False))
    
    # 输出测试结果
    print("\n" + "=" * 50)
    print("测试结果汇总")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n总体结果: {passed}/{total} 测试通过")
    
    if passed == total:
        print("🎉 所有测试通过！系统运行正常。")
    else:
        print("⚠️  部分测试失败，请检查系统配置。")


if __name__ == "__main__":
    main()
