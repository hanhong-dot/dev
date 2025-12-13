# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       :
# Describe   :
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2024/6/13__17:52
# -------------------------------------------------------
import lib.common.loginfo as info
import maya.cmds as cmds

EXP_NAME = ['speakBorder', 'Face_Root_Ctl']
SET_NAME = ['ControlSet']

import lib.maya.node.grop as group_common


class Check(object):
    """
    检查控制器是否归零
    """

    def __init__(self):

        super(Check, self).__init__()

        self.tooltip = u'已检测控制器是否归零'

    def checkinfo(self):
        """
        显示检查信息
        :return:
        """
        _error = self.run()
        _error_list = []
        if _error:
            _error_list.append(u"以下控制器未归零,请检查")
            _error_list.extend(_error)
            return False, info.displayErrorInfo(title=self.tooltip, objList=_error_list)
        else:
            return True, info.displayInfo(title=self.tooltip)

    def run(self):

        """
        检查关键帧
        :return:
        """
        error = []
        _sets=[]
        for setname in SET_NAME:
            if cmds.objExists(setname):
                _sets.append(setname)
        if not _sets:
            return
        ctrls = cmds.sets(_sets, q=True)
        if not ctrls:
            return

        # ctrls = cmds.ls(type='nurbsCurve')

        # ctrl_trs = self._get_trs(ctrls)
        # if ctrl_trs:
        #     ctrl_trs = list(set(ctrl_trs))
        # if not ctrl_trs:
        #     return
        ctrl_trs= self._get_ctrls(ctrls)
        if not ctrl_trs:
            return
        for ctrl in ctrl_trs:
            if self._judge_ctrl(ctrl) == True:
                for attr in ['tx', 'ty', 'tz', 'rx', 'ry', 'rz']:
                    if self._judge_attr(ctrl, attr) == True:
                        value = cmds.getAttr(ctrl + '.' + attr)
                        if value != 0.0:
                            error.append(ctrl)
                for attr in ['sx', 'sy', 'sz']:
                    if self._judge_attr(ctrl, attr) == True:
                        value = cmds.getAttr(ctrl + '.' + attr)
                        if value != 1.0:
                            error.append(ctrl)
        if error:
            return list(set(error))

    def _get_ctrls(self,ctrls):
        _ctrls = []
        if not ctrls:
            return
        for ctrl in ctrls:
            if cmds.objExists(ctrl)  and cmds.listRelatives(ctrl, s=True, type='nurbsCurve'):
                _ctrls.append(ctrl)
        return _ctrls

    def _judge_ctrl(self, ctrl):
        if cmds.objExists(ctrl) and ctrl.split('|')[-1] not in EXP_NAME:
            return True
        else:
            return False

    def _judge_attr(self, ctrl, attr):
        _attr = '{}.{}'.format(ctrl, attr)
        vis = cmds.getAttr(_attr, k=True)
        if vis == True:
            cons = cmds.listConnections(_attr, s=1)
            if cons:
                return False
        else:
            return False
        lock = cmds.getAttr(_attr, lock=True)
        if lock == True:
            return False
        if attr in ['tx', 'ty', 'tz']:
            cons = cmds.listConnections('{}.translate'.format(ctrl), s=1)
            if cons:
                return False
        if attr in ['rx', 'ry', 'rz']:
            cons = cmds.listConnections('{}.rotate'.format(ctrl), s=1)
            if cons:
                return False
        if attr in ['sx', 'sy', 'sz']:
            cons = cmds.listConnections('{}.scale'.format(ctrl), s=1)
            if cons:
                return False

        return True

    def fix(self):
        """
        修复相关内容
        :return:
        """
        _errors = self.run()
        if _errors:
            for _err in _errors:
                self._set_attr(_err)
        # _errors_01 = self.run()
        # if _errors_01:
        #     for _err in _errors_01:
        #         self._set_attr(_err)





    def _ctrl_freeze(self,ctrl):
        tr_error=False
        for attr in ['tx', 'ty', 'tz']:
            if self._judge_attr(ctrl, attr) == True and cmds.getAttr(ctrl + '.' + attr) != 0.0:
                tr_error=True
                break
        if tr_error:
            try:
                cmds.makeIdentity(ctrl, apply=True, t=1)
            except:
                pass
        ro_error=False
        for attr in ['rx', 'ry', 'rz']:
            if self._judge_attr(ctrl, attr) == True and cmds.getAttr(ctrl + '.' + attr) != 0.0:
                ro_error=True
                break
        if ro_error:
            try:
                cmds.makeIdentity(ctrl, apply=True, r=1)
            except:
                pass
        sc_error=False
        for attr in ['sx', 'sy', 'sz']:
            if self._judge_attr(ctrl, attr) == True and cmds.getAttr(ctrl + '.' + attr) != 1.0:
                sc_error=True
                break
        if sc_error:
            try:
                cmds.makeIdentity(ctrl, apply=True, s=1)
            except:
                pass








    def _set_attr(self,ctrl):
        for attr in ['tx', 'ty', 'tz', 'rx', 'ry', 'rz']:
            if self._judge_attr(ctrl, attr) == True:
                try:
                    cmds.setAttr(ctrl + '.' + attr, 0)
                except:
                    pass
        for attr in ['sx', 'sy', 'sz']:
            if self._judge_attr(ctrl, attr) == True:
                try:
                    cmds.setAttr(ctrl + '.' + attr, 1.0)
                except:
                    pass


    def _get_trs(self, ctrls):
        trs = []
        for ctrl in ctrls:
            if cmds.objExists(ctrl):
                tr = cmds.listRelatives(ctrl, p=True, type='transform')
                if tr:
                    trs.extend(tr)
        return trs
