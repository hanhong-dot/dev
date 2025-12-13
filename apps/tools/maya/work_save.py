# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       : work_save
# Describe   : work 文件保存时,自动保存work 描述信息(文件名,文件路径,文件大小,文件修改时间，人员)
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2023/10/20__11:07
# -------------------------------------------------------


import os
from lib.common import fileio


def work_read_user(work_file):
    _json_file = get_work_json_file(work_file)
    if _json_file and os.path.exists(_json_file):
        _file_info = eval(fileio.read(_json_file))
        if _file_info and _file_info.has_key(u'user'):
            return _file_info[u'user']




def work_read_json(work_file):
    _json_file = get_work_json_file(work_file)
    _file_info = fileio.read(_json_file)
    print _file_info


def work_write_json_maya():
    import maya.cmds as cmds
    work_file = cmds.file(q=1, exn=1)
    _json_file = get_work_json_file(work_file)
    _file_info = get_work_file_info()
    _file_info['path'] = cmds.file(q=1, exn=1)
    fileio.write(u'{}'.format(_file_info), _json_file, wtype="w")


def get_work_json_file(work_file):
    _dir, _file = os.path.split(work_file)
    _base, _ext = os.path.splitext(_file)
    work_data_dir = '{}/data/description'.format(_dir)
    if not os.path.isdir(work_data_dir):
        os.makedirs(work_data_dir)
    json_file = '{}/{}.json'.format(work_data_dir, _base)
    return json_file


def get_work_file_info():
    return {'user': get_user(), 'time': get_current_time()}


def get_user():
    import getpass
    return getpass.getuser()


def get_current_time():
    import time
    return time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime())
