# -*- coding: utf-8 -*-#
# -------------------------------------------------------
# NAME       : replace_camera
# Describe   : 说明描述
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2025/5/20__下午3:22
# -------------------------------------------------------
try:
    from PySide2.QtWidgets import *
    from PySide2.QtGui import *
    from PySide2.QtCore import *
except:
    from PyQt5.QtWidgets import *
    from PyQt5.QtGui import *
    from PyQt5.QtCore import *
from apps.publish.ui.message.messagebox import msgview
import os
from apps.tools.maya.pose_library_tool import pose_lib_fun

from lib.common.log import Logger


class ReplaceCameraUI(QDialog):
    def __init__(self, camera_name=None, character=None, fbx_path=None, thumbnail=None, description=None, model=0,
                 parent=None):
        """
        :param camera_name: Camera名称
        :param character: 角色名称
        :param fbx_path: Camera fbx文件路径
        :param thumbnail: Camera缩略图路径
        :param description: 描述信息
        :param mode: 0: 0 服务器 1 本地
        """
        super(ReplaceCameraUI, self).__init__(parent)
        self.setWindowTitle(u'编辑更新当前Camera数据')
        self.setGeometry(600, 200, 600, 200)
        self.__camera_name = camera_name
        self.__character = character
        self.__fbx_path = fbx_path
        self.__thumbnail = thumbnail
        self.__description = description
        self.__model = model
        if self.__model == 0:
            __log_dir = pose_lib_fun.get_lib_log_path()
        else:
            __log_dir = pose_lib_fun.get_local_lib_log_path()

        __log_path = os.path.join(__log_dir, "updata_camera_lib_{}.log".format(self.__get_current_time()))
        self.__logger = Logger(__log_path)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.WindowCloseButtonHint)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.__initUI()
        self.__connect_signals()

    def __initUI(self):
        self.__character_name = QLineEdit()
        self.__character_name.setPlaceholderText(self.__character)
        self.__character_name.setText(self.__character)
        # 不可编辑
        self.__character_name.setReadOnly(True)
        self.__character_name.setMinimumHeight(30)
        self.__camera_lib_name = QLineEdit(self.__camera_name)
        self.__camera_lib_name.setMinimumHeight(30)
        self.__camera_lib_layout = QHBoxLayout()
        self.__camera_fbx_path = QLineEdit(self.__fbx_path)
        self.__camera_fbx_path.setMinimumHeight(30)
        self.__camera_lib_layout.addWidget(self.__camera_fbx_path)
        self.__camera_fbx_btn = QPushButton(u"浏览")
        self.__camera_fbx_btn.setMinimumHeight(30)
        self.__camera_lib_layout.addWidget(self.__camera_fbx_btn)
        self.__camera_lib_description = QPlainTextEdit(self.__description)
        self.__camera_lib_description.setMinimumHeight(60)
        self.__camera_thumbnail_layout = QHBoxLayout()
        self.__camera_lib_thumbnail = QLineEdit()
        self.__camera_lib_thumbnail.setText(self.__thumbnail)
        self.__camera_lib_thumbnail.setMinimumHeight(30)
        self.__camera_thumbnail_layout.addWidget(self.__camera_lib_thumbnail)
        self.__camera_thumbnail_btn = QPushButton(u"浏览")
        self.__camera_thumbnail_btn.setMinimumHeight(30)
        self.__camera_thumbnail_layout.addWidget(self.__camera_thumbnail_btn)
        self.__camera_replace_btn = QPushButton(u"替换Camera库数据")
        self.__camera_replace_btn.setBackgroundRole(QPalette.Button)
        self.__camera_replace_btn.setStyleSheet("background-color: rgb(30, 90, 87);color: rgb(255, 255, 255);")
        self.__camera_replace_btn.setMinimumHeight(30)
        self.__common_checkbox = QCheckBox(u"通用相机资产")
        self.__common_checkbox.setMinimumHeight(30)
        self.__common_checkbox.setChecked(False)
        self.__common_checkbox.setStyleSheet("QCheckBox::indicator { width: 20px; height: 20px; }")
        ml = QVBoxLayout(self)
        ml.addWidget(QLabel(u"角色名称:"))
        ml.addWidget(self.__character_name)
        ml.addWidget(QLabel(u"相机资产名称:"))
        ml.addWidget(self.__camera_lib_name)
        ml.addWidget(QLabel(u"Camera Fbx文件路径:"))
        ml.addLayout(self.__camera_lib_layout)
        ml.addWidget(QLabel(u"缩略图路径:"))
        ml.addLayout(self.__camera_thumbnail_layout)
        ml.addWidget(QLabel(u"描述信息:"))
        ml.addWidget(self.__camera_lib_description)
        ml.addWidget(self.__common_checkbox)
        ml.addWidget(self.__camera_replace_btn)

    def __connect_signals(self):
        self.__camera_fbx_btn.clicked.connect(self.__camera_fbx_btn_clicked)
        self.__camera_thumbnail_btn.clicked.connect(self.__camera_thumbnail_btn_clicked)
        self.__camera_replace_btn.clicked.connect(self.__camera_replace_btn_clicked)

    def __camera_fbx_btn_clicked(self):
        __camera_fbx_file_path = self.__camera_fbx_path.text()
        self.__camera_fbx_file_path = QFileDialog.getOpenFileName(self, u"选择fbx文件", __camera_fbx_file_path,
                                                                  u"FBX Files (*.fbx);;All Files (*)")
        if self.__camera_fbx_file_path:
            self.__camera_fbx_path.setText(self.__camera_fbx_file_path[0])
            self.__camera_fbx_file_path = self.__camera_fbx_file_path[0]
            if not self.__camera_fbx_file_path:
                msgview(u'请选择fbx文件', 1)
                return

    def __camera_thumbnail_btn_clicked(self):

        __camera_thumbnail_path_txt_path = self.__camera_lib_thumbnail.text()

        self.__camera_thumbnail_file_path = QFileDialog.getOpenFileName(self, u"选择缩略图文件",
                                                                        __camera_thumbnail_path_txt_path,
                                                                        u"Image Files (*.png *.jpg);;All Files (*)")
        if self.__camera_thumbnail_file_path:
            self.__camera_lib_thumbnail.setText(self.__camera_thumbnail_file_path[0])
            self.__camera_thumbnail_file_path = self.__camera_thumbnail_file_path[0]
            # if not self.__camera_thumbnail_file_path:
            #     msgview(u'请选择缩略图文件', 2)
            #     return

    def __camera_replace_btn_clicked(self):
        self.__update_user = self.__get_user()

        camera_name = self.__camera_lib_name.text()
        character = self.__character_name.text()
        fbx_path = self.__camera_fbx_path.text()
        thumbnail = self.__camera_lib_thumbnail.text()
        description = self.__camera_lib_description.toPlainText()
        common_check = self.__common_checkbox.isChecked()
        if common_check:
            common=1
        else:
            common=0

        if not camera_name:
            msgview(u'camera名称不能为空，请检查', 1)
            return
        if not fbx_path:
            msgview(u'camera fbx文件不能为空，请检查', 1)
            return
        if not thumbnail:
            msgview(u'camera缩略图文件不能为空，请检查', 1)
            return

        if fbx_path.endswith('.fbx') is False:
            msgview(u'camera 文件格式不正确,需要为fbx文件，请检查', 1)
            return
        if thumbnail.endswith('.png') is False and thumbnail.endswith('.jpg') is False:
            msgview(u'camera缩略图文件格式不正确,需要为png或jpg文件，请检查', 1)
            return
        if not os.path.exists(fbx_path):
            msgview(u'camera fbx文件不存在,请检查', 21)
            return
        if not os.path.exists(thumbnail):
            msgview(u'camera缩略图文件不存在，请检查', 1)
            return

        if self.__model == 0:
            __cameras_data = pose_lib_fun.get_camera_library_data()
        else:
            __cameras_data = pose_lib_fun.get_local_camera_library_data()
        __fix_camera_data = []

        camera_data = {
            "name": camera_name,
            "character": character,
            "fbx_path": fbx_path,
            "thumbnail": thumbnail,
            "description": description,
            "update_time": self.__get_current_time(),
            "update_user": self.__get_user(),
            "common": common
        }
        self.__logger.info(u'camera数据更新开始,{},{}'.format(camera_data, self.__update_user))
        ok, result = self.__process_camera_data(camera_data)
        if not ok:
            msgview(result, 1)
            self.__logger.info(u'camera数据更新失败,{},{}'.format(result, self.__update_user))
            return
        camera_data = result

        self.__logger.info(type(__cameras_data))

        if not __cameras_data:
            __fix_camera_data.append(camera_data)
        else:
            for camera in __cameras_data:
                self.__logger.info(u'Camera,{}'.format(camera))
                __camera_name = camera.get("name")
                __camera_character = camera.get("character")
                __create_time = camera.get("create_time")
                __create_user = camera.get("user")
                if not __camera_name:
                    continue
                if not __camera_character:
                    continue
                if __camera_name == self.__camera_name and __camera_character == self.__character:
                    camera_data["create_time"] = __create_time
                    camera_data["create_user"] = __create_user
                    __fix_camera_data.append(camera_data)
                else:
                    __fix_camera_data.append(camera)

        if self.__model == 0:
            pose_lib_fun.save_camera_library(__fix_camera_data)
        else:
            pose_lib_fun.save_local_camera_library(__fix_camera_data)
        self.__logger.info(u'{} camera数据更新成功,{}'.format(camera_name, self.__update_user))
        msgview(u'camera数据替换成功', 2)

    def __process_camera_data(self, camera_data):
        __camera_lib_name = camera_data.get('name')
        __camera_lib_description = camera_data.get('description')
        __camera_lib_thumbnail = camera_data.get('thumbnail')
        __camera_lib_character = camera_data.get('character')
        __camera_lib_create_time = camera_data.get('create_time') if camera_data.get(
            'create_time') else self.__get_current_time()
        __camera_lib_user_name = camera_data.get('user') if camera_data.get('user') else self.__get_user()
        __camera_fbx_path = camera_data.get('fbx_path')

        if self.__model == 0:

            __camera_library_path = pose_lib_fun.get_camera_library_path()

        else:
            __camera_library_path = pose_lib_fun.get_local_camera_library_path()
        self.__logger.info(u'camera数据处理开始')
        self.__logger.info(u'__camera_library_path,{}'.format(__camera_library_path))
        __server_camera_fbx_path = u'{}/{}/{}/fbx/{}.fbx'.format(__camera_library_path, __camera_lib_character,
                                                                 __camera_lib_name, __camera_lib_name)

        __server_camera_thumbnail_path = u'{}/{}/{}/thumbnail/{}.png'.format(__camera_library_path,
                                                                             __camera_lib_character,
                                                                             __camera_lib_name, __camera_lib_name)

        __camera_fbx_path = self.__cover_ud(__camera_fbx_path)
        __camera_lib_thumbnail = self.__cover_ud(__camera_lib_thumbnail)
        __server_camera_fbx_path = self.__cover_ud(__server_camera_fbx_path)
        __server_camera_thumbnail_path = self.__cover_ud(__server_camera_thumbnail_path)

        __result = self.__copy_file(__camera_fbx_path, __server_camera_fbx_path)

        if not __result:
            self.__logger.info(u'camera库fbx文件复制失败,请检查路径是否正确')
            return False, u'camera库fbx文件复制失败,请检查路径是否正确'
        __result = self.__copy_file(__camera_lib_thumbnail, __server_camera_thumbnail_path)
        if not __result:
            self.__logger.info(u'camera库缩略图文件复制失败,请检查路径是否正确')
            return False, u'camera库缩略图文件复制失败,请检查路径是否正确'
        camera_data['fbx_path'] = __server_camera_fbx_path
        camera_data['thumbnail'] = __server_camera_thumbnail_path
        self.__logger.info(u'camera数据处理完成,{}'.format(camera_data))
        return True, camera_data

    def __copy_file(self, src, dst):
        import shutil
        scr = src.replace('\\', '/')
        dst = dst.replace('\\', '/')
        __dir = os.path.dirname(dst)
        if not os.path.exists(__dir):
            try:
                os.makedirs(__dir)
            except:
                msgview(u'创建目录失败', 2)
                return False
        if scr == dst:
            return True
        try:
            os.remove(dst)
        except:
            pass

        try:
            shutil.copy(src, dst)
            return True
        except Exception as e:
            return False

    def __cover_ud(self, info):
        if isinstance(info, str):
            info = info.decode('utf-8')
        return info.replace('\\', '/')

    def __get_current_time(self):
        return QDateTime.currentDateTime().toString("yyyy-MM-dd-hh-mm-ss")

    def __get_user(self):
        import getpass
        return getpass.getuser()


if __name__ == '__main__':
    import sys

    camera_name = "Cha_PL_Arm"
    character = "PL"
    fbx_path = "M:\\projects\\x3\\library\\camera_library\\PL\\Cha_PL_Arm\\fbx\\Cha_PL_Arm.fbx"
    thumbnail = "M:\\projects\\x3\\library\\camera_library\\PL\\Cha_PL_Arm\\thumbnail\\Cha_PL_Arm.png"
    description = "test"

    app = QApplication(sys.argv)
    window = ReplaceCameraUI(camera_name, character, fbx_path, thumbnail, description)
    window.show()
    sys.exit(app.exec_())
