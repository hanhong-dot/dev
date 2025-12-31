# -*- coding: utf-8 -*-
# author: linhuan
# file: check_rolaccesory_ap_joint.py
# time: 2025/12/30 19:49
# description:
# -*- coding: utf-8 -*-
# author: linhuan
# file: check_pl_head_joint_weight.py
# time: 2025/12/24 18:45
# description:
import maya.cmds as cmds
import lib.common.loginfo as info
import lib.maya.analysis.analyze_structure as structure

reload(structure)
import database.shotgun.fun.get_entity as get_entity
import database.shotgun.core.sg_analysis as sg_analysis

reload(get_entity)
#

PARENTJOINT = 'Head_M_spare'


class Check(object):

    def __init__(self, TaskData):
        super(Check, self).__init__()

        self.__TaskData = TaskData
        self.__entity_type = self.__TaskData.entity_type
        self.__entity_id = self.__TaskData.entity_id
        self.__entity_name = self.__TaskData.entity_name
        self.__task_id = self.__TaskData.task_id
        self.__asset_type = self.__TaskData.asset_type
        self.__sg = sg_analysis.Config().login()
        self.__tooltip = u'开始检测配饰【AP拆分】骨骼'
        self.__err = u"以配饰【AP拆分】骨骼，有以下问题，请检查"
        self.__end = u'已检测配饰【AP拆分】骨骼'

    def checkinfo(self):
        __errors = self.run()
        __error_list = []
        if __errors:
            for k, v in __errors.items():
                __error_list.append(k)
                __error_list.extend(v)
        if __errors:
            return False, info.displayErrorInfo(title=self.__err, objList=__error_list)
        else:
            return True, info.displayInfo(title=self.__tooltip, objList=[self.__end])

    def run(self):
        __error = {}
        __not_exit_errors = []
        __db_empty_errors = []
        if self.__asset_type not in ['rolaccesory']:
            return __error
        __task_text = self._get_task_text()
        if u'AP拆分' not in __task_text:
            return __error
        __jnt = 'AP_{}_jnt'.format(self.__entity_name)
        __collider_jnt = 'AP_{}_Collider_jnt'.format(self.__entity_name)
        __db_jnt = 'AP_{}_DB_jnt'.format(self.__entity_name)
        if not cmds.ls(__jnt):
            __not_exit_errors.append(__jnt)
        if not cmds.ls(__collider_jnt):
            __not_exit_errors.append(__collider_jnt)
        if not cmds.ls(__db_jnt):
            __not_exit_errors.append(__db_jnt)
        if cmds.ls(__db_jnt):
            __child_joints = self.__get_all_child_joints(__db_jnt)
            if not __child_joints:
                __db_empty_errors.append(u'{}没有子骨骼'.format(__db_jnt))
            else:
                result = False
                for _joint in __child_joints:
                    joint_short = _joint.split('|')[-1]
                    if joint_short.startswith('DB_'):
                        result = True
                        break
                if not result:
                    __db_empty_errors.append(u'{}的子骨骼没有以DB_开头的骨骼'.format(__db_jnt))
        if __not_exit_errors:
            __error[u'缺少以下骨骼:'] = __not_exit_errors
        if __db_empty_errors:
            __error[u'DB骨骼存在以下问题:'] = __db_empty_errors
        return __error

    def __get_all_child_joints(self, parent_joint):
        __joints = []
        if not cmds.ls(parent_joint):
            return __joints
        __ch_joins = cmds.listRelatives(parent_joint, ad=1, type='joint', f=1)
        if __ch_joins:
            __joints.extend(__ch_joins)
        if __joints:
            __joints = list(set(__joints))
        return __joints

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
        task = self.__sg.find_one('Task', filters, fields)
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


