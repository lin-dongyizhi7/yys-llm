import cv2
import numpy as np
from ultralytics import YOLO
import os
from typing import List, Tuple, Optional
import json


class SudokuDetector:
    """使用YOLOv8-nano进行数独网格检测和切割"""
    
    def __init__(self, model_path: Optional[str] = None):
        """
        初始化数独检测器
        
        Args:
            model_path: 预训练模型路径，如果为None则使用默认的YOLOv8-nano
        """
        if model_path and os.path.exists(model_path):
            self.model = YOLO(model_path)
        else:
            # 使用预训练的YOLOv8-nano模型
            self.model = YOLO('yolov8n.pt')
        
        self.grid_size = 9  # 数独网格大小
    
    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """
        预处理图像
        
        Args:
            image: 输入图像
            
        Returns:
            预处理后的图像
        """
        # 转换为灰度图
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
        
        # 高斯模糊去噪
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # 自适应阈值处理
        thresh = cv2.adaptiveThreshold(
            blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY_INV, 11, 2
        )
        
        return thresh
    
    def find_sudoku_grid(self, image: np.ndarray) -> Optional[np.ndarray]:
        """
        查找数独网格轮廓
        
        Args:
            image: 预处理后的图像
            
        Returns:
            数独网格的ROI区域，如果未找到则返回None
        """
        # 查找轮廓
        contours, _ = cv2.findContours(
            image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        
        if not contours:
            return None
        
        # 按面积排序，找到最大的轮廓
        contours = sorted(contours, key=cv2.contourArea, reverse=True)
        
        for contour in contours[:10]:  # 只检查前10个最大的轮廓
            # 近似轮廓为多边形
            epsilon = 0.02 * cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, epsilon, True)
            
            # 检查是否为四边形
            if len(approx) == 4:
                # 检查面积是否合理
                area = cv2.contourArea(contour)
                img_area = image.shape[0] * image.shape[1]
                if area > img_area * 0.1:  # 面积应该至少占图像的10%
                    return approx
        
        return None
    
    def order_points(self, pts: np.ndarray) -> np.ndarray:
        """
        对四个角点进行排序：左上、右上、右下、左下
        
        Args:
            pts: 四个角点坐标
            
        Returns:
            排序后的角点坐标
        """
        rect = np.zeros((4, 2), dtype="float32")
        
        # 计算每个点的和与差
        s = pts.sum(axis=1)
        rect[0] = pts[np.argmin(s)]  # 左上
        rect[2] = pts[np.argmax(s)]  # 右下
        
        diff = np.diff(pts, axis=1)
        rect[1] = pts[np.argmin(diff)]  # 右上
        rect[3] = pts[np.argmax(diff)]  # 左下
        
        return rect
    
    def extract_grid(self, image: np.ndarray, corners: np.ndarray, 
                    target_size: int = 450) -> np.ndarray:
        """
        提取并透视变换数独网格
        
        Args:
            image: 原始图像
            corners: 四个角点坐标
            target_size: 目标网格大小
            
        Returns:
            提取的数独网格图像
        """
        # 排序角点
        rect = self.order_points(corners)
        
        # 计算目标矩形的宽度和高度
        widthA = np.sqrt(((rect[2][0] - rect[3][0]) ** 2) + ((rect[2][1] - rect[3][1]) ** 2))
        widthB = np.sqrt(((rect[1][0] - rect[0][0]) ** 2) + ((rect[1][1] - rect[0][1]) ** 2))
        maxWidth = max(int(widthA), int(widthB))
        
        heightA = np.sqrt(((rect[1][0] - rect[2][0]) ** 2) + ((rect[1][1] - rect[2][1]) ** 2))
        heightB = np.sqrt(((rect[0][0] - rect[3][0]) ** 2) + ((rect[0][1] - rect[3][1]) ** 2))
        maxHeight = max(int(heightA), int(heightB))
        
        # 目标点坐标
        dst = np.array([
            [0, 0],
            [maxWidth - 1, 0],
            [maxWidth - 1, maxHeight - 1],
            [0, maxHeight - 1]
        ], dtype="float32")
        
        # 计算透视变换矩阵
        M = cv2.getPerspectiveTransform(rect, dst)
        
        # 应用透视变换
        warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))
        
        # 调整到目标大小
        warped = cv2.resize(warped, (target_size, target_size))
        
        return warped
    
    def split_grid(self, grid_image: np.ndarray) -> List[List[np.ndarray]]:
        """
        将数独网格分割为9x9的单元格
        
        Args:
            grid_image: 数独网格图像
            
        Returns:
            9x9的单元格图像列表
        """
        cells = []
        cell_size = grid_image.shape[0] // self.grid_size
        
        for i in range(self.grid_size):
            row = []
            for j in range(self.grid_size):
                # 提取单元格，留出一些边距
                margin = 2
                cell = grid_image[
                    i * cell_size + margin:(i + 1) * cell_size - margin,
                    j * cell_size + margin:(j + 1) * cell_size - margin
                ]
                row.append(cell)
            cells.append(row)
        
        return cells
    
    def detect_sudoku(self, image_path: str) -> Tuple[Optional[np.ndarray], 
                                                      Optional[List[List[np.ndarray]]]]:
        """
        检测数独并返回网格和分割后的单元格
        
        Args:
            image_path: 图像文件路径
            
        Returns:
            (网格图像, 单元格列表) 的元组
        """
        # 读取图像
        image = cv2.imread(image_path)
        if image is None:
            print(f"无法读取图像: {image_path}")
            return None, None
        
        # 预处理
        processed = self.preprocess_image(image)
        
        # 查找数独网格
        corners = self.find_sudoku_grid(processed)
        if corners is None:
            print("未找到数独网格")
            return None, None
        
        # 提取网格
        grid = self.extract_grid(image, corners)
        
        # 分割单元格
        cells = self.split_grid(grid)
        
        return grid, cells
    
    def visualize_detection(self, image_path: str, save_path: Optional[str] = None):
        """
        可视化检测结果
        
        Args:
            image_path: 输入图像路径
            save_path: 保存路径，如果为None则显示图像
        """
        image = cv2.imread(image_path)
        if image is None:
            print(f"无法读取图像: {image_path}")
            return
        
        processed = self.preprocess_image(image)
        corners = self.find_sudoku_grid(processed)
        
        if corners is not None:
            # 绘制检测到的轮廓
            cv2.drawContours(image, [corners], -1, (0, 255, 0), 3)
            
            # 绘制角点
            for i, point in enumerate(corners):
                cv2.circle(image, tuple(point[0]), 5, (0, 0, 255), -1)
                cv2.putText(image, str(i), tuple(point[0]), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
        
        if save_path:
            cv2.imwrite(save_path, image)
        else:
            cv2.imshow('Sudoku Detection', image)
            cv2.waitKey(0)
            cv2.destroyAllWindows()


if __name__ == "__main__":
    # 测试代码
    detector = SudokuDetector()
    
    # 测试图像路径
    test_image = "trainData/image/2025-08-28T00-39-26-096Z-简单-1.png"
    
    if os.path.exists(test_image):
        print("检测数独...")
        grid, cells = detector.detect_sudoku(test_image)
        
        if grid is not None:
            print(f"成功检测到数独网格，大小: {grid.shape}")
            print(f"分割得到 {len(cells)}x{len(cells[0])} 个单元格")
            
            # 保存检测结果
            cv2.imwrite("detected_grid.png", grid)
            
            # 可视化检测结果
            detector.visualize_detection(test_image, "detection_result.png")
        else:
            print("检测失败")
    else:
        print(f"测试图像不存在: {test_image}")
