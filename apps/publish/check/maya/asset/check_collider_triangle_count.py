# -*- coding: utf-8 -*-
# author: linhuan
# file: check_collider_triangle_count.py
# time: 2026/1/16 10:29
# description:
import maya.cmds as cmds
import lib.common.loginfo as info
import database.shotgun.core.sg_analysis as sg_analysis
import database.shotgun.fun.get_entity as get_entity
import lib.maya.analysis.analyze_structure as structure

MAXCOUNT = 512
UVSETNUM = 1


class Check(object):
    """
    检查资产文件结构（以后按配置文件来查)
    """

    def __init__(self, TaskData):
        """
        实例初始化
        """
        # 即使直接派生自object，最好也调用一下super().__init__，
        # 不然可能造成多重继承时派生层次中某些类的__init__被跳过。
        super(Check, self).__init__()

        self._taskdata = TaskData
        # 结构

        self.entity_type = self._taskdata.entity_type
        self.entity_id = self._taskdata.entity_id
        self.entity_name = self._taskdata.entity_name
        self.step_name = self._taskdata.step_name
        self.task_name = self._taskdata.task_name
        self.sg = sg_analysis.Config().login()
        self._asset_level = get_entity.BaseGetSgInfo(self.sg, self.entity_id, self.entity_type).get_asset_level()

        self.asset_type = self._taskdata.asset_type
        self.analyze_handle = structure.AnalyStrue(self._taskdata)
        self.structure = self.analyze_handle.get_structure()
        self._structure = self._get_structure
        self.tooltip = u'开始检测碰撞体模型三角面数量是否超标'
        self.__error_info = u'请检查以下碰接体问题:'
        self._triangle_err = u'以下碰撞模型三角面数量超出{}，请检查：'.format(MAXCOUNT)
        self._uvset_error = u'以下碰撞模型UVSET数量不为{}，请检查：'.format(UVSETNUM)

        self.end = u"已检测完成，未发现碰撞体模型三角面数量超标情况。"
        if not self._structure:
            return

    @property
    def _get_structure(self):
        u"""
        获取结构
        :return:
        """
        structure = self.structure
        if self.asset_type in ['body', 'cartoon_body', 'cartoon_role', 'role']:
            structure = self._get_body_structure(structure)

        if (not self._asset_level or self._asset_level < 1) and isinstance(structure,
                                                                           dict) and 'level_0' in self.structure:
            return structure['level_0']
        elif self._asset_level and self._asset_level > 0:
            _key = 'level_{}'.format(self._asset_level)
            if _key and _key in structure:
                return structure[_key]
            elif 'level_0' in structure:
                return structure['level_0']
            else:
                return structure

        else:
            return structure

    def _get_body_structure(self, structure_info):

        if self.entity_name.endswith('_New'):

            if structure_info and isinstance(structure_info, list):
                structure_info_new = []
                for i in range(len(structure_info)):
                    info_new = structure_info[i].replace('_HD', '_New_HD').replace('_LD', '_New_LD').replace('_UE',
                                                                                                             '_New_UE')
                    structure_info_new.append(info_new)
                return structure_info_new
            elif structure_info and isinstance(structure_info, dict):
                structure_info_new = {}
                for k, v in structure_info.items():
                    if isinstance(v, str):
                        info_new = v.replace('_HD', '_New_HD').replace('_LD', '_New_LD').replace('_UE', '_New_UE')
                        structure_info_new[k] = info_new
                    elif isinstance(v, list):
                        info_new = []
                        for i in range(len(v)):
                            info_n = v[i].replace('_HD', '_New_HD').replace('_LD', '_New_LD').replace('_UE', '_New_UE')
                            info_new.append(info_n)
                        structure_info_new[k] = info_new
                return structure_info_new
            else:
                return structure_info

        else:
            return structure_info

    def checkinfo(self):
        """
        显示检查信息
        :return:
        """
        _error = self.run()

        _error_list = []
        if _error:
            _error_list.append(self.__error_info)
            for k, v in _error.items():
                _error_list.append(k)
                for obj in v:
                    _error_list.append('    {}'.format(obj))
                _error_list.append('===========')

            return False, info.displayErrorInfo(title=self.tooltip, objList=_error_list)
        else:
            return True, info.displayInfo(title=self.end)

    def run(self):
        error_triangle_meshs = []
        error_uvset_meshs = []
        error = {}
        collider_meshs = self._get_mod_grps_cllicder_meshs()
        if not collider_meshs:
            return
        for mesh in collider_meshs:
            triangle_num = self.get_mesh_triangle_num(mesh)
            if triangle_num > MAXCOUNT:
                error_triangle_meshs.append(mesh)
            uvset_num = self.get_meshs_uv_set_num(mesh)
            if not uvset_num or uvset_num != UVSETNUM:
                error_uvset_meshs.append(mesh)

        if error_triangle_meshs:
            error_triangle_meshs = list(set(error_triangle_meshs))
            error[self._triangle_err] = error_triangle_meshs
        if error_uvset_meshs:
            error_uvset_meshs = list(set(error_uvset_meshs))
            error[self._uvset_error] = error_uvset_meshs

        return error

    def _get_mod_grps_cllicder_meshs(self):
        mesh_list = []
        mod_grps = self._get_grps_structure(self._structure)
        if mod_grps:
            for mod_grp in mod_grps:
                if mod_grp and cmds.ls(mod_grp, type='transform'):
                    meshs = cmds.listRelatives(mod_grp, ad=1, type='mesh', f=1)
                    if meshs:
                        trs = cmds.listRelatives(meshs, p=1, f=1)
                        if trs:
                            for tr in trs:
                                if tr and tr not in mesh_list and tr.split('|')[-1].endswith('_Collider'):
                                    mesh_list.append(tr)
        return mesh_list

    def get_meshs_uv_set_num(self, mesh):
        """
        获取mesh的uv集数量
        :param mesh:
        :return:
        """
        if not mesh or not cmds.ls(mesh, type='transform'):
            return 0
        return cmds.polyUVSet(mesh, query=True, allUVSets=True).__len__()

    def get_mesh_triangle_num(self, mesh):
        """
        获取mesh三角面数量
        :param mesh:
        :return:
        """
        if not mesh or not cmds.ls(mesh, type='transform'):
            return 0
        shapes = cmds.listRelatives(mesh, s=1, f=1, type='mesh')
        if not shapes:
            return 0
        return cmds.polyEvaluate(mesh, triangle=1)

    def _get_grps_structure(self, structure):
        mod_grps = []
        if isinstance(structure, dict):
            for k, v in structure.items():
                if isinstance(v, list):
                    for _v in v:
                        if isinstance(_v, str) or isinstance(_v, unicode):
                            objs = cmds.ls('{}|{}'.format(k, _v))
                            if objs:
                                mod_grps.extend(objs)
                        elif isinstance(_v, dict):
                            mod_grps.extend(self._get_grps_structure(_v))
                elif isinstance(v, str) or isinstance(v, unicode):
                    objs = cmds.ls(v)
                    if objs:
                        mod_grps.extend(objs)
                elif isinstance(v, dict):
                    mod_grps.extend(self._get_grps_structure(v))
        if isinstance(structure, str) or isinstance(structure, unicode):
            objs = cmds.ls(structure)
            if objs:
                mod_grps.extend(objs)
        if isinstance(structure, list):
            for _v in structure:
                if isinstance(_v, str) or isinstance(_v, unicode):
                    objs = cmds.ls(_v)
                    if objs:
                        mod_grps.extend(objs)
                elif isinstance(_v, dict):
                    mod_grps.extend(self._get_grps_structure(_v))
        return mod_grps
