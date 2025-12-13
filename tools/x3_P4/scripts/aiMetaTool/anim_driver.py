# coding=utf-8
import os
import json
from maya import cmds, mel
from maya.api.OpenMaya import *
from maya.api.OpenMayaAnim import *
import re


def read_text_targets(name):
    path = os.path.abspath(__file__+"/../data/%s.txt" % name).replace("\\", "/")
    with open(path, "r") as fp:
        text = fp.read()
    poses = re.split(r"\s", text)
    poses = [str(name) for name in poses if name]
    return poses


def save_json_data(data, name):
    path = os.path.abspath(__file__+"/../data/%s.json" % name).replace("\\", "/")
    with open(path, "w") as fp:
        json.dump(data, fp, indent=4)


def load_json_data(name):
    with open(os.path.abspath(__file__ + "/../data/%s.json" % name), "r") as fp:
        return json.load(fp)


def is_anim_attr(attr):
    typ = cmds.getAttr(attr, type=True)
    if typ not in ["double", "doubleAngle", "doubleLinear"]:
        return False
    if cmds.getAttr(attr, l=1):
        return False
    inputs = cmds.listConnections(attr, s=1, d=0)
    if inputs:
        if not cmds.objectType(inputs[0]).startswith("animCurve"):
            return False
    return True


def get_attrs(controls):
    attrs = []
    for ctrl in controls:
        for attr in cmds.listAttr(ctrl, k=True) or []:
            ctrl_attr = ctrl + "." + attr
            if not is_anim_attr(ctrl_attr):
                continue
            attrs.append(ctrl_attr)
    return attrs


def is_ctrl(ctrl):
    if cmds.objectType(ctrl) == "joint":
        return True
    if not cmds.listRelatives(ctrl, s=1):
        return False
    shapes = cmds.listRelatives(ctrl, s=1)
    shape = shapes[0]
    if cmds.objectType(shape) not in ["nurbsCurve", "nurbsSurface"]:
        return False
    return True


def get_base_pose_data(frames, names, attrs):
    pose_data = {}
    for frame, name in zip(frames, names):
        cmds.currentTime(frame)
        pose_data[name] = [cmds.getAttr(attr) for attr in attrs]
    attrs = [attr.split(":")[-1] for attr in attrs]
    return dict(pose_data=pose_data, attrs=attrs)


def get_attrs_by_set(ctrl_set):
    ctrls = cmds.ls(cmds.sets(ctrl_set, q=1), type="transform", o=1)
    ctrls = list(filter(is_ctrl, ctrls))
    attrs = get_attrs(ctrls)
    return attrs


def create_node(typ, name, parent=None):
    if cmds.objExists(name):
        return name
    if parent is not None:
        return cmds.createNode(typ, n=name, p=parent, ss=True)
    else:
        return cmds.createNode(typ, n=name, ss=True)


def connect_attr(src, dst):
    if not src:
        return
    if not dst:
        return
    if not cmds.objExists(src):
        return
    if not cmds.objExists(dst):
        return
    if cmds.isConnected(src, dst):
        return
    cmds.connectAttr(src, dst, f=1)


def add_attr(node, attr, **kwargs):
    if cmds.objExists(node+"."+attr):
        return
    cmds.addAttr(node, ln=attr, **kwargs)


def init_locator_driver_ctrl(name, poses):
    ctrl = create_node("transform", name, None)
    create_node("locator", ctrl+"Shape", ctrl)
    for pose in poses:
        add_attr(ctrl, pose, at="double", min=0, max=1, k=1)
    return ctrl


