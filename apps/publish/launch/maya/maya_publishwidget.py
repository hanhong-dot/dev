# -*- coding: utf-8 -*-#
# Python       : python 2.7.16
# -------------------------------------------------------------------------------
# NAME         : publishwidget
# Describe     : 说明描述
# Version      : v0.01
# Author       : linhuan
# Email        : hanhong@papegames.net
# DateTime     : 2022.2.22__16:37
# -------------------------------------------------------------------------------
# -------------------------------------------------------------------------------
# example:
# 
# -------------------------------------------------------------------------------

__AUTHORZH__ = u"韩虹"
__AUTHOR__ = "linhuan"
__EMAIL__ = "hanhong@papegames.net"

try:
    from PySide2.QtWidgets import *
    from PySide2.QtGui import *
    from PySide2.QtCore import *
except:
    from Qt.QtWidgets import *
    from Qt.QtGui import *
    from Qt.QtCore import *

import apps.publish.ui.layout.publishwidget as _pwidget

reload(_pwidget)

import apps.launch.maya.interface.mayaview as _mayaview
import method.shotgun.get_task as get_task
reload(get_task)

import apps.publish.ui.basewindow.basewiondow as basewindow
import method.maya.common.project_info as _projectinfo
import apps.publish.util.analyze_xml as _get_data
import apps.publish.launch.maya.maya_checkwidget as maya_checkwidget
import apps.publish.ui.message.messagebox as _messagebox

import maya.cmds as cmds
import os
import sys


class PublishWidget(_pwidget.PublishWidget):
    def __init__(self, task_data, parent=None):
        super(PublishWidget, self).__init__(task_data, parent)
        self.task_data = task_data
        self._analyse_data = _get_data.GetXLMData(self.task_data)

    def _show_proiteminfo(self, widget):
        self._clearInfo()
        # _widget_name = widget.name()
        if not os.path.exists(os.path.dirname(self._processlogfile(widget.objectName()))):
            os.makedirs(os.path.dirname(self._processlogfile(widget.objectName())))
        cmds.scriptEditorInfo(clearHistoryFile=True, historyFilename=self._processlogfile(widget.objectName()),
                              writeHistory=True)

    def _show_proiteminfo2(self, widget):
        with open(self._processlogfile(widget.objectName()), 'r') as f:
            contents = f.read().splitlines()
            for content in contents:
                self._listwidget._listwidget.addItem(content.decode('gbk'))
        cmds.scriptEditorInfo(writeHistory=False)

    def _show_proallinfo(self):
        self._clearInfo()
        self._listwidget._listwidget.addItem(u'全部处理:')
        if not os.path.exists(os.path.dirname(self._processlogfile(self._process_alllogname))):
            os.makedirs(os.path.dirname(self._processlogfile(self._process_alllogname)))
        cmds.scriptEditorInfo(clearHistoryFile=True, historyFilename=self._processlogfile(self._process_alllogname),
                              writeHistory=True)

    def _show_proallinfo2(self):
        with open(self._processlogfile(self._process_alllogname), 'r') as f:
            contents = f.read().splitlines()
            for content in contents:
                self._listwidget._listwidget.addItem(content.decode('gbk'))
        cmds.scriptEditorInfo(writeHistory=False)


def current_filename():
    path = cmds.file(q=1, exn=1)
    _filename = ''
    if path:
        _filename = os.path.basename(path)
    if not _filename:
        raise Exception(u'maya文件是否没有文件名'.encode('gbk'))
    return _filename


def _user_authentication(_task_data):
    _user_authentication = _pwidget.PublishWidget(_task_data)._user_authentication()
    #
    if not _user_authentication or _user_authentication != True:
        _messagebox.msgview(u"这个任务没有分配给你，请联系leader或PM", 1)
        raise Exception(u"这个任务没有分配给你，请联系leader或PM".encode('gbk'))


def load_ui():
    _task_data = get_task.TaskInfo(current_filename(), _projectinfo.current_project(), 'maya', 'version')
    # 任务状态检查
    _task_status_check(_task_data)
    # 用户验证
    _user_authentication(_task_data)
    _is_result = maya_checkwidget.load_ui(_task_data, True, True)
    # 暂时添加
    # _is_result=''
    cmds.select(cl=1)
    if not _is_result:
        load_publish_ui(_task_data)


def _task_status_check(_task_data):
    _task_status = _task_data.task_status
    if _task_status and _task_status in ['omt']:
        _messagebox.msgview(u"任务状态为omt,已锁定,请联系leader或PM", 1)
        raise Exception(u"任务状态为omt,已锁定,请联系leader或PM".encode('gbk'))


def load_publish_ui(_task_data):
    cmds.select(cl=1)
    app = QApplication.instance()
    global maya_publish
    try:
        maya_publish.close()
        maya_publish.deleteLater()
    except:
        pass

    if not app:
        app = QApplication(sys.argv)
    maya_publish = basewindow.BaseWindow(_mayaview.get_maya_window(), "publish panel")

    maya_publish.set_central_widget(
        PublishWidget(_task_data))
    maya_publish.set_modal()
    maya_publish.setMinimumSize(600, 900)
    maya_publish.show()
    app.exec_()


if __name__ == '__main__':
    load_ui()
