# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       : batch_item_mdl_publish
# Describe   : 说明描述
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2024/1/9__23:54
# -------------------------------------------------------

from apps.batch.process.mayaprocess import MayaProcess

DCC_EXECUTEPATH = "c:/Program Files/Autodesk/Maya2018/bin/mayabatch.exe"

def item_mdl_batch_publish(file_path,log_file):
    fullpathname = file_path

    dcc_executepath = DCC_EXECUTEPATH
    executeCommand = "import sys;sys.path.append('z:/dev');import apps.launch.maya.interface.maya_launch as maya_launch;maya_launch.launch('batch');import apps.publish.batch_publish.batch_item_publish as batch_item_publish;batch_item_publish.batch_publish('{}','{}')".format(
        fullpathname,log_file)
    # executeCommand=executeCommand.replace(';','\n')
    mayaprocess = MayaProcess(fullpathname, dcc_executepath, executeCommand)

    return mayaprocess.runProcess()

#
# if __name__ == '__main__':
#
#     file_path='E:/p/card_cream_fx_003.drama_mdl.v002.ma'
#     log_file='E:/p/card_cream_fx_003.drama_mdl.v002.log'
#     item_mdl_batch_publish(file_path,log_file)
