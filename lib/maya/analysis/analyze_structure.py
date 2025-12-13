# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       : analyze_structure
# Describe   : 解析文件结构 (maya_structure)
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2022/8/31__11:49
# -------------------------------------------------------

import lib.common.config as config
import lib.common.jsonio as jsonio
import lib.maya.node.grop as group_common


class AnalyStrueBase(object):
    u"""
    需要清理的节点解析
    """

    def __init__(self):
        self.data = self._get_config()

    def _get_config(self):
        '''获取模板信息
        '''
        _configpath = config.GetConfig(dcc='maya', configfile="maya_structure.json").get_config()
        return jsonio.read(_configpath)

    def get_data_info(self):
        u"""

        :return:
        """
        return self.data


class AnalyStrue(AnalyStrueBase):

    def __init__(self, taskdata):
        u"""

        Args:
            taskdata: 任务信息
        """
        AnalyStrueBase.__init__(self)

        self.taskdata = taskdata
        self.entity_name = self.taskdata.entity_name
        self.entity_type = self.taskdata.entity_type
        self.asset_type = ''
        if self.entity_type == 'Asset':
            self.asset_type = self.taskdata.asset_type
        self.step_name = self.taskdata.step_name
        self.task_name = self.taskdata.task_name

    def get_structure(self):
        u"""
        获取文件结构信息
        Returns:

        """
        _key = ''
        if self.entity_type in 'Asset':
            _key = self._get_asset_key()
        else:
            _key = self._get_shot_key()
        print('_key',_key)
        _structure_info = self._get_structure(_key)
        print('_structure_info',_structure_info)
        if _structure_info:
            return self._cover_variable(_structure_info)

    def _get_asset_key(self):
        u"""
        根据taskdata 获取资产key信息
        Returns:

        """

        _key = '{}.{}.{}.{}'.format(self.entity_type, self.asset_type, self.step_name.lower(), self.task_name)
        if _key in self.data:
            return _key
        else:
            _key = '{}.{}.{}'.format(self.entity_type, self.asset_type, self.step_name.lower())
            if _key in self.data:
                return _key
            else:
                _key = '{}.{}'.format(self.entity_type, self.asset_type.lower())
                if _key in self.data:
                    return _key
                else:
                    return self.entity_type

    def _get_shot_key(self):
        u"""
        根据taskdata 获取镜头key信息
        Returns:

        """
        _key = '{}.{}.{}'.format(self.entity_type, self.step_name, self.task_name)
        if _key in self.data:
            return _key
        else:
            _key = '{}.{}.{}'.format(self.entity_type, self.asset_type, self.step_name)
            if _key in self.data:
                return _key
            else:
                _key = '{}.{}'.format(self.entity_type, self.asset_type)
                if _key in self.data:
                    return _key
                else:
                    return self.entity_type

    def _get_structure(self, _key):
        u"""
        获取相应结构信息
        Args:
            _key: key

        Returns:

        """
        try:
            return self.data[_key]
        except:
            return

    def _replace(self, _info, _ver,_str):
        u"""
        变量转换基础函数
        Args:
            _info: 需要转换的信息
            _ver: 需要转换的变亮
            _str：转换的string

        Returns:

        """
        if not _info:
            return
        if isinstance(_info,str) or isinstance(_info,unicode):
            return (_info.replace(_ver,_str))
        else:
            return eval(str(_info).replace(_ver,_str))


    def _cover_entity_name(self, _info):
        u"""
        转换{entity_name}变量
        Returns:

        """

        if '{entity_name}' in _info or '{entity_name}' in str(_info):
            return self._replace(_info,'{entity_name}', self.entity_name)
        else:
            return _info

    def _cover_ad(self, _info):
        u"""
        转换ad变量
        Args:
            _info:

        Returns:

        """
        _rig_group = self.rig_group
        if _rig_group and '{ad}' in str(_info):
            return self._replace(_info, '{ad}', _rig_group[0].split('|')[-1].split('_Rig')[0])

        else:
            return self._replace(_info, '{ad}', '*')


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
                if '_Rig' in grp.split('|')[-1] and grp not in _rig_group and grp.split('_')[-1]=='Rig':
                    _rig_group.append(grp)
        return _rig_group

    @property
    def root_group(self):
        u"""
        获取最外层大组
        Returns:

        """

        return group_common.BaseGroup().get_root_groups()

    @property
    def fx_group(self):
        u"""
        获取fx组
        Returns:

        """
        _fx_group = []
        _root_groups = self.root_group
        if _root_groups:
            for grp in _root_groups:
                if '_FX' in grp.split('|')[-1] and grp not in _fx_group:
                    _fx_group.append(grp)
        return _fx_group

    def _cover_variable(self, _info):
        u"""
        转换变量
        Args:
            _info:

        Returns:

        """
        _info = self._cover_entity_name(_info)
        if _info:
            _info = self._cover_ad(_info)
        # if _info:
        #     _info = self._cover_fx(_info)

        return _info

    def _cover_fx(self,_info):
        u"""
        转换fx变量
        Args:
            _info:

        Returns:

        """
        _fx_groups = self.fx_group
        if _info:
            if _fx_groups and '{fx}' in str(_info):
                for grp in _fx_groups:
                    _ad_infos= grp.split('|')[-1].split('_FX')[0].split('_')
                    if len(_ad_infos)>1:
                        _info=self._replace(_info, '{fx}','{}_FX'.format(_ad_infos[1]))

                    elif len(_ad_infos)==1:
                        _info=self._replace(_info, '{fx}','FX')
        return _info










if __name__ == '__main__':
    import method.shotgun.get_task as get_task

    taskdata = get_task.TaskInfo('TDTEST_ROLEACCE.ue_mdl.v008.ma', 'X3', 'maya', 'version')
    _handle=AnalyStrue(taskdata)
    print(_handle._get_asset_key())
    print(_handle.data)
    print(AnalyStrue(taskdata).get_structure())
