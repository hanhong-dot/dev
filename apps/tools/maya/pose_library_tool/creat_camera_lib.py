# -*- coding: utf-8 -*-#
# -------------------------------------------------------
# NAME       : creat_camera_lib
# Describe   : 说明描述
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2025/5/10__上午12:02
# -------------------------------------------------------
try:
    from PySide2.QtWidgets import *
    from PySide2.QtGui import *
    from PySide2.QtCore import *
except:
    from PyQt5.QtWidgets import *
    from PyQt5.QtGui import *
    from PyQt5.QtCore import *

import getpass
import os
from lib.common import fileio

from apps.tools.maya.pose_library_tool import pose_lib_fun
from apps.publish.ui.message.messagebox import msgview


class CreatCameraLibUI(QWidget):
    CamLibSignal = Signal()

    def __init__(self, character=None, model=0, parent=None):
        """
        :param character: 角色名称
        :param model: 0 服务器 1 本地
        """
        super(CreatCameraLibUI, self).__init__(parent)
        if model == 0:
            self.setWindowTitle(u"添加相机库资产(服务器)")
        else:
            self.setWindowTitle(u"添加相机库资产(本地)")
        self.setMinimumWidth(400)
        self.setMinimumHeight(300)
        self.setMaximumHeight(600)
        self.setMaximumWidth(800)

        self.__character = character

        self.__model = model

        self.__user_name = getpass.getuser()

        self.__init_ui()
        self.__connect_signal()

    def __get_current_time(self):
        return QDateTime.currentDateTime().toString("yyyy-MM-dd-hh-mm-ss")

    def __init_ui(self):

        self.__character_name = QLineEdit()
        self.__character_name.setPlaceholderText(self.__character)
        self.__character_name.setMinimumHeight(30)

        self.__camera_lib_name = QLineEdit()
        self.__camera_lib_name.setPlaceholderText(u"请输入camera资产名称")
        self.__camera_lib_name.setMinimumHeight(30)

        self.__camera_fbx_layout = QHBoxLayout()
        self.__camera_fbx_path = QLineEdit()
        self.__camera_fbx_path.setPlaceholderText(u"请输入或选择相机fbx文件")

        self.__camera_fbx_path.setMinimumHeight(30)
        self.__camera_fbx_layout.addWidget(self.__camera_fbx_path)
        self.__camera_fbx_btn = QPushButton(u"浏览")
        self.__camera_fbx_btn.setMinimumHeight(30)

        self.__camera_fbx_layout.addWidget(self.__camera_fbx_btn)

        self.__camera_lib_description = QPlainTextEdit()
        self.__camera_lib_description.setPlaceholderText(u"请输入描述信息")
        self.__camera_lib_description.setMinimumHeight(60)

        self.__camera_thumbnail_layout = QHBoxLayout()
        self.__camera_lib_thumbnail = QLineEdit()
        self.__camera_lib_thumbnail.setPlaceholderText(u"请输入或选择缩略图路径(支持png,jpg格式)")
        self.__camera_lib_thumbnail.setMinimumHeight(30)
        self.__camera_thumbnail_layout.addWidget(self.__camera_lib_thumbnail)
        self.__camera_thumbnail_btn = QPushButton(u"浏览")
        self.__camera_thumbnail_btn.setMinimumHeight(30)
        self.__camera_thumbnail_layout.addWidget(self.__camera_thumbnail_btn)

        self.__common_checkbox = QCheckBox(u"通用相机资产")
        self.__common_checkbox.setMinimumHeight(30)
        self.__common_checkbox.setChecked(False)
        self.__common_checkbox.setStyleSheet("QCheckBox::indicator { width: 20px; height: 20px; }")

        self.__btn_create = QPushButton("Create camera Library")
        self.__btn_create.setBackgroundRole(QPalette.Button)

        self.__btn_create.setStyleSheet("background-color: rgb(30, 90, 87); color: white;")
        self.__btn_create.setMinimumHeight(30)

        ml = QVBoxLayout(self)

        ml.addWidget(QLabel(u"角色名称:"))
        ml.addWidget(self.__character_name)
        ml.addWidget(QLabel(u"camera资产名称:"))
        ml.addWidget(self.__camera_lib_name)
        ml.addWidget(QLabel(u"camera Fbx文件路径:"))

        ml.addLayout(self.__camera_fbx_layout)

        ml.addWidget(QLabel(u"缩略图路径:"))
        ml.addLayout(self.__camera_thumbnail_layout)

        ml.addWidget(QLabel(u"描述信息:"))
        ml.addWidget(self.__camera_lib_description)
        ml.addWidget(self.__common_checkbox)
        ml.addWidget(self.__btn_create)

    def ___camera_fbx_btn_clicked(self):
        # 选择fbx文件
        __fbx_file_path = self.__read_camera_fbx_path()
        self.__camera_fbx_file_path = QFileDialog.getOpenFileName(self, u"选择fbx文件", __fbx_file_path,
                                                                  u"FBX Files (*.fbx);;All Files (*)")
        if self.__camera_fbx_file_path:
            self.__camera_fbx_path.setText(self.__camera_fbx_file_path[0])
            self.__camera_fbx_file_path = self.__camera_fbx_file_path[0]
            if not self.__camera_fbx_file_path:
                msgview(u'请选择fbx文件', 2)
                return

    def __camera_thumbnail_btn_clicked(self):
        # 选择缩略图文件
        __camera_thumbnail_path_txt_path = self.__get_camera_thumbnail_txt_path()
        __thumbnail_file_path = self.__read_path(__camera_thumbnail_path_txt_path)

        self.__camera_thumbnail_file_path = QFileDialog.getOpenFileName(self, u"选择缩略图文件", __thumbnail_file_path,
                                                                        u"Image Files (*.png *.jpg);;All Files (*)")
        if self.__camera_thumbnail_file_path:
            self.__camera_lib_thumbnail.setText(self.__camera_thumbnail_file_path[0])
            self.__camera_thumbnail_file_path = self.__camera_thumbnail_file_path[0]
            if not self.__camera_thumbnail_file_path:
                msgview(u'请选择缩略图文件', 2)
                return

    def __get_camera_fbx_txt_path(self):
        __local_dir = self.__get_local_path('camera_fbx')
        if not os.path.exists(__local_dir):
            os.makedirs(__local_dir)
        return u'{}/fbx_path.txt'.format(__local_dir)

    def __get_camera_thumbnail_txt_path(self):
        __local_dir = self.__get_local_path('camera_thumbnail')
        if not os.path.exists(__local_dir):
            os.makedirs(__local_dir)
        return u'{}/thumbnail_path.txt'.format(__local_dir)

    def __cover_ud(self, info):
        if isinstance(info, str):
            info = info.decode('utf-8')
        return info.replace('\\', '/')

    def __read_path(self, path):
        if not os.path.exists(path):
            return None
        path = fileio.read(path, rtype='r')
        if not path:
            return None
        return path

    def __write_path(self, info, path, wtype='w'):
        if not path:
            msgview(u'请先选择文件', 2)
            return
        return fileio.write(info, path, wtype=wtype)

    def __write_camera_fbx_path(self, fbx_path):
        if not fbx_path:
            msgview(u'请先选择fbx文件', 2)
            return
        __camera_fbx_txt_path = self.__get_camera_fbx_txt_path()
        self.__write_path(fbx_path, __camera_fbx_txt_path, wtype='w')

    def __read_camera_fbx_path(self):
        __camera_fbx_txt_path = self.__get_camera_fbx_txt_path()
        if not os.path.exists(__camera_fbx_txt_path):
            return None
        __camera_fbx_path = fileio.read(__camera_fbx_txt_path, rtype='r')
        if not __camera_fbx_path:
            return None
        return __camera_fbx_path

    def __get_local_path(self, add_path=None):
        if add_path:
            __local_path = u'{}/camera_library/{}'.format(os.getenv('APPDATA'), add_path)
        else:
            __local_path = u'{}/camera_library'.format(os.getenv('APPDATA'))

        __local_path = __local_path.replace('\\', '/')
        if not os.path.exists(__local_path):
            os.makedirs(__local_path)

        return __local_path

    def __copy_file(self, src, dst):
        import shutil
        __dir = os.path.dirname(dst)
        if not os.path.exists(__dir):
            try:
                os.makedirs(__dir)
            except:
                msgview(u'创建目录失败', 2)
                return False
        try:
            shutil.copy(src, dst)
            return True
        except Exception as e:
            return False

    def __updatate_camera_lib_by_lib_data(self, camera_lib_data):
        if not camera_lib_data:
            return
        __camera_lib_name = camera_lib_data.get('name') if camera_lib_data.get(
            'name') else self.__camera_lib_name.text()
        __camera_lib_description = camera_lib_data.get('description') if camera_lib_data.get(
            'description') else self.__camera_lib_description.toPlainText()
        __camera_lib_thumbnail = camera_lib_data.get('thumbnail') if camera_lib_data.get(
            'thumbnail') else self.__camera_lib_thumbnail.text()
        __camera_lib_character = camera_lib_data.get('character') if camera_lib_data.get(
            'character') else self.__character
        __camera_lib_create_time = camera_lib_data.get('create_time') if camera_lib_data.get(
            'create_time') else self.__get_current_time()
        __camera_lib_user_name = camera_lib_data.get('user') if camera_lib_data.get(
            'user') else self.__user_name

        __camera_fbx_path = camera_lib_data.get('fbx_path') if camera_lib_data.get(
            'fbx_path') else self.__camera_fbx_path.text()
        __camera_lib_common = camera_lib_data.get('common') if camera_lib_data.get(
            'common') else self.__common_checkbox.isChecked()

        if not __camera_lib_name:
            return False, u'camera库名称不能为空,请输入camera库名称'

        if not __camera_fbx_path:
            return False, u'camera库fbx文件路径不能为空,请输入camera库fbx文件路径'

        if not __camera_lib_thumbnail:
            return False, u'camera库缩略图文件路径不能为空,请输入camera库缩略图文件路径'
        if not __camera_lib_character:
            return False, u'camera库角色名称不能为空,请输入camera库角色名称'
        if not os.path.exists(__camera_fbx_path):
            return False, u'camera库fbx文件路径不存在,请检查路径是否正确'
        else:
            __camera_fbx_path = self.__camera_fbx_path.text()
            self.__write_camera_fbx_path(u'{}'.format(__camera_fbx_path))
        if not os.path.exists(__camera_lib_thumbnail):
            return False, u'camera库缩略图文件路径不存在,请检查路径是否正确'
        else:
            __camera_lib_thumbnail = self.__camera_lib_thumbnail.text()
            __camera_lib_thumbnail = __camera_lib_thumbnail.replace('\\', '/')
            __camera_lib_thumbnail = u'{}'.format(__camera_lib_thumbnail)
            self.__write_path(__camera_lib_thumbnail, self.__get_camera_thumbnail_txt_path(), wtype='w')
        return True, u'camera库信息更新成功'

    def __connect_signal(self):
        self.__camera_fbx_btn.clicked.connect(self.___camera_fbx_btn_clicked)
        self.__btn_create.clicked.connect(self.__btn_create_clicked)
        self.__camera_thumbnail_btn.clicked.connect(self.__camera_thumbnail_btn_clicked)

    def __btn_create_clicked(self):
        __camera_data = self.__get_camera_data()

        if not __camera_data:
            msgview(u'camera库信息不能为空,请填写camera库信息', 2)
            return
        __camera_data = self.__process_camera_data(__camera_data)
        if not __camera_data:
            msgview(u'camera库信息处理失败,请检查camera库信息', 2)
            return

        ok, result = self.__updatate_camera_lib_by_lib_data(__camera_data)
        if not ok:
            msgview(result, 2)
            return
        if self.__model == 0:
            __camera_lib_data = pose_lib_fun.read_camera_library_json()
            if not __camera_lib_data:
                pose_lib_fun.write_camera_library_json([__camera_data])
            else:
                __camera_lib_data.append(__camera_data)
                pose_lib_fun.write_camera_library_json(__camera_lib_data)
        else:
            __camera_lib_data = pose_lib_fun.get_local_camera_library_data()
            if not __camera_lib_data:
                pose_lib_fun.save_local_camera_library([__camera_data])
            else:
                __camera_lib_data.append(__camera_data)
                pose_lib_fun.save_local_camera_library(__camera_lib_data)

        msgview(u'camera库添加成功', 2)

    def __process_camera_data(self, camera_data):
        __camera_lib_name = camera_data.get('name')
        __camera_lib_description = camera_data.get('description')
        __camera_lib_thumbnail = camera_data.get('thumbnail')
        __camera_lib_character = camera_data.get('character')
        __camera_lib_create_time = camera_data.get('create_time')
        __camera_lib_user_name = camera_data.get('user')
        __camera_fbx_path = camera_data.get('fbx_path')
        __common = camera_data.get('__common')

        if self.__model == 0:
            __camera_library_path = pose_lib_fun.get_camera_library_path()
        else:
            __camera_library_path = pose_lib_fun.get_local_camera_library_path()
        __server_camera_fbx_path = '{}/{}/{}/fbx/{}.fbx'.format(__camera_library_path, __camera_lib_character,
                                                                __camera_lib_name, __camera_lib_name)

        __server_camera_thumbnail_path = '{}/{}/{}/thumbnail/{}.png'.format(__camera_library_path,
                                                                            __camera_lib_character,
                                                                            __camera_lib_name, __camera_lib_name)

        __camera_fbx_path = self.__cover_ud(__camera_fbx_path)
        __camera_lib_thumbnail = self.__cover_ud(__camera_lib_thumbnail)
        __server_camera_fbx_path = self.__cover_ud(__server_camera_fbx_path)
        __server_camera_thumbnail_path = self.__cover_ud(__server_camera_thumbnail_path)

        __result = self.__copy_file(__camera_fbx_path, __server_camera_fbx_path)
        if not __result:
            msgview(u'camera库fbx文件复制失败,请检查路径是否正确', 2)
            return
        __result = self.__copy_file(__camera_lib_thumbnail, __server_camera_thumbnail_path)
        if not __result:
            msgview(u'camera库缩略图文件复制失败,请检查路径是否正确', 2)
            return
        camera_data['fbx_path'] = __server_camera_fbx_path
        camera_data['thumbnail'] = __server_camera_thumbnail_path
        return camera_data

    def __get_camera_data(self):
        __camera_data = {}
        __camera_lib_name = self.__camera_lib_name.text()
        __camera_lib_description = self.__camera_lib_description.toPlainText()
        __camera_lib_thumbnail = self.__camera_lib_thumbnail.text()
        __camera_lib_character = self.__character
        __common_check = self.__common_checkbox.isChecked()
        if __common_check:
            __common = 1
        else:
            __common = 0

        __camera_lib_create_time = self.__get_current_time()
        __camera_lib_user_name = self.__user_name
        __camera_fbx_path = self.__camera_fbx_path.text()
        __camera_data['name'] = self.__cover_ud(__camera_lib_name)
        __camera_data['fbx_path'] = self.__cover_ud(__camera_fbx_path)
        __camera_data['description'] = self.__cover_ud(__camera_lib_description)
        __camera_data['thumbnail'] = self.__cover_ud(__camera_lib_thumbnail)
        __camera_data['character'] = self.__cover_ud(__camera_lib_character)
        __camera_data['create_time'] = self.__cover_ud(__camera_lib_create_time)
        __camera_data['user'] = self.__cover_ud(__camera_lib_user_name)
        __camera_data['common'] = __common

        return __camera_data


if __name__ == '__main__':
    import sys

    character = 'PL'

    app = QApplication(sys.argv)
    window = CreatCameraLibUI(character)
    window.show()
    sys.exit(app.exec_())
