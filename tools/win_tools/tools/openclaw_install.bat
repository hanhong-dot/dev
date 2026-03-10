@echo off
chcp 65001 >nul
setlocal
echo ======================================
echo OpenClaw Install Start
echo please wait...
echo ======================================

if not exist "Z:\software\tools\openclaw" (
    echo ERROR: 无法访问网络路径 Z:\software\tools\openclaw
    echo 请确认 Z 盘已挂载并可访问。
    pause
    exit /b 1
)

if not exist "Z:\software\tools\openclaw\OpenClaw_Setup.exe" (
    echo ERROR: 未找到安装程序 OpenClaw_Setup.exe
    pause
    exit /b 1
)

cd /d Z:\software\tools\openclaw
OpenClaw_Setup.exe /S
if %ERRORLEVEL% neq 0 (
    echo ERROR: OpenClaw 安装失败，错误代码 %ERRORLEVEL%
    pause
    exit /b %ERRORLEVEL%
)

echo ======================================
echo OpenClaw Install Finished
echo ======================================

echo ======================================
echo OpenClaw 下载安装完成！
echo ======================================

pause
