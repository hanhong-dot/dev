# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       :
# Describe   :
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2024/8/26_16:05
# -------------------------------------------------------
import maya.cmds as cmds
import lib.common.loginfo as _info

reload(_info)




class Check(object):
    """
    检查同一个模型重叠点问题
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
        self.errortip = u"以下模型有重点,请检查"

    def checkinfo(self):
        """
        显示检查信息
        :return:
        """
        _error = self.run()
        _error_list = []
        if _error:
            for _err in _error:
                if _err:
                    for _key, _value in _err.items():
                        _error_list.append(_key)
                        _error_list.append(u'【{}】模型,以下点重合,请检查'.format(_key))
                        _error_list.extend(_value)

            return False, _info.displayErrorInfo(title=self.errortip, objList=_error_list)
        else:
            return True, _info.displayInfo(title=self.tooltip)

    def run(self):
        _error_list = []
        __meshs = self._get_meshs()

        __trs = self._get_mesh_trs(__meshs)


        __trs=self.__get_hair_trs(__trs)
        if not __trs:
            return
        for tr in __trs:
            _error = self._get_closing_vtx(tr)
            if _error:
                _error_list.append(_error)
        return _error_list


    def __get_hair_trs(self,trs,match='_Hair'):
        _trs=[]
        if trs:
            for tr in trs:
                if match in tr.split('|')[-1]:
                    _trs.append(tr)
        return _trs


    def _get_mesh_trs(self, meshs):
        _trs = []
        if not meshs:
            return _trs
        for __mesh in meshs:
            _tr = cmds.listRelatives(__mesh, p=1,type='transform',f=1)
            if _tr:
                _trs.append(_tr[0])
        if _trs:
            return list(set(_trs))

    def _get_meshs(self):
        if self.groups_list:
            return [__mesh for group in self.groups_list for __mesh in cmds.listRelatives(group, ad=1, type="mesh")]
        else:
            return cmds.ls(type="mesh")

    def fix(self):
        """
        修复相关内容
        :return:
        """
        pass

    def _get_closing_vtx(self,tr):
        import pymel.core as pm
        error={}
        cmds.select(cl=1)
        cmds.select(tr)
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
        if same_id:

            error[tr]=['{}.vtx[{}]'.format(tr,i) for i in same_id]
        return error






    def _get_distance(self, pos1, pos2):
        import math
        return math.sqrt(math.pow(pos1[0] - pos2[0], 2) + math.pow(pos1[1] - pos2[1], 2) + math.pow(pos1[2] - pos2[2], 2))

if __name__ == '__main__':

    check = Check()
    chinfo=check.checkinfo()