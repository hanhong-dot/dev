# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       : maya_batch_process
# Describe   : 说明描述
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2024/3/6__11:46
# -------------------------------------------------------
from apps.batch.process.mayaprocess import MayaProcess

DCC_EXECUTEPATH = "c:/Program Files/Autodesk/Maya2018/bin/mayabatch.exe"


def batch_item_fbx_cover_wbx_publish(file_path, log_file):
    fullpathname=file_path
    dcc_executepath = DCC_EXECUTEPATH
    executeCommand = u"import sys;sys.path.append('z:/dev');import apps.launch.maya.interface.maya_launch as maya_launch;maya_launch.launch('batch');import apps.publish.batch_publish.batch_item_publish as batch_item_publish;batch_item_publish.batch_cover_fbx_publish('{}','{}')".format(
        fullpathname, log_file)
    # executeCommand=executeCommand.replace(';','\n')
    mayaprocess = MayaProcess(fullpathname, dcc_executepath, executeCommand)

    return mayaprocess.runProcess()
