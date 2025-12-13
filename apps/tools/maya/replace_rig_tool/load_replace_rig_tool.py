# -*- coding: utf-8 -*-
# -----------------------------------
# @File    :
# @Author  : linhuan
# @Time    : 2025/10/10 18:01
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
from apps.tools.maya.replace_rig_tool import replace_rig_tool_ui
reload(replace_rig_tool_ui)

def load_replace_rig_tool():
    app = QApplication.instance()
    global replace_rig_tool_ui
    try:
        replace_rig_tool_ui.close()
        replace_rig_tool_ui.deleteLater()
    except:
        pass

    if not app:
        app = QApplication(sys.argv)
    win_handle = replace_rig_tool_ui.ReplaceRigToolUI()

    replace_rig_tool_ui = basewindow.BaseWindow(_mayaview.get_maya_window(), u"批量替换角色绑定", "批量替换角色绑定")

    replace_rig_tool_ui.set_central_widget(win_handle)
    replace_rig_tool_ui.set_help(url=r"https://papergames.feishu.cn/wiki/OFCRwaw1biTE61kYj98cfwLOn1c?from=from_copylink")

    replace_rig_tool_ui.setMinimumSize(450, 250)
    replace_rig_tool_ui.show()
    # win_handle.CloseSignal.connect(load_replace_rig_tool)
    app.exec_()
