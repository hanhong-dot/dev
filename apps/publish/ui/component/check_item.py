# -*- coding: utf-8 -*-#
# Python       : python 2.7.16
# -------------------------------------------------------------------------------
# NAME         : check_item
# Describe     : 检测项
# Version      : v0.01
# Author       : linhuan
# Email        : hanhong@papegames.net
# DateTime     : 2022/5/28__17:47
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


class CheckItemWidget(QFrame):
    def __init__(self, item_name, check_command, fix_command, ignore, task_data, tooltip=None, parent=None):
        super(CheckItemWidget, self).__init__(parent)

        self._name = item_name
        self._check_command = check_command
        self._fix_command = fix_command
        self._ignore = ignore
        self.task_data = task_data
        self.tooltip = tooltip

        self._result = None
        self._info = None
        self._build()
        self._init_button()
        # self.is_normal()
        self.is_right()

        self._pushbutton1.clicked.connect(self.docheck)
        self._pushbutton2.clicked.connect(self.dorecheck)

    def _build(self):
        self.setMaximumHeight(35)

        self._pushbutton = QPushButton()
        self._pushbutton.setText(self._name)
        self._pushbutton.setStyleSheet("background-color:rgba(0,0,0,0);font:11px")
        self._pushbutton.setToolTip(self.tooltip)

        self._pushbutton1 = QPushButton()
        self._pushbutton1.setFixedSize(50, 25)
        self._pushbutton1.setText(u"检查")

        self._pushbutton2 = QPushButton()
        self._pushbutton2.setFixedSize(50, 25)
        self._pushbutton2.setText(u"修复")

        # self._pushbutton3 = QPushButton()
        # self._pushbutton3.setFixedSize(75, 25)
        # self._pushbutton3.setText(u"显示信息")

        self._checkbox = QCheckBox()
        self._checkbox.setFixedSize(50, 25)
        self._checkbox.setText(u"忽略")

        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(0, 2, 0, 2)
        self._layout.setSpacing(2)
        self._layout.addWidget(self._pushbutton)
        self._layout.addStretch()
        self._layout.addWidget(self._pushbutton1)
        self._layout.addWidget(self._pushbutton2)
        # self._layout.addWidget(self._pushbutton3)
        self._layout.addWidget(self._checkbox)

    def _init_button(self):
        if not self._fix_command:
            self._pushbutton2.setEnabled(False)
        if not self._ignore:
            self._checkbox.setEnabled(False)

    def is_right(self):
        _qss = "QFrame{border-top: 2px solid #32fc13;}"
        self.setStyleSheet(_qss)

    def is_wrong(self):
        _qss = "QFrame{background-color: #ff0000; border-top: 2px solid #ff0000;}"
        self.setStyleSheet(_qss)

    def is_normal(self):
        _qss = "QFrame{border-top: 2px solid #aaaaaa;}"
        self.setStyleSheet(_qss)

    def docheck(self):
        if not self.is_ignore():
            if isinstance(self._check_command, str):
                _command = self._check_command.split(';')[-1]
                print(_command)
                _command_new = _command.replace('TaskData_Class', 'self.task_data')
                exec (self._check_command[0:len(self._check_command) - len(_command)])
                self._result, self._info = eval(_command_new)
            if self._result:
                self.is_right()
            else:
                self.is_wrong()
            return self._result, self._info
        else:
            self._result = None
            self._info = None
            self.is_right()
            return self._result, self._info

    def dofix(self):
        if not self.is_ignore():
            if isinstance(self._fix_command, str):
                _command = self._fix_command.split(';')[-1]
                _command_new = _command.replace('TaskData_Class', 'self.task_data')
                exec (self._fix_command[0:len(self._fix_command) - len(_command)])
                eval(_command_new)

    def dorecheck(self):
        self.dofix()
        self.docheck()

    def name(self):
        return self._name

    def result(self):
        return self._result

    def info(self):
        if self._info and self._info != False:
            return (self._info).decode('gbk', 'ignore').encode('utf-8')
        else:
            return (self._info)

    def is_ignore(self):
        return self._checkbox.isChecked()


if __name__ == '__main__':
    import method.shotgun.get_task as get_task
    # import publish.check.common.maya.check_A_templet as check_A_templet;reload(check_A_templet);check_A_templet.checkinfo(get_task.TaskInfo())
    import sys

    app = QApplication(sys.argv)
    win = CheckItemWidget("检查软件版本是否符合项目规定", "import publish.check.common.check_A_templet as "
                                            "check_A_templet;reload("
                                            "check_A_templet);check_A_templet.checkinfo('a')",
                          "import publish.check.common.check_A_templet as check_A_templet;reload("
                          "check_A_templet);check_A_templet.fix()", False, tooltip='fuck', task_data=
                          get_task.TaskInfo('test.drama_mdl.v001.ma', 'X3_test04', 'maya', 'version'))
    win.show()
    sys.exit(app.exec_())
#
# # a = ['1', '2', '3']
# # task = 'srf_hig'
# # tt = _select_item(task, *a)
# # def _select_item(task_data, d, e, f):
# # 	print task_data, d, e, f
# import check.common.maya.asset.chr
# execfile(r"E:\lib\Develop\apps\publish\check\common\maya\check_A_templet.py")

#
