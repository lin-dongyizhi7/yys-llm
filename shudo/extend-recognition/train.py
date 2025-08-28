#!/usr/bin/env python3
"""
数独识别模型训练脚本
支持MNIST预训练和数独数据集微调
"""

import os
import argparse
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, random_split
from torchvision import transforms, datasets
import numpy as np
import cv2
import json
from tqdm import tqdm
import matplotlib.pyplot as plt
from digit_recognizer import DigitRecognizer
from sudoku_dataset import SudokuCellDataset


def train_mnist(model, device, epochs=10, batch_size=64, learning_rate=0.001, 
                save_path="models/mnist_pretrained.pth"):
    """
    在MNIST数据集上预训练模型
    
    Args:
        model: 模型
        device: 设备
        epochs: 训练轮数
        batch_size: 批次大小
        learning_rate: 学习率
        save_path: 保存路径
    """
    print("开始MNIST预训练...")
    
    # 创建模型保存目录
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    
    # 数据变换
    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.1307,), (0.3081,))
    ])
    
    # 加载MNIST数据集
    train_dataset = datasets.MNIST('./data', train=True, download=True, transform=transform)
    test_dataset = datasets.MNIST('./data', train=False, transform=transform)
    
    # 创建数据加载器
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)
    
    # 定义损失函数和优化器
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)
    scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=5, gamma=0.5)
    
    # 训练历史
    train_losses = []
    train_accuracies = []
    test_accuracies = []
    
    # 训练循环
    best_accuracy = 0.0
    
    for epoch in range(epochs):
        # 训练阶段
        model.train()
        running_loss = 0.0
        correct = 0
        total = 0
        
        pbar = tqdm(train_loader, desc=f'Epoch {epoch+1}/{epochs}')
        for batch_idx, (data, target) in enumerate(pbar):
            data, target = data.to(device), target.to(device)
            
            optimizer.zero_grad()
            output = model(data)
            loss = criterion(output, target)
            loss.backward()
            optimizer.step()
            
            running_loss += loss.item()
            _, predicted = torch.max(output.data, 1)
            total += target.size(0)
            correct += predicted.eq(target.data).sum().item()
            
            pbar.set_postfix({
                'Loss': f'{running_loss/(batch_idx+1):.4f}',
                'Acc': f'{100.*correct/total:.2f}%'
            })
        
        # 计算训练准确率
        train_accuracy = 100. * correct / total
        train_losses.append(running_loss / len(train_loader))
        train_accuracies.append(train_accuracy)
        
        # 测试阶段
        model.eval()
        test_correct = 0
        test_total = 0
        
        with torch.no_grad():
            for data, target in test_loader:
                data, target = data.to(device), target.to(device)
                output = model(data)
                _, predicted = torch.max(output.data, 1)
                test_total += target.size(0)
                test_correct += predicted.eq(target.data).sum().item()
        
        test_accuracy = 100. * test_correct / test_total
        test_accuracies.append(test_accuracy)
        
        print(f'Epoch {epoch+1}: Train Loss: {train_losses[-1]:.4f}, '
              f'Train Acc: {train_accuracy:.2f}%, Test Acc: {test_accuracy:.2f}%')
        
        # 保存最佳模型
        if test_accuracy > best_accuracy:
            best_accuracy = test_accuracy
            torch.save({
                'epoch': epoch,
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'best_accuracy': best_accuracy,
                'train_losses': train_losses,
                'train_accuracies': train_accuracies,
                'test_accuracies': test_accuracies
            }, save_path)
            print(f"新的最佳模型已保存，准确率: {best_accuracy:.2f}%")
        
        scheduler.step()
    
    print(f"MNIST预训练完成！最佳测试准确率: {best_accuracy:.2f}%")
    
    # 绘制训练曲线
    plot_training_curves(train_losses, train_accuracies, test_accuracies, 
                        save_path="training_curves_mnist.png")
    
    return best_accuracy


