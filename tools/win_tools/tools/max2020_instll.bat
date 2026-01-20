@echo off
chcp 936 >nul
setlocal EnableDelayedExpansion

:: ================== 管理员权限 ==================
net session >nul 2>&1
if %errorlevel% NEQ 0 (
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

set ROOT=Z:\software\dcc\install\3dsmax2020
set IMG=%ROOT%\Img

pushd "%IMG%"
echo ===============================
echo Install Max 2020 Start
echo ===============================

echo ===============================
echo Install VC Runtime
echo ===============================

:: VC++ 2010
"%IMG%\3rdParty\x86\VCRedist\2010SP1\vcredist_x86.exe" /q /norestart
"%IMG%\3rdParty\x64\VCRedist\2010SP1\vcredist_x64.exe" /q /norestart

:: VC++ 2012
"%IMG%\3rdParty\x86\VCRedist\2012UPD4\vcredist_x86.exe" /install /quiet /norestart
"%IMG%\3rdParty\x64\VCRedist\2012UPD4\vcredist_x64.exe" /install /quiet /norestart

:: VC++ 2013
"%IMG%\3rdParty\x86\VCRedist\2013\vcredist_x86.exe" /q /norestart
"%IMG%\3rdParty\x64\VCRedist\2013\vcredist_x64.exe" /q /norestart

:: VC++ 2015-2017
"%IMG%\3rdParty\x86\VCRedist\2017\vc_redist.x86.exe" /install /quiet /norestart
"%IMG%\3rdParty\x64\VCRedist\2017\vc_redist.x64.exe" /install /quiet /norestart

:: UCRT
"%IMG%\3rdParty\ucrt\AdUcrtInstaller.exe" /S

:: .NET 4.7
"%IMG%\3rdParty\NET\47\wcu\dotNetFramework\dotnetfx47_full_x86_x64.exe" /q /norestart

echo ===============================
echo Install Autodesk Licensing
echo ===============================

"%IMG%\x86\AdskLicensing\AdskLicensing-installer.exe" --mode unattended --unattendedmodeui none

timeout /t 5 >nul

echo ===============================
echo Install Material Library
echo ===============================

msiexec /i "%IMG%\Content\ADSKMaterials\2020\CM\MaterialLibrary2020.msi" /qn
msiexec /i "%IMG%\Content\ADSKMaterials\2020\ILB\BaseImageLibrary2020.msi" /qn
msiexec /i "%IMG%\Content\ADSKMaterials\2020\ILM\MediumImageLibrary2020.msi" /qn

echo ===============================
echo Install 3ds Max 2020 Core
echo ===============================

msiexec /i "%IMG%\x64\max\3dsMax.msi" TRANSFORMS="%IMG%\x64\max\3dsMax-3dsmax2020.mst" /qn

echo ===============================
echo Install Plugins
echo ===============================

msiexec /i "%IMG%\x64\MAXtoA\ArnoldPlug.msi" /qn
msiexec /i "%IMG%\x64\MENTALRAYPLUG\MentalrayPlugins2020.msi" /qn
msiexec /i "%IMG%\x64\Inventor_Server\Inventor_Engine_Max.msi" /qn
msiexec /i "%IMG%\x86\Comp\CV\CivilView2020.msi" /qn

echo ===============================
echo Install max2020 Finished
echo ===============================

popd
pause
