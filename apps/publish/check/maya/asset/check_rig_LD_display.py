# -*- coding: utf-8 -*-
# author: linhuan
# file: check_rig_LD_display.py
# time: 2026/3/4 18:57
# description:

import lib.common.loginfo as info
import maya.cmds as cmds


class Check(object):

    def __init__(self, TaskData):
        super(Check, self).__init__()

        self._taskdata = TaskData
        self.__entity_type = self._taskdata.entity_type
        self.__entity_id = self._taskdata.entity_id
        self.__entity_name = self._taskdata.entity_name
        self.__task_id = self._taskdata.task_id
        self._asset_type = self._taskdata.asset_type
        self.__tooltip = u'开始检测套装LD模型组显示'
        self.__err = u"以下LD模型组没有隐藏,请检查"
        self.__end = u'已检测套装LD模型组显示'

    def checkinfo(self):
        __errors = self.run()
        if __errors:
            return False, info.displayErrorInfo(title=self.__err, objList=__errors)
        else:
            return True, info.displayInfo(title=self.__tooltip, objList=[self.__end])

    def run(self):
        __error = []
        if self._asset_type not in ['role']:
            return __error
        __rig_group = self.__get_rig_group()
        if not __rig_group:
            return __error
        __all_ld_groups = self.__get_all_ld_groups(__rig_group)
        if not __all_ld_groups:
            return __error
        for ld_group in __all_ld_groups:
            if cmds.getAttr('{}.v'.format(ld_group)):
                __error.append(ld_group)
        return __error

    def __get_rig_group(self):
        rig_group = cmds.ls('*_Rig', type='transform')
        if rig_group:
            return rig_group[0]
        return None

    def __get_all_ld_groups(self, rig_group):
        all_ld_groups = []
        children = cmds.listRelatives(rig_group, c=True, type='transform') or []
        if not children:
            return all_ld_groups
        for child in children:
            if child.endswith('_LD'):
                all_ld_groups.append(child)
        return all_ld_groups

    def fix(self):
        __errors= self.run()
        if not __errors:
            return
        for error in __errors:
            cmds.setAttr('{}.v'.format(error), 0)

