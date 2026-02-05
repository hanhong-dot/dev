# -*- coding: utf-8 -*-
# author: linhuan
# file: load_uv_transfer_tool.py
# time: 2026/2/5 14:06
# description:
import sys

try:
    from PySide2.QtWidgets import *
    from PySide2.QtGui import *
    from PySide2.QtCore import *
except:
    from PyQt5.QtWidgets import *
    from PyQt5.QtGui import *
    from PyQt5.QtCore import *
import apps.publish.ui.basewindow.basewiondow as basewindow
import apps.launch.maya.interface.mayaview as _mayaview
from apps.tools.maya.uv_transfer_tool import uv_transfer_tool_ui

reload(uv_transfer_tool_ui)


def load_uv_transfer_tool():
    app = QApplication.instance()
    global uv_transfer_window
    try:
        uv_transfer_window.close()
        uv_transfer_window.deleteLater()
    except:
        pass

    if not app:
        app = QApplication(sys.argv)

    win_handle = uv_transfer_tool_ui.UVTransferToolUI()

    uv_transfer_window = basewindow.BaseWindow(_mayaview.get_maya_window(), u"UV对烘工具", u"UV对烘工具")

    uv_transfer_window.set_central_widget(win_handle)
    uv_transfer_window.set_help(url=r"https://papergames.feishu.cn/wiki/Bg8TwhTEri509gkKRJUcsoIDnBw?from=from_copylink")

    uv_transfer_window.setMinimumSize(450, 200)
    uv_transfer_window.show()
    # win_handle.CloseSignal.connect(load_add_group_name_ui)
    app.exec_()
