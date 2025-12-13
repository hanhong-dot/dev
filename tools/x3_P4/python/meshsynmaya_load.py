# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       : meshsynmaya_load
# Describe   : 说明描述
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2023/6/20__19:36
# -------------------------------------------------------


import maya.cmds as cmds
import maya.mel as mel


def load_meshsynmaya():
    plugin_load(['MeshSyncClientMaya'])
    plugin_path=cmds.pluginInfo('MeshSyncClientMaya', q=1,path=True)
    melpath='{}/scripts/userSetup.mel'.format(plugin_path.split('plug-ins')[0])
    mel.eval('source "{}"'.format(melpath))


def plugin_load(pluginlist):
    """
    加载插件
    :param pluginlist: 需要加载的插件列表
    :type pluginlist: list
    :return: True
    :rtype: bool
    """
    if pluginlist:
        for plug in pluginlist:
            load = cmds.pluginInfo(plug, loaded=1, q=1)
            if load != True:
                cmds.loadPlugin(plug, qt=1)
        return True
