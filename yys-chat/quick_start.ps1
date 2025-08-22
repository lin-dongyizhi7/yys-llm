Write-Host "🎯 yys-chat 快速启动" -ForegroundColor Green
Write-Host "=" * 50 -ForegroundColor Cyan

Write-Host "请选择要启动的功能:" -ForegroundColor White
Write-Host "1. 🚀 简单训练界面" -ForegroundColor Cyan
Write-Host "2. 🚀 高级训练界面" -ForegroundColor Cyan
Write-Host "3. 📊 训练演示" -ForegroundColor Cyan
Write-Host "4. 🔧 安装依赖" -ForegroundColor Yellow
Write-Host "5. 📚 查看帮助" -ForegroundColor Yellow
Write-Host "6. ❌ 退出" -ForegroundColor Red

Write-Host "=" * 50 -ForegroundColor Cyan

$choice = Read-Host "请输入选择 (1-6)"

switch ($choice) {
    "1" {
        Write-Host "🚀 启动简单训练界面..." -ForegroundColor Green
        .\scripts\start_training_ui.ps1
    }
    "2" {
        Write-Host "🚀 启动高级训练界面..." -ForegroundColor Green
        .\scripts\start_advanced_ui.ps1
    }
    "3" {
        Write-Host "📊 启动训练演示..." -ForegroundColor Green
        python .\demo_training_ui.py
    }
    "4" {
        Write-Host "🔧 安装依赖..." -ForegroundColor Green
        pip install -r requirements.txt
        Write-Host "✅ 依赖安装完成" -ForegroundColor Green
    }
    "5" {
        Write-Host "📚 帮助信息:" -ForegroundColor Green
        Write-Host "=" * 50 -ForegroundColor Cyan
        Write-Host "🚀 训练界面:" -ForegroundColor White
        Write-Host "  - 简单界面: 基础训练功能" -ForegroundColor Gray
        Write-Host "  - 高级界面: 完整功能 + 实时监控" -ForegroundColor Gray
        Write-Host ""
        Write-Host "📖 文档:" -ForegroundColor White
        Write-Host "  - 训练界面: TRAINING_UI_README.md" -ForegroundColor Gray
        Write-Host "  - 日志功能: LOGGING_README.md" -ForegroundColor Gray
        Write-Host "  - 项目说明: README.md" -ForegroundColor Gray
        Write-Host ""
        Write-Host "🔧 脚本:" -ForegroundColor White
        Write-Host "  - 启动界面: scripts\start_*.ps1" -ForegroundColor Gray
        Write-Host "  - 训练脚本: scripts\train_*.ps1" -ForegroundColor Gray
        Write-Host ""
        Write-Host "💡 快速开始:" -ForegroundColor White
        Write-Host "  1. 选择 '4' 安装依赖" -ForegroundColor Gray
        Write-Host "  2. 选择 '1' 或 '2' 启动训练界面" -ForegroundColor Gray
        Write-Host "  3. 在浏览器中配置参数并开始训练" -ForegroundColor Gray
        Write-Host "=" * 50 -ForegroundColor Cyan
    }
    "6" {
        Write-Host "👋 再见！" -ForegroundColor Green
        exit 0
    }
    default {
        Write-Host "❌ 无效选择，请输入 1-6" -ForegroundColor Red
    }
}

Write-Host "=" * 50 -ForegroundColor Cyan
Write-Host "按任意键继续..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
