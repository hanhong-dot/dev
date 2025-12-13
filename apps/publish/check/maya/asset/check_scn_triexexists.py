# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       : check_scn_triexexists
# Describe   : 检测场景中是否有三角面
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2023/3/27__17:39
# -------------------------------------------------------
import lib.common.loginfo as info
import lib.maya.node.mesh as meshcommon


class Check(object):
    def __init__(self, TaskData):
        super(Check, self).__init__()
        self.TaskData = TaskData
        self.asset_type = self.TaskData.asset_type
        self.task_name = self.TaskData.task_name
        self.tooltip = u'已检测场景中是否有三角面'
        self.error=u'场景中,以下模型有三角面,请检查'

    def checkinfo(self):
        _error = self.run()
        _error_list = []
        if _error:
            _error_list.append(self.error)
            _error_list.extend(_error)
            return False, info.displayErrorInfo(title=self.tooltip, objList=_error_list)
        else:
            return True, info.displayInfo(title=self.tooltip)

    def run(self):
        if self.asset_type in ['item', 'envmodel', 'plant', 'structure', 'indoor', 'envprop']:
            return self._check_triangles()

    def _check_triangles(self):
        import maya.cmds as cmds
        # 获取场景中所有三角面
        _meshs = cmds.ls(type='mesh', l=1)
        _trs = [cmds.listRelatives(x, p=1, f=1)[0] for x in _meshs if cmds.listRelatives(x, p=1, f=1)]
        _triangles=[]
        for _tr in _trs:
            _mesh = meshcommon.Mesh(_tr)
            _triangle = _mesh.get_triangles()
            if _triangle:
                _triangles.extend(_triangle)
        return _triangles


# if __name__ == '__main__':
#     import method.shotgun.get_task as get_task
#
#     reload(get_task)
#     import maya.cmds as cmds
#
#     _filename = cmds.file(q=1, exn=1)
#
#     test_task_data = get_task.TaskInfo(_filename, 'X3', 'maya', 'publish')
#     _handle = Check(test_task_data)
#     print(_handle.checkinfo())
