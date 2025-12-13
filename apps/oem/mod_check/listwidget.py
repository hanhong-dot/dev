# -*- coding: utf-8 -*-#
# Python       : python 2.7.16
# -------------------------------------------------------------------------------
# NAME         : check_listwidget
# Describe     : 说明描述
# Version      : v0.01
# Author       : linhuan
# Email        : hanhong@papegames.net
# DateTime     : 2022/5/1__14:43
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




class ListWidget(QFrame):
    def __init__(self, parent=None):
        super(ListWidget, self).__init__(parent)
        self.list_setup()

    def list_setup(self):
        self._grpboxwidget = QGroupBox()
        self._grpboxwidget.setTitle(u'反馈信息')
        self._listwidget = QListWidget()
        self._listwidget.setSelectionMode(QAbstractItemView.ContiguousSelection)
        self._listwidget.setMinimumHeight(200)
        # self._listwidget.setMaximumHeight(700)
        self._listwidget.setVerticalScrollMode(QAbstractItemView.ScrollPerItem)
        self._grplayout = QHBoxLayout()
        self._listlayout = QVBoxLayout()
        self._listlayout.addWidget(self._listwidget)
        self._grpboxwidget.setLayout(self._listlayout)
        self._grplayout.addWidget(self._grpboxwidget)

        self.setLayout(self._grplayout)

    def _clear_info(self):
        self._listwidget.clear()


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    win = ListWidget()
    win.show()
    sys.exit(app.exec_())
