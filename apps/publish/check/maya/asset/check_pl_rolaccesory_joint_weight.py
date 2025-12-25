# -*- coding: utf-8 -*-
# author: linhuan
# file: check_pl_head_joint_weight.py
# time: 2025/12/24 18:45
# description:
import maya.cmds as cmds
import lib.common.loginfo as info
import lib.maya.analysis.analyze_structure as structure

reload(structure)

# import lib.maya.analysis.analyze_structure as structure
#
# reload(structure)

import database.shotgun.fun.get_entity as get_entity
import database.shotgun.core.sg_analysis as sg_analysis

reload(get_entity)
#

PARENTJOINT = 'Head_M_spare'


class Check(object):

    def __init__(self, TaskData):
        super(Check, self).__init__()

        self._taskdata = TaskData
        self.__entity_type = self._taskdata.entity_type
        self.__entity_id = self._taskdata.entity_id
        self.__entity_name = self._taskdata.entity_name
        self.__task_id= self._taskdata.task_id
        self._asset_type = self._taskdata.asset_type
        self.__sg = sg_analysis.Config().login()
        self._asset_level = get_entity.BaseGetSgInfo(self.__sg, self.__entity_id, self.__entity_type).get_asset_level()
        self.analyze_handle = structure.AnalyStrue(self._taskdata)
        self.structure = self.analyze_handle.get_structure()
        self._structure = self._get_structure
        self.__tooltip = u'开始检测pl配饰骨骼权重'
        self.__err = u"以下骨骼与女主模型没有有效蒙皮权重,请检查"
        self.__end = u'已检测pl配饰骨骼权重'

    def checkinfo(self):
        __errors = self.run()
        if __errors:
            return False, info.displayErrorInfo(title=self.__err, objList=__errors)
        else:
            return True, info.displayInfo(title=self.__tooltip, objList=[self.__end])

    def run(self):
        __error_joints = []
        if self._asset_type not in ['rolaccesory']:
            return __error_joints
        __task_text = self._get_task_text()
        if u'PL捏脸' not in __task_text:
            return __error_joints
        mod_grps_meshs = self._get_mod_grps_meshs()
        if not mod_grps_meshs:
            return __error_joints
        all_joints = self._get_all_joints_parent_joint()
        if not all_joints:
            return __error_joints
        for joint in all_joints:
            if not self._judge_empty_joint(joint, mod_grps_meshs):
                __error_joints.append(joint)
        return __error_joints

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

    def _get_task_text(self):
        fields = ['sg_text']
        filters = [
            ['id', 'is', self.__task_id]
        ]
        task= self.__sg.find_one('Task', filters, fields)
        if task and 'sg_text' in task:
            return u'{}'.format(task['sg_text'])
        return ''



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

    def _get_grps_structure(self, structure):
        mod_grps = []
        if isinstance(structure, dict):
            for k, v in structure.items():
                k = cmds.ls(k)
                if not k:
                    continue
                k = k[0]
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


# if __name__ == '__main__':
#     import method.shotgun.get_task as get_task
#
#     _filename = 'P202HE.drama_rig.001.ma'
#
#     taskdata = get_task.TaskInfo(_filename, 'X3', 'maya', 'version')
#     handle = Check(taskdata)
#
#     print(handle.run())
