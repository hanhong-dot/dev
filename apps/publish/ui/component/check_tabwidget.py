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
import apps.publish.util.analyze_xml as _get_data


class TabWidget(QTabWidget):
    def __init__(self, task_data, first_tabname=None, second_tabname=None, parent=None, *args):
        super(TabWidget, self).__init__(parent)
        self.checkscrollwidgets = []

        self.task_data = task_data
        self._check_tabname = first_tabname
        self._process_tabname = second_tabname
        self._analyse_data = _get_data.GetXLMData(self.task_data)

        self._check_tab = QWidget()
        if self._analyse_data.get_checkdata():
            self.addTab(self._check_tab, self._check_tabname)

        self._checkUI()

    # self.setWindowTitle(u"检测工具")

    def _checkUI(self):
        self._check_scrollarea = check_scrollarea.CheckScrollareaWidget(self.task_data,
                                                                        self._analyse_data.get_checkdata())
        print self._check_scrollarea

        layout = QFormLayout()
        layout.addWidget(self._check_scrollarea)
        self._check_tab.setLayout(layout)
        self.checkscrollwidgets.append(self._check_scrollarea)

    def get_checkscrollwidget(self):
        return self.checkscrollwidgets

if __name__ == '__main__':
	# import publish.check.common.check_A_templet as check_A_templet
	# reload(check_A_templet)
	import sys
	import method.shotgun.get_task as get_task

	app = QApplication(sys.argv)

	demo = TabWidget(get_task.TaskInfo('ST001S.drama_mdl.v001.ma', 'X3', 'maya', 'version'), '111', '222')

	demo.show()
	sys.exit(app.exec_())
