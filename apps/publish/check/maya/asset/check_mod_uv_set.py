# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       : check_mod_uv_set
# Describe   : 说明描述
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2023/10/19__19:34
# -------------------------------------------------------
import lib.common.loginfo as info
import maya.cmds as cmds
import lib.maya.node.mesh as meshcommon
import maya.api.OpenMaya as om2

GROUP_LIST = ['*_H_HD','*_H_LD']

class Check(object):

    def __init__(self, TaskData):
        super(Check, self).__init__()
        self._asset_type = TaskData.asset_type
        self._task_name = TaskData.task_name
        self._tooltip_error= u'以下模型的uvset不在第一象限,请检查'
        self._tooltip_true = u'已检测uvset象限是否在第一象限'


    def checkinfo(self):
        _error = self.run()
        _error_list = []
        if _error:
            _error_list.extend(_error)
            return False, info.displayErrorInfo(title=self._tooltip_error, objList=_error_list)
        else:
            return True, info.displayInfo(title=self._tooltip_true )

    def run(self):
        if self._asset_type in ['body','cartoon_body']:

            return self._judge_uvset()

    def _judge_uvset(self):
        u"""
        检测文件中的 uvset是否在第一象限
        :return:
        """
        error=[]
        meshs=self._mesh_list()
        if meshs:
            for _mesh in meshs:
                #
                try:
                    _mesh_class = meshcommon.Mesh(_mesh)
                    uvsets = om2.MFnMesh(_mesh_class.mesh).getUVSetNames()
                    for uvset in uvsets:
                        _uvset = om2.MFnMesh(_mesh_class.mesh).getUVs(uvSet=uvset)
                        if _uvset:
                            for _uv in _uvset:
                                if _uv[0] < 0 or _uv[1] < 0:
                                    error.append(cmds.listRelatives(_mesh, p=1)[0])
                except:
                    pass
        if error:
            return list(set(error))


    def _mesh_list(self):
        u"""
        需要检测的模型
        """
        import lib.maya.node.grop as groupcommon
        groups= []
        for grp in GROUP_LIST:
            groups.extend(cmds.ls(grp, l=1))
        _meshs = []
        if groups:
            for _grop in groups:
                _mesh = groupcommon.Group(_grop).select_group_meshs()
                if _mesh:
                    _meshs.extend(_mesh)
        return _meshs

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
#     print(_handle._judge_uvset())