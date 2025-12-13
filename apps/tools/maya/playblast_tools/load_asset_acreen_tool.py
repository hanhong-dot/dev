# -*- coding: utf-8 -*-
# author: linhuan
# file: load_asset_acreen_tool.py
# time: 2025/11/5 17:49
# description:

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

import apps.tools.maya.playblast_tools.asset_screen_tool_ui as asset_screen_tool_ui
reload(asset_screen_tool_ui)

def load_asset_screen_tool_ui():
    app = QApplication.instance()
    global asset_screen_tool_ui
    try:
        asset_screen_tool_ui.close()
        asset_screen_tool_ui.deleteLater()
    except:
        pass

    if not app:
        app = QApplication(sys.argv)
    win_handle = asset_screen_tool_ui.AssetScreenToolUI()

    asset_screen_tool_ui = basewindow.BaseWindow(_mayaview.get_maya_window(), u"资产截屏工具", "资产截屏工具")

    asset_screen_tool_ui.set_central_widget(win_handle)

    asset_screen_tool_ui.set_help("https://papergames.feishu.cn/wiki/DeJPwQWH9igIMNkjUs4ciFusnYV?from=from_copylink")

    asset_screen_tool_ui.setMinimumSize(300, 250)
    asset_screen_tool_ui.show()
    # win_handle.CloseSignal.connect(load_asset_screen_tool_ui)
    app.exec_()