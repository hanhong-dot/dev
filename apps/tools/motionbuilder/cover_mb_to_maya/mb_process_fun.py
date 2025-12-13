# -*- coding: utf-8 -*-
# author: linhuan
# file: mb_process_fun.py
# time: 2025/11/27 16:17
# description:
from pyfbsdk import *
from lib.mobu import mb_fun

reload(mb_fun)

from apps.tools.motionbuilder.cover_mb_to_maya import sg_fun
import os
import json


def process_current_mobu_file(mb_file, mapping_dict, out_path, bake=False, log_handle=None):
    from apps.tools.motionbuilder.cover_mb_to_maya import cover_maya_batch_process
    ok, result = processt_mb_file(mb_file, mapping_dict, out_path, bake=bake, log_handle=log_handle)
    mb_fun.mb_file_new()
    if not ok:
        return False, result
    json_file, ma_file = result
    result = cover_maya_batch_process.run_process_cover_to_maya2018(json_file)
    if 'True' in result and os.path.exists(ma_file):
        if log_handle:
            log_handle.info("Maya file conversion succeeded: {}".format(ma_file))
        return True, ma_file
    return False, "Maya file conversion failed."


def batch_process_mobu_files(dir_path, mapping_dict, out_path, bake=False, log_handle=None):
    from apps.tools.motionbuilder.cover_mb_to_maya import cover_maya_batch_process
    fbx_files = get_fbx_from_dir(dir_path)
    if not fbx_files:
        return False, "No fbx file found in the directory."
    success_files = []
    failed_files = []
    for mb_file in fbx_files:
        mb_fun.open_mb_file(mb_file)
        if bake == True:
            bake = 1
        else:
            bake = 0
        ok, result = processt_mb_file(mb_file, mapping_dict, out_path, bake=bake, log_handle=log_handle)
        if not ok:
            failed_files.append({'mb_file': mb_file, 'error': result})
            log_handle.error("Processing failed for {}: {}".format(mb_file, result))
            continue
        json_file, ma_file = result
        result = cover_maya_batch_process.run_process_cover_to_maya2018(json_file)
        if 'True' in result and os.path.exists(ma_file):
            if log_handle:
                log_handle.info("Maya file conversion succeeded: {}".format(ma_file))
            success_files.append(ma_file)
        else:
            failed_files.append({'mb_file': mb_file, 'error': "Maya file conversion failed."})
        mb_fun.mb_file_new()

    return True, {'success_files': success_files, 'failed_files': failed_files}


def rename_namespace(namespace, new_namespace):
    scene = FBSystem().Scene

    return scene.NamespaceRename(namespace, new_namespace)


def rename_same_namespace(namespace, asset_name, all_namespaces):
    if namespace != asset_name:
        return namespace
    index = 1
    new_namespace = "{}_{}".format(namespace, index)
    if new_namespace not in all_namespaces:
        rename_namespace(namespace, new_namespace)
        return new_namespace
    while True:
        index += 1
        new_namespace = "{}_{}".format(namespace, index)
        if new_namespace not in all_namespaces:
            rename_namespace(namespace, new_namespace)
            break
    return new_namespace


def get_fbx_from_dir(dir_path):
    fbx_files = []
    files = os.listdir(dir_path)
    for file in files:
        if file.lower().endswith('.fbx'):
            fbx_file = os.path.join(dir_path, file)
            fbx_file = fbx_file.replace('\\', '/')
            fbx_files.append(fbx_file)
    return fbx_files


def processt_mb_file(mb_file, mapping_dict, out_dir, bake=0, log_handle=None):
    base = get_base(mb_file)
    characts = mb_fun.get_all_characters()
    fbx_dir = '{}/fbx/{}'.format(out_dir, base)
    if not os.path.exists(fbx_dir):
        os.makedirs(fbx_dir)
    data_dir = '{}/data'.format(out_dir)
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    json_file = '{}/{}.json'.format(data_dir, base)
    mb_data = {}
    chr_data = []
    maya_dir = '{}/maya'.format(out_dir)
    if not os.path.exists(maya_dir):
        os.makedirs(maya_dir)
    ma_file = '{}/{}.ma'.format(maya_dir, base)
    if not characts:
        return False, "No character found in the scene."
    start_frame = FBSystem().CurrentTake.LocalTimeSpan.GetStart().GetFrame()
    end_frame = FBSystem().CurrentTake.LocalTimeSpan.GetStop().GetFrame()
    mb_fun.bake_all()
    prop_data = []
    ok, result = export_character_fbx(fbx_dir, mapping_dict, log_handle=log_handle)
    if not ok:
        return False, result
    chr_data = result
    ok, result = export_prop_fbx(fbx_dir)
    if not ok:
        return False, u'道具导出失败: {}'.format(result)
    if result:
        prop_data = result

    if chr_data:
        mb_data['character_data'] = chr_data
        mb_data['ma_file'] = ma_file
        mb_data['base_name'] = base
        mb_data['bake'] = bake
        mb_data['start_frame'] = start_frame
        mb_data['end_frame'] = end_frame
        mb_data['prop_data'] = prop_data
        if os.path.exists(ma_file):
            os.remove(ma_file)
        write_json(mb_data, json_file)
        return True, [json_file, ma_file]
    else:
        return False, "No valid character data processed."


