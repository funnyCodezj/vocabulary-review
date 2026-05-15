@echo off
chcp 65001 >nul
title Vocabulary Review

echo ============================================
echo   Vocabulary Review - 一键启动
echo ============================================
echo.

cd /d "%~dp0"

:: Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未检测到 Python,请先安装 Python 3.10+
    pause
    exit /b 1
)

:: Install backend dependencies
echo [1/3] 安装后端依赖...
pip install -r backend\requirements.txt -q
if %errorlevel% neq 0 (
    echo [错误] 依赖安装失败
    pause
    exit /b 1
)

:: Rebuild frontend if needed
echo [2/3] 构建前端...
if not exist frontend\dist\index.html (
    if exist frontend\node_modules (
        cd frontend
        call npm run build >nul 2>&1
        cd ..
    ) else (
        echo [信息] 未检测到 node_modules,跳过前端构建
        echo [信息] 如需构建前端,请执行: cd frontend ^&^& npm install ^&^& npm run build
    )
) else (
    echo     前端已构建
)

:: Start service
echo [3/3] 启动服务...
echo.
echo ============================================
echo   服务启动中...
echo   访问地址: http://localhost:8004
echo   按 Ctrl+C 停止
echo ============================================
echo.

cd backend
python -m uvicorn app:app --host 0.0.0.0 --port 8004 --reload

pause
