# -*- coding: utf-8 -*-
# author: linhuan
# file: add_group.py
# time: 2025/12/9 16:19
# description:
import os
import sys
import maya.cmds as cmds
from database.shotgun.core.sg_analysis import Config

PROJECTNAME = 'X3'


def create_group_by_file_name():
    file_path = cmds.file(q=1, exn=1)
    if not file_path:
        cmds.confirmDialog(title='Error', message='Please save the scene first.', button=['OK'])
        return
    file_name = os.path.basename(file_path)
    asset_name = file_name.split('.')[0]
    check_result = check_asset_name(asset_name)
    if not check_result:
        cmds.confirmDialog(title='Error', message='Asset name "{}" does not exist in Shotgun.'.format(asset_name),
                           button=['OK'])
        return
    group_name = '{}_HD'.format(asset_name)
    if not cmds.objExists(group_name):
        cmds.group(em=1, name=group_name)
    all_meshs =  get_select_objs()
    if not all_meshs:
        return
    for mesh in all_meshs:
        if cmds.objExists(group_name):
            try:
                cmds.parent(mesh, group_name)
            except Exception as e:
                print("Failed to parent {} to {}: {}".format(mesh, group_name, e))
    cmds.confirmDialog(title='Success', message=u'已创建"{}"组,请检查'.format(group_name), button=['OK'])
    return True


def get_all_meshs():
    all_meshes = cmds.ls(type='mesh', long=True)
    transform_nodes = set()
    for mesh in all_meshes:
        parent = cmds.listRelatives(mesh, parent=True, fullPath=True, type="transform")
        if parent:
            transform_nodes.add(parent[0])
    return list(transform_nodes)


def get_select_objs():
    selected_objs = cmds.ls(selection=True, long=True,tr=1)
    return selected_objs


def check_asset_name(asset_name):
    sg_login = Config()
    sg = sg_login.login()
    filters = [['project.Project.name', 'is', PROJECTNAME], ['code', 'is', asset_name]]
    fields = ['id']

    result = sg.find_one(entity_type='Asset',
                         filters=filters,
                         fields=fields)
    if result:
        return True
    return False
