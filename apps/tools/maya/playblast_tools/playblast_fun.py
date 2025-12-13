# -*- coding: utf-8 -*-
# author: linhuan
# file: playblast_fun.py
# time: 2025/11/5 15:20
# description:


import maya.cmds as cmds
import maya.mel as mel
import os
import method.maya.common.panel as common_panel

import method.maya.common.file as common_file
import method.common.dir as common_dir
import uuid
from lib.maya.plugin import plugin_load

CAM_FILE = r"M:/projects/x3/library/camera_library/FYN/Front_New/fbx/Front_New.fbx"
CAM_NAME = 'A_CameraAnimation_Front_New'


def asset_screen(width=512, height=512, output_dir=None):
    ok, reslut = judge_import_camera(CAM_FILE)
    if not ok:
        return False, reslut
    file_name = cmds.file(q=1, exn=1)
    base_name = os.path.basename(file_name)
    name, ext = os.path.splitext(base_name)
    name = name.split('.')[0]
    pic_path = u'{}/{}_front.png'.format(output_dir, name)

    ok, result = get_cam()
    if not ok:
        return False, result
    cam = result
    mel.eval('setNamedPanelLayout("Single Perspective View")')

    look_through_Cam(cam)
    panel_handle = common_panel.Panel()
    __viewpanel = panel_handle.get_viewpanel()
    cmds.modelEditor(__viewpanel, e=1, allObjects=0)
    cmds.modelEditor(__viewpanel, e=1, polymeshes=1, displayAppearance='smoothShaded', headsUpDisplay=0, grid=0,
                     pluginShapes=0, textures=1, displayTextures=1)
    curFrame = cmds.currentTime(q=1)

    pic_path = cmds.playblast(completeFilename=pic_path, frame=curFrame, format="image", compression="png", quality=100,
                              widthHeight=[width, height], percent=100, showOrnaments=True, viewer=True, offScreen=True)
    # panel_handle.set_persp_boundingBox()
    mel.eval('setNamedPanelLayout("Single Perspective View")')
    # delete_cam(cam)
    if not os.path.exists(pic_path):
        return False, u'截图失败，请检查'
    return True, pic_path


def get_cam():
    cams = cmds.ls(CAM_NAME)
    if not cams:
        return False, u'文件中不存在名称为{}的相机，请检查'.format(CAM_NAME)
    __cam = ''
    for _cam in cams:
        _cam_shape = cmds.listRelatives(_cam, s=1, type='camera')
        if _cam_shape:
            __cam = _cam_shape[0]
            break
    if not __cam:
        return False, u'文件中不存在名称为{}的相机，请检查'.format(CAM_NAME)
    return True, __cam


def judge_import_camera(camera_fbx_path):
    camers = cmds.ls(type='camera')
    _cam_list = []
    for _cmd in camers:
        tr = cmds.listRelatives(_cmd, p=1)
        if tr and tr[0] not in _cam_list:
            _cam_list.append(tr[0])
    if CAM_NAME not in _cam_list:
        return import_camera(camera_fbx_path)
    return True, camera_fbx_path


def import_camera(camera_fbx_path):
    try:
        plugin_load(['fbxmaya'])
    except Exception as e:
        pass

    camera_fbx_path = camera_fbx_path.decode('utf-8')
    if not camera_fbx_path or not os.path.exists(camera_fbx_path):
        return False, u'Camera文件不存在,请检查'
    try:
        cmds.file(camera_fbx_path, i=True, type='FBX', ignoreVersion=True, ra=True,
                  mergeNamespacesOnClash=False, options="v=0;p=17,f=0", pr=True,
                  importTimeRange="combine", loadReferenceDepth="all")
        return True, camera_fbx_path
    except Exception as e:
        return False, u'未正确导入相机fbx文件,请检查'


def delete_cam(cam):
    tr = cmds.listRelatives(cam, p=1)
    if tr:
        cmds.delete(tr)


def get_thum_file():
    _dir = common_dir.set_localtemppath(sub_dir='Info_Temp/screen')
    file_name = 'screen_{}.png'.format(uuid.uuid4().get_hex())
    return '{}/{}'.format(_dir, file_name)


def look_through_Cam(cam, fitFactor=1.0):
    cmds.lookThru(cam)
    cmds.viewFit(cam, fitFactor=fitFactor)
    modelPanelActiv = common_panel.Panel().get_viewpanel()
    cmds.modelEditor(modelPanelActiv, e=1, polymeshes=1, hud=1, ca=0, pluginShapes=0, lt=0, nurbsCurves=1,
                     displayAppearance='smoothShaded')


if __name__ == '__main__':
    asset_screen(width=4000, height=4000, output_dir=u'D:/测试')
