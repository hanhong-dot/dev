# -*- coding: utf-8 -*-
# author: linhuan
# file: ma_process_fun.py
# time: 2025/11/28 21:42
# description:
import json
import os
import sys

sys.path.append('z:/dev')
import method.maya.common.file as maya_file
import lib.maya.plugin as maya_plugin
import maya.cmds as cmds
import maya.mel as mel
from apps.tools.motionbuilder.cover_mb_to_maya import bake_to_control

reload(bake_to_control)
import time


def ma_process_file(json_file):
    # type: (str) -> (bool, str)
    maya_plugin.plugin_load(['mtoa'])
    data = read_json(json_file)
    if not data:
        return False, u"没有读取到json数据"
    start_frame = data.get('start_frame', None)
    if start_frame is None:
        raise ValueError("start_frame is missing")
    end_frame = data.get('end_frame', None)
    if end_frame is None:
        raise ValueError("end_frame is missing")
    bake = data.get('bake', False)
    ma_file = data.get('ma_file', None)
    base_name = data.get('base_name', None)
    character_data = data.get('character_data', [])
    prop_data = data.get('prop_data', [])
    if not ma_file:
        raise ValueError("ma_file is missing")
    if not character_data:
        raise ValueError(u"缺少角色数据")
    maya_file_handle = maya_file.BaseFile()

    maya_file_handle.open_file(r'Z:\dev\config\common\maya\base.ma')
    maya_file_handle.save_file(ma_file)
    __ref_name_space_list = []
    set_frame_range(start_frame, end_frame)

    for char_data in character_data:
        asset_name = process_character_by_data(char_data)
        __ref_name_space_list.append(asset_name)
    if prop_data:
        for __pro_data in prop_data:
            pro_name_space = __pro_data.get('name_space', None)
            prop_fbx_path = __pro_data.get('fbx_path', None)
            import_fbx_file(prop_fbx_path, namespace=pro_name_space)

    set_frame_range(start_frame, end_frame)
    if bake == 1 or bake is True:
        for name_space in __ref_name_space_list:
            name_space=name_space + ':'
            result = bake_to_control.bake_to_control_by_name_space(name_space, start_frame, end_frame)
            if result:
                print("Baking completed for namespace: {}".format(name_space))

    if bake == 1 or bake is True:
        time.sleep(2)
        remove_fbx_references()


    maya_file_handle.save_file(ma_file)
    print("Processed MA file saved at: {}".format(ma_file))
    return True, ma_file


def remove_fbx_references():
    ref_nodes = cmds.ls(type='reference')
    for ref_node in ref_nodes:
        try:
            ref_file = cmds.referenceQuery(ref_node, filename=True)
            if ref_file.lower().endswith('.fbx'):
                cmds.file(rfn=ref_node, removeReference=1)
        except:
            continue


def process_character_by_data(char_data):
    mb_character_name = char_data.get('character_name', None)
    asset_name = char_data.get('asset_name', None)
    mb_fbx_path = char_data.get('mb_fbx_path', None)
    publish_path = char_data.get('publish_path', None)
    maya_file.BaseFile().reference_file(publish_path, namespace=asset_name)
    # if ':' in mb_character_name:
    #     mb_name_space= mb_character_name.split(':')[0]
    # else:
    mb_name_space = ':'
    reference_fbx_file(mb_fbx_path, namespace=mb_name_space)
    source_base_name = '{}_mb_to_maya'.format(asset_name)
    source_character = '{}:{}'.format(asset_name, source_base_name)
    if not cmds.objExists(source_character):
        source_base_name = '{}_mb_to_maya'.format(asset_name.split('_')[0])
        source_character = '{}:{}'.format(asset_name, source_base_name)
    set_character(source_character, mb_character_name)
    return asset_name


def reference_fbx_file(fbx_path, namespace):
    try:
        maya_plugin.plugin_load(['fbxmaya'])
    except:
        pass

    try:
        cmds.file(fbx_path, r=True, type="FBX", ignoreVersion=True, gl=True, mergeNamespacesOnClash=True,
                  namespace=namespace, options="fbx")
    except Exception as e:
        raise RuntimeError("Failed to reference FBX file {}: {}".format(fbx_path, str(e)))


def set_frame_range(start_frame, end_frame):
    cmds.playbackOptions(min=start_frame, ast=start_frame)
    cmds.playbackOptions(max=end_frame, aet=end_frame)


def import_fbx_file(fbx_path, namespace):
    try:
        maya_plugin.plugin_load(['fbxmaya'])
    except:
        pass
    try:
        cmds.file(fbx_path, i=True, type="FBX", ignoreVersion=True, ra=True, mergeNamespacesOnClash=False,
                  namespace=namespace, options="fbx", pr=True, importFrameRate=True, importTimeRange="override")
    except Exception as e:
        raise RuntimeError("Failed to import FBX file {}: {}".format(fbx_path, str(e)))


def set_character(source_character, target_character):
    _cmd = 'hikSetCharacterInput( "{}", "{}" );'.format(source_character, target_character)
    return mel.eval(_cmd)


def read_json(path, rtype="r", hook=None):
    if not os.path.exists(path):
        return None
    with open(path, rtype) as f:
        _data = json.load(f, object_pairs_hook=hook)
        f.close()
    return _data


def delete_rig_nodes_without_reference():
    __nodes = []
    rig_nodes = cmds.ls('*:*_Rig', tr=1, l=1) + cmds.ls('*_Rig', tr=1, l=1)
    if not rig_nodes:
        return __nodes
    for rig_node in rig_nodes:
        __ref = cmds.referenceQuery(rig_node, inr=1)
        if not __ref:
            __nodes.append(rig_node)
    if __nodes:
        try:
            cmds.delete(__nodes)
        except:
            pass
    return __nodes


def delete_ref_nodes_without_reference():
    __nodes = []
    ref_nodes = cmds.ls('*:Reference') + cmds.ls('Reference') + cmds.ls('*:*:Reference')
    if not ref_nodes:
        return __nodes
    for ref_node in ref_nodes:
        __ref = cmds.referenceQuery(ref_node, inr=1)
        if not __ref:
            __nodes.append(ref_node)
    if __nodes:
        try:
            cmds.delete(__nodes)
        except:
            pass


# if __name__ == '__main__':
#     import pprint
#
#     json_file = r'D:\Info_Temp\mobu\cover_mb_to_maya\output\data\DC_B_ML_C1S1_S01_P01_Act_Other_Award_01+1.json'
#
#     ok, result = ma_process_file(json_file)
#     pprint.pprint((ok, result))
