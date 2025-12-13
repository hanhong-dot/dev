# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       : check_exist_dis
# Describe   : 检查文件中是否存在显示层
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2022/7/15__10:00
# -------------------------------------------------------
import maya.cmds as cmds
import lib.common.loginfo as info

LAYERTYPE = ["displayLayer"]
EXCEPT = ["defaultLayer"]


class Check(object):
    """
    检查项目当前使用maya软件的相关信息
    """

    def __init__(self,TaskData):
        """
        实例初始化
        """
        # 即使直接派生自object，最好也调用一下super().__init__，
        # 不然可能造成多重继承时派生层次中某些类的__init__被跳过。
        super(Check, self).__init__()
        self._taskdata=TaskData
        self._task_name = self._taskdata.task_name

        self.tooltip = u'已检查显示层'

    def checkinfo(self):
        """
        显示检查信息
        :return:
        """
        _error = self.run()
        _error_list = []
        if _error:
            _error_list.append(u"文件中有以下显示层，请检查")
            _error_list.extend(_error)
            return False, info.displayErrorInfo(title=self.tooltip, objList=_error_list)
        else:
            return True, info.displayInfo(title=self.tooltip)

    def run(self):

        """
        检查关键帧
        :return:
        """
        if self._task_name in ['drama_rig','rbf','ue_rig','out_rig']:
            return self._check_rig()
        else:
            return self._chek_mod()

    def _chek_mod(self):
        _layers=cmds.ls(type=LAYERTYPE)
        if len(_layers)>1:
            return list(set(cmds.ls(type=LAYERTYPE)) - set(EXCEPT))

    def _check_rig(self):
        u"""
        rig 显示层检测(参考缘故，放松了对defaultLayer的检测)
        """
        _err = []
        _layers = cmds.ls(type=LAYERTYPE)
        if _layers:
            for _layer in _layers :
                if EXCEPT[0] not in _layer:
                    _err.append(_layer)
        return _err




    def fix(self):
        """
        修复相关内容
        :return:
        """
        _error = self.run()
        if _error:
            self._delete_nodes(_error)

    def _delete_nodes(self, _nodelist):
        u"""
        删除节点
        Args:
            _nodelist: 需要删除的节点列表

        Returns:

        """
        if _nodelist:
            try:
                cmds.delete(_nodelist)
            except:
                for _err in _nodelist:
                    try:
                        cmds.lockNode(_err, l=0)
                        cmds.delete(_nodelist)
                    except:
                        pass
