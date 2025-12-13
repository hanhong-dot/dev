# -*- coding: utf-8 -*-#
# Python       : python 2.7.16
# -------------------------------------------------------------------------------
# NAME         : checkwidget
# Describe     : 说明描述
# Version      : v0.01
# Author       : linhuan
# Email        : hanhong@papegames.net
# DateTime     : 2022/5/21__16:37
# -------------------------------------------------------------------------------
# -------------------------------------------------------------------------------
# example:
# 
# -------------------------------------------------------------------------------


import apps.publish.ui.component.check_bottom as check_bottom
import apps.publish.ui.component.listwidget as listwidget
import apps.publish.ui.component.check_tabwidget as multi_tabwidget
import method.common.dir as dir

try:
    from PySide2.QtWidgets import *
    from PySide2.QtGui import *
    from PySide2.QtCore import *
except:
    from Qt.QtWidgets import *
    from Qt.QtGui import *
    from Qt.QtCore import *

import os
from functools import partial
import lib.common.xmlio as xmlio
import apps.publish.util.analyze_xml as _get_data
import lib.common.jsonio as jsonio
import lib.common as libs


# import python.code_lib.analyze_addtion as analyze_addtion


class CheckWidget(QWidget, check_bottom.CheckBottomWidget):

    def __init__(self, task_data,ui=None,parent=None):
        super(CheckWidget, self).__init__(parent)
        self._checkwidgets = []
        self._processwidgets = []

        self.task_data = task_data

        self.filename = self.task_data.filename
        self._getdata = _get_data.GetXLMData(self.task_data)
        self._ui=ui
        if not self._getdata._get_xml_path('check_config.xml') and not self._getdata._get_xml_path(
                'process_config.xml'):
            self._setup2()
        else:
            self._check_tabname = self._get_tabname()

            self.checkbottom_setup()
            self._setup()
            # self._assert_panel_mode()

    def _setup2(self):
        self._frame_none = QFrame()
        self._frame_none.setMinimumWidth(500)

        self._lable_none = QLabel(u'{}任务common下没有配置文件，因此不进行相关检测'.format(self.task_data.task_name))
        self._lable_layout = QHBoxLayout()
        self._lable_layout.addWidget(self._lable_none)

        self._none_layout = QHBoxLayout()
        self._none_layout.addLayout(self._lable_layout)

        self.setLayout(self._none_layout)

    def _setup(self):
        # self.set_title_name(u"%s----check工具"
        #                     % self._task_name)

        self._allframe = QFrame()
        self._allframe.setMinimumWidth(500)

        # self._baseinfoWidget = _baseinfo.PubInfoWidget(self.task_data, self._get_publishthumbnail())
        self._multi_tabwidget = multi_tabwidget.TabWidget(self.task_data, self._check_tabname)

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

        # checkitem信号
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
        '''
        获取check配置文件内容
        :return:
        '''
        if self._getdata._get_xml_path('check_config.xml'):
            check_data = xmlio.SelectXML(self._getdata._get_xml_path('check_config.xml'))
            check_name = check_data.select_findallattr('check_tab')[0]['tab_name'] if check_data.select_findallattr(
                'check_tab') else None
        else:
            check_name = None
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
        '''
        DCC软件重写
        :return:
        '''
        pass

    def _change_show(self):
        '''设置显示模式
        '''
        for _item in self._checkwidgets:
            if self._check_displayallbox.isChecked():
                _item.setHidden(False)
            else:
                if _item.result():
                    _item.setHidden(True)

    def check_all(self, is_publish=False):
        has_result = []
        config = r"{}/check_config_{}.json".format(libs.pipedata_path(), os.path.splitext(self.filename)[0])
        _ignore_info = {}
        _ignores = []
        _check_info = {}
        _values = []

        if is_publish == True:
            _check_info = jsonio.read(config)
            if _check_info:
                _values = _check_info.values()[0]
        for _widget in self._checkwidgets:
            if is_publish:
                if _values:
                    # if _widget._name in _values:
                    for obj in _values:
                        if _widget._name == obj[0]:
                            _widget._checkbox.setChecked(obj[1])
                            _widget._checkbox.setChecked(obj[1])
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
        if _ignore_info:
            jsonio.write(_ignore_info, config)

        if False not in has_result:
            self._ui.close()
            self._ui.deleteLater()

        return has_result

    def _get_publishthumbnail(self):
        '''
        获取路径下的缩略图
        :return: 缩略图路径
        '''
        _task_type = self.task_data.task_type
        _entity_name = self.task_data.entity_name
        _task_name = self.task_data.task_name

        _thumbnail_dir = self.task_data.publish_thubnail

        return self._get_mastername(_thumbnail_dir, ['.png','.jpg'])

    def _get_mastername(self, _dir, suffixs):
        '''
		:param suffix: 后缀，例如：.jpg,.png,.mb
		:return:
		'''
        return dir.get_laster_file(_dir, suffixs)


# if __name__ == '__main__':
#     import sys
#     import method.shotgun.get_task as get_task
#
#     app = QApplication.instance()
#     if not app:
#         app = QApplication(sys.argv)
#
#     win = CheckWidget(get_task.TaskInfo('ST_BODY.drama_rig.v008.ma', 'X3', 'maya', 'version'))
#
#     win.show()
#     sys.exit(app.exec_())
