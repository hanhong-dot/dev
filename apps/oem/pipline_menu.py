# -*- coding: utf-8 -*-#
# Python       : python 2.7.16
# -------------------------------------------------------------------------------
# NAME         : check_bottom
# Describe     : 添加pipline菜单
# Version      : v0.01
# Author       : linhuan
# Email        : hanhong@papegames.net
# DateTime     : 2024/3/13__17:40
# -------------------------------------------------------------------------------
# -------------------------------------------------------------------------------
# example:
#
# -------------------------------------------------------------------------------

import sys
import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

sys.path.append('{}/site-packages'.format(BASE_DIR))
sys.path.append(BASE_DIR)



def create_pipline_menu(menuname):
    import maya.cmds as cmds
    # 检查菜单是否已存在，如果存在则删除
    if cmds.menu(menuname, exists=True):
        cmds.deleteUI(menuname, menu=True)

    # 创建菜单
    pipeline_menu = cmds.menu(menuname, label=u'X3 Pipeline Tools', parent='MayaWindow', tearOff=True)

    cmds.menuItem(label=u'模型检测', parent=pipeline_menu, command=perform_model_check)


def perform_model_check(*args):
    import mod_check.maya_checkwidget as maya_checkwidget
    reload(maya_checkwidget)
    maya_checkwidget.load_ui()


    print("执行模型检测...")


