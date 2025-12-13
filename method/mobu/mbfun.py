# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       : mbfun
# Describe   : mb
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2023/5/11__17:37
# -------------------------------------------------------
import  pyfbsdk as  fb
def cl_select():
    u"""
    取消所有选择
    :return:
    """
    _sels = get_selobjs()
    try:
        for child in _sels:
            child.Selected = False
    except:
        pass


def get_selobjs():
    u"""
    获取所有选择节点
    :return:
    """
    ModelList = fb.FBModelList()
    fb.FBGetSelectedModels(ModelList)
    return ModelList