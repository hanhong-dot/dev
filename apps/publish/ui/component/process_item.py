# -*- coding: utf-8 -*-#
# Python       : python 2.7.16
# -------------------------------------------------------------------------------
# NAME         : process_item
# Describe     : 说明描述
# Version      : v0.01
# Author       : linhuan
# Email        : hanhong@papegames.net
# DateTime     : 2022/5/3__16:47
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


class ProcessItemWidget(QFrame):
    def __init__(self, item_name, process_command, task_data,mb_export,version_file=None, tooltip=None, parent=None):
        super(ProcessItemWidget, self).__init__(parent)
        self._name = item_name
        self._process_command = process_command
        self.task_data = task_data
        self.tootip = tooltip
        self.mb_export=mb_export
        self.version_file=version_file
        self._build()

    # self._pushbutton1.clicked.connect(self.doprocess)
    # self._pushbutton2.clicked.connect(self.process_openlog)

    def _build(self):
        self.setMaximumHeight(35)

        self._pushbutton = QPushButton()
        self._pushbutton.setText(self._name)
        self._pushbutton.setStyleSheet("background-color:rgba(0,0,0,0);font:11px")
        self._pushbutton.setToolTip(self.tootip)

        self._pushbutton1 = QPushButton()
        self._pushbutton1.setFixedSize(50, 25)
        self._pushbutton1.setText(u"处理")

        self._pushbutton2 = QPushButton()
        self._pushbutton2.setFixedSize(50, 25)
        self._pushbutton2.setText(u"打开log")

        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(0, 2, 0, 2)
        self._layout.setSpacing(2)
        self._layout.addWidget(self._pushbutton)
        self._layout.addStretch()
        self._layout.addWidget(self._pushbutton1)
        self._layout.addWidget(self._pushbutton2)
        _qss = "QFrame{border-top: 2px solid #32fc13;}"
        self.setStyleSheet(_qss)

    def doprocess(self):
        if isinstance(self._process_command, str):
            _command = self._process_command.split(';')[-1]
            _command_new = _command.replace('TaskData_Class', 'self.task_data').replace('mb_export', 'self.mb_export').replace('version_file','self.version_file')
            exec (self._process_command[0:len(self._process_command) - len(_command)])
            eval(_command_new)

    def name(self):
        return self._name


# if __name__ == '__main__':
#     import sys
#     import method.shotgun.get_task as get_task
#
#     app = QApplication(sys.argv)
#     win = ProcessItemWidget("生成publish文件",
#                             "import publish.process.maya.process_sgfile as process_sgfile;reload(process_sgfile);process_sgfile.processPublish(TaskData)", tooltip='test', task_data=
#                             get_task.TaskInfo('ST001S.drama_mdl.v010.ma', 'X3_test04', 'maya', 'version'))
#     win.show()
#     sys.exit(app.exec_())
