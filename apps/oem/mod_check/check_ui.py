try:
    from PySide2.QtWidgets import *
    from PySide2.QtGui import *
    from PySide2.QtCore import *
except:
    from PyQt5 import QtCore
    from PyQt5.QtWidgets import *
    from PyQt5.QtGui import *
    from PyQt5.QtCore import *

import check_bottom
reload(check_bottom)
import listwidget
reload(listwidget)
import check_tabwidget as multi_tabwidget
reload(multi_tabwidget)


import os
from functools import partial




# import python.code_lib.analyze_addtion as analyze_addtion


class CheckWidget(QWidget, check_bottom.CheckBottomWidget):

    def __init__(self, ui=None,parent=None):
        super(CheckWidget, self).__init__(parent)
        self._checkwidgets = []
        self._processwidgets = []




        self._ui=ui

        self._check_tabname = self._get_tabname()

        self.checkbottom_setup()
        self._setup()



    def _setup(self):
        self._allframe = QFrame()
        self._allframe.setMinimumWidth(500)

        # self._baseinfoWidget = _baseinfo.PubInfoWidget(self.task_data, self._get_publishthumbnail())
        self._multi_tabwidget = multi_tabwidget.TabWidget(self._check_tabname)

        self._check_listwidget = listwidget.ListWidget()
        self._check_layout = QVBoxLayout()
        self._check_layout.addWidget(self._check_listwidget)
        self._check_layout.addWidget(self._check_bottomframe)
        self._widget_check = QWidget()
        self._widget_check.setLayout(self._check_layout)

        self._layout = QVBoxLayout(self._allframe)
        self._layout.setContentsMargins(0, 0, 0, 0)
        # self._layout.addWidget(self._baseinfoWidget)
        self._layout.addWidget(self._multi_tabwidget)
        self._layout.addWidget(self._widget_check)

        self._alllayout = QVBoxLayout()
        self._alllayout.addWidget(self._allframe)
        self.setLayout(self._alllayout)

        self._multi_tabwidget.currentChanged.connect(
            self._tab_indexchange)
        self._check_listwidget._listwidget.itemSelectionChanged.connect(self._select_item)

        for checkscrollwidget in self._multi_tabwidget.get_checkscrollwidget():
            for _checkitem in checkscrollwidget.get_checkwidgets():
                _checkitem._pushbutton1.clicked.connect(partial(self._show_cinfo, _checkitem))
                _checkitem._pushbutton2.clicked.connect(self._check_listwidget._clear_info)
                # _checkitem._pushbutton3.clicked.connect(partial(self._show_cinfo, _checkitem))
                self._checkwidgets.append(_checkitem)


    def _tab_indexchange(self, index):
        if index == 0:
            self._widget_check.setVisible(1)
            self._widget_prcess.setVisible(0)
            self._widget_check.setMinimumHeight(200)
            self._widget_prcess.setMinimumHeight(200)
        if index == 1:
            self._widget_check.setVisible(0)
            self._widget_prcess.setVisible(1)
            self._widget_check.setMinimumHeight(200)
            self._widget_prcess.setMinimumHeight(200)

    def _assert_panel_mode(self):
        widgets = QApplication.topLevelWidgets()
        if widgets:
            for _widget in widgets:
                if _widget.objectName().startswith("pipeline_"):
                    if _widget.windowModality() == Qt.WindowModality.WindowModal:
                        self.set_modal()

    def _get_tabname(self):
        check_name=u'drama_mdl check'
        return check_name

    def _show_cinfo(self, widget):
        _widget_name = widget.name()
        _checkinfo = widget.info()
        if _checkinfo:
            items = _checkinfo.split("\n")
            self._check_listwidget._clear_info()
            self._check_listwidget._listwidget.addItem(_widget_name + ':')
            for item in items:
                self._check_listwidget._listwidget.addItem(item)
        else:
            self._check_listwidget._clear_info()

    def _select_item(self):
        pass

    def _change_show(self):
        for _item in self._checkwidgets:
            if self._check_displayallbox.isChecked():
                _item.setHidden(False)
            else:
                if _item.result():
                    _item.setHidden(True)

    def check_all(self):
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





if __name__ == '__main__':
    import sys

    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)
#
    win = CheckWidget()

    win.show()
    sys.exit(app.exec_())