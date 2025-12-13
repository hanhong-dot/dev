# -*- coding: utf-8 -*-
# author: linhuan
# file: load_mb_replace_character_tool.py
# time: 2025/10/20 16:27
# description:
import sys

sys.path.append('Z:/dev')

try:
    from PySide2.QtWidgets import *
    from PySide2.QtGui import *
    from PySide2.QtCore import *
except:
    from PyQt5.QtWidgets import *
    from PyQt5.QtGui import *
    from PyQt5.QtCore import *

import apps.publish.ui.basewindow.basewiondow as basewindow

import apps.tools.motionbuilder.mb_replace_rig.mb_replace_rig_ui as mb_replace_rig_ui

reload(mb_replace_rig_ui)
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


def load_replace_character_ui():
    FBApplication().FBCreate()
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)

    global replace_tools
    try:
        replace_tools.close()
        replace_tools.deleteLater()
    except:
        pass

    replace_tools = basewindow.BaseWindow(get_mainwindows(), title=u"批量替换角色体工具")

    replace_tools.set_central_widget(mb_replace_rig_ui.MBReplaceRigUI())
    replace_tools.set_help(
        url=r"https://papergames.feishu.cn/wiki/OFCRwaw1biTE61kYj98cfwLOn1c?from=from_copylink")
    # replace_tools.set_modal()
    replace_tools.setMinimumSize(650, 300)
    replace_tools.show()
    app.exec_()
