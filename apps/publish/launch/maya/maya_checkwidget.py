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
    from Qt.QtWidgets import *
    from Qt.QtGui import *
    from Qt.QtCore import *

import apps.publish.ui.layout.checkwidget as _mayacheckwidget

reload(_mayacheckwidget)
import apps.launch.maya.interface.mayaview as _mayaview
import method.shotgun.get_task as _get_task
import method.maya.common.project_info as _projectinfo
import apps.publish.ui.basewindow.basewiondow as basewindow
import maya.cmds as cmds
import lib.common.jsonio as jsonio
import lib.common as libs

class CheckWidget(_mayacheckwidget.CheckWidget):
    def __init__(self, parent=None, ui=None, load_pub=False):
        super(CheckWidget, self).__init__(parent, ui=ui)
        self.load_pub = load_pub
    def _select_item(self):
        _sels = self._check_listwidget._listwidget.selectedItems()
        if _sels:
            cmds.select(cl=1)
            for name in _sels:
                try:
                    cmds.select(name.text(), add=1)
                except:
                    pass

    def check_all(self,is_publish=False):
        _result=self._check_all(is_publish)
        if self.load_pub==True and False not in _result:
            import apps.publish.launch.maya.maya_publishwidget as maya_publishwidget
            maya_publishwidget.load_publish_ui(self.task_data)
        return _result



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


def current_filename():
    path = cmds.file(q=1, exn=1)
    _filename = ''
    if path:
        _filename = os.path.basename(path)
    if not _filename:
        raise Exception(u'maya文件是否没有文件名'.encode('gbk'))
    return _filename


def current_project():
    return _projectinfo.current_project()



def load_ui(_task_data=None,is_publish=False,load_pub=False):
    if not _task_data:
        _task_data = _get_task.TaskInfo(current_filename(), current_project(), 'maya', 'version', is_lastversion=True)
    #
    check_name()

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
    maya_checkwin = basewindow.BaseWindow(_mayaview.get_maya_window(), u"%s----check工具" % _task_data.task_name)
    checkwidget = CheckWidget(_task_data, ui=maya_checkwin,load_pub=load_pub)
    maya_checkwin.set_central_widget(checkwidget)
    maya_checkwin.set_help(url=r"http:..10.98.98.211:8090.pages")
    maya_checkwin.setMinimumSize(600, 900)
    maya_checkwin.show()
    app.exec_()
    if is_publish:
        checkinfos = checkwidget._check_all(is_publish)
        if False not in checkinfos:
            maya_checkwin.close()
            maya_checkwin.deleteLater()

            return False
    return True

def check_name():
    _filename=cmds.file(q=1,exn=1)
    if not _filename or  ('/work/' not in _filename and '\\work\\' not in _filename):

        cmds.confirmDialog(title=u'错误信息', message=u'<font color=gold><h3>当前文件未用Work工具保存,请用Work Save工具保存', button=['Yes'],
                                 defaultButton='Yes')
        cmds.error(u'当前文件未用Work工具保存,请用Work Save工具保存')

def save_file():
    import method.maya.common.file as _file
    inf = cmds.confirmDialog(title=u'提示信息', message=u'请确认是否保存当前文件', button=['Yes', 'No'],
                             defaultButton='Yes')
    if inf == 'No':
        return
    _file.BaseFile().save_current_file()


if __name__ == '__main__':
    load_ui()
