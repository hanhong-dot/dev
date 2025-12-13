# -*- coding: utf-8 -*-#
# -------------------------------------------------------
# NAME       : load_ai_colider_ui
# Describe   : 说明描述
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2025/6/26__下午5:38
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
from apps.tools.maya.ai_collider_tool import ai_colider_ui
reload(ai_colider_ui)


def load_ai_colider_ui():
    app = QApplication.instance()
    global ai_colider_win
    try:
        ai_colider_win.close()
        ai_colider_win.deleteLater()
    except:
        pass

    if not app:
        app = QApplication(sys.argv)
    win_handle = ai_colider_ui.AiColiderUI(convex_type=[1,6])

    ai_colider_win = basewindow.BaseWindow(_mayaview.get_maya_window(), "Ai Coloder Tool", "AI碰撞体工具")

    ai_colider_win.set_central_widget(win_handle)

    # ai_colider_win.setMinimumSize(450, 450)
    ai_colider_win.show()
    win_handle.CloseSignal.connect(load_ai_colider_ui)
    app.exec_()
