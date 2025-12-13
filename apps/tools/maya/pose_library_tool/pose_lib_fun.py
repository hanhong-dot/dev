# -*- coding: utf-8 -*-#
# -------------------------------------------------------
# NAME       : pose_lib_fun
# Describe   : 说明描述
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2025/5/9__上午10:34
# -------------------------------------------------------

ROOT_PATH = 'M:/projects/x3/library'
import json
import os
from method.common import dir as common_dir

from lib.common import jsonio
import shutil
from lib.common.md5 import Md5


def get_local_lib_root_path():
    __local_dir = common_dir.get_localtemppath('x3_library')
    if not os.path.exists(__local_dir):
        os.makedirs(__local_dir)
    return __local_dir


def get_local_lib_root_data_path():
    return '{}/data'.format(get_local_lib_root_path())


def get_local_lib_log_path():
    return '{}/log'.format(get_local_lib_root_path())


def get_lib_log_path():
    return '{}/log'.format(ROOT_PATH)


def get_local_pose_library_json_path():
    return '{}/pose_library.json'.format(get_local_lib_root_data_path())


def get_local_camera_library_json_path():
    return '{}/camera_library.json'.format(get_local_lib_root_data_path())


def get_local_pose_library_path():
    return '{}/pose_library'.format(get_local_lib_root_path())


def get_local_camera_library_path():
    return '{}/camera_library'.format(get_local_lib_root_path())


def get_db_pose_library_data():
    json_dir = '{}/db_pose'.format(get_lib_root_data_path())
    json_files = get_json_files_in_dir(json_dir)
    data = []
    for json_file in json_files:
        json_data = read_json_file(json_file)
        data.extend(json_data)
    return data


def get_json_files_in_dir(json_dir):
    json_files = []
    if not os.path.exists(json_dir):
        return json_files
    for file in os.listdir(json_dir):
        if file.endswith('.json'):
            json_files.append(os.path.join(json_dir, file))
    return json_files


def get_local_pose_library_data():
    json_path = get_local_pose_library_json_path()
    if not os.path.exists(json_path):
        return {}
    data = read_json_file(json_path)
    return data


def get_local_camera_library_data():
    json_path = get_local_camera_library_json_path()
    if not os.path.exists(json_path):
        return {}
    data = read_json_file(json_path)
    return data


def save_local_pose_library(data):
    json_path = get_local_pose_library_json_path()
    if not os.path.exists(os.path.dirname(json_path)):
        os.makedirs(os.path.dirname(json_path))
    backup_json_file(json_path)
    write_json_file(json_path, data)


def save_local_camera_library(data):
    json_path = get_local_camera_library_json_path()
    if not os.path.exists(os.path.dirname(json_path)):
        os.makedirs(os.path.dirname(json_path))
    backup_json_file(json_path)
    write_json_file(json_path, data)


def get_lib_root_data_path():
    return '{}/data'.format(ROOT_PATH)


def get_pose_library_json_path():
    return '{}/pose_library.json'.format(get_lib_root_data_path())


def get_camera_library_json_path():
    return '{}/camera_library.json'.format(get_lib_root_data_path())


def get_character_library_json_path():
    return '{}/character_data.json'.format(get_lib_root_data_path())


def get_pose_library_path():
    return '{}/pose_library'.format(ROOT_PATH)


def get_camera_library_path():
    return '{}/camera_library'.format(ROOT_PATH)


def read_camera_library_json():
    json_path = get_camera_library_json_path()
    if not os.path.exists(json_path):
        return {}
    data = read_json_file(json_path)
    return data


def read_character_library_json():
    json_path = get_character_library_json_path()

    if not os.path.exists(json_path):
        return {}
    data = read_json_file(json_path)
    return data


def read_pose_library_json():
    json_path = get_pose_library_json_path()
    if not os.path.exists(json_path):
        return {}
    data = read_json_file(json_path)
    return data


def get_pose_library_data():
    return read_pose_library_json()


def get_camera_library_data():
    return read_camera_library_json()


def get_character_library_data():
    return read_character_library_json()


def write_pose_library_json(data):
    json_path = get_pose_library_json_path()
    __dir, __file = os.path.split(json_path)
    if not os.path.exists(__dir):
        os.makedirs(__dir)
    backup_json_file(json_path)

    write_json_file(json_path, data)


def copy_file(src, dst):
    if not os.path.exists(src):
        return False
    if not os.path.exists(dst):
        os.makedirs(dst)
    try:
        shutil.copy(src, dst)
        return True
    except Exception as e:
        print(e)
        return False


def get_current_time():
    import datetime
    return datetime.datetime.now().strftime('%Y-%m-%d-%H')


def save_pose_library(data):
    write_pose_library_json(data)


def save_character_library(data):
    write_character_library_json(data)


def save_camera_library(data):
    write_camera_library_json(data)


def write_camera_library_json(data):
    json_path = get_camera_library_json_path()
    if not os.path.exists(os.path.dirname(json_path)):
        os.makedirs(os.path.dirname(json_path))
    write_json_file(json_path, data)


def backup_json_file(json_path):
    current_time = get_current_time()
    __dir, __file = os.path.split(json_path)
    if json_path and os.path.exists(json_path):
        __back_dir = os.path.join(__dir, 'backup', current_time)
        __md5 = Md5().get_md5(json_path)
        __back_file = '{}/{}/{}'.format(__back_dir, __md5, __file)
        __back_file = __back_file.replace('\\', '/')
        return copy_file(json_path, __back_file)
    return False


def write_character_library_json(data):
    json_path = get_character_library_json_path()
    if not os.path.exists(os.path.dirname(json_path)):
        os.makedirs(os.path.dirname(json_path))
    write_json_file(json_path, data)


def read_json_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except:
        return jsonio.read(file_path, rtype='r', hook=None)


def write_json_file(file_path, data):
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        return True
    except:
        return jsonio.write(data, file_path, wtype='w')
