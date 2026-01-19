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

    def __init__(self, TaskData):
        super(Check, self).__init__()

        self.tooltip = u'已检测重名节点'
        self.error = u'以下节点为重名节点,请修改'
        self.taskdata = TaskData
        self.asset_type = self.taskdata.asset_type

    def checkinfo(self):
        """
        显示检查信息
        :return:
        """
        _error = self.run()
        _error_list = []
        if _error:
            for _name, _nodes in _error.items():
                _error_list.append(u'请检查以下节点,有重名【{}】'.format(_name))
                _error_list.extend(_nodes)

        if _error:
            _error_list.extend(_error)
            return False, info.displayErrorInfo(title=self.error, objList=_error_list)
        else:
            return True, info.displayInfo(title=self.tooltip)

    def run(self):
        import maya.cmds as cmds
        if self.asset_type in ['body']:
            return
        _nodes = cmds.ls(tr=1, l=1)
        return self.__get_same_name_nodes(_nodes)

    def __get_same_name_nodes(self, nodes):
        import maya.cmds as cmds
        _same_name_dict = {}
        _list = []
        if not nodes:
            return _same_name_dict
        for _node in nodes:
            # 判断节点未引用
            if cmds.referenceQuery(_node, isNodeReferenced=True):
                continue

            _short_name = _node.split('|')[-1]
            if _short_name not in _list:
                _list.append(_short_name)
        if not _list:
            return _same_name_dict
        for _name in _list:
            _same_nodes = cmds.ls(_name, long=True)
            if _same_nodes and len(_same_nodes) > 1:
                _same_name_dict[_name] = _same_nodes
        return _same_name_dict

