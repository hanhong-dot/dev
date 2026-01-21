@echo off
chcp 65001 >nul
setlocal EnableDelayedExpansion

rem If this file is saved as UTF-8 with BOM, chcp 65001 will display Chinese correctly.

:: ================== 管理员权限 ==================
net session >nul 2>&1
if %errorlevel% NEQ 0 (
    echo Requesting admin privilege...
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)
echo ======================================
echo 3ds Max 2020 Install Start
echo ======================================
cd /d Z:\dev\dcc\3dsmax2020\Img
:: ================== 安装主程序 ==================
Z:\dev\dcc\3dsmax2020\Img\Setup.exe  /W /q /I  Z:\dev\dcc\3dsmax2020\Img\3dsmax2020.ini   /language zh-cn

echo Return Code = %ERRORLEVEL%
if %ERRORLEVEL% NEQ 0 (
    echo 3ds Max 2020 安装失败，错误码 %ERRORLEVEL%
    pause
    exit /b %ERRORLEVEL%
)


echo ======================================
echo 3ds Max 2020 Install Finished
echo ======================================

robocopy "Z:\dev\dcc\3dsmax2020" "D:\Autodesk\3ds Max 2020" 3dsmax.exe /R:0 /W:0 /NFL /NDL
echo 3ds Max 2020 破解文件复制完成
:: ================== 设置环境变量 ==================

robocopy "Z:\dev\dcc\3dsmax2020" "D:\Autodesk\3ds Max 2020\en-US" plugin.ini /R:0 /W:0 /NFL /NDL
robocopy "Z:\dev\dcc\3dsmax2020" "D:\Autodesk\3ds Max 2020\zh-CN" plugin.ini /R:0 /W:0 /NFL /NDL
echo 3ds Max 2020 插件配置文件设置完成
echo ======================================
echo 3ds Max 2020 安装及配置完成！
echo ======================================
pause
