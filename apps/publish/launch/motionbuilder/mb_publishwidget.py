# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       : mb_publishwidget
# Describe   : motionbuilder发布窗口
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2023/4/13__12:00
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
import apps.publish.ui.layout.publishwidget as _pwidget
import apps.publish.ui.basewindow.basewiondow as basewindow

import method.shotgun.get_task as get_task

import method.maya.common.project_info as _projectinfo

reload(_pwidget)


def current_filename():
    u"""
    获取当前文件名
    :return:
    """
    return FBApplication().FBXFileName


def get_taskdata():
    scene = current_filename()
    if scene:
        return get_task.TaskInfo(scene, _projectinfo.current_project(), 'motionbuilder', 'version', is_lastversion=True)


def get_mainwindows():
    return qApp.topLevelWidgets()[0]


def load_publish_ui():
    _taskdata = get_taskdata()
    if not _taskdata:
        title = "Error"
        information = "Current scene,unable to parse correct task information,please check"
        FBMessageBox(title, information, "OK")
    else:
        FBApplication().FBCreate()
        app = QApplication.instance()
        if not app:
            app = QApplication(sys.argv)

        mobu_publish = basewindow.BaseWindow(get_mainwindows(), "publish panel")

        mobu_publish.set_central_widget(_pwidget.PublishWidget(_taskdata))
        mobu_publish.set_modal()
        mobu_publish.setMinimumSize(600, 900)
        mobu_publish.show()
        app.exec_()


if __name__ == '__main__':
    load_publish_ui()
