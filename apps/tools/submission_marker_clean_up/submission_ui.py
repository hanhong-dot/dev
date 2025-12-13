# -*- coding: utf-8 -*-#
import os

from apps.publish.ui.message.messagebox import msgview
try:
    from PySide2.QtWidgets import *
    from PySide2.QtGui import *
    from PySide2.QtCore import *
except:
    from PyQt5.QtWidgets import *
    from PyQt5.QtGui import *
    from PyQt5.QtCore import *
import lib.common.jsonio as _jsonio

INPUTPATH='M:/projects/x3_shogun/AI_Marker_Clean_Up/data/'

SAVEPATH='M:/projects/x3_shogun/AI_Marker_Clean_Up/save/'



class SubmissionMarkerCleanUpUI(QWidget):
    def __init__(self, parent=None):
        super(SubmissionMarkerCleanUpUI, self).__init__(parent)
        self.setWindowTitle("Submission Marker Clean Up Tool")
        self.resize(400, 200)
        self.setWindowFlags(Qt.Window)
        self.setWindowModality(Qt.ApplicationModal)
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)
        self.__property_data = self.get_property_from_json

        self.create_widgets()
        self.create_layout()
        self.create_connections()

    def create_widgets(self):
        self.clean_up_btn = QPushButton(u"提交任务")
        self.clean_up_btn.setToolTip("Clean up all submission markers in the scene.")

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setToolTip("Close the window.")

    @property
    def get_property_from_json(self):
        return self.__read_json()

    def __set_property_layout(self):
        self.__property_layout = QVBoxLayout()
        self.__property_group = QGroupBox()
        # self.__property_group.setTitle("Property")
        self.__property_group.setLayout(self.__property_layout)
        self.main_layout.addWidget(self.__property_group)
        self.__set_file_type_layout(self.__property_layout)
        # self.__set_p4_project_path_layout(self.__property_layout)
        self.__set_input_path_layout(self.__property_layout)
        self.__set_save_path_layout(self.__property_layout)

    def __set_input_path_layout(self, layout):
        self.__input_path_layout = QHBoxLayout()
        self.__input_path_label = QLabel("SourceDir:")
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

    # def __set_p4_project_path_layout(self, layout):
    #     self.__p4_project_path_layout = QHBoxLayout()
    #     self.__p4_project_path_label = QLabel("P4Project:")
    #     self.__p4_project_path_text = QTextEdit()
    #     if self.__property_data and "p4_project_path" in self.__property_data:
    #         self.__p4_project_path_text.setText(self.__property_data["p4_project_path"])
    #     else:
    #         self.__p4_project_path_text.setText(u"//depot/X3_RawData/Animation")
    #     self.__p4_project_path_text.setEnabled(False)
    #     self.__p4_project_path_text.setFixedHeight(25)
    #     self.__p4_project_path_layout.addWidget(self.__p4_project_path_label)
    #     self.__p4_project_path_layout.addWidget(self.__p4_project_path_text)
    #
    #     layout.addLayout(self.__p4_project_path_layout)

    def __set_file_type_layout(self, layout):
        self.__file_type_layout = QHBoxLayout()

        self.__file_type_label = QLabel("FileType:")
        self.__file_type = QComboBox()
        self.__file_type.setFixedWidth(400)
        self.__file_type_layout.setAlignment(Qt.AlignLeft)
        self.__file_type.addItems([u'mcp', u'x2d', u'vdf'])
        if self.__property_data and "file_type" in self.__property_data:
            self.__file_type.setCurrentText(self.__property_data["file_type"])
        else:
            self.__file_type.setCurrentText(u"mcp")
        self.__file_type_layout.addWidget(self.__file_type_label)
        self.__file_type_layout.addWidget(self.__file_type)

        layout.addLayout(self.__file_type_layout)

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
        return '{}/submission_marker_clean_up.json'.format(__dir)

    def __get_json_dir(self):
        __dir = os.path.normpath(os.path.expandvars('%AppData%/shogun/marker_clean_up/property'))
        if not os.path.exists(__dir):
            os.makedirs(__dir)
        return __dir

    def create_layout(self):
        self.__set_property_layout()

        #
        # self.main_layout.addStretch()
        self.main_layout.addWidget(self.clean_up_btn)
        self.main_layout.addWidget(self.cancel_btn)

    def create_connections(self):
        self.clean_up_btn.clicked.connect(self.__clean_up_clicked)
        self.cancel_btn.clicked.connect(self.close)

    def __get_property(self):
        __property = {}
        __property['input_path'] = self.__input_path_line_edit.text()
        __property['file_type'] = self.__file_type.currentText()
        __property['save_path'] = self.__save_path_line_edit.text()
        return __property

    def __clean_up_clicked(self):
        from apps.tools.submission_marker_clean_up import sub_mark_fun
        reload(sub_mark_fun)
        from lib.common import admin_process
        import shutil

        __source_dir = self.__input_path_line_edit.text()
        __save_dir = self.__save_path_line_edit.text()
        __file_type = self.__file_type.currentText()
        __source_dir=__source_dir.replace('\\','/')
        __save_dir=__save_dir.replace('\\','/')
        ini_file='//10.10.201.151/share/development/netrende/ProgramData/Thinkbox/Deadline10/deadline.ini'
        local_ini_file='C:/ProgramData/Thinkbox/Deadline10/deadline.ini'
        local_in_dir='C:/ProgramData/Thinkbox/Deadline10'

        admin_process.process_copy(ini_file, local_ini_file)
        if not os.path.exists(local_in_dir):
            try:
                os.makedirs(local_in_dir)
            except:
                pass
        if not os.path.exists(local_ini_file):
            shutil.copy(ini_file, local_ini_file)


        QMessageBox.setStyleSheet(self, "QMessageBox{background-color: rgb(20, 20, 20);}")

        ok, result = sub_mark_fun.sub_mark_to_deadline(__source_dir, __file_type,__save_dir)
        if not ok:
            msgview(u'提交失败:\n{}'.format(result), 0)
            # QMessageBox.information(self, '提示', '提交失败:{}'.format(result))
            return

        self.__write_json(self.__get_property())
        msgview(u'提交成功', 2)
        # QMessageBox.information(self, '提示', '提交成功')

        return


if __name__ == '__main__':
    app = QApplication([])
    win = SubmissionMarkerCleanUpUI()
    win.show()
    app.exec_()
