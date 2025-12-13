# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       : process_mb_fbx
# Describe   : 处理maya 中导出的_MB.fbx文件
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2023/8/7__19:09
# -------------------------------------------------------
import os

import sys

import time

sys.path.append(r'Z:\dev\tools\x3_P4\scripts\adPose2_FKSdk\adPose2\adPose_mb')
sys.path.append(r'Z:\dev')
sys.path.append(r'C:\Program Files\Autodesk\MotionBuilder 2019\bin\x64')

import lib.common.fileio as fileio

reload(fileio)
import method.common.dir as _dir

from lib.mobu import mbfile
from pyfbsdk import *

FBX_FILE_EVENT = 'FBX_FILE_PATH'


def run():
    # print 'FBX_FILE_EVENT'
    # print os.environ[FBX_FILE_EVENT]
    fbx_file = read_fbx_file()
    if not fbx_file or not os.path.exists(fbx_file):
        return
    process_fbx(str(fbx_file))
    # del os.environ[FBX_FILE_EVENT]


def process_fbx(fbx_file):
    open_fbx_file(fbx_file)
    FBSystem().Scene.Evaluate()
    time.sleep(3)
    process_fbx_file()
    FBSystem().Scene.Evaluate()
    time.sleep(3)
    save_fbx_file(fbx_file)

    return fbx_file


def merge_fbx_file(fbx_file):
    """
    合并fbx文件
    :param fbx_file: 文件路径+文件名
    :return:
    """
    mbfile.mb_merge_file(fbx_file, settake=False)

    return fbx_file


def open_fbx_file(fbx_file):
    """
    打开fbx文件
    :param fbx_file: 文件路径+文件名
    :return:
    """
    mbfile.mb_open_file(fbx_file)

    return fbx_file


def save_fbx_file(fbx_file):
    """
    保存fbx文件
    :param fbx_file: 文件路径+文件名
    :return:
    """
    mbfile.mb_save_file(fbx_file)

    return fbx_file


def get_local_file():
    local_dir = _dir.get_localtemppath("MB_FBX_INFO")
    if not os.path.exists(local_dir):
        os.makedirs(local_dir)
    return '{}/info.txt'.format(local_dir)


def read_fbx_file():
    fbx_info_file = get_local_file()
    return fileio.read(fbx_info_file)


def process_fbx_file():
    import ad_main
    reload(ad_main)
    ad_main.ad_main()
    # import ad_main.admin
    # import mb_control_core, mb_hik_core, ad_core, ad_neck_untwist
    # import ad_twist_bs_driver
    # reload(ad_twist_bs_driver)
    # reload(mb_control_core)
    # reload(mb_hik_core)
    # reload(ad_core)
    # reload(ad_neck_untwist)
    # mb_control_core.main()
    # ad_core.main()
    # mb_hik_core.main()
    # ad_neck_untwist.main()
    # ad_twist_bs_driver.main()





run()

# if __name__ == '__main__':
#     mb=r'C:\Program Files\Autodesk\MotionBuilder 2019\bin\x64\motionbuilder.exe'
#     fbx_file=r'E:\testtt\YS001S_CLOSE_MB.fbx'
#     # cmd='"{}" -batch -noconsole -file "{}"'.format(mb,fbx_file)
#     cmd=mb
#     os.system(cmd)
