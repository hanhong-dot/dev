@echo off
chcp 65001 >nul
setlocal
:: ===== 切换工作目录（EXE 必须）=====
echo ======================================
echo 3ds Max 2020 Install Start
echo ======================================
cd /d Z:\dev\dcc\3dsmax2020\Img
Setup.exe /I 3dsmax2020.ini /language zh-cn

echo ======================================
echo 3ds Max 2020 Install Finished
echo ======================================

robocopy "Z:\dev\dcc\3dsmax2020" "D:\Autodesk\3ds Max 2020" 3dsmax.exe /R:0 /W:0 /NFL /NDL

echo Crack file copy done

robocopy "Z:\dev\dcc\3dsmax2020" "D:\Autodesk\3ds Max 2020\en-US" plugin.ini /R:0 /W:0 /NFL /NDL
robocopy "Z:\dev\dcc\3dsmax2020" "D:\Autodesk\3ds Max 2020\zh-CN" plugin.ini /R:0 /W:0 /NFL /NDL

echo Plugin config done

echo ======================================
echo 3ds Max 2020 安装及配置完成！
echo ======================================

exit /b 0
