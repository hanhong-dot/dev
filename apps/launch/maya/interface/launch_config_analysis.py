# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       : launch_config_analysis
# Describe   : 说明描述
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2022/5/5__21:26
# -------------------------------------------------------
import os


class ConfigInfo():
    def __init__(self, _project=None, _base_dir=None, _version=None):
        u"""
        配置信息
        :param _project: 项目名
        :param _base_dir: 基本路径
        """
        self._project = _project
        self._base_dir = _base_dir
        self._version = _version
        if not self._base_dir:
            self._base_dir = os.path.dirname(os.path.abspath(__file__)).split('app')[0]

    def get_env_configfile(self):
        u"""
        获取环境变量配置文件
        :return:
        """
        if not self._version:
            return (u"{}/apps/launch/config/project/{}/env_config.json".format(self._base_dir,
                                                                               self._project)).replace('\\',
                                                                                                       '/').replace(
                '//', '/')
        else:
            return (u"{}/apps/launch/config/project/{}/env_{}_config.json".format(self._base_dir,
                                                                                  self._project,
                                                                                  self._version)).replace('\\',
                                                                                                          '/').replace(
                '//', '/')

    def get_shelf_configfile(self):
        u"""
        获取 maya_shelf_setting.json
        :return:
        """
        if not self._version:
            return (u"{}/apps/launch/config/project/{}/maya_shelf_setting.json".format(self._base_dir,
                                                                                       self._project)).replace('\\',
                                                                                                               '/').replace(
                '//', '/')
        else:
            return (u"{}/apps/launch/config/project/{}/maya_{}_shelf_setting.json".format(self._base_dir,
                                                                                          self._project,
                                                                                          self._version)).replace('\\',
                                                                                                                  '/').replace(
                '//', '/')


def current_project():
    u"""
    获取当前项目名
    :return:
    """
    return 'X3'
    # import sgtk
    # try:
    #     return sgtk.platform.current_engine().context.project['name']
    # except:
    #     pass

# if __name__ == '__main__':
#     print(ConfigInfo().get_env_configfile())
