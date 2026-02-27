# -*- coding: utf-8 -*-
# author: linhuan
# file: process_record_data.py
# time: 2026/2/27 16:16
# description:
import maya.cmds as cmds
import database.shotgun.core.sg_analysis as sg_analysis


def process_record_data(TaskData):
    task_id = TaskData.task_id
    process_record_data = BaseProcessRecordData(task_id)
    process_record_data.updata_record_data()


class BaseProcessRecordData(object):
    def __init__(self, task_id, sg=None):
        super(BaseProcessRecordData, self).__init__()
        self.__task_id = task_id
        self.__sg = sg
        if self.__sg is None:
            self.__sg = sg_analysis.Config().login()

    def updata_record_data(self):
        shader_data = self.get_record_data()
        if not shader_data:
            return False
        __data = '{}'.format(shader_data)
        self.__sg.update('Task', self.__task_id, {'sg_data': __data})
        return True

    def get_record_data(self):
        shader_data = self.__get_maya_shader_data()
        return shader_data

    def __get_maya_shader_data(self):

        meshs = self.__get_all_meshs()
        shader_data = {}
        if not meshs:
            return shader_data
        for mesh in meshs:
            sgs = cmds.listConnections(mesh, type='shadingEngine')
            if not sgs:
                continue
            sgs = list(set(sgs))
            if len(sgs) == 1:
                shader = cmds.listConnections('{}.surfaceShader'.format(sgs[0]), s=1, d=0)
                if not shader or shader[0] == 'lambert1':
                    continue
                __mesh = mesh.split('|')[-1]
                tr = cmds.listRelatives(mesh, parent=1, fullPath=1)[0]
                shader_data[tr.split('|')[-1]] = [{'shape': __mesh, 'shader': shader[0], 'sg': sgs[0]}]
            else:
                __mesh = mesh.split('|')[-1]
                tr = cmds.listRelatives(mesh, parent=1, fullPath=1)[0]
                __list = []
                for sg in sgs:
                    _shaper = ''
                    __shapers = cmds.sets(sg, q=1)
                    if not __shapers:
                        continue
                    for __shaper in __shapers:
                        if '{}.f['.format(tr) in __shaper:
                            _shaper = __shaper
                            break
                    if not _shaper:
                        _shaper = __mesh
                    shader = cmds.listConnections('{}.surfaceShader'.format(sg), s=1, d=0)
                    if not shader or shader == 'lambert1':
                        continue
                    __list.append({'shape': _shaper, 'shader': shader[0], 'sg': sg})
                shader_data[tr.split('|')[-1]] = __list
        return shader_data

    def __get_all_meshs(self):
        all_meshs = cmds.ls(type='mesh', long=True)
        return all_meshs


# if __name__ == '__main__':
#     task_id = 722642
#     process_record_data = BaseProcessRecordData(task_id)
#     process_record_data.updata_record_data()
