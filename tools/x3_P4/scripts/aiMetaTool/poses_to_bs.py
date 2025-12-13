from maya import cmds
import os
import json
import re
from . import bs

def load_json_data(name):
    with open(os.path.abspath(__file__ + "/../data/%s.json" % name), "r") as fp:
        return json.load(fp)


def is_polygon(polygon):
    shapes = cmds.listRelatives(polygon, s=1, f=1)
    if not shapes:
        return False
    if cmds.objectType(shapes[0]) != "mesh":
        return False
    return True


def get_selected_polygons():
    polygons = list(filter(is_polygon, cmds.ls(sl=1, type="transform", l=1)))
    return polygons


def read_text_targets(name):
    path = os.path.abspath(__file__+"/../data/%s.txt" % name).replace("\\", "/")
    with open(path, "r") as fp:
        text = fp.read()
    poses = re.split(r"\s", text)
    poses = [str(name) for name in poses if name]
    return poses


def get_comb_data_by_targets(comb_targets):
    data = dict()
    for target in comb_targets:
        if "_" not in target:
            continue
        data[target] = list(target.split("_"))
    return data


def re_comb_data(dup_polygons, comb_data):
    for dup_polygon in dup_polygons:
        _bs = bs.get_bs(dup_polygon)
        for comb, base_targets in comb_data.items():
            cmds.setAttr(_bs+"."+comb, 1)
            for base_target in base_targets:
                cmds.setAttr(_bs + "." + base_target, -1)
            temp = cmds.duplicate(dup_polygon)[0]
            cmds.setAttr(_bs+"."+comb, 0)
            for base_target in base_targets:
                cmds.setAttr(_bs + "." + base_target, 0)
            bs.re_real_target(dup_polygon, _bs, temp, comb)
            cmds.delete(temp)


def ai_meta_convert_sel_blend_shape():
    polygons = get_selected_polygons()
    frames = read_text_targets("mh_low_frames")
    frames = [int(f) for f in frames]
    poses = read_text_targets("mh_low_targets")
    frames += [1, 81]
    poses += ["base",  "jawOpen25"]
    dup_polygons = []
    cmds.currentTime(0)

    for polygon in polygons:
        dup_polygon = cmds.duplicate(polygon, n=polygon.split(":")[-1])[0]
        dup_polygons.append(dup_polygon)
    for frame, pose in zip(frames, poses):
        cmds.currentTime(frame)
        for polygon, dup_polygon in zip(polygons, dup_polygons):
            temp = cmds.duplicate(polygon)[0]
            _bs = bs.get_bs(dup_polygon)
            bs.re_real_target(dup_polygon, _bs, temp, pose)
            cmds.delete(temp)
    cmds.currentTime(0)
    re_comb_data(dup_polygons, get_comb_data_by_targets(poses))
    re_comb_data(dup_polygons, {'mouthLipsTogetherD': ['mouthLipsTogetherU']})
    re_comb_data(dup_polygons, {'mouthLipsTogetherU': ['jawOpen']})
    re_comb_data(dup_polygons, {'mouthStickyC': ['mouthSticky']})
    re_comb_data(dup_polygons, {'mouthSticky': ['jawOpen25']})
    return dup_polygons


def convert_comb():
    polygons = get_selected_polygons()
    dup_polygons = []
    for polygon in polygons:
        dup_polygon = cmds.duplicate(polygon, n="dup_"+polygon)[0]
        _bs = cmds.blendShape(polygon, dup_polygon)[0]
        cmds.blendShape(_bs, e=1, w=(0, 1))
        dup_polygons.append(dup_polygon)
    if len(dup_polygons) == 1:
        return dup_polygons[0]
    comb_polygon = cmds.polyUnite(dup_polygons, ch=1, n="Head_Comb_Geo")[0]
    cmds.select(comb_polygon)
    return comb_polygon


def ai_meta_convert_blend_shape():
    polygons = get_selected_polygons()
    comb = convert_comb()
    joints = []
    for polygon in polygons:
        joints += cmds.skinCluster(polygon, q=1, inf=1)
    joints = cmds.ls(joints)
    dup_polygons = ai_meta_convert_sel_blend_shape()
    cmds.select(comb)
    cmds.DeleteHistory()
    cmds.delete(comb)
    cmds.currentTime(1)
    cmds.skinCluster(joints, dup_polygons[0])
    cmds.select(polygons, dup_polygons)
    cmds.CopySkinWeights()


def doit():
    # cmds.select("ST001C:RY_Head")
    ai_meta_convert_blend_shape()
    print("comb")
    # ai_meta_convert_blend_shape()
