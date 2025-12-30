# -*- coding: utf-8 -*-
# author: linhuan
# file: check_pl_rolaccesory_bs.py
# time: 2025/12/26 14:48
# description:
import maya.cmds as cmds
import lib.common.loginfo as info
import lib.maya.analysis.analyze_structure as structure

reload(structure)
import database.shotgun.fun.get_entity as get_entity
import database.shotgun.core.sg_analysis as sg_analysis

reload(get_entity)

#
CHECKS = ['style_a', 'style_b', 'style_c', 'style_d', 'style_e', 'style_f']


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
        self._asset_level = get_entity.BaseGetSgInfo(self.__sg, self.__entity_id, self.__entity_type).get_asset_level()
        self.analyze_handle = structure.AnalyStrue(self._taskdata)
        self.structure = self.analyze_handle.get_structure()
        self._structure = self._get_structure
        self.__tooltip = u'开始检测pl配饰BS节点(PL捏脸)'
        self.__err = u"配饰模型BS节点报错信息如下(PL捏脸),请检查"
        self.__end = u'已检测pl配饰BS节点(PL捏脸)'

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
        if u'PL捏脸' not in __task_text:
            return __error
        mod_grps_meshs = self._get_mod_grps_meshs()
        if not mod_grps_meshs:
            return __error
        bs_nodes = self.get_bs_list_by_meshs(mod_grps_meshs)
        if not bs_nodes:
            __error.append(u'配饰模型没有关联任何BS节点')
            return __error
        ok, result = self.check_bs_weight_name(bs_nodes)
        if not ok:
            __error.extend(result)
            return __error
        return __error

    def get_bs_nodes_by_mesh(self, mesh):
        bs_list = []
        nodes = cmds.listHistory(mesh)
        if not nodes:
            return bs_list
        for node in nodes:
            if cmds.nodeType(node) == 'blendShape':
                bs_list.append(node)
        return bs_list

    def get_bs_list_by_meshs(self, meshs):
        bs_list = []
        for mesh in meshs:
            _bs_list = self.get_bs_nodes_by_mesh(mesh)
            if _bs_list:
                for bs in _bs_list:
                    if bs not in bs_list:
                        bs_list.append(bs)
        if bs_list:
            return list(set(bs_list))
        return []

    def check_bs_weight_name(self, bs_nodes):
        error_bs = []
        bs_true = []

        if not bs_nodes:
            error_bs.append(u'配饰模型没有关联任何BS节点')
            return False, error_bs
        for bs in bs_nodes:
            judge = True
            for check in CHECKS:
                if not cmds.ls('{}.{}'.format(bs, check)):
                    judge = False
                    break
            if judge:
                bs_true.append(bs)
        if not bs_true:
            error_bs.append(u'没有BS节点的目标形态包含全部有效名称:{}'.format(','.join(CHECKS)))
            return False, error_bs
        return True, bs_true

    def _get_task_text(self):
        fields = ['sg_text']
        filters = [
            ['id', 'is', self.__task_id]
        ]
        task = self.__sg.find_one('Task', filters, fields)
        if task and 'sg_text' in task:
            return u'{}'.format(task['sg_text'])
        return ''

    def _get_mod_grps_meshs(self):
        mesh_list = []
        mod_grps = self._get_grps_structure(self._structure)
        if mod_grps:
            for mod_grp in mod_grps:
                if mod_grp and cmds.ls(mod_grp, type='transform'):
                    meshs = cmds.listRelatives(mod_grp, ad=1, type='mesh', f=1)
                    if meshs:
                        trs = cmds.listRelatives(meshs, p=1, f=1)
                        if trs:
                            for tr in trs:
                                if tr and tr not in mesh_list:
                                    mesh_list.append(tr)
        return mesh_list

    def _get_grps_structure(self, structure):
        mod_grps = []
        if isinstance(structure, dict):
            for k, v in structure.items():
                k = cmds.ls(k)
                if not k:
                    continue
                k = k[0]
                if isinstance(v, list):
                    for _v in v:
                        if isinstance(_v, str) or isinstance(_v, unicode):
                            objs = cmds.ls('{}|{}'.format(k, _v))
                            if objs:
                                mod_grps.extend(objs)
                        elif isinstance(_v, dict):
                            mod_grps.extend(self._get_grps_structure(_v))
                elif isinstance(v, str) or isinstance(v, unicode):
                    objs = cmds.ls(v)
                    if objs:
                        mod_grps.extend(objs)
                elif isinstance(v, dict):
                    mod_grps.extend(self._get_grps_structure(v))
        if isinstance(structure, str) or isinstance(structure, unicode):
            objs = cmds.ls(structure)
            if objs:
                mod_grps.extend(objs)
        if isinstance(structure, list):
            for _v in structure:
                if isinstance(_v, str) or isinstance(_v, unicode):
                    objs = cmds.ls(_v)
                    if objs:
                        mod_grps.extend(objs)
                elif isinstance(_v, dict):
                    mod_grps.extend(self._get_grps_structure(_v))
        return mod_grps

    @property
    def _get_structure(self):
        u"""
        获取结构
        :return:
        """
        structure = self.structure

        if (not self._asset_level or self._asset_level < 1) and isinstance(structure,
                                                                           dict) and 'level_0' in self.structure:
            return structure['level_0']
        elif self._asset_level and self._asset_level > 0:
            _key = 'level_{}'.format(self._asset_level)
            if _key and _key in structure:
                return structure[_key]
            elif 'level_0' in structure:
                return structure['level_0']
            else:
                return structure

        else:
            return structure

