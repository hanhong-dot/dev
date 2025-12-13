# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       : test
# Describe   : 说明描述
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2023/3/20__19:28
# -------------------------------------------------------
import subprocess
fp = r"Z:\dev\tools\x3_P4\wsy_scripts\fbx_exporter_single_person\main_check_nan\main_check_nan.exe"
#fp= r"F:\0-wsy\code\fbx_handler\dist\main_check_nan\main_check_nan.exe"
export_fp = r"1111"
startupinfo = subprocess.STARTUPINFO()
startupinfo.dwFlags = subprocess.CREATE_NEW_CONSOLE | subprocess.STARTF_USESHOWWINDOW
startupinfo.wShowWindow = subprocess.SW_HIDE
p = subprocess.Popen([fp, export_fp,], startupinfo=startupinfo,stdout=subprocess.PIPE, stderr=subprocess.PIPE,)
res = p.wait()

line=p.stdout.read()


print(line)
line= p.stderr.read()
print(line)
print res