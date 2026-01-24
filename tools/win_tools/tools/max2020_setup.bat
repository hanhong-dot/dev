@echo off
chcp 65001 >nul
setlocal EnableDelayedExpansion

:: ===== 查找 Max2020 安装路径 =====
set MAX_PATH=

for %%K in (
    "HKLM\SOFTWARE\Autodesk\3dsMax\22.0"
    "HKLM\SOFTWARE\WOW6432Node\Autodesk\3dsMax\22.0"
) do (
    for /f "tokens=2,*" %%A in ('reg query %%K /v Installdir 2^>nul') do (
        set "MAX_PATH=%%B"
    )
)

if not defined MAX_PATH (
    echo 未找到 3ds Max 2020
    exit /b 1
)

echo 找到 Max2020 安装路径： !MAX_PATH!

:: ===== INI 源文件路径 =====
set SRC_INI=Z:\dev\dcc\3dsmax2020\plugin.ini

if not exist "%SRC_INI%" (
    echo plugin.ini 不存在
    exit /b 1
)

:: ===== 复制到英文目录 =====
if exist "!MAX_PATH!\en-US" (
    robocopy "Z:\dev\dcc\3dsmax2020" "!MAX_PATH!\en-US" "plugin.ini" /R:0 /W:0 /NFL /NDL /NJH /NJS
    echo 已部署
)

:: ===== 复制到中文目录 =====
if exist "!MAX_PATH!\zh-CN" (
    robocopy "Z:\dev\dcc\3dsmax2020" "!MAX_PATH!\zh-CN" "plugin.ini" /R:0 /W:0 /NFL /NDL /NJH /NJS
    echo 已部署
)

echo Max2020 部署完成
pause
