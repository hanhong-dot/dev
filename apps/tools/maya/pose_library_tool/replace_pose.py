# -*- coding: utf-8 -*-#
# -------------------------------------------------------
# NAME       : replace_pose
# Describe   : 说明描述
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2025/5/19__下午5:48
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


class ReplacePoseUI(QWidget):
    def __init__(self, pose_name=None, character=None, fbx_path=None, thumbnail=None, description=None, model=0,
                 parent=None):
        """
        :param pose_name: Pose名称
        :param character: 角色名称
        :param fbx_path: Pose fbx文件路径
        :param thumbnail: Pose缩略图路径
        :param description: 描述信息
        :param mode: 0: 0 服务器 1 本地
        """
        super(ReplacePoseUI, self).__init__(parent)
        self.setWindowTitle(u'编辑更新当前Pose数据')
        self.setGeometry(600, 200, 600, 200)
        self.__pose_name = pose_name
        self.__character = character
        self.__fbx_path = fbx_path
        self.__thumbnail = thumbnail
        self.__description = description
        self.__model = model
        if self.__model == 0:
            __log_dir = pose_lib_fun.get_lib_log_path()
        else:
            __log_dir = pose_lib_fun.get_local_lib_log_path()

        __log_path = os.path.join(__log_dir, "updata_pose_lib_{}.log".format(self.__get_current_time()))
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
        self.__pose_lib_name = QLineEdit(self.__pose_name)
        self.__pose_lib_name.setMinimumHeight(30)
        self.__pose_fbx_layout = QHBoxLayout()
        self.__pose_fbx_path = QLineEdit(self.__fbx_path)
        self.__pose_fbx_path.setMinimumHeight(30)
        self.__pose_fbx_layout.addWidget(self.__pose_fbx_path)
        self.__pose_fbx_btn = QPushButton(u"浏览")
        self.__pose_fbx_btn.setMinimumHeight(30)
        self.__pose_fbx_layout.addWidget(self.__pose_fbx_btn)
        self.__pose_lib_description = QPlainTextEdit(self.__description)
        self.__pose_lib_description.setMinimumHeight(60)
        self.__pose_thumbnail_layout = QHBoxLayout()
        self.__pose_lib_thumbnail = QLineEdit()
        self.__pose_lib_thumbnail.setText(self.__thumbnail)
        self.__pose_lib_thumbnail.setMinimumHeight(30)
        self.__pose_thumbnail_layout.addWidget(self.__pose_lib_thumbnail)
        self.__pose_thumbnail_btn = QPushButton(u"浏览")
        self.__pose_thumbnail_btn.setMinimumHeight(30)
        self.__pose_thumbnail_layout.addWidget(self.__pose_thumbnail_btn)
        self.__pose_replace_btn = QPushButton("替换Pose库数据")
        self.__pose_replace_btn.setBackgroundRole(QPalette.Button)
        self.__pose_replace_btn.setStyleSheet("background-color: rgb(30, 90, 87);color: rgb(255, 255, 255);")
        self.__pose_replace_btn.setMinimumHeight(30)
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
        ml.addWidget(self.__pose_replace_btn)

    def __connect_signals(self):
        self.__pose_fbx_btn.clicked.connect(self.__pose_fbx_btn_clicked)
        self.__pose_thumbnail_btn.clicked.connect(self.__pose_thumbnail_btn_clicked)
        self.__pose_replace_btn.clicked.connect(self.__pose_replace_btn_clicked)

    def __pose_fbx_btn_clicked(self):
        __pose_fbx_file_path = self.__pose_fbx_path.text()
        self.__pose_fbx_file_path = QFileDialog.getOpenFileName(self, u"选择fbx文件", __pose_fbx_file_path,
                                                                u"FBX Files (*.fbx);;All Files (*)")
        if self.__pose_fbx_file_path:
            self.__pose_fbx_path.setText(self.__pose_fbx_file_path[0])
            self.__pose_fbx_file_path = self.__pose_fbx_file_path[0]
            if not self.__pose_fbx_file_path:
                msgview(u'请选择fbx文件', 1)
                return

    def __pose_thumbnail_btn_clicked(self):

        __pose_thumbnail_path_txt_path = self.__pose_lib_thumbnail.text()

        self.__pose_thumbnail_file_path = QFileDialog.getOpenFileName(self, u"选择缩略图文件",
                                                                      __pose_thumbnail_path_txt_path,
                                                                      u"Image Files (*.png *.jpg);;All Files (*)")
        if self.__pose_thumbnail_file_path:
            self.__pose_lib_thumbnail.setText(self.__pose_thumbnail_file_path[0])
            self.__pose_thumbnail_file_path = self.__pose_thumbnail_file_path[0]
            # if not self.__pose_thumbnail_file_path:
            #     msgview(u'请选择缩略图文件', 2)
            #     return

    def __pose_replace_btn_clicked(self):
        self.__update_user = self.__get_user()

        pose_name = self.__pose_lib_name.text()
        character = self.__character_name.text()
        fbx_path = self.__pose_fbx_path.text()
        thumbnail = self.__pose_lib_thumbnail.text()
        description = self.__pose_lib_description.toPlainText()

        if not pose_name:
            msgview(u'Pose名称不能为空，请检查', 1)
            return
        if not fbx_path:
            msgview(u'Pose fbx文件不能为空，请检查', 1)
            return
        if not thumbnail:
            msgview(u'Pose缩略图文件不能为空，请检查', 1)
            return

        if fbx_path.endswith('.fbx') is False:
            msgview(u'Pose 文件格式不正确,需要为fbx文件，请检查', 1)
            return
        if thumbnail.endswith('.png') is False and thumbnail.endswith('.jpg') is False:
            msgview(u'Pose缩略图文件格式不正确,需要为png或jpg文件，请检查', 1)
            return
        if not os.path.exists(fbx_path):
            msgview(u'Pose fbx文件不存在,请检查', 21)
            return
        if not os.path.exists(thumbnail):
            msgview(u'Pose缩略图文件不存在，请检查', 1)
            return

        if self.__model == 0:
            __poses_data = pose_lib_fun.get_pose_library_data()
        else:
            __poses_data = pose_lib_fun.get_local_pose_library_data()
        __fix_pose_data = []


        pose_data = {
            "name": pose_name,
            "character": character,
            "fbx_path": fbx_path,
            "thumbnail": thumbnail,
            "description": description,
            "update_time": self.__get_current_time(),
            "update_user": self.__get_user()
        }
        self.__logger.info(u'Pose数据更新开始,{},{}'.format(pose_data,self.__update_user))
        ok, result = self.__process_pose_data(pose_data)
        if not ok:
            msgview(result, 1)
            self.__logger.info(u'Pose数据更新失败,{},{}'.format(result, self.__update_user))
            return
        pose_data = result

        self.__logger.info(type(__poses_data))

        if not __poses_data:
            __fix_pose_data.append(pose_data)
        else:
            for pose in __poses_data:
                self.__logger.info(u'pose,{}'.format(pose))
                __pose_name= pose.get("name")
                __pose_character = pose.get("character")
                __create_time = pose.get("create_time")
                __create_user = pose.get("user")
                if not __pose_name:
                    continue
                if not __pose_character:
                    continue
                if __pose_name==self.__pose_name and __pose_character==self.__character:
                    pose_data["create_time"] = __create_time
                    pose_data["create_user"] = __create_user
                    __fix_pose_data.append(pose_data)
                else:
                    __fix_pose_data.append(pose)

        if self.__model == 0:
            pose_lib_fun.save_pose_library(__fix_pose_data)
        else:
            pose_lib_fun.save_local_pose_library(__fix_pose_data)
        self.__logger.info(u'{} Pose数据更新成功,{}'.format(pose_name, self.__update_user))
        msgview(u'Pose数据替换成功', 2)

    def __process_pose_data(self, pose_data):
        __pose_lib_name = pose_data.get('name')
        __pose_lib_description = pose_data.get('description')
        __pose_lib_thumbnail = pose_data.get('thumbnail')
        __pose_lib_character = pose_data.get('character')
        __pose_lib_create_time = pose_data.get('create_time') if pose_data.get(
            'create_time') else self.__get_current_time()
        __pose_lib_user_name = pose_data.get('user') if pose_data.get('user') else self.__get_user()
        __pose_fbx_path = pose_data.get('fbx_path')

        if self.__model == 0:

            __pose_library_path = pose_lib_fun.get_pose_library_path()

        else:
            __pose_library_path = pose_lib_fun.get_local_pose_library_path()
        self.__logger.info(u'Pose数据处理开始')
        self.__logger.info(u'__pose_library_path,{}'.format(__pose_library_path))
        __server_pose_fbx_path = '{}/{}/{}/fbx/{}.fbx'.format(__pose_library_path, __pose_lib_character,
                                                              __pose_lib_name, __pose_lib_name)

        __server_pose_thumbnail_path = '{}/{}/{}/thumbnail/{}.png'.format(__pose_library_path, __pose_lib_character,
                                                                          __pose_lib_name, __pose_lib_name)

        self.__logger.info(u'__server_pose_fbx_path,{}'.format(__server_pose_fbx_path))
        self.__logger.info(u'__server_pose_thumbnail_path,{}'.format(__server_pose_thumbnail_path))
        __pose_fbx_path = self.__cover_ud(__pose_fbx_path)
        __pose_lib_thumbnail = self.__cover_ud(__pose_lib_thumbnail)
        __server_pose_fbx_path = self.__cover_ud(__server_pose_fbx_path)
        __server_pose_thumbnail_path = self.__cover_ud(__server_pose_thumbnail_path)

        __result = self.__copy_file(__pose_fbx_path, __server_pose_fbx_path)

        if not __result:
            self.__logger.info(u'Pose库fbx文件复制失败,请检查路径是否正确')
            return False, u'Pose库fbx文件复制失败,请检查路径是否正确'
        __result = self.__copy_file(__pose_lib_thumbnail, __server_pose_thumbnail_path)
        if not __result:
            self.__logger.info(u'Pose库缩略图文件复制失败,请检查路径是否正确')
            return False, u'Pose库缩略图文件复制失败,请检查路径是否正确'
        pose_data['fbx_path'] = __server_pose_fbx_path
        pose_data['thumbnail'] = __server_pose_thumbnail_path
        self.__logger.info(u'Pose数据处理完成,{}'.format(pose_data))
        return True, pose_data

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

    pose_name = "Cha_PL_Arm"
    character = "PL"
    fbx_path = "M:\\projects\\x3\\library\\pose_library\\PL\\Cha_PL_Arm\\fbx\\Cha_PL_Arm.fbx"
    thumbnail = "M:\\projects\\x3\\library\\pose_library\\PL\\Cha_PL_Arm\\thumbnail\\Cha_PL_Arm.png"
    description = "test"

    app = QApplication(sys.argv)
    window = ReplacePoseUI(pose_name, character, fbx_path, thumbnail, description)
    window.show()
    sys.exit(app.exec_())
