# -*- coding: utf-8 -*-#
# Python     : 
# -------------------------------------------------------
# NAME       :unlock_textlist.py
# Describe   :
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2024/12/31 20:03
# -------------------------------------------------------
import maya.cmds as cmds


def set_textlistlu():
    textlists = cmds.ls(type='defaultTextureList')
    for textlist in textlists:
        try:
            cmds.lockNode(textlist, l=0, lu=0)
        except:
            pass
    cmds.lockNode('renderPartition', l=False, lockUnpublished=False)
    cmds.confirmDialog(title=u'提示信息', message=u'已解锁相关节点,请检查文件', button=['Yes'])
