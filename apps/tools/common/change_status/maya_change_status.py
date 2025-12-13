# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       : maya_change_status
# Describe   : maya当前文件更新状态到ip
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2022/11/9__20:32
# -------------------------------------------------------
import maya.cmds as cmds
import apps.tools.common.change_status.change_statu as _change_status
reload(_change_status)

def maya_change_status(_project=None, _filename=None, ui=True):
    u"""
    收集节点文件到相应work路径
    """
    if ui == True:
        result = cmds.confirmDialog(title=u'提示信息', message=u'<font color=gold><h3>请确认当前文件任务状态是否需要设置为【ip】', button=['Yes','No'],defaultButton='Yes', cancelButton='No', dismissString='No')
        if result =='No':
            return
    if not _filename:
        _filename = cmds.file(q=1, exn=1)
    return _change_status.change_status(_filename)