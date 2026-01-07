# -*- coding: utf-8 -*-
# author: linhuan
# file: auto_copy_skin_ui.py
# time: 2025/12/13 11:49
# description:
import os.path
import sys

try:
    from PySide2.QtWidgets import *
    from PySide2.QtGui import *
    from PySide2.QtCore import *
except:
    from PyQt5.QtWidgets import *
    from PyQt5.QtGui import *
    from PyQt5.QtCore import *

from apps.publish.ui.message.messagebox import msgview
from apps.tools.maya.auto_copy_skin_tool import sg_fun as copy_skin_sg_fun
from apps.tools.maya.auto_copy_skin_tool import auto_copy_skin_fun

reload(copy_skin_sg_fun)

MAPINGDATA = {
    'PL': 'PL_Body',
    'ST': 'ST_Body',
    'FY': 'FY_Body_New',
    'RY': 'RY_Body',
    'YG': 'YG_Body',
    'YS': 'YS_Body',
    'XL': 'XL_Body'

}


class AutoCopySkinUI(QWidget):
    def __init__(self, sg, TaskData, parent=None):
        super(AutoCopySkinUI, self).__init__(parent)
        self.setWindowTitle(u"自动蒙皮工具")
        self.setGeometry(100, 100, 100, 100)
        self.setWindowFlags(Qt.Window)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.__sg = sg
        self.__task_data = TaskData
        self.__asset_name = self.__task_data.entity_name
        self.__entity_type = self.__task_data.entity_type
        self.__asset_type = self.__task_data.asset_type
        self.__task_name = self.__task_data.task_name
        self.__init_ui()
        self.__connect_signals()

    def __init_ui(self):
        main_layout = QVBoxLayout(self)
        self.__title_layout = QHBoxLayout()
        self.__title_txt = u"当前资产: {0}  类型: {1}  任务: {2}".format(self.__asset_name, self.__asset_type,
                                                                         self.__task_name)

        self.__group_box = QGroupBox(self.__title_txt)

        self.__group_box_layout = QVBoxLayout()
        self.__group_box.setLayout(self.__group_box_layout)

        self.__target_asset_layout = QHBoxLayout()
        self.__target_asset_label = QLabel(u"body资产:")
        self.__asset_abb = self.__get_asset_abb()
        if self.__asset_abb:
            mapping_body_asset = self.__get_mapping_body_asset(self.__asset_abb)
            if mapping_body_asset:
                self.__target_asset_line_edit = QLineEdit(mapping_body_asset)
            else:
                self.__target_asset_line_edit = QLineEdit(u"未找到对应body资产，请手动输入")

        self.__target_asset_layout.addWidget(self.__target_asset_label)
        self.__target_asset_layout.addWidget(self.__target_asset_line_edit)
        self.__target_asset_layout.addStretch()
        self.__target_asset_layout.addSpacing(40)

        self.__group_box_layout.addLayout(self.__target_asset_layout)
        self.__out_put_layout = QHBoxLayout()
        self.__out_pub_label = QLabel(u"输出路径:")
        self.__out_put_line_edit = QLineEdit()
        self.__out_put_button = QPushButton(u"选择路径")
        self.__out_put_layout.addWidget(self.__out_pub_label)
        self.__out_put_layout.addWidget(self.__out_put_line_edit)
        self.__out_put_layout.addWidget(self.__out_put_button)
        self.__group_box_layout.addLayout(self.__out_put_layout)

        self.__copy_skin_button = QPushButton(u"确定自动蒙皮")
        self.__copy_skin_button.setFixedHeight(25)
        main_layout.addWidget(self.__group_box)
        main_layout.addWidget(self.__copy_skin_button)
        self.setLayout(main_layout)

    def __connect_signals(self):
        self.__out_put_button.clicked.connect(
            lambda: self.__out_put_line_edit.setText(QFileDialog.getExistingDirectory(self, u"选择输出路径", "")))
        self.__copy_skin_button.clicked.connect(self.__on_copy_skin_clicked)

    def __on_copy_skin_clicked(self):
        __target_asset_name = self.__target_asset_line_edit.text().strip()
        __out_put_path = self.__out_put_line_edit.text().strip()
        if not __out_put_path:
            msgview(u"请填写输出路径！", 0)
            return
        if not os.path.exists(__out_put_path):
            try:
                os.makedirs(__out_put_path)
            except Exception as e:
                msgview(u"输出路径创建失败，请检查路径是否正确！", 0)
                return
        if not __target_asset_name:
            msgview(u"请填写目标body资产名称！", 0)
            return
        ok, result = self.__check_body_asset_exist(__target_asset_name)
        if not ok:
            msgview(result, 0)
            return
        ok, result = self.__get_asset_rig_publish_file(__target_asset_name)
        if not ok:
            msgview(result, 0)
            return

        body_rig_publish_file = result
        ok, result = copy_skin_sg_fun.auto_copy_skin(__target_asset_name, self.__asset_type, self.__asset_abb,
                                                     body_rig_publish_file, __out_put_path)
        if not ok:
            msgview(result, 0)
            return
        else:
            __add_path_list, __over_path_list = result
            __msg = u"蒙皮复制完成！\n"
            if __add_path_list:
                __msg = __msg + u"新增文件:\n"
                for path in __add_path_list:
                    __msg += u"{}\n".format(path)
            if __over_path_list:
                __msg = __msg + u"覆盖文件:\n"
                for path in __over_path_list:
                    __msg += u"{}\n".format(path)
            msgview(__msg, 2)

    def __get_asset_abb(self):
        if self.__entity_type != "Asset":
            msgview(u"当前资产不是Asset，无法使用自动蒙皮工具", 0)
            return
        if self.__asset_type not in ['role', 'hair']:
            msgview(u"当前资产类型不是role或hair，无法使用自动蒙皮工具", 0)
            return
        return self.__asset_name[:2]

    def __get_mapping_body_asset(self, asset_abb=None):
        if asset_abb in MAPINGDATA.keys():
            return MAPINGDATA[asset_abb]
        else:
            return None

    def __get_asset_rig_publish_file(self, asset_name):
        return copy_skin_sg_fun.get_rig_publish_file_by_asset_name(asset_name)

    def __check_body_asset_exist(self, body_asset_name):
        return copy_skin_sg_fun.check_targe_asset_type(self.__sg, body_asset_name)
