# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       : check_scn_2u_overlapp
# Describe   : 说明描述
# version    : 检测场景中uvset(2u)是否重叠
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2023/3/28__11:39
# -------------------------------------------------------
import lib.common.loginfo as info
import maya.cmds as cmds
import lib.maya.node.mesh as meshcommon
import maya.api.OpenMaya as om2


class Check(object):

    def __init__(self, TaskData, group_list=None):
        super(Check, self).__init__()
        self._asset_type = TaskData.asset_type
        self._task_name = TaskData.task_name
        self._tooltip_error = u'场景中,以下模型的2u uvset有重叠,请检查'
        self._tooltip = u'已检测场景中uvset是否重叠'
        self.group_list = group_list

    def checkinfo(self):
        _error = self.run()
        _error_list = []
        if _error:
            _error_list.extend(_error)
            return False, info.displayErrorInfo(title=self._tooltip_error, objList=_error_list)
        else:
            return True, info.displayInfo(title=self._tooltip)

    def run(self):
        if self._asset_type in ['item', 'envmodel', 'plant', 'structure', 'indoor', 'envprop']:
            return self._judge_2u_overlapp()

    def _judge_2u_overlapp(self):
        u"""
        检测场景中的2u uvset是否在第一象限
        :return:
        """
        error = []
        meshs = self._mesh_list()
        if meshs:
            for _mesh in meshs:
                #
                try:
                    _mesh_class = meshcommon.Mesh(_mesh)
                    uvset_current=_mesh_class.currentUVSetName
                    uvsets = om2.MFnMesh(_mesh_class.mesh).getUVSetNames()
                    for uvset in uvsets:
                        if uvset in ['2u']:
                            if uvset_current != uvset:
                                cmds.polyUVSet(_mesh, currentUVSet=True, uvSet=uvset)
                            _face=cmds.polyUVOverlap('{}.f[:]'.format(_mesh), oc=True)
                            if _face:
                                error.extend(cmds.listRelatives(_mesh,p=1, type='transform', f=1))
                            if uvset_current != uvset:
                                cmds.polyUVSet(_mesh, currentUVSet=True, uvSet=uvset_current)

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
