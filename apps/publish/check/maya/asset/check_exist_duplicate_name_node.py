# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       : check_exist_dis
# Describe   : 检查文件中是否存重名节点
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2024/6/26
# -------------------------------------------------------
import lib.common.loginfo as info

class Check(object):
    """
    检查项目当前使用maya软件的相关信息
    """

    def __init__(self):
        super(Check, self).__init__()

        self.tooltip = u'已检测重名节点'
        self.error=u'以下节点为重名节点,请修改'

    def checkinfo(self):
        """
        显示检查信息
        :return:
        """
        _error = self.run()
        _error_list = []
        if _error:
            _error_list.extend(_error)
            return False, info.displayErrorInfo(title=self.error, objList=_error_list)
        else:
            return True, info.displayInfo(title=self.tooltip)

    def run(self):
        import maya.cmds as cmds
        _error = []
        _nodes = cmds.ls()
        if _nodes:
            _error = [node for node in _nodes if '|' in node]
        return _error



