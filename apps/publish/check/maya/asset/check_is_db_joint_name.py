# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       :
# Describe   :
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2024/10/24__10:33
# -------------------------------------------------------

import lib.common.loginfo as _info

reload(_info)

import maya.cmds as cmds

class Check(object):

    def __init__(self, TaskData):
        super(Check, self).__init__()
        self.__taskdata = TaskData
        self.__entity_name = TaskData.entity_name
        self.__pre_name=self.__entity_name.split('_')[0]
        self.__assettype = TaskData.asset_type
        self.__task_name = TaskData.task_name

        self.tooltip = u'已检测db骨骼命名'
        self.errortip = u"以下db骨骼命名不正确,请检查"

    def checkinfo(self):
        """
        显示检查信息
        :return:
        """
        _error = self.run()
        if _error:
            return False, _info.displayErrorInfo(title=self.errortip, objList=_error)
        else:
            return True, _info.displayInfo(title=self.tooltip)

    def run(self):
        if self.__assettype in ['role','roleacessry']:
            return self.__check_db_joint_name()

    def fix(self):
        _error=self.run()
        if _error:
            fix_errors=self.__rename_db_joint(_error)
            if fix_errors:
                return False, _info.displayErrorInfo(title=u'以下db骨骼命名修复失败,请检查', objList=fix_errors)

    def __get_db_joints(self):
        db_joints = []
        joints = cmds.ls(type='joint')
        if not joints:
            return db_joints
        for joint in joints:
            short_name = joint.split('|')[-1]
            is_ref=cmds.referenceQuery(joint,inr=True)
            if short_name.startswith('DB_') and is_ref!=True:
                db_joints.append(joint)
        return db_joints

    def __check_db_joint_name(self):
        db_joints = self.__get_db_joints()
        error_list = []
        for db_joint in db_joints:
            if not db_joint.startswith('DB_{}_'.format(self.__pre_name)):
                error_list.append(db_joint)
        return error_list

    def __rename_db_joint(self, db_joints):
        if not db_joints:
            return
        errors=[]
        for db_joint in db_joints:
            short_name = db_joint.split('|')[-1]
            last_name=short_name.split('DB_')[-1]
            new_name = 'DB_{}_{}'.format(self.__pre_name,last_name)


            try:
                cmds.rename(short_name, new_name)
            except:
                cmds.lockNode(db_joint, lock=False)
                try:
                    cmds.rename(short_name, new_name)
                except:
                    errors.append(short_name)
        return errors

