# 数独游戏启动脚本
Write-Host "正在启动数独游戏..." -ForegroundColor Green

# 检查是否已安装依赖
if (-not (Test-Path "node_modules")) {
    Write-Host "正在安装依赖..." -ForegroundColor Yellow
    npm install
}

# 启动开发服务器
Write-Host "启动开发服务器..." -ForegroundColor Green
npm start
