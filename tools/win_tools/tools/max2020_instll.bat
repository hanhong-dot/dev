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
cd /d "Z:\software\dcc\install\3dsmax2020"
:: ================== 安装主程序 ==================
"Z:\software\dcc\install\3dsmax2020\Img\Setup.exe" /W /q /I "Z:\software\dcc\install\3dsmax2020\Img\3dsmax2020.ini" /language zh-cn



:: ================== 判断安装完成 ==================
rem 安装完成后，运行授权工具
rem 判断安装是否成功


echo ======================================
echo 3ds Max 2020 Install Finished
echo ======================================
start "" /wait "Z:\software\dcc\AutodeskLic\AutodeskLic.exe" /q
echo Return Code = %ERRORLEVEL%

if %ERRORLEVEL%==0 (
    echo 授权工具执行成功
) else (
    echo 授权工具执行失败
)

pause
