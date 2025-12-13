# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       : check_exist_closingpoint
# Describe   : 检测重合的点
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2022/6/29__14:03
# -------------------------------------------------------
import maya.cmds as cmds
import lib.common.loginfo as _info
reload(_info)
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

        self.tooltip = u'已检测重合的点'
        self.errortip=u"以下模型有重点,请检查"

    def checkinfo(self):
        """
        显示检查信息
        :return:
        """
        _error = self.run()
        _error_list = []
        if _error:
            _error_list=_error_list
            return False, _info.displayErrorInfo(title=self.errortip, objList=_error_list)
        else:
            return True, _info.displayInfo(title=self.tooltip)

    def run(self):

        """
        检查maya相关版本信息
        :return:
        """
        polygons = set(mesh.getParent() for mesh in pm.ls(type="mesh"))
        cmds.select(cl=1)
        if polygons:
            for polygon in polygons:
                self._closing_vtx(polygon)
        errors=cmds.ls(sl=1)
        if errors:
            return errors
        else:
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


# if __name__ == '__main__':
#     print
#     Check().run()
