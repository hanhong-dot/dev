# -*- coding: utf-8 -*-#
# -------------------------------------------------------
# NAME       : open_claw_ui
# Describe   : OpenClaw工具UI
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2026/3/10
# -------------------------------------------------------
try:
    from PySide2.QtWidgets import *
    from PySide2.QtGui import *
    from PySide2.QtCore import *
except:
    from PyQt5.QtWidgets import *
    from PyQt5.QtGui import *
    from PyQt5.QtCore import *

from apps.tools.maya.open_claw_tool import open_claw_fun

reload(open_claw_fun)

from apps.publish.ui.message.messagebox import msgview

import sys


class OpenClawUI(QWidget):
    CloseSignal = Signal()

    def __init__(self, parent=None):
        super(OpenClawUI, self).__init__(parent)
        self.__init_ui()
        self.__builder()
        self.__connect()

    def __connect(self):
        self.__add_btn.clicked.connect(self.__add_select_ctrl)
        self.__remove_btn.clicked.connect(self.__remove_select_ctrl)
        self.__clear_btn.clicked.connect(self.__clear_ctrls)
        self.__open_btn.clicked.connect(self.__open_claw)
        self.__close_btn.clicked.connect(self.__close_claw)
        self.__reset_btn.clicked.connect(self.__reset_claw)

    def __init_ui(self):
        self.setWindowTitle(u'OpenClaw Tool')
        self.resize(350, 300)
        self.__main_layout = QVBoxLayout()
        self.setLayout(self.__main_layout)

    def __builder(self):
        # 控制器列表区域
        self.__list_layout = QHBoxLayout()
        self.__btn_layout = QVBoxLayout()
        self.__btn_layout.setAlignment(Qt.AlignTop)
        self.__btn_layout.setSpacing(10)

        self.__add_btn = QPushButton(u'添加控制器')
        self.__add_btn.setStyleSheet("background-color: rgb(30, 90, 87); color: white;")
        self.__remove_btn = QPushButton(u'移除选中')
        self.__clear_btn = QPushButton(u'清空')

        self.__btn_layout.addWidget(self.__add_btn)
        self.__btn_layout.addWidget(self.__remove_btn)
        self.__btn_layout.addWidget(self.__clear_btn)

        self.__listwidget = QListWidget()
        self.__listwidget.setSelectionMode(QAbstractItemView.ContiguousSelection)
        self.__listwidget.setVerticalScrollMode(QAbstractItemView.ScrollPerItem)

        self.__list_layout.addWidget(self.__listwidget)
        self.__list_layout.addLayout(self.__btn_layout)

        self.__main_layout.addLayout(self.__list_layout)

        # 操作按钮区域
        self.__action_layout = QHBoxLayout()
        self.__open_btn = QPushButton(u'张开爪子')
        self.__close_btn = QPushButton(u'闭合爪子')
        self.__reset_btn = QPushButton(u'重置')

        self.__action_layout.addWidget(self.__open_btn)
        self.__action_layout.addWidget(self.__close_btn)
        self.__action_layout.addWidget(self.__reset_btn)

        self.__main_layout.addLayout(self.__action_layout)

    def __add_select_ctrl(self):
        ctrls = open_claw_fun.get_select_controls()
        listwidget_items = [self.__listwidget.item(i).text() for i in range(self.__listwidget.count())]
        if not ctrls:
            msgview(u'请先在场景中选择控制器', 1)
            return
        for ctrl in ctrls:
            if ctrl in listwidget_items:
                continue
            self.__listwidget.addItem(ctrl)

    def __remove_select_ctrl(self):
        select_items = self.__listwidget.selectedItems()
        for item in select_items:
            self.__listwidget.takeItem(self.__listwidget.row(item))

    def __clear_ctrls(self):
        self.__listwidget.clear()

    def __get_ctrls(self):
        return [self.__listwidget.item(i).text() for i in range(self.__listwidget.count())]

    def __open_claw(self):
        ctrls = self.__get_ctrls()
        if not ctrls:
            msgview(u'请先添加控制器', 1)
            return
        errors = open_claw_fun.open_claw(ctrls)
        if errors:
            msgview(u'以下控制器操作失败:\n{}'.format('\n'.join(errors)), 1)

    def __close_claw(self):
        ctrls = self.__get_ctrls()
        if not ctrls:
            msgview(u'请先添加控制器', 1)
            return
        errors = open_claw_fun.close_claw(ctrls)
        if errors:
            msgview(u'以下控制器操作失败:\n{}'.format('\n'.join(errors)), 1)

    def __reset_claw(self):
        ctrls = self.__get_ctrls()
        if not ctrls:
            msgview(u'请先添加控制器', 1)
            return
        errors = open_claw_fun.reset_claw(ctrls)
        if errors:
            msgview(u'以下控制器操作失败:\n{}'.format('\n'.join(errors)), 1)


if __name__ == '__main__':
    try:
        app = QApplication(sys.argv)
    except:
        app = QApplication.instance()
    ui = OpenClawUI()
    ui.show()
    sys.exit(app.exec_())
