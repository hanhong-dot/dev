# -*- coding: utf-8 -*-#
# Python       : python 2.7.16
# -------------------------------------------------------------------------------
# NAME         : checkitem
# Describe     : 说明描述
# Version      : v0.01
# Author       : linhuan
# Email        : hanhong@papegames.net
# DateTime     : 2022/5/2__14:03
# -------------------------------------------------------------------------------
# -------------------------------------------------------------------------------
# example:
#
# -------------------------------------------------------------------------------
try:
    from PySide2.QtWidgets import *
    from PySide2.QtGui import *
    from PySide2.QtCore import *
except:
    from Qt.QtWidgets import *
    from Qt.QtGui import *
    from Qt.QtCore import *

from functools import partial


class CheckItemWidget(QFrame):
    # def __init__(self,item_name,status_list):
    def __init__(self, item_name, process_list):
        super(CheckItemWidget, self).__init__()
        self._data_true = []
        self._data_false = []
        self._datas = {True: self._data_true, False: self._data_false}
        self._name = item_name
        self._process_list = process_list

        self._layout_check = QHBoxLayout()
        self._layout_check.setAlignment(Qt.AlignLeft)
        # self._radio_layout = QHBoxLayout()
        self._label = QLabel(self._name)
        self._layout_check.addWidget(self._label)
        self._check_grp = QButtonGroup()
        self.check_list = []

        for obj in self._process_list:
            check = QCheckBox()
            check.setText(obj[0])
            check.setToolTip(obj[1])
            # check.setChecked(True)
            # self._check_grp.addButton(check)
            self._layout_check.addWidget(check)
            self._get_checkButton(check)

            check.clicked.connect(partial(self._get_checkButton, check))
            self.check_list.append(check)

        self.setLayout(self._layout_check)

    def _get_checkButton(self, checkbox):
        if checkbox.isChecked():
            self._data_true.append(checkbox)
        else:
            self._data_false.append(checkbox)

    def get_check_is(self, checkbox):
        return checkbox.isChecked()

    def _get_checkName(self):
        if self._datas and True in self._datas and self._datas[True]:
            return {True: i.text() for i in self._datas[True] if self._datas[True]}
        if self._datas and False in self._datas and self._datas[False]:
            return {False: i.text() for i in self._datas[False] if self._datas[False]}


if __name__ == '__main__':
    import sys

    try:

        app = QApplication(sys.argv)
    except:
        app = QApplication.instance()
    state_list = [('downstream', u'可提交下个环节状态'), ('upstream', u'可提交上个环节状态')]
    win = CheckItemWidget(u'任务提交状态选择 : ', state_list)
    print win._data_true
    win.show()
    sys.exit(app.exec_())
