# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       :
# Describe   : 模型每个点创建一个local
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2024/1019
# -------------------------------------------------------


try:
    from PySide2.QtWidgets import *
    from PySide2.QtGui import *
    from PySide2.QtCore import *
except:
    from PyQt5.QtWidgets import *
    from PyQt5.QtGui import *
    from PyQt5.QtCore import *

import apps.tools.maya.add_point_local.add_mesh_point_local as add_mesh_point_local

reload(add_mesh_point_local)
import sys
# from lib.common.log import Logger
#
# log_handle = Logger('D:/add_mesh_point_local_ui.log')


class LocalPointUI(QWidget):
    def __init__(self, parent=None):
        super(LocalPointUI, self).__init__(parent)
        self.__init_ui()
        self.__builder()
        self.__connect()

    def __connect(self):
        self.__add_btn.clicked.connect(self.__add_select_mesh)
        self.__remove_btn.clicked.connect(self.__remove_select_mesh)
        self._clear_btn.clicked.connect(self.__clear_select_mesh)
        self.__apply_btn.clicked.connect(self.__apply_local)

    def __init_ui(self):
        self.setWindowTitle(u'模型每个点创建一个local')
        self.resize(300, 100)
        self.__main_layout = QVBoxLayout()
        self.setLayout(self.__main_layout)

    def __builder(self):
        self.__add_layout = QHBoxLayout()
        self.__butoon_layout = QVBoxLayout()
        self.__add_btn = QPushButton(u'选择模型添加')
        self.__remove_btn = QPushButton(u'选择移除')
        self._clear_btn = QPushButton(u'清空')
        self.__listwidget = QListWidget()
        self.__listwidget.setSelectionMode(QAbstractItemView.ContiguousSelection)
        self.__listwidget.setVerticalScrollMode(QAbstractItemView.ScrollPerItem)
        self.__butoon_layout.addWidget(self.__add_btn)
        self.__butoon_layout.addWidget(self.__remove_btn)
        self.__butoon_layout.addWidget(self._clear_btn)
        self.__butoon_layout.setAlignment(Qt.AlignBaseline)
        self.__add_layout.addWidget(self.__listwidget)
        self.__add_layout.addLayout(self.__butoon_layout)

        self.__main_layout.addLayout(self.__add_layout)
        self.__start_layout = QHBoxLayout()
        self.__start_num_label = QLabel(u'local起始序号:')
        self._start_num_spinbox = QSpinBox()
        self._start_num_spinbox.setFixedSize(200, 25)
        self._start_num_spinbox.setMinimum(0)
        self._start_num_spinbox.setMaximum(1000000)
        self._start_num_spinbox.setValue(1000)

        self._auto_uv_layout = QHBoxLayout()
        self._auto_uv_lable=QLabel(u'是否自动生成UV:')
        self._auto_uv_combobox=QComboBox()
        self._auto_uv_combobox.addItems([u'是',u'否'])
        self._auto_uv_layout.addWidget(self._auto_uv_lable)
        self._auto_uv_layout.addWidget(self._auto_uv_combobox)
        self.__main_layout.addLayout(self._auto_uv_layout)
        self.__start_layout.addWidget(self.__start_num_label)
        self.__start_layout.addWidget(self._start_num_spinbox)

        self.__main_layout.addLayout(self.__start_layout)

        self.__apply_btn = QPushButton(u'创建约束local')
        self.__main_layout.addWidget(self.__apply_btn)

    def __add_select_mesh(self):
        select_meshs = add_mesh_point_local.get_select_meshs()
        listwidget_items = [self.__listwidget.item(i).text() for i in range(self.__listwidget.count())]
        if not select_meshs:
            return
        for mesh in select_meshs:
            if mesh in listwidget_items:
                continue
            self.__listwidget.addItem(mesh)

    def __remove_select_mesh(self):
        select_items = self.__listwidget.selectedItems()
        for item in select_items:
            self.__listwidget.takeItem(self.__listwidget.row(item))

    def __clear_select_mesh(self):
        self.__listwidget.clear()

    def __apply_local(self):
        start_num = self._start_num_spinbox.value()
        # log_handle.info('start add local point ......')
        # log_handle.info('start_num:{}'.format(start_num))
        select_meshs = [self.__listwidget.item(i).text() for i in range(self.__listwidget.count())]
        # log_handle.info('select_meshs:{}'.format(select_meshs))
        add_mesh_point_local.add_meshs_point_local_grp(select_meshs, grp_name='local_grp', start_num=start_num)


def load_ui():
    import apps.publish.ui.basewindow.basewiondow as basewindow
    import apps.launch.maya.interface.mayaview as _mayaview
    app = QApplication.instance()
    global mesh_point_tool_ui
    try:
        mesh_point_tool_ui.close()
        mesh_point_tool_ui.deleteLater()
    except:
        pass

    if not app:
        app = QApplication(sys.argv)
    mesh_point_tool_ui = basewindow.BaseWindow(_mayaview.get_maya_window(), "Add Mesh Locl Tool",
                                               "模型每个点创建一个local")

    mesh_point_tool_ui.set_central_widget(LocalPointUI())
    mesh_point_tool_ui.setMinimumSize(200, 300)
    mesh_point_tool_ui.show()
    app.exec_()


if __name__ == '__main__':
    import sys

    try:
        app = QApplication(sys.argv)
    except:
        app = QApplication.instance()
    ui = LocalPointUI()
    ui.show()
    sys.exit(app.exec_())
