# -*- coding: utf-8 -*-
# author: linhuan
# file: auto_copy_skin_fun.py
# time: 2025/12/13 15:59
# description:
from method.maya.common.file import BaseFile
from lib.maya.node.grop import BaseGroup
import maya.cmds as cmds

import maya.mel as mel
import maya.OpenMaya as om
import lib.maya.process.export_fbx as _fbx_common


def copy_skin_weights(source_mesh, target_mesh_list):
    if not source_mesh or not target_mesh_list:
        return False, 'source_mesh or target_mesh_list is None'
    if not cmds.objExists(source_mesh):
        return False, 'source_mesh {} is not exists'.format(source_mesh)
    for target_mesh in target_mesh_list:
        if not cmds.objExists(target_mesh):
            return False, 'target_mesh {} is not exists'.format(target_mesh)

    sskin = mel.eval('findRelatedSkinCluster {0}'.format(source_mesh))
    if not sskin:
        return False, 'source_mesh {} has no skincluster'.format(source_mesh)
    bone = cmds.skinCluster(sskin, q=True, inf=True)
    for mesh in target_mesh_list:
        dskin = cmds.skinCluster(bone, mesh, tsb=True, mi=20)[0]
        cmds.copySkinWeights(ss=sskin, ds=dskin, nm=True, sa='closestPoint')
        cmds.select(mesh, r=True)
        mel.eval('removeUnusedInfluences')
        cmds.select(cl=True)
        om.MGlobal.displayInfo('Skincluster tansfer over')
    return True, 'copy skin weights success'


def auto_copy_skin(body_asset_name, asset_type, asset_add, body_publish_file,asset_name, out_dir):
    ok, result = get_select_meshs()
    if not ok:
        return False, u'请先选择需要复制蒙皮的模型mesh！'
    scene_meshs = result
    if not scene_meshs:
        return False, u'请选择需要复制蒙皮的模型mesh！'

    result = import_file(body_asset_name, body_publish_file)
    if not result:
        return False, u'导入body资产{}上传文件失败，请检查！'.format(body_asset_name)

    ok, result = get_process_meshs_by_asset(body_asset_name, asset_type, asset_add)
    if not ok:
        return False, result
    body_process_mesh = result
    ok, result = copy_skin_weights(body_process_mesh, scene_meshs)
    if not ok:
        return False, result
    out_path='{}/{}_AutoSkin.fbx'.format(out_dir, asset_name)
    ok=export_fbx_file(scene_meshs, out_path)
    if not ok:
        return False, u'自动蒙皮FBX导出失败，请检查！'
    return True, u'自动蒙皮完成！'


def export_fbx_file(export_meshs, out_fbx_file):
    if not export_meshs:
        return False, u'没有可导出的mesh！'
    return _fbx_common.export_fbx(export_meshs, out_fbx_file, hi=1, triangulate=1, warning=0)


def get_process_meshs_by_asset(body_asset_name, asset_type, asset_add):
    body_group = ''
    if asset_type == 'hair' and not body_asset_name.endswith('_New'):
        body_group = '*:{}001H_HD'.format(asset_add)
    elif asset_type == 'role' and not body_asset_name.endswith('_New'):
        body_group = '*:{}001B_HD'.format(asset_add)
    elif asset_type == 'hair' and body_asset_name.endswith('_New'):
        body_group = '*:{}001H_New_HD'.format(asset_add)
    elif asset_type == 'role' and body_asset_name.endswith('_New'):
        body_group = '*:{}001B_New_HD'.format(asset_add)
    if not body_group:
        return False, u'不支持该类型资产的蒙皮复制操作！'
    if not cmds.ls(body_group):
        return False, u'{}资产文件中缺少{}组，请检查！'.format(body_asset_name, body_group.split(':')[-1])
    body_group = cmds.ls(body_group)[0]

    meshs = get_dis_meshs_from_group(body_group)
    if not meshs:
        return False, u'{}资产文件中{}组下没有可见的mesh，请检查！'.format(body_asset_name, body_group.split(':')[-1])

    process_mesh = ''
    if len(meshs) > 1:
        new_mesh_name = '{}_Process_Mesh'.format(body_asset_name)
        success, result = combine_meshs(meshs, new_mesh_name)
        if not success:
            return False, result
        process_mesh = result
    else:
        process_mesh = meshs[0]
    return True, process_mesh


def combine_meshs(mesh_list, new_mesh_name):
    if not mesh_list or len(mesh_list) < 2:
        return False, u"需要合并的mesh数量不足！"
    cmds.select(mesh_list, r=True)
    combined_mesh = cmds.polyUnite(n=new_mesh_name, ch=1)[0]
    return True, combined_mesh


def import_file(asset_name, file_path):
    return BaseFile().import_file(file_path, namespace=asset_name)


def get_current_groups():
    return BaseGroup().get_root_groups()


def get_select_meshs():
    select_objs = cmds.ls(sl=1, l=1)
    meshs = []
    if not select_objs:
        return False, meshs
    for obj in select_objs:
        shape_nodes = cmds.listRelatives(obj, s=1, type='mesh', f=1)
        if not shape_nodes:
            continue
        meshs.append(obj)
    if not meshs:
        return False, meshs
    return True, meshs


def get_all_meshs_in_scene():
    meshs = cmds.ls(type='mesh', long=True)
    trs = []
    if not meshs:
        return trs
    for mesh in meshs:
        tr = cmds.listRelatives(mesh, p=True, f=True, type='transform')
        if tr and tr[0] not in trs:
            trs.append(tr[0])
    if trs:
        trs = list(set(trs))
    return trs


def get_dis_meshs_from_group(group_name):
    trs = []
    meshs = cmds.listRelatives(group_name, ad=True, type='mesh', f=True)
    if not meshs:
        return trs
    for mesh in meshs:
        tr = cmds.listRelatives(mesh, p=True, f=True, type='transform')
        if not tr:
            continue
        dis = cmds.getAttr(tr[0] + '.visibility')
        if dis and tr[0] not in trs:
            trs.append(tr[0])

    if trs:
        trs = list(set(trs))
    return trs
