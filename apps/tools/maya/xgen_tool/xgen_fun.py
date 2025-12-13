# -*- coding: utf-8 -*-
# -----------------------------------
# @File    : axgen_fun.py
# @Author  : linhuan
# @Time    : 2025/7/5 13:23
# @Description : 
# -----------------------------------
import maya.cmds as cmds
import uuid
import maya.mel as mel


def get_selected_xgen_descriptions():
    """
    获取当前选中的Xgen描述
    :return: 选中的Xgen描述列表
    """
    selected = cmds.ls(selection=True, long=True)
    xgen_descriptions = [desc for desc in selected if get_type_by_transform(desc) == 'xgmDescription']
    return xgen_descriptions


def find_transform_by_xgen_description(xgen_description):
    if not cmds.objExists(xgen_description):
        return None
    transform = cmds.listRelatives(xgen_description, parent=True, fullPath=True,type='transform')
    if transform:
        return transform[0]
    return None


def get_type_by_transform(tr):
    if not tr or not cmds.objExists(tr):
        return None
    shape = cmds.listRelatives(tr, shapes=True, fullPath=True)
    if not shape:
        return 'Group'
    return cmds.nodeType(shape[0])


def get_node_uuid5(node):
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, str(node)))


def set_xgen_description_by_group_name(xgen_description, group_name):
    ok, result = add_xgen_description_group_name_attr(xgen_description, group_name)
    if not ok:
        return False, result
    ok, result = set_xgen_description_outliner_color_by_group_name(xgen_description, group_name)
    if not ok:
        return False, result
    return True, (xgen_description, group_name)


def remove_xgen_description_group_name_attr(xgen_description):
    if not cmds.objExists(xgen_description):
        return False, ("Xgen描述 {} 不存在".format(xgen_description))

    if cmds.attributeQuery('groupName', node=xgen_description, exists=True):
        cmds.deleteAttr('{}.groupName'.format(xgen_description))
        return True, (xgen_description, "groupName属性已删除")
    else:
        return False, ("Xgen描述 {} 没有groupName属性".format(xgen_description))


def set_remove_grom_name_attr_outliner_color(xgen_description):
    try:
        cmds.setAttr('{}.outlinerColor'.format(xgen_description), 0, 0, 0, type='double3')
        cmds.setAttr('{}.useOutlinerColor'.format(xgen_description), 0)
        mel.eval('AEdagNodeCommonRefreshOutliners();')
        return True, (xgen_description, "groupName属性已删除，颜色已重置")
    except Exception as e:
        return False, ("设置Xgen描述 {} 的颜色失败: {}".format(xgen_description, str(e)))


def add_xgen_description_group_name_attr(xgen_description, group_name):
    if not cmds.objExists(xgen_description):
        return False, ("Xgen描述 {} 不存在".format(xgen_description))

    if not cmds.attributeQuery('groupName', node=xgen_description, exists=True):
        cmds.addAttr(xgen_description, longName='groupName', dataType='string')

    cmds.setAttr('{}.groupName'.format(xgen_description), group_name, type='string')
    cmds.setAttr('{}.groupName'.format(xgen_description), keyable=True)
    return True, (xgen_description, group_name)


def get_uuid_by_group_name(group_name):
    return get_node_uuid5(group_name)


def set_xgen_description_outliner_color_by_group_name(xgen_description, group_name):

    group_name_uuid = get_uuid_by_group_name(group_name)
    color = cover_color_by_uuid(group_name_uuid)
    if cmds.objExists(xgen_description):
        cmds.setAttr('{}.useOutlinerColor'.format(xgen_description), 1)


        cmds.setAttr('{}.outlinerColor'.format(xgen_description), color[0], color[1], color[2], type='double3')
        mel.eval('AEdagNodeCommonRefreshOutliners();')
    else:
        return False, ("Xgen描述 {} 不存在".format(xgen_description))
    return True, (xgen_description, group_name)


def cover_color_by_uuid(_uuid):
    if not _uuid:
        return (1, 1, 1)
    r = int(_uuid[:2], 16) / 255.0
    g = int(_uuid[2:4], 16) / 255.0
    b = int(_uuid[4:6], 16) / 255.0

    return (r, g, b)
