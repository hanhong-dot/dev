# -*- coding: utf-8 -*-#
# -------------------------------------------------------
# NAME       : pose_library_ui
# Describe   : 说明描述
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2025/4/25__下午5:41
# -------------------------------------------------------
try:
    from PySide2.QtWidgets import *
    from PySide2.QtGui import *
    from PySide2.QtCore import *
except:
    from PyQt5.QtWidgets import *
    from PyQt5.QtGui import *
    from PyQt5.QtCore import *

import os

from apps.tools.maya.pose_library_tool.pose_lib_analyze_xml import GetXMLData
from apps.tools.maya.pose_library_tool import pose_lib_fun

TABS = [u'Pose库', u'相机库', u'DB Pose库', u'本地Pose库', u'本地相机库', u'Character Action']
POSE_RIGHT_XML_NAME = 'pose_right_menu_config.xml'
from functools import partial
import time


class PoseLibraryUI(QWidget):
    def __init__(self, parent=None):
        super(PoseLibraryUI, self).__init__(parent)
        self.setWindowTitle("Pose Library")
        self.setGeometry(100, 100, 300, 400)
        self.setWindowFlags(Qt.Window)
        self.setAttribute(Qt.WA_DeleteOnClose)

        self.__setup_init()
        self.__connect()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.__refresh_library)
        self.timer.start(5)

    def __setup_init(self):
        # Layout
        self.__pose_library_data = pose_lib_fun.get_pose_library_data()
        self.__camera_library_data = pose_lib_fun.get_camera_library_data()
        self.__db_pose_library_data=pose_lib_fun.get_db_pose_library_data()
        self.__local_pose_library_data = pose_lib_fun.get_local_pose_library_data()
        self.__local_camera_library_data = pose_lib_fun.get_local_camera_library_data()
        self.__setup_layout = QHBoxLayout()
        self.__set_left_area()
        self.__set_center_area()
        self.__set_right_area()
        self.setLayout(self.__setup_layout)

    def __set_left_area(self):
        self.__left_layout = QVBoxLayout()
        self.__left_label = QLabel(u"角色")
        self.__left_label.setMinimumWidth(100)
        self.__left_list_weight = QListWidget()
        self.__left_list_weight.setMinimumWidth(100)
        self.__left_layout.addWidget(self.__left_label)
        self.__left_layout.addWidget(self.__left_list_weight)
        self.__setup_layout.addLayout(self.__left_layout)
        self.__set_left_list_weight()

    def __refresh_library(self):
        __character_list = self.__get_select_character()

        __current_tab_index = self.__center_tab_widget.currentIndex()
        self.__referesh_library(__character_list, __current_tab_index)

    def __set_right_area(self):
        self.__right_layout = QVBoxLayout()
        self.__right_layout.setAlignment(Qt.AlignTop)
        self.__right_label = QLabel("")
        self.__right_label.setMinimumWidth(200)

        self.__right_group = QGroupBox()
        self.__right_group.setAlignment(Qt.AlignTop)
        self.__right_group.setMinimumWidth(200)
        self.__right_group.setMaximumHeight(400)
        self.__right_group.setEnabled(False)

        self.__right_info_layout = QVBoxLayout()
        self.__right_group.setLayout(self.__right_info_layout)

        self.__chacter_label = QLabel()
        self.__pose_label = QLabel()
        self.__fbx_label = QLabel()
        self.__user_label = QLabel()
        self.__description_label = QLabel()
        self.__create_time_label = QLabel()
        self.__thumbnail_icon = QIcon()
        self.__right_info_layout.addWidget(self.__chacter_label)
        self.__right_info_layout.addWidget(self.__pose_label)
        # self.__right_group.addWidget(self.__fbx_label)
        # self.__right_group.addWidget(self.__thumbnail_label)
        self.__right_info_layout.addWidget(self.__user_label)
        self.__right_info_layout.addWidget(self.__description_label)
        self.__right_info_layout.addWidget(self.__create_time_label)

        self.__thumbnail_label = QLabel()
        self.__thumbnail_label.setPixmap(self.__thumbnail_icon.pixmap(128, 128))
        self.__right_info_layout.addWidget(self.__thumbnail_label)
        self.__right_layout.addWidget(self.__right_label)
        self.__right_layout.addWidget(self.__right_group)
        self.__setup_layout.addLayout(self.__right_layout)

    def __set_center_area(self):
        self.__center_layout = QVBoxLayout()

        self.__center_label = QLabel(u"请选择Pose或相机")
        # self.__center_layout.addWidget(self.__center_label)

        self.__set_center_tab()

        self.__set_center_list_weight()

        self.__setup_layout.addLayout(self.__center_layout)

    def __connect(self):

        self.__left_list_weight.itemClicked.connect(self.__click_pose_library_list)
        self.__center_tab_widget.currentChanged.connect(self.__click_pose_library_tab)
        self.__pose_library_list_weight.itemClicked.connect(self.__pose_library_list_weight_clicked)

        self.__pose_library_list_weight.setContextMenuPolicy(Qt.CustomContextMenu)

        self.__pose_library_list_weight.customContextMenuRequested.connect(self.__right_pose_library_context_menu)

        self.__camera_library_list_weight.itemClicked.connect(self.__click_camera_library_list)
        self.__camera_library_list_weight.setContextMenuPolicy(Qt.CustomContextMenu)
        self.__camera_library_list_weight.customContextMenuRequested.connect(self.__right_camera_library_context_menu)


        self.__db_pose_library_list_weight.itemClicked.connect(self.__db_pose_library_list_weight_clicked)
        self.__db_pose_library_list_weight.setContextMenuPolicy(Qt.CustomContextMenu)
        self.__db_pose_library_list_weight.customContextMenuRequested.connect(
            self.__right_db_pose_library_context_menu)

        self.__local_pose_library_list_weight.itemClicked.connect(self.__pose_library_list_weight_clicked)
        self.__local_pose_library_list_weight.setContextMenuPolicy(Qt.CustomContextMenu)
        self.__local_pose_library_list_weight.customContextMenuRequested.connect(
            self.__right_local_pose_library_context_menu)

        self.__local_camera_library_list_weight.itemClicked.connect(self.__click_camera_library_list)
        self.__local_camera_library_list_weight.setContextMenuPolicy(Qt.CustomContextMenu)
        self.__local_camera_library_list_weight.customContextMenuRequested.connect(
            self.__right_local_camera_library_context_menu)

        self.__left_list_weight.setContextMenuPolicy(Qt.CustomContextMenu)
        self.__left_list_weight.customContextMenuRequested.connect(self.__right_left_list_context_menu)

    def __click_camera_library_list(self, item):
        __item_data = item.data(Qt.UserRole)
        if not __item_data:
            return
        __camera_name = u'{}'.format(__item_data.get('name')) if 'name' in __item_data else ''
        __fbx_path = u'{}'.format(__item_data.get('fbx_path')) if 'fbx_path' in __item_data else ''
        __thumbnail_path = u'{}'.format(__item_data.get('thumbnail')) if 'thumbnail' in __item_data else ''
        __user = u'{}'.format(__item_data.get('user')) if 'user' in __item_data else ''
        __create_time = u'{}'.format(__item_data.get('create_time')) if 'create_time' in __item_data else ''
        __description = u'{}'.format(__item_data.get('description')) if 'description' in __item_data else ''
        __character = u'{}'.format(__item_data.get('character')) if 'character' in __item_data else ''

        self.__right_group.setEnabled(True)
        self.__right_group.setTitle(u'Camera信息')
        self.__chacter_label.setText(u'角色名称 {}'.format(__character))
        self.__pose_label.setText(u'相机资产名称 {}'.format(__camera_name))
        self.__fbx_label.setText(u'FBX路径 {}'.format(__fbx_path))
        # self.__thumbnail_label.setText(u'缩略图路径 {}'.format(__thumbnail_path))
        self.__user_label.setText(u'创建人 {}'.format(__user))
        self.__description_label.setText(u'描述信息 {}'.format(__description))
        self.__create_time_label.setText(u'创建时间 {}'.format(__create_time))

        if os.path.exists(__thumbnail_path):
            pixmap = QPixmap(__thumbnail_path)

            self.__thumbnail_label.setAlignment(Qt.AlignCenter)
            self.__thumbnail_label.setStyleSheet("background-color: rgb(85, 85, 85);")
            self.__thumbnail_label.setPixmap(pixmap.scaled(128, 128, Qt.KeepAspectRatio))
        else:
            self.__thumbnail_label.clear()

    def __pose_library_list_weight_clicked(self, item):
        __item_data = item.data(Qt.UserRole)
        if not __item_data:
            return
        __pose_name = u'{}'.format(__item_data.get('name')) if 'name' in __item_data else ''
        __fbx_path = u'{}'.format(__item_data.get('fbx_path')) if 'fbx_path' in __item_data else ''
        __thumbnail_path = u'{}'.format(__item_data.get('thumbnail')) if 'thumbnail' in __item_data else ''
        __user = u'{}'.format(__item_data.get('user')) if 'user' in __item_data else ''
        __create_time = u'{}'.format(__item_data.get('create_time')) if 'create_time' in __item_data else ''
        __description = u'{}'.format(__item_data.get('description')) if 'description' in __item_data else ''
        __character = u'{}'.format(__item_data.get('character')) if 'character' in __item_data else ''

        self.__right_group.setEnabled(True)
        self.__right_group.setTitle(u'Pose信息')
        self.__chacter_label.setText(u'角色名称 {}'.format(__character))
        self.__pose_label.setText(u'Pose名称 {}'.format(__pose_name))
        self.__fbx_label.setText(u'FBX路径 {}'.format(__fbx_path))
        # self.__thumbnail_label.setText(u'缩略图路径 {}'.format(__thumbnail_path))
        self.__user_label.setText(u'创建人 {}'.format(__user))
        self.__description_label.setText(u'描述信息 {}'.format(__description))
        self.__create_time_label.setText(u'创建时间 {}'.format(__create_time))
        if os.path.exists(__thumbnail_path):
            pixmap = QPixmap(__thumbnail_path)

            self.__thumbnail_label.setAlignment(Qt.AlignCenter)
            self.__thumbnail_label.setStyleSheet("background-color: rgb(85, 85 ,85);")
            self.__thumbnail_label.setPixmap(pixmap.scaled(128, 128, Qt.KeepAspectRatio))
        else:
            self.__thumbnail_label.clear()

    def __db_pose_library_list_weight_clicked(self,item):
        __item_data = item.data(Qt.UserRole)
        if not __item_data:
            return
        __db_pose_name = u'{}'.format(__item_data.get('name')) if 'name' in __item_data else ''
        __fbx_path = u'{}'.format(__item_data.get('fbx_path')) if 'fbx_path' in __item_data else ''
        __thumbnail_path = u'{}'.format(__item_data.get('thumbnail')) if 'thumbnail' in __item_data else ''
        __user = u'{}'.format(__item_data.get('user')) if 'user' in __item_data else ''
        __create_time = u'{}'.format(__item_data.get('create_time')) if 'create_time' in __item_data else ''
        __description = u'{}'.format(__item_data.get('description')) if 'description' in __item_data else ''
        __character = u'{}'.format(__item_data.get('character')) if 'character' in __item_data else ''
        self.__right_group.setEnabled(True)
        self.__right_group.setTitle(u'DB Pose信息')
        self.__chacter_label.setText(u'角色名称 {}'.format(__character))
        self.__pose_label.setText(u'Pose名称 {}'.format(__db_pose_name))
        self.__fbx_label.setText(u'FBX路径 {}'.format(__fbx_path))
        # self.__thumbnail_label.setText(u'缩略图路径 {}'.format(__thumbnail_path))
        self.__user_label.setText(u'创建人 {}'.format(__user))
        self.__description_label.setText(u'描述信息 {}'.format(__description))
        self.__create_time_label.setText(u'创建时间 {}'.format(__create_time))
        if os.path.exists(__thumbnail_path):
            pixmap = QPixmap(__thumbnail_path)

            self.__thumbnail_label.setAlignment(Qt.AlignCenter)
            self.__thumbnail_label.setStyleSheet("background-color: rgb(85, 85 ,85);")
            self.__thumbnail_label.setPixmap(pixmap.scaled(128, 128, Qt.KeepAspectRatio))
        else:
            self.__thumbnail_label.clear()


    def __right_db_pose_library_context_menu(self, pos):
        # 获取当前选中的项
        print('pos',pos)
        item = self.__db_pose_library_list_weight.itemAt(pos)
        print('item',item)
        if not item:
            return
        __right_process = GetXMLData().get_right_process_data_by_tab_name(POSE_RIGHT_XML_NAME, TABS[2])
        print('__right_process',__right_process)
        if not __right_process:
            return

        # 创建右键菜单
        self.__db_pos_lib_menu = QMenu(self)

        for process in __right_process:
            action = QAction(process['item_name'], self)
            process_command = process['process_command']
            print('process_command',process_command)
            action.setData(process)
            self.__db_pos_lib_menu.addAction(action)

            action.triggered.connect(partial(self.__process_action, process_command, item))

        self.__db_pos_lib_menu.exec_(self.__db_pose_library_list_weight.mapToGlobal(pos))
        __character = self.__get_select_character()
        self.__referesh_db_pose_library(__character)


    def __right_pose_library_context_menu(self, pos):
        # 获取当前选中的项
        item = self.__pose_library_list_weight.itemAt(pos)
        if not item:
            return
        __right_process = GetXMLData().get_right_process_data_by_tab_name(POSE_RIGHT_XML_NAME, TABS[0])
        if not __right_process:
            return

        # 创建右键菜单
        self.__pos_lib_menu = QMenu(self)

        for process in __right_process:
            action = QAction(process['item_name'], self)
            process_command = process['process_command']
            action.setData(process)
            self.__pos_lib_menu.addAction(action)

            action.triggered.connect(partial(self.__process_action, process_command, item))

        self.__pos_lib_menu.exec_(self.__pose_library_list_weight.mapToGlobal(pos))
        __character = self.__get_select_character()
        self.__refresh_pose_library_list(__character)




    def __right_local_pose_library_context_menu(self, pos):
        # 获取当前选中的项
        item = self.__local_pose_library_list_weight.itemAt(pos)
        if not item:
            return
        __right_process = GetXMLData().get_right_process_data_by_tab_name(POSE_RIGHT_XML_NAME, TABS[3])
        if not __right_process:
            return

        # 创建右键菜单
        self.__local_pose_lib_menu = QMenu(self)

        for process in __right_process:
            action = QAction(process['item_name'], self)
            process_command = process['process_command']
            action.setData(process)
            self.__local_pose_lib_menu.addAction(action)

            action.triggered.connect(partial(self.__process_action, process_command, item))

        self.__local_pose_lib_menu.exec_(self.__pose_library_list_weight.mapToGlobal(pos))
        __chracter = self.__get_select_character()
        time.sleep(1)
        self.__referesh_pose_library(__chracter)

    def __right_camera_library_context_menu(self, pos):
        # 获取当前选中的项
        item = self.__camera_library_list_weight.itemAt(pos)
        if not item:
            return
        __right_process = GetXMLData().get_right_process_data_by_tab_name(POSE_RIGHT_XML_NAME, TABS[1])
        if not __right_process:
            return

        # 创建右键菜单
        self.__camera_lib_menu = QMenu(self)

        for process in __right_process:
            action = QAction(process['item_name'], self)
            process_command = process['process_command']
            action.setData(process)
            self.__camera_lib_menu.addAction(action)

            action.triggered.connect(partial(self.__process_action, process_command, item))

        self.__camera_lib_menu.exec_(self.__camera_library_list_weight.mapToGlobal(pos))
        __chracter = self.__get_select_character()
        self.__refersh_camera_library(__chracter)

    def __right_local_camera_library_context_menu(self, pos):
        # 获取当前选中的项
        item = self.__local_camera_library_list_weight.itemAt(pos)
        if not item:
            return
        __right_process = GetXMLData().get_right_process_data_by_tab_name(POSE_RIGHT_XML_NAME, TABS[4])
        if not __right_process:
            return

        # 创建右键菜单
        self.__local_camera_lib_menu = QMenu(self)

        for process in __right_process:
            action = QAction(process['item_name'], self)
            process_command = process['process_command']
            action.setData(process)
            self.__local_camera_lib_menu.addAction(action)

            action.triggered.connect(partial(self.__process_action, process_command, item))

        self.__local_camera_lib_menu.exec_(self.__local_camera_library_list_weight.mapToGlobal(pos))
        __chracter = self.__get_select_character()
        self.__refresh_local_camera_library(__chracter)

    def __right_left_list_context_menu(self, pos):
        # 获取当前选中的项
        item = self.__left_list_weight.itemAt(pos)
        charcter_list = self.__get_select_character()
        tab_index = self.__center_tab_widget.currentIndex()

        if not item:
            return
        __right_process = GetXMLData().get_right_process_data_by_tab_name(POSE_RIGHT_XML_NAME, TABS[5])

        if not __right_process:
            return
        # 创建右键菜单
        self.__left_list_menu = QMenu(self)
        for process in __right_process:
            action = QAction(process['item_name'], self)
            process_command = process['process_command']
            action.setData(process)
            self.__left_list_menu.addAction(action)
            action.triggered.connect(partial(self.__process_left_list_action, process_command, item))
        self.__left_list_menu.exec_(self.__left_list_weight.mapToGlobal(pos))
        self.__add_pose_library_list(charcter_list)

    def __referesh_library(self, charcter_list=None, tab_index=None):

        if not charcter_list:
            charcter_list = self.__get_select_character()
        if tab_index is None:
            tab_index = self.__center_tab_widget.currentIndex()

        if tab_index == 0:

            self.__refresh_pose_library_list(charcter_list)
        elif tab_index == 1:
            self.__refresh_camera_library_list(charcter_list)

        elif tab_index == 2:
            self.__referesh_db_pose_library(charcter_list)

        elif tab_index == 3:
            self.__refresh_local_pose_library_list(charcter_list)
        elif tab_index ==4:
            self.__refresh_local_camera_library_list(charcter_list)

    def __referesh_db_pose_library(self, charcter_list=None):
        __db_pose_library_data = pose_lib_fun.get_db_pose_library_data()
        self.__refresh_items_by_pose_data(__db_pose_library_data, self.__db_pose_library_list_weight, charcter_list)
        self.__db_pose_library_data = __db_pose_library_data



    def __refresh_pose_library_list(self, charcter_list):

        __pose_library_data = pose_lib_fun.get_pose_library_data()
        self.__refresh_items_by_pose_data(__pose_library_data, self.__pose_library_list_weight, charcter_list)
        self.__pose_library_data = __pose_library_data

    def __refresh_camera_library_list(self, charcter_list=None):
        __current_camera_items = self.__get_all_list_items(self.__camera_library_list_weight)
        __camera_library_data = pose_lib_fun.get_camera_library_data()
        self.__refresh_items_by_pose_data(__camera_library_data, self.__camera_library_list_weight, charcter_list)
        self.__camera_library_data = __camera_library_data

    def __refresh_local_pose_library_list(self, charcter_list=None):
        __current_pose_items = self.__get_all_list_items(self.__local_pose_library_list_weight)
        __local_pose_library_data = pose_lib_fun.get_local_pose_library_data()
        self.__refresh_items_by_pose_data(__local_pose_library_data, self.__local_pose_library_list_weight,
                                          charcter_list)
        self.__local_pose_library_data = __local_pose_library_data

    def __refresh_local_camera_library_list(self, charcter_list=None):
        __current_camera_items = self.__get_all_list_items(self.__local_camera_library_list_weight)
        __local_camera_library_data = pose_lib_fun.get_local_camera_library_data()
        self.__refresh_items_by_pose_data(__local_camera_library_data, self.__local_camera_library_list_weight,
                                          charcter_list)
        self.__local_camera_library_data = __local_camera_library_data

    def __refresh_items_by_pose_data(self, pose_data, list_widget, charcter_list=None):

        if not charcter_list:
            charcter_list = self.__get_select_character()

        __current_pose_items = self.__get_all_list_items(list_widget)
        __pose_names = [pose.get('name') for pose in pose_data]
        if not charcter_list:
            self.__remove_items(list_widget.findItems('', Qt.MatchContains))
            return

        if not pose_data and not __current_pose_items:
            return
        __current_pose_items.sort()
        __pose_names.sort()
        if __current_pose_items == __pose_names:
            return
        if not pose_data:
            self.__remove_items(list_widget.findItems('', Qt.MatchContains))

        else:

            for __pose in pose_data:
                __pose_character = __pose.get('character')
                __pose_name = __pose.get('name')
                __thumbnail_path = __pose.get('thumbnail')
                __common = __pose.get('common') if 'common' in __pose else 0
                if __pose_name in __current_pose_items:
                    continue
                if __pose_character not in charcter_list and __common == 0:
                    continue
                __item = QListWidgetItem()
                icon = QIcon(__thumbnail_path)
                __item.setIcon(icon)
                __item.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                __item.setText(__pose_name)
                __item.setData(Qt.UserRole, __pose)
                __item.setBackground(QColor(30, 30, 30))
                __item.setSelected(True)
                list_widget.addItem(__item)
        __current_pose_items = self.__get_all_list_items(list_widget)

        if not __current_pose_items:
            return
        __remove_items = []

        if not __pose_names:
            return
        for item in list_widget.findItems('', Qt.MatchContains):
            item_character = item.data(Qt.UserRole).get('character')
            item_name = item.data(Qt.UserRole).get('name')
            common = item.data(Qt.UserRole).get('common') if 'common' in item.data(Qt.UserRole) else 0

            if item.text() not in __pose_names or (item_character not in charcter_list and common == 0):
                __remove_items.append(item)
                continue
        if __remove_items:
            self.__remove_items(__remove_items)

    def __remove_items(self, item_list):
        if not item_list:
            return

        for item in item_list:
            item.setEnabled(False)

    def __referesh_pose_library(self, charcter_list=None):
        self.__pose_library_list_weight.clear()
        self.__set_pose_library_list_weight(charcter_list, True)

    def __refersh_camera_library(self, charcter_list=None):
        self.__camera_library_list_weight.clear()
        self.__set_camera_library_list_weight(charcter_list, True)

    def __refresh_local_pose_library(self, charcter_list=None):
        self.__local_pose_library_list_weight.clear()
        self.__set_local_pose_library_list_weight(charcter_list, True)

    def __refresh_local_camera_library(self, charcter_list=None):
        self.__local_camera_library_list_weight.clear()
        self.__set_local_camera_library_list_weight(charcter_list, True)

    def __process_action(self, command, item):
        str_commond = command
        _command = str_commond.split(';')[-1]
        __data = item.data(Qt.UserRole)
        fbx_file = __data.get('fbx_path')
        fbx_file = fbx_file.replace('\\', '/')
        character_name = __data.get('character') if 'character' in __data else ''
        thumbnail_path = __data.get('thumbnail') if 'thumbnail' in __data else ''
        description = __data.get('description') if 'description' in __data else ''
        thumbnail_path = thumbnail_path.replace('\\', '/')
        pose_name = item.text()

        _command_new = _command.replace('FbxPath', '"{}"'.format(fbx_file))
        _command_new = _command_new.replace('PoseName', '"{}"'.format(pose_name))
        _command_new = _command_new.replace('CameraName', '"{}"'.format(pose_name))
        _command_new = _command_new.replace('ThumbnailPath', '"{}"'.format(thumbnail_path))
        _command_new = _command_new.replace('Description', '"{}"'.format(description))
        _command_new = _command_new.replace('CharacterName', '"{}"'.format(character_name))

        exec (str_commond[0:len(str_commond) - len(_command)])

        return eval(_command_new)

    def __process_left_list_action(self, command, item):
        __item_name = item.text()
        str_commond = command
        _command = str_commond.split(';')[-1]
        _command_new = _command.replace('CharacterName', '"{}"'.format(__item_name))
        exec (str_commond[0:len(str_commond) - len(_command)])
        eval(_command_new)

    def right_menu_action_clicked_process(self, action):
        action_data = action.data()
        item_name = action_data['item_name']
        indexes = self.tableView.selectionModel().selectedRows()
        for index in indexes:
            process_cmd_item = self.tableview_model.item(index.row(), self.tableview_model.columnCount() - 1)
            process_cmd_item.setText(item_name)
            process_cmd_item.setData(action_data)

    def __set_center_tab(self):
        self.__center_tab_widget = QTabWidget()
        self.__center_tab_widget.setMinimumWidth(370)

        # Add tabs
        self.__center_tab_widget.addTab(QWidget(), TABS[0])
        self.__center_tab_widget.addTab(QWidget(), TABS[1])
        self.__center_tab_widget.addTab(QWidget(), TABS[2])
        self.__center_tab_widget.addTab(QWidget(), TABS[3])
        self.__center_tab_widget.addTab(QWidget(), TABS[4])
        self.__center_layout.addWidget(self.__center_tab_widget)

    def __get_pose_library_list(self):
        return pose_lib_fun.get_pose_library_data()

    def __get_camera_library_list(self):
        return pose_lib_fun.get_camera_library_data()

    def __get_character_data_list(self):
        return pose_lib_fun.get_character_library_data()

    def __set_center_list_weight(self):
        self.__center_weight = QWidget()
        self.__center_pose_layout = QVBoxLayout()

        __tab_index = self.__center_tab_widget.currentIndex()

        self.__pose_library_list_weight = QListWidget()
        self.__pose_library_list_weight.setMinimumWidth(450)

        self.__pose_library_list_weight.setViewMode(QListView.IconMode)
        self.__pose_library_list_weight.setIconSize(QSize(80, 80))
        # self.__pose_library_list_weight.setGridSize(QSize(80, 100))
        self.__pose_library_list_weight.setMovement(QListView.Static)
        self.__pose_library_list_weight.setResizeMode(QListView.Adjust)
        self.__pose_library_list_weight.setSpacing(10)
        self.__pose_library_list_weight.setFlow(QListView.LeftToRight)
        self.__center_pose_layout.addWidget(self.__pose_library_list_weight)
        self.__center_weight.setLayout(self.__center_pose_layout)
        self.__center_tab_widget.widget(__tab_index).setLayout(self.__center_pose_layout)

        self.__camera_library_list_weight = QListWidget()
        self.__camera_library_list_weight.setMinimumWidth(400)
        self.__camera_library_list_weight.setViewMode(QListView.IconMode)
        self.__camera_library_list_weight.setIconSize(QSize(80, 80))
        self.__camera_library_list_weight.setMovement(QListView.Static)
        self.__camera_library_list_weight.setSpacing(10)
        self.__camera_library_list_weight.setFlow(QListView.LeftToRight)
        self.__camera_library_list_weight.setResizeMode(QListView.Adjust)

        self.__center_camera_layout = QVBoxLayout()
        self.__center_camera_layout.addWidget(self.__camera_library_list_weight)
        self.__center_weight.setLayout(self.__center_camera_layout)

        self.__center_tab_widget.widget(__tab_index).setLayout(self.__center_camera_layout)

        self.__db_pose_library_list_weight = QListWidget()
        self.__db_pose_library_list_weight.setMinimumWidth(400)
        self.__db_pose_library_list_weight.setViewMode(QListView.IconMode)
        self.__db_pose_library_list_weight.setIconSize(QSize(80, 80))
        self.__db_pose_library_list_weight.setMovement(QListView.Static)
        self.__db_pose_library_list_weight.setResizeMode(QListView.Adjust)
        self.__db_pose_library_list_weight.setSpacing(10)
        self.__db_pose_library_list_weight.setFlow(QListView.LeftToRight)
        self.__center_db_pose_layout = QVBoxLayout()
        self.__center_db_pose_layout.addWidget(self.__db_pose_library_list_weight)
        self.__center_weight.setLayout(self.__center_db_pose_layout)
        self.__center_tab_widget.widget(__tab_index).setLayout(self.__center_db_pose_layout)

        self.__local_pose_library_list_weight = QListWidget()
        self.__local_pose_library_list_weight.setMinimumWidth(400)
        self.__local_pose_library_list_weight.setViewMode(QListView.IconMode)
        self.__local_pose_library_list_weight.setIconSize(QSize(80, 80))
        self.__local_pose_library_list_weight.setMovement(QListView.Static)
        self.__local_pose_library_list_weight.setResizeMode(QListView.Adjust)
        self.__local_pose_library_list_weight.setSpacing(10)
        self.__local_pose_library_list_weight.setFlow(QListView.LeftToRight)
        self.__center_local_pose_layout = QVBoxLayout()
        self.__center_local_pose_layout.addWidget(self.__local_pose_library_list_weight)
        self.__center_weight.setLayout(self.__center_local_pose_layout)
        self.__center_tab_widget.widget(__tab_index).setLayout(self.__center_local_pose_layout)

        self.__local_camera_library_list_weight = QListWidget()
        self.__local_camera_library_list_weight.setMinimumWidth(400)
        self.__local_camera_library_list_weight.setViewMode(QListView.IconMode)
        self.__local_camera_library_list_weight.setIconSize(QSize(80, 80))
        self.__local_camera_library_list_weight.setMovement(QListView.Static)
        self.__local_camera_library_list_weight.setResizeMode(QListView.Adjust)
        self.__local_camera_library_list_weight.setSpacing(10)
        self.__local_camera_library_list_weight.setFlow(QListView.LeftToRight)
        self.__center_local_camera_layout = QVBoxLayout()
        self.__center_local_camera_layout.addWidget(self.__local_camera_library_list_weight)
        self.__center_weight.setLayout(self.__center_local_camera_layout)
        self.__center_tab_widget.widget(__tab_index).setLayout(self.__center_local_camera_layout)

    def __click_pose_library_list(self, item):
        __current_lib_tab = self.__center_tab_widget.currentIndex()
        __select_character = self.__get_select_character()

        if __current_lib_tab == 0:

            self.__pose_library_list_weight.clear()
            self.__set_pose_library_list_weight([item.text()])
        elif __current_lib_tab == 1:

            self.__camera_library_list_weight.clear()

            self.__set_camera_library_list_weight([item.text()])

        elif __current_lib_tab == 2:
            self.__db_pose_library_list_weight.clear()
            self.__set_db_pose_library_list_weight([item.text()])

        elif __current_lib_tab == 3:

            self.__local_pose_library_list_weight.clear()
            self.__set_local_pose_library_list_weight([item.text()])

        elif __current_lib_tab == 4:
            self.__local_camera_library_list_weight.clear()
            self.__set_local_camera_library_list_weight([item.text()])

    def __click_pose_library_tab(self, index):
        __select_character = self.__get_select_character()
        if index == 0:
            self.__center_tab_widget.widget(index).setLayout(self.__center_pose_layout)
            self.__pose_library_list_weight.clear()
            self.__set_pose_library_list_weight(__select_character)
        elif index == 1:

            self.__center_tab_widget.widget(index).setLayout(self.__center_camera_layout)

            self.__camera_library_list_weight.clear()

            self.__set_camera_library_list_weight(__select_character)

        elif index == 2:
            self.__center_tab_widget.widget(index).setLayout(self.__center_db_pose_layout)

            self.__db_pose_library_list_weight.clear()
            self.__set_db_pose_library_list_weight(__select_character)

        elif index == 3:
            self.__center_tab_widget.widget(index).setLayout(self.__center_local_pose_layout)

            self.__local_pose_library_list_weight.clear()
            self.__set_local_pose_library_list_weight(__select_character)
        elif index == 4:
            self.__center_tab_widget.widget(index).setLayout(self.__center_local_camera_layout)
            self.__local_camera_library_list_weight.clear()
            self.__set_local_camera_library_list_weight(__select_character)

    def __set_camera_library_list_weight(self, character_list=None, refresh=False):
        if refresh:
            __camera_library_list = pose_lib_fun.get_camera_library_data()
            self.__camera_library_data = __camera_library_list
        else:
            __camera_library_list = self.__camera_library_data

        if not character_list:
            __select_character_list = self.__get_select_character()
        else:
            __select_character_list = character_list

        __all_list_items = self.__get_all_list_items(self.__camera_library_list_weight)

        if not __select_character_list:
            return
        for __pose in __camera_library_list:
            character = __pose.get('character')

            pose_name = __pose.get('name')

            fbx_path = __pose.get('fbx_path')

            thumbnail_path = __pose.get('thumbnail')
            common = __pose.get('common') if 'common' in __pose else 0

            if not character or not pose_name or not fbx_path or not thumbnail_path:
                continue

            if character not in __select_character_list and common == 0:
                continue
            if pose_name in __all_list_items:
                continue

            __data = {}

            __item = QListWidgetItem()
            icon = QIcon(thumbnail_path)
            __item.setIcon(icon)
            __item.setText(pose_name)
            __item.setData(Qt.UserRole, __pose)
            __item.setBackground(QColor(30, 30, 30))
            self.__camera_library_list_weight.addItem(__item)

    def __set_db_pose_library_list_weight(self, character_list=None, refresh=False):
        if refresh:
            __pose_library_list = pose_lib_fun.get_db_pose_library_data()
            self.__db_pose_library_data = __pose_library_list
        else:
            __pose_library_list = self.__db_pose_library_data

        if not __pose_library_list:
            return

        if not character_list:
            __select_character_list = self.__get_select_character()
        else:
            __select_character_list = character_list

        if not __select_character_list:
            return
        self.__db_pose_library_data = __pose_library_list
        for __pose in self.__db_pose_library_data:

            character = __pose.get('character') if 'character' in __pose else ''
            pose_name = __pose.get('name') if 'name' in __pose else ''
            fbx_path = __pose.get('fbx_path') if 'fbx_path' in __pose else ''
            thumbnail_path = __pose.get('thumbnail') if 'thumbnail' in __pose else ''
            user = __pose.get('user') if 'user' in __pose else ''
            create_time = __pose.get('create_time') if 'create_time' in __pose else ''
            description = __pose.get('description') if 'description' in __pose else ''

            if not character or not pose_name or not fbx_path or not thumbnail_path:
                continue

            if character not in __select_character_list:
                continue

            __item = QListWidgetItem()
            icon = QIcon(thumbnail_path)
            __item.setIcon(icon)
            __item.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            __item.setText(pose_name)
            __item.setData(Qt.UserRole, __pose)
            __item.setBackground(QColor(30, 30, 30))
            __item.setSelected(True)
            self.__db_pose_library_list_weight.addItem(__item)
        self.__db_pose_library_data = __pose_library_list

    def __set_local_camera_library_list_weight(self, character_list=None, refresh=False):
        if refresh:
            __camera_library_list = pose_lib_fun.get_local_camera_library_data()
            self.__local_camera_library_data = __camera_library_list
        else:
            __camera_library_list = self.__local_camera_library_data
        if not __camera_library_list:
            return
        if not character_list:
            __select_character_list = self.__get_select_character()
        else:
            __select_character_list = character_list
        if not __select_character_list:
            return
        for __pose in __camera_library_list:
            character = __pose.get('character') if 'character' in __pose else ''
            pose_name = __pose.get('name') if 'name' in __pose else ''
            fbx_path = __pose.get('fbx_path') if 'fbx_path' in __pose else ''
            thumbnail_path = __pose.get('thumbnail') if 'thumbnail' in __pose else ''
            user = __pose.get('user') if 'user' in __pose else ''
            create_time = __pose.get('create_time') if 'create_time' in __pose else ''
            description = __pose.get('description') if 'description' in __pose else ''
            common = __pose.get('common') if 'common' in __pose else 0

            if not character or not pose_name or not fbx_path or not thumbnail_path:
                continue

            if character not in __select_character_list and common == 0:
                continue

            __item = QListWidgetItem()
            icon = QIcon(thumbnail_path)
            __item.setIcon(icon)
            # text在图片下方显示
            __item.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            __item.setText(pose_name)
            __item.setData(Qt.UserRole, __pose)
            __item.setBackground(QColor(30, 30, 30))
            self.__local_camera_library_list_weight.addItem(__item)

    def __get_all_list_items(self, list_widget):
        items = []
        for i in range(list_widget.count()):
            item = list_widget.item(i)
            items.append(item.text())
        return items

    def __set_pose_library_list_weight(self, character_list=None, refresh=False):

        if refresh:
            __pose_library_list = pose_lib_fun.get_pose_library_data()
            self.__pose_library_data = __pose_library_list
        else:
            __pose_library_list = self.__pose_library_data

        if not __pose_library_list:
            return

        if not character_list:
            __select_character_list = self.__get_select_character()
        else:
            __select_character_list = character_list

        if not __select_character_list:
            return
        self.__pose_library_data = __pose_library_list
        for __pose in self.__pose_library_data:

            character = __pose.get('character') if 'character' in __pose else ''
            pose_name = __pose.get('name') if 'name' in __pose else ''
            fbx_path = __pose.get('fbx_path') if 'fbx_path' in __pose else ''
            thumbnail_path = __pose.get('thumbnail') if 'thumbnail' in __pose else ''
            user = __pose.get('user') if 'user' in __pose else ''
            create_time = __pose.get('create_time') if 'create_time' in __pose else ''
            description = __pose.get('description') if 'description' in __pose else ''

            character = self.__cover_ud(character)
            pose_name = self.__cover_ud(pose_name)
            fbx_path = self.__cover_ud(fbx_path)
            thumbnail_path = self.__cover_ud(thumbnail_path)
            user = self.__cover_ud(user)
            create_time = self.__cover_ud(create_time)
            description = self.__cover_ud(description)

            if not character or not pose_name or not fbx_path or not thumbnail_path:
                continue

            if character not in __select_character_list:
                continue

            __item = QListWidgetItem()
            icon = QIcon(thumbnail_path)
            __item.setIcon(icon)
            __item.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            __item.setText(pose_name)
            __item.setData(Qt.UserRole, __pose)
            __item.setBackground(QColor(30, 30, 30))
            __item.setSelected(True)
            self.__pose_library_list_weight.addItem(__item)
        self.__pose_library_data = __pose_library_list

    def __cover_ud(self, name):
        try:
            return name.encode("utf8").dcode("GB2312")
        except:
            return name

    def __set_local_pose_library_list_weight(self, character_list=None, refresh=False):
        if refresh:
            __pose_library_list = pose_lib_fun.get_local_pose_library_data()
            self.__local_pose_library_data = __pose_library_list
        else:
            __pose_library_list = self.__local_pose_library_data
        if not __pose_library_list:
            return
        if not character_list:
            __select_character_list = self.__get_select_character()
        else:
            __select_character_list = character_list
        if not __select_character_list:
            return
        for __pose in __pose_library_list:
            character = __pose.get('character') if 'character' in __pose else ''
            pose_name = __pose.get('name') if 'name' in __pose else ''
            fbx_path = __pose.get('fbx_path') if 'fbx_path' in __pose else ''
            thumbnail_path = __pose.get('thumbnail') if 'thumbnail' in __pose else ''
            user = __pose.get('user') if 'user' in __pose else ''
            create_time = __pose.get('create_time') if 'create_time' in __pose else ''
            description = __pose.get('description') if 'description' in __pose else ''

            if not character or not pose_name or not fbx_path or not thumbnail_path:
                continue

            if character not in __select_character_list:
                continue

            __item = QListWidgetItem()
            icon = QIcon(thumbnail_path)
            __item.setIcon(icon)
            __item.setText(pose_name)
            __item.setData(Qt.UserRole, __pose)
            __item.setBackground(QColor(30, 30, 30))
            self.__local_pose_library_list_weight.addItem(__item)

    def __get_select_character(self):
        __select_character = self.__left_list_weight.selectedItems()

        if not __select_character:
            return None
        return [__character.text() for __character in __select_character]

    def __set_left_list_weight(self):
        __character_list = self.__get_character_data_list()
        if not __character_list:
            return

        for __character_name in __character_list:
            item = QListWidgetItem(__character_name)
            self.__left_list_weight.addItem(item)

    def addPose(self):
        pass

    def removePose(self):
        pass


if __name__ == '__main__':
    # handle = PoseLibraryUI()
    # print(handle.character_list())
    import sys

    app = QApplication(sys.argv)
    window = PoseLibraryUI()
    window.show()
    sys.exit(app.exec_())
