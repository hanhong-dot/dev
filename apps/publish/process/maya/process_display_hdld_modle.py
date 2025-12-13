# -*- coding: utf-8 -*-
# author: linhuan
# file: process_display_hdld_modle.py
# time: 2025/11/21 11:32
# description:
import maya.cmds as cmds


def display_hdld_model(TaskData):
    asset_type = TaskData.asset_type
    entity_name = TaskData.entity_name
    if asset_type.lower() != 'weapon':
        return
    if not entity_name.startswith('PL') and not entity_name.startswith('RY') and not entity_name.startswith('XL'):
        return
    grp_ld = '{}_LD'.format(entity_name)
    grp_hd = '{}_HD'.format(entity_name)
    trs_ld_list = get_all_trs_from_grp(grp_ld)
    trs_hd_list = get_all_trs_from_grp(grp_hd)
    display_trs(trs_ld_list, display=True)
    display_trs(trs_hd_list, display=True)
    return True


def display_trs(trs_list, display=True):
    if not trs_list:
        return
    for trs in trs_list:
        if not cmds.objExists(trs):
            continue
        if display:
            cmds.setAttr('{}.visibility'.format(trs), 1)
        else:
            cmds.setAttr('{}.visibility'.format(trs), 0)


def get_all_trs_from_grp(grp):
    trs_list = []
    if not grp or not cmds.objExists(grp):
        return trs_list
    grp = cmds.ls(grp, long=True)[0]
    if not grp:
        return trs_list
    trs_list.append(grp)

    children = cmds.listRelatives(grp, ad=True, fullPath=True, type='transform') or []
    if children:
        trs_list.extend(children)
    return trs_list
