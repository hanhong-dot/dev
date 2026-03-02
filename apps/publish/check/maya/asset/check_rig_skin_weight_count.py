# -*- coding: utf-8 -*-
# author: linhuan
# file: check_item_skin_weight.py
# time: 2025/12/10 20:54
# description:
import lib.common.loginfo as info
import maya.cmds as cmds

import lib.maya.node.grop as group_common

import lib.maya.node.nodes as node_common

import method.maya.common.file as filecommon

import database.shotgun.core.sg_analysis as sg_analysis
import database.shotgun.fun.get_entity as get_entity
import lib.maya.analysis.analyze_structure as structure

MINWIGET = 0.05


class Check(object):
    def __init__(self, TaskData):
        super(Check, self).__init__()
        self._taskdata = TaskData
        self._assetype = self._taskdata.asset_type
        self.entity_id = self._taskdata.entity_id
        self.entity_type = self._taskdata.entity_type
        self.sg = sg_analysis.Config().login()

        self._asset_level = get_entity.BaseGetSgInfo(self.sg, self.entity_id, self.entity_type).get_asset_level()
        self.tooltip = u'开始检测绑定蒙皮权重'
        self.weight_joint_num = 4
        if self._asset_level and int(self._asset_level) == 5 and self._assetype == 'item':
            self.weight_joint_num = 8
        if self._assetype in ['role', 'rolaccesory']:
            self.weight_joint_num = 8
        self.err = u"以下模型蒙皮骨骼超过上限,请检查".format(self.weight_joint_num)
        self.end = u'已检测绑定蒙皮权重'

    def checkinfo(self):
        _error = self.run()
        _error_list = []
        if _error:
            for error_data in _error:
                for mesh, vtx_infos in error_data.items():
                    _error_list.append(u'模型:{} 存在以下顶点蒙皮骨骼数超过{}根'.format(mesh, self.weight_joint_num))
                    for vtx_info in vtx_infos:
                        vtx = vtx_info[0]
                        num = len(vtx_info[1])
                        _error_list.append(u'    顶点:{} 蒙皮骨骼数:{}'.format(vtx, num))

            return False, info.displayErrorInfo(title=self.err, objList=_error_list)
        else:
            return True, info.displayInfo(title=self.tooltip, objList=[self.end])

    def run(self):
        if self._assetype not in ['item', 'role', 'rolaccesory']:
            return []
        __meshs = self._get_all_meshs()
        return self._check_meshs_weight_joint_num(__meshs)

    def _get_all_meshs(self):
        __structure = structure.AnalyStrue(self._taskdata).get_structure()
        _meshs = []
        __groups = self._get_check_groups(__structure)
        if not __groups:
            return _meshs
        for group in __groups:
            __meshs = self._get_meshs_from_group(group)
            if __meshs:
                _meshs.extend(__meshs)
        if _meshs:
            _meshs = list(set(_meshs))
        return _meshs

    def _check_meshs_weight_joint_num(self, meshs):
        error_list = []
        if not meshs:
            return error_list
        for mesh in meshs:
            skin_clusters = self._get_skin_cluster(mesh)
            if not skin_clusters:
                continue
            vtx_count = cmds.polyEvaluate(mesh, v=True)
            influences = cmds.skinCluster(skin_clusters[0], q=True, inf=True)
            __error = []
            for i in range(vtx_count):
                for skin in skin_clusters:
                    vtx = '{}.vtx[{}]'.format(mesh, i)
                    weights = cmds.skinPercent(skin, vtx, q=True, value=True)
                    jw = list(zip(influences, weights))
                    jw = [(j, w) for j, w in jw if w > 0.0]
                    if len(jw) > self.weight_joint_num:
                        __error.append([vtx, jw])
            if __error:
                error_list.append({mesh: __error})
        return error_list

    def _get_skin_cluster(self, mesh):
        history = cmds.listHistory(mesh) or []
        skins = cmds.ls(history, type='skinCluster')
        return skins if skins else None

    def _get_meshs_from_group(self, group):
        _meshs = []
        if not group or not cmds.objExists(group):
            return _meshs
        __meshs = cmds.listRelatives(group, ad=True, type='mesh', f=1)
        if __meshs:
            for mesh in __meshs:
                tr = cmds.listRelatives(mesh, p=True, f=True, type='transform')
                if tr:
                    _meshs.append(tr[0])
        if _meshs:
            _meshs = list(set(_meshs))

        return _meshs

    def _get_check_groups(self, _structure):
        _groups = []
        if not _structure:
            return _groups
        if isinstance(_structure, list):
            _groups.extend(_structure)
        elif isinstance(_structure, str) or isinstance(_structure, unicode):
            _groups.append(_structure)
        elif isinstance(_structure, dict):
            for k, v in _structure.items():
                if isinstance(v, list):
                    _groups.extend(v)
                elif isinstance(v, str) or isinstance(v, unicode):
                    _groups.append(v)
                elif isinstance(v, dict):
                    _groups.extend(self.__get_check_groups(v))
        return _groups

    def fix(self):
        error_list = self.run()
        if not error_list:
            return
        for error_data in error_list:
            for k, v in error_data.items():
                info.displayInfo(title=u'正在修复模型:{} 顶点蒙皮骨骼数超过{}根的问题'.format(k, self.weight_joint_num))
                mesh = k
                for vtx_info in v:
                    vtx = vtx_info[0]
                    jw = vtx_info[1]
                    jw.sort(key=lambda x: x[1], reverse=True)
                    jw_to_keep = jw[:self.weight_joint_num]
                    total_weight = sum([w for j, w in jw_to_keep])
                    jw_to_keep = [(j, w / total_weight) for j, w in jw_to_keep]
                    set_list = []
                    for j, w in jw:
                        if j not in [jk for jk, wk in jw_to_keep] and w <= MINWIGET:
                            set_list.append(j)
                    if set_list:
                        for j in set_list:
                            skin_clusters = self._get_skin_cluster(mesh)
                            if skin_clusters:
                                cmds.skinPercent(skin_clusters[0], vtx, transformValue=[(j, 0.0)])
                        jw_to_keep = [(j, w) for j, w in jw if j not in set_list]
                        total_weight = sum([w for j, w in jw_to_keep])
                        jw_to_keep = [(j, w / total_weight) for j, w in jw_to_keep]
                        for j, w in jw_to_keep:
                            skin_clusters = self._get_skin_cluster(mesh)
                            if skin_clusters:
                                cmds.skinPercent(skin_clusters[0], vtx, transformValue=[(j, w)])

        return True
