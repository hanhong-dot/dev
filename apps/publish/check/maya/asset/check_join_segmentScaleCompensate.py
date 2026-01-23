# -*- coding: utf-8 -*-
# author: linhuan
# file: check_join_segmentScaleCompensate.py
# time: 2026/1/23 10:52
# description:
import lib.common.loginfo as info
import maya.cmds as cmds


class Check(object):
    def __init__(self, TaskData):
        self.task_data = TaskData
        self.asset_type = self.task_data.asset_type
        self.tooltip = u'开始检测item骨骼分段补偿属性'
        self.tooltip_error = u'以下骨骼segmentScaleCompensate属性未关闭'
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
        __is_errors = []
        if self.asset_type not in ['item']:
            return __is_errors
        __is_errors = self.__check_joins_segmentScaleCompensate()
        return __is_errors

    def __check_joins_segmentScaleCompensate(self):
        __is_errors = []
        all_joints = self.get_all_joints()
        if not all_joints:
            return __is_errors
        for joint in all_joints:
            is_segmentScaleCompensate = self.__check_is_segmentScaleCompensate(joint)
            if is_segmentScaleCompensate:
                __is_errors.append(joint)
        if __is_errors:
            __is_errors = list(set(__is_errors))
        return __is_errors

    def get_all_joints(self):
        all_joints = cmds.ls(type='joint', l=1)
        return all_joints

    def __check_is_segmentScaleCompensate(self, _joint):
        is_segmentScaleCompensate = cmds.getAttr(_joint + '.segmentScaleCompensate')
        return is_segmentScaleCompensate

if __name__ == '__main__':
    import method.shotgun.get_task as get_task

    import maya.cmds as cmds
    _filename = cmds.file(q=1, exn=1)

    test_task_data = get_task.TaskInfo(_filename, 'X3', 'maya', 'publish')
    _handle = Check(test_task_data)
    print(_handle.run())