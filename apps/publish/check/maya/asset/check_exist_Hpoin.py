# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       : check_exist_Hpoin
# Describe   : 检测绑定文件中是否有手部挂点(卡米提供基本代码)
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2023/2/9__15:40
# -------------------------------------------------------
import lib.common.loginfo as info
import maya.cmds as cmds

HPOINTHAND = {'HPoint_hand_R': {'matchTransform': 'Wrist_R', 'parent': 'Wrist_R'},
              'HPoint_hand_L': {'matchTransform': 'Wrist_L', 'parent': 'Wrist_L'}}


class Check(object):
    """
    检查项目当前使用maya软件的相关信息
    """

    def __init__(self, TaskData):
        """
        实例初始化
        """
        # 即使直接派生自object，最好也调用一下super().__init__，
        # 不然可能造成多重继承时派生层次中某些类的__init__被跳过。
        super(Check, self).__init__()
        self.assettype=TaskData.asset_type

        self.tooltip = u'已检测手部挂点'

    def checkinfo(self):
        """
        显示检查信息
        :return:
        """
        _error = self.run()
        _error_list = []
        if _error:
            _error_list.append(u"缺少以下手部挂点，请检查(可点修复)")
            _error_list.extend(_error)
            return False, info.displayErrorInfo(title=self.tooltip, objList=_error_list)
        else:
            return True, info.displayInfo(title=self.tooltip)

    def run(self):

        """
        检查关键帧
        :return:
        """
        if self.assettype and self.assettype.lower() in ['npc']:
            error = []
            hpoints = HPOINTHAND.keys()
            for i in range(len(hpoints)):
                if not cmds.objExists(hpoints[i]):
                    error.extend([hpoints[i]])
            if error:
                return list(set(error))

    # </editor-fold>

    def fix(self):
        """
        修复相关内容
        :return:
        """
        _errors = self.run()
        if _errors:
            for _err in _errors:
                _hand = cmds.createNode('joint', n=_err)
                cmds.matchTransform(_hand, HPOINTHAND[_err]['matchTransform'], pos=True)
                y_value = cmds.getAttr(_hand + '.ty')
                cmds.setAttr(_hand + '.ty', y_value - 4.0)
                cmds.parent(_hand, HPOINTHAND[_err]['parent'])