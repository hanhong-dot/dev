# -*- coding: utf-8 -*-#
# -------------------------------------------------------
# NAME       : load_pose_syn_ui
# Describe   : 说明描述
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2025/6/28__下午6:56
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
from apps.tools.maya.pose_syn_tool import pose_syn_ui
reload(pose_syn_ui)

def load_pose_syn_ui():
    app = QApplication.instance()
    global pose_syn_ui
    try:
        pose_syn_ui.close()
        pose_syn_ui.deleteLater()
    except:
        pass

    if not app:
        app = QApplication(sys.argv)
    win_handle = pose_syn_ui.PoseSynUI()

    pose_syn_ui = basewindow.BaseWindow(_mayaview.get_maya_window(), u"APose模型同步工具", "APose模型同步工具")

    pose_syn_ui.set_central_widget(win_handle)

    pose_syn_ui.setMinimumSize(450, 450)
    pose_syn_ui.show()
    # win_handle.CloseSignal.connect(load_pose_syn_ui)
    app.exec_()
