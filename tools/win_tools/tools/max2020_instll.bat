@echo off
setlocal

REM ================== 路径配置 ==================

set MaxInstallPath=Z:\dev\dcc\max2020

echo ======================================
echo Start Install, Please Wait...
echo ======================================



REM 等待5秒
timeout /t 5 /nobreak >nul

cd /d "%MaxInstallPath%"

REM 执行安装（等待完成）
"%MaxInstallPath%\Img\Setup.exe" /W /q /I "%MaxInstallPath%\Img\3dsmax2020.ini" /language zh-cn

REM 获取返回码
set RET=%ERRORLEVEL%
echo.
echo ======================================
echo Install Finished
echo Return Code: %RET%
echo ======================================

REM 判断结果
if "%RET%"=="0" (
    echo Install Success!
) else (
    echo Install Failed! Error Code: %RET%
)
REM 判断程序是否存在
if exist "%MAX_EXE%" (
    echo 3ds Max EXE Found!
) else (
    echo 3ds Max EXE NOT Found!
)

pause
