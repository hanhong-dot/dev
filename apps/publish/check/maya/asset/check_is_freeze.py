# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       : check_is_freeze
# Describe   :
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2022/6/27__17:39
# -------------------------------------------------------

import lib.maya.node.grop as group_common
import lib.maya.node.nodes as node_common
import lib.common.loginfo as info
import maya.cmds as cmds


class Check(object):
    u"""
    检测文件中(组下)是否有未freeze物体
    """

    def __init__(self, grpsname=None, is_checkobjs=True):
        u"""
        检测文件（特定组下)是否有未freeze物体
        :param grpsname: 组名(如果为None，则会检测文件中所有大组),不为空时，则为list，例如['MODEL']
        :param is_checkobjs: 为True时，检测组及组下物体；为False时，则仅检测大组列表，不检测组下物体
        """
        self.groups = grpsname
        self.is_checkobjs = is_checkobjs
        if self.groups == None:
            self.groups = group_common.BaseGroup().get_root_groups()

    def checkinfo(self):
        errlist = self.run()
        if errlist:
            return False, info.displayErrorInfo(objList=errlist)
        else:
            return True, None

    def run(self):
        u"""
        freeze物体检测
        :return: errdict
        """
        errlist = []
        checkobjs = []
        if self.groups and self.is_checkobjs == True:
            for i in range(len(self.groups)):
                objs = group_common.Group(self.groups[i]).select_group_transforms()
                if objs:
                    checkobjs.extend(objs)
        if self.groups:
            checkobjs.extend(self.groups)
        if checkobjs:
            errlist = self._freezecheck(checkobjs)
        return errlist

    def fix(self):
        u"""
        修复未freeze物体（将未freeze物体，进行freeze)
        :return: 为True时，修复成功,为False时，未修复成功
        """
        errlist = self.run()
        result = True
        if errlist:
            result = self._freeze(errlist)
        return result

    def _freeze(self, objlist):
        u"""
        将objlist列表中的物体(或组)进行freeze
        :param objlist: 需要freeze的物体列表
        :return: True，修复成功,False，未修复成功
        """
        import maya.mel as mel
        no_freezelist = []
        if objlist:
            # 解锁
            node_common.BaseNodeProcess().unlock_nodelist(objlist)
            # freeze
            for obj in objlist:
                try:
                    cmds.select(obj)
                    mel.eval("FreezeTransformations()")
                    mel.eval("ResetTransformations()")
                except:
                    no_freezelist.append(obj)

        if no_freezelist:
            return False
        else:
            return True

    def _freezecheck(self, objlist):
        u"""
        检查objs中没有frezze的物体
        :param objs: 物体列表
        :return: nofreezelist
        """
        _Num = [1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0]
        _piv=[0,0,0,0,0,0]
        _error=[]
        if objlist:
            for _obj in objlist:
                if _obj and cmds.ls(_obj) and (cmds.xform(_obj, q=1, m=1, ws=1) !=_Num or cmds.xform(_obj,q=1,piv=1,ws=1)!=_piv) and _obj not in _error:
                    _error.append(_obj)
        return _error