import cv2
import numpy as np
import os
import json
from typing import List, Tuple, Optional, Dict
import matplotlib.pyplot as plt
from sudoku_detector import SudokuDetector
from digit_recognizer import DigitRecognizer


class SudokuRecognizer:
    """完整的数独识别系统"""
    
    def __init__(self, detector_model_path: Optional[str] = None, 
                 recognizer_model_path: Optional[str] = None):
        """
        初始化数独识别系统
        
        Args:
            detector_model_path: 检测器模型路径
            recognizer_model_path: 识别器模型路径
        """
        # 初始化检测器和识别器
        self.detector = SudokuDetector(detector_model_path)
        self.recognizer = DigitRecognizer(recognizer_model_path)
        
        print("数独识别系统初始化完成")
    
    def recognize_from_image(self, image_path: str) -> Tuple[Optional[np.ndarray], 
                                                           Optional[np.ndarray], 
                                                           Optional[np.ndarray]]:
        """
        从图像识别数独
        
        Args:
            image_path: 图像文件路径
            
        Returns:
            (识别的数独, 置信度矩阵, 检测到的网格) 的元组
        """
        print(f"正在识别图像: {image_path}")
        
        # 检测数独网格
        grid, cells = self.detector.detect_sudoku(image_path)
        
        if grid is None or cells is None:
            print("未能检测到数独网格")
            return None, None, None
        
        print("成功检测到数独网格，开始识别数字...")
        
        # 识别数字
        sudoku, confidences = self.recognizer.recognize_sudoku(cells)
        
        print("数字识别完成！")
        print(f"识别结果:\n{sudoku}")
        print(f"平均置信度: {np.mean(confidences):.3f}")
        
        return sudoku, confidences, grid
    
    def batch_recognize(self, image_dir: str, json_dir: str, 
                       output_dir: str = "recognition_results") -> Dict[str, Dict]:
        """
        批量识别数独图像
        
        Args:
            image_dir: 图像目录
            json_dir: JSON标注目录
            output_dir: 输出目录
            
        Returns:
            识别结果字典
        """
        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)
        
        # 获取所有图像文件
        image_files = [f for f in os.listdir(image_dir) if f.endswith('.png')]
        
        results = {}
        total_images = len(image_files)
        
        print(f"开始批量识别 {total_images} 张图像...")
        
        for i, image_file in enumerate(image_files):
            print(f"\n处理图像 {i+1}/{total_images}: {image_file}")
            
            image_path = os.path.join(image_dir, image_file)
            json_file = image_file.replace('.png', '.json')
            json_path = os.path.join(json_dir, json_file)
            
            # 识别数独
            sudoku, confidences, grid = self.recognize_from_image(image_path)
            
            if sudoku is not None:
                # 读取真实标签
                ground_truth = None
                if os.path.exists(json_path):
                    with open(json_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        ground_truth = np.array(data['data'])
                
                # 计算准确率
                accuracy = None
                if ground_truth is not None:
                    # 只计算非零位置（有数字的位置）
                    mask = ground_truth != 0
                    if np.any(mask):
                        accuracy = np.mean(sudoku[mask] == ground_truth[mask])
                
                # 保存结果
                result = {
                    'recognized_sudoku': sudoku.tolist(),
                    'confidences': confidences.tolist(),
                    'ground_truth': ground_truth.tolist() if ground_truth is not None else None,
                    'accuracy': accuracy,
                    'average_confidence': float(np.mean(confidences))
                }
                
                results[image_file] = result
                
                # 保存网格图像
                if grid is not None:
                    grid_path = os.path.join(output_dir, f"{image_file}_grid.png")
                    cv2.imwrite(grid_path, grid)
                
                # 保存识别结果到JSON
                result_path = os.path.join(output_dir, f"{image_file}_result.json")
                with open(result_path, 'w', encoding='utf-8') as f:
                    json.dump(result, f, ensure_ascii=False, indent=2)
                
                print(f"识别完成，准确率: {accuracy:.3f if accuracy else 'N/A'}")
            else:
                print("识别失败")
                results[image_file] = {'error': 'Recognition failed'}
        
        # 保存总体结果
        overall_result = {
            'total_images': total_images,
            'successful_recognition': len([r for r in results.values() if 'error' not in r]),
            'overall_accuracy': np.mean([r['accuracy'] for r in results.values() 
                                       if 'accuracy' in r and r['accuracy'] is not None]),
            'average_confidence': np.mean([r['average_confidence'] for r in results.values() 
                                         if 'average_confidence' in r]),
            'results': results
        }
        
        overall_path = os.path.join(output_dir, "overall_results.json")
        with open(overall_path, 'w', encoding='utf-8') as f:
            json.dump(overall_result, f, ensure_ascii=False, indent=2)
        
        print(f"\n批量识别完成！")
        print(f"成功识别: {overall_result['successful_recognition']}/{total_images}")
        print(f"总体准确率: {overall_result['overall_accuracy']:.3f}")
        print(f"平均置信度: {overall_result['average_confidence']:.3f}")
        
        return overall_result
    
    def visualize_recognition(self, image_path: str, save_path: Optional[str] = None):
        """
        可视化识别结果
        
        Args:
            image_path: 输入图像路径
            save_path: 保存路径
        """
        # 识别数独
        sudoku, confidences, grid = self.recognize_from_image(image_path)
        
        if sudoku is None:
            print("无法识别数独")
            return
        
        # 创建可视化图像
        fig, axes = plt.subplots(1, 3, figsize=(15, 5))
        
        # 原始图像
        original = cv2.imread(image_path)
        original_rgb = cv2.cvtColor(original, cv2.COLOR_BGR2RGB)
        axes[0].imshow(original_rgb)
        axes[0].set_title('原始图像')
        axes[0].axis('off')
        
        # 检测到的网格
        if grid is not None:
            grid_rgb = cv2.cvtColor(grid, cv2.COLOR_BGR2RGB)
            axes[1].imshow(grid_rgb)
            axes[1].set_title('检测到的网格')
            axes[1].axis('off')
        
        # 识别结果
        axes[2].imshow(np.zeros((9, 9)), cmap='gray')
        axes[2].set_title('识别结果')
        
        # 在网格上显示数字
        for i in range(9):
            for j in range(9):
                digit = sudoku[i, j]
                confidence = confidences[i, j]
                color = 'red' if confidence < 0.5 else 'black'
                axes[2].text(j, i, str(digit), ha='center', va='center', 
                            fontsize=12, color=color, weight='bold')
        
        axes[2].set_xticks(range(9))
        axes[2].set_yticks(range(9))
        axes[2].grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"可视化结果已保存到: {save_path}")
        else:
            plt.show()
    
    def evaluate_performance(self, image_dir: str, json_dir: str) -> Dict:
        """
        评估识别性能
        
        Args:
            image_dir: 图像目录
            json_dir: JSON标注目录
            
        Returns:
            性能评估结果
        """
        print("开始性能评估...")
        
        # 批量识别
        results = self.batch_recognize(image_dir, json_dir, "evaluation_results")
        
        # 计算详细指标
        successful_results = [r for r in results['results'].values() if 'error' not in r]
        
        if not successful_results:
            print("没有成功的识别结果")
            return results
        
        # 计算每个数字的识别准确率
        digit_accuracies = {i: [] for i in range(10)}
        digit_confidences = {i: [] for i in range(10)}
        
        for result in successful_results:
            sudoku = np.array(result['recognized_sudoku'])
            ground_truth = np.array(result['ground_truth'])
            confidences = np.array(result['confidences'])
            
            if ground_truth is not None:
                for i in range(9):
                    for j in range(9):
                        if ground_truth[i, j] != 0:  # 只计算有数字的位置
                            digit = ground_truth[i, j]
                            predicted = sudoku[i, j]
                            confidence = confidences[i, j]
                            
                            digit_accuracies[digit].append(1 if predicted == digit else 0)
                            digit_confidences[digit].append(confidence)
        
        # 计算统计信息
        performance_metrics = {
            'overall_accuracy': results['overall_accuracy'],
            'average_confidence': results['average_confidence'],
            'digit_wise_accuracy': {},
            'digit_wise_confidence': {},
            'confusion_matrix': np.zeros((10, 10), dtype=int)
        }
        
        for digit in range(10):
            if digit_accuracies[digit]:
                performance_metrics['digit_wise_accuracy'][digit] = np.mean(digit_accuracies[digit])
                performance_metrics['digit_wise_confidence'][digit] = np.mean(digit_confidences[digit])
            else:
                performance_metrics['digit_wise_accuracy'][digit] = 0.0
                performance_metrics['digit_wise_confidence'][digit] = 0.0
        
        # 计算混淆矩阵
        for result in successful_results:
            sudoku = np.array(result['recognized_sudoku'])
            ground_truth = np.array(result['ground_truth'])
            
            if ground_truth is not None:
                for i in range(9):
                    for j in range(9):
                        if ground_truth[i, j] != 0:
                            true_digit = ground_truth[i, j]
                            pred_digit = sudoku[i, j]
                            performance_metrics['confusion_matrix'][true_digit][pred_digit] += 1
        
        # 保存性能指标
        metrics_path = "evaluation_results/performance_metrics.json"
        with open(metrics_path, 'w', encoding='utf-8') as f:
            # 转换numpy数组为列表以便JSON序列化
            metrics_copy = performance_metrics.copy()
            metrics_copy['confusion_matrix'] = metrics_copy['confusion_matrix'].tolist()
            json.dump(metrics_copy, f, ensure_ascii=False, indent=2)
        
        print("性能评估完成！")
        print(f"总体准确率: {performance_metrics['overall_accuracy']:.3f}")
        print(f"平均置信度: {performance_metrics['average_confidence']:.3f}")
        
        # 打印每个数字的准确率
        print("\n各数字识别准确率:")
        for digit, acc in performance_metrics['digit_wise_accuracy'].items():
            conf = performance_metrics['digit_wise_confidence'][digit]
            print(f"数字 {digit}: 准确率 {acc:.3f}, 置信度 {conf:.3f}")
        
        return performance_metrics


