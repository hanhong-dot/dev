# -*- coding: utf-8 -*-#
# Python       : python 2.7.16
# -------------------------------------------------------------------------------
# NAME         : publish_pic
# Describe     : 说明描述
# Version      : v0.01
# Author       : linhuan
# Email        : hanhong@papegames.net
# DateTime     : 2022/5/19__10:26
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

import os


class PicWidget(QFrame):
    def __init__(self, Taskdata,suffix, parent=None,dcc='maya'):
        super(PicWidget, self).__init__(parent)
        self.setAcceptDrops(True)
        self._data = []
        self._taskdata = Taskdata
        self._suffix = suffix
        self._suffixlist = self._set_suffix_list()

        self._build()
        self._picbutton.clicked.connect(self._get_file)
        self._sceenbutton.clicked.connect(self._sceen_shot)
        self._default_screen_button.clicked.connect(self.default_sceen_shot)
        self._dcc=dcc

    def _build(self):
        self.setMaximumHeight(266)
        self._label_pic = QLabel()
        self._label_pic.setMinimumHeight(20)
        self._label_pic.setText(u"请选择图片/视频或拖入窗口")
        # self._label_pic.setText(u"Thumbnail")

        self._listwidget_pic = QListWidget()
        self._listwidget_pic.setFixedHeight(80)
        self._listwidget_pic.setSelectionMode(QAbstractItemView.ContiguousSelection)

        self._picbutton = QPushButton()
        self._picbutton.setFixedSize(QSize(70, 20))
        self._picbutton.setText(u"...")

        self._default_screen_button=QPushButton()
        self._default_screen_button.setFixedSize(QSize(70, 20))
        self._default_screen_button.setText(u"默认截图")


        self._sceenbutton=QPushButton()
        self._sceenbutton.setFixedSize(QSize(70, 20))
        self._sceenbutton.setText(u"框选截图")


        self._seclayout = QHBoxLayout()

        self._seclayout.addWidget(self._label_pic)
        self._seclayout.addWidget(self._default_screen_button)
        self._seclayout.addWidget(self._sceenbutton)
        self._seclayout.addWidget(self._picbutton)

        self._layout_pic = QVBoxLayout(self)
        self._layout_pic.addLayout(self._seclayout)
        self._layout_pic.addWidget(self._listwidget_pic)
        self._layout_pic.addStretch()  # 增加伸缩量

    def _set_suffix_list(self):
        _list = []
        # for _item in self._suffix.values():
        for _item in self._suffix:
            _list.extend([i for i in _item])
        return _list

    def _get_file(self):
        '''获取文件
        '''
        _path = "./"
        if os.path.exists(os.path.dirname(self._taskdata.last_des)):
            _path = os.path.dirname(self._taskdata.last_des)
    
        if self._suffixlist:
            filter_order = "Files ({})".format(" *".join(self._suffixlist))
        else:
            filter_order = "all Files (*)"
        _files = QFileDialog.getOpenFileNames(self,
                                              u"文件选择",
                                              _path,
                                              filter_order)
        if _files and self._listwidget_pic.count() < 1:
            self._additem(_files[0])

    def _additem(self, items):
        '''添加列表项，按需求限定添加一个
        '''
        for _item in items:
            if _item not in self._data:
                self._item = QListWidgetItem(self._listwidget_pic)
                self._item.setText(_item)
                self._data.append(_item)

    def dropEvent(self, event):
        '''获取文件
        '''
        if event.mimeData().hasUrls():
            _urls = event.mimeData().urls()
            _realurls = self._check_urls([i.toLocalFile() for i in _urls])
            # if _realurls:
            if _realurls and self._listwidget_pic.count() < 1:
                # self._lineedit.setText(",".join(_realurls))
                self._additem(_realurls)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Delete:
            _items = self._listwidget_pic.selectedIndexes()
            if _items:
                _indexs = [_i.row() for _i in _items]
                for i in sorted(_indexs, reverse=True):
                    _item = self._listwidget_pic.item(i)
                    # print(_item)
                    self._data.pop(i)
                    self._removeitem(i)

    def _removeitem(self, index):
        self._listwidget_pic.takeItem(index)

    def _check_urls(self, urls):
        return [_url for _url in urls if os.path.splitext(_url)[-1] in self._suffixlist]

    def _get_picData(self):
        print(self._data)
        return self._data

    def _sceen_shot(self):
        import apps.tools.common.screenshot.sceen_tool as sceen_tool
        _pic=sceen_tool.ScreenShot().screenshot()
        if _pic and os.path.exists(_pic):
            self._additem([_pic])

    def default_sceen_shot(self):
        if self._dcc =='maya':
            _pic=self._maya_dedault_sceen_shot()
            if _pic and os.path.exists(_pic):
                self._additem([_pic])


    def _maya_dedault_sceen_shot(self):
        import apps.tools.maya.screen as maya_screen
        reload(maya_screen)
        return maya_screen.screen_shot()
if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    win = PicWidget([('.jpeg', u'.jpg', u'.png', u'.gif', u'.tif'),
                     (u'.mov', u'.avi', u'.mp4')])
    win.show()
    sys.exit(app.exec_())
