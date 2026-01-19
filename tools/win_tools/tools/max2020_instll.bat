@echo off
setlocal EnableDelayedExpansion

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

:== Microsoft Visual C++ 2010 SP1 Redistributable (x86)
Z:\software\dcc\3dsmax2020\Img\3rdParty\x86\VCRedist\2010SP1\vcredist_x86.exe /q /norestart

:== Microsoft Visual C++ 2010 SP1 Redistributable (x64)
Z:\software\dcc\3dsmax2020\Img\3rdParty\x64\VCRedist\2010SP1\vcredist_x64.exe /q /norestart

:== Microsoft Visual C++ 2012 Redistributable (x86)
Z:\software\dcc\3dsmax2020\Img\3rdParty\x86\VCRedist\2012UPD4\vcredist_x86.exe /install /quiet /norestart

:== Microsoft Visual C++ 2012 Redistributable (x64)
Z:\software\dcc\3dsmax2020\Img\3rdParty\x64\VCRedist\2012UPD4\vcredist_x64.exe /install /quiet /norestart

:== Microsoft Visual C++ 2013 Redistributable (x86)
Z:\software\dcc\3dsmax2020\Img\3rdParty\x86\VCRedist\2013\vcredist_x86.exe /q /norestart /l C:\Users\linhuan\AppData\Local\Temp\vcredist_x86_2013.log

:== Microsoft Visual C++ 2013 Redistributable (x64)
Z:\software\dcc\3dsmax2020\Img\3rdParty\x64\VCRedist\2013\vcredist_x64.exe /q /norestart /l C:\Users\linhuan\AppData\Local\Temp\vcredist_x64_2013.log

:== Universal C Runtime (KB3118401)
Z:\software\dcc\3dsmax2020\Img\3rdParty\ucrt\AdUcrtInstaller.exe /S

:== Microsoft Visual C++ 2015 Redistributable (x86)
Z:\software\dcc\3dsmax2020\Img\3rdParty\x86\VCRedist\2015UPD3\vcredist_x86.exe /q /norestart

:== Microsoft Visual C++ 2015 Redistributable (x64)
Z:\software\dcc\3dsmax2020\Img\3rdParty\x64\VCRedist\2015UPD3\vcredist_x64.exe /q /norestart

:== Microsoft Visual C++ 2017 Redistributable (x86)
Z:\software\dcc\3dsmax2020\Img\3rdParty\x86\VCRedist\2017\vc_redist.x86.exe /install /quiet /norestart

:== Microsoft Visual C++ 2017 Redistributable (x64)
Z:\software\dcc\3dsmax2020\Img\3rdParty\x64\VCRedist\2017\vc_redist.x64.exe /install /quiet /norestart

:== .NET Framework Runtime 4.7
Z:\software\dcc\3dsmax2020\Img\3rdParty\NET\47\wcu\dotNetFramework\dotnetfx47_full_x86_x64.exe /q /norestart


:===================================
:: Autodesk 产品
:===================================

:== Autodesk Material Library 2020
Z:\software\dcc\3dsmax2020\Img\Content\ADSKMaterials\2020\CM\MaterialLibrary2020.msi ADSK_EULA_STATUS=#1 MUILANG=zh-cn ADSK_SOURCE_ROOT="Z:\software\dcc\3dsmax2020\Img\" REBOOT=ReallySuppress ADSK_SETUP_EXE=1 /q

:== Autodesk Material Library Base Resolution Image Library 2020
Z:\software\dcc\3dsmax2020\Img\Content\ADSKMaterials\2020\ILB\BaseImageLibrary2020.msi ADSK_EULA_STATUS=#1 MUILANG=zh-cn ADSK_SOURCE_ROOT="Z:\software\dcc\3dsmax2020\Img\" REBOOT=ReallySuppress ADSK_SETUP_EXE=1 /q

:== Autodesk Material Library Medium Resolution Image Library 2020
Z:\software\dcc\3dsmax2020\Img\Content\ADSKMaterials\2020\ILM\MediumImageLibrary2020.msi ADSK_EULA_STATUS=#1 MUILANG=zh-cn ADSK_SOURCE_ROOT="Z:\software\dcc\3dsmax2020\Img\" REBOOT=ReallySuppress ADSK_SETUP_EXE=1 /q

:== Autodesk Genuine Service
"Z:\software\dcc\3dsmax2020\Img\x64\AGS\Autodesk Genuine Service.msi" ADSK_EULA_STATUS=#1 MUILANG=zh-cn ADSK_SOURCE_ROOT="Z:\software\dcc\3dsmax2020\Img\" REBOOT=ReallySuppress ADSK_SETUP_EXE=1 /q

:== Autodesk Licensing
Z:\software\dcc\3dsmax2020\Img\x86\AdskLicensing\AdskLicensing-installer.exe --mode unattended --unattendedmodeui none

:== Autodesk 3ds Max 2020
Z:\software\dcc\3dsmax2020\Img\x64\max\3dsMax.msi TRANSFORMS="Z:\software\dcc\3dsmax2020\Img\x64\max\3dsMax-3dmax2020.mst" ADSK_SOURCE_ROOT="Z:\software\dcc\3dsmax2020\Img\" REBOOT=ReallySuppress ADSK_SETUP_EXE=1 /q

:== NVIDIA mental ray and IRay plugins
Z:\software\dcc\3dsmax2020\Img\x64\MENTALRAYPLUG\MentalrayPlugins2020.msi ADSK_SOURCE_ROOT="Z:\software\dcc\3dsmax2020\Img\" /q

:== Autodesk Single Sign On
Z:\software\dcc\3dsmax2020\Img\x64\AdSSO\AdSSO.msi ADSK_SOURCE_ROOT="Z:\software\dcc\3dsmax2020\Img\" /q

:== MAXtoA Arnold
Z:\software\dcc\3dsmax2020\Img\x64\MAXtoA\ArnoldPlug.msi ADSK_SOURCE_ROOT="Z:\software\dcc\3dsmax2020\Img\" /q

:== Inventor Server Engine
Z:\software\dcc\3dsmax2020\Img\x64\Inventor_Server\Inventor_Engine_Max.msi ADSK_SOURCE_ROOT="Z:\software\dcc\3dsmax2020\Img\" /q

:== SQL Server LocalDB
Z:\software\dcc\3dsmax2020\Img\x64\RvtSQLDB\SqlLocalDb.msi IACCEPTSQLLOCALDBLICENSETERMS=yes ADSK_SOURCE_ROOT="Z:\software\dcc\3dsmax2020\Img\" /q

:== Revit Interoperability
Z:\software\dcc\3dsmax2020\Img\x64\REVIT\RXM.msi INSTALLDIR="D:\Autodesk\" ADSK_SOURCE_ROOT="Z:\software\dcc\3dsmax2020\Img\" /q

:== Civil View
Z:\software\dcc\3dsmax2020\Img\x86\Comp\CV\CivilView2020.msi ADSK_SOURCE_ROOT="Z:\software\dcc\3dsmax2020\Img\" /q


:: ================== 判断安装完成 ==================
#安装完成后，运行授权工具
#判断安装是否成功


echo ======================================
echo 3ds Max 2020 Install Finished
echo ======================================
start "" /wait "Z:\software\dcc\AutodeskLic\AutodeskLic.exe" /q
echo Return Code = %ERRORLEVEL%

if %ERRORLEVEL%==0 (
    echo lic ok
) else (
    echo lic failed
)



pause
