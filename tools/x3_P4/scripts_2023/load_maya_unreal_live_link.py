# -*- coding: utf-8 -*-
# author: linhuan
# file: load_maya_unreal_live_link.py
# time: 2025/10/22 19:29
# description:
import maya.mel as mel
import maya.cmds as cmds
import lib.maya.plugin as maya_plugin
def load_maya_unreal_live_link():
    plugin_list=['MayaUnrealLiveLinkPluginUI','MayaUnrealLiveLinkPlugin_4_27']
    try:
        maya_plugin.plugin_load(plugin_list)
    except:
        pass
    mel.eval('MayaUnrealLiveLinkUI')

