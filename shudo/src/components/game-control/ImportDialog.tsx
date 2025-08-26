import React, { useState, useRef } from 'react';
import './ImportDialog.css';
import { quickRecognize, quickRecognizeOCR, RecognitionResult } from '../../utils/imageRecognition';

interface ImportDialogProps {
  isOpen: boolean;
  onClose: () => void;
  onImport: (board: number[][]) => void;
}

const ImportDialog: React.FC<ImportDialogProps> = ({ isOpen, onClose, onImport }) => {
  const [fileType, setFileType] = useState<'json' | 'image'>('json');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string>('');
  const [imagePreview, setImagePreview] = useState<string>('');
  const [recognitionMethod, setRecognitionMethod] = useState<'transformer' | 'ocr'>('transformer');
  const fileInputRef = useRef<HTMLInputElement>(null);

  if (!isOpen) return null;

  const handleFileSelect = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setIsLoading(true);
    setError('');
    setImagePreview('');

    try {
      if (fileType === 'json') {
        await handleJsonFile(file);
      } else {
        await handleImageFile(file);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : '导入失败');
    } finally {
      setIsLoading(false);
    }
  };

  const handleJsonFile = async (file: File): Promise<void> => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      
      reader.onload = (e) => {
        try {
          const content = e.target?.result as string;
          const data = JSON.parse(content);
          
          if (!data.data || !Array.isArray(data.data) || data.data.length !== 9) {
            throw new Error('JSON格式错误：需要包含9x9的data数组');
          }
          
          // 验证每个行是否为9个数字
          for (let i = 0; i < 9; i++) {
            if (!Array.isArray(data.data[i]) || data.data[i].length !== 9) {
              throw new Error('JSON格式错误：每行需要包含9个数字');
            }
            
            for (let j = 0; j < 9; j++) {
              const cell = data.data[i][j];
              if (typeof cell !== 'number' || cell < 0 || cell > 9) {
                throw new Error('JSON格式错误：每个格子必须是0-9的数字');
              }
            }
          }
          
          onImport(data.data);
          onClose();
          resolve();
        } catch (err) {
          reject(err);
        }
      };
      
      reader.onerror = () => reject(new Error('文件读取失败'));
      reader.readAsText(file);
    });
  };

  const handleImageFile = async (file: File): Promise<void> => {
    try {
      // 显示图片预览
      const reader = new FileReader();
      reader.onload = (e) => {
        setImagePreview(e.target?.result as string);
      };
      reader.readAsDataURL(file);

      console.log('🖼️ 开始图片识别...');
      console.log(`🔧 识别方法: ${recognitionMethod === 'transformer' ? 'Transformer模型' : 'OCR识别'}`);
      
      let result: RecognitionResult;
      
      if (recognitionMethod === 'transformer') {
        // 使用Transformer模型识别
        result = await quickRecognize(file);
      } else {
        // 使用OCR识别
        result = await quickRecognizeOCR(file);
      }

      if (result.success && result.board) {
        console.log('✅ 图片识别成功');
        console.log('📊 识别结果:', result.board);
        console.log(`🎯 置信度: ${(result.confidence || 0) * 100}%`);
        
        onImport(result.board);
        onClose();
      } else {
        throw new Error(result.error || '图片识别失败');
      }
      
    } catch (err) {
      console.error('❌ 图片识别失败:', err);
      throw err;
    }
  };

  const handleDrop = (event: React.DragEvent) => {
    event.preventDefault();
    const files = event.dataTransfer.files;
    if (files.length > 0) {
      const file = files[0];
      if (fileInputRef.current) {
        fileInputRef.current.files = files;
        handleFileSelect({ target: { files } } as any);
      }
    }
  };

  const handleDragOver = (event: React.DragEvent) => {
    event.preventDefault();
  };

  const triggerFileInput = () => {
    fileInputRef.current?.click();
  };

  const clearImagePreview = () => {
    setImagePreview('');
    setError('');
  };

  return (
    <div className="import-dialog-overlay" onClick={onClose}>
      <div className="import-dialog" onClick={(e) => e.stopPropagation()}>
        <div className="import-dialog-header">
          <h3>导入数独</h3>
          <button className="close-button" onClick={onClose}>×</button>
        </div>
        
        <div className="import-dialog-content">
          <div className="file-type-selector">
            <label>
              <input
                type="radio"
                value="json"
                checked={fileType === 'json'}
                onChange={(e) => {
                  setFileType(e.target.value as 'json' | 'image');
                  clearImagePreview();
                }}
              />
              JSON文件
            </label>
            <label>
              <input
                type="radio"
                value="image"
                checked={fileType === 'image'}
                onChange={(e) => {
                  setFileType(e.target.value as 'json' | 'image');
                  clearImagePreview();
                }}
              />
              图片文件
            </label>
          </div>

          {fileType === 'image' && (
            <div className="recognition-method-selector">
              <label>
                <input
                  type="radio"
                  value="transformer"
                  checked={recognitionMethod === 'transformer'}
                  onChange={(e) => setRecognitionMethod(e.target.value as 'transformer' | 'ocr')}
                />
                🧠 Transformer模型 (推荐)
              </label>
              <label>
                <input
                  type="radio"
                  value="ocr"
                  checked={recognitionMethod === 'ocr'}
                  onChange={(e) => setRecognitionMethod(e.target.value as 'transformer' | 'ocr')}
                />
                📝 OCR识别
              </label>
            </div>
          )}

          <div className="file-upload-area"
               onDrop={handleDrop}
               onDragOver={handleDragOver}
               onClick={triggerFileInput}>
            {imagePreview ? (
              <div className="image-preview-container">
                <img src={imagePreview} alt="数独图片预览" className="image-preview" />
                <div className="image-preview-overlay">
                  <button className="change-image-btn" onClick={(e) => {
                    e.stopPropagation();
                    clearImagePreview();
                  }}>
                    🔄 更换图片
                  </button>
                </div>
              </div>
            ) : (
              <>
                <div className="upload-icon">📁</div>
                <p>点击选择文件或拖拽文件到此处</p>
                <p className="file-format-hint">
                  {fileType === 'json' 
                    ? '支持JSON格式：{data: [9×9数组]}'
                    : '支持JPG、PNG等图片格式'
                  }
                </p>
              </>
            )}
            <input
              ref={fileInputRef}
              type="file"
              accept={fileType === 'json' ? '.json' : 'image/*'}
              onChange={handleFileSelect}
              style={{ display: 'none' }}
            />
          </div>

          {isLoading && (
            <div className="loading">
              <div className="spinner"></div>
              <p>
                {fileType === 'json' 
                  ? '正在解析JSON文件...'
                  : `正在使用${recognitionMethod === 'transformer' ? 'Transformer模型' : 'OCR'}识别图片中的数独...`
                }
              </p>
              {fileType === 'image' && (
                <div className="recognition-progress">
                  <div className="progress-bar">
                    <div className="progress-fill"></div>
                  </div>
                  <p className="progress-text">识别中，请稍候...</p>
                </div>
              )}
            </div>
          )}

          {error && (
            <div className="error-message">
              ❌ {error}
            </div>
          )}

          <div className="import-instructions">
            <h4>导入说明：</h4>
            <ul>
              {fileType === 'json' ? (
                <>
                  <li>JSON文件必须包含 <code>data</code> 字段</li>
                  <li><code>data</code> 必须是一个9×9的二维数组</li>
                  <li>数组中的数字：0表示空格，1-9表示对应数字</li>
                  <li>示例：<code>{"{data: [[1,2,3,...], [4,5,6,...], ...]}"}</code></li>
                </>
              ) : (
                <>
                  <li>支持JPG、PNG、GIF等常见图片格式</li>
                  <li>图片应包含清晰的数独网格</li>
                  <li><strong>🧠 Transformer模型</strong>：使用深度学习模型，识别准确率更高</li>
                  <li><strong>📝 OCR识别</strong>：使用传统OCR技术，适用于标准网格</li>
                  <li>建议使用高分辨率、对比度高的图片以获得最佳识别效果</li>
                </>
              )}
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ImportDialog;
