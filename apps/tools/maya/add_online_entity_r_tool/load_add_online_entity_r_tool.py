# -*- coding: utf-8 -*-
# author: linhuan
# file: load_add_online_entity_r_tool.py
# time: 2026/2/2 16:29
# description:
import sys
from apps.publish.ui.message.messagebox import msgview
import maya.cmds as cmds
import apps.publish.ui.basewindow.basewiondow as basewindow
from apps.tools.maya.add_online_entity_r_tool import add_online_entity_r_ui
reload(add_online_entity_r_ui)
import method.shotgun.get_task as get_task
import apps.launch.maya.interface.mayaview as _mayaview
from database.shotgun.core.sg_analysis import Config

try:
    from PySide2.QtWidgets import *
    from PySide2.QtGui import *
    from PySide2.QtCore import *
except:
    from Qt.QtWidgets import *
    from Qt.QtGui import *
    from Qt.QtCore import *


def load_add_online_entity_r_tool():
    app = QApplication.instance()
    global auto_copy_skin_tool
    try:
        auto_copy_skin_tool.close()
        auto_copy_skin_tool.deleteLater()
    except:
        pass

    if not app:
        app = QApplication(sys.argv)


    win_handle = add_online_entity_r_ui.AddOnlineEntityRUI()
    add_online_entity_r_tool = basewindow.BaseWindow(_mayaview.get_maya_window(), u"更新在线版本工具", "更新在线版本")

    add_online_entity_r_tool.set_central_widget(win_handle)

    # add_online_entity_r_tool.set_help("https://papergames.feishu.cn/wiki/IxoNw1IjPiahBAkyaBAcDbP2nwc?from=from_copylink")

    add_online_entity_r_tool.setMinimumSize(350, 200)
    add_online_entity_r_tool.show()
    # win_handle.CloseSignal.connect(load_asset_screen_tool_ui)
    app.exec_()
