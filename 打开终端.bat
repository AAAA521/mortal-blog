@echo off
cd /d "%~dp0"
title Mortal Blog - 终端

rem 本机未安装系统版 Node.js，改用内置运行时
set "NODE_DIR=D:\node-js"
if exist "%NODE_DIR%\npm.cmd" set "PATH=%NODE_DIR%;%PATH%"

echo ============================================
echo   Mortal Blog  项目终端
echo ============================================
echo.
echo 当前目录: %CD%
echo.
echo 版本检查:
node -v 2>nul
npm -v 2>nul
echo.
echo --------------------------------------------
echo 常用命令:
echo   npm run dev    启动本地预览   localhost:4321
echo   npm run build  构建静态站点   输出到 dist\
echo   dir src\content\posts   查看文章文件
echo --------------------------------------------
echo.
echo 现在可以在这里输入命令了。关闭窗口即退出。
echo.

cmd /k
