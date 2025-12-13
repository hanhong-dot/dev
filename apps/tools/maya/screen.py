# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       :
# Describe   : maya内截图工具
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2024/5/30
# -------------------------------------------------------

import maya.cmds as cmds
import maya.mel as mel
import os
import method.maya.common.panel as common_panel

import method.maya.common.file as common_file
import method.common.dir as common_dir
import uuid
CAM_FILE=r'Z:\TD\cam\scrren_cam.ma'
CAM_NAME='screen_cam'

def screen_shot():
    cams = cmds.ls(type='camera')
    common_file.BaseFile().import_file(CAM_FILE)

    cams_new= cmds.ls(type='camera')
    cam_n=list(set(cams_new)-set(cams))
    if cam_n:
        cam=cam_n[0]
        look_through_Cam(cam)
        panel_handle = common_panel.Panel()
        cmds.modelEditor(panel_handle.get_viewpanel(), e=1, allObjects=1)  # 先把当前视窗所有内容勾选显示出来
        curFrame = cmds.currentTime(q=1)
        temp_pic_path = get_thum_file()
        pic_path = cmds.playblast(completeFilename=temp_pic_path, frame=curFrame, format="image", compression="png",
                                  widthHeight=[512, 512], percent=100, showOrnaments=False, viewer=False)
        # panel_handle.set_persp_boundingBox()
        mel.eval('setNamedPanelLayout("Single Perspective View")')
        delete_cam(cam)
        return pic_path



def delete_cam(cam):

    tr=cmds.listRelatives(cam,p=1)
    if tr:
        cmds.delete(tr)

def get_thum_file():
    _dir=common_dir.set_localtemppath(sub_dir='Info_Temp/screen')
    file_name='screen_{}.png'.format(uuid.uuid4().get_hex())
    return '{}/{}'.format(_dir,file_name)
def look_through_Cam(cam,fitFactor=1.0):
    cmds.lookThru(cam)
    cmds.viewFit(cam, fitFactor=fitFactor)
    modelPanelActiv = common_panel.Panel().get_viewpanel()
    cmds.modelEditor(modelPanelActiv, e=1, polymeshes=1, hud=1, ca=0, pluginShapes=0, lt=0, nurbsCurves=1,
                     displayAppearance='smoothShaded')


