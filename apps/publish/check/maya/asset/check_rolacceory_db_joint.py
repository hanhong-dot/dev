# -*- coding: utf-8 -*-
# author: linhuan
# file: check_rolacceory_db_joint.py
# time: 2025/12/26 15:27
# description:
import maya.cmds as cmds
import lib.common.loginfo as info

import database.shotgun.core.sg_analysis as sg_analysis


#


class Check(object):

    def __init__(self, TaskData):
        super(Check, self).__init__()

        self._taskdata = TaskData
        self.__entity_type = self._taskdata.entity_type
        self.__entity_id = self._taskdata.entity_id
        self.__entity_name = self._taskdata.entity_name
        self.__task_id = self._taskdata.task_id
        self._asset_type = self._taskdata.asset_type
        self.__sg = sg_analysis.Config().login()
        self.__tooltip = u'开始检测配饰是否有DB骨骼(DB参数)'
        self.__err = u"缺少DB骨骼(DB参数),请检查"
        self.__end = u'已检测配饰是否有DB骨骼(DB参数)'

    def checkinfo(self):
        __errors = self.run()
        if __errors:
            return False, info.displayErrorInfo(title=self.__err, objList=__errors)
        else:
            return True, info.displayInfo(title=self.__tooltip, objList=[self.__end])

    def run(self):
        __error = []
        if self._asset_type not in ['rolaccesory']:
            return __error
        __task_text = self._get_task_text()
        if u'DB参数' not in __task_text:
            return __error
        __result = self.__check_exist_db_joint()
        if not __result:
            __error.append('缺少DB骨骼(DB参数)')
        return __error

    def _get_task_text(self):
        fields = ['sg_text']
        filters = [
            ['id', 'is', self.__task_id]
        ]
        task = self.__sg.find_one('Task', filters, fields)
        if task and 'sg_text' in task:
            return u'{}'.format(task['sg_text'])
        return ''

    def __check_exist_db_joint(self):
        db_joins = self.__get_db_joints()
        if not db_joins:
            return False
        return True

    def __get_db_joints(self):
        db_joints = []
        joints = cmds.ls(type='joint')
        if not joints:
            return db_joints
        for joint in joints:
            short_name = joint.split('|')[-1]
            is_ref = cmds.referenceQuery(joint, inr=True)
            if short_name.startswith('DB_') and is_ref != True:
                db_joints.append(joint)
        return db_joints


if __name__ == '__main__':
    import method.shotgun.get_task as get_task

    _filename = cmds.file(q=1, exn=1)

    taskdata = get_task.TaskInfo(_filename, 'X3', 'maya', 'version')
    handle = Check(taskdata)

    print(handle.run())
