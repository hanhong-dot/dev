# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       : reference
# Describe   : 获得参考信息
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2022/7/13__10:37
# -------------------------------------------------------
import maya.cmds as cmds
import os


def reference_info_dict(load=True):
    u"""
    文件参考信息(最外层参考信息)
    :param load: 为True时，只读取load的参考，为False时，读取所有参考(没有load的参考也读取)
    :return:
    """
    refs = cmds.file(q=1, r=1)
    result = {}
    if not refs:
        pass

    for ref in refs:
        refRN = cmds.referenceQuery(ref, referenceNode=1)
        _isload = cmds.referenceQuery(refRN, isLoaded=1)
        if (_isload and load == 1) or load == 0:
            refPath = ref
            ns = cmds.file(refPath, namespace=1, q=1)
            if '{' in refPath:
                refPath = refPath.split('{')[0]
            if os.path.exists(refPath):
                result[ns] = [refRN, refPath]
    return result
