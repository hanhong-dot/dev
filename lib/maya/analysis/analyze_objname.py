# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       : analyze_objname
# Describe   : 解析组下物体命名
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2023/3/15__19:42
# -------------------------------------------------------
import lib.common.config as config

import lib.common.jsonio as jsonio


class AnalyObjNameBase(object):
    u"""
    组下物体解板
    """

    def __init__(self):
        self.data = self._get_config()

    def _get_config(self):
        '''获取模板信息
        '''
        _configpath = config.GetConfig(dcc='maya', configfile="maya_objname.json").get_config()
        return jsonio.read(_configpath)

    def get_data_info(self):
        u"""

        :return:
        """
        return self.data


class AnalyObjNames(AnalyObjNameBase):

    def __init__(self, taskdata):
        u"""

        Args:
            taskdata: 任务信息
        """
        AnalyObjNameBase.__init__(self)

        self.taskdata = taskdata
        self.entity_name = self.taskdata.entity_name
        self.entity_type = self.taskdata.entity_type
        self.asset_type = ''
        if self.entity_type == 'Asset':
            self.asset_type = self.taskdata.asset_type
        self.step_name = self.taskdata.step_name
        self.task_name = self.taskdata.task_name

    def get_objname(self):
        u"""
        获取文件结构信息
        Returns:

        """
        _key = ''
        if self.entity_type in 'Asset':
            _key = self._get_asset_key()
        else:
            _key = self._get_shot_key()

        _fbx_info = self._get_grp_objs(_key)

        if _fbx_info:
            return self._cover_variable(_fbx_info)

    def _get_asset_key(self):
        u"""
        根据taskdata 获取资产key信息
        Returns:

        """

        _key = '{}.{}.{}.{}'.format(self.entity_type, self.asset_type, self.step_name, self.task_name)

        if _key and _key in self.data:
            return _key
        else:
            _key = '{}.{}.{}'.format(self.entity_type, self.asset_type, self.step_name)
            if _key and _key in self.data:
                return _key
            else:
                _key = '{}.{}'.format(self.entity_type, self.asset_type)
                if _key  and _key in self.data:
                    return _key
                else:
                    return self.entity_type

    def _get_shot_key(self):
        u"""
        根据taskdata 获取镜头key信息
        Returns:

        """
        _key = '{}.{}.{}'.format(self.entity_type, self.step_name, self.task_name)
        if _key and _key in self.data:
            return _key
        else:
            _key = '{}.{}.{}'.format(self.entity_type, self.asset_type, self.step_name)

            if _key and _key in self.data:
                return _key
            else:
                _key = '{}.{}'.format(self.entity_type, self.asset_type)
                if _key and _key in self.data:
                    return _key
                else:
                    return self.entity_type

    def _get_grp_objs(self, _key):
        u"""
        获取相应组下物体
        Args:
            _key: key

        Returns:

        """
        try:
            return self.data[_key]
        except:
            return

    def _cover_entity_name(self, _info):
        u"""
        转换{entity_name}变量
        Returns:

        """

        try:

            return self._replace(_info, '{entity_name}', self.entity_name)
        except:
            return _info

    def _replace(self, _info, _ver, _str):
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
        if isinstance(_info, str) or isinstance(_info, unicode):
            return (_info.replace(_ver, _str))
        else:
            return eval(str(_info).replace(_ver, _str))

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

        return _info

    def _cover_ad(self, _info):
        u"""
        转换ad变量
        Args:
            _info:

        Returns:

        """

        if self.asset_type and self.asset_type.lower() in ['body']:
            return self._replace(_info, '{ad}', self.entity_name.split('_')[0])

        else:
            return self._replace(_info, '{ad}', '*')

# if __name__ == '__main__':
#     import method.shotgun.get_task as get_task
#     _filename='FY_BODY.drama_mdl.v001.ma'
#     #
#     taskdata = get_task.TaskInfo(_filename, 'X3', 'maya', 'version')
#     #     _handle= AnalyFbx(taskdata)
#     # #     print(_handle._get_asset_key())
#     # #     print(_handle.data)
#     print(AnalyObjNames(taskdata).get_objname())
