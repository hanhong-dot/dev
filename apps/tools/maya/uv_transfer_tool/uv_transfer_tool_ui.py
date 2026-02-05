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

        instruction_label = QLabel("Select two meshes in the scene:\n"
                                   "1. Source Mesh (with desired UVs)\n"
                                   "2. Target Mesh (to receive UVs)")
        instruction_label.setWordWrap(True)
        layout.addWidget(instruction_label)

        uv_set_layout = QHBoxLayout()
        uv_set_label = QLabel("Target UVSet Name:")
        self.uv_set_input = QLineEdit("map3")
        uv_set_layout.addWidget(uv_set_label)
        uv_set_layout.addWidget(self.uv_set_input)
        layout.addLayout(uv_set_layout)

        self.transfer_button = QPushButton("Transfer UVs")
        self.transfer_button.clicked.connect(self.on_transfer_uvs)
        layout.addWidget(self.transfer_button)

        self.result_label = QLabel("")
        layout.addWidget(self.result_label)

        self.setLayout(layout)

    def on_transfer_uvs(self):
        target_uv_set_name = self.uv_set_input.text().strip()
        if not target_uv_set_name:
            self.result_label.setText("map4")
            return
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
