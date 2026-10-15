@echo off
cd /d "%~dp0"
title Mortal Blog - Dev Server

rem Node.js 24.22.0 安装在 D:\node-js（如果换了位置，改下面这一行）
set "NODE_DIR=D:\node-js"
if exist "%NODE_DIR%\npm.cmd" set "PATH=%NODE_DIR%;%PATH%"

echo ============================================
echo   Mortal Blog  本地预览
echo ============================================
echo.
echo 项目目录: %CD%
echo.

where npm >nul 2>&1
if errorlevel 1 (
    echo [X] 找不到 npm，无法启动。
    echo     请先安装 Node.js，或让我帮你配置环境。
    echo.
    pause
    exit /b 1
)

if not exist "node_modules" (
    echo [1/2] 首次运行，正在安装依赖，请稍候...
    call npm install
) else (
    echo [1/2] 依赖已就绪，跳过安装
)

echo.
echo [2/2] 启动开发服务器...
echo       浏览器打开 http://localhost:4321/mortal-blog/
echo       改文章后会自动刷新，不用重启
echo       要停止：直接关掉这个窗口，或按 Ctrl+C
echo.
echo ============================================
echo.

call npm run dev

pause
