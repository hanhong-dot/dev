# -*- coding: utf-8 -*-#
# -------------------------------------------------------
# NAME       : export_mesh
# Describe   : 说明描述
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2025/6/11__下午6:33
# -------------------------------------------------------
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

from apps.tools.common.export_fbx_mesh.mesh_export_fbx_ui import MeshExportFbxUI


def load_export_single_mesh_tool_ui():
    app = QApplication.instance()
    global export_single_mesh_tool
    try:
        export_single_mesh_tool.close()
        export_single_mesh_tool.deleteLater()
    except:
        pass

    if not app:
        app = QApplication(sys.argv)
    export_single_mesh_tool = basewindow.BaseWindow(title=u"拆分导出单个Mesh FBX工具")
    export_single_mesh_tool.set_central_widget(MeshExportFbxUI())
    # collect.set_help(url=r"https://papergames.feishu.cn/wiki/SavswLVLLinFsAkRuzncIVVenCR?from=from_copylink")
    export_single_mesh_tool.setMinimumSize(400, 150)
    export_single_mesh_tool.show()
    app.exec_()


load_export_single_mesh_tool_ui()