def train_sudoku(model, device, image_dir, json_dir, epochs=20, batch_size=16, 
                 learning_rate=0.0001, save_path="models/sudoku_finetuned.pth"):
    """
    在数独数据集上微调模型
    
    Args:
        model: 预训练模型
        device: 设备
        image_dir: 图像目录
        json_dir: JSON标注目录
        epochs: 训练轮数
        batch_size: 批次大小
        learning_rate: 学习率
        save_path: 保存路径
    """
    print("开始数独数据集微调...")
    
    # 创建模型保存目录
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    
    # 创建数据集
    dataset = SudokuCellDataset(image_dir, json_dir, cell_size=28, augment=True)
    
    # 分割训练集和验证集
    train_size = int(0.8 * len(dataset))
    val_size = len(dataset) - train_size
    train_dataset, val_dataset = random_split(dataset, [train_size, val_size])
    
    # 创建数据加载器
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)
    
    print(f"训练集大小: {len(train_dataset)}, 验证集大小: {len(val_dataset)}")
    
    # 定义损失函数和优化器
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='min', patience=3, factor=0.5)
    
    # 训练历史
    train_losses = []
    val_losses = []
    val_accuracies = []
    
    # 训练循环
    best_val_loss = float('inf')
    
    for epoch in range(epochs):
        # 训练阶段
        model.train()
        running_loss = 0.0
        
        pbar = tqdm(train_loader, desc=f'Epoch {epoch+1}/{epochs}')
        for batch_idx, (data, target) in enumerate(pbar):
            data, target = data.to(device), target.to(device)
            
            optimizer.zero_grad()
            output = model(data)
            
            # 重塑输出和目标以匹配损失函数
            output = output.view(-1, 10)
            target = target.view(-1)
            
            loss = criterion(output, target)
            loss.backward()
            optimizer.step()
            
            running_loss += loss.item()
            pbar.set_postfix({'Loss': f'{running_loss/(batch_idx+1):.4f}'})
        
        train_loss = running_loss / len(train_loader)
        train_losses.append(train_loss)
        
        # 验证阶段
        model.eval()
        val_loss = 0.0
        val_correct = 0
        val_total = 0
        
        with torch.no_grad():
            for data, target in val_loader:
                data, target = data.to(device), target.to(device)
                output = model(data)
                
                # 重塑输出和目标
                output = output.view(-1, 10)
                target = target.view(-1)
                
                loss = criterion(output, target)
                val_loss += loss.item()
                
                _, predicted = torch.max(output.data, 1)
                val_total += target.size(0)
                val_correct += predicted.eq(target.data).sum().item()
        
        val_loss = val_loss / len(val_loader)
        val_accuracy = 100. * val_correct / val_total
        
        val_losses.append(val_loss)
        val_accuracies.append(val_accuracy)
        
        print(f'Epoch {epoch+1}: Train Loss: {train_loss:.4f}, '
              f'Val Loss: {val_loss:.4f}, Val Acc: {val_accuracy:.2f}%')
        
        # 学习率调度
        scheduler.step(val_loss)
        
        # 保存最佳模型
        if val_loss < best_val_loss:
            best_val_loss = val_loss
            torch.save({
                'epoch': epoch,
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'best_val_loss': best_val_loss,
                'train_losses': train_losses,
                'val_losses': val_losses,
                'val_accuracies': val_accuracies
            }, save_path)
            print(f"新的最佳模型已保存，验证损失: {best_val_loss:.4f}")
        
        # 每5个epoch保存一次检查点
        if (epoch + 1) % 5 == 0:
            checkpoint_path = f"{save_path}_epoch_{epoch+1}.pth"
            torch.save({
                'epoch': epoch,
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'train_losses': train_losses,
                'val_losses': val_losses,
                'val_accuracies': val_accuracies
            }, checkpoint_path)
            print(f"检查点已保存: {checkpoint_path}")
    
    print(f"数独数据集微调完成！最佳验证损失: {best_val_loss:.4f}")
    
    # 绘制训练曲线
    plot_training_curves(train_losses, val_accuracies, val_accuracies, 
                        save_path="training_curves_sudoku.png", 
                        labels=['训练损失', '验证准确率', '验证准确率'])
    
    return best_val_loss


