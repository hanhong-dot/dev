# -*- coding: utf-8 -*-#
# Python     : 
# -------------------------------------------------------
# NAME       : check_rig_sg
# Describe   : 检测并修复文件sg节点
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2025/3/13__17:08
# -------------------------------------------------------
import lib.common.loginfo as info
import method.maya.common.file as maya_file

import maya.cmds as cmds

SGNAME = 'RigCheckSG'


class Check(object):
    """
    检测文件能否正常创建sg节点，并进行修复
    """

    def __init__(self):
        super(Check, self).__init__()
        self._tooltip_error = u'文件无法正常创建SG节点,请点修复进行修复'
        self._tooltip_true = u'已检测SG节点是否可以正常创建'

    def checkinfo(self):
        _error = self.run()

        objlist = []
        if _error:
            objlist.append(_error)
            return False, info.displayErrorInfo(title=self._tooltip_error, objList=objlist)
        else:
            return True, info.displayInfo(title=self._tooltip_true)

    def run(self):

        try:
            sg = cmds.sets(renderable=1, noSurfaceShader=1, em=1, n=SGNAME)
            cmds.delete(sg)
            return
        except:
            try:
                sg = cmds.sets(renderable=1, noSurfaceShader=1, em=1, n=SGNAME)
                cmds.delete(sg)
                return
            except:
                return u'文件无法正常创建SG节点,请点修复进行修复'

    def fix(self):
        __texturelist = cmds.ls(type='defaultTextureList')
        if __texturelist:
            for _texturelist in __texturelist:
                cmds.lockNode(_texturelist, l=False, lockUnpublished=False)

        cmds.lockNode('renderPartition', l=False, lockUnpublished=False)
        sg = cmds.sets(renderable=1, noSurfaceShader=1, em=1, n=SGNAME)
        cmds.delete(sg)


    def __fix_sg(self):
        __texturelist = cmds.ls(type='defaultTextureList')
        if __texturelist:
            for _texturelist in __texturelist:
                cmds.lockNode(_texturelist, l=False, lockUnpublished=False)

        cmds.lockNode('renderPartition', l=False, lockUnpublished=False)

