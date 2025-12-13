# -*- coding: utf-8 -*-#
# Python     : 
# -------------------------------------------------------
# NAME       : check_exist_ap_joint
# Describe   : 检测AP关节是否存在
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2025/4/15__17:20
# -------------------------------------------------------
import maya.cmds as cmds

import lib.common.loginfo as info

AP_JOINS = ["AP_Face_Glass", "AP_Face_Mask", "AP_Face_Dec_L", "AP_Face_Dec_R", "AP_Face_Dot_L", "AP_Face_Dot_R"]
rolaccesory_AP_JOINS = ["AP_Face_Mask", "AP_Face_Dec_L", "AP_Face_Dec_R", "AP_Face_Dot_L", "AP_Face_Dot_R"]

ASSET_TYPES = ['role', 'rolaccesory']
EXCLUDE_ASSETS = ['PL015S', 'PL013S', 'PL026C', 'PL062C']

INCLUDEGRPS = ['{Entity}_HD', '{Entity}_LD']

import maya.cmds as cmds
import lib.common.loginfo as info
import lib.maya.analysis.analyze_structure as structure

reload(structure)

import database.shotgun.fun.get_entity as get_entity

reload(get_entity)

import database.shotgun.core.sg_analysis as sg_analysis

SETS = ['FkSdkJointSet']


class Check(object):
    """
    检查资产文件结构（以后按配置文件来查)
    """

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
        self._errortip = u"文件中有以下AP命名骨骼有蒙皮,请检查"
        self._tooltip = u'已检查文件中是否存在AP命名骨骼有蒙皮'

    def checkinfo(self):
        _error = self.run()
        if _error:
            _error_list = _error
            return False, info.displayErrorInfo(title=self._errortip, objList=_error_list)
        else:
            return True, info.displayInfo(title=self._tooltip)

    def run(self):
        if self.asset_type and self.asset_type not in ASSET_TYPES:
            return []
        if self.entity_name in EXCLUDE_ASSETS:
            return []

        __error_joins = []
        __meshs = self.__get_mod_grps_meshs()
        if not __meshs:
            return []
        if self.asset_type == 'rolaccesory':
            check_joins = rolaccesory_AP_JOINS
        else:
            check_joins = AP_JOINS
        for __joint in check_joins:
            if cmds.ls(__joint):
                __result = self.__judge_skin_joint(__joint, __meshs)
                if __result:
                    __error_joins.append(__joint)
        return __error_joins

    @property
    def _get_structure(self):
        u"""
        获取结构
        :return:
        """
        structure = self.structure

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

    def __judge_skin_joint(self, joint, meshs):
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

    def __get_mod_grps_meshs(self):
        mesh_list = []
        mod_grps = self._get_grps_structure(self._structure)
        mod_grps = self.__get_grps_from_include(mod_grps)

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

    def __get_include_grps(self):
        include_grps = []

        for grp_pattern in INCLUDEGRPS:
            grp_name = grp_pattern.format(Entity=self.entity_name)
            include_grps.append(grp_name)
        if include_grps:
            return list(set(include_grps))
        else:
            return []

    def __get_grps_from_include(self, grps):
        mod_grps = []
        include_grps = self.__get_include_grps()
        for grp in grps:
            if grp.split('|')[-1] in include_grps:
                mod_grps.append(grp)
        return mod_grps

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

# if __name__ == '__main__':
#     # 测试代码
#     import method.shotgun.get_task as get_task
#
#     reload(get_task)
#     _filename = cmds.file(q=1, exn=1)
#
#     test_task_data = get_task.TaskInfo(_filename, 'X3', 'maya', 'publish')
#     #     #
#     #     #     # print test_task_data.project_soft
#     _handle = Check(test_task_data)
#     objs = _handle.run()
