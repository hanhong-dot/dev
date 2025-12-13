# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       : check_is_structure
# Describe   : 资产文件结构检测
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2022/7/9__14:25
# -------------------------------------------------------
import lib.common.loginfo as info
import maya.cmds as cmds

import lib.maya.node.grop as group_common

import lib.maya.node.nodes as node_common

import method.maya.common.file as filecommon

import lib.maya.analysis.analyze_structure as structure

reload(structure)

import database.shotgun.fun.get_entity as get_entity

reload(get_entity)

import database.shotgun.core.sg_analysis as sg_analysis

EXGRP = [u'*_split_*']
EXGRP_10 = [u'*_split_*']

EXRLIST = [{"asset_name": "RY803C_Card", "exr_grp": ["RY803C_Card_FA_HD","RY803C_Card_HE_HD"]},{"asset_name": "PL813C_Card", "exr_grp": ["PL813C_Card_FA_HD","PL813C_Card_HE_HD"]}]


# 2023.06.01 添加{资产名}_split_HD 组免检(资产级别为10)

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
        # 结构

        self.entity_type = self._taskdata.entity_type
        self.entity_id = self._taskdata.entity_id
        self.entity_name = self._taskdata.entity_name
        self.step_name = self._taskdata.step_name
        self.task_name = self._taskdata.task_name
        self.sg = sg_analysis.Config().login()
        self._asset_level = get_entity.BaseGetSgInfo(self.sg, self.entity_id, self.entity_type).get_asset_level()

        self.asset_type = self._taskdata.asset_type
        self.analyze_handle = structure.AnalyStrue(self._taskdata)
        self.structure = self.analyze_handle.get_structure()
        self._structure = self._get_structure
        self.tooltip = u'开始检测文件结构'
        self._root_err = u'最外层大组不正确，请检查以下大组'
        self._grpex_err = u"请检查以下大组,文件中缺少或不止一个组"
        self._ver_error = u"请检查以下大组，有{变量"
        self.end = u"已检测文件结构"
        if not self._structure:
            return

    @property
    def _get_structure(self):
        u"""
        获取结构
        :return:
        """
        structure = self.structure
        if self.asset_type in ['body', 'cartoon_body']:
            structure = self._get_body_structure(structure)

        if (not self._asset_level or self._asset_level < 1) and isinstance(structure,
                                                                           dict) and 'level_0' in self.structure:
            return structure['level_0']
        elif self._asset_level and self._asset_level > 0:
            _key = 'level_{}'.format(self._asset_level)
            print('key', _key)

            if _key and _key in structure:
                return structure[_key]
            elif 'level_0' in structure:
                return structure['level_0']
            else:
                return structure

        else:
            return structure

    def checkinfo(self):
        """
        显示检查信息
        :return:
        """
        _error = self.run()

        _error_list = []
        if _error:
            for k, v in _error.items():
                if v:
                    if k == "error_roots":
                        _error_list.append(self._root_err)
                        _error_list.extend(v)
                    if k == "error_exists":
                        _error_list.append(self._grpex_err)
                        _error_list.extend(v)
                    if k == "error_ver":
                        _error_list.append(self._ver_error)
                        _error_list.extend(v)
                    if k == "error_pr":
                        for m, n in v.items():
                            _error_list.append(u"请检查以下大组,{}需要在{}组下".format(n, m))
                            _error_list.extend([m])
                            _error_list.extend(n)
            return False, info.displayErrorInfo(title=self.tooltip, objList=_error_list)
        else:
            return True, info.displayInfo(title=self.tooltip, objList=[self.end])

    def run(self):
        u"""
        检测
        Returns:

        """
        _err = {}

        # 检测最外层大组
        _error_roots = self._check_root_groups(self._structure)
        # 检测组是否唯 一
        _error_exists = self._check_structure_exists(self._structure)
        # 检测大组父子关系
        _error_pr_dict = self.check_para(self._structure)

        # 检测变量
        _error_ver = self._check_ver()

        if _error_roots:
            _err['error_roots'] = _error_roots
        if _error_exists:
            _err['error_exists'] = _error_exists
        if _error_pr_dict:
            _err['error_pr'] = _error_pr_dict
        if _error_ver:
            _err['error_ver'] = _error_ver

        return _err

    def fix(self):
        u"""
        修复
        Returns:

        """
        _error = self.run()
        if _error:
            if 'error_roots' in _error:
                self._fix_root(_error['error_roots'])
            if 'error_pr' in _error:
                _structure = structure.AnalyStrue(self._taskdata).get_structure()
                self._fix_par(_structure)

    def _fix_par(self, _dict):
        u"""
        修复父子关系
        Args:
            _dict:

        Returns:

        """
        if _dict:
            for k, v in _dict.items():
                if isinstance(v, str) or isinstance(v, unicode):
                    self._parent_grps(k, [v])
                if isinstance(v, list):
                    self._parent_grps(k, v)
                if isinstance(v, dict):
                    self._parent_grps(k, v.keys())
                    self._fix_par(v)

    def _creat_grps(self, _grps):
        u"""
        创建组
        Args:
            _grps: 组列表

        Returns:

        """
        if _grps:
            for _grp in _grps:
                if _grp and not cmds.ls(_grp):
                    group_common.Group(_grp).creat_group()

    def _parent_grps(self, _grpp, _grps):
        u"""
        打组
        Args:
            _grpp: 父组
            _grps: 子组列表

        Returns:

        """
        # 创建不存在的组
        self._creat_grps(_grps)
        # 打组
        group_common.BaseGroup().parent_group(_grpp, _grps)

    def _fix_root(self, grps):
        u"""
        修复最外层大组
        Args:
            grps:

        Returns:

        """
        if grps:
            for grp in grps:
                _handle = group_common.Group(grp)
                if grp and not cmds.ls(grp):
                    _handle.creat_group(grp)
                if grp and cmds.ls(grp):
                    _handle.parent_root_group(grp)

    def _check_ver(self):
        u"""
        检测文件中是否有变量
        Returns:

        """
        _err = []
        trs = cmds.ls(tr=1)
        if trs:
            for i in range(len(trs)):
                _short = self._short(trs[i])
                if '{' in _short or '}' in _short:
                    _err.extend(trs[i])
        return list(set(_err))

    def _check_root_groups(self, _strinfo):
        u"""
        检测最外层大组
        Args:
            _strinfo:

        Returns:

        """
        _error = []
        _root_grps = self.root_group
        _str_list = []
        if _root_grps:
            if self.asset_type in ['role']:
                if isinstance(_strinfo, str) or isinstance(_strinfo, unicode):
                    if '_FX_' in _strinfo:
                        fx_grps = cmds.ls(_strinfo, l=1)
                        _fx_grps, _error = self._check_fx_grps(fx_grps)
                        if _fx_grps:
                            _str_list.extend(_fx_grps)
                        if _error:
                            _error.extend(_error)
                    else:

                        if not cmds.ls(_strinfo) or cmds.ls(_strinfo, l=1)[0] not in _root_grps:
                            _error.extend([_strinfo])
                        else:
                            _str_list.extend(cmds.ls(_strinfo, l=1))
                if isinstance(_strinfo, list):
                    for i in range(len(_strinfo)):
                        if '_FX_' in _strinfo[i]:
                            fx_grps = cmds.ls(_strinfo[i], l=1)
                            _fx_grps, _error = self._check_fx_grps(fx_grps)
                            if _fx_grps:
                                _str_list.extend(_fx_grps)
                            if _error:
                                _error.extend(_error)
                        else:
                            if not cmds.ls(_strinfo[i]) or cmds.ls(_strinfo[i], l=1)[0] not in _root_grps:
                                _error.extend([_strinfo[i]])
                            else:
                                _str_list.extend(cmds.ls(_strinfo[i], l=1))
            else:
                if isinstance(_strinfo, str) or isinstance(_strinfo, unicode):
                    if not cmds.ls(_strinfo) or cmds.ls(_strinfo, l=1)[0] not in _root_grps:
                        _error.extend([_strinfo])
                    else:
                        _str_list.extend(cmds.ls(_strinfo, l=1))
                if isinstance(_strinfo, list):
                    for i in range(len(_strinfo)):
                        if not cmds.ls(_strinfo[i]) or cmds.ls(_strinfo[i], l=1)[0] not in _root_grps:
                            _error.extend([_strinfo[i]])
                        else:
                            _str_list.extend(cmds.ls(_strinfo[i], l=1))

            ex_assets = [ex_data["asset_name"] for ex_data in EXRLIST if ex_data and "asset_name" in ex_data]
            if self.entity_name in ex_assets:
                for ex_data in EXRLIST:
                    if ex_data and "asset_name" in ex_data and ex_data["asset_name"] == self.entity_name:
                        _str_list.extend(ex_data["exr_grp"])

            # 添加不检测的最外层大组
            for _ex in EXGRP:
                if _ex and cmds.ls(_ex):
                    _str_list.extend(cmds.ls(_ex, l=1))
            if str(self._asset_level) == '10':
                for _ex10 in EXGRP_10:
                    if _ex10 and cmds.ls(_ex10):
                        _str_list.extend(cmds.ls(_ex10, l=1))
            if _str_list:
                _str_list = list(set(_str_list))

            if (self.step_name in ['mod', 'fight'] or self.task_name in ['ue_mdl', 'ue_final']) and _root_grps:
                for j in range(len(_root_grps)):
                    if _root_grps[j] not in _str_list:
                        _error.extend([_root_grps[j]])

            if isinstance(_strinfo, dict):
                _errorl = self._check_root_groups(_strinfo.keys())
                if _errorl:
                    _error.extend(_errorl)
        else:
            _error.extend([u'文件中没有组，请检查'])

        return _error

    def _get_body_structure(self, structure_info):

        if self.entity_name.endswith('_New'):

            if structure_info and isinstance(structure_info, list):
                structure_info_new = []
                for i in range(len(structure_info)):
                    info_new = structure_info[i].replace('_HD', '_New_HD').replace('_LD', '_New_LD').replace('_UE',
                                                                                                             '_New_UE')
                    structure_info_new.append(info_new)
                return structure_info_new
            elif structure_info and isinstance(structure_info, dict):
                structure_info_new = {}
                for k, v in structure_info.items():
                    if isinstance(v, str):
                        info_new = v.replace('_HD', '_New_HD').replace('_LD', '_New_LD').replace('_UE', '_New_UE')
                        structure_info_new[k] = info_new
                    elif isinstance(v, list):
                        info_new = []
                        for i in range(len(v)):
                            info_n = v[i].replace('_HD', '_New_HD').replace('_LD', '_New_LD').replace('_UE', '_New_UE')
                            info_new.append(info_n)
                        structure_info_new[k] = info_new
                return structure_info_new
            else:
                return structure_info

        else:
            return structure_info

    def _check_fx_grps(self, grps):
        u"""
        检测fx组
        Args:
            grps:

        Returns:

        """
        _error = []
        _fx_grps = []
        if grps:
            for grp in grps:
                short_grp = grp.split('|')[-1]
                if short_grp.startswith(self.entity_name):
                    _remove_start = short_grp.split('{}_'.format(self.entity_name))[-1]
                    if _remove_start and 'FX' in _remove_start:
                        _fx_infos = _remove_start.split('FX')[0].split('_')
                        if not _fx_infos or len(_fx_infos) <= 2:
                            _fx_grps.append(grp)
                        else:
                            _error.append(grp)
                    else:
                        _error.append(grp)
                else:
                    _error.append(grp)

        return _fx_grps, _error

    def _check_structure_exists(self, _strinfo):
        u"""
        大组存在，并唯一
        Returns:

        """

        _errgrp = []
        if isinstance(_strinfo, str) or isinstance(_strinfo, unicode):
            _gpr = self._group_check(_strinfo)
            if _gpr:
                _errgrp.extend(_gpr)
        if isinstance(_strinfo, list):
            for i in range(len(_strinfo)):
                if _strinfo[i] and self._group_check(_strinfo[i]):
                    _errgrp.extend(self._group_check(_strinfo[i]))
        if isinstance(_strinfo, dict):
            for k, v in _strinfo.items():
                _check_k = self._check_structure_exists(k)

                _check_v = self._check_structure_exists(v)
                if _check_k:
                    _errgrp.extend(_check_k)
                if _check_v:
                    _errgrp.extend(_check_v)
        ex_assets = [ex_data["asset_name"] for ex_data in EXRLIST if ex_data and "asset_name" in ex_data]
        _str_list = []
        if self.entity_name in ex_assets:
            for ex_data in EXRLIST:
                if ex_data and "asset_name" in ex_data and ex_data["asset_name"] == self.entity_name:
                    _str_list.extend(ex_data["exr_grp"])
        if _str_list and _errgrp:
            for _er_grp in _errgrp:
                if _er_grp in _str_list:
                    _errgrp.remove(_er_grp)

        return _errgrp

    def check_para(self, _strinfo):
        u"""
        检测父子关系
        Args:
            _strinfo:

        Returns:

        """
        _str_list = []
        ex_assets = [ex_data["asset_name"] for ex_data in EXRLIST if ex_data and "asset_name" in ex_data]
        if self.entity_name in ex_assets:
            for ex_data in EXRLIST:
                if ex_data and "asset_name" in ex_data and ex_data["asset_name"] == self.entity_name:
                    _str_list.extend(ex_data["exr_grp"])

        if _strinfo and isinstance(_strinfo, dict):
            for k, v in _strinfo.items():
                if cmds.ls(k):
                    _grp = cmds.ls(k)[0]
                    return self._group_par_check(_grp, v, _str_list)
                else:
                    return self._group_par_check(k, v, _str_list)

    def _group_par_check(self, _gprp, _grpc, _str_list):
        u"""
        检测父子组关系
        Args:
            _gprp:父组
            _grpc:子组

        Returns:

        """
        _error = {}
        if not _gprp or not _grpc:
            return
        if isinstance(_grpc, str) or isinstance(_grpc, unicode):
            if (_str_list and _grpc not in _str_list) or not _str_list:
                _par = self._par_grp(_grpc)
                if not _par or self._short(_par) != self._short(_gprp):
                    _error[_gprp] = _grpc
        if isinstance(_grpc, list):
            _list = [_grp for _grp in _grpc if
                     ((not self._par_grp(_grp) or self._short(self._par_grp(_grp)) != self._short(_gprp))) and (
                                 (_str_list and _grp not in _str_list) or not _str_list)]
            if _list:
                _error[_gprp] = _list
        if isinstance(_grpc, dict):
            _error_p = self._group_par_check(_gprp, _grpc.keys(), _str_list)
            if _error_p:
                _error.update(_error_p)
            for k, v in _grpc.items():
                _error_c = self._group_par_check(k, v, _str_list)
                if _error_c:
                    _error.update(_error_c)
        return _error

    def _par_grp(self, _grp):
        u"""
        上一层大组
        Args:
            _grp:

        Returns:

        """
        try:
            return cmds.listRelatives(_grp, p=1)[0]
        except:
            return

    def _short(self, obj):
        u"""
        短写
        Args:
            obj:

        Returns:

        """
        try:
            return obj.split('|')[-1]
        except:
            return obj

    def _group_check(self, _grp):
        u"""
        检测组(有且只有一个相应组)
        Args:
            _grp:

        Returns:

        """
        if 'FX' not in _grp:
            if not cmds.ls(_grp) or len(cmds.ls(_grp)) != 1:
                return [_grp]

    # def run(self):
    #
    #     """
    #     检查文件结构
    #     :return:
    #     """
    #     errdict = {}
    #     # 第一组报错字典(根据任务不同，有不同类型的报错
    #     _err01 = {}
    #     # 第二组报错字典(根据任务不同，有不同类型的报错
    #     _err02 = {}
    #
    #     # 最外层大组需要为*_Rig
    #     _err01 = self._check_rig_group()
    #
    #     # Roots 骨骼链
    #
    #     _err02 =self._check_root_join()
    #
    #     #
    #
    #     if self._task_name == 'drama_mdl':
    #         _err01 = self._check_group('HD')
    #         _err02 = self._check_mesh('HD')
    #     if self._task_name == 'fight_mdl':
    #         _err01 = self._check_group('LD')
    #         _err02 = self._check_mesh('LD')
    #     if self._task_name in ["drama_rig", "rbf"]:
    #         if self.ref_info and self.ref_info != False:
    #             _err01 = self._check_rig_group()
    #             _err02 = self.check_rig_hd_group()
    #         else:
    #             _err01 = self._check_rig_group()
    #     if _err01:
    #         errdict.update(_err01)
    #     if _err02:
    #         errdict.update(_err02)
    #     return errdict

    def _check_body_group(self):
        u"""
        body 检测 (_BaseHead,_BaseBody,_BaseHair大组)
        Returns:

        """
        _groups = group_common.BaseGroup().get_groups()

    def _get_group(self, key=''):
        u"""
        获得组
        Args:
            key:关键字

        Returns:

        """

    @property
    def root_group(self):
        u"""
        获取最外层大组
        Returns:

        """

        return group_common.BaseGroup().get_root_groups()

    def _check_root_join(self):
        u"""
        检测骨骼链根部
        Returns:

        """
        _root_joins = self.root_join
        if not _root_joins or len(_root_joins) != 1 or _root_joins[0] != 'Roots':
            return {u"join_root_error": ['Roots']}

    @property
    def root_join(self):
        u"""
        获取骨骼链根部
        Returns:

        """
        joins = cmds.ls(type='joint')
        _roots = []
        _rig_groups = self.rig_group
        for join in joins:
            if join and not cmds.listRelatives(join, p=1, type='joint') and join not in _roots and \
                    cmds.listRelatives(join, p=1, f=1)[0] in _rig_groups:
                _roots.extend([join])
        return _roots

    @property
    def rig_group(self):
        u"""
        获取 _Rig 组
        Returns:

        """
        _rig_group = []
        _root_groups = self.root_group
        if _root_groups:
            for grp in _root_groups:
                if '_Rig' in grp.split('|')[-1] and grp not in _rig_group and grp.split('_')[-1] == 'Rig':
                    _rig_group.append(grp)
        return _rig_group

    @property
    def ref_info(self):
        u"""
        参考信息
        Returns:

        """
        return filecommon.BaseFile().reference_info_dict()

    def _check_rig_group(self):
        u"""
        检测绑定文件结构(暂时，以后再进一步规范）
        Returns:

        """
        # 需要有且只有一个 *_Rig 大组
        _rig_group = self.rig_group
        if not _rig_group or len(_rig_group) != 1:
            return {u"rig_group_error": ['_Rig']}

    def check_rig_hd_group(self):
        u"""
        Rig 组下需要有{资产名}_HD大组
        Returns:

        """
        _rig_groups = cmds.ls('*_Rig')
        if not _rig_groups or len(_rig_groups) != 1:
            return {u"rig_group_error": ['_Rig']}
        _rig_grp = _rig_groups[0]
        _grp_hd = '{}_HD'.format(self._asset_name)
        _grplist = cmds.listRelatives(_rig_grp, c=1, type='transform')
        if not _grplist or _grp_hd not in _grplist:
            return {'rig_hd_error': [_grp_hd]}

    def _check_group(self, _k='HD'):
        u"""
        drama_rig 任务文件结构检测
        Returns:

        """
        _group = '|{}_{}'.format(self._asset_name, _k)
        _root_group = self.root_group
        if not _root_group or len(_root_group) != 1 or _root_group[0] != _group:
            return {u"group_error": [_group]}

    def _check_mesh(self, _k='HD'):
        u"""
        检测模型名
        Returns:

        """
        _errorlist = []
        meshs = cmds.ls(type='mesh')
        self.pre = '{}_{}'.format(self._asset_name, _k)
        if meshs:
            for _mesh in meshs:
                tr = cmds.listRelatives(_mesh, p=1, type='transform')[0]
                _short = tr.split('|')[-1]
                if self.pre not in _short:
                    _errorlist.extend([tr])
                else:
                    if _short.split('_{}'.format(_k))[0] != self._asset_name:
                        _errorlist.extend([tr])
        if _errorlist:
            return {"mesh_error": _errorlist}

    # </editor-fold>

    def _fix_mod_meshs(self, _meshs):
        u"""
        修复mesh 命名
        Args:
            _meshs: mesh列表

        Returns:修复后mesh列表

        """
        _fixlist = []
        if _meshs:
            for _tr in _meshs:
                _newname = ''
                _short = _tr.split('|')[-1]
                if '_HD_' in _short:
                    _newname = '{}_{}'.format(self.pre, _short.split('_HD_')[-1])
                elif '_LD_' in _short:
                    _newname = '{}_{}'.format(self.pre, _short.split('_LD_')[-1])
                else:
                    _newname = '{}_{}'.format(self.pre, _short)
                if _newname:
                    _result = node_common.BaseNodeProcess().rename_node_nodenew(_tr, _newname)
                    if _result and _result != False:
                        _fixlist.extend(cmds.ls(_newname))
        return _fixlist

    def _fix_mod_group(self, _group=''):
        u"""
        修复模型最外层大组命名
        Args:
            _group: 修复后的最外层大组命名

        Returns:
        """
        _root_groups = self.root_group
        # 如果没有大组，就创建一个大组
        if not _root_groups:
            group_common.Group(_group).creat_group()
        else:
            if len(_root_groups) == 1:
                # 如果只有一个大组，进行改名
                group_common.Group(_root_groups[0]).rename_group(_group)
            else:
                # 如果不止一个大组,创建新组
                group_common.Group(_group).creat_group()
        return _group


if __name__ == '__main__':
    # 测试代码
    import method.shotgun.get_task as get_task

    reload(get_task)
    _filename = cmds.file(q=1, exn=1)

    test_task_data = get_task.TaskInfo(_filename, 'X3', 'maya', 'publish')
    #     #
    #     #     # print test_task_data.project_soft
    _handle = Check(test_task_data)

    print(_handle._get_structure)

    print(_handle.run())
#     #     #
#     print(_handle.checkinfo())
#     print(_handle.check_para(_handle._structure))
