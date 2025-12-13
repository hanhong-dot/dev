# -*- coding: utf-8 -*-
# -----------------------------------
# @File    : load_add_group_name_ui.py
# @Author  : linhuan
# @Time    : 2025/7/5 14:38
# @Description : 
# -----------------------------------
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
from apps.tools.maya.xgen_tool import add_xgen_group_name_attr_ui
reload(add_xgen_group_name_attr_ui)
def load_add_group_name_ui():
    app = QApplication.instance()
    global add_group_name_window
    try:
        add_group_name_window.close()
        add_group_name_window.deleteLater()
    except:
        pass

    if not app:
        app = QApplication(sys.argv)

    win_handle = add_xgen_group_name_attr_ui.AddXgenGroupNameAttrUI()

    add_group_name_window = basewindow.BaseWindow(_mayaview.get_maya_window(), "Add Xgen Group Name Tool", "Xgen 描述添加Group Name属性工具")

    add_group_name_window.set_central_widget(win_handle)
    add_group_name_window.set_help(url=r"https://papergames.feishu.cn/wiki/SeQdwazFHiX6VmkcVLGcFq53naf?from=from_copylink")

    add_group_name_window.setMinimumSize(400, 260)
    add_group_name_window.show()
    # win_handle.CloseSignal.connect(load_add_group_name_ui)
    app.exec_()