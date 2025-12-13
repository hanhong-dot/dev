# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       : check_take
# Describe   : 检测take(需要为唯一,且命名为Take 001)
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2023/5/9__18:47
# -------------------------------------------------------
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

TAKE = 'Take 001'


class Check(object):

    def __init__(self):
        """
        实例初始化
        """
        super(Check, self).__init__()

        self.tooltip = u'已检测文件中Take'

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
        _error = []
        takeList = []
        for take in fb.FBSystem().Scene.Takes:
            takeList.append(take.Name)
        if not takeList:
            _error.append(u"文件中没有Take")
        elif len(takeList) > 1:
            _error.append(u"文件中有多个Take")
            _error.extend(takeList)
        elif takeList[0] != TAKE:
            _error.append(u"文件中Take命名不正确,请命名为Take 001")
            _error.extend(takeList)
        return _error
# print(Check().checkinfo())
