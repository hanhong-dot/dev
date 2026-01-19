@echo off
setlocal EnableDelayedExpansion

:: ================== 管理员权限 ==================
net session >nul 2>&1
if %errorlevel% NEQ 0 (
    echo Requesting admin privilege...
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

:: ================== 路径配置 ==================

set SRC=Z:\software\dcc\3dmax2020
set SETUP=%SRC%\Img\Setup.exe
set INI=%SRC%\Img\3dmax2020.ini
set LOG=%TEMP%\Max2020_install.log


echo ======================================
echo Start Install 3ds Max 2020
echo ======================================

timeout /t 3 >nul

:: ================== 路径检查 ==================

if not exist "%SETUP%" (
    echo ERROR: Setup.exe not found
    pause
    exit /b 1
)

if not exist "%INI%" (
    echo ERROR: ini file not found
    pause
    exit /b 1
)

:: ================== 执行安装 ==================
cd /d "%SRC%"

"%SETUP%"  /Q /I "%INI%"

set RET=%ERRORLEVEL%

echo.
echo ======================================
echo Install Finished
echo Return Code: %RET%
echo ======================================

if "%RET%"=="0" (
    echo Install Success!
) else (
    echo Install Failed! Error Code: %RET%
)


pause
