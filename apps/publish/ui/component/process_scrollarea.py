# -*- coding: utf-8 -*-#
# Python       : python 2.7.16
# -------------------------------------------------------------------------------
# NAME         : process_scrollarea
# Describe     : 说明描述
# Version      : v0.01
# Author       : linhuan
# Email        : hanhong@papegames.net
# DateTime     : 2022/5/3__17:00
# -------------------------------------------------------------------------------
# -------------------------------------------------------------------------------
# example:
# 
# -------------------------------------------------------------------------------

__AUTHORZH__ = u"韩虹"
__AUTHOR__ = "linhuan"
__EMAIL__ = "hanhong@papegames.net"

import time
import process_item as process_item

try:
    from PySide2.QtWidgets import *
    from PySide2.QtGui import *
    from PySide2.QtCore import *
except:
    from Qt.QtWidgets import *
    from Qt.QtGui import *
    from Qt.QtCore import *


class ProcessScrollareaWidget(QWidget):
    def __init__(self, task_data=None, xml_message=None,mb_export=None,version_file=None,parent=None):
        super(ProcessScrollareaWidget, self).__init__(parent)

        self._process_widgets = []
        self.xml_message = xml_message
        self.task_data = task_data
        self.mb_export=mb_export
        self.version_file=version_file
        self.setup()

    def setup(self):
        self._frame = QFrame()
        self._scrollarea = QScrollArea()
        self._scrollarea.setWidget(self._frame)
        self._scrollarea.setWidgetResizable(True)
        self._scrollarea.setBackgroundRole(QPalette.NoRole)
        self._scrollarea.setFrameShape(QFrame.NoFrame)

        self._process_scrolllayout = QVBoxLayout()
        self._process_scrolllayout.addWidget(self._scrollarea)
        self.set_checkitemwidgets()
        self.setLayout(self._process_scrolllayout)

    def set_checkitemwidgets(self):
        '''
        设置处理项
        :return:
        '''
        self._scrollayout = QVBoxLayout(self._frame)
        self._scrollayout.setContentsMargins(0, 0, 0, 0)

        num = 0
        for _processitem in self.xml_message:
            num = num + 1
            _widget = process_item.ProcessItemWidget(_processitem['item_name'], _processitem['process_command'],
                                                     self.task_data,self.mb_export,self.version_file, tooltip=_processitem['toolTip'])
            _widget.setObjectName(time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime(time.time())) + '_' + str(num))
            self._scrollayout.addWidget(_widget)
            self._process_widgets.append(_widget)

        self._scrollayout.addStretch()
        self._frame.setLayout(self._scrollayout)

    def get_processwidgets(self):
        return self._process_widgets


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    ui = ProcessScrollareaWidget()
    ui.show()
    sys.exit(app.exec_())
