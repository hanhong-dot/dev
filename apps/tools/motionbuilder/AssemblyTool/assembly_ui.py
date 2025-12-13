# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       : assembly_ui
# Describe   : 说明描述
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2023/3/20__15:28
# -------------------------------------------------------
import sys

try:
    from PySide2 import QtCore
    from PySide2.QtWidgets import *
    from PySide2.QtGui import *
    from PySide2.QtCore import *
except:
    from Qt.QtWidgets import *
    from Qt.QtGui import *
    from Qt.QtCore import *

from pyfbsdk import FBApplication
from pyfbsdk import FBMessageBox
from pyfbsdk_additions import *
import apps.tools.common.shot_tools.shot_dialog as shot_dialog
import method.shotgun.get_task as get_task
import method.maya.common.project_info as _projectinfo
import apps.tools.common.shot_tools.cover_taskdata as cover_taskdata
import apps.publish.ui.basewindow.basewiondow as basewindow



def get_scene():
    u"""
    获取当前文件名
    :return:
    """
    return FBApplication().FBXFileName


def get_taskdata():
    scene = get_scene()
    if scene:
        return get_task.TaskInfo(scene, _projectinfo.current_project(), 'motionbuilder', 'version',
                                 is_lastversion=False)
def get_mainwindows():
    return qApp.topLevelWidgets()[0]

def show():
    _taskdata = get_taskdata()
    if not _taskdata:
        title = "Error"
        information = "Current scene,unable to parse correct task information,please check"
        FBMessageBox(title, information,"OK")
    else:
        FBApplication().FBCreate()
        entity_list = cover_taskdata.cover_taskdata(_taskdata)
        app = QApplication.instance()
        if not app:
            app = QApplication(sys.argv)

        mobu_publish = basewindow.BaseWindow(get_mainwindows(), "assembly panel")

        mobu_publish.set_central_widget(shot_dialog.ShotInfoDialog(entity_list,dcc='motionbuilder'))
        mobu_publish.set_modal()
        mobu_publish.setMinimumSize(900, 700)
        mobu_publish.show()
        app.exec_()


