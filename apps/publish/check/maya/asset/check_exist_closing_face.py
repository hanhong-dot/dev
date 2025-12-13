# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       : check_exist_closingpoint
# Describe   : 检测重合的面
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2024/3/4_14:03
# -------------------------------------------------------
import maya.cmds as cmds
import lib.common.loginfo as info
import pymel.core as pm

from lib.maya.node.mesh import Mesh


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

        self.tooltip = u'已检测重合的面'

    def checkinfo(self):
        """
        显示检查信息
        :return:
        """
        _error = self.run()
        _error_list = []
        if _error:
            _error_list.append(u"以下模型有重叠面，请检查")
            _error_list.extend(_error)
            return False, info.displayErrorInfo(title=self.tooltip, objList=_error_list)
        else:
            return True, info.displayInfo(title=self.tooltip)

    def run(self):

        """
        检查maya相关版本信息
        :return:
        """
        error = []

        polygons = set(mesh.getParent() for mesh in pm.ls(type="mesh"))

        cmds.select(cl=1)
        if polygons:
            for polygon in polygons:
                _closing_face = self._closing_face(polygon)
                if _closing_face:
                    error.extend(_closing_face)

        if error:
            error = list(set(error))
            cmds.select(error)
        return error

    def fix(self):
        """
        修复相关内容
        :return:
        """
        pass

    def __get_hair_trs(self,trs,match='_Hair'):
        _trs=[]
        if trs:
            for tr in trs:
                if match in tr.split('|')[-1]:
                    _trs.append(tr)
        return _trs


    def _closing_face(self, polygon,match='_Hair'):
        polygon_name=polygon.name()
        if match and match not in polygon_name.split('|')[-1]:
            return []

        same_points = self._get_same_points(polygon)
        if not same_points:
            return []
        mesh = polygon.getShape()
        _structure = Mesh(mesh.name()).get_pology_structure()
        same_faces = []
        if not _structure:
            return []
        for k, v in _structure.items():
            face_same_point = []
            if not v:
                continue
            for i in range(len(v)):
                if v[i] in same_points:
                    face_same_point.append(v[i])
            if face_same_point and len(face_same_point) >= 3:
                same_faces.append(k)
        return same_faces

    def _get_same_points(self, polygon):
        mesh = polygon.getShape()
        points = cmds.xform(mesh.name() + ".vtx[*]", q=1, t=1, ws=1)
        points = [tuple(int(points[j] * 10000) for j in range(i, i + 3, 1)) for i in range(0, len(points), 3)]
        point_set = set()
        same_id = set()
        same_points = []
        for i, p in enumerate(points):
            if p in point_set:
                same_id.add(i)
            point_set.add(p)
        if same_id:
            for id in same_id:
                point = mesh.vtx[id].name()
                same_points.append(point)
        return same_points

    def get_obj_from_mesh(self, mesh):
        if mesh and cmds.listRelatives(mesh, p=1, type='transform'):
            return cmds.listRelatives(mesh, p=1, type='transform')[0]


if __name__ == '__main__':
    handle = Check()
    print handle.checkinfo()
