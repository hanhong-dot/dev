# -*- coding: utf-8 -*-#
# -------------------------------------------------------
# NAME       : pose_syn_fun
# Describe   : 说明描述
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2025/6/27__下午12:15
# -------------------------------------------------------
import maya.cmds as cmds

from maya.api.OpenMaya import MSelectionList


def create_target(bs, target_name):
    base_mesh = get_base_mesh(bs)
    if not base_mesh:
        return None
    if cmds.objExists(target_name):
        cmds.delete(target_name)
    target = cmds.duplicate(base_mesh, name=target_name)[0]
    delete_target(bs, target)
    add_target(bs, target)
    cmds.delete(target)
    return target


def get_base_mesh(bs):
    try:
        return cmds.blendShape(bs, q=True, geometry=True)[0]
    except:
        return None


def creat_target_group(grp_name='A_Pose_Grp'):
    return cmds.group(empty=True, name=grp_name)


def get_target_name_by_mesh(mesh):
    return '{}_Target'.format(mesh.split('|')[-1].split(':')[-1])


def get_mesh_bs(poly):
    meshs = get_mesh(poly)
    if not meshs:
        return None
    for __msh in meshs:
        bs = cmds.ls(cmds.listHistory(__msh), type="blendShape")
        if bs:
            return bs[0]
    return None


def add_target(bs, target):
    if cmds.objExists(bs + "." + target):
        cmds.delete(bs + "." + target)
    index = get_next_index(bs)
    bs_attr = bs + '.weight[%i]' % index
    cmds.setAttr(bs + '.weight[%i]' % index, 1)
    cmds.aliasAttr(target, bs_attr)
    ipt_name = "{bs}.it[0].itg[{index}].iti[6000].ipt".format(**locals())
    ict_name = "{bs}.it[0].itg[{index}].iti[6000].ict".format(**locals())
    cmds.getAttr(ipt_name, type=1)
    cmds.getAttr(ict_name, type=1)
    return target


def delete_target(bs, target):
    attr = bs + "." + target
    if not cmds.objExists(attr):
        return
    index = get_index(bs, target)
    cmds.aliasAttr(attr, rm=1)
    cmds.removeMultiInstance(bs + ".weight[%i]" % index, b=1)
    cmds.removeMultiInstance(bs + ".it[0].itg[%i]" % index, b=1)


def get_mesh(tr):
    if not tr:
        return None
    mesh = cmds.listRelatives(tr, shapes=True, fullPath=True, type='mesh')
    if not mesh:
        return None
    return mesh


def get_next_index(bs):
    elem_indexes = cmds.getAttr(bs + ".weight", mi=1) or []
    index = len(elem_indexes)
    for i in range(index):
        if i == elem_indexes[i]:
            continue
        index = i
        break
    return index


def rebuild_target(bs, target_name):
    index = get_index(bs, target_name)
    cmds.sculptTarget(bs, e=1, regenerate=1, target=index)
    igt_name = "{bs}.it[0].itg[{index}].iti[6000].igt".format(**locals())
    return target_name


def get_index(bs, target):
    return api_ls(bs + "." + target).getPlug(0).logicalIndex()


def api_ls(*names):
    selection_list = MSelectionList()
    for name in names:
        selection_list.add(name)
    return selection_list