def build_bridge_driver(ani_ns, ctrl, pose_data, attrs):
    driven_attrs = [ani_ns+attr for attr in attrs]
    pose_data = dict(pose_data)
    base_values = pose_data.pop("base")
    for driven_attr in driven_attrs:
        bw = driven_attr.replace(":", "_").replace("|", "_").replace(".", "_") + "_BW"
        if cmds.objExists(bw):
            cmds.delete(bw)
    for driven_value_index, driven_attr in enumerate(driven_attrs):
        if not cmds.objExists(driven_attr):
            continue
        pose_values = {}
        for pose, values in pose_data.items():
            if not cmds.objExists("{ctrl}.{pose}".format(**locals())):
                continue
            value = values[driven_value_index]
            value -= base_values[driven_value_index]
            if abs(value) < 0.0001:
                continue
            pose_values[pose] = value
        if not pose_values:
            continue
        bw = driven_attr.replace(":", "_").replace("|", "_").replace(".", "_") + "_BW"
        bw = cmds.createNode("blendWeighted", n=bw)
        cmds.setAttr(bw + ".input[0]", base_values[driven_value_index])
        cmds.setAttr(bw + ".weight[0]", 1)

        for j, (pose, value) in enumerate(pose_values.items()):
            i = j + 1
            cmds.setAttr("{bw}.input[{i}]".format(**locals()), value)
            connect_attr("{ctrl}.{pose}".format(**locals()), "{bw}.weight[{i}]".format(**locals()))
        connect_attr(bw + ".output", driven_attr)


def get_selected_ctrl_set():
    sets = cmds.ls(sl=1, type="objectSet")
    if sets:
        return sets[0]
    return ""


# def get_name_space():
#     selected = cmds.ls(sl=1)
#     if not selected:
#         return ""
#     obj = selected[0]
#     if ":" in obj:
#         return obj.split(":")[0]+":"
#     else:
#         return ""


def get_name_space():
    selected = cmds.ls(sl=1, l=0)
    if not selected:
        return ""
    if ":" in selected[0]:
        return selected[0][:-len(selected[0].split(":")[-1])]
    else:
        return ""

def get_bs_anim_data_by_dir(path):
    anim_curve_data = {}
    for n in os.listdir(path):
        if not n.endswith(".json"):
            continue
        json_path = os.path.join(path, n).replace("\\", "/")
        t = int(n.replace(".json", ""))
        with open(json_path, "r") as fp:
            data = json.load(fp)
        for target, w in data.items():
            fvs = anim_curve_data.setdefault(target, dict(frames=[], values=[]))
            fvs["frames"].append(t)
            fvs["values"].append(w)
    return anim_curve_data


def get_bs_anim_data(path):
    anim_curve_data = {}
    with open(path, "r") as fp:
        data = json.load(fp)
    for t, row in enumerate(data):
        for target, w in row.items():
            fvs = anim_curve_data.setdefault(target, dict(frames=[], values=[]))
            fvs["frames"].append(t+1)
            fvs["values"].append(w)
    return anim_curve_data


def get_anim_curve(attr):
    node, at = attr.split(".")
    cmds.setKeyframe(node, at=at, t=0, v=0)
    typs = ["animCurveTA", "animCurveTU", "animCurveTL"]
    anim_curves = cmds.listConnections(attr, s=1, d=0)
    if not anim_curves:
        return ""
    anim_curve = anim_curves[0]
    if cmds.nodeType(anim_curve) not in typs:
        return ""
    return anim_curve


def api_ls(*names):
    selection_list = MSelectionList()
    for name in names:
        selection_list.add(name)
    return selection_list


def set_attr_anis(attr, frames, values):
    if not cmds.objExists(attr):
        return
    anim_curve = get_anim_curve(attr)
    if not anim_curve:
        return
    mel.eval('cutKey -clear -time ":" '+attr)
    node, at = attr.split(".")
    cmds.setKeyframe(node, at=at, t=frames[0], v=values[0])
    anim_curve = MFnAnimCurve(api_ls(attr).getPlug(0))
    fps = MTime.uiUnit()
    offset = 0
    times = [MTime(f+offset, fps) for f in frames]
    anim_curve.addKeys(times, values)


def find_bs(polygon):
    # 查找 模型 blend shape
    shapes = set(cmds.listRelatives(polygon, s=1, f=1))
    for bs in cmds.ls(cmds.listHistory(polygon), type="blendShape"):
        if cmds.ls(cmds.blendShape(bs, q=1, g=1), l=1)[0] in shapes:
            return bs


def load_bs_anim(path):
    polygon = cmds.ls(sl=1)[0]
    bs = find_bs(polygon)
    if not bs:
        return
    anim_curve_data = get_bs_anim_data(path)
    for target, fvs in anim_curve_data.items():
        set_attr_anis(bs+"."+target, fvs["frames"], fvs["values"])


