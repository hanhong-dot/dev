# -*- coding: utf-8 -*-#
# Python       : python 2.7.16
# -------------------------------------------------------------------------------
# NAME         : publish_tabwidget
# Describe     : 说明描述
# Version      : v0.01
# Author       : linhuan
# Email        : hanhong@papegames.net
# DateTime     : 2022/5/25__10:08
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

import apps.publish.ui.component.publish_pic_o as _picture
reload(_picture)
import apps.publish.ui.component.publish_descrip as _description
import apps.publish.ui.component.process_widget as _process_widget
import apps.publish.util.analyze_xml as _get_data


class TabWidget(QTabWidget):
    def __init__(self, task_data, sub_tabname=None, sub_widget=None, process_tabname=None,mb_export=None,version_file=None,
                 parent=None, *args):
        '''
        创建publish TabWidget
        :param task_data:  task_data
        :param sub_tabname: 自定义tab名
        :param sub_widget: 如果sub_tabname不为None,需传个sub_weidget进来
        :param parent:
        :param args:
        '''
        super(TabWidget, self).__init__(parent)

        self.processscrollwidget = []
        self.processscrollbuttons = []
        self._task_data = task_data
        self._analyse_data = _get_data.GetXLMData(self._task_data)
        self._suffix = self._get_suffixs()
        self._sub_tabname = sub_tabname
        self._process_tabname = process_tabname
        self._mb_export=mb_export
        self._version_file=version_file
        self._base_tab = QWidget()
        self._sub_tab = QWidget()
        self._process_tab = QWidget()

        self.addTab(self._base_tab, u'编辑基础信息')
        self._baseUI()
        if self._sub_tabname:
            self.addTab(self._sub_tab, self._sub_tabname)
            self._addSubUI(sub_widget)

        if self._process_tabname:
            self.addTab(self._process_tab, self._process_tabname)
            self._addProcessUI()

    # self.setWindowTitle(u"aaa")

    def _get_suffixs(self):
        # print self._analyse_data.get_processdata()
        return self._analyse_data.get_publishdata()[1]

    def _baseUI(self):
        self._pictureWidget = _picture.PicWidget(self._task_data,self._suffix)
        self._descripWidget = _description.DescWidget()

        self._layout_publish = QVBoxLayout()
        self._layout_publish.addWidget(self._pictureWidget)
        self._layout_publish.addWidget(self._descripWidget)

        self._base_tab.setLayout(self._layout_publish)

    def _addSubUI(self, _widget):
        self._layout_sub = QVBoxLayout()
        self._layout_sub.addWidget(_widget)
        self._sub_tab.setLayout(self._layout_sub)

    def _addProcessUI(self):
        self._process = _process_widget.ProcessPanel(self._task_data,self._mb_export,self._version_file)
        self._layout_pro = QVBoxLayout()
        self._layout_pro.addWidget(self._process)
        self._process_tab.setLayout(self._layout_pro)
        self.processscrollwidget = self._process.get_processscrollwidget()
        self.processscrollbuttons = self._process.processsbuttons


# if __name__ == '__main__':
#     # import publish.check.common.check_A_templet as check_A_templet
#     # reload(check_A_templet)
#     import sys
#     import method.shotgun.get_task as get_task
#
#     app = QApplication(sys.argv)
#     demo = TabWidget(get_task.TaskInfo('PL001S.drama_mdl.v001.ma', 'X3', 'maya', 'version'),
#                      process_tabname='process')
#     demo.show()
#     sys.exit(app.exec_())
