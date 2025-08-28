import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import torchvision.transforms as transforms
import torchvision.datasets as datasets
from torchvision import models
import numpy as np
import cv2
import os
import json
from typing import List, Tuple, Optional
import matplotlib.pyplot as plt
from tqdm import tqdm


class DigitCNN(nn.Module):
    """轻量级CNN模型用于数字识别"""
    
    def __init__(self, num_classes: int = 10):
        super(DigitCNN, self).__init__()
        
        # 简化的CNN架构，避免尺寸计算问题
        self.features = nn.Sequential(
            # 第一个卷积块: 28x28 -> 14x14
            nn.Conv2d(1, 32, kernel_size=3, padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2, 2),
            
            # 第二个卷积块: 14x14 -> 7x7
            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2, 2),
            
            # 第三个卷积块: 7x7 -> 7x7 (保持尺寸)
            nn.Conv2d(64, 128, kernel_size=3, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(inplace=True),
        )
        
        # 全连接层: 7x7x128 = 6272
        self.classifier = nn.Sequential(
            nn.Linear(128 * 7 * 7, 256),
            nn.ReLU(inplace=True),
            nn.Dropout(0.5),
            nn.Linear(256, num_classes)
        )
        
    def forward(self, x):
        # 特征提取
        x = self.features(x)
        
        # 展平: 128 * 7 * 7 = 6272
        x = x.view(x.size(0), -1)
        
        # 分类
        x = self.classifier(x)
        
        return x


class SudokuDataset(Dataset):
    """数独数据集类 - 修复版本"""
    
    def __init__(self, image_dir: str, json_dir: str, transform=None, cell_size: int = 28):
        """
        初始化数据集
        
        Args:
            image_dir: 图像目录路径
            json_dir: JSON标注文件路径
            transform: 图像变换
            cell_size: 单元格大小
        """
        self.image_dir = image_dir
        self.json_dir = json_dir
        self.transform = transform
        self.cell_size = cell_size
        
        # 获取所有图像文件
        self.image_files = [f for f in os.listdir(image_dir) if f.endswith('.png')]
        
        # 数据增强变换
        if transform is None:
            self.transform = transforms.Compose([
                transforms.ToPILImage(),
                transforms.Resize((cell_size, cell_size)),
                transforms.ToTensor(),
                transforms.Normalize((0.1307,), (0.3081,))  # MNIST标准化
            ])
        
        # 预加载所有数据
        self.data_pairs = []
        self._load_all_data()
    
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
                            # 提取单元格图像 (这里需要实际的单元格分割逻辑)
                            # 暂时使用整个图像作为占位符
                            self.data_pairs.append((image, digit))
                
            except Exception as e:
                print(f"加载数据时出错 {img_name}: {e}")
                continue
        
        print(f"成功加载 {len(self.data_pairs)} 个训练样本")
    
    def __len__(self):
        return len(self.data_pairs)
    
    def __getitem__(self, idx):
        if idx >= len(self.data_pairs):
            return torch.zeros(1, self.cell_size, self.cell_size), torch.tensor(0)
        
        image, digit = self.data_pairs[idx]
        
        # 应用变换
        if self.transform:
            image = self.transform(image)
        
        return image, torch.tensor(digit, dtype=torch.long)


