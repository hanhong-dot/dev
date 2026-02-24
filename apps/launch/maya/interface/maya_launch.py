# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       : maya_launch
# Describe   : 说明描述
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2022/5/5__17:06
# -------------------------------------------------------
import os
import maya.mel as mel
import apps.launch.maya.interface.shelf_common as _shelf
import logging

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
import apps.launch.maya.interface.add_environment as _config

import apps.launch.maya.interface.launch_config_analysis as launch_config_analysis


def launch(handle="UI", module='py2',version=None):
    '''执行dcc软件初始化设置
    '''
    # if handle != "batch":
    #     # 添加加载maya默认工具架
    #     _modoules = [load_default_shelf, load_maya_shelf, load_env,load_maya_scriptjob]
    # else:
    #     _modoules = [load_env,load_maya_scriptjob]

    if handle != "batch" and module == 'py2' and not version:
        # 添加加载maya默认工具架
        _modoules = [load_default_shelf, load_maya_shelf, load_env_py2]
    elif handle != "batch" and module == 'py3' and not version:
        _modoules = [load_default_shelf, load_maya_shelf, load_env_py3]
    elif handle == "batch" and module == 'py2' and not version:
        _modoules = [load_env_py2]
    elif handle != "batch" and module == 'py3' and version in ['2023', '2024']:
        _modoules = [load_default_shelf,load_maya_2023_shelf,load_env_2023]

    elif handle == "batch" and module == 'py3' and version in ['2023', '2024']:
        _modoules = [load_env_2023]

    else:
        _modoules = [load_env_py3]

    _funcs = _modoules
    for _func in _funcs:
        logging.info(_func)
        _func()





def load_env_py2(version=None):
    u"""
    添加环境
    """
    _config.env_add('server_py2')
    _config.add_environment('env_py2')
    _config.maya_env_add()


def load_env_py3():
    _config.env_add('server_py3')
    _config.add_environment('env_py3')
    _config.maya_env_add()

def load_env_2023():
    _config.env_add('server_py3',version='2023')
    _config.add_environment('env_py3',version='2023')
    _config.maya_env_add('2023')

def load_maya_shelf():
    '''加载maya工具盒
    '''
    # 项目
    _project = 'x3'
    _config_path = launch_config_analysis.ConfigInfo(_project).get_shelf_configfile()
    try:
        _shelf.restore_shelf2(_config_path, _project)
    except:
        pass

def load_maya_2023_shelf():
    '''加载maya工具盒
    '''
    # 项目
    _project = 'x3'
    _config_path = launch_config_analysis.ConfigInfo(_project,_version='2023').get_shelf_configfile()
    try:
        _shelf.restore_shelf2(_config_path, _project)
    except:
        pass


def _get_shelf_files():
    '''
    获取maya安装目录下shelf
    :return:
    '''
    _shelf_files = []
    _removes = ['shelf_Shelf1.mel']
    _maya_shelf_path = '{}/scripts/shelves'.format(os.getenv('MAYA_LOCATION'))
    _files = os.listdir(_maya_shelf_path)
    if _files:
        for _file in _files:
            if '_' in _file and '.' in _file and '.res.' not in _file and _file not in _removes:
                _shelf_files.append(_file.split('.')[0].split('_')[-1])
    return _shelf_files


def load_maya_scriptjob(version='2018'):
    u"""
    加载maya脚本任务
    """
    if version in ['2018']:
        import apps.launch.maya.interface.scriptjob as scriptjob
        logger.info("add maya scriptjob")
        scriptjob.lod_script_job()
    elif version in ['2023', '2024']:
        import apps.launch.maya.interface.scriptjob_2023 as scriptjob_2023
        logger.info("add maya scriptjob")
        scriptjob_2023.lod_script_job()


def load_default_shelf():
    '''
    加载maya默认shelf
    :return:
    '''
    # 获取当前shelfs
    _allShelfs = mel.eval('shelfTabLayout -q -childArray $gShelfTopLevel')
    # 获取maya默认shelfs
    _maya_shelf_files = _get_shelf_files()
    if _maya_shelf_files:
        for _shelf in _maya_shelf_files:
            if _shelf and _shelf not in _allShelfs:
                try:
                    mel.eval('loadNewShelf "shelf_{}.mel";'.format(_shelf))
                except Exception as e:
                    logger.error("load maya shelf {} error: {}".format(_shelf, e))

#
# if __name__ == '__main__':
#     launch()
