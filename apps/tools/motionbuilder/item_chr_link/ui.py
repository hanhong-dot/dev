# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       : ui
# Describe   : 道具,关联角色,左右手 信息关联面板
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2023/5/12__15:20
# -------------------------------------------------------
try:
    from PySide2.QtWidgets import *
    from PySide2.QtGui import *
    from PySide2.QtCore import *
except:
    from Qt.QtWidgets import *
    from Qt.QtGui import *
    from Qt.QtCore import *


class ItemLinkUI(QFrame):
    def __init__(self, parent=None):
        super(ItemLinkUI, self).__init__(parent)
        self.window = QMainWindow()
        self.window.resize(300, 500)
        self._builder()

    def _builder(self):
        self._setup()
        self.layout_active = QVBoxLayout(self)
        self.layout_active.addLayout(self.list_layout)
        self.layout_active.addLayout(self.radio_layout)
        self.layout_active.addWidget(self.link_pushButton)

        self.layout_active.addWidget(self.Export_pushButton)
        self.layout_active.addWidget(self.reload_pushButton)
        self.layout_active.addWidget(self.clear_link_pushButton)

        self.link_pushButton.clicked.connect(self._link)
        self.Export_pushButton.clicked.connect(self._export)
        self.reload_pushButton.clicked.connect(self._reload)

    def _setup(self):
        self.item_layout = QVBoxLayout()

        self.ItemLabel = QLabel(self.window)
        self.ItemLabel.setText("请选择道具")

        self.ItemlistView = QListWidget(self.window)
        self.ItemlistView.setObjectName(u"ItemlistView")
        self.ItemlistView.setSelectionMode(QListWidget.SingleSelection)

        self.item_layout.addWidget(self.ItemLabel)
        self.item_layout.addWidget(self.ItemlistView)

        self.chr_layout = QVBoxLayout()

        self.ChrLabel = QLabel(self.window)
        self.ChrLabel.setText("请选择关联角色")

        self.ChrlistView = QListWidget(self.window)
        self.ChrlistView.setObjectName(u"ChrlistView")
        self.ChrlistView.setSelectionMode(QListWidget.SingleSelection)

        self.chr_layout.addWidget(self.ChrLabel)
        self.chr_layout.addWidget(self.ChrlistView)

        self.list_layout = QHBoxLayout()
        self.list_layout.addLayout(self.item_layout)
        self.list_layout.addLayout(self.chr_layout)

        self.radioButton_L = QRadioButton(self.window)
        self.radioButton_L.setObjectName(u"lefthand")

        self.left_layout = QHBoxLayout()
        self.left_layout.addWidget(self.radioButton_L)

        # 删除 setGeometry 方法调用
        # self.LeftLabel.setGeometry(QRect(40, 40, 131, 192))
        self.LeftLabel = QLabel(self.window)
        self.LeftLabel.setText("左手")
        self.left_layout.addWidget(self.LeftLabel)

        self.radioButton_R = QRadioButton(self.window)
        self.radioButton_R.setObjectName(u"righthand")
        self.radioButton_R.setChecked(True)

        self.right_layout = QHBoxLayout()
        self.right_layout.addWidget(self.radioButton_R)

        self.RightLabel = QLabel(self.window)
        self.RightLabel.setText("右手")
        self.right_layout.addWidget(self.RightLabel)

        # 在左右手控件后面添加 QSpacerItem 对象
        self.left_layout.addItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.right_layout.addItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))

        self.radio_layout = QHBoxLayout()
        self.radio_layout.addLayout(self.left_layout)
        self.radio_layout.addLayout(self.right_layout)

        self.reload_pushButton = QPushButton(self.window)
        self.reload_pushButton.setText("重新加载道具和角色列表")

        self.link_pushButton = QPushButton(self.window)
        self.link_pushButton.setText("选择关联")

        self.clear_link_pushButton = QPushButton(self.window)
        self.clear_link_pushButton.setText("选择解除关联")

        self.Export_pushButton = QPushButton(self.window)
        self.Export_pushButton.setText("导出关联信息")

    def _link(self):
        print('link')
        pass

    def _export(self):
        pass

    def _reload(self):
        pass


if __name__ == '__main__':
    try:
        import sys

        app = QApplication(sys.argv)
    except:
        app = QApplication.instance()

    window = ItemLinkUI()
    window.show()

    app.exec_()
