# -*- coding: utf-8 -*-
# author: linhuan
# file: mb_replace_rig_ui.py
# time: 2025/10/14 21:06
# description:
import os

from PySide2.QtWidgets import *
from PySide2.QtCore import *

from lib.common.log import Logger
from apps.publish.ui.message.messagebox import msgview

import apps.tools.motionbuilder.mb_replace_rig.mb_replace_fun as mb_replace_fun
reload(mb_replace_fun)

import json


class MBReplaceRigUI(QDialog):
    def __init__(self, parent=None):
        super(MBReplaceRigUI, self).__init__(parent)
        self.__mb_window_name = "MBReplaceRigUI"
        self.__mb_window_title = "批量替换角色体"
        self.__mb_window_size = (600, 300)
        self.__current_time = self.__get_current_time()
        self.__local_dir = self.__get_local_dir()
        self.__json_dir = self.__get_json_dir()
        self._log_file = '{}/replace_character_{}.log'.format(self.__get_local_dir(), self.__current_time)
        self.__json_file = '{}/replace_character_data.json'.format(self.__get_json_dir())

        self.__init_ui()

        self.__logger = Logger(self._log_file)
        self.__connect_signals()

    def __init_ui(self):
        self.__main_layout = QVBoxLayout(self)
        self.__batch_file_layout = QHBoxLayout()
        self.__batch_file_label = QLabel(u"批量文件路径:")
        self.__batch_file_input = QLineEdit()
        self.__batch_file_browse = QPushButton(u"浏览")
        self.__batch_file_layout.addWidget(self.__batch_file_label)
        self.__batch_file_layout.addWidget(self.__batch_file_input)
        self.__batch_file_layout.addWidget(self.__batch_file_browse)
        self.__main_layout.addLayout(self.__batch_file_layout)

        self.__need_replace_chr_layout = QHBoxLayout()
        self.__need_replace_chr_label = QLabel(u"需要替换rig:")
        self.__need_replace_chr_input = QLineEdit()
        self.__need_replace_chr_layout.addWidget(self.__need_replace_chr_label)
        self.__need_replace_chr_layout.addWidget(self.__need_replace_chr_input)

        self.__replace_layout = QHBoxLayout()
        self.__replace_label = QLabel(u"替换角色体文件:")
        self.__replace_input = QLineEdit()
        self.__replace_browse = QPushButton(u"浏览")
        self.__replace_layout.addWidget(self.__replace_label)
        self.__replace_layout.addWidget(self.__replace_input)
        self.__replace_layout.addWidget(self.__replace_browse)
        self.__set_data_from_json()

        self.__btn_confirm = QPushButton(u"确认替换")
        self.__btn_cancel = QPushButton(u"取消")

        self.__main_layout.addLayout(self.__need_replace_chr_layout)
        self.__main_layout.addLayout(self.__replace_layout)
        self.__main_layout.addWidget(self.__btn_confirm)
        self.__main_layout.addWidget(self.__btn_cancel)

    def __get_local_dir(self):
        local_temp_path = set_localtemppath(sub_dir='Info_Temp/mobu/replace_character/log')
        if not os.path.exists(local_temp_path):
            os.makedirs(local_temp_path)
        return local_temp_path

    def __get_json_dir(self):
        local_temp_path = set_localtemppath(sub_dir='Info_Temp/mobu/replace_character/json')
        if not os.path.exists(local_temp_path):
            os.makedirs(local_temp_path)
        return local_temp_path

    def __get_current_time(self):
        return QDateTime.currentDateTime().toString("yyyy-MM-dd-hh-mm-ss")

    def __connect_signals(self):
        self.__batch_file_browse.clicked.connect(self.__browse_batch_path)
        self.__replace_browse.clicked.connect(self.__browse_replace_file)

        self.__btn_confirm.clicked.connect(self.__confirm_replace)
        self.__btn_cancel.clicked.connect(self.close)

    def __browse_replace_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "选择替换角色体文件", "", "FBX Files (*.fbx);;All Files (*)")
        if file_path:
            self.__replace_input.setText(file_path)

    def __browse_batch_path(self):
        dir_path = QFileDialog.getExistingDirectory(self, "选择批量文件路径", "")
        if dir_path:
            self.__batch_file_input.setText(dir_path)

    def __write_data_to_json(self):
        __data = {
            'batch_file_path': self.__batch_file_input.text().strip(),
            'need_to_replace_rig': self.__need_replace_chr_input.text().strip(),
            'replace_with_file': self.__replace_input.text().strip()
        }

        json_write(__data, self.__json_file)

    def __set_data_from_json(self):
        if os.path.exists(self.__json_file):
            __data = json_read(self.__json_file)
            if 'batch_file_path' in __data:
                self.__batch_file_input.setText(__data['batch_file_path'])
            if 'need_to_replace_rig' in __data:
                self.__need_replace_chr_input.setText(__data['need_to_replace_rig'])
            if 'replace_with_file' in __data:
                self.__replace_input.setText(__data['replace_with_file'])

    def __confirm_replace(self):
        self.__write_data_to_json()
        batch_path = self.__batch_file_input.text()
        if not batch_path or not os.path.exists(batch_path):
            msgview(u"请输入批量文件路径", 2)

            return
        need_replace_chr = self.__need_replace_chr_input.text()
        if not need_replace_chr:
            msgview(u"请填写需要替换的角色体", 2)
            return
        replace_file = self.__replace_input.text()
        if not replace_file or not os.path.exists(replace_file):
            msgview(u"请选择替换角色体文件", 2)
            return
        self.__logger.info("开始批量替换角色体")
        self.__logger.info("批量文件路径: {}".format(batch_path))
        self.__logger.info("需要替换角色体: {}".format(need_replace_chr))
        self.__logger.info("替换角色体文件: {}".format(replace_file))
        ok, reslut = mb_replace_fun.batch_replace_character_from_dir(batch_path, need_replace_chr, replace_file,
                                                                     log_handle=self.__logger)
        if not ok:
            msgview(reslut, 0)
            msgview(u'请查看日志文件:\n{}'.format(self._log_file), 0)
            return
        self.__logger.info("批量替换角色体完成")
        msgview(u"批量替换角色体完成,请查看日志文件:\n{}".format(self._log_file), 2)


def set_localtemppath(sub_dir='Info_Temp/'):
    _root = ''
    if os.path.exists('D:/'):
        _root = 'D:/'
    elif os.path.exists('E:/'):
        _root = 'E:/'
    elif os.path.exists('F:/'):
        _root = 'F:/'
    elif os.path.exists('C:/'):
        _root = 'C:/'
    if not _root:
        return False
    _tempPath = _root + sub_dir
    if not os.path.exists(_tempPath):
        try:
            os.makedirs(_tempPath)
        except:
            return False
    return _tempPath


def json_read(path, rtype="r", hook=None):
    if not os.path.exists(path):
        return None
    with open(path, rtype) as f:
        _data = json.load(f, object_pairs_hook=hook)
        f.close()
    return _data


def json_write(info, path, wtype="w"):
    _path = os.path.dirname(path)
    if not os.path.exists(_path):
        os.makedirs(_path)
    with open(path, wtype) as f:
        json.dump(info, f, indent=4, separators=(',', ':'))
        f.close()
    return True
