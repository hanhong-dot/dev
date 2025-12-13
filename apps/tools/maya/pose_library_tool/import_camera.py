# -*- coding: utf-8 -*-#
# -------------------------------------------------------
# NAME       : import_camera
# Describe   : 说明描述
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2025/5/10__下午1:53
# -------------------------------------------------------

from apps.publish.ui.message.messagebox import msgview


def import_camera(camera_fbx_path):
    import maya.cmds as cmds
    import os

    result = msgview(u'请确定是否导入Camera文件', 1, 1)
    if result == 0:
        return
    camera_fbx_path = camera_fbx_path.decode('utf-8')

    if not camera_fbx_path or not os.path.exists(camera_fbx_path):
        msgview(u'Camera文件不存在,请检查', 1)
        return False

    try:
        cmds.file(camera_fbx_path, i=True, type='FBX', ignoreVersion=True, ra=True,
                  mergeNamespacesOnClash=False, options="v=0;p=17,f=0", pr=True,
                  importTimeRange="combine", loadReferenceDepth="all")
        msgview(u'Camera文件已成功导入,请检查', 2)
        return True
    except Exception as e:
        msgview(u'未正确导入相机fbx文件,请检查', 0)

        return False
