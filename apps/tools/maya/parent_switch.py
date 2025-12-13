# -*- coding: utf-8 -*-#
# Python     : 
# -------------------------------------------------------
# NAME       :parent_switch.py
# Describe   : 卡米提供
# version    : v0.01
# Author     : linhuan(卡米提供)
# Email      : hanhong@papegames.net
# DateTime   : 2024/11/27 16:09
# -------------------------------------------------------
import maya.cmds as cmds


def parent_switch():
    sel = cmds.ls(sl=True)

    if sel:
        for ii in sel:
            if cmds.objExists(ii + '.Parent_Switch') == 1:
                enum_name = cmds.attributeQuery('Parent_Switch', node=ii, le=1)[0].split(':')
                enum_number = len(enum_name)
                current_id = cmds.getAttr(ii + '.Parent_Switch')
                if current_id < range(enum_number)[-1]:
                    matrix = cmds.xform(ii, q=1, m=1, ws=1)
                    cmds.setAttr(ii + '.Parent_Switch', current_id + 1)
                    cmds.xform(ii, m=matrix, ws=1)
                    cmds.headsUpMessage('parent switch convert to {0}'.format(enum_name[current_id + 1]), t=2)
                else:
                    matrix = cmds.xform(ii, q=1, m=1, ws=1)
                    cmds.setAttr(ii + '.Parent_Switch', 0)
                    cmds.xform(ii, m=matrix, ws=1)
                    cmds.headsUpMessage('parent switch convert to {0}'.format(enum_name[0]), t=2)
