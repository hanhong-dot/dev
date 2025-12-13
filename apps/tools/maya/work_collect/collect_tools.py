# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       : collect_tools
# Describe   : 说明描述
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2022/7/5__16:48
# -------------------------------------------------------

import apps.tools.maya.work_collect.collect_workfile as collect_workfile

reload(collect_workfile)
import maya.cmds as cmds
import maya.mel as mel
import os

def collect_work(_project=None, _filename=None, ui=True, _cover='.tif'):
    u"""
    收集节点文件到相应work路径
    """
    try:
        mel.eval('hyperShadePanelMenuCommand("hyperShadePanel1", "deleteUnusedNodes")')
    except:
        pass
    if ui == True:
        inf = cmds.confirmDialog(title=u'提示信息', message=u'请确认是否收集节点文件到<{}>项目work路径'.format(_project), button=['Yes',
                                                                                                              'No'],
                                 defaultButton='Yes')
        if inf == 'No':
            return
    if not _filename:
        _filename = cmds.file(q=1, exn=1)
    dir,base_name=os.path.split(_filename)
    info= base_name.split('.')
    if 2<=len(info)<4:
        _base_name='{}.{}.v001.ma'.format(info[0],info[1])
        _filename='{}/{}'.format(dir,_base_name)

    collect_workfile.CollectWork(_filename, _project).collect_work_nodefile(_cover=_cover)