class DigitRecognizer:
    """数字识别器类"""
    
    def __init__(self, model_path: Optional[str] = None):
        """
        初始化数字识别器
        
        Args:
            model_path: 预训练模型路径
        """
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        print(f"使用设备: {self.device}")
        
        # 创建模型
        self.model = DigitCNN(num_classes=10)
        self.model.to(self.device)
        
        # 加载预训练模型
        if model_path and os.path.exists(model_path):
            self.load_model(model_path)
            print(f"已加载预训练模型: {model_path}")
        else:
            print("使用随机初始化的模型")
        
        # 图像预处理
        self.transform = transforms.Compose([
            transforms.ToPILImage(),
            transforms.Resize((28, 28)),
            transforms.ToTensor(),
            transforms.Normalize((0.1307,), (0.3081,))
        ])
    
    def load_model(self, model_path: str):
        """加载预训练模型"""
        checkpoint = torch.load(model_path, map_location=self.device)
        if 'model_state_dict' in checkpoint:
            self.model.load_state_dict(checkpoint['model_state_dict'])
        else:
            self.model.load_state_dict(checkpoint)
        self.model.eval()
    
    def save_model(self, model_path: str, epoch: int = 0, optimizer_state: Optional[dict] = None):
        """保存模型"""
        checkpoint = {
            'epoch': epoch,
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': optimizer_state
        }
        torch.save(checkpoint, model_path)
        print(f"模型已保存到: {model_path}")
    
    def preprocess_cell(self, cell_image: np.ndarray) -> torch.Tensor:
        """
        预处理单元格图像
        
        Args:
            cell_image: 单元格图像
            
        Returns:
            预处理后的张量
        """
        # 转换为灰度图
        if len(cell_image.shape) == 3:
            cell_image = cv2.cvtColor(cell_image, cv2.COLOR_BGR2GRAY)
        
        # 应用变换
        cell_tensor = self.transform(cell_image)
        return cell_tensor.unsqueeze(0).to(self.device)
    
    def recognize_digit(self, cell_image: np.ndarray) -> Tuple[int, float]:
        """
        识别单个数字
        
        Args:
            cell_image: 单元格图像
            
        Returns:
            (识别的数字, 置信度) 的元组
        """
        self.model.eval()
        
        with torch.no_grad():
            # 预处理
            cell_tensor = self.preprocess_cell(cell_image)
            
            # 前向传播
            output = self.model(cell_tensor)
            probabilities = F.softmax(output, dim=1)
            
            # 获取预测结果
            predicted = torch.argmax(output, dim=1).item()
            confidence = probabilities[0][predicted].item()
            
            return predicted, confidence
    
    def recognize_sudoku(self, cells: List[List[np.ndarray]]) -> np.ndarray:
        """
        识别整个数独
        
        Args:
            cells: 9x9的单元格图像列表
            
        Returns:
            9x9的数字数组
        """
        sudoku = np.zeros((9, 9), dtype=int)
        confidences = np.zeros((9, 9), dtype=float)
        
        for i in range(9):
            for j in range(9):
                digit, confidence = self.recognize_digit(cells[i][j])
                sudoku[i, j] = digit
                confidences[i, j] = confidence
        
        return sudoku, confidences
    
    def train_on_mnist(self, epochs: int = 10, batch_size: int = 64, 
                       learning_rate: float = 0.001, save_path: str = "digit_model.pth"):
        """
        在MNIST数据集上预训练模型
        
        Args:
            epochs: 训练轮数
            batch_size: 批次大小
            learning_rate: 学习率
            save_path: 模型保存路径
        """
        print("开始MNIST预训练...")
        
        # 加载MNIST数据集
        transform = transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize((0.1307,), (0.3081,))
        ])
        
        train_dataset = datasets.MNIST('./data', train=True, download=True, transform=transform)
        train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
        
        # 定义损失函数和优化器
        criterion = nn.CrossEntropyLoss()
        optimizer = optim.Adam(self.model.parameters(), lr=learning_rate)
        
        # 训练循环
        self.model.train()
        for epoch in range(epochs):
            running_loss = 0.0
            correct = 0
            total = 0
            
            pbar = tqdm(train_loader, desc=f'Epoch {epoch+1}/{epochs}')
            for batch_idx, (data, target) in enumerate(pbar):
                data, target = data.to(self.device), target.to(self.device)
                
                optimizer.zero_grad()
                output = self.model(data)
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
            
            print(f'Epoch {epoch+1}: Loss: {running_loss/len(train_loader):.4f}, '
                  f'Accuracy: {100.*correct/total:.2f}%')
        
        # 保存模型
        self.save_model(save_path)
        print("MNIST预训练完成！")
    
    def train_on_sudoku(self, image_dir: str, json_dir: str, epochs: int = 20, 
                        batch_size: int = 16, learning_rate: float = 0.0001,
                        save_path: str = "sudoku_digit_model.pth"):
        """
        在数独数据集上微调模型
        
        Args:
            image_dir: 图像目录
            json_dir: JSON标注目录
            epochs: 训练轮数
            batch_size: 批次大小
            learning_rate: 学习率
            save_path: 模型保存路径
        """
        print("开始数独数据集微调...")
        
        # 创建数据集和数据加载器
        dataset = SudokuDataset(image_dir, json_dir)
        train_loader = DataLoader(dataset, batch_size=batch_size, shuffle=True)
        
        # 定义损失函数和优化器
        criterion = nn.CrossEntropyLoss()
        optimizer = optim.Adam(self.model.parameters(), lr=learning_rate)
        
        # 训练循环
        self.model.train()
        for epoch in range(epochs):
            running_loss = 0.0
            
            pbar = tqdm(train_loader, desc=f'Epoch {epoch+1}/{epochs}')
            for batch_idx, (data, target) in enumerate(pbar):
                data, target = data.to(self.device), target.to(self.device)
                
                optimizer.zero_grad()
                output = self.model(data)
                
                # 重塑输出和目标以匹配损失函数
                output = output.view(-1, 10)
                target = target.view(-1)
                
                loss = criterion(output, target)
                loss.backward()
                optimizer.step()
                
                running_loss += loss.item()
                pbar.set_postfix({'Loss': f'{running_loss/(batch_idx+1):.4f}'})
            
            print(f'Epoch {epoch+1}: Loss: {running_loss/len(train_loader):.4f}')
            
            # 每5个epoch保存一次
            if (epoch + 1) % 5 == 0:
                self.save_model(f"{save_path}_epoch_{epoch+1}.pth", epoch+1, optimizer.state_dict())
        
        # 保存最终模型
        self.save_model(save_path, epochs, optimizer.state_dict())
        print("数独数据集微调完成！")
    
    def evaluate(self, test_loader: DataLoader) -> float:
        """
        评估模型性能
        
        Args:
            test_loader: 测试数据加载器
            
        Returns:
            准确率
        """
        self.model.eval()
        correct = 0
        total = 0
        
        with torch.no_grad():
            for data, target in test_loader:
                data, target = data.to(self.device), target.to(self.device)
                output = self.model(data)
                
                _, predicted = torch.max(output.data, 1)
                total += target.size(0)
                correct += predicted.eq(target.data).sum().item()
        
        accuracy = 100. * correct / total
        print(f'测试准确率: {accuracy:.2f}%')
        return accuracy


if __name__ == "__main__":
    # 测试代码
    recognizer = DigitRecognizer()
    
    # 在MNIST上预训练
    print("开始MNIST预训练...")
    recognizer.train_on_mnist(epochs=5)
    
    # 在数独数据集上微调
    print("开始数独数据集微调...")
    recognizer.train_on_sudoku(
        image_dir="trainData/image",
        json_dir="trainData/json",
        epochs=10
    )
    
    print("训练完成！")
