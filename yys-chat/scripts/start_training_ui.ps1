Write-Host "🚀 启动 yys-chat 训练界面" -ForegroundColor Green
Write-Host "=" * 50 -ForegroundColor Cyan

# 检查 Python 环境
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python 环境: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ 未找到 Python 环境" -ForegroundColor Red
    exit 1
}

# 检查依赖
Write-Host "📦 检查依赖..." -ForegroundColor Yellow
try {
    python -c "import gradio" 2>$null
    Write-Host "✅ Gradio 已安装" -ForegroundColor Green
} catch {
    Write-Host "❌ Gradio 未安装，正在安装..." -ForegroundColor Yellow
    pip install gradio
}

# 启动训练界面
Write-Host "🌐 启动训练界面..." -ForegroundColor Green
Write-Host "💡 界面将在浏览器中打开: http://localhost:7861" -ForegroundColor Cyan
Write-Host "🔄 按 Ctrl+C 停止服务" -ForegroundColor Yellow
Write-Host "=" * 50 -ForegroundColor Cyan

# 启动训练界面
python .\src\train\simple_train_ui.py
