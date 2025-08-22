Param(
    [string]$BaseModel = "Qwen/Qwen2-1.5B-Instruct",
    [string]$Dataset = ".\data\yys\train.jsonl",
    [string]$Role = "Mentor",
    [string]$OutputDir = ".\models\yys_mentor",
    [int]$Epochs = 3,
    [int]$BatchSize = 2,
    [double]$LR = 2e-4,
    [int]$CutoffLen = 2048,
    [string]$Quant = "none",
    [int]$MonitorInterval = 10
)

Write-Host "🚀 启动 yys-chat 训练 (带监控)" -ForegroundColor Green
Write-Host "=" * 60 -ForegroundColor Cyan

# 检查数据集
if (-not (Test-Path $Dataset)) {
    Write-Host "❌ 错误: 数据集文件不存在: $Dataset" -ForegroundColor Red
    exit 1
}

# 检查输出目录
if (Test-Path $OutputDir) {
    Write-Host "⚠️  警告: 输出目录已存在: $OutputDir" -ForegroundColor Yellow
    $response = Read-Host "是否继续？(y/N)"
    if ($response -ne "y" -and $response -ne "Y") {
        Write-Host "训练已取消" -ForegroundColor Yellow
        exit 0
    }
}

# 显示训练参数
Write-Host "📋 训练参数:" -ForegroundColor Cyan
Write-Host "  基础模型: $BaseModel" -ForegroundColor White
Write-Host "  数据集: $Dataset" -ForegroundColor White
Write-Host "  角色: $Role" -ForegroundColor White
Write-Host "  输出目录: $OutputDir" -ForegroundColor White
Write-Host "  训练轮数: $Epochs" -ForegroundColor White
Write-Host "  批次大小: $BatchSize" -ForegroundColor White
Write-Host "  学习率: $LR" -ForegroundColor White
Write-Host "  最大长度: $CutoffLen" -ForegroundColor White
Write-Host "  量化: $Quant" -ForegroundColor White
Write-Host "  监控间隔: ${MonitorInterval}秒" -ForegroundColor White

Write-Host "=" * 60 -ForegroundColor Cyan

# 启动训练
Write-Host "🎯 开始训练..." -ForegroundColor Green
Write-Host "💡 提示: 训练过程中会显示详细的日志和资源监控" -ForegroundColor Yellow
Write-Host "📁 日志文件将保存在: $OutputDir\training.log" -ForegroundColor Cyan
Write-Host "📊 监控日志将保存在: $OutputDir\monitor.log" -ForegroundColor Cyan

# 构建训练命令
$trainCmd = @(
    "python", ".\src\train\train_lora.py",
    "--base_model", $BaseModel,
    "--dataset", $Dataset,
    "--role", $Role,
    "--output_dir", $OutputDir,
    "--epochs", $Epochs,
    "--batch_size", $BatchSize,
    "--lr", $LR,
    "--cutoff_len", $CutoffLen,
    "--quant", $Quant
)

Write-Host "🔧 执行命令: $($trainCmd -join ' ')" -ForegroundColor Gray
Write-Host "=" * 60 -ForegroundColor Cyan

# 执行训练
try {
    & $trainCmd[0] $trainCmd[1..($trainCmd.Length-1)]
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ 训练完成!" -ForegroundColor Green
        Write-Host "📁 模型保存在: $OutputDir" -ForegroundColor Cyan
        
        # 显示输出目录内容
        if (Test-Path $OutputDir) {
            Write-Host "📋 输出文件:" -ForegroundColor Cyan
            Get-ChildItem $OutputDir -Recurse | ForEach-Object {
                $size = if ($_.PSIsContainer) { "<DIR>" } else { "$([math]::Round($_.Length/1MB, 2)) MB" }
                Write-Host "  $($_.Name): $size" -ForegroundColor White
            }
        }
    } else {
        Write-Host "❌ 训练失败，退出码: $LASTEXITCODE" -ForegroundColor Red
        exit $LASTEXITCODE
    }
} catch {
    Write-Host "❌ 训练过程中出现错误: $_" -ForegroundColor Red
    exit 1
}

Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host "🎉 训练脚本执行完成!" -ForegroundColor Green
