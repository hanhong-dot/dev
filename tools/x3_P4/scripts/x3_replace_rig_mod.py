# coding=utf-8
import os
from maya import cmds


def get_skin_cluster(polygon_name):
    shapes = cmds.listRelatives(polygon_name, s=1, f=1)
    for skin_cluster in cmds.ls(cmds.listHistory(polygon_name), type="skinCluster"):
        for shape in cmds.skinCluster(skin_cluster, q=1, geometry=1):
            for long_shape in cmds.ls(shape, l=1):
                if long_shape in shapes:
                    return skin_cluster


def copy_weight(src, dst):
    skin_cluster = get_skin_cluster(src)
    joints = cmds.skinCluster(skin_cluster, q=1, influence=1)
    cmds.skinCluster(joints, dst, tsb=1)
    cmds.select(src, dst)
    cmds.CopySkinWeights()


def get(uid):
    return cmds.ls(uid, l=1)[0]


def replace_mod(src_uid, dst_uid):
    cmds.rename(get(dst_uid), "temp_dst_"+get(dst_uid).split("|")[-1])
    parent = cmds.listRelatives(get(dst_uid), p=1, f=1)[0]
    cmds.parent(get(src_uid), parent)
    children = cmds.listRelatives(parent)
    index = children.index(get(dst_uid).split("|")[-1]) + 1
    cmds.reorder(get(dst_uid), r=index)
    cmds.rename(get(src_uid), get(dst_uid).split("|")[-1][9:])
    copy_weight(get(dst_uid), get(src_uid))
    cmds.delete(get(dst_uid))


def replace_rig_mod(mod_path, rig_path, result_path):
    assert os.path.isfile(mod_path), "can nof find " + mod_path
    assert os.path.isfile(rig_path), "can nof find " + rig_path

    typ = "mayaBinary" if mod_path.endswith(".mb") else "mayaAscii"
    cmds.file(mod_path, o=1, f=1, typ=typ, ignoreVersion=True)

    cmds.select(all=1)
    all_ids = cmds.ls(sl=1, type="transform", uid=1)

    mesh_list = cmds.ls(type="mesh", l=1) or []
    polygon_list = [cmds.listRelatives(mesh, p=1, f=1) or [] for mesh in mesh_list]
    polygon_list = sum(polygon_list, [])
    path_ids = []
    for path in polygon_list:
        path_ids.append([path[1:], cmds.ls(path, uid=1)[0]])
    assert len(polygon_list) > 0, "can not find mod polygon"
    for uid in all_ids:
        cmds.rename(get(uid), "temp_src_" + get(uid).split("|")[-1])

    typ = "mayaBinary" if rig_path.endswith(".mb") else "mayaAscii"
    cmds.file(rig_path, i=1, typ=typ, ns=":", ignoreVersion=True)
    for find_path, src_uid in path_ids:
        dst_ids = cmds.ls(find_path, uid=1) or []
        assert len(dst_ids) == 1, "can not find rig " + find_path
        dst_uid = dst_ids[0]
        replace_mod(src_uid, dst_uid)
    cmds.delete(cmds.ls(all_ids))
    cmds.select(all=1)
    cmds.select(cmds.ls(sl=1, type="transform"))
    dir_path = os.path.dirname(result_path)
    if not os.path.isdir(dir_path):
        os.makedirs(dir_path)
    typ = "mayaBinary" if result_path.endswith(".mb") else "mayaAscii"
    cmds.file(result_path, pr=1, es=1, f=1, typ=typ)


def try_replace_rig_mod(mod_path, rig_path, result_path):
    try:
        replace_rig_mod(mod_path, rig_path, result_path)
    except Exception as e:
        return False, e
    return True, None


def test():
    replace_rig_mod(
        mod_path="D:/work/x3_replace_sg/common_droplet_001.drama_mdl.v001.ma",
        rig_path="D:/work/x3_replace_sg/common_droplet_001.drama_rig.v001.ma",
        result_path="D:/work/x3_replace_sg/result.ma",
    )
