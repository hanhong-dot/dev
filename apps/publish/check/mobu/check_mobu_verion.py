# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       : check_mobu_verion
# Describe   : 说明描述
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2023/5/9__17:55
# -------------------------------------------------------
import lib.common.loginfo as info
import pyfbsdk as fb


class Check(object):

    def __init__(self):
        """
        实例初始化
        """
        super(Check, self).__init__()

        self.tooltip = u'已检测motionbuilder版本'

    def checkinfo(self):
        """
        显示检查信息
        :return:
        """
        _error = self.run()
        _error_list = []
        if _error:
            _error_list.extend(_error)
            return False, info.displayErrorInfo(title=self.tooltip, objList=_error_list)
        else:
            return True, info.displayInfo(title=self.tooltip)

    def run(self):
        u"""

        :return:
        """
        _version=fb.FBSystem().Version
        if _version!=19000.0:
            return [u"当前版本不是2019版本，请检查"]
