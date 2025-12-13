# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       : check_exist_binpose
# Describe   : 检测文件中是否存在BinPose节点
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2022/7/15__10:08
# -------------------------------------------------------
import maya.cmds as cmds
import lib.common.loginfo as info
from lib.maya.node.grop import BaseGroup
from method.maya.common.file import BaseFile




class Check(object):
    """
    检查项目当前使用maya软件的相关信息
    """

    def __init__(self):
        """
        """
        super(Check, self).__init__()

        self.tooltip = u'已强制清理文件,请检查文件'
        self.error=u'强制清理文件失败,请检查文件'

    def checkinfo(self):
        """
        显示检查信息
        :return:
        """
        _error = self.run()

        if _error==True:
            return True, info.displayInfo(title=self.tooltip)
        else:
            return False, info.displayErrorInfo(title=self.error)

    def run(self):

        """
        :return:
        """
        resutl=True
        file_name= cmds.file(q=1, exn=1)
        groups=BaseGroup().get_root_groups()
        if groups:
            try:
                BaseFile().export_file(groups,file_name)
                resutl=True
            except:
                resutl=False
            BaseFile().open_file(file_name)
        return resutl




