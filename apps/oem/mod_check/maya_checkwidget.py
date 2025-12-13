# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       : maya_checkwidget
# Describe   : 说明描述
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2022/6/24__15:57
# -------------------------------------------------------
import os
import sys

try:
    from PySide2.QtWidgets import *
    from PySide2.QtGui import *
    from PySide2.QtCore import *
except:
    from PyQt5.QtWidgets import *
    from PyQt5.QtGui import *
    from PyQt5.QtCore import *

import check_ui as _mayacheckwidget

reload(_mayacheckwidget)
import mayaview as _mayaview

import basewindow.basewiondow as basewindow

reload(basewindow)
import maya.cmds as cmds


class CheckWidget(_mayacheckwidget.CheckWidget):
    def __init__(self, ui=None, parent=None):
        super(CheckWidget, self).__init__(ui=ui, parent=parent)

    def _select_item(self):
        _sels = self._check_listwidget._listwidget.selectedItems()
        if _sels:
            cmds.select(cl=1)
            for name in _sels:
                try:
                    cmds.select(name.text(), add=1)
                except:
                    pass

    def check_all(self):
        _result = self._check_all()
        return _result

    def _check_all(self):
        has_result = []
        _ignore_info = {}
        _ignores = []
        _check_info = {}
        _values = []
        for _widget in self._checkwidgets:
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

        if False not in has_result:
            self._ui.close()
            self._ui.deleteLater()

        return has_result


def current_filename():
    path = cmds.file(q=1, exn=1)
    _filename = ''
    if path:
        _filename = os.path.basename(path)
    if not _filename:
        raise Exception(u'maya文件是否没有文件名'.encode('gbk'))
    return _filename


def current_project():
    return 'X3'


def load_ui():
    # 检测前先保存文件
    save_file()

    app = QApplication.instance()
    global maya_checkwin
    try:
        maya_checkwin.close()
        maya_checkwin.deleteLater()
    except:
        pass

    if not app:
        app = QApplication(sys.argv)
    maya_checkwin = basewindow.BaseWindow(_mayaview.get_maya_window(), u"drama_mdl----check工具")
    checkwidget = CheckWidget(ui=maya_checkwin)
    maya_checkwin.set_central_widget(checkwidget)
    maya_checkwin.set_help(url=r"")
    maya_checkwin.setMinimumSize(600, 900)
    maya_checkwin.show()
    app.exec_()
    return True


def save_file():
    import maya_file as _file
    inf = cmds.confirmDialog(title=u'提示信息', message=u'请确认是否保存当前文件', button=['Yes', 'No'],
                             defaultButton='Yes')
    if inf == 'No':
        return
    _file.BaseFile().save_current_file()


# if __name__ == '__main__':
#     load_ui()
