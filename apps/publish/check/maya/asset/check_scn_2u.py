# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       : check_scn_2u
# Describe   : 检测场景2u uvset 是否在第一象限
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2023/3/27__20:49
# -------------------------------------------------------
import lib.common.loginfo as info
import maya.cmds as cmds
import lib.maya.node.mesh as meshcommon
import maya.api.OpenMaya as om2
import database.shotgun.core.sg_analysis as sg_analysis
import database.shotgun.fun.get_entity as get_entity

class Check(object):

    def __init__(self, TaskData, group_list=None):
        super(Check, self).__init__()
        self._asset_type = TaskData.asset_type
        self._task_name = TaskData.task_name
        self.entity_id = TaskData.entity_id
        self.entity_type = TaskData.entity_type
        self._tooltip_error= u'场景中,以下模型的2u uvset不在第一象限,请检查'
        self._tooltip_true = u'已检测场景中uvset象限'
        self.group_list = group_list
        self.sg=sg_analysis.Config().login()
        self._asset_level = get_entity.BaseGetSgInfo(self.sg, self.entity_id, self.entity_type).get_asset_level()

    def checkinfo(self):
        _error = self.run()
        _error_list = []
        if _error:
            _error_list.extend(_error)
            return False, info.displayErrorInfo(title=self._tooltip_error, objList=_error_list)
        else:
            return True, info.displayInfo(title=self._tooltip_true )

    def run(self):
        if self._asset_type in ['item', 'envmodel', 'plant', 'structure', 'indoor', 'envprop']:
            return self._judge_2u()
            #20240731根据蕃鼠需求,去掉这一级别,改为全部级别检测可忽略
            # asset_level = self._asset_level
            # if not asset_level or asset_level !=3:
            #     return self._judge_2u()

    def _judge_2u(self):
        u"""
        检测场景中的2u uvset是否在第一象限
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
                        if uvset in ['2u']:
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
        if not self.group_list:
            return cmds.ls(type='mesh', l=1)
        else:
            _meshs = []
            for _grop in self.group_list:
                _mesh = groupcommon.Group(_grop).select_group_meshs()
                if _mesh:
                    _meshs.extend(_mesh)
            return _meshs

if __name__ == '__main__':
    import method.shotgun.get_task as get_task

    reload(get_task)
    import maya.cmds as cmds

    _filename = cmds.file(q=1, exn=1)

    test_task_data = get_task.TaskInfo(_filename, 'X3', 'maya', 'publish')
    _handle = Check(test_task_data)
    d=_handle._judge_2u()
#     print(type(_handle._asset_level))
