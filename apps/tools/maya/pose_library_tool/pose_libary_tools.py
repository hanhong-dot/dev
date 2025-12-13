# -*- coding: utf-8 -*-#
# -------------------------------------------------------
# NAME       : pose_libary_tools
# Describe   : 说明描述
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2025/4/27__下午6:40
# -------------------------------------------------------
import sys

sys.path.append('Z:/dev')

try:
    from PySide2.QtWidgets import *
    from PySide2.QtGui import *
    from PySide2.QtCore import *
except:
    from PyQt5.QtWidgets import *
    from PyQt5.QtGui import *
    from PyQt5.QtCore import *

import apps.publish.ui.basewindow.basewiondow as basewindow

from apps.tools.maya.pose_library_tool import pose_library_ui

reload(pose_library_ui)

from apps.tools.maya.pose_library_tool import creat_pose_lib

reload(creat_pose_lib)

from apps.tools.maya.pose_library_tool import creat_camera_lib

reload(creat_camera_lib)

import apps.launch.maya.interface.mayaview as _mayaview
from apps.tools.maya.pose_library_tool import replace_pose
reload(replace_pose)

from apps.tools.maya.pose_library_tool import replace_camera
reload(replace_camera)


def load_pose_library_ui():
    app = QApplication.instance()
    global PoseLibrary
    try:
        PoseLibrary.close()
        PoseLibrary.deleteLater()
    except:
        pass

    if not app:
        app = QApplication(sys.argv)
    PoseLibrary = basewindow.BaseWindow(_mayaview.get_maya_window(), "Pose Library")
    PoseLibrary.set_central_widget(pose_library_ui.PoseLibraryUI())
    #
    PoseLibrary.set_help(url=r"https://papergames.feishu.cn/wiki/KeUywrqgti3JAGkZV31cL4XZnUA?from=from_copylink")

    PoseLibrary.setMinimumSize(500, 650)
    PoseLibrary.show()
    app.exec_()


def replace_pose_library_ui(pose_name, character, fbx_path, thumbnai, description, mode=0):
    app = QApplication.instance()
    global ReplacePoseLibrary
    try:
        ReplacePoseLibrary.close()
        ReplacePoseLibrary.deleteLater()
    except:
        pass

    if not app:
        app = QApplication(sys.argv)
    if mode == 0:
        __title = "替换Pose库资产(服务器)"
    else:
        __title = "替换Pose库资产(本地)"
    ReplacePoseLibrary = basewindow.BaseWindow(_mayaview.get_maya_window(), __title)

    ReplacePoseLibrary.set_central_widget(
        replace_pose.ReplacePoseUI(pose_name, character, fbx_path, thumbnai, description, mode))
    # collect.set_help(url=r"https://papergames.feishu.cn/wiki/SavswLVLLinFsAkRuzncIVVenCR?from=from_copylink")
    ReplacePoseLibrary.setMinimumSize(400, 300)
    ReplacePoseLibrary.show()


def replace_camera_library_ui(camera_name, character, fbx_path, thumbnai, description, mode=0):
    app = QApplication.instance()
    global ReplacePoseLibrary
    try:
        ReplacePoseLibrary.close()
        ReplacePoseLibrary.deleteLater()
    except:
        pass

    if not app:
        app = QApplication(sys.argv)
    if mode == 0:
        __title = "替换Pose库资产(服务器)"
    else:
        __title = "替换Pose库资产(本地)"
    ReplacePoseLibrary = basewindow.BaseWindow(_mayaview.get_maya_window(), __title)

    ReplacePoseLibrary.set_central_widget(
        replace_camera.ReplaceCameraUI(camera_name, character, fbx_path, thumbnai, description, mode))
    # collect.set_help(url=r"https://papergames.feishu.cn/wiki/SavswLVLLinFsAkRuzncIVVenCR?from=from_copylink")
    ReplacePoseLibrary.setMinimumSize(400, 300)
    ReplacePoseLibrary.show()



def creat_pose_library_ui(character_name, model=0):
    app = QApplication.instance()
    global CreatPoseLibrary
    try:
        CreatPoseLibrary.close()
        CreatPoseLibrary.deleteLater()
    except:
        pass

    if not app:
        app = QApplication(sys.argv)
    if model == 0:
        __title = "添加Pose库资产(服务器)"
    else:
        __title = "添加Pose库资产(本地)"
    CreatPoseLibrary = basewindow.BaseWindow(_mayaview.get_maya_window(), __title)

    CreatPoseLibrary.set_central_widget(creat_pose_lib.CreatPoseLibraryUI(character_name, model))
    # collect.set_help(url=r"https://papergames.feishu.cn/wiki/SavswLVLLinFsAkRuzncIVVenCR?from=from_copylink")
    CreatPoseLibrary.setMinimumSize(400, 300)
    CreatPoseLibrary.show()


def creat_camera_library_ui(character_name, model=0):
    app = QApplication.instance()
    global CreatCameraLibrary
    try:
        CreatCameraLibrary.close()
        CreatCameraLibrary.deleteLater()
    except:
        pass

    if not app:
        app = QApplication(sys.argv)

    if model == 0:
        __title = "添加相机库资产(服务器)"
    else:
        __title = "添加相机库资产(本地)"

    CreatCameraLibrary = basewindow.BaseWindow(_mayaview.get_maya_window(), __title)

    CreatCameraLibrary.set_central_widget(creat_camera_lib.CreatCameraLibUI(character_name, model))
    # collect.set_help(url=r"https://papergames.feishu.cn/wiki/SavswLVLLinFsAkRuzncIVVenCR?from=from_copylink")
    CreatCameraLibrary.setMinimumSize(400, 300)
    CreatCameraLibrary.show()
