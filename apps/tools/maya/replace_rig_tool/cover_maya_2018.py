# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       :
# Describe   :
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2025/2/28__17:48
# -------------------------------------------------------
import os
import sys
sys.path.append('Z:/dev')

from lib.common import fileio as fileio


def cover_animation(file_path, save_path):
    pre_process(file_path, save_path)
    return process_file(file_path, save_path)


def process_file(file_path, save_path):
    from method.maya.common.file import BaseFile

    __handle = BaseFile()

    try:
        __handle.open_file(file_path)
    except:
        pass
    try:
        __handle.save_file(save_path)
    except:
        return False, 'save file fail'
    if os.path.exists(save_path):
        return True, save_path
    return False, 'save file fail'


def pre_process(file_path, save_path):
    if not save_path:
        return False, 'save path is None'
    if os.path.exists(save_path):
        try:
            os.remove(save_path)
        except:
            pass
    save_dir = os.path.dirname(save_path)

    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    _data = read_file(file_path)
    if not _data:
        return False, 'read file fail'
    _data = cover_version(_data)
    if not _data:
        return False, 'cover version fail'

    _data = cover_color_manage(_data)
    if not _data:
        return False, 'cover color manage fail'
    write_file(save_path, _data)


def cover_version(data):
    return data.replace("//Maya ASCII 2023 scene", "//Maya ASCII 2018 scene").replace('requires maya "2023"',
                                                                                      'requires maya "2018"').replace(
        'fileInfo "product" "Maya 2023";', 'fileInfo "product" "Maya 2018";').replace('fileInfo "version" "2023";',
                                                                                      'fileInfo "version" "2018";')


def cover_color_manage(data):
    data = data.replace('setAttr ".cfe" yes;', 'setAttr ".cme" no;')
    data = data.replace('setAttr ".vtn" -type "string" "sRGB gamma (legacy)";', '')
    data = data.replace('setAttr ".vn" -type "string" "sRGB gamma";', 'setAttr ".ovt" no;')
    data = data.replace('setAttr ".wsn" -type "string" "scene-linear Rec 709/sRGB";', 'setAttr ".ovt" no;')
    data = data.replace('setAttr ".dn" -type "string" "legacy";', '')
    data = data.replace('setAttr ".otn" -type "string" "sRGB gamma (legacy)";', '')
    data = data.replace('etAttr ".potn" -type "string" "sRGB gamma (legacy)";', '')
    data = data.replace('-showPlayRangeShades \"on\" \n"', '')
    return data


def read_file(file_path):
    return fileio.read(file_path)


def write_file(file_path, data):
    return fileio.write_without(data, file_path)


if __name__ == '__main__':
    file_path = r'Z:\netrender\animation\submit\FY_AnimCard_Act_Other_FY_D_0036_CC01_05.ma'
    save_path = r'Z:\netrender\animation\submit\FY_AnimCard_Act_Other_FY_D_0036_CC01_05_test.ma'

    pre_process(file_path, save_path)
    # path=r'Z:\netrender\animation\submit\test.txt'
    # print(read_file(path))