def plot_training_curves(train_losses, train_accuracies, test_accuracies, 
                        save_path="training_curves.png", 
                        labels=['训练损失', '训练准确率', '测试准确率']):
    """
    绘制训练曲线
    
    Args:
        train_losses: 训练损失列表
        train_accuracies: 训练准确率列表
        test_accuracies: 测试准确率列表
        save_path: 保存路径
        labels: 标签列表
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5))
    
    # 损失曲线
    ax1.plot(train_losses, label=labels[0])
    ax1.set_title('训练损失')
    ax1.set_xlabel('Epoch')
    ax1.set_ylabel('Loss')
    ax1.legend()
    ax1.grid(True)
    
    # 准确率曲线
    ax2.plot(train_accuracies, label=labels[1])
    ax2.plot(test_accuracies, label=labels[2])
    ax2.set_title('准确率')
    ax2.set_xlabel('Epoch')
    ax2.set_ylabel('Accuracy (%)')
    ax2.legend()
    ax2.grid(True)
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"训练曲线已保存到: {save_path}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='数独识别模型训练')
    parser.add_argument('--mode', type=str, default='both', 
                       choices=['mnist', 'sudoku', 'both'],
                       help='训练模式: mnist预训练, sudoku微调, 或both')
    parser.add_argument('--image_dir', type=str, default='trainData/image',
                       help='数独图像目录')
    parser.add_argument('--json_dir', type=str, default='trainData/json',
                       help='数独JSON标注目录')
    parser.add_argument('--mnist_epochs', type=int, default=10,
                       help='MNIST预训练轮数')
    parser.add_argument('--sudoku_epochs', type=int, default=20,
                       help='数独微调轮数')
    parser.add_argument('--batch_size', type=int, default=64,
                       help='批次大小')
    parser.add_argument('--learning_rate', type=float, default=0.001,
                       help='学习率')
    parser.add_argument('--mnist_model_path', type=str, default='models/mnist_pretrained.pth',
                       help='MNIST预训练模型保存路径')
    parser.add_argument('--sudoku_model_path', type=str, default='models/sudoku_finetuned.pth',
                       help='数独微调模型保存路径')
    
    args = parser.parse_args()
    
    # 检查CUDA可用性
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"使用设备: {device}")
    
    # 创建模型
    model = DigitRecognizer().model
    model.to(device)
    
    if args.mode in ['mnist', 'both']:
        # MNIST预训练
        print("=" * 50)
        print("开始MNIST预训练")
        print("=" * 50)
        
        best_acc = train_mnist(
            model=model,
            device=device,
            epochs=args.mnist_epochs,
            batch_size=args.batch_size,
            learning_rate=args.learning_rate,
            save_path=args.mnist_model_path
        )
        
        print(f"MNIST预训练完成，最佳准确率: {best_acc:.2f}%")
    
    if args.mode in ['sudoku', 'both']:
        # 数独数据集微调
        print("=" * 50)
        print("开始数独数据集微调")
        print("=" * 50)
        
        # 检查数据路径
        if not os.path.exists(args.image_dir) or not os.path.exists(args.json_dir):
            print(f"错误: 数据路径不存在")
            print(f"图像目录: {args.image_dir}")
            print(f"JSON目录: {args.json_dir}")
            return
        
        best_loss = train_sudoku(
            model=model,
            device=device,
            image_dir=args.image_dir,
            json_dir=args.json_dir,
            epochs=args.sudoku_epochs,
            batch_size=args.batch_size // 4,  # 数独数据集使用较小的批次
            learning_rate=args.learning_rate / 10,  # 微调使用较小的学习率
            save_path=args.sudoku_model_path
        )
        
        print(f"数独数据集微调完成，最佳验证损失: {best_loss:.4f}")
    
    print("=" * 50)
    print("训练完成！")
    print("=" * 50)


if __name__ == "__main__":
    main()