def re_scene_node(ns, name, node):
    ns = ns[:-1]+"_ctrl"
    if cmds.objExists(ns+"RN"):
        return ns+":"+node
    path = os.path.abspath(__file__ + "/../data/scenes/"+name)
    try:
        cmds.file(path, r=1, ns=ns)
    except RuntimeError:
        pass
    return ns+":"+node


def x6_poses_to_driver(ani_ns, ctrl_set):
    attrs = get_attrs_by_set(ctrl_set)
    frames = list(range(0, 52))
    poses = read_text_targets("arkit_x6_targets")
    poses.insert(0, "base")
    data = get_base_pose_data(frames, poses, attrs)
    driver_ctrl = re_scene_node(ani_ns, "arkit_ctrl.ma", "ARKitDriver")
    build_bridge_driver(ani_ns, driver_ctrl, data["pose_data"], data["attrs"])


def connect_driver_comb(ctrl, comb_data):
    for comb_target, base_targets in comb_data.items():
        comb = ctrl.replace("|", "_") + "_comb_" + comb_target
        if cmds.objExists(comb):
            cmds.delete(comb)
        create_node("combinationShape", comb)
        add_attr(ctrl, comb_target, at="double", min=0, max=1, k=1)
        cmds.setAttr(comb + ".combinationMethod", 1)
        for i, base_target in enumerate(base_targets):
            connect_attr(ctrl + "." + base_target, "{comb}.inputWeight[{i}]".format(**locals()))
        connect_attr(comb + ".outputWeight", ctrl + "." + comb_target)


def get_comb_data_by_targets(comb_targets):
    data = dict()
    for target in comb_targets:
        if "_" not in target:
            continue
        data[target] = list(target.split("_"))
    return data


def re_pose_comb_data(data, comb_data):
    for comb_target, base_targets in comb_data.items():
        if comb_target not in data:
            continue
        for base_target in base_targets:
            data[comb_target] = [comb_v-target_v+base_v for comb_v, target_v, base_v in
                                 zip(data[comb_target], data[base_target], data["base"])]


def x3_arkit_poses_to_driver(ani_ns, ctrl_set):
    attrs = get_attrs_by_set(ctrl_set)
    poses = read_text_targets("arkit_x3_comb_targets")
    poses.insert(0, "base")
    frames = list(range(0, len(poses)))
    comb_data = get_comb_data_by_targets(poses[53:])
    driver_ctrl = init_locator_driver_ctrl(ani_ns+"ARKit52Driver", poses[1:])
    connect_driver_comb(driver_ctrl, comb_data)
    data = get_base_pose_data(frames, poses, attrs)

    re_pose_comb_data(data["pose_data"], comb_data)
    build_bridge_driver(ani_ns, driver_ctrl, data["pose_data"], data["attrs"])


def connect_x6_bs():
    # poses = read_text_targets("arkit_x6_targets")
    # ctrl = init_locator_driver_ctrl("ARKitDriver", poses)
    # cmds.select(ctrl, "head_lod2_mesh")
    src, dst = cmds.ls(sl=1)
    dst_bs = find_bs(dst)
    x6_51_targets = read_text_targets("arkit_x6_targets")
    mh_51_targets = read_text_targets("arkit_mh_targets")
    map_target = {a: b for a, b in zip(mh_51_targets, x6_51_targets)}
    for mh_target in cmds.listAttr(dst_bs + ".weight", m=1):
        if mh_target in map_target:
            connect_attr(src + "." + map_target[mh_target], dst_bs + "." + mh_target)
        else:
            connect_attr(src + "." + map_target[mh_target+"R"], dst_bs + "." + mh_target)


def load_x3_arkit_anim(path):
    ctrl = cmds.ls(sl=1, type="transform")[0]
    x6_51_targets = read_text_targets("arkit_x3_targets")
    mh_51_targets = read_text_targets("arkit_mh_targets")
    anim_curve_48 = get_bs_anim_data(path)
    for x6_target, mh_target in zip(x6_51_targets, mh_51_targets):
        if mh_target in anim_curve_48:
            fvs = anim_curve_48[mh_target]
        else:
            fvs = anim_curve_48[mh_target[:-1]]
        set_attr_anis(ctrl+"."+x6_target, fvs["frames"], fvs["values"])
