# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       :
# Describe   :
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2024/6/17_16:17
# -------------------------------------------------------
import maya.cmds as cmds
import lib.common.loginfo as info
from lib.maya.node.grop import Group
from method.maya.common.file import BaseFile
import database.shotgun.fun.get_entity as get_entity
import database.shotgun.core.sg_analysis as sg_analysis
class Check(object):
    """
    检查资产文件结构（以后按配置文件来查)
    """

    def __init__(self, TaskData):
        """
        实例初始化
        """
        # 即使直接派生自object，最好也调用一下super().__init__，
        # 不然可能造成多重继承时派生层次中某些类的__init__被跳过。
        super(Check, self).__init__()
        self.taskdata = TaskData
        self.task_id= TaskData.task_id
        self.asset_type = TaskData.asset_type
        self.entity_type = TaskData.entity_type
        self.entity_id = TaskData.entity_id
        self.sg = sg_analysis.Config().login()
        self.entity_name= TaskData.entity_name
        self.tooltip = u'检测bs模型名'
    def checkinfo(self):
        """
        显示检查信息
        :return:
        """
        _error = self.run()
        if _error:
            _error_list=[]
            for _key,_value in _error.items():
                _error_list.append(_key)
                if _value and isinstance(_value,list):
                    for _v in _value:
                        if isinstance(_v,dict):
                            for _k,_v in _v.items():
                                _error_list.append(_k)
                                _error_list.append(_v)
                        else:
                            _error_list.append(_v)

            return False, info.displayErrorInfo(title=self.tooltip, objList=_error_list)
        else:
            return True, info.displayInfo(title=self.tooltip)

    def run(self):
        asset_level = self._get_asset_level()
        if self.asset_type.lower() in ['item'] and asset_level  and int(asset_level) == 1:
            return self._check_bs_mesh_name_e()


    def _check_bs_mesh_name_e(self):
        group='{}_HD'.format(self.entity_name)
        if not cmds.objExists(group):
            return
        _meshs = Group(group).select_group_meshs()
        if not _meshs:
            return
        _trs = self._get_tr_from_meshs(_meshs)
        _parent_meshs = self._get_parent_bs_meshs(_trs)
        if not _parent_meshs:
            return
        _error = self._check_bs_mesh_name(_parent_meshs)
        return _error






    def _check_bs_mesh_name(self,parent_meshs):
        __error={}
        __empty_bs=[]
        __error_bs_name=[]
        for _mesh in parent_meshs:
            grp=self._get_parent_group(_mesh)
            if grp:
                _grp_meshs=self._get_meshs_from_group(grp)
                _parent_meshs=self._get_parent_bs_meshs(_grp_meshs)
                if _parent_meshs and len(_parent_meshs)==1:
                    base_mesh=self._get_short_name(_parent_meshs[0])
                    bs_meshs=self._get_bs_meshs(_grp_meshs)
                    if not bs_meshs:
                        __empty_bs.append(_parent_meshs[0])

                    for _mesh in bs_meshs:
                        _result=False

                        _mesh_short=self._get_short_name(_mesh)
                        for i in range(1,100):
                            if _mesh_short=='{}_bs_{}'.format(base_mesh,i):
                                _result =True
                                break
                        if _result!=True:
                            __error_bs_name.append({_mesh:u'正确命名为{}_bs_数字'.format(base_mesh)})
        if __empty_bs:
            __error[u'没有bs模型,请检查'] = __empty_bs

        if __error_bs_name:
            __error[u'bs模型名不正确,请检查'] = __error_bs_name

        return __error






    def _get_parent_bs_meshs(self,meshs):
        _parent_meshs=[]
        for _mesh in meshs:
            _mesh_short=self._get_short_name(_mesh)
            if '_bs' not in _mesh_short:
                _parent_meshs.append(_mesh)
        return _parent_meshs

    def _get_bs_meshs(self,meshs):
        _bs_meshs=[]
        for _mesh in meshs:
            _mesh_short=self._get_short_name(_mesh)
            if '_bs' in _mesh_short:
                _bs_meshs.append(_mesh)
        return _bs_meshs


    def _get_short_name(self, mesh):
        return mesh.split('|')[-1]

    def _get_parent_group(self, mesh):
        _parent = cmds.listRelatives(mesh, p=1,f=1)
        if _parent:
            return _parent[0]

    def _get_meshs_from_group(self, group):
        _meshs = cmds.listRelatives(group, ad=1, type='mesh', f=1)
        if _meshs:
            return self._get_tr_from_meshs(_meshs)
        else:
            return []


    def _get_tr_from_meshs(self, meshs):
        _tr = []
        for _mesh in meshs:
            _tr.append(cmds.listRelatives(_mesh, p=1,f=1)[0])
        if _tr:
            _tr=list(set(_tr))
        return _tr



    def _get_asset_level(self):
        """
        获取资产级别
        :return:
        """
        return get_entity.BaseGetSgInfo(self.sg, self.entity_id, self.entity_type).get_asset_level()

if __name__ == '__main__':
    import method.shotgun.get_task as get_task

    reload(get_task)
    _filename = cmds.file(q=1, exn=1)

    test_task_data = get_task.TaskInfo(_filename, 'X3', 'maya', 'publish')

    #
    #     # print test_task_data.project_soft
    _handle = Check(test_task_data)

    print _handle.checkinfo()


