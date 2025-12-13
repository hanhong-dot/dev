# -*- coding: utf-8 -*-
# -----------------------------------
# @File    : replace_rig_tool_ui.py
# @Author  : linhuan
# @Time    : 2025/10/9 10:43
# @Description : 
# -----------------------------------
import os

try:
    from PySide2.QtWidgets import *
    from PySide2.QtGui import *
    from PySide2.QtCore import *
except:
    from PyQt5.QtWidgets import *
    from PyQt5.QtGui import *
    from PyQt5.QtCore import *

from apps.publish.ui.message.messagebox import msgview
from lib.common.log import Logger
import apps.tools.maya.replace_rig_tool.replace_rig_fun as replace_rig_fun

reload(replace_rig_fun)
from method.common.dir import set_localtemppath
from lib.common import jsonio


class ReplaceRigToolUI(QDialog):
    def __init__(self, parent=None):
        super(ReplaceRigToolUI, self).__init__(parent)
        self.__current_time = self.__get_current_time()
        self.__log_file = '{}/replace_rig_{}.log'.format(self.__get_local_dir(), self.__current_time)
        self.__json_file = '{}/replace_rig_data.json'.format(self.__get_json_dir())

        self.__logger = Logger(self.__log_file)
        self.setWindowTitle(u"批量替换角色绑定")
        self.setGeometry(100, 100, 400, 200)
        self.__init_ui()
        self.__connect_signals()

    def __init_ui(self):
        self.__layout = QVBoxLayout(self)

        self.__batch_file_layout = QHBoxLayout()
        self.__batch_file_label = QLabel(u"批量文件路径:")
        self.__batch_file_input = QLineEdit()
        self.__batch_file_browse = QPushButton(u"浏览")
        self.__batch_file_layout.addWidget(self.__batch_file_label)
        self.__batch_file_layout.addWidget(self.__batch_file_input)
        self.__batch_file_layout.addWidget(self.__batch_file_browse)
        self.__layout.addLayout(self.__batch_file_layout)

        self.__need_to_replace_layout = QHBoxLayout()
        self.__need_to_replace_label = QLabel(u"需要替换的绑定文件:")
        self.__need_to_replace_input = QLineEdit()
        self.__need_to_replace_browse = QPushButton(u"浏览")
        self.__need_to_replace_layout.addWidget(self.__need_to_replace_label)
        self.__need_to_replace_layout.addWidget(self.__need_to_replace_input)
        self.__need_to_replace_layout.addWidget(self.__need_to_replace_browse)
        self.__layout.addLayout(self.__need_to_replace_layout)

        self.__replace_with_layout = QHBoxLayout()
        self.__replace_with_label = QLabel(u"替换后的绑定文件:")
        self.__replace_with_input = QLineEdit()
        self.__replace_with_browse = QPushButton(u"浏览")
        self.__replace_with_layout.addWidget(self.__replace_with_label)
        self.__replace_with_layout.addWidget(self.__replace_with_input)
        self.__replace_with_layout.addWidget(self.__replace_with_browse)
        self.__layout.addLayout(self.__replace_with_layout)
        self.__set_data_from_json()

        self.__replace_button = QPushButton(u"执行替换")
        self.__layout.addWidget(self.__replace_button)
        self.__layout.addStretch()

    def __set_data_from_json(self):
        if os.path.exists(self.__json_file):
            __data = jsonio.read(self.__json_file)
            if 'batch_file_path' in __data:
                self.__batch_file_input.setText(__data['batch_file_path'])
            if 'need_to_replace_file' in __data:
                self.__need_to_replace_input.setText(__data['need_to_replace_file'])
            if 'replace_with_file' in __data:
                self.__replace_with_input.setText(__data['replace_with_file'])

    def _write_data_to_json(self):
        __data = {
            'batch_file_path': self.__batch_file_input.text().strip(),
            'need_to_replace_file': self.__need_to_replace_input.text().strip(),
            'replace_with_file': self.__replace_with_input.text().strip()
        }

        jsonio.write(__data,self.__json_file)

    def __connect_signals(self):
        self.__batch_file_browse.clicked.connect(self.__browse_batch_file)
        self.__need_to_replace_browse.clicked.connect(self.__browse_need_to_replace_file)
        self.__replace_with_browse.clicked.connect(self.__browse_replace_with_file)
        self.__replace_button.clicked.connect(self.__replace_button_clicked)

    def __browse_batch_file(self):
        # 选择文件夹
        # file_path, _ = QFileDialog.getOpenFileName(self, u"选择批量文件", "", "All Files (*);;Text Files (*.txt)")
        # if file_path:
        #     self.__batch_file_input.setText(file_path)
        dir_path = QFileDialog.getExistingDirectory(self, u"选择批量文件夹", "")
        if dir_path:
            self.__batch_file_input.setText(dir_path)

    def __browse_need_to_replace_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, u"选择需要替换的绑定文件", "",
                                                   "Maya Files (*.ma *.mb);;All Files (*)")
        if file_path:
            self.__need_to_replace_input.setText(file_path)

    def __browse_replace_with_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, u"选择替换后的绑定文件", "",
                                                   "Maya Files (*.ma *.mb);;All Files (*)")
        if file_path:
            self.__replace_with_input.setText(file_path)

    def __replace_button_clicked(self):
        self._write_data_to_json()

        __dir_path = self.__batch_file_input.text().strip()
        if not __dir_path or not os.path.exists(__dir_path):
            msgview(u'请正确输入批量路径', 1)
            return
        __ma_files = self.__get_ma_files_from_dir(__dir_path)
        if not __ma_files:
            msgview(u'批量路径下没有.ma文件', 1)
            return
        __need_to_replace_file = self.__need_to_replace_input.text().strip()
        if not __need_to_replace_file or not os.path.exists(
                __need_to_replace_file) or not __need_to_replace_file.endswith('.ma'):
            msgview(u'请正确输入需要替换的绑定文件(ma文件)', 1)
            return
        __replace_with_file = self.__replace_with_input.text().strip()
        if not __replace_with_file or not os.path.exists(__replace_with_file) or not __replace_with_file.endswith(
                '.ma'):
            msgview(u'请正确输入替换后的绑定文件(ma文件(', 1)
            return
        self.__logger.info('=================开始替换=================')
        self.__logger.info('批量文件路径:{}'.format(__dir_path))
        self.__logger.info('需要替换的绑定文件:{}'.format(__need_to_replace_file))
        self.__logger.info('替换后的绑定文件:{}'.format(__replace_with_file))
        self.__logger.info('需要处理的文件:{}'.format(__ma_files))

        replace_rig_fun.batch_replace_rig(__ma_files, __need_to_replace_file, __replace_with_file, self.__logger)
        msgview(u'替换完成,请查看日志:\n{}'.format(self.__log_file), 2)

    def __get_ma_files_from_dir(self, dir_path):
        ma_files = []
        __files = os.listdir(dir_path)
        for f in __files:
            if f.endswith('.ma'):
                __path = os.path.join(dir_path, f)
                __path = __path.replace('\\', '/')
                if os.path.isfile(__path):
                    ma_files.append(__path)
        return ma_files

    def __get_current_time(self):
        return QDateTime.currentDateTime().toString("yyyy-MM-dd-hh-mm-ss")

    def __get_local_dir(self):
        local_temp_path = set_localtemppath(sub_dir='Info_Temp/replace_rig/log')
        if not os.path.exists(local_temp_path):
            os.makedirs(local_temp_path)
        return local_temp_path

    def __get_json_dir(self):
        local_temp_path = set_localtemppath(sub_dir='Info_Temp/replace_rig/json')
        if not os.path.exists(local_temp_path):
            os.makedirs(local_temp_path)
        return local_temp_path


if __name__ == '__main__':
    import sys

    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)
    win_handle = ReplaceRigToolUI()
    win_handle.show()
    app.exec_()
