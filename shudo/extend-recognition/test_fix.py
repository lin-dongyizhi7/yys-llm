#!/usr/bin/env python3
"""
测试修复后的训练流程
"""

import torch
from sudoku_dataset import SudokuCellDataset
from digit_recognizer import DigitCNN
from torch.utils.data import DataLoader


def test_dataset():
    """测试数据集"""
    print("=" * 50)
    print("测试数独单元格数据集")
    print("=" * 50)
    
    try:
        # 创建数据集
        dataset = SudokuCellDataset(
            image_dir="trainData/image",
            json_dir="trainData/json",
            cell_size=28,
            augment=False
        )
        
        print(f"✅ 数据集创建成功，大小: {len(dataset)}")
        
        if len(dataset) > 0:
            # 测试第一个样本
            cell_image, digit = dataset[0]
            print(f"✅ 第一个样本: 图像形状 {cell_image.shape}, 标签 {digit}")
            
            # 测试数据加载器
            loader = DataLoader(dataset, batch_size=4, shuffle=True)
            
            for batch_idx, (images, labels) in enumerate(loader):
                print(f"✅ 批次 {batch_idx}: 图像 {images.shape}, 标签 {labels.shape}")
                print(f"   标签范围: {labels.min().item()} - {labels.max().item()}")
                break
            
            return True
        else:
            print("❌ 数据集为空")
            return False
            
    except Exception as e:
        print(f"❌ 数据集测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_model():
    """测试模型"""
    print("\n" + "=" * 50)
    print("测试CNN模型")
    print("=" * 50)
    
    try:
        # 创建模型
        model = DigitCNN(num_classes=10)
        print(f"✅ 模型创建成功，参数数量: {sum(p.numel() for p in model.parameters()):,}")
        
        # 创建测试输入
        input_tensor = torch.randn(4, 1, 28, 28)
        print(f"✅ 测试输入创建成功: {input_tensor.shape}")
        
        # 前向传播
        with torch.no_grad():
            output = model(input_tensor)
        
        print(f"✅ 前向传播成功: {output.shape}")
        print(f"   输出形状正确: {output.shape == (4, 10)}")
        
        return True
        
    except Exception as e:
        print(f"❌ 模型测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_training_step():
    """测试训练步骤"""
    print("\n" + "=" * 50)
    print("测试训练步骤")
    print("=" * 50)
    
    try:
        # 创建模型和数据集
        model = DigitCNN(num_classes=10)
        dataset = SudokuCellDataset(
            image_dir="trainData/image",
            json_dir="trainData/json",
            cell_size=28,
            augment=False
        )
        
        if len(dataset) == 0:
            print("❌ 数据集为空，无法测试训练步骤")
            return False
        
        # 创建数据加载器
        loader = DataLoader(dataset, batch_size=2, shuffle=False)
        
        # 获取一个批次
        for images, labels in loader:
            print(f"✅ 获取批次: 图像 {images.shape}, 标签 {labels.shape}")
            
            # 前向传播
            output = model(images)
            print(f"✅ 前向传播: 输出 {output.shape}")
            
            # 计算损失
            criterion = torch.nn.CrossEntropyLoss()
            loss = criterion(output, labels)
            print(f"✅ 损失计算: {loss.item():.4f}")
            
            # 反向传播
            loss.backward()
            print(f"✅ 反向传播成功")
            
            break
        
        return True
        
    except Exception as e:
        print(f"❌ 训练步骤测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主测试函数"""
    print("数独识别系统修复测试")
    print("=" * 50)
    
    tests = [
        ("数据集测试", test_dataset),
        ("模型测试", test_model),
        ("训练步骤测试", test_training_step)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name}出现异常: {str(e)}")
            results.append((test_name, False))
    
    # 输出测试结果
    print("\n" + "=" * 50)
    print("测试结果汇总")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n总体结果: {passed}/{total} 测试通过")
    
    if passed == total:
        print("🎉 所有测试通过！修复成功。")
        print("\n现在可以运行训练脚本了:")
        print("python train.py --mode sudoku --sudoku_epochs 10")
    else:
        print("⚠️  部分测试失败，请检查修复。")


if __name__ == "__main__":
    main()
