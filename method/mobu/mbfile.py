# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       : mbfile
# Describe   : mb 文件处理
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2023/4/26__19:28
# -------------------------------------------------------

from pyfbsdk import FBApplication
from pyfbsdk_additions import *
from pyfbsdk import FBFbxOptions


def mb_current_file():
    u"""
    当前文件名(文件路径+文件名)
    :return:
    """
    return FBApplication().FBXFileName


def mb_save_file(_file):
    u"""
    保存文件
    :param _file: 文件路径+文件名
    :return:
    """
    FBApplication().FileSave(_file)


def mb_new_file():
    u"""
    生成一个空的maya文件
    :return:
    """
    FBApplication().FileNew()


def mb_open_file(_file):
    u"""
    打开文件
    :param _file: 文件路径+文件名
    :return:
    """
    FBApplication().FileOpen(_file)


def mb_merge_file(_file, settake=False):
    u"""
    合并文件
    :param _file: 文件路径+文件名
    :return:
    """
    fbxLoadOptions = FBFbxOptions(True)
    if settake == True:
        for takeIndex in range(0, fbxLoadOptions.GetTakeCount()):
            fbxLoadOptions.SetTakeSelect(takeIndex, 0)

    fbxLoadOptions.FileMerge(_file, False, fbxLoadOptions)
