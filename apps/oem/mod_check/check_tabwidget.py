# -*- coding: utf-8 -*-#
# Python       : python 2.7.16
# -------------------------------------------------------------------------------
# NAME         : multi_page
# Describe     : 说明描述
# Version      : v0.01
# Author       : linhuan
# Email        : hanhong@papegames.net
# DateTime     : 2022/5/2__14:46
# -------------------------------------------------------------------------------
# -------------------------------------------------------------------------------
# example:
# 
# -------------------------------------------------------------------------------

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

import check_scrollarea as check_scrollarea
reload(check_scrollarea)



class TabWidget(QTabWidget):
    def __init__(self,  first_tabname=None, second_tabname=None, parent=None, *args):
        super(TabWidget, self).__init__(parent)
        self.checkscrollwidgets = []


        self._check_tabname = first_tabname
        self._process_tabname = second_tabname


        self._check_tab = QWidget()

        self.addTab(self._check_tab, self._check_tabname)

        self._checkUI()

    # self.setWindowTitle(u"检测工具")

    def _checkUI(self):
        self._check_scrollarea = check_scrollarea.CheckScrollareaWidget()
        print self._check_scrollarea

        layout = QFormLayout()
        layout.addWidget(self._check_scrollarea)
        self._check_tab.setLayout(layout)
        self.checkscrollwidgets.append(self._check_scrollarea)

    def get_checkscrollwidget(self):
        return self.checkscrollwidgets

if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    demo = TabWidget('111', '222')
    demo.show()
    sys.exit(app.exec_())
