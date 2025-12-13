# -*- coding: utf-8 -*-
# author: linhuan
# file: maya_batch_process.py
# time: 2025/12/1 18:02
# description:

from apps.batch.process.mayaprocess import MayaProcess

DCC_EXECUTEPATH = "c:/Program Files/Autodesk/Maya2018/bin/mayabatch.exe"

def cover_to_maya_by_json(json_file):
    dcc_executepath = DCC_EXECUTEPATH
    fullpathname=None
    executeCommand = "import sys;sys.path.append('z:/dev');import apps.launch.maya.interface.maya_launch as maya_launch;maya_launch.launch('batch');import apps.tools.motionbuilder.cover_mb_to_maya import ma_process_fun;reload(ma_process_fun);ma_process_fun.ma_process_file('{}')".format(json_file)
    # executeCommand=executeCommand.replace(';','\n')
    mayaprocess = MayaProcess(fullpathname, dcc_executepath, executeCommand)

    return mayaprocess.runProcess()
