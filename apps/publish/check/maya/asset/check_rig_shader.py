# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       : check_rig_shader
# Describe   : 检测材质命名(item rig)
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2023/9/26__9:10
# -------------------------------------------------------

import lib.common.loginfo as info
import lib.maya.analysis.analyze_structure as structure

reload(structure)
import maya.cmds as cmds
import maya.mel as mel


class Check(object):
    """
    检查资产文件结构（以后按配置文件来查)
    """

    def __init__(self, TaskData):
        super(Check, self).__init__()

        self._taskdata = TaskData
        self._asset_type = self._taskdata.asset_type
        self._tooltip_error = u'以下模型的材质命名不正确,请检查\n需要以_mat结尾'
        self._tooltip_true = u'已检测模型材质命名'

        self.analyze_handle = structure.AnalyStrue(self._taskdata)
        self.structure = self.analyze_handle.get_structure()

    def checkinfo(self):
        _error = self.run()
        _error_list = []
        if _error:
            _error_list.extend(_error)
            return False, info.displayErrorInfo(title=self._tooltip_error, objList=_error_list)
        else:
            return True, info.displayInfo(title=self._tooltip_true)

    def run(self):
        if self._asset_type in ['item']:
            grp_list = [k for k in self.structure.keys() if k]
            meshs = self._get_meshs_from_grps(grp_list)
            return self._judge_shader(meshs)

    def _judge_shader(self, meshs):
        error = []
        if meshs:
            for mesh in meshs:
                sgs = cmds.listConnections(mesh, type='shadingEngine')
                if sgs:
                    for sg in sgs:
                        shaders = cmds.listConnections('{}.surfaceShader'.format(sg), s=1, d=0)
                        if shaders:

                            if not shaders[0].endswith('_mat'):
                                error.append(shaders[0])

        return error

    def _get_meshs_from_grps(self, grps):
        meshs = []
        if grps:
            for grp in grps:
                meshs.extend(cmds.listRelatives(grp, ad=1, type='mesh', f=1))
        return meshs

    def fix(self):
        error= self.run()
        if error:
            self. fix_shader()
        error= self.run()
        court = 0
        while error and court <10:
            self. fix_shader()
            error= self.run()
            court +=1


    def fix_shader(self):
        _shader, _sg = self._creat_com_shader()
        grp_list = [k for k in self.structure.keys() if k]
        meshs = self._get_meshs_from_grps(grp_list)
        all_meshs = cmds.ls(type='mesh', l=1)
        clear_meshs = []
        for mesh in all_meshs:
            if mesh not in meshs:
                trs = cmds.listRelatives(mesh, p=1, type='transform', f=1)
                if trs:
                    clear_meshs.extend(trs)
        if clear_meshs:
            cmds.sets(clear_meshs, e=1, forceElement=_sg)
        print clear_meshs
        self._clear_unused_nodes()
        for _mesh in meshs:
            self._rename_mesh_shader(_mesh)

    def _rename_mesh_shader(self, mesh):
        sgs = cmds.listConnections(mesh, type='shadingEngine')
        if sgs:
            for sg_ in sgs:
                shaders = cmds.listConnections('{}.surfaceShader'.format(sg_), s=1, d=0)
                if shaders:
                    shader = shaders[0]

                    if not shader.endswith('_mat'):
                        shader_ = '{}_mat'.format(mesh.split('|')[-1])
                        shader_new = shader_
                        if not cmds.objExists(shader_):
                            shader_new = shader_
                        else:
                            count = 0
                            while count < 1000:
                                shader_new = '{}_{}_mat'.format(mesh.split('|')[-1], count)
                                count += 1
                                if not cmds.objExists(shader_new):
                                    break
                        shander_n = cmds.rename(shader, shader_new)
                        sg = cmds.listConnections(shander_n, type='shadingEngine')
                        if shander_n.endswith('_mat') and sg:
                            cmds.rename(sg[0], shander_n + 'SG')
                        else:
                            tr = cmds.listRelatives(mesh, p=1, tr=1)
                            if tr:
                                shader_t = '{}_mat'.format(tr[0].split('|')[-1])
                                cmds.rename(shander_n, shader_t)
                                cmds.rename(sg[0], shader_t + 'SG')

    def _clear_unused_nodes(self):
        mel.eval('MLdeleteUnused;')

    def _creat_com_shader(self, shader_name='clear_common_lamber'):
        if not cmds.objExists(shader_name):
            shader = cmds.shadingNode('lambert', asShader=1, n=shader_name)
            sg = cmds.sets(renderable=1, noSurfaceShader=1, empty=1, n=shader_name + 'SG')
            cmds.connectAttr('%s.outColor' % shader, '%s.surfaceShader' % sg)
        else:
            shader = shader_name
            sg = shader_name + 'SG'
        return shader, sg

# if __name__ == '__main__':
#     import maya.cmds as cmds
#
#     import method.shotgun.get_task as get_task
#
#     reload(get_task)
#     _filename = cmds.file(q=1, exn=1)
#
#     test_task_data = get_task.TaskInfo(_filename, 'X3', 'maya', 'publish')
#
#     _handle = Check(test_task_data)
#     print _handle.structure
