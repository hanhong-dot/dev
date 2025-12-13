# -*- coding: utf-8 -*-
# -----------------------------------
# @File    : check_exist_jont_skin.py
# @Author  : linhuan
# @Time    : 2025/7/4 16:39
# @Description : 
# -----------------------------------

import maya.cmds as cmds
import lib.common.loginfo as info
import lib.maya.analysis.analyze_structure as structure

reload(structure)

import database.shotgun.fun.get_entity as get_entity

reload(get_entity)

import database.shotgun.core.sg_analysis as sg_analysis

PARENTJOINT = 'Head_M_spare'


class Check(object):

    def __init__(self, TaskData):
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
        self.tooltip = u'开始检查Head_M_spare及以下骨骼与衣服,配饰,武器是否有蒙皮'
        self._err = u'以下骨骼与服,配饰,武器有蒙皮,请检查'

        self.end = u"已检测Head_M_spare及以下骨骼与衣服,配饰,武器是否有蒙皮"
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
            _error_list.append(self._err)
            _error_list.extend(_error)
            return False, info.displayErrorInfo(title=self.tooltip, objList=_error_list)
        else:
            return True, info.displayInfo(title=self.end)

    def run(self):
        if self.asset_type in ['role', 'rolaccesory', 'weapon', 'cartoon_role', 'cartoon_accessory']:
            return self.__check_skin_joints()
        else:

            return

    def __check_skin_joints(self):
        error_joints = []
        grp_meshs = self._get_mod_grps_meshs()
        joints = self._get_all_joints_parent_joint(PARENTJOINT)
        if grp_meshs and joints:
            for joint in joints:
                if self._judge_empty_joint(joint, grp_meshs):
                    error_joints.append(joint)
        if error_joints:
            return error_joints

    def _get_mod_grps_meshs(self):
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
                                if tr and tr not in mesh_list:
                                    mesh_list.append(tr)
        return mesh_list

    def _get_joins_from_sets(self):
        joints = []
        for set in SETS:
            joints.extend(self._get_set_joint(set))
        return joints

    def _judge_empty_joint(self, joint, meshs):
        joint_mesh = []
        if joint and meshs:
            for mesh in meshs:
                try:
                    result = cmds.skinCluster(mesh, inf=joint, q=True, dr=True)
                    if result:
                        joint_mesh.append(mesh)
                except:
                    pass
        if joint_mesh:
            return True
        else:
            return False

    def _get_all_joints_parent_joint(self, parent_joint=PARENTJOINT):
        __joints = []
        if not cmds.ls(parent_joint):
            return __joints
        __joints.append(cmds.ls(parent_joint)[0])
        __ch_joins = cmds.listRelatives(parent_joint, ad=1, type='joint', f=1)
        if __ch_joins:
            __joints.extend(__ch_joins)
        if __joints:
            __joints = list(set(__joints))
        return __joints

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
