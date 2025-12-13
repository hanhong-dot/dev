# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       : batch_ui
# Describe   : 说明描述
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2023/12/30__14:54
# -------------------------------------------------------
import os

def getRootPath():
    rootPath = os.path.dirname(os.path.abspath(__file__)).split('lib')[0].replace('\\', '/')
    return rootPath


def apps_path():

    return os.path.join(root_path(), 'apps')


def database_path():

    return os.path.join(root_path(), 'db')


def root_path():

    return os.path.dirname(os.path.abspath(__file__).split('lib')[0])


def config_path():

    return os.path.join(root_path(), 'conf')


def publish_config_path():

    return os.path.join(root_path(), 'apps/publish/config')


def workfile_config_path():

    return os.path.join(root_path(), 'apps/workfile/config')


def appdata_path():

    _path = os.getenv('APPDATA')
    _path_ele = _path.split(os.sep)
    return os.sep.join(_path_ele)


def pipedata_path():

    return os.path.join(appdata_path(), 'ftpipeline')