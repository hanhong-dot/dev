# -*- coding: utf-8 -*-
# -----------------------------------
# @File    : check_ue_role_shader.py
# @Author  : linhuan
# @Time    : 2025/7/23 11:12
# @Description : 
# -----------------------------------
import lib.common.loginfo as info
import lib.maya.analysis.analyze_structure as structure
import database.shotgun.fun.get_entity as get_entity
import database.shotgun.core.sg_analysis as sg_analysis
import maya.cmds as cmds

from lib.maya.analysis.analyze_config import AnalyDatas
class Check(object):

    def __init__(self, TaskData):
        super(Check, self).__init__()
        self.TaskData = TaskData
        self.asset_type = self.TaskData.asset_type
        self.task_name = self.TaskData.task_name
        self.sg = sg_analysis.Config().login()
        self.entity_id = self.TaskData.entity_id
        self.entity_type = self.TaskData.entity_type
        self.entity_name = self.TaskData.entity_name
        self._asset_level = get_entity.BaseGetSgInfo(self.sg, self.entity_id, self.entity_type).get_asset_level()
        self.tooltip = u'已检测UE材质命名'
        self.error_info = u'以下节点命名不符合规范,请检查'
        self.analyze_handle = structure.AnalyStrue(self.TaskData)
        self.structure = self.analyze_handle.get_structure()

    def checkinfo(self):
        _error = self.run()
        _error_list = []
        if _error:
            for k, v in _error.items():
                _error_list.append(k)
                for k,v in v.items():
                    _error_list.append('     "{}" 正确命名应为 "{}"'.format(k,v))
            return False, info.displayErrorInfo(title=self.error_info, objList=_error_list)
        else:
            return True, info.displayInfo(title=self.tooltip)

    def run(self):
        __error = {}
        if self.asset_type.lower() in ['role', 'body','npc']:
            mode_group_list = self._get_check_mod_group_list()
            if not mode_group_list:
                return None
            __meshs = self._get_meshs_from_group_list(mode_group_list)
            if not __meshs:
                return None
            ok, result = self.__get_error_data(__meshs)
            if not ok:
                return None
            __sg_error_dict, __shader_error_dict = result
            if __sg_error_dict:
                __error[u"以下SG节点命名不正确,请检查"] = __sg_error_dict
            if __shader_error_dict :
                __error[u"以下材质球节点命名不正确,请检查"] = __shader_error_dict
        return __error

    def _get_check_mod_group_list(self):
        structure_data = self._get_structure
        __grp_list = []
        if isinstance(structure_data, dict):
            for k, v in structure_data.items():
                if isinstance(v, list):
                    __grp_list.extend(v)
                if isinstance(v, str):
                    __grp_list.append(v)
        elif isinstance(structure_data, list):
            __grp_list = structure_data
        else:
            __grp_list = [structure_data]
        if __grp_list:
            __grp_list = list(set(__grp_list))
        return __grp_list

    def __get_error_data(self, meshs):

        __sg_error_dict={}
        __shader_error_dict = {}
        if not meshs:
            return False, (__sg_error_dict, __shader_error_dict)
        for mesh in meshs:
            tr=self._get_mesh_by_mesh_shape([mesh])
            if not tr:
                continue
            mesh_short=tr[0].split('|')[-1]
            sg_list = cmds.listConnections(mesh, type='shadingEngine')
            if not sg_list:
                continue
            sg=sg_list[0]
            if sg!='{}_mat_sg'.format(mesh_short):
                __sg_error_dict[sg]='{}_mat_sg'.format(mesh_short)
            shader_list = self._select_sg_surfaceshaderlist(sg)
            if not shader_list:
                continue
            shader=shader_list[0]
            shader_name='{}_mat'.format(mesh_short)
            if shader!=shader_name:
                __shader_error_dict[shader]=shader_name
        return True, (__sg_error_dict, __shader_error_dict )

    def _select_sg_surfaceshaderlist(self, sgname):
        _sgattrlist = ['{}.surfaceShader'.format(sgname), '{}.aiSurfaceShader'.format(sgname)]
        return [cmds.listConnections(i)[0] for i in _sgattrlist if (cmds.ls(i) and cmds.listConnections(i))]

    def _get_meshs_from_group_list(self, group_list):
        mesh_list = []
        for group in group_list:
            meshs = cmds.listRelatives(group, ad=1, type='mesh', f=1)
            if meshs:
                mesh_list.extend(meshs)
        if mesh_list:
            mesh_list = list(set(mesh_list))
        return mesh_list

    def _get_mesh_by_mesh_shape(self, mesh_shapes):
        if not mesh_shapes:
            return []
        __trs = []
        for mesh_shape in mesh_shapes:
            tr = cmds.listRelatives(mesh_shape, p=1, type='transform', f=1)
            if tr:
                __trs.append(tr[0])
        return __trs

    @property
    def _get_structure(self):
        u"""
        获取结构
        :return:
        """
        structure = self.structure
        if self.asset_type in ['body', 'cartoon_body']:
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

    def fix(self):
        errors = self.run()
        if errors:
            for k, v in errors.items():
                if k == u"以下材质球节点命名不正确,需要为'_mat'结尾":
                    shader_errors = v
                    for __shader_name in shader_errors:
                        __shader_name_new = self._get_fix_shade_name(__shader_name)
                        result = self.__rename(__shader_name, __shader_name_new)
                if k == u"以下SG节点命名不正确,需要为'_mat_sg'结尾":
                    sg_errors = v
                    for __sg_name in sg_errors:
                        __sg_name_new = self._get_fix_sg_name(__sg_name)
                        result = self.__rename(__sg_name, __sg_name_new)
        return True

    def __rename(self, source_name, target_name):
        try:
            cmds.rename(source_name, target_name)
            return True
        except:
            return False

    def _get_fix_sg_name(self, sg_name):
        __shaders = self._select_sg_surfaceshaderlist(sg_name)
        __sg_name_new = ''
        if __shaders:
            __shader_name = __shaders[0]
            __shader_pre_name = self.get_pre_name(__shader_name)
            if __shader_name.endswith('_mat'):
                __sg_name_new = '{}_sg'.format(__shader_name)
                if cmds.objExists(__sg_name_new):
                    count = 1
                    __sg_name_new = '{}_0{}_mat_sg'.format(__shader_pre_name, count)
                    if cmds.objExists(__sg_name_new):
                        while cmds.objExists(__sg_name_new):
                            count = count + 1
                            __sg_name_new = '{}_0{}_mat_sg'.format(__shader_pre_name, count)
                            if not cmds.objExists(__sg_name_new):
                                break
            else:
                count = 1
                __sg_name_new = '{}_0{}_mat_sg'.format(__shader_name, count)
                if cmds.objExists(__sg_name_new):
                    while cmds.objExists(__sg_name_new):
                        count = count + 1
                        __sg_name_new = '{}_0{}_mat_sg'.format(__shader_pre_name, count)
                        if not cmds.objExists(__sg_name_new):
                            break
        else:
            count = 1
            __sg_name_new = '{}_0{}_mat_sg'.format(self.entity_name, count)
            if cmds.objExists(__sg_name_new):
                while cmds.objExists(__sg_name_new):
                    count = count + 1
                    __sg_name_new = '{}_0{}_mat_sg'.format(self.entity_name, count)
                    if not cmds.objExists(__sg_name_new):
                        break
        return __sg_name_new

    def _get_fix_shade_name(self, shade_name):

        __end_name = shade_name.split('_')[-1]
        __info = shade_name.split('_')
        __shade_name_new = ''
        __pre_name = self.get_pre_name(shade_name)
        if 'mat' in __end_name and len(__info) > 1:
            __pre_name_new = self.get_pre_name(__pre_name)
            __sub_name = __info[-2]
            if self.is_valid_number(__sub_name):
                count = 1
                __sub_name_new = '0{}'.format(int(__sub_name) + count)
                __shade_name_new = '{}_{}_mat'.format(__pre_name_new, __sub_name_new)
                while cmds.objExists(__shade_name_new):
                    count = count + 1
                    __sub_name_new = '0{}'.format(int(__sub_name) + count)
                    __shade_name_new = '{}_{}_mat'.format(__pre_name_new, __sub_name_new)
                    if not cmds.objExists(__shade_name_new):
                        break
            else:
                count = 1
                __sub_name_new = '0{}'.format(count)
                __shade_name_new = '{}_{}_mat'.format(__pre_name_new, __sub_name_new)
                while cmds.objExists(__shade_name_new):
                    count = count + 1
                    __sub_name_new = '0{}'.format(count)
                    __shade_name_new = '{}_{}_mat'.format(__pre_name_new, __sub_name_new)
                    if not cmds.objExists(__shade_name_new):
                        break

        elif 'mat' in __end_name and len(__info) == 1:
            count = 1
            __end_name_new = '{}_0{}_mat'.format(__pre_name, count)
            if cmds.objExists(__end_name_new):
                while cmds.objExists(__end_name_new):
                    count = count + 1
                    __end_name_new = '{}_0{}_mat'.format(__pre_name, count)
                    if not cmds.objExists(__end_name_new):
                        break
        else:
            count = 1
            __shade_name_new = '{}_0{}_mat'.format(shade_name, count)
            if cmds.objExists(__shade_name_new):
                while cmds.objExists(__shade_name_new):
                    count = count + 1
                    __shade_name_new = '{}_0{}_mat'.format(__end_name, count)
                    if not cmds.objExists(__shade_name_new):
                        break
        return __shade_name_new

    def get_pre_name(self, name):
        info = name.split('_')
        pre_name = ''
        if len(info) > 1:
            info.pop(-1)
            for i in range(len(info)):
                if i == 0:
                    pre_name = info[i]
                else:
                    pre_name = pre_name + '_' + info[i]
        else:
            pre_name = info[0]
        return pre_name

    def is_valid_number(self, s):
        import re
        return re.match(r'[+-]?(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?', s) is not None



