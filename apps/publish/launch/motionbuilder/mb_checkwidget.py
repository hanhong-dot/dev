# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       : mb_checkwidget
# Describe   : 说明描述
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2023/4/13__12:01
# -------------------------------------------------------
import apps.publish.ui.layout.checkwidget as _checkwidget
import sys
import os

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
import  pyfbsdk as  fb

import apps.publish.ui.basewindow.basewiondow as basewindow
import lib.common as libs
import lib.common.jsonio as jsonio

import method.shotgun.get_task as get_task

import method.maya.common.project_info as _projectinfo


class CheckWidget(_checkwidget.CheckWidget):
    def __init__(self, parent=None, ui=None, load_pub=False):
        super(CheckWidget, self).__init__(parent, ui=ui)
        self.load_pub = load_pub


    def _select_item(self):
        _sels = self._check_listwidget._listwidget.selectedItems()
        # 取消所有选择
        self._clselect()
        # 选择
        _nodes = []
        if _sels:
            for name in _sels:
                try:
                    _nodes.append(str(name.text()))
                except:
                    pass
        if _nodes:
            print(_nodes)
            self._sel_nodes(_nodes)

    def check_all(self, is_publish=False):
        _result = self._check_all(is_publish)
        if self.load_pub == True and False not in _result:
            import apps.publish.launch.motionbuilder.mb_publishwidget as mb_publishwidget
            mb_publishwidget.load_publish_ui()
        return _result

    def _sel_nodes(self, _nodes):
        ComponentList = fb.FBComponentList()
        for i in range(len(_nodes)):
            _nd = _nodes[i].split('::')[-1]
            fb.FBFindObjectsByName(_nd, ComponentList, True, False)
            MilaCharacter = ComponentList[i]
            MilaCharacter.Selected = True

    def _get_sel_nodename(self):
        u"""
        获取选择节点名称
        :return:
        """
        _sels = self._selobjs()
        return [child.LongName for child in _sels if (child and child.LongName)]

    def _clselect(self):
        u"""
        取消所有选择
        :return:
        """
        _sels = self._selobjs()
        try:
            for child in _sels:
                child.Selected = False
        except:
            pass

    def _selobjs(self):
        u"""
        获取所有选择节点
        :return:
        """
        ModelList = fb.FBModelList()
        fb.FBGetSelectedModels(ModelList)
        return ModelList

    def _check_all(self, is_publish=False):
        has_result = []
        config = r"{}/check_config_{}.json".format(libs.pipedata_path(), os.path.splitext(self.filename)[0])
        _ignore_info = {}
        _ignores = []
        _check_info = {}
        _values = []

        if is_publish == True:
            _check_info = jsonio.read(config)
            if _check_info:
                _values = _check_info.values()[0]
        for _widget in self._checkwidgets:
            if is_publish:
                if _values:
                    # if _widget._name in _values:
                    for obj in _values:
                        if _widget._name == obj[0]:
                            _widget._checkbox.setChecked(obj[1])
                            _widget._checkbox.setChecked(obj[1])
            if _widget.is_ignore():
                _ignores.append((_widget._name, True))
                _result = True
                has_result.append(_result)
            else:
                _ignores.append((_widget._name, False))
                if self._checkfixbox.isChecked():
                    _widget.dorecheck()
                _result, _info = _widget.docheck()
                has_result.append(_result)
            if not _result:
                _widget.setHidden(False)
            else:
                if not self._check_displayallbox.isChecked():
                    _widget.setHidden(True)
                else:
                    _widget.setHidden(False)

        if _ignores:
            _ignore_info["ignore_names"] = _ignores
        if _ignore_info:
            jsonio.write(_ignore_info, config)

        if False not in has_result:
            self._ui.close()
            self._ui.deleteLater()

        return has_result


def get_mainwindows():
    return qApp.topLevelWidgets()[0]


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


def load_check_ui(is_publish=False, load_pub=False):
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

        mobu_check = basewindow.BaseWindow(get_mainwindows(), "check panel")
        checkwidget = CheckWidget(_taskdata, ui=mobu_check, load_pub=load_pub)

        mobu_check.set_central_widget(checkwidget)
        mobu_check.set_modal()
        mobu_check.setMinimumSize(600, 900)
        mobu_check.show()
        app.exec_()
        if is_publish:
            checkinfos = checkwidget._check_all(is_publish)
            if False not in checkinfos:
                mobu_check.close()
                mobu_check.deleteLater()

                return False
