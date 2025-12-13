# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       : check_is_mirror
# Describe   : 检测模型镜像
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2022/6/27__18:51
# -------------------------------------------------------
import lib.common.loginfo as info

import os
import sys
if sys.getdefaultencoding() != 'utf-8':
    reload(sys)
    sys.setdefaultencoding('utf-8')



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

        self.tooltip = u'以下点不是镜像,请检查'

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

        """
        检查maya相关版本信息
        :return:
        """
        import maya.cmds as cmds
        import pymel.core as pm
        # 加载插件
        self._load_ocd_plug()

        polygons = set(mesh.getParent() for mesh in pm.ls(type="mesh"))
        pm.select(polygons)
        cmds.mirror_check()
        return cmds.ls(sl=1, l=1)

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

    def _load_ocd_plug(self):
        import lib.common as lib_common
        import pymel.core as pm
        _root_path = lib_common.root_path()
        _version = int(round(float(pm.about(q=1, v=1))))
        path = u'{}/tools/plug-ins/maya/ocd/maya{}/ocd.mll'.format(_root_path, _version)
        if not os.path.isfile(path):
            return pm.warning(u"can not find ocd")
        if not pm.pluginInfo(u"ocd", q=1, l=1):
            pm.loadPlugin(path)
