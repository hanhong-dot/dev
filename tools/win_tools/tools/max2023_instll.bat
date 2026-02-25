@echo off
chcp 65001 >nul
setlocal
echo ======================================
echo 3ds Max 2023 Install Start
echo please wait...
echo ======================================
cd /d Z:\software\dcc\3dsmax2023
Setup.exe -i install -q -language=CHS

echo ======================================
echo 3ds Max 2023 Install Finished
echo ======================================

robocopy "Z:\dev\dcc\3dsmax2023" "C:\Program Files\Autodesk\3ds Max 2023" 3dsmax.exe /R:0 /W:0 /NFL /NDL

echo Crack file copy done

robocopy "Z:\dev\dcc\3dsmax2023" "C:\Program Files\Autodesk\3ds Max 2023\en-US" plugin.ini /R:0 /W:0 /NFL /NDL
robocopy "Z:\dev\dcc\3dsmax2023" "C:\Program Files\Autodesk\3ds Max 2023\zh-CN" plugin.ini /R:0 /W:0 /NFL /NDL

echo Plugin config done

setx ADSK_3DSMAX_PLUGINS_ADDON_DIR Z:\dev\tools\max2023\PlugIns



echo ======================================
echo 3ds Max 2023 安装及配置完成！
echo ======================================

exit /b 0
pause