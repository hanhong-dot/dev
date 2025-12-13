# -*- coding: utf-8 -*-#
# -------------------------------------------------------
# NAME       : remove_camera
# Describe   : 说明描述
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2025/5/10__下午2:08
# -------------------------------------------------------
from apps.tools.maya.pose_library_tool import pose_lib_fun

reload(pose_lib_fun)
from apps.publish.ui.message.messagebox import msgview


def remove_camera(camera_name, camera_fbx_path, model=0, ui=True):
    """
    删除Camera资产
    :param camera_name: Camera名称
    :param camera_fbx_path: Camera FBX路径
    :param model: 0:服务器 1:本地库
    """
    result = msgview(u'请确定是否要删除Camera资产', 1, 1)
    if result == 0:
        return

    if model == 0:

        camera_data = pose_lib_fun.get_camera_library_data()

    else:
        camera_data = pose_lib_fun.get_local_camera_library_data()

    if not camera_data:
        return

    for camera in camera_data:
        __camera_name = camera['name'] if camera['name'] else ''
        __camera_fbx_path = camera['fbx_path'] if camera['fbx_path'] else ''
        if __camera_name == camera_name and __camera_fbx_path == camera_fbx_path:
            camera_data.remove(camera)

    if not camera_data:
        if model == 0:
            pose_lib_fun.save_camera_library([])
        else:
            pose_lib_fun.save_local_camera_library([])
    else:
        if model == 0:
            pose_lib_fun.save_camera_library(camera_data)
        else:
            pose_lib_fun.save_local_camera_library(camera_data)

    if ui:
        message = '删除成功,请检查相机库'
        msgview(message, 2)
