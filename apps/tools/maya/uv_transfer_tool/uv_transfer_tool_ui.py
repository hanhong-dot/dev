# -*- coding: utf-8 -*-
# author: linhuan
# file: uv_transfer_tool_ui.py
# time: 2026/2/5 14:00
# description:
try:
    from PySide2.QtWidgets import *
    from PySide2.QtGui import *
    from PySide2.QtCore import *
except:
    from PyQt5.QtWidgets import *
    from PyQt5.QtGui import *
    from PyQt5.QtCore import *
from apps.tools.maya.uv_transfer_tool import uv_transfer_fun

reload(uv_transfer_fun)

from apps.publish.ui.message.messagebox import msgview


class UVTransferToolUI(QWidget):
    def __init__(self, parent=None):
        super(UVTransferToolUI, self).__init__(parent)
        self.setWindowTitle("UV Transfer Tool")
        self.setMinimumSize(300, 150)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        lable_layout = QHBoxLayout()

        instruction_label = QLabel(u"请选择两个模型：\n"
                                   u"1. 第一个模型,源模型（传递当前UV）\n"
                                   u"2. 第二个模型,目标模型（接收UV）")
        instruction_label.setWordWrap(True)
        # instruction_label背景色深色
        instruction_label.setStyleSheet("QLabel { background-color : #2c2c2c; color : white; padding: 8px; }")
        lable_layout.addWidget(instruction_label)
        layout.addLayout(lable_layout)
        lable_layout.addSpacing(10)
        # 加下拉线
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        layout.addWidget(line)

        uv_set_layout = QHBoxLayout()
        uv_set_label = QLabel(u"目标UVSet名称:")
        self.uv_set_input= QComboBox()
        self.uv_set_input.addItems(["map3", "map4"])
        self.uv_set_input.setCurrentText("map3")
        self.uv_set_input.setMinimumSize(200, 30)
        self.uv_set_input.setView(QListView())

        uv_set_layout.addWidget(uv_set_label)
        uv_set_layout.addWidget(self.uv_set_input)
        uv_set_layout.addStretch()
        line2 = QFrame()
        line2.setFrameShape(QFrame.HLine)
        line2.setFrameShadow(QFrame.Sunken)
        layout.addWidget(line2)

        layout.addLayout(uv_set_layout)

        self.transfer_button = QPushButton("Transfer UVs")
        self.transfer_button.setMinimumHeight(25)
        self.transfer_button.clicked.connect(self.on_transfer_uvs)
        layout.addWidget(self.transfer_button)

        self.result_label = QLabel("")
        layout.addWidget(self.result_label)

        self.setLayout(layout)

    def on_transfer_uvs(self):
        target_uv_set_name = self.uv_set_input.currentText()
        success, message = uv_transfer_fun.uv_transfer_mesh(target_uv_set_name)
        self.result_label.setText(message)
        if not success:
            msgview(message, 0)
        else:
            msgview(message, 2)


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    window = UVTransferToolUI()
    window.show()
    sys.exit(app.exec_())
