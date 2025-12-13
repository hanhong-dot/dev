# -*- coding: utf-8 -*-#
# Python     : 
# -------------------------------------------------------
# NAME       :process_repair_skin.py
# Describe   :
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2024/11/18 10:38
# -------------------------------------------------------
import maya.cmds as cmds
from apps.publish.process.maya.process_rig_export_fbx import Porcess_RigFbx_Export
from method.maya.common.file import BaseFile

import maya.mel as mel
import database.shotgun.fun.get_entity as get_entity
import database.shotgun.core.sg_analysis as sg_analysis
ROOT = 'Root_M'


class ProcessRepairSkin(Porcess_RigFbx_Export):

    def __init__(self, TaskData):
        Porcess_RigFbx_Export.__init__(self, TaskData)
        self.__task_data = TaskData
        self.__asset_type = TaskData.asset_type
        self.__entity_id=TaskData.entity_id
        self.__entity_type=TaskData.entity_type
        self.sg = sg_analysis.Config().login()
        self.__asset_level = get_entity.BaseGetSgInfo(self.sg, self.__entity_id, self.__entity_type).get_asset_level()
        print('asset_level:', self.__asset_level)

    def repair_skin(self):

        if self.__asset_type.lower() in ['role','body'] or (self.__asset_type.lower() in ['item'] and  self.__asset_level==4):
            self.__repair_skin()
        else:
            return


    def get_export_meshs(self):
        return self.__get_exoprt_mesh_objs()

    def __repair_skin(self):
        meshs= self.__get_exoprt_mesh_objs()
        if not meshs:
            return
        error_objs = self._get_error_objs(meshs)
        print('error_objs:', error_objs)
        if not error_objs:
            return
        self.__repair_error_skin(error_objs)

    def __repair_error_skin(self, error_objs):
        if not error_objs:
            return
        for error_obj in error_objs:
            skin = mel.eval('findRelatedSkinCluster {}'.format(error_obj))
            try:
                cmds.skinCluster(skin,e=1,ai='Root_M',lw=1,wt=0)
            except Exception as e:
                print('repair_error_skin:', e)

    def _get_error_objs(self, meshs):
        error_objs = []
        for mesh in meshs:
            if self.__check_skin_cluster(mesh) == False:
                error_objs.append(mesh)
        return error_objs

    def __check_skin_cluster(self, mesh):
        skin = mel.eval('findRelatedSkinCluster {}'.format(mesh))
        if skin:
            bones = cmds.skinCluster(skin, q=1, inf=1)
            if ROOT not in bones:
                return False
        return True



    def __get_exoprt_mesh_objs(self):
        export_objs = self.get_export_mod_objs_info()
        if not export_objs:
            return None
        export_grps = self.__get_objs(export_objs)
        if not export_grps:
            return None
        meshs = self.__sect_grps_mes_trs(export_grps)
        return meshs

    def __get_objs(self, objs):
        _objs = []
        for obj in objs:
            if cmds.ls(objs):
                _objs.extend(cmds.ls(obj, l=1, tr=1))
        if _objs:
            return list(set(_objs))

    def __sect_grps_mes_trs(self, _grps):
        trs = []
        _meshs = self.__get_meshs_from_grps(_grps)
        if _meshs:
            for _mesh in _meshs:
                tr = cmds.listRelatives(_mesh, p=1, type='transform', f=1)
                if tr:
                    trs.extend(tr)
        if trs:
            return list(set(trs))

    def __get_meshs_from_grps(self, _grps):

        _meshs = []
        if _grps:
            for _grp in _grps:
                _mshs = self.select_grp_meshs(_grp)
                if _mshs:
                    _meshs.extend(_mshs)
        return _meshs

if __name__ == '__main__':
    import method.shotgun.get_task as get_task

    _filename = cmds.file(q=1, exn=1)
    taskdata = get_task.TaskInfo(_filename, 'X3', 'maya', 'version')

    handle = ProcessRepairSkin(taskdata)
    handle.repair_skin()
    # meshs = handle.get_export_meshs()
    # error=handle._get_error_objs(meshs)