def main():
    """主函数 - 演示数独识别系统"""
    
    # 初始化识别系统
    recognizer = SudokuRecognizer()
    
    # 设置路径
    image_dir = "trainData/image"
    json_dir = "trainData/json"
    
    # 检查路径是否存在
    if not os.path.exists(image_dir) or not os.path.exists(json_dir):
        print(f"训练数据路径不存在: {image_dir} 或 {json_dir}")
        return
    
    # 选择操作模式
    print("数独识别系统")
    print("1. 单张图像识别")
    print("2. 批量识别")
    print("3. 性能评估")
    print("4. 训练模型")
    
    choice = input("请选择操作 (1-4): ").strip()
    
    if choice == "1":
        # 单张图像识别
        image_files = [f for f in os.listdir(image_dir) if f.endswith('.png')]
        if image_files:
            test_image = os.path.join(image_dir, image_files[0])
            print(f"测试图像: {test_image}")
            
            # 识别
            sudoku, confidences, grid = recognizer.recognize_from_image(test_image)
            
            if sudoku is not None:
                # 可视化结果
                recognizer.visualize_recognition(test_image, "recognition_result.png")
    
    elif choice == "2":
        # 批量识别
        recognizer.batch_recognize(image_dir, json_dir)
    
    elif choice == "3":
        # 性能评估
        recognizer.evaluate_performance(image_dir, json_dir)
    
    elif choice == "4":
        # 训练模型
        print("开始训练数字识别模型...")
        
        # 在MNIST上预训练
        print("1. MNIST预训练")
        recognizer.recognizer.train_on_mnist(epochs=5)
        
        # 在数独数据集上微调
        print("2. 数独数据集微调")
        recognizer.recognizer.train_on_sudoku(
            image_dir=image_dir,
            json_dir=json_dir,
            epochs=10
        )
        
        print("训练完成！")
    
    else:
        print("无效选择")


if __name__ == "__main__":
    main()
