#!/usr/bin/env python3
"""
专门的数独数据集类
用于训练数字识别模型
"""

import torch
from torch.utils.data import Dataset
import torchvision.transforms as transforms
import cv2
import numpy as np
import os
import json
from typing import Tuple, List


class SudokuCellDataset(Dataset):
    """数独单元格数据集类"""
    
    def __init__(self, image_dir: str, json_dir: str, cell_size: int = 28, 
                 augment: bool = True):
        """
        初始化数据集
        
        Args:
            image_dir: 图像目录路径
            json_dir: JSON标注文件路径
            cell_size: 单元格大小
            augment: 是否使用数据增强
        """
        self.image_dir = image_dir
        self.json_dir = json_dir
        self.cell_size = cell_size
        self.augment = augment
        
        # 获取所有图像文件
        self.image_files = [f for f in os.listdir(image_dir) if f.endswith('.png')]
        
        # 数据变换
        if augment:
            self.transform = transforms.Compose([
                transforms.ToPILImage(),
                transforms.Resize((cell_size, cell_size)),
                transforms.RandomRotation(10),  # 随机旋转
                transforms.RandomAffine(degrees=0, translate=(0.1, 0.1)),  # 随机平移
                transforms.ToTensor(),
                transforms.Normalize((0.1307,), (0.3081,))  # MNIST标准化
            ])
        else:
            self.transform = transforms.Compose([
                transforms.ToPILImage(),
                transforms.Resize((cell_size, cell_size)),
                transforms.ToTensor(),
                transforms.Normalize((0.1307,), (0.3081,))  # MNIST标准化
            ])
        
        # 预加载所有数据
        self.data_pairs = []
        self._load_all_data()
    
    def _extract_cell(self, image: np.ndarray, row: int, col: int) -> np.ndarray:
        """
        从数独图像中提取指定位置的单元格
        
        Args:
            image: 数独图像
            row: 行索引 (0-8)
            col: 列索引 (0-8)
            
        Returns:
            提取的单元格图像
        """
        # 计算单元格尺寸
        h, w = image.shape
        cell_h = h // 9
        cell_w = w // 9
        
        # 计算单元格边界
        y1 = row * cell_h
        y2 = (row + 1) * cell_h
        x1 = col * cell_w
        x2 = (col + 1) * cell_w
        
        # 提取单元格，留出一些边距
        margin = 2
        y1 = max(0, y1 + margin)
        y2 = min(h, y2 - margin)
        x1 = max(0, x1 + margin)
        x2 = min(w, x2 - margin)
        
        cell = image[y1:y2, x1:x2]
        
        return cell
    
    def _load_all_data(self):
        """预加载所有数据"""
        print("正在加载数独数据集...")
        
        for img_name in self.image_files:
            img_path = os.path.join(self.image_dir, img_name)
            json_name = img_name.replace('.png', '.json')
            json_path = os.path.join(self.json_dir, json_name)
            
            if not os.path.exists(json_path):
                continue
            
            try:
                # 读取图像
                image = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
                if image is None:
                    continue
                
                # 读取JSON数据
                with open(json_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                sudoku_data = data['data']
                
                # 为每个非零数字创建训练样本
                for i in range(9):
                    for j in range(9):
                        digit = sudoku_data[i][j]
                        if digit != 0:  # 只处理有数字的单元格
                            # 提取单元格图像
                            cell_image = self._extract_cell(image, i, j)
                            
                            # 检查单元格是否有效
                            if cell_image.size > 0 and np.std(cell_image) > 10:  # 避免空白单元格
                                self.data_pairs.append((cell_image, digit))
                
            except Exception as e:
                print(f"加载数据时出错 {img_name}: {e}")
                continue
        
        print(f"成功加载 {len(self.data_pairs)} 个训练样本")
        
        # 统计各数字的分布
        digit_counts = {}
        for _, digit in self.data_pairs:
            digit_counts[digit] = digit_counts.get(digit, 0) + 1
        
        print("数字分布:")
        for digit in sorted(digit_counts.keys()):
            print(f"  数字 {digit}: {digit_counts[digit]} 个")
    
    def __len__(self):
        return len(self.data_pairs)
    
    def __getitem__(self, idx):
        if idx >= len(self.data_pairs):
            return torch.zeros(1, self.cell_size, self.cell_size), torch.tensor(0)
        
        cell_image, digit = self.data_pairs[idx]
        
        # 应用变换
        if self.transform:
            cell_tensor = self.transform(cell_image)
        else:
            # 如果没有变换，直接转换为张量
            cell_tensor = torch.from_numpy(cell_image).float().unsqueeze(0)
            cell_tensor = cell_tensor / 255.0  # 归一化到 [0, 1]
        
        return cell_tensor, torch.tensor(digit, dtype=torch.long)


class SudokuGridDataset(Dataset):
    """数独网格数据集类 - 用于端到端训练"""
    
    def __init__(self, image_dir: str, json_dir: str, grid_size: int = 224):
        """
        初始化数据集
        
        Args:
            image_dir: 图像目录路径
            json_dir: JSON标注文件路径
            grid_size: 网格图像大小
        """
        self.image_dir = image_dir
        self.json_dir = json_dir
        self.grid_size = grid_size
        
        # 获取所有图像文件
        self.image_files = [f for f in os.listdir(image_dir) if f.endswith('.png')]
        
        # 数据变换
        self.transform = transforms.Compose([
            transforms.ToPILImage(),
            transforms.Resize((grid_size, grid_size)),
            transforms.ToTensor(),
            transforms.Normalize((0.1307,), (0.3081,))
        ])
        
        # 预加载所有数据
        self.data_pairs = []
        self._load_all_data()
    
    def _load_all_data(self):
        """预加载所有数据"""
        print("正在加载数独网格数据集...")
        
        for img_name in self.image_files:
            img_path = os.path.join(self.image_dir, img_name)
            json_name = img_name.replace('.png', '.json')
            json_path = os.path.join(self.json_dir, json_name)
            
            if not os.path.exists(json_path):
                continue
            
            try:
                # 读取图像
                image = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
                if image is None:
                    continue
                
                # 读取JSON数据
                with open(json_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                sudoku_data = data['data']
                
                # 创建标签张量 (9x9)
                labels = torch.zeros(9, 9, dtype=torch.long)
                for i in range(9):
                    for j in range(9):
                        labels[i, j] = sudoku_data[i][j]
                
                self.data_pairs.append((image, labels))
                
            except Exception as e:
                print(f"加载数据时出错 {img_name}: {e}")
                continue
        
        print(f"成功加载 {len(self.data_pairs)} 个数独网格")
    
    def __len__(self):
        return len(self.data_pairs)
    
    def __getitem__(self, idx):
        if idx >= len(self.data_pairs):
            return torch.zeros(1, self.grid_size, self.grid_size), torch.zeros(9, 9, dtype=torch.long)
        
        image, labels = self.data_pairs[idx]
        
        # 应用变换
        if self.transform:
            image_tensor = self.transform(image)
        else:
            image_tensor = torch.from_numpy(image).float().unsqueeze(0) / 255.0
        
        return image_tensor, labels


def test_dataset():
    """测试数据集"""
    print("测试数独数据集...")
    
    # 测试单元格数据集
    cell_dataset = SudokuCellDataset(
        image_dir="trainData/image",
        json_dir="trainData/json",
        cell_size=28,
        augment=False
    )
    
    print(f"单元格数据集大小: {len(cell_dataset)}")
    
    if len(cell_dataset) > 0:
        # 测试第一个样本
        cell_image, digit = cell_dataset[0]
        print(f"第一个样本: 图像形状 {cell_image.shape}, 标签 {digit}")
        
        # 测试数据加载器
        from torch.utils.data import DataLoader
        loader = DataLoader(cell_dataset, batch_size=4, shuffle=True)
        
        for batch_idx, (images, labels) in enumerate(loader):
            print(f"批次 {batch_idx}: 图像 {images.shape}, 标签 {labels.shape}")
            break
    
    # 测试网格数据集
    grid_dataset = SudokuGridDataset(
        image_dir="trainData/image",
        json_dir="trainData/json",
        grid_size=224
    )
    
    print(f"网格数据集大小: {len(grid_dataset)}")
    
    if len(grid_dataset) > 0:
        grid_image, grid_labels = grid_dataset[0]
        print(f"第一个网格样本: 图像形状 {grid_image.shape}, 标签形状 {grid_labels.shape}")


if __name__ == "__main__":
    test_dataset()
