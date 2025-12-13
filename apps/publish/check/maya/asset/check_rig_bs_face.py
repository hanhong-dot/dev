# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       :
# Describe   :
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2024/10/08__16:03
# -------------------------------------------------------
import lib.common.loginfo as info
import maya.cmds as cmds
from apps.publish.process.maya import process_rig_export_fbx

reload(process_rig_export_fbx)
from lib.maya.node.mesh import Mesh

LIMIT_FACE_COUNT = 80000


class Check(object):
    def __init__(self, TaskData):
        self.task_data = TaskData
        self.tooltip = u'开始检测导出fbx组面数(超过80000,则不允许连接BlendShape)'
        self.tooltip_error = u'以下导出fbx组面数超过80000,不允许连接BlendShape'
        self.end = u'已检测'

    def checkinfo(self):
        _error = self.run()

        _error_list = []
        if _error:
            _error_list.append(self.tooltip_error)
            _error_list.extend(_error)

            return False, info.displayErrorInfo(title=self.tooltip, objList=_error_list)
        else:
            return True, info.displayInfo(title=self.tooltip, objList=[self.end])

    def run(self):
        _error = []
        _exp_handle=process_rig_export_fbx.Porcess_RigFbx_Export(self.task_data)
        __exp_grps=_exp_handle.get_fbx_objs()
        _error=self.__check_grps(__exp_grps)
        return _error

    def __get_meshs_from_group(self, group):
        _meshs = []
        if not group or not cmds.objExists(group):
            return _meshs
        __meshs = cmds.listRelatives(group, ad=True, type='mesh',f=1)
        if __meshs:
            for mesh in __meshs:
                tr = cmds.listRelatives(mesh, p=True, f=True)
                if tr:
                    _meshs.append(tr[0])
        if _meshs:
            _meshs = list(set(_meshs))

        return _meshs

    def __get_num_from_group(self, group):
        _num = 0

        meshs = self.__get_meshs_from_group(group)
        for mesh in meshs:
            __mesh_num = Mesh(mesh).numFaces
            _num += __mesh_num
        return _num

    def __check_group_bs(self, group):
        bs=[]
        meshs= self.__get_meshs_from_group(group)
        if not meshs:
            return
        for mesh in meshs:
            bs_nodes=[]
            his=cmds.listHistory(mesh)
            if not his:
                continue
            for h in his:
                if cmds.nodeType(h)=='blendShape':
                    bs_nodes.append(h)
            if bs_nodes:
                bs.append(mesh)
        if bs:
            bs= list(set(bs))
        return bs

    def __check_group(self, group):
        _num = self.__get_num_from_group(group)
        if _num > LIMIT_FACE_COUNT:
            bs=self.__check_group_bs(group)
            if bs:
                return bs
            else:
                return None
        return None

    def __check_grps(self,grps):
        _error = []
        if not grps:
            return _error
        for grp in grps:
            _bs=self.__check_group(grp)
            if _bs:
                _error.append(grp)
        if _error:
            _error= list(set(_error))
        return _error








