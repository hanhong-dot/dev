# -*- coding: utf-8 -*-#
# -------------------------------------------------------
# NAME       : creat_pose_lib
# Describe   : 说明描述
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2025/5/7__下午5:25
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


class CreatPoseLibraryUI(QWidget):

    def __init__(self, character=None, model=0, parent=None):
        """
        :param character: 角色名称
        :param model: 0:服务器 1:本地
        """
        super(CreatPoseLibraryUI, self).__init__(parent)
        if model == 0:
            self.setWindowTitle("添加Pose库资产(服务器)")
        else:
            self.setWindowTitle("添加Pose库资产(本地)")
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

        self.__pose_lib_name = QLineEdit()
        self.__pose_lib_name.setPlaceholderText(u"请输入Pose资产名称")
        self.__pose_lib_name.setMinimumHeight(30)

        self.__pose_fbx_layout = QHBoxLayout()
        self.__pose_fbx_path = QLineEdit()
        self.__pose_fbx_path.setPlaceholderText(u"请输入或选择library fbx文件")

        self.__pose_fbx_path.setMinimumHeight(30)
        self.__pose_fbx_layout.addWidget(self.__pose_fbx_path)
        self.__pose_fbx_btn = QPushButton(u"浏览")
        self.__pose_fbx_btn.setMinimumHeight(30)

        self.__pose_fbx_layout.addWidget(self.__pose_fbx_btn)

        self.__pose_lib_description = QPlainTextEdit()
        self.__pose_lib_description.setPlaceholderText(u"请输入描述信息")
        self.__pose_lib_description.setMinimumHeight(60)

        self.__pose_thumbnail_layout = QHBoxLayout()
        self.__pose_lib_thumbnail = QLineEdit()
        self.__pose_lib_thumbnail.setPlaceholderText(u"请输入或选择缩略图路径(支持png,jpg格式)")
        self.__pose_lib_thumbnail.setMinimumHeight(30)
        self.__pose_thumbnail_layout.addWidget(self.__pose_lib_thumbnail)
        self.__pose_thumbnail_btn = QPushButton(u"浏览")
        self.__pose_thumbnail_btn.setMinimumHeight(30)
        self.__pose_thumbnail_layout.addWidget(self.__pose_thumbnail_btn)

        # self.__pose_lib_thumbnail.setAcceptDrops(True)
        # self.__pose_lib_thumbnail.setDragEnabled(True)

        # def dragEnterEvent(event):
        #     if event.mimeData().hasUrls():
        #         event.accept()
        #     else:
        #         event.ignore()
        #
        # def dropEvent(event):
        #     if event.mimeData().hasUrls():
        #         urls = event.mimeData().urls()
        #         if urls:
        #             file_path = urls[0].toLocalFile()
        #             self.__pose_lib_thumbnail.setText(file_path)
        #             event.accept()
        #         else:
        #             event.ignore()
        #     else:
        #         event.ignore()

        # self.__pose_lib_thumbnail.dragEnterEvent = dragEnterEvent
        # self.__pose_lib_thumbnail.dropEvent = dropEvent
        # 设置self.__pose_lib_thumbnail尺寸

        self.__btn_create = QPushButton("Create Pose Library")
        self.__btn_create.setBackgroundRole(QPalette.Button)
        # self.__btn_create设置为灰绿色
        self.__btn_create.setStyleSheet("background-color: rgb(30, 90, 87); color: white;")
        self.__btn_create.setMinimumHeight(30)

        ml = QVBoxLayout(self)

        ml.addWidget(QLabel(u"角色名称:"))
        ml.addWidget(self.__character_name)
        ml.addWidget(QLabel(u"Pose资产名称:"))
        ml.addWidget(self.__pose_lib_name)
        ml.addWidget(QLabel(u"Pose Fbx文件路径:"))

        ml.addLayout(self.__pose_fbx_layout)

        ml.addWidget(QLabel(u"缩略图路径:"))
        ml.addLayout(self.__pose_thumbnail_layout)

        ml.addWidget(QLabel(u"描述信息:"))
        ml.addWidget(self.__pose_lib_description)
        ml.addWidget(self.__btn_create)

    def ___pose_fbx_btn_clicked(self):
        # 选择fbx文件
        __fbx_file_path = self.__read_pose_fbx_path()
        self.__pose_fbx_file_path = QFileDialog.getOpenFileName(self, u"选择fbx文件", __fbx_file_path,
                                                                u"FBX Files (*.fbx);;All Files (*)")
        if self.__pose_fbx_file_path:
            self.__pose_fbx_path.setText(self.__pose_fbx_file_path[0])
            self.__pose_fbx_file_path = self.__pose_fbx_file_path[0]
            if not self.__pose_fbx_file_path:
                msgview(u'请选择fbx文件', 2)
                return

    def __cover_ud(self, info):
        if isinstance(info, str):
            info = info.decode('utf-8')
        return info.replace('\\', '/')

    def __pose_thumbnail_btn_clicked(self):
        # 选择缩略图文件
        __pose_thumbnail_path_txt_path = self.__get_pose_thumbnail_txt_path()
        __thumbnail_file_path = self.__read_path(__pose_thumbnail_path_txt_path)

        self.__pose_thumbnail_file_path = QFileDialog.getOpenFileName(self, u"选择缩略图文件", __thumbnail_file_path,
                                                                      u"Image Files (*.png *.jpg);;All Files (*)")
        if self.__pose_thumbnail_file_path:
            self.__pose_lib_thumbnail.setText(self.__pose_thumbnail_file_path[0])
            self.__pose_thumbnail_file_path = self.__pose_thumbnail_file_path[0]
            if not self.__pose_thumbnail_file_path:
                msgview(u'请选择缩略图文件', 2)
                return

    def __get_pose_fbx_txt_path(self):
        __local_dir = self.__get_local_path('pose_fbx')
        if not os.path.exists(__local_dir):
            os.makedirs(__local_dir)
        return u'{}/fbx_path.txt'.format(__local_dir)

    def __get_pose_thumbnail_txt_path(self):
        __local_dir = self.__get_local_path('pose_thumbnail')
        if not os.path.exists(__local_dir):
            os.makedirs(__local_dir)
        return u'{}/thumbnail_path.txt'.format(__local_dir)

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

    def __write_pose_fbx_path(self, fbx_path):
        if not fbx_path:
            msgview(u'请先选择fbx文件', 2)
            return
        __pose_fbx_txt_path = self.__get_pose_fbx_txt_path()
        self.__write_path(fbx_path, __pose_fbx_txt_path, wtype='w')

    def __read_pose_fbx_path(self):
        __pose_fbx_txt_path = self.__get_pose_fbx_txt_path()
        if not os.path.exists(__pose_fbx_txt_path):
            return None
        __pose_fbx_path = fileio.read(__pose_fbx_txt_path, rtype='r')
        if not __pose_fbx_path:
            return None
        return __pose_fbx_path

    def __get_local_path(self, add_path=None):
        if add_path:
            __local_path = u'{}/pose_library/{}'.format(os.getenv('APPDATA'), add_path)
        else:
            __local_path = u'{}/pose_library'.format(os.getenv('APPDATA'))

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

    def __updatate_pose_lib_by_lib_data(self, pose_lib_data):
        if not pose_lib_data:
            return
        __pose_lib_name = pose_lib_data.get('name') if pose_lib_data.get(
            'name') else self.__pose_lib_name.text()
        __pose_lib_description = pose_lib_data.get('description') if pose_lib_data.get(
            'description') else self.__pose_lib_description.toPlainText()
        __pose_lib_thumbnail = pose_lib_data.get('thumbnail') if pose_lib_data.get(
            'thumbnail') else self.__pose_lib_thumbnail.text()
        __pose_lib_character = pose_lib_data.get('character') if pose_lib_data.get(
            'character') else self.__character
        __pose_lib_create_time = pose_lib_data.get('create_time') if pose_lib_data.get(
            'create_time') else self.__get_current_time()
        __pose_lib_user_name = pose_lib_data.get('user') if pose_lib_data.get(
            'user') else self.__user_name

        __pose_fbx_path = pose_lib_data.get('fbx_path') if pose_lib_data.get(
            'fbx_path') else self.__pose_fbx_path.text()
        if not __pose_lib_name:
            return False, u'Pose库名称不能为空,请输入Pose库名称'

        if not __pose_fbx_path:
            return False, u'Pose库fbx文件路径不能为空,请输入Pose库fbx文件路径'

        if not __pose_lib_thumbnail:
            return False, u'Pose库缩略图路径不能为空,请输入Pose库缩略图路径'
        if not __pose_lib_character:
            return False, u'Pose库角色名称不能为空,请输入Pose库角色名称'

        if not os.path.exists(__pose_fbx_path):
            return False, u'Pose库fbx文件路径不存在,请检查路径是否正确'
        else:
            __pose_fbx_path = self.__pose_fbx_path.text()
            self.__write_pose_fbx_path(u'{}'.format(__pose_fbx_path))
        if not os.path.exists(__pose_lib_thumbnail):
            return False, u'Pose库缩略图路径不存在,请检查路径是否正确'
        else:
            __pose_lib_thumbnail = self.__pose_lib_thumbnail.text()
            __pose_lib_thumbnail = __pose_lib_thumbnail.replace('\\', '/')
            __pose_lib_thumbnail = u'{}'.format(__pose_lib_thumbnail)
            self.__write_path(__pose_lib_thumbnail, self.__get_pose_thumbnail_txt_path(), wtype='w')
        return True, u'Pose库信息更新成功'

    def __connect_signal(self):
        self.__pose_fbx_btn.clicked.connect(self.___pose_fbx_btn_clicked)
        self.__btn_create.clicked.connect(self.__btn_create_clicked)
        self.__pose_thumbnail_btn.clicked.connect(self.__pose_thumbnail_btn_clicked)

    def __btn_create_clicked(self):
        __pose_data = self.__get_pose_data()

        if not __pose_data:
            msgview(u'Pose库信息不能为空,请填写Pose库信息', 2)
            return
        __pose_data = self.__process_pose_data(__pose_data)
        if not __pose_data:
            msgview(u'Pose库信息处理失败,请检查Pose库信息', 2)
            return

        ok, result = self.__updatate_pose_lib_by_lib_data(__pose_data)
        if not ok:
            msgview(result, 1)
            return

        if self.__model == 0:

            __pose_lib_data = pose_lib_fun.read_pose_library_json()
            if not __pose_lib_data:
                pose_lib_fun.write_pose_library_json([__pose_data])
            else:
                __pose_lib_data.append(__pose_data)
                pose_lib_fun.write_pose_library_json(__pose_lib_data)

        else:
            __pose_lib_data = pose_lib_fun.get_local_pose_library_data()
            if not __pose_lib_data:
                pose_lib_fun.save_local_pose_library([__pose_data])
            else:
                __pose_lib_data.append(__pose_data)
                pose_lib_fun.save_local_pose_library(__pose_lib_data)
        msgview(u'Pose库添加成功', 2)

    def __process_pose_data(self, pose_data):
        __pose_lib_name = pose_data.get('name')
        __pose_lib_description = pose_data.get('description')
        __pose_lib_thumbnail = pose_data.get('thumbnail')
        __pose_lib_character = pose_data.get('character')
        __pose_lib_create_time = pose_data.get('create_time')
        __pose_lib_user_name = pose_data.get('user')
        __pose_fbx_path = pose_data.get('fbx_path')

        if self.__model == 0:

            __pose_library_path = pose_lib_fun.get_pose_library_path()

        else:
            __pose_library_path = pose_lib_fun.get_local_pose_library_path()
        __server_pose_fbx_path = '{}/{}/{}/fbx/{}.fbx'.format(__pose_library_path, __pose_lib_character,
                                                              __pose_lib_name, __pose_lib_name)

        __server_pose_thumbnail_path = '{}/{}/{}/thumbnail/{}.png'.format(__pose_library_path, __pose_lib_character,
                                                                          __pose_lib_name, __pose_lib_name)
        __pose_fbx_path = self.__cover_ud(__pose_fbx_path)
        __pose_lib_thumbnail = self.__cover_ud(__pose_lib_thumbnail)
        __server_pose_fbx_path = self.__cover_ud(__server_pose_fbx_path)
        __server_pose_thumbnail_path = self.__cover_ud(__server_pose_thumbnail_path)

        __result = self.__copy_file(__pose_fbx_path, __server_pose_fbx_path)
        if not __result:
            msgview(u'Pose库fbx文件复制失败,请检查路径是否正确', 2)
            return
        __result = self.__copy_file(__pose_lib_thumbnail, __server_pose_thumbnail_path)
        if not __result:
            msgview(u'Pose库缩略图文件复制失败,请检查路径是否正确', 2)
            return
        pose_data['fbx_path'] = __server_pose_fbx_path
        pose_data['thumbnail'] = __server_pose_thumbnail_path
        return pose_data

    def __get_pose_data(self):
        __pose_data = {}
        __pose_lib_name = self.__pose_lib_name.text()
        __pose_lib_description = self.__pose_lib_description.toPlainText()
        __pose_lib_thumbnail = self.__pose_lib_thumbnail.text()
        __pose_lib_character = self.__character

        __pose_lib_create_time = self.__get_current_time()
        __pose_lib_user_name = self.__user_name
        __pose_fbx_path = self.__pose_fbx_path.text()

        __pose_data['name'] = self.__cover_ud(__pose_lib_name)
        __pose_data['fbx_path'] = self.__cover_ud(__pose_fbx_path)
        __pose_data['description'] = self.__cover_ud(__pose_lib_description)
        __pose_data['thumbnail'] = self.__cover_ud(__pose_lib_thumbnail)
        __pose_data['character'] = self.__cover_ud(__pose_lib_character)
        __pose_data['create_time'] = self.__cover_ud(__pose_lib_create_time)
        __pose_data['user'] = self.__cover_ud(__pose_lib_user_name)
        return __pose_data


if __name__ == '__main__':
    import sys

    character = 'PL'

    app = QApplication(sys.argv)
    window = CreatPoseLibraryUI(character)
    window.show()
    sys.exit(app.exec_())
