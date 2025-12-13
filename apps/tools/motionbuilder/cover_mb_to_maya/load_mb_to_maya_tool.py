# -*- coding: utf-8 -*-
# author: linhuan
# file: load_mb_to_maya_tool.py
# time: 2025/11/27 14:44
# description:
import sys

#
# sys.path.append('Z:/dev')

try:
    from PySide2.QtWidgets import *
    from PySide2.QtGui import *
    from PySide2.QtCore import *
except:
    from PyQt5.QtWidgets import *
    from PyQt5.QtGui import *
    from PyQt5.QtCore import *

import apps.publish.ui.basewindow.basewiondow as basewindow

import apps.tools.motionbuilder.cover_mb_to_maya.mb_to_maya_ui as cover_mb_to_maya_ui

reload(cover_mb_to_maya_ui)
from pyfbsdk import *


def get_mainwindows():
    try:
        main_window = QApplication.activeWindow()
        while True:
            last_win = main_window.parent()
            if last_win:
                main_window = last_win
            else:
                break
        return main_window
    except:
        pass


def load_cover_mb_to_maya_tool():
    FBApplication().FBCreate()
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)

    global cover_mb_to_maya_tools
    try:
        cover_mb_to_maya_tools.close()
        cover_mb_to_maya_tools.deleteLater()
    except:
        pass

    cover_mb_to_maya_tools = basewindow.BaseWindow(get_mainwindows(), title=u"MbToMaya工具")

    cover_mb_to_maya_tools.set_central_widget(cover_mb_to_maya_ui.CoverMBToMayaUI())
    cover_mb_to_maya_tools.set_help(url=r"https://papergames.feishu.cn/wiki/B5ZHwbQGZicmtJkEEjDc4JFZnMA?from=from_copylink")
    # cover_mb_to_maya_tools.set_modal()

    # cover_mb_to_maya_tools.setMinimumSize(400, 350)
    cover_mb_to_maya_tools.show()
    app.exec_()
