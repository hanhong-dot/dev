# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       :
# Describe   :
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2025/2/28__17:48
# -------------------------------------------------------

import os

try:
    from PySide2.QtWidgets import *
    from PySide2.QtGui import *
    from PySide2.QtCore import *
except:
    from PyQt5.QtWidgets import *
    from PyQt5.QtGui import *
    from PyQt5.QtCore import *
import lib.common.jsonio as _jsonio

INPUTPATH = 'Z:/netrender/animation/submit'

SAVEPATH = 'Z:/netrender/animation/save'
from apps.publish.ui.message.messagebox import msgview


class SubmissionMayaCoverUI(QWidget):
    def __init__(self, parent=None):
        super(SubmissionMayaCoverUI, self).__init__(parent)
        self.setWindowTitle("Submission Maya Cover")
        self.resize(400, 200)
        self.setWindowFlags(Qt.Window)
        self.setWindowModality(Qt.ApplicationModal)
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)
        self.__property_data = self.get_property_from_json

        self.__create_cover_widgets()
        self.__create_cover_layout()
        self.__create_connections()

    def __create_cover_widgets(self):
        self.__sub_ma_btn = QPushButton(u"提交任务")
        self.__sub_ma_btn.setToolTip("Cover to maya2018.")

        self.__cancel_btn = QPushButton("Cancel")
        self.__cancel_btn.setToolTip("Close the window.")

    @property
    def get_property_from_json(self):
        return self.__read_json()

    def __set_property_layout(self):
        self.__property_layout = QVBoxLayout()
        self.__property_group = QGroupBox()
        self.__property_group.setLayout(self.__property_layout)
        self.main_layout.addWidget(self.__property_group)

        self.__set_input_path_layout(self.__property_layout)
        self.__set_save_path_layout(self.__property_layout)

    def __set_input_path_layout(self, layout):
        self.__input_path_layout = QHBoxLayout()
        self.__input_path_label = QLabel("SourceFilePath:")
        self.__input_path_line_edit = QLineEdit()
        if self.__property_data and "input_path" in self.__property_data:
            self.__input_path_line_edit.setText(self.__property_data["input_path"])
        else:
            self.__input_path_line_edit.setText(INPUTPATH)
        self.__input_path_btn = QPushButton("...")
        self.__input_path_layout.addWidget(self.__input_path_label)
        self.__input_path_layout.addWidget(self.__input_path_line_edit)
        self.__input_path_layout.addWidget(self.__input_path_btn)
        self.__input_path_btn.setFixedWidth(30)
        self.__input_path_btn.clicked.connect(lambda: self.__set_push_path(self.__input_path_line_edit))
        layout.addLayout(self.__input_path_layout)

    def __set_push_path(self, path_line_edit):
        path = QFileDialog.getExistingDirectory(self, "选择文件夹", path_line_edit.text())
        if path:
            path_line_edit.setText(path)

    def __set_save_path_layout(self, layout):
        self.__save_path_layout = QHBoxLayout()
        self.__save_path_label = QLabel("SaveDir:")
        self.__save_path_line_edit = QLineEdit()
        if self.__property_data and "save_path" in self.__property_data:
            self.__save_path_line_edit.setText(self.__property_data["save_path"])
        else:
            self.__save_path_line_edit.setText(SAVEPATH)
        self.__save_path_btn = QPushButton("...")
        self.__save_path_layout.addWidget(self.__save_path_label)
        self.__save_path_layout.addWidget(self.__save_path_line_edit)
        self.__save_path_layout.addWidget(self.__save_path_btn)
        self.__save_path_btn.setFixedWidth(30)
        self.__save_path_btn.clicked.connect(lambda: self.__set_push_path(self.__save_path_line_edit))
        layout.addLayout(self.__save_path_layout)

    def __read_json(self):
        __json_file = self.__get_json_file()
        if not os.path.exists(__json_file):
            return {}
        return _jsonio.read(__json_file)

    def __write_json(self, dict):
        __json_file = self.__get_json_file()
        _jsonio.write(dict, __json_file)

    def __get_json_file(self):
        __dir = self.__get_json_dir()
        return '{}/cover_to_maya2018.json'.format(__dir)

    def __get_json_dir(self):
        __dir = os.path.normpath(os.path.expandvars('%AppData%/maya/cover_version/property'))
        if not os.path.exists(__dir):
            os.makedirs(__dir)
        return __dir

    def __create_cover_layout(self):
        self.__set_property_layout()

        #
        # self.main_layout.addStretch()
        self.main_layout.addWidget(self.__sub_ma_btn)
        self.main_layout.addWidget(self.__cancel_btn)

    def __create_connections(self):
        self.__sub_ma_btn.clicked.connect(self.__sub_ma_clicked)
        self.__cancel_btn.clicked.connect(self.close)

    def __get_property(self):
        __property = {}
        __property['input_path'] = self.__input_path_line_edit.text()
        __property['save_path'] = self.__save_path_line_edit.text()
        return __property

    def __sub_ma_clicked(self):
        from apps.tools.maya.sub_animation_cover import sub_cover_to_deadline
        from lib.common import admin_process
        import shutil

        __source_path = self.__input_path_line_edit.text()
        __save_dir = self.__save_path_line_edit.text()
        __source_dir = __source_path.replace('\\', '/')
        __save_dir = __save_dir.replace('\\', '/')

        if not __source_path:
            msgview(u'请填入需要处理的ma文件或文件夹', 0)
            return
        if not os.path.exists(__source_path):
            msgview(u'输入路径不存在', 0)
            return
        ok, result = sub_cover_to_deadline.sub_cover_files_to_maya2018_to_deadline(__source_path, __save_dir)
        if not ok:
            msgview(u'提交失败:\n{}'.format(result), 0)
            return

        self.__write_json(self.__get_property())
        # QMessageBox.information(self, '提示', '提交成功')
        msgview(u'提交成功', 2)
        return


if __name__ == '__main__':
    app = QApplication([])
    win = SubmissionMayaCoverUI()
    win.show()
    app.exec_()
