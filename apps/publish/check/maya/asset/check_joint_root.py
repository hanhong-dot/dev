# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       : check_is_structure
# Describe   :  绑定root 骨骼链检测
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2022/7/9__14:25
# -------------------------------------------------------
import lib.common.loginfo as info
import maya.cmds as cmds

import lib.maya.node.grop as group_common

import lib.maya.node.nodes as node_common

import method.maya.common.file as filecommon

import database.shotgun.core.sg_analysis as sg_analysis
import database.shotgun.fun.get_entity as get_entity


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
        self._taskdata = TaskData

        self._assetype = self._taskdata.asset_type
        self.entity_id = self._taskdata.entity_id
        self.entity_type = self._taskdata.entity_type
        self.sg=sg_analysis.Config().login()
        self._asset_level = get_entity.BaseGetSgInfo(self.sg, self.entity_id, self.entity_type).get_asset_level()

        self.tooltip = u'开始检测骨骼链Roots'
        self.err = u"Rig大组下,骨骼链根部需要是Roots,请检查"
        self._item_root = 'common_item_export_grp'
        self.item_err = u"{}大组下,骨骼链根部需要是Root_M,请检查".format(self._item_root)
        self.item_2_err = u"道具资产级别为2,{}大组下,骨骼链根部需要是Roots,请检查".format(self._item_root)
        self.item_second_err=u"Root_M 下,需要有且仅有一个Root_M_Skin骨骼,请检查"
        self.item_second_2_err=u"Roots 下,需要有两个且仅有以下两个骨骼,请检查"
        self.tom_err = u"骨骼链Roots 下,必须包含Root_M,RootMotion两个子级骨骼,请检查\n现在缺失以下子级骨骼"

    def checkinfo(self):
        """
        显示检查信息
        :return:
        """
        _error = self.run()
        _error_list = []
        if _error:
            for k, v in _error.items():
                if v:
                    if k == "join_root_error":
                        _error_list.append(self.err)
                        _error_list.extend(v)
                    if k == "join_root_item_error":
                        _error_list.append(self.item_err)
                        _error_list.extend(v)
                    if k == "join_root_item_2_error":
                        _error_list.append(self.item_2_err)
                        _error_list.extend(v)
                    if k == "join_root_enemy_error":
                        _error_list.append(self.tom_err)
                        _error_list.extend(v)
                    if k == "join_root_item_second_error":
                        _error_list.append(self.item_second_err)
                        _error_list.extend(v)
                    if k == "join_root_item_second_2_error":
                        _error_list.append(self.item_second_2_err)
                        _error_list.extend(v)
            return False, info.displayErrorInfo(title=self.tooltip, objList=_error_list)
        else:
            return True, info.displayInfo(title=self.tooltip)

    def run(self):

        """
        检查文件结构
        :return:
        """
        if self._assetype and self._assetype in ['item']:
            return self._check_item_root_join()
        elif self._assetype and self._assetype in ['enemy']:
            return self._check_enemy_root_join()

        else:
            return self._check_root_join()

    def _check_enemy_root_join(self):
        u"""
        怪物骨骼链检测
        :return:
        """
        _err_dict = {}
        _root_error = self._check_root_join()
        _adlist = []
        _adroots = ['Root_M', 'RootMotion']
        _err_list=[]
        if not _root_error:
            _root_join = self.root_join[0]
            _ads = cmds.listRelatives(_root_join, c=1,f=1)
            if _ads:
                for _ad in _ads:
                    if _ad.split('|')[-1] in _adroots and cmds.nodeType(_ad):
                        _adlist.extend([_ad.split('|')[-1]])
        if _adlist:
            _adlist = list(set(_adlist))
        if not _adlist:
            _err_list = _adroots
        else:
            for _ad_j in _adroots:
                if _ad_j not in _adlist:
                    _err_list.extend([_ad_j])
        if _err_list:
            _err_dict['join_root_enemy_error']=_err_list

        if _root_error:
            _err_dict.update(_root_error)
        return _err_dict

    def _check_item_root_join(self):
        u"""
        检测骨骼链根部
        Returns:

        """
        asset_level=self._asset_level
        _root_joins = self._get_item_root_join()
        if asset_level and asset_level == 2:
            if not _root_joins or len(_root_joins) != 1 or _root_joins[0] != 'Roots':
                return {u"join_root_item_2_error": ['Roots']}
        else:
            if not _root_joins or len(_root_joins) != 1 or _root_joins[0] != 'Root_M':
                return {u"join_root_item_error": ['Root_M']}
        _root_join=''
        if asset_level and asset_level == 2:
            if _root_joins and len(_root_joins) == 1 and _root_joins[0] == 'Roots':
                _root_join = _root_joins[0]
        else:
            if _root_joins and len(_root_joins) == 1 and _root_joins[0] == 'Root_M':
                _root_join = _root_joins[0]
        _root_join_childs = cmds.listRelatives(_root_join, c=1, f=1)

        if asset_level and asset_level == 2:
            if not _root_join_childs or len(_root_join_childs) != 2 :
                return {u"join_root_item_second_2_error": ['Root_M', 'RootMotion']}
            else:
                for join_child in _root_join_childs:
                    short_name=join_child.split('|')[-1]
                    if short_name not in ['Root_M','RootMotion']:
                        return {u"join_root_item_second_2_error": ['Root_M', 'RootMotion']}
        else:
            if not _root_join_childs or len(_root_join_childs) != 1 or _root_join_childs[0].split('|')[-1] != 'Root_M_Skin':
                return {u"join_root_item_second_error": ['Root_M_Skin']}





    def _get_item_root_join(self):
        u"""
        检测item Root_M
        :return:
        """
        _grp_root = self.root_group
        _join_root = self.root_n_join

        _item_grp = self._item_root
        _root_grp = ''
        _join_roots = []
        for _grp in _grp_root:
            _short = _grp.split('|')[-1]
            if _short == _item_grp:
                _root_grp = _grp
        if _root_grp and _join_root:
            for _joint in _join_root:
                if cmds.listRelatives(_joint, p=1, f=1) and cmds.listRelatives(_joint, p=1, f=1)[0] == _root_grp:
                    _join_roots.extend([_joint])
        return _join_roots

    @property
    def root_group(self):
        u"""
        获取最外层大组
        Returns:

        """

        return group_common.BaseGroup().get_root_groups()

    def _check_root_join(self):
        u"""
        检测骨骼链根部
        Returns:

        """
        _root_joins = self.root_join
        if not _root_joins or len(_root_joins) != 1 or _root_joins[0] != 'Roots':
            return {u"join_root_error": ['Roots']}

    @property
    def root_n_join(self):
        u"""
        获取骨骼链根部
        Returns:

        """
        joins = cmds.ls(type='joint')
        _roots = []
        for join in joins:
            if join and not cmds.listRelatives(join, p=1, type='joint') and join not in _roots:
                _roots.extend([join])
        return _roots

    @property
    def root_join(self):
        u"""
        获取骨骼链根部
        Returns:

        """
        joins = cmds.ls(type='joint')
        _roots = []
        _rig_groups = self.rig_group
        for join in joins:
            if join and not cmds.listRelatives(join, p=1, type='joint') and join not in _roots and \
                    cmds.listRelatives(join, p=1, f=1)[0] in _rig_groups:
                _roots.extend([join])
        return _roots

    @property
    def rig_group(self):
        u"""
        获取 _Rig 组
        Returns:

        """
        _rig_group = []
        _root_groups = self.root_group
        if _root_groups:
            for grp in _root_groups:
                if '_Rig' in grp.split('|')[-1] and grp not in _rig_group:
                    _rig_group.append(grp)
        return _rig_group

    # </editor-fold>

    def fix(self):
        """
        修复相关内容
        :return:
        """
        pass


if __name__ == '__main__':
    # 测试代码
    import method.shotgun.get_task as get_task

    reload(get_task)
    _filename = cmds.file(q=1, exn=1)

    test_task_data = get_task.TaskInfo(_filename, 'X3', 'maya', 'publish')

    # print test_task_data.project_soft

    print(Check(test_task_data).run())
