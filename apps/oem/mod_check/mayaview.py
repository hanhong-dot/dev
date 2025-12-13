# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       : mayaview
# Describe   : 说明描述
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2022/6/8__19:41
# -------------------------------------------------------
try:
    from PySide2.QtWidgets import *
    from PySide2.QtGui import *
    from PySide2.QtCore import *
except:
    from Qt.QtWidgets import *
    from Qt.QtGui import *
    from Qt.QtCore import *

import shiboken2 as shiboken

# except:
#     from PySide import QtCore, QtWidgets
#     from PySide import QtGui as QtWidgets
#     import shiboken as shiboken

import maya.OpenMayaUI as omui
import maya.cmds as cmds
import maya.mel as mel

'''maya窗口抓取函数集
'''
__all__ = ["get_maya_window", "buildin_maya", "restore_ui"]


def get_maya_window():
    '''获取maya主窗口
    '''
    ptr = omui.MQtUtil.mainWindow()
    return shiboken.wrapInstance(long(ptr), QWidget)


# def get_maya_window_point():
#     '''获取maya主窗口
#     '''
#     ptr = omui.MQtUtil.mainWindow()
#     return _shiboken.wrapInstance(long(ptr), QtWidgets.Qwidget)


def buildin_maya(widget):
    '''
    将组件嵌入mayalayout(单列)
    :param widget:qt组件或maya组件
    :return:
    '''

    _layout = cmds.formLayout(p=StaticView.ViewLayout)
    _qtobj = shiboken.wrapInstance(long(omui.MQtUtil.findLayout(_layout)), QObject)
    _qtobj.children()[0].layout().addWidget(widget)
    child = cmds.formLayout(_layout, q=True, childArray=True)
    cmds.formLayout(_layout, edit=True,
                    attachForm=[(child[0], "right", 0),
                                (child[0], "left", 0),
                                (child[0], "top", 0),
                                (child[0], "bottom", 0)])
    cmds.setParent("..")
    return _layout


def restore_ui():
    mel.eval("ShowAttributeEditorOrChannelBox;")
    mel.eval("RestoreUIElements;")
    mel.eval("restoreMainWindowComponents;")


class StaticView(object):
    '''
    maya常用内置窗口名
    '''
    ViewLayout = "Shelf|MainShelfLayout|formLayout16"