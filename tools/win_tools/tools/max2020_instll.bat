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

set SRC=D:\3dmax2020
set SETUP=%SRC%\Img\Setup.exe
set INI=%SRC%\Img\3dmax2020.ini
set LOG=%TEMP%\Max2020_install.log
set MAX_EXE=C:\Program Files\Autodesk\3ds Max 2020\3dsmax.exe

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

"%SETUP%" /W /Q /I "%INI%" /language zh-cn /log "%LOG%"

set RET=%ERRORLEVEL%

echo.
echo ======================================
echo Install Finished
echo Return Code: %RET%
echo Log: %LOG%
echo ======================================

if "%RET%"=="0" (
    echo Install Success!
) else (
    echo Install Failed! Error Code: %RET%
)

if exist "%MAX_EXE%" (
    echo 3ds Max EXE Found!
) else (
    echo 3ds Max EXE NOT Found!
)

pause
