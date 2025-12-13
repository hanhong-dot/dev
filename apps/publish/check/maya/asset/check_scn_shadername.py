# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       : check_scn_shadername
# Describe   : 检测场景中的材质名是否符合规范
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2023/3/27__11:29
# -------------------------------------------------------
import lib.common.loginfo as info


class Check(object):

    def __init__(self, TaskData):
        super(Check, self).__init__()
        self.TaskData = TaskData
        self.asset_type = self.TaskData.asset_type
        self.task_name = self.TaskData.task_name
        self.tooltip = u'已检测场景材质命名'
        self.error_info=u'场景中的材质名不符合规范,请检查,需要"_mat"结尾'

    def checkinfo(self):
        _error = self.run()
        _error_list = []
        if _error:
            _error_list.extend(_error)
            return False, info.displayErrorInfo(title=self.tooltip, objList=_error_list)
        else:
            return True, info.displayInfo(title=self.tooltip)

    def run(self):
        if self.asset_type in ['item', 'envmodel', 'plant', 'structure', 'indoor', 'envprop']:
            return self._judge_shadername()

    def _judge_shadername(self):
        import maya.cmds as cmds

        polygons = cmds.ls(type="mesh",l=1)
        error_list = []
        for polygon_shape in polygons:
            if polygon_shape:
                shader_list = cmds.listConnections(polygon_shape, type="shadingEngine")
                if shader_list:
                    for shader in shader_list:
                        shader_names = cmds.listConnections(shader + ".surfaceShader")
                        if shader_names:
                            for shader_name in shader_names:
                                shader_info = shader_name.split("_")
                                if shader_info[-1] != 'mat' and shader_name not in error_list:
                                    error_list.append(shader_name)

        return error_list
# if __name__ == '__main__':
#     import method.shotgun.get_task as get_task
#
#     reload(get_task)
#     import maya.cmds as cmds
#     _filename = cmds.file(q=1, exn=1)
#
#     test_task_data = get_task.TaskInfo(_filename, 'X3', 'maya', 'publish')
#     _handle = Check(test_task_data)
#     print(_handle.run())