# -*- coding: utf-8 -*-
# author: linhuan
# file: uv_transfer_fun.py
# time: 2026/2/4 11:15
# description:
import maya.cmds as cmds
import maya.mel as mel
import time


def uv_transfer_mesh(target_uv_set_name='map3'):
    meshs = get_meshs_by_select()
    if not meshs:
        return False, u'未选择模型,请选择需要传递UV的模型'
    if meshs and len(meshs) != 2:
        return False, u'请选择两个模型,第一个为源模型,第二个为目标模型'
    src = meshs[0]
    dst = meshs[1]
    scr_uv_set = get_current_uv_set(src)
    if not scr_uv_set:
        return False, u'源模型当前没有UVSet,请检查源模型'
    targe_uv_sets = get_all_uv_sets(dst)
    result = create_uv_set(dst, target_uv_set_name)
    if not result:
        return False, u'目标模型创建{}UVSet失败,请检查目标模型'.format(target_uv_set_name)
    result = set_current_uv_set(dst, target_uv_set_name)
    if not result:
        return False, u'目标模型设置{}UVSet到当前失败,请检查目标模型'.format(target_uv_set_name)

    try:
        cmds.delete(dst, ch=True)
    except:
        pass
    time.sleep(1)
    result = transfer_uvs_between_meshes(scr_uv_set, target_uv_set_name)

    if not result:
        return False, u'UV传递失败,请检查模型'
    return True, u'UV传递成功'


def transfer_uvs_between_meshes(src_uv_set_name='map1', dst_uv_set_name='map3'):
    try:
        mel.eval(
            'transferAttributes -transferPositions 0 -transferNormals 0 -transferUVs 1 -sourceUvSet "{}" -targetUvSet "{}" -transferColors 0 -sampleSpace 0 -sourceUvSpace "{}" -targetUvSpace "{}" -searchMethod 3-flipUVs 0 -colorBorders 1'.format(
                src_uv_set_name, dst_uv_set_name, src_uv_set_name, dst_uv_set_name))
        return True
    except:
        return False


def set_current_uv_set(mesh, uv_set_name):
    all_uv_sets = get_all_uv_sets(mesh)
    current_uv = get_current_uv_set(mesh)[0]
    if all_uv_sets and uv_set_name in all_uv_sets and current_uv != uv_set_name:
        try:
            cmds.polyUVSet(mesh, currentUVSet=True, uvSet=uv_set_name)
            return True
        except:
            return False
    return True


def create_uv_set(mesh, uv_set_name):
    all_uv_sets = get_all_uv_sets(mesh)
    if all_uv_sets and uv_set_name in all_uv_sets:
        return True
    try:
        cmds.polyUVSet(mesh, create=True, uvSet=uv_set_name)
        return True
    except:
        return False


def get_all_uv_sets(mesh):
    uv_sets = cmds.polyUVSet(mesh, query=True, allUVSets=True)
    return uv_sets if uv_sets else []


def get_current_uv_set(mesh):
    uv_sets = cmds.polyUVSet(mesh, query=True, currentUVSet=True)
    if uv_sets:
        return uv_sets[0]
    return None


def get_meshs_by_select():
    meshs = []
    objs = cmds.ls(sl=True, tr=1, l=1)
    for obj in objs:
        shape = cmds.listRelatives(obj, s=1, type='mesh')
        if shape:
            meshs.append(obj)
    if meshs:
        meshs = list(set(meshs))
    return meshs
