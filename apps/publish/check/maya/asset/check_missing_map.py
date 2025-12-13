# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       : check_missing_image
# Describe   : 检查缺失贴图
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2022/6/29__18:15
# -------------------------------------------------------
import lib.maya.analysis.analyze_data as analyze_data
import lib.common.loginfo as info
import os

TEXTURE_ATTR = analyze_data.AnalyData().data["TEXTURE_ATTR"]


class Check(object):
    """
    检查项目当前使用maya软件的相关信息
    """

    def __init__(self):
        """
        实例初始化
        """
        # 即使直接派生自object，最好也调用一下super().__init__，
        # 不然可能造成多重继承时派生层次中某些类的__init__被跳过。
        super(Check, self).__init__()

        self.tooltip = u'已检查缺失贴图'

    def checkinfo(self):
        """
        显示检查信息
        :return:
        """
        _error = self.run()
        _error_list = []
        if _error:
            for k, v in _error.items():
                _error_list.append(u"以下节点")
                _error_list.append(k)
                _error_list.append(u"缺失贴图")
                _error_list.append(v)
            return False, info.displayErrorInfo(title=self.tooltip, objList=_error_list)
        else:
            return True, info.displayInfo(title=self.tooltip)

    def run(self):

        """
        检查maya相关版本信息
        :return:
        """
        import maya.cmds as cmds
        errdict = {}
        for k, v in TEXTURE_ATTR.items():
            _fils = cmds.ls(type=k)
            if _fils:
                for _fil in _fils:
                    _attr = '{}{}'.format(_fil, v)
                    if _attr and cmds.ls(_attr):
                        _img = cmds.getAttr(_attr)
                        if _img and not os.path.exists(_img) or ' ' in _img or _img.startswith('/'):
                            errdict[_fil] = _img
        return errdict

    # </editor-fold>

    def fix(self):
        """
        修复相关内容
        :return:
        """
        import maya.cmds as cmds
        _meshlist = self.run()
        if _meshlist:
            try:
                cmds.delete(_meshlist)
            except:
                pass
