# -*- coding: utf-8 -*-
# author: linhuan
# file: check_item_rig_shader_same_mod.py
# time: 2026/2/27 17:43
# description: item 检测 rig shader是否同模型一致

import lib.common.loginfo as info
import maya.cmds as cmds

import database.shotgun.core.sg_analysis as sg_analysis
from apps.publish.process.maya import process_record_data

reload(process_record_data)
import lib.maya.analysis.analyze_structure as structure

reload(structure)


class Check(object):
    def __init__(self, TaskData):
        self.__task_data = TaskData
        self.__asset_type = self.__task_data.asset_type
        self.__asset_name = self.__task_data.entity_name
        self.__tooltip = u'开始检测绑定组下模型和drama_mdl的材质命名是否一致'
        self.__tooltip_error = u'绑定组下模型和drama_mdl不一致,请检查以下报错信息\n'
        self.__end = u'已检测'
        self.__sg = sg_analysis.Config().login()
        self.__asset_id = self.__task_data.entity_id
        self.analyze_handle = structure.AnalyStrue(self.__task_data)
        self.structure = self.analyze_handle.get_structure()

    def checkinfo(self):
        _error = self.run()
        _error_list = []
        if _error:
            if not isinstance(_error, dict):
                _error_list.append(_error)
            else:
                for k, v in _error.items():
                    if k == 'no_mdl_data':
                        _error_list.append(
                            u'以下模型没有找到drama_mdl的材质记录信息,请检查drama_mdl文件是否一致\n'.format(
                                self.__asset_name))
                        for v_item in v:
                            _error_list.append(u'    模型:{}'.format(v_item))
                    elif k == 'error_shader':
                        _error_list.append(u'以下模型没有连接材质球或者连接的材质球是lambert1\n')
                        for v_item in v:
                            _error_list.append(u'    模型:{}'.format(v_item))
                    elif k == 'not_same':
                        _error_list.append(u'以下模型和drama_mdl的材质记录信息不一致\n')
                        for v_item in v:
                            _error_list.append(u'    模型:{}'.format(v_item))
            return False, info.displayErrorInfo(title=self.tooltip, objList=_error_list)
        else:
            return True, info.displayInfo(title=self.tooltip, objList=[self.end])

    def run(self):
        if self.__asset_type in ['item']:
            __drama_mdl_data = self.__get_drama_mdl_data()
            if not __drama_mdl_data:
                return u'没有找到drama_mdl的材质记录信息,请先上传{}drama_mdl任务'.format(self.__asset_name)
            grp_list = [k for k in self.structure.keys() if k]
            meshs = self._get_meshs_from_grps(grp_list)
            return self.__check_shader(meshs, __drama_mdl_data)

    def __check_shader(self, meshs, drama_mdl_data):
        error_mdl_data = []
        error_not_same = []
        error_shader = []
        __error = {}
        if not meshs:
            return
        for mesh in meshs:
            __mdl_data = []
            for __item in drama_mdl_data:
                for k, v in __item.items():
                    if k == mesh:
                        __mdl_data = v
                        break
            if not __mdl_data:
                error_mdl_data.append(mesh)
                continue
            shapes = cmds.listRelatives(mesh, shapes=1, fullPath=1, type='mesh')
            if not shapes:
                continue
            shape = shapes[0]
            sgs = cmds.listConnections(shape, type='shadingEngine')
            if not sgs:
                continue
            if len(sgs) == 1:
                shader = cmds.listConnections('{}.surfaceShader'.format(sgs[0]), s=1, d=0)
                if not shader or shader[0] == 'lambert1':
                    error_shader.append(mesh)
                    continue
                sg = sgs[0]
                __mdl_shader = __mdl_data[0]['shader']
                __mdl_sg = __mdl_data[0]['sg']
                if shader[0] != __mdl_shader or sg != __mdl_sg:
                    error_not_same.append(mesh)
            else:
                for sg in sgs:
                    __meshs = cmds.sets(sg, q=1)
                    if not __meshs:
                        continue
                    _mesh = ''
                    for __mesh in __meshs:
                        if '{}.f['.format(mesh) in __mesh:
                            _mesh = __mesh
                            break
                    if not _mesh:
                        _mesh = shape
                    for __mdl_item in __mdl_data:
                        if __mdl_item['shape'] == _mesh:
                            __mdl_shader = __mdl_item['shader']
                            __mdl_sg = __mdl_item['sg']
                            shader = cmds.listConnections('{}.surfaceShader'.format(sg), s=1, d=0)
                            if not shader or shader[0] == 'lambert1':
                                error_shader.append(mesh)
                                continue
                            if shader[0] != __mdl_shader or sg != __mdl_sg:
                                error_not_same.append(mesh)
        if error_mdl_data:
            __error['no_mdl_data'] = list(set(error_mdl_data))
        if error_not_same:
            __error['not_same'] = list(set(error_not_same))
        if error_shader:
            __error['error_shader'] = list(set(error_shader))
        return __error

    def fix(self):
        __error = self.run()
        if not __error:
            return True, info.displayInfo(title=self.tooltip, objList=[u'没有检测到错误,无需修复'])
        if not isinstance(__error, dict):
            return False, info.displayErrorInfo(title=self.tooltip, objList=[__error])
        if 'no_mdl_data' in __error:
            return False, info.displayErrorInfo(title=self.tooltip, objList=[
                u'没有找到drama_mdl的材质记录信息,请先上传{}drama_mdl任务'.format(self.__asset_name)])
        if 'error_shader' in __error:
            return False, info.displayErrorInfo(title=self.tooltip, objList=[
                u'以下模型没有连接材质球或者连接的材质球是lambert1,请检查文件手动修复\n{}'.format(
                    '\n'.join(__error['error_shader']))])
        if 'not_same' in __error:
            __error_meshs = __error['not_same']
            __drama_mdl_data = self.__get_drama_mdl_data()
            self.fix_shader(__error_meshs, __drama_mdl_data)

    def fix_shader(self, error_meshs, drama_mdl_data):
        if not error_meshs:
            return
        for mesh in error_meshs:
            __mdl_data = []
            for __item in drama_mdl_data:
                for k, v in __item.items():
                    if k == mesh:
                        __mdl_data = v
                        break
            if not __mdl_data:
                continue
            shapes = cmds.listRelatives(mesh, shapes=1, fullPath=1, type='mesh')
            if not shapes:
                continue
            shape = shapes[0]
            sgs = cmds.listConnections(shape, type='shadingEngine')
            if not sgs:
                continue
            if len(sgs) == 1:
                shader = cmds.listConnections('{}.surfaceShader'.format(sgs[0]), s=1, d=0)
                if not shader or shader[0] == 'lambert1':
                    continue
                sg = sgs[0]
                __mdl_shader = __mdl_data[0]['shader']
                __mdl_sg = __mdl_data[0]['sg']
                if shader[0] != __mdl_shader:
                    cmds.rename(shader[0], __mdl_shader)
                if sg != __mdl_sg:
                    cmds.rename(sg, __mdl_sg)
            else:
                for sg in sgs:
                    __meshs = cmds.sets(sg, q=1)
                    if not __meshs:
                        continue
                    _mesh = ''
                    for __mesh in __meshs:
                        if '{}.f['.format(mesh) in __mesh:
                            _mesh = __mesh
                            break
                    if not _mesh:
                        _mesh = shape
                    for __mdl_item in __mdl_data:
                        if __mdl_item['shape'] == _mesh:
                            __mdl_shader = __mdl_item['shader']
                            __mdl_sg = __mdl_item['sg']
                            shader = cmds.listConnections('{}.surfaceShader'.format(sg), s=1, d=0)
                            if shader[0] != __mdl_shader:
                                cmds.rename(shader[0], __mdl_shader)
                            if sg != __mdl_sg:
                                cmds.rename(sg, __mdl_sg)

    def _get_meshs_from_grps(self, grps):
        meshs = []
        if grps:
            for grp in grps:
                mesh_sp = cmds.listRelatives(grp, ad=1, type='mesh', f=1)
                if not mesh_sp:
                    continue
                for mesh in mesh_sp:
                    tr = cmds.listRelatives(mesh, parent=1, fullPath=1)
                    if not tr:
                        continue
                    meshs.append(tr[0].split('|')[-1])
        if not meshs:
            return []
        return list(set(meshs))

    def __get_drama_mdl_data(self):
        filter = [['entity', 'is', {'type': 'Asset', 'id': self.asset_id}], ['content', 'is', 'drama_mdl']]
        fields = ['sg_data']
        data = self.sg.find_one('Task', filter, fields)
        if not data or 'sg_data' not in data or not data['sg_data']:
            return {}
        return eval(data['sg_data'])
