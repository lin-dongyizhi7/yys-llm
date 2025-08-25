import React, { useState, useRef } from 'react';
import './ImportDialog.css';
import { quickRecognize, RecognitionResult } from '../../utils/imageRecognition';

interface ImportDialogProps {
  isOpen: boolean;
  onClose: () => void;
  onImport: (board: number[][]) => void;
}

const ImportDialog: React.FC<ImportDialogProps> = ({ isOpen, onClose, onImport }) => {
  const [fileType, setFileType] = useState<'json' | 'image'>('json');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string>('');
  const fileInputRef = useRef<HTMLInputElement>(null);

  if (!isOpen) return null;

  const handleFileSelect = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setIsLoading(true);
    setError('');

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
      console.log('🖼️ 开始图片识别...');
      
      // 使用图片识别功能
      const result: RecognitionResult = await quickRecognize(file);
      
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
                onChange={(e) => setFileType(e.target.value as 'json' | 'image')}
              />
              JSON文件
            </label>
            <label>
              <input
                type="radio"
                value="image"
                checked={fileType === 'image'}
                onChange={(e) => setFileType(e.target.value as 'json' | 'image')}
              />
              图片文件
            </label>
          </div>

          <div className="file-upload-area"
               onDrop={handleDrop}
               onDragOver={handleDragOver}
               onClick={triggerFileInput}>
            <div className="upload-icon">📁</div>
            <p>点击选择文件或拖拽文件到此处</p>
            <p className="file-format-hint">
              {fileType === 'json' 
                ? '支持JSON格式：{data: [9×9数组]}'
                : '支持JPG、PNG等图片格式'
              }
            </p>
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
                  : '正在识别图片中的数独...'
                }
              </p>
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
                  <li>系统将自动识别数字并转换为数独数据</li>
                  <li>建议使用高分辨率、对比度高的图片</li>
                  <li>识别准确率取决于图片质量和清晰度</li>
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
