# -*- coding: utf-8 -*-#
# Python     : 
# -------------------------------------------------------
# NAME       : load_animschool_picker_2023
# Describe   : 说明描述
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2025/4/17__11:20
# -------------------------------------------------------
ANIMSCHOOL2023PLUG = "Z:\\dev\\tools\\AnimSchool_2024\\maya2023\\AnimSchoolPicker.mll"
import maya.mel as mel
import maya.cmds as cmds

def load_animschool_picker_2023():
    load = cmds.pluginInfo(ANIMSCHOOL2023PLUG, loaded=1, q=1)
    if not load or load != True:
        cmds.loadPlugin(ANIMSCHOOL2023PLUG, qt=1)
    mel.eval("AnimSchoolPicker();")
