# -*- coding: utf-8 -*-
# -----------------------------------
# @File    : check_asis_shader.py
# @Author  : linhuan
# @Time    : 2025/7/29 10:46
# @Description : 
# -----------------------------------
import lib.common.loginfo as info
import database.shotgun.core.sg_analysis as sg_analysis
from lib.maya.analysis.analyze_config import AnalyDatas
import maya.cmds as cmds


class Check(object):

    def __init__(self, TaskData):
        super(Check, self).__init__()
        self.TaskData = TaskData
        self.asset_type = self.TaskData.asset_type
        self.task_name = self.TaskData.task_name
        self.sg = sg_analysis.Config().login()
        self.entity_id = self.TaskData.entity_id
        self.entity_type = self.TaskData.entity_type
        self.entity_name = self.TaskData.entity_name
        self.error_info = u'检查输出asis fbx模型组件的材质信息'
        self.tooltip = u'已检查输出asis fbx模型组件的材质信息'

    def checkinfo(self):
        _error = self.run()
        _error_list = []
        if _error:
            _error_list.append(u'请检查以下shader,不符合"_mat"命名规范:\n')
            _error_list.extend(_error)
            return False, info.displayErrorInfo(title=self.error_info, objList=_error_list)
        else:
            return True, info.displayInfo(title=self.tooltip)

    def get_fbx_mod_grp_list(self):
        fbx_data = AnalyDatas(self.TaskData, 'maya_fbx.json').get_datas()
        grp_list = []
        if not fbx_data:
            return None
        for i in range(len(fbx_data)):
            fbx_file = fbx_data[i]['fbx_file'] if fbx_data[i]['fbx_file'] else ''
            fbx_objs = fbx_data[i]['fbx_objs'] if fbx_data[i]['fbx_objs'] else []
            if fbx_file.endswith('_asis'):
                grp_list.extend(fbx_objs)
        return grp_list

    def get_check_meshs(self):
        _error = {}
        _check_meshs = []
        fbx_mod_grp_list = self.get_fbx_mod_grp_list()
        if not fbx_mod_grp_list:
            return None
        for grp in fbx_mod_grp_list:
            if not grp or not cmds.objExists(grp):
                continue
            meshs = self.__get_mesh_from_grp(grp)
            if not meshs:
                continue
            _check_meshs.extend(meshs)
        return _check_meshs

    def run(self):
        __error = []
        if self.asset_type and self.asset_type.lower() in ['role']:
            __check_meshs = self.get_check_meshs()
            if not __check_meshs:
                return None
            __error = self.check_shader(__check_meshs)
            if __error:
                __error = list(set(__error))
        return __error

    def check_shader(self, meshs):
        error = []
        for mesh in meshs:
            if not cmds.objExists(mesh):
                continue
            shading_groups = cmds.listConnections(mesh, type='shadingEngine')
            if not shading_groups:
                continue
            for sg in shading_groups:
                shaders = self.__select_sg_surfaceshaderlist(sg)
                if not shaders:
                    continue
                for shader in shaders:
                    if not cmds.objExists(shader):
                        continue
                    if not shader.endswith('_mat'):
                        error.append(shader)

        return error

    def __select_sg_surfaceshaderlist(self, sgname):
        _sgattrlist = ['{}.surfaceShader'.format(sgname), '{}.aiSurfaceShader'.format(sgname)]
        return [cmds.listConnections(i)[0] for i in _sgattrlist if (cmds.ls(i) and cmds.listConnections(i))]

    def __get_mesh_from_grp(self, grp):
        return cmds.listRelatives(grp, ad=1, type='mesh', fullPath=True) or []

    def fix(self):
        __error = self.run()
        if not __error:
            return True, info.displayInfo(title=u'已修复所有不符合"_mat"命名规范的材质')
        for shader in __error:
            if not cmds.objExists(shader):
                continue
            if shader.endswith('_mat'):
                continue

            if shader == 'lambert1':
                self._re_assign_shader(shader)
                continue
            shade_name_new = self._get_fix_shade_name(shader)
            result = self.__rename(shader, shade_name_new)
        return True

    def __rename(self, source_name, target_name):
        try:
            cmds.rename(source_name, target_name)
            return True
        except:
            return False


    def _re_assign_shader(self,shader):
        if shader=='lambert1':
            count=1
            __meshs = self._get_mesh_by_shader(shader)
            shader_new='{}_0{}_mat'.format(self.entity_name,count)
            if cmds.objExists(shader_new):
                while cmds.objExists(shader_new):
                    count = count + 1
                    shader_new = '{}_0{}_mat'.format(self.entity_name, count)
                    if not cmds.objExists(shader_new):
                        break



            sg = self.__create_shader(name=shader_new, type='lambert')

            if not __meshs:
                return False
            if not sg:
                return False
            try:
                cmds.sets(__meshs, e=True, forceElement=sg)
            except Exception as e:
                info.displayErrorInfo(title=u'材质球重新分配失败', objList=[u'材质球重新分配失败，请检查是否有mesh使用了{}材质球'.format(shader)])
                return False





    def _get_mesh_by_shader(self, shader):
        """
        获取使用指定材质球的mesh
        :param shader: 材质球名称
        :return: mesh列表
        """
        if not cmds.objExists(shader):
            return []
        shading_groups = cmds.listConnections(shader, type='shadingEngine')
        if not shading_groups:
            return []
        meshs = []
        for sg in shading_groups:
            __meshs=cmds.sets(sg, q=True)
            if __meshs:
                meshs.extend(__meshs)
        return meshs


    def __create_shader(self, name='lambert_combine', type='lambert'):
        u"""
        创建材质球
        :param type:
        :return:
        """
        try:
            sg = '{}SG'.format(name)
            if cmds.ls(name, type='lambert'):
                cmds.delete(name)
            if cmds.ls(sg, type='shadingEngine'):
                cmds.delete(sg)

            shader = cmds.shadingNode(type, asShader=True, n=name)

            # sg =cmds.createNode('shadingEngine', name=sg)

            sg = cmds.sets(renderable=1, noSurfaceShader=1, em=1, n=sg)

            cmds.connectAttr(('%s.outColor' % shader), ('%s.surfaceShader' % sg))
            return sg
        except:
            return

    def _get_fix_shade_name(self, shade_name):

        __end_name = shade_name.split('_')[-1]
        __info = shade_name.split('_')
        __shade_name_new = ''
        __pre_name = self.get_pre_name(shade_name)


        if 'mat' in __end_name and len(__info) > 1:
            __pre_name_new = self.get_pre_name(__pre_name)
            __sub_name = __info[-2]
            if self.is_valid_number(__sub_name):
                count = 1
                __sub_name_new = '0{}'.format(int(__sub_name) + count)
                __shade_name_new = '{}_{}_mat'.format(__pre_name_new, __sub_name_new)
                while cmds.objExists(__shade_name_new):
                    count = count + 1
                    __sub_name_new = '0{}'.format(int(__sub_name) + count)
                    __shade_name_new = '{}_{}_mat'.format(__pre_name_new, __sub_name_new)
                    if not cmds.objExists(__shade_name_new):
                        break
            else:
                count = 1
                __sub_name_new = '0{}'.format(count)
                __shade_name_new = '{}_{}_mat'.format(__pre_name_new, __sub_name_new)
                while cmds.objExists(__shade_name_new):
                    count = count + 1
                    __sub_name_new = '0{}'.format(count)
                    __shade_name_new = '{}_{}_mat'.format(__pre_name_new, __sub_name_new)
                    if not cmds.objExists(__shade_name_new):
                        break

        elif 'mat' in __end_name and len(__info) == 1:
            count = 1
            __end_name_new = '{}_0{}_mat'.format(__pre_name, count)
            if cmds.objExists(__end_name_new):
                while cmds.objExists(__end_name_new):
                    count = count + 1
                    __end_name_new = '{}_0{}_mat'.format(__pre_name, count)
                    if not cmds.objExists(__end_name_new):
                        break
        else:
            count = 1
            __shade_name_new = '{}_0{}_mat'.format(shade_name, count)
            if cmds.objExists(__shade_name_new):
                while cmds.objExists(__shade_name_new):
                    count = count + 1
                    __shade_name_new = '{}_0{}_mat'.format(__end_name, count)
                    if not cmds.objExists(__shade_name_new):
                        break
        return __shade_name_new

    def get_pre_name(self, name):
        info = name.split('_')
        pre_name = ''
        if len(info) > 1:
            info.pop(-1)
            for i in range(len(info)):
                if i == 0:
                    pre_name = info[i]
                else:
                    pre_name = pre_name + '_' + info[i]
        else:
            pre_name = info[0]
        return pre_name



    def is_valid_number(self, s):
        import re
        return re.match(r'[+-]?(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?', s) is not None
if __name__ == '__main__':
    import method.shotgun.get_task as get_task

    reload(get_task)
    import maya.cmds as cmds

    _filename = cmds.file(q=1, exn=1)

    test_task_data = get_task.TaskInfo(_filename, 'X3', 'maya', 'publish')
    check = Check(test_task_data)
    check.checkinfo()
