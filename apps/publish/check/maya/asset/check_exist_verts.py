# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       : check_exist_verts
# Describe   : 说明描述
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2023/3/8__16:01
# -------------------------------------------------------
import lib.common.loginfo as info
import maya.cmds as cmds

import lib.maya.node.grop as group_common

import lib.maya.analysis.analyze_config as analyze_config

reload(analyze_config)

import database.shotgun.fun.get_entity as get_entity

reload(get_entity)

import database.shotgun.core.sg_analysis as sg_analysis

import lib.maya.node.mesh as meshcommon

reload(meshcommon)
EXP = ['Cam', 'FX']
EXP_GRPS = ['NPC_*_split']


class Check(object):
    """
    检查资产文件结构（以后按配置文件来查)
    """

    def __init__(self, TaskData):
        """
        实例初始化
        """
        # 即使直接派生自object，最好也调用一下super().__init__，
        # 不然可能造成多重继承时派生层次中某些类的__init__被跳过。
        super(Check, self).__init__()

        self._taskdata = TaskData
        # 信息
        self.verts = analyze_config.AnalyDatas(self._taskdata, configfile="maya_verts.json", dcc="maya").get_datas()
        self.entity_name = self._taskdata.entity_name

        self.entity_type = self._taskdata.entity_type
        self.entity_id = self._taskdata.entity_id
        self.step_name = self._taskdata.step_name
        self.sg = sg_analysis.Config().login()
        self._asset_level = get_entity.BaseGetSgInfo(self.sg, self.entity_id, self.entity_type).get_asset_level()

        self.tooltip = u'开始检测顶点数'
        self._info_err = u'缺少max顶点数配置信息,请联系TD'
        self._all_max_err = u"文件中顶点数已超,请检查"
        self._max_err = u"以下组中顶点数已超,请检查"
        self.end = u"已检测顶点数"
        if not self.verts:
            return

    def checkinfo(self):
        """
        显示检查信息
        :return:
        """
        _error = self.run()

        _error_list = []
        if _error:
            for k, v in _error.items():
                if k == 'max_err':
                    _error_list.append(self._max_err)
                    for m, n in v.items():
                        _error_list.append(m)
                        _error_list.extend(n)
                else:
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
        _err = {}
        _max_err = {}
        if str(self._asset_level) not in ['10']:
            if self.verts:
                for k, v in self.verts.items():
                    if k and v:
                        _meshs_verts = self._select_grps_verts(k)
                        _max_verts = self._get_maxvertsnum(v)

                        if _max_verts == False:
                            _err[self._info_err] = ['{}.{}'.format(self.entity_name, self.step_name)]
                        else:
                            if _max_verts and _meshs_verts > _max_verts:
                                if k == '{all}':
                                    _err[self._all_max_err] = [u"max顶点数【{}】".format(_max_verts),
                                                               u"当前顶点数【{}】".format(_meshs_verts)]
                                else:
                                    _max_err[k] = [u"max顶点数【{}】".format(_max_verts), u"当前顶点数【{}】".format(_meshs_verts)]
            if _max_err:
                _err['max_err'] = _max_err
        return _err

    def _select_grps_verts(self, _grp):
        u"""
        获取组下模型的顶点数
        :param _grps:
        :return:
        """
        _meshs = []
        _numverts = 0
        _grps = []
        if _grp == "{all}":
            _grps = self.root_group
        else:
            _grps = [_grp]
        _exgrp = []
        for i in range(len(EXP_GRPS)):
            if EXP_GRPS[i] and cmds.ls(EXP_GRPS[i]):
                _exgrp.extend(cmds.ls(EXP_GRPS[i], l=1))
        if _exgrp and _grps:
            _grps = list(set(_grps) - set(_exgrp))

        if _grps:
            _meshs = self._get_meshs(_grps)
        if _meshs:
            _numverts = self._select_meshs_verts(_meshs)
        return _numverts

    def _get_maxvertsnum(self, _info):
        u"""
        获取信息的 值
        :param _info:
        :return:
        """
        _key = ''
        if not self._asset_level or self._asset_level < 1:
            _key = 'level_0'
        if self._asset_level and self._asset_level >= 1:
            _key = 'level_{}'.format(self._asset_level)
        if _info and _key and _key in _info:
            return _info[_key]
        else:
            return False

    def _select_meshs_verts(self, _meshs):
        u"""
        获得列表模型的顶点数
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

    @property
    def root_group(self):
        u"""
        获取最外层大组
        Returns:

        """

        return group_common.BaseGroup().get_root_groups()

    def _get_meshs(self, _grps):
        u"""
        获取组下所有模型
        :param _grps:
        :return:
        """
        _meshs = []
        if _grps:
            for i in range(len(_grps)):
                if _grps[i] and cmds.ls(_grps[i]):
                    _mess = cmds.listRelatives(_grps[i], ad=1, type='mesh', f=1)
                    if _mess:
                        for i in range(len(_mess)):
                            tr = cmds.listRelatives(_mess[i], p=1, type='transform', f=1)
                            if tr and tr[0].split('_')[-1] not in EXP:
                                _meshs.extend(tr)
        return _meshs

if __name__ == '__main__':
    # 测试代码
    import method.shotgun.get_task as get_task

    reload(get_task)
    _filename = cmds.file(q=1, exn=1)

    test_task_data = get_task.TaskInfo(_filename, 'X3', 'maya', 'publish')

    #
    #     # print test_task_data.project_soft
    _handle = Check(test_task_data)

    _handle.run()

# cmds.select(_handle._get_meshs(['NPC_ZZN_BaseHair']))
