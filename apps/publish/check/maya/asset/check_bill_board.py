# -*- coding: utf-8 -*-
# -----------------------------------
# @File    : check_bill_board.py
# @Author  : linhuan
# @Time    : 2025/8/14 11:13
# @Description : 
# -----------------------------------
import lib.common.loginfo as info
import maya.cmds as cmds
from lib.maya.node.mesh import Mesh


class Check(object):

    def __init__(self):
        super(Check, self).__init__()
        self.tooltip = u'已检测Billboard模型'
        self.error_info = u'请检查以下Billboard模型问题\n'

    def checkinfo(self):
        _error = self.run()
        _error_list = []
        if _error:
            for k, v in _error.items():
                _error_list.append(k)
                _error_list.extend(v)
            return False, info.displayErrorInfo(title=self.error_info, objList=_error_list)


        else:
            return True, info.displayInfo(title=self.tooltip)

    def run(self):
        return self.__get_bill_board_errors()

    def __get_mesh_structure(self,mesh):
        return Mesh(mesh).get_pology_structure()

    def __get_bill_board_errors(self):
        __error = {}
        __quad_error = []
        __point_error = []
        __uv_error = []
        bill_board_meshs = self.__get_bill_board_meshs()
        if not bill_board_meshs:
            return []
        for _mesh in bill_board_meshs:
            _mesh_structure = self.__get_mesh_structure(_mesh)
            if not self._jude_mesh_is_quads(_mesh_structure):
                __quad_error.append(_mesh)
                continue
            __type = self._judge_mesh_poins_distance(_mesh_structure)
            if __type == 'point':
                __point_error.append(_mesh)
                continue
            # ok, uv_info = self._check_uv(_mesh)
            # if not ok:
            #     __uv_error.append(_mesh + ' : ' + uv_info)
            #     continue
        if __quad_error:
            __error[u'以下模型不是四边面,请检查'] = __quad_error
        if __point_error:
            __error[u'以下模型为点模型,请检查'] = __point_error
        # if __uv_error:
        #     __error[u'以下模型UV检查不通过'] = __uv_error
        return __error

    def __get_bill_board_meshs(self):
        meshs = cmds.ls(type='mesh')
        bill_board_meshs = []
        for mesh in meshs:
            if cmds.listRelatives(mesh, parent=True, type='transform'):
                parent = cmds.listRelatives(mesh, type='transform', parent=True)[0]
                if parent.endswith('_Billboard'):
                    bill_board_meshs.append(parent)
        return bill_board_meshs

    def _jude_mesh_is_quads(self, mesh_structure):
        for k, v in mesh_structure.items():
            if len(v) != 4:
                return False
        return True

    def _judge_mesh_poins_distance(self, mesh_structure):
        __judge_model = 'model'
        for k, v in mesh_structure.items():
            for i in range(len(v)):
                pos = cmds.pointPosition(v[i], w=1)
                for j in range(len(v)):
                    pos_01 = cmds.pointPosition(v[j], w=1)
                    if v[i] != v[j]:
                        distance = ((pos[0] - pos_01[0]) ** 2 + (pos[1] - pos_01[1]) ** 2 + (
                                pos[2] - pos_01[2]) ** 2) ** 0.5
                        if distance <= 0.001:
                            __judge_model = 'point'
                            return __judge_model
                        if distance > 0.01:
                            __judge_model = 'model'
                            return __judge_model

        return __judge_model

    def _check_uv(self, mesh):
        all_uv_sets = cmds.polyUVSet(mesh, query=True, allUVSets=True)
        if not all_uv_sets:
            return False, u'缺少UV'
        for uv_set in all_uv_sets:
            if uv_set=='map2':
                return False, u'有占用map2 UVMap,请检查: {}'.format(uv_set)
        return True, u'UV检查通过'
