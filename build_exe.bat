@echo off
chcp 65001 >nul
title Build Vocabulary Review EXE

echo ============================================
echo   Vocabulary Review - 打包独立 EXE
echo ============================================
echo.

:: Go to project root
cd /d "%~dp0"

:: Check PyInstaller
pip show pyinstaller >nul 2>&1
if %errorlevel% neq 0 (
    echo [1/4] 安装 PyInstaller...
    pip install pyinstaller -q
) else (
    echo [1/4] PyInstaller 已安装
)

:: Rebuild frontend
echo [2/4] 构建前端...
cd /d "%~dp0frontend"
if not exist node_modules (
    call npm install >nul 2>&1
)
call npm run build >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 前端构建失败
    pause
    exit /b 1
)
echo     前端构建完成

:: Install backend deps
echo [3/4] 安装后端依赖...
cd /d "%~dp0backend"
pip install -r requirements.txt -q

:: Build EXE
echo [4/4] 打包 EXE (需等待 1-3 分钟)...
echo.

cd /d "%~dp0"

pyinstaller --onefile ^
    --name "VocabularyReview" ^
    --distpath "dist_exe" ^
    --add-data "frontend\dist;frontend\dist" ^
    --add-data "backend\audio;audio" ^
    --add-data "backend\images;images" ^
    --hidden-import "uvicorn.logging" ^
    --hidden-import "uvicorn.loops.auto" ^
    --hidden-import "uvicorn.protocols.http.auto" ^
    --hidden-import "sqlalchemy" ^
    --hidden-import "routes" ^
    --hidden-import "routes.words" ^
    --hidden-import "routes.review" ^
    --hidden-import "routes.stats" ^
    --hidden-import "routes.media" ^
    --hidden-import "services" ^
    --hidden-import "services.audio" ^
    --hidden-import "services.image" ^
    --hidden-import "services.dictionary" ^
    --hidden-import "edge_tts" ^
    --collect-all "edge_tts" ^
    "backend\main.py"

if %errorlevel% == 0 (
    echo.
    echo ============================================
    echo   打包成功！
    echo   输出: %~dp0dist_exe\VocabularyReview.exe
    echo   双击即可运行,访问 http://localhost:8004
    echo ============================================
) else (
    echo [错误] 打包失败
)

pause
