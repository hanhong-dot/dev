# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       : check_exist_colo_set
# Describe   : 说明描述
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2024/1/24__15:54
# -------------------------------------------------------
import lib.common.loginfo as info
import maya.cmds as cmds

import lib.maya.node.grop as group_common

import lib.maya.analysis.analyze_config as analyze_config

reload(analyze_config)

import database.shotgun.fun.get_entity as get_entity

reload(get_entity)

import lib.maya.node.mesh as meshcommon

reload(meshcommon)
EXP = ['Cam', 'FX']
EXP_GRPS = ['NPC_*_split']


class Check(object):
    def __init__(self, TaskData):
        """
        实例初始化
        """
        # 即使直接派生自object，最好也调用一下super().__init__，
        # 不然可能造成多重继承时派生层次中某些类的__init__被跳过。
        super(Check, self).__init__()

        self._taskdata = TaskData
        # 信息

        self.asset_type = self._taskdata.asset_type

        self.entity_type = self._taskdata.entity_type

        self.tooltip = u'开始检测顶点颜色'
        self.no_color_set_error = u'以下模型没有顶点颜色,请检查'
        self.color_error = u'以下模型顶点颜色不正确,请检查(顶点颜色需要为全白)'

        self.end = u"已检测顶点数"

    def checkinfo(self):
        """
        显示检查信息
        :return:
        """
        _error = self.run()

        _error_list = []
        if _error:
            for k, v in _error.items():
                _error_list.append(k)
                _error_list.extend(v)
            return False, info.displayErrorInfo(title=self.tooltip, objList=_error_list)
        else:
            return True, info.displayInfo(title=self.tooltip, objList=[self.end])
    def run(self):
        u"""
        运行检测
        :return:
        """
        _error = {}
        _no_color_sets = []
        _color_errors = []
        if self.asset_type and self.asset_type in ['fx','cartoon_fx']:
            _meshs = self._get_meshs()
        else:
            _meshs = self._get_fx_meshs()
        if _meshs:
            for _mesh in _meshs:
                _color_set = meshcommon.Mesh(_mesh).ColorSetNames
                if not _color_set:
                    cmds.select(_mesh)
                    cmds.polyColorSet(create=True, colorSet='{}_colorSet'.format(_mesh))
                    cmds.polyColorPerVertex(rgb=[1, 1, 1], cdo=True)
                else:
                    cmds.select(_mesh)
                    cmds.polyColorPerVertex(rgb=[1, 1, 1], cdo=True)
        return

    def _select_meshs_color_set(self, _meshs):
        u"""
        获得列表模型的顶点颜色
        :param _meshs:
        :return:
        """
        _num = 0
        if _meshs:
            for i in range(len(_meshs)):
                if i == 0:
                    _num = meshcommon.Mesh(_meshs[i]).numVertices
                else:
                    _num = _num + meshcommon.Mesh(_meshs[i]).numVertices
        return _num

    def _get_meshs(self):
        u"""
        获取所有模型
        :param _grps:
        :return:
        """

        trs = []
        _meshs = cmds.ls(type='mesh', l=1)
        for i in range(len(_meshs)):
            tr = cmds.listRelatives(_meshs[i], p=1, type='transform', f=1)
            if tr and tr[0] not in trs:
                trs.append(tr[0])

        return trs

    def _get_fx_meshs(self):
        __meshs=self._get_meshs()
        __fx_meshs=[]
        for _mesh in __meshs:
            if _mesh.endswith('_fx') or _mesh.endswith('_FX'):
                __fx_meshs.append(_mesh)
        return __fx_meshs

    def fix(self):
        u"""
        修复
        :return:
        """
        _error = self.run()
        if _error:
            for k, v in _error.items():
                if k==self.no_color_set_error:
                    if not v:
                        continue
                    for _mesh in v:
                        cmds.select(_mesh)
                        cmds.polyColorSet(create=True, colorSet='{}_colorSet'.format(_mesh))
                        cmds.polyColorPerVertex(rgb=[1, 1, 1], cdo=True)
                elif k==self.color_error:

                    if not v:
                        continue
                    for _mesh in v:
                        cmds.select(_mesh)
                        cmds.polyColorPerVertex(rgb=[1, 1, 1], cdo=True)




