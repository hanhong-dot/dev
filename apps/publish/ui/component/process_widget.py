# -*- coding: utf-8 -*-#
# Python       : python 2.7.16
# -------------------------------------------------------------------------------
# NAME         : process_widget
# Describe     : 说明描述
# Version      : v0.01
# Author       : linhuan
# Email        : hanhong@papegames.net
# DateTime     : 2022/6/14__11:54
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

import process_scrollarea as process_scrollarea
import apps.publish.ui.component.process_bottom as process_bottom
import apps.publish.util.analyze_xml as _get_data


class ProcessPanel(QFrame, process_bottom.ProcessBottomWidget):
    def __init__(self, task_data,mb_export,version_file=None):
        super(ProcessPanel, self).__init__()
        self.processscrollwidgets = []
        self.processsbuttons = []
        self._task_data = task_data
        self._analyse_data = _get_data.GetXLMData(self._task_data)
        self._mb_export=mb_export
        self._version_file=version_file
        self.processbottom_setup()
        self._setup()

    def _setup(self):
        self._process_scrollarea = process_scrollarea.ProcessScrollareaWidget(self._task_data,
                                                                              self._analyse_data.get_processdata(),self._mb_export,self._version_file)
        layout = QFormLayout(self)
        layout.addWidget(self._process_scrollarea)
        layout.addWidget(self._process_bottomframe)
        self.processscrollwidgets.append(self._process_scrollarea)
        self.processsbuttons = [self._process_allpushbutton, self._process_allopenlogbutton]

    def get_processscrollwidget(self):
        return self.processscrollwidgets


# if __name__ == '__main__':
#     import sys
#     import method.shotgun.get_task as get_task
#
#     app = QApplication(sys.argv)
#     bswin = ProcessPanel(get_task.TaskInfo('ST001S.drama_mdl.v010.ma', 'X3_test04', 'maya', 'version'))
#     bswin.show()
#     sys.exit(app.exec_())
