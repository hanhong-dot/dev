# -*- coding: utf-8 -*-
# author: linhuan
# file: load_auto_copy_skin_tool.py
# time: 2025/12/13 14:22
# description:

import sys
from apps.publish.ui.message.messagebox import msgview
import maya.cmds as cmds
import apps.publish.ui.basewindow.basewiondow as basewindow
from apps.tools.maya.auto_copy_skin_tool import auto_copy_skin_ui
reload(auto_copy_skin_ui)
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


def get_task_data():
    __file_path = cmds.file(q=True, exn=True)
    if not __file_path:
        msgview(u"请先保存场景文件！", 0)
        return None
    task_data = get_task.TaskInfo(__file_path, 'X3', 'maya', 'publish', thumbnail_down=False, is_lastversion=False,
                                  ui=False, batch=False)
    if not task_data:
        msgview(u"无法获取任务信息，请检查场景文件路径是否正确！", 0)
        return None
    return task_data


def load_auto_copy_skin_tool():
    app = QApplication.instance()
    global auto_copy_skin_tool
    try:
        auto_copy_skin_tool.close()
        auto_copy_skin_tool.deleteLater()
    except:
        pass

    if not app:
        app = QApplication(sys.argv)

    try:
        task_data = get_task_data()
    except:
        msgview(u"无法获取任务信息，请检查场景文件命名是否正确！", 0)
        return
    if not task_data:
        return
    sg = Config().login()

    win_handle = auto_copy_skin_ui.AutoCopySkinUI(sg, task_data)
    auto_copy_skin_tool = basewindow.BaseWindow(_mayaview.get_maya_window(), u"自动蒙皮工具", "自动蒙皮工具")

    auto_copy_skin_tool.set_central_widget(win_handle)

    auto_copy_skin_tool.set_help("https://papergames.feishu.cn/wiki/IxoNw1IjPiahBAkyaBAcDbP2nwc?from=from_copylink")

    auto_copy_skin_tool.setMinimumSize(200, 200)
    auto_copy_skin_tool.show()
    # win_handle.CloseSignal.connect(load_asset_screen_tool_ui)
    app.exec_()
