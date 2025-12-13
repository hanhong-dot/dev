# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       : check_exist_triexceed
# Describe   : 检测面数(三角面)
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2022/10/27__19:41
# -------------------------------------------------------

import lib.common.loginfo as info
import maya.cmds as cmds

NODETYPES = ['blindDataTemplate']


class Check(object):
    u"""
    检测文件中(组下)是否有未freeze物体
    """

    def __init__(self):
        self._tooltip_error = u'有以下无用节点,请检查修复'
        self._tooltip = u'已检测无用节点'
        self._fix = u'已清理无用节点'

    def checkinfo(self):
        errlist = self.run()
        if errlist:
            return False, info.displayErrorInfo(objList=errlist)
        else:
            return True, info.displayInfo(title=self._tooltip)

    def run(self):
        u"""
        无用节点检测
        :return: errdict
        """
        errlist = []
        for nodetype in NODETYPES:
            nodes = cmds.ls(type=nodetype)
            if nodes:
                for node in nodes:
                    cons = cmds.listConnections(node)
                    if not cons:
                        errlist.append(node)
        return errlist

    def fix(self):
        u"""
        修复未freeze物体（将未freeze物体，进行freeze)
        :return: 为True时，修复成功,为False时，未修复成功
        """
        errlist = self.run()
        result = True
        if errlist:
            result = self._clean(errlist)
        if result:
            return True, info.displayInfo(title=self._fix)
        else:
            _err=[]
            _errlist = self.run()
            if _errlist:
                _err.append(u"以下节点未清理,请检查是否为参考节点,请先清理参考文件节点")
                _err.extend(_errlist)
                return False, info.displayErrorInfo(objList=_err)

    def _clean(self, objlist):
        if objlist:
            try:
                cmds.delete(objlist)
                return True
            except:
                return False
