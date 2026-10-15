@echo off
cd /d "%~dp0"
title Mortal Blog - Build

rem Node.js 24.22.0 安装在 D:\node-js（如果换了位置，改下面这一行）
set "NODE_DIR=D:\node-js"
if exist "%NODE_DIR%\npm.cmd" set "PATH=%NODE_DIR%;%PATH%"

echo ============================================
echo   Mortal Blog  构建静态站点
echo ============================================
echo.
echo 项目目录: %CD%
echo.

echo [1/2] 正在构建...
call npm run build

if errorlevel 1 (
    echo.
    echo [错误] 构建失败，请看上面的报错信息
    pause
    exit /b 1
)

echo.
echo [2/2] 构建完成，产物在 dist\ 目录
echo       可以直接把 dist\ 里的内容上传到服务器 / GitHub Pages
echo.
echo ============================================
echo.
echo 按任意键在本地预览构建结果 (localhost:4330)...
pause >nul

call npm run preview -- --port 4330

pause
