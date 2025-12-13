# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       : check_rig_bstarge
# Describe   : 检测绑定文件中bs target list,如果list内关键字有Finger的target,则报错
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2023/3/28__16:24
# -------------------------------------------------------
KEYNAME = 'Finger'
import maya.cmds as cmds
import lib.common.loginfo as info
from adPose2_FKSdk.adPose2.ADPose import ADPoses

from adPose2_FKSdk import tools

from adPose2_FKSdk import get_bs_info
import apps.publish.process.maya.process_bs_export as process_bs_export
reload(process_bs_export)


class Check(object):

    def __init__(self, TaskData):
        super(Check, self).__init__()
        self._asset_type = TaskData.asset_type
        self._task_name = TaskData.task_name
        self.TaskData = TaskData
        self._tooltip_error = u'以下BS节点,targelist有"Finger"关键字,请检查'
        self._tooltip_true = u'已检测绑定文件中bs target list'

    def checkinfo(self):
        _error = self.run()
        _error_list = []
        if _error:
            _error_list.extend(_error)
            return False, info.displayErrorInfo(title=self._tooltip_error, objList=_error_list)
        else:
            return True, info.displayInfo(title=self._tooltip_true)

    def run(self):
        if self._asset_type in ['role','cartoon_role'] and self._task_name in ['rbf', 'drama_rig']:
            return self.get_key_targetlist()

    def get_key_targetlist(self):
        u"""
        :return:
        """
        _target_dict = self.get_targetlist()
        _key_list = []
        if _target_dict:
            for k,v in _target_dict.items():
                for _target in v:
                    if KEYNAME in _target:
                        _key_list.append(k)
        if _key_list:
            return list(set(_key_list))

    def get_targetlist(self):
        u"""
        :return:
        """
        import maya.cmds as cmds
        _dict={}
        _target_list = []
        _handle = process_bs_export.PorcessBsExport(self.TaskData)
        _objs_file_dict = _handle._get_objs_file_dict()
        if _objs_file_dict:
            for k, v in _objs_file_dict.items():
                if '_Render' not in k:
                    _meshs,_bs_objs= _handle._selet_objs_bs(v)
                    if _bs_objs:
                        _bs_dict= self._get_targes(_bs_objs)
                        if _bs_dict:
                            _dict.update(_bs_dict)
        return _dict


    def _get_targes(self, bsobjs):
        u"""

        :param bsobjs: bs 物体列表
        :return:
        """
        if not bsobjs:
            return
        cmds.select(cl=1)
        cmds.select(bsobjs)
        all_targets = ADPoses.get_targets() + tools.get_twist_targets()
        bsMeshs_path_list, bs_nodes = get_bs_info.get_bsMeshs_list(all_targets, False)
        _dict={}
        for bs_node in bs_nodes:
            targets = []
            for target in all_targets:
                if bs_node.hasAttr(target) and target in bs_node.weight.elements():
                    targets.append(target)
            if targets:
                _dict[bs_node.name()] = targets
        return _dict


if __name__ == '__main__':
    import method.shotgun.get_task as get_task

    _filename = cmds.file(q=1, exn=1)

    TaskData_Class = get_task.TaskInfo(_filename, 'X3', 'maya', 'publish')
    print(Check(TaskData_Class).run())