def export_character_fbx(out_fbx_dir, mapping_dict, log_handle=None):
    characts = mb_fun.get_all_characters()
    data = []
    if not characts:
        return False, "No character found in the scene."
    for char in characts:
        mb_fun.cancel_selected()
        __exr_data = {}
        rig_node = mb_fun.get_character_rig_node(char)
        if not rig_node:
            continue
        if rig_node.Name in mapping_dict:
            asset_name = str(mapping_dict[rig_node.Name])
        else:
            asset_name = rig_node.LongName.split(':')[0]
            if not asset_name:
                if log_handle:
                    log_handle.error("{} 没有找到绑定的资产名称,请检查".format(rig_node.LongName))
                    return False, "{} 没有找到绑定的资产名称,请检查".format(rig_node.LongName)

        name_space = rig_node.LongName.split(':')[0]
        if name_space == asset_name:
            all_namespaces = mb_fun.get_all_namespaces()
            name_space = rename_same_namespace(name_space, asset_name, all_namespaces)
            if not name_space:
                if log_handle:
                    log_handle.error("命名空间重命名失败: {}".format(rig_node.LongName))
                    return False, "命名空间重命名失败: {}".format(rig_node.LongName)
            char = mb_fun.get_character_by_namespace(name_space)

        ok, publish_path = sg_fun.rig_publish_file_by_asset_name(asset_name)
        if not ok:
            if log_handle:
                log_handle.error("{} 没有找到绑定上传文件,请检查".format(asset_name))
                return False, "{} 没有找到绑定上传文件,请检查".format(asset_name)
        if not publish_path or not os.path.exists(publish_path):
            if log_handle:
                log_handle.error("{} 绑定的上传文件不存在,请检查".format(asset_name))
            return False, "{} 绑定的上传文件不存在,请检查".format(asset_name)
        fbx_file = '{}/{}.fbx'.format(out_fbx_dir, asset_name)
        mb_fun.set_current_character(char)
        mb_fun.bake_to_skeleton(char)
        mb_fun.bake_to_control_rig(char)
        mb_fun.export_character_fbx(char, fbx_file)
        if not os.path.exists(fbx_file):
            if log_handle:
                log_handle.error("导出FBX文件失败: {}".format(fbx_file))
            return False, "导出FBX文件失败: {}".format(fbx_file)
        __exr_data['mb_fbx_path'] = fbx_file
        __exr_data['asset_name'] = asset_name
        __exr_data['publish_path'] = publish_path
        __exr_data['character_name'] = char.LongName

        data.append(__exr_data)
    if not data:
        return False, "没有正确导出任何角色FBX文件"
    return True, data


def export_prop_fbx(out_fbx_dir):
    prop_list = mb_fun.find_modelnull_noeds_by_name('common_item_export_grp')
    fbx_list = []
    error_list = []

    if not prop_list:
        return True, fbx_list
    for prop in prop_list:
        mb_fun.cancel_selected()
        namespace = prop.LongName.split(':')[0]
        fbx_file = '{}/{}.fbx'.format(out_fbx_dir, namespace)

        prop.Selected = True
        child_nodes = mb_fun.get_all_children(prop)
        if not child_nodes:
            continue
        for child in child_nodes:
            child.Selected = True
        result = mb_fun.export_selected_models_fbx(fbx_file)
        if result and os.path.exists(fbx_file):
            fbx_list.append({'name_space': namespace, 'fbx_path': fbx_file})
        else:
            error_list.append(prop.LongName)
    if error_list:
        return False, error_list
    return True, fbx_list


def get_base(file_path):
    base = os.path.basename(file_path)
    name, ext = os.path.splitext(base)
    return name


def write_json(info, path, wtype="w"):
    _path = os.path.dirname(path)
    if not os.path.exists(_path):
        os.makedirs(_path)
    with open(path, wtype) as f:
        json.dump(info, f, indent=4, separators=(',', ':'))
        f.close()
    return True


if __name__ == '__main__':
    mapping_dict = {'YG_Rig': u'YG_Body', 'YS_Rig': u'YS_Body', 'RY_Rig': u'RY_Body', 'PL_Rig': u'PL_Body',
                    'FY_Rig': u'FY_Body_New', 'ST_Rig': u'ST_Body', 'XL_Rig': u'XL_Body'}
