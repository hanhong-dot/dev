# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       : sub_assets_ui
# Describe   : 说明描述
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2023/12/12__14:41
# -------------------------------------------------------

from apps.tools.maya.sub_assets_republish import base_dialog
reload(base_dialog)

import sys

try:
    from PySide2.QtWidgets import *
    from PySide2.QtGui import *
    from PySide2.QtCore import *
except:
    from Qt.QtWidgets import *
    from Qt.QtGui import *
    from Qt.QtCore import *
import apps.publish.ui.basewindow.basewiondow as basewindow
import apps.launch.maya.interface.mayaview as _mayaview
import database.shotgun.core.sg_analysis as sg_analysis
import method.maya.common.project_info as _projectinfo

def load_sub_assets_tool_ui():

    sg = sg_analysis.Config().login()

    app = QApplication.instance()
    global maya_sub_assets
    try:
        maya_sub_assets.close()
        maya_sub_assets.deleteLater()
    except:
        pass

    if not app:
        app = QApplication(sys.argv)
    maya_sub_assets = basewindow.BaseWindow(_mayaview.get_maya_window(), "SubAssets Republish")

    maya_sub_assets.set_central_widget(base_dialog.SubAssetsInfoDialog(sg, get_task_id()))
    maya_sub_assets.set_modal()
    maya_sub_assets.setMinimumSize(600, 450)
    maya_sub_assets.show()
    app.exec_()

def get_task_id():
    import maya.cmds as cmds
    import method.shotgun.get_task as get_task
    file_name=cmds.file(q=True,exn=True)
    if not file_name:
        raise Exception(u'当前文件是空文件，请打开文件后再执行此操作')
    task_data=get_task.TaskInfo(file_name, _projectinfo.current_project(), 'maya', 'version',is_lastversion=False)
    if not task_data:
        raise Exception(u'当前文件无法解析出正确的任务信息，请检查文件名是否正确')
    return task_data.task_id


