# -*- coding: utf-8 -*-#
# -------------------------------------------------------
# NAME       : load_open_claw_ui
# Describe   : OpenClaw工具入口
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2026/3/10
# -------------------------------------------------------
try:
    from PySide2.QtWidgets import *
    from PySide2.QtGui import *
    from PySide2.QtCore import *
except:
    from PyQt5.QtWidgets import *
    from PyQt5.QtGui import *
    from PyQt5.QtCore import *

import sys
import apps.publish.ui.basewindow.basewiondow as basewindow
import apps.launch.maya.interface.mayaview as _mayaview
from apps.tools.maya.open_claw_tool import open_claw_ui

reload(open_claw_ui)


def load_open_claw_ui():
    app = QApplication.instance()
    global open_claw_win
    try:
        open_claw_win.close()
        open_claw_win.deleteLater()
    except:
        pass

    if not app:
        app = QApplication(sys.argv)

    win_handle = open_claw_ui.OpenClawUI()

    open_claw_win = basewindow.BaseWindow(_mayaview.get_maya_window(), "Open Claw Tool", u"OpenClaw工具")

    open_claw_win.set_central_widget(win_handle)

    open_claw_win.setMinimumSize(400, 350)
    open_claw_win.show()
    app.exec_()
