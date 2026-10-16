@echo off
cd /d "%~dp0"
title Mortal Blog - Deploy

rem ============================================================
rem  本机环境说明（重要）
rem  ----------------------------------------------------------
rem  1. Node.js 24.22.0 安装在 D:\node-js
rem  2. 本机【没有】独立安装 Git，只有 WorkBuddy 自带的便携版。
rem     下面这两行就是把它接进来；以后若自己装了正式版 Git，
rem     把这两行删掉即可。
rem ============================================================
set "GITCMD_DIR=D:\workbuddy\resources\vendor\PortableGit\cmd"
if exist "%GITCMD_DIR%\git.exe" set "PATH=%GITCMD_DIR%;%PATH%"

set "NODE_DIR=D:\node-js"
if exist "%NODE_DIR%\node.exe" set "PATH=%NODE_DIR%;%PATH%"

rem 清掉可能继承到的 HTTP 代理环境变量
rem （git 若走代理会报: CONNECT tunnel failed, response 502）
set "http_proxy="
set "https_proxy="
set "HTTP_PROXY="
set "HTTPS_PROXY="
set "ALL_PROXY="
set "all_proxy="

echo ============================================
echo   Mortal Blog  提交并推送到 GitHub
echo ============================================
echo.
echo 项目目录: %CD%
echo.

where git >nul 2>&1
if errorlevel 1 goto no_git

echo 正在检查到 github.com 的连接...
git ls-remote https://github.com/AAAA521/mortal-blog.git >nul 2>&1
if errorlevel 1 goto no_net
echo [OK] 已连上 GitHub
echo.

echo [1/5] 检查 git 身份
git config user.email >nul 2>&1
if not errorlevel 1 goto hasid

echo.
echo   第一次推送，先登记一下身份（只是提交记录里的署名，随便填）
echo.
set "GITNAME="
set "GITMAIL="
set /p "GITNAME=你的名字: "
set /p "GITMAIL=你的邮箱: "
if "%GITNAME%"=="" set "GITNAME=AAAA521"
if "%GITMAIL%"=="" set "GITMAIL=AAAA521@users.noreply.github.com"
git config --global user.name "%GITNAME%"
git config --global user.email "%GITMAIL%"
echo [OK] 身份已登记
echo.
goto step2

:hasid
echo [OK] git 身份已设置，跳过
echo.

:step2
echo [2/5] 检查 git 仓库
if exist ".git" goto hasrepo
git init
echo [OK] 已初始化
echo.
goto step3

:hasrepo
echo [OK] 仓库已存在，跳过
echo.

:step3
echo [3/5] 暂存所有改动
git add -A
echo [OK] 完成
echo.

echo [4/5] 提交
git commit -m "update blog content"
if errorlevel 1 echo [i] 没有新改动，跳过提交
echo.

echo [5/5] 推送
git remote get-url origin >nul 2>&1
if not errorlevel 1 goto dopush

echo.
echo   还没有绑定远程仓库。
echo   默认地址是 https://github.com/AAAA521/mortal-blog.git
echo.
set "REPO="
set /p "REPO=直接回车用默认地址，或粘贴新地址: "
if "%REPO%"=="" set "REPO=https://github.com/AAAA521/mortal-blog.git"
git remote add origin %REPO%
git branch -M main
echo.

:dopush
echo 正在推送... 如果弹出浏览器窗口，登录你的 GitHub 账号即可
echo.
git push -u origin main

if errorlevel 1 goto failed

echo.
echo ============================================
echo   推送成功！
echo ============================================
echo.
echo 接下来:
echo   1. 打开仓库页面 https://github.com/AAAA521/mortal-blog
echo   2. 点 Actions 标签，等出现绿色对勾（约 1 分钟）
echo   3. 只有第一次需要：Settings - Pages - Source 选 GitHub Actions
echo   4. 完成后访问 https://AAAA521.github.io/mortal-blog/
echo.
pause
exit /b 0

rem ============================================================

:no_git
echo.
echo ============================================
echo   [X] 找不到 git 命令
echo ============================================
echo.
echo 脚本尝试过的路径:
echo   %GITCMD_DIR%\git.exe
echo.
echo 如果这个文件不存在，说明 WorkBuddy 更新过目录结构。
echo 解决办法：自己装一个 Git for Windows（https://git-scm.com/），
echo 装完把这个窗口关掉重开，再双击本脚本即可。
echo.
pause
exit /b 1

:no_net
echo.
echo ============================================
echo   [X] 连不上 GitHub
echo ============================================
echo.
echo 请检查:
echo   1. 网络是否正常
echo   2. Steam++（Watt Toolkit）的 GitHub 加速是否开着
echo      —— 你的 hosts 文件把 github.com 指向了 127.0.0.1，
echo         必须让 Steam++ 保持运行，否则连不上。
echo.
pause
exit /b 1

:failed
echo.
echo ============================================
echo   推送失败，请看上面的红色报错
echo ============================================
echo.
echo 常见原因与对策:
echo   1. 登录窗口被浏览器拦截  -^> 允许弹窗后重试
echo   2. 认证失败              -^> 见 README 的「用 Token 推送」一节
echo   3. 仓库地址打错了
echo.
pause
exit /b 1
