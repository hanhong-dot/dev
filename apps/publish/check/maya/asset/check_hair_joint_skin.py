# -*- coding: utf-8 -*-
# -----------------------------------
# @File    : check_hair_joint_skin.py
# @Author  : linhuan
# @Time    : 2025/8/1 11:01
# @Description : 
# -----------------------------------
import maya.cmds as cmds
import lib.common.loginfo as info

CHECK_JOINT_LIST = ['Head_rivet_M_4', 'Head_rivet_M_7', 'Head_rivet_R_0', 'Head_rivet_L_0', 'Head_rivet_L_1',
                    'Head_rivet_R_1', 'Head_rivet_L_42', 'Head_rivet_R_42']


class Check(object):
    def __init__(self, TaskData):
        super(Check, self).__init__()
        self._taskdata = TaskData
        self._asset_type = self._taskdata.asset_type
        self._entity_name = self._taskdata.entity_name
        self.tooltip = u'检测PL女主头发跟随头皮检测'
        self.end = u'检测完成'
        self._err = u'请检查以下骨骼,均与头发模型没有有效蒙皮'

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
        if self._asset_type.lower() == 'hair' and (self._entity_name.startswith('PL') or self._entity_name.startswith('pl') or self._entity_name.startswith('Pl')):
            return self.check_hair_joint_skin()

    def check_hair_joint_skin(self):
        """
        检测头发骨骼是否绑定到头皮上
        :return:
        """

        _no_empty_joints = []
        hair_meshs = self.get_hair_meshs()
        if not hair_meshs:
            return

        for joint in CHECK_JOINT_LIST:
            if not cmds.objExists(joint):
                continue
            __judge_result = self._judge_empty_joint(joint, hair_meshs)
            if __judge_result:
                _no_empty_joints.append(joint)

        if not _no_empty_joints:

            return CHECK_JOINT_LIST

        else:
            return

    def get_hair_model_group(self):
        """
        获取头发模型组
        :return: 头发模型组名称
        """
        hair_model_group = '{}_HD'.format(self._entity_name)
        if cmds.objExists(hair_model_group):
            return hair_model_group
        else:
            return None

    def get_hair_meshs(self):
        """
        获取头发模型
        :return: 头发模型列表
        """
        hair_model_group = self.get_hair_model_group()
        if not hair_model_group:
            return []

        hair_meshs = cmds.listRelatives(hair_model_group, ad=True, type='mesh')
        if not hair_meshs:
            return []

        return hair_meshs

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


# if __name__ == '__main__':
#     # 测试代码
#     import method.shotgun.get_task as get_task
#
#     reload(get_task)
#     _filename = cmds.file(q=1, exn=1)
#
#     test_task_data = get_task.TaskInfo(_filename, 'X3', 'maya', 'publish')
#     _handle = Check(test_task_data)
#     print(_handle.run())
