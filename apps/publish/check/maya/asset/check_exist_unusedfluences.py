# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       : check_exist_unusedfluences
# Describe   : 说明描述
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2022/7/15__11:33
# -------------------------------------------------------
import maya.cmds as cmds
import maya.mel as mel

import method.maya.common.file as filecommon
import lib.maya.node.grop as groupcommon
import lib.common.loginfo as info

import method.maya.common.file as filecommon
class Check(object):
    u"""
    检查文件中是否存在需要清理的节点
    """

    def __init__(self, task_data):
        u"""
        检测未影响的骨骼
        Args:
            task_data: 任务信息
        """
        super(Check, self).__init__()
        self._taskdata = task_data
        # 资产类型
        self._asset_type = self._taskdata.asset_type
        # 资产名
        self._asset_name = self._taskdata.entity_name

        self.tooltip = u'已检测文件中的未影响骨骼'

    def checkinfo(self):
        """
        显示检查信息
        :return:
        """
        # 这个检测实际是修复
        _error = self.run()
        # _error_list = []
        # if _error:
        #     _error_list.append(u"以下模型为重叠模型，请检查")
        #     _error_list.extend(_error)
        #     return False, info.displayErrorInfo(title=self.tooltip, objList=_error_list)
        # else:
        return True, info.displayInfo(title=self.tooltip)

    def run(self):

        """
        检查关键帧
        :return:
        """
        _check_grps = self._get_check_grou()
        if _check_grps:
            _check_meshs = self._get_meshs(_check_grps)
            if _check_meshs:
                for _mesh in _check_meshs:

                    try:
                        cmds.select(_mesh)
                        mel.eval('removeUnusedInfluences()')
                    except:
                        pass

    @property
    def ref_info(self):
        u"""
        参考信息
        Returns:

        """
        return filecommon.BaseFile().reference_info_dict()


    def _check_unusefluences(self, _meshs):
        u"""
        检测
        Args:
            _meshs:

        Returns:

        """

    def _get_check_grou(self):
        u"""
        需要检测的大组
        Returns:

        """
        if self.ref_info:
            _grps = cmds.ls('*_Rig')
        else:
            _grps = cmds.ls(['{}_HD'.format(self._asset_name), '{}_LD'.format(self._asset_name)])
        return _grps


    def _get_meshs(self, _grps):
        u"""
        获得组下所有模型节点
        Args:
            _grps:

        Returns:

        """
        _meshs = []
        if _grps:
            for _gr in _grps:
                if _gr and cmds.ls(_gr):
                    _mesh = groupcommon.Group(_gr).select_group_meshs()
                    if _mesh:
                        _meshs.extend(_mesh)
        return _meshs



    def fix(self):
        """
        修复相关内容
        :return:
        """
        pass
