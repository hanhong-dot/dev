# -*- coding: utf-8 -*-#
# -------------------------------------------------------
# NAME       : remove_pose
# Describe   : 说明描述
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2025/5/9__下午5:57
# -------------------------------------------------------
from apps.tools.maya.pose_library_tool import pose_lib_fun

reload(pose_lib_fun)
from apps.publish.ui.message.messagebox import msgview

def remove_pose(pose_name, fbx_file,model=0,ui=True):
    """
    删除pose
    :param pose_name: pose名称
    :param fbx_file: pose文件
    :param model: 0:服务器 1:本地库
    """
    result=msgview(u'请确定要删除Pose',1,1)
    if result == 0:
        return
    if model==0:
        pose_data = pose_lib_fun.get_pose_library_data()
    else:
        pose_data = pose_lib_fun.get_local_pose_library_data()

    if not pose_data:
        return
    for pose in pose_data:
        __pose_name = pose['name'] if pose['name'] else ''
        __fbx_file = pose['fbx_path'] if pose['fbx_path'] else ''
        if __pose_name  == pose_name and __fbx_file  == fbx_file:
            pose_data.remove(pose)

    if not pose_data:
        if model==0:
            pose_lib_fun.save_pose_library([])
        else:
            pose_lib_fun.save_local_pose_library([])
    else:
        if model==0:
            pose_lib_fun.save_pose_library(pose_data)
        else:
            pose_lib_fun.save_local_pose_library(pose_data)
    if ui:
        message = '删除Pose资产成功,请检查'
        msgview(message, 2)


