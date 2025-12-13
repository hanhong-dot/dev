# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       : add_environment
# Describe   : 说明描述
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2022/5/5__18:08
# -------------------------------------------------------
import os
import sys

import apps.launch.maya.interface.launch_config_analysis as launch_config_analysis
import lib.common.jsonio as jsonio


def read_env_config(version=None):
    _config = launch_config_analysis.ConfigInfo(_project='x3',_version=version).get_env_configfile()
    try:
        return jsonio.read(_config)
    except:
        return


def maya_env_add(version=None):
    u"""
    添加maya env 环境,主要用于添加P4环境
    """
    _info = read_env_config(version)
    _env = os.environ
    _path = sys.path
    if _info and 'maya_env' in _info:
        for k, v in _info['maya_env'].items():
            if k and k in _env and os.environ.get(k):
                if _env[k] not in v:
                    v = '{};{}'.format(v, _env[k])
                    os.environ[k] = v
                    if v not in _path:
                        sys.path.insert(0,v)




def env_add(_model='server_py2',version=None):
    u"""
    添加环境
    _model:模式，为server时为服务器环境，为local时为本地环境
    """
    _info = read_env_config(version)
    _path = sys.path
    if _info and _model in _info and _model in ["server_py2", "server_py3","local_py2","local_py3"]:
        _env_info = _info[_model]
        _root = _env_info['root']
        _package = _env_info['package']

        _env_paths = [os.path.join(_root, i) for i in _package if i]
        _env_paths.append(_root)
        for i in range(len(_env_paths)):
            if _env_paths[i] not in _path:
                sys.path.insert(0, _env_paths[i])




def add_environment(_model='env_py2',version=None):
    u"""
    添加环境变量
    :return:
    """

    _info = read_env_config(version)
    for k, v in _info[_model].items():
        _it = env_variable_convers(v)
        if k and _it:
            os.environ[k] = _it


def env_variable_convers(info):
    u"""
    变量转换
    :param info: 需要转换的变量
    :return: str
    """
    if info and info == '{current_project}':
        try:
            return launch_config_analysis.current_project()
        except:
            return 'X3'
    else:
        return info


if __name__ == '__main__':
    env_add()
