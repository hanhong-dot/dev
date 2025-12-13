# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       : check_exist_fiveedge
# Describe   : 检查多边面
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2022/6/29__15:51
# -------------------------------------------------------
import maya.cmds as cmds
import lib.common.loginfo as info
import pymel.core as pm


class Check(object):
    """
    检查项目当前使用maya软件的相关信息
    """

    def __init__(self, groups_list=None):
        """
        实例初始化
        """
        # 即使直接派生自object，最好也调用一下super().__init__，
        # 不然可能造成多重继承时派生层次中某些类的__init__被跳过。
        super(Check, self).__init__()
        self.groups_list = groups_list

        self.tooltip = u'已检测多边面'

    def checkinfo(self):
        """
        显示检查信息
        :return:
        """
        _error = self.run()
        _error_list = []
        if _error:
            _error_list.append(u"请检查以下模型面")
            _error_list.extend(_error)
            return False, info.displayErrorInfo(title=self.tooltip, objList=_error_list)
        else:
            return True, info.displayInfo(title=self.tooltip)

    def run(self):

        """
        检查maya相关版本信息
        :return:
        """
        try:
            pm.select(cl=1)
            pm.mel.polyCleanupArgList(4, ["1", "2", "0", "0", "1", "0", "0", "0", "0", "1e-05", "0", "1e-05", "0", "1e-05",
                                          "0", "-1", "0", "0"])
            return cmds.ls(sl=1,l=1)
        except:
            return []

    def fix(self):
        """
        修复相关内容
        :return:
        """
        pass

    def _closing_vtx(self, polygon=None):
        if polygon is None:
            polygon = pm.selected()[0]
        mesh = polygon.getShape()
        points = cmds.xform(mesh.name() + ".vtx[*]", q=1, t=1, ws=1)
        points = [tuple(int(points[j] * 10000) for j in range(i, i + 3, 1)) for i in range(0, len(points), 3)]
        point_set = set()
        same_id = set()
        for i, p in enumerate(points):
            if p in point_set:
                same_id.add(i)
            point_set.add(p)
        pm.select([mesh.vtx[i] for i in same_id], tgl=1)
        return bool(same_id)
if __name__ == '__main__':
    print Check().run()