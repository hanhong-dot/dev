# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       : scriptjob
# Describe   : 事件
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2023/3/22__17:34
# ------------------------
# -------------------------------
from pyfbsdk import *


def lod_script_jobs():
    #
    FBApplication().OnFileNew.Add(Onfilenew)
    FBApplication().OnFileOpen.Add(Onfileopen)
    Onfilecurren()


def Onfilecurren():
    SetSnapAndPlayOnFrames()
    SetFps30()


def Onfilenew(control, event):
    SetSnapAndPlayOnFrames()


def Onfileopen(control, event):
    SetFps30()


def SetSnapAndPlayOnFrames():
    # 获取当前播放器控制对象
    player_control = FBPlayerControl()

    # 将播放模式设置为 Snap & Play on Frames
    player_control.SnapMode = FBTransportSnapMode.kFBTransportSnapModeSnapAndPlayOnFrames


def SetFps30():
    player_control = FBPlayerControl()

    player_control.SetTransportFps(FBTimeMode.kFBTimeMode30Frames)
