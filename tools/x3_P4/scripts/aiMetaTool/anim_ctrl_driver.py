import os

from .anim_driver import *


def load_mh_ctrl(ns, name):
    ns = ns[:-1]+"_MhPlane"
    if cmds.objExists(ns+"RN"):
        return ns+":QMeta_expressions"
    path = os.path.abspath(__file__ + "/../data/"+name)
    cmds.file(path, r=1, ns=ns)
    return ns+":QMeta_expressions"


def sub_data(data, sub_poses):
    new_data = {}
    for pose1, pose2 in zip(sub_poses, sub_poses[1:]):
        if not all([pose in data for pose in [pose1, pose2, "base"]]):
            continue
        new_data[pose2] = [base_v+v2-v1 for base_v, v1, v2 in zip(data["base"], data[pose1], data[pose2])]
    data.update(new_data)


def x3_91_poses_to_driver(ani_ns, ctrl_set):
    driver_ctrl = load_mh_ctrl(ani_ns, "QMetaPlaneCtrlFinal.ma")
    frames = read_text_targets("mh_91_frames")
    frames = [int(f) for f in frames]
    poses = read_text_targets("mh_91_targets")
    frames += [1, 166, 169]
    poses += ["base", "jawOpen50", "jawOpen25"]
    attrs = get_attrs_by_set(ctrl_set)
    data = get_base_pose_data(frames, poses, attrs)
    sub_data(data["pose_data"], ["jawOpen50", "mouthLowerLipTowardsTeeth", "mouthUpperLipTowardsTeeth"])
    sub_data(data["pose_data"], ["jawOpen25", "mouthStickyDOUT", "mouthStickyDIN", "mouthStickyDC",
                                 "mouthStickyUOUT", "mouthStickyUIN", "mouthStickyUC"])
    build_bridge_driver(ani_ns, driver_ctrl, data["pose_data"], data["attrs"])


def bs_weights_to_ctrl_values(weights, value):
    return [value*w for w in weights]


def set_ctrl_anim(bs_curve_data, sdk_data):
    ns = get_name_space()
    attr_curve_data = {}
    for target, fvs in bs_curve_data.items():
        if target not in sdk_data:
            continue
        attr = sdk_data[target]["ctrl"]+"."+sdk_data[target]["attr"]
        values = bs_weights_to_ctrl_values(fvs["values"], sdk_data[target]["ts"][1])
        if attr in attr_curve_data:
            values = [v1 + v2 for v1, v2 in zip(attr_curve_data[attr]["values"], values)]
        attr_curve_data[attr] = dict(values=values, frames=fvs["frames"])
    for attr, fvs in attr_curve_data.items():
        set_attr_anis(ns + attr, fvs["frames"], fvs["values"])
    et = len(list(attr_curve_data.items())[0][1]["frames"])
    st = 1
    cmds.playbackOptions(ast=st, aet=et, min=st, max=et)


def load_ctrl_anim(path, sdk_data):
    set_ctrl_anim(get_bs_anim_data(path), sdk_data)


def load_mh_low_ctrl_anim(path):
    load_ctrl_anim(path, load_json_data("mh_low_sdk"))


def load_x6_anim(path):
    load_ctrl_anim(path, load_json_data("arkit_sdk"))


def filter_frame_poses(frames, poses, ctrl_set):
    ctrls = cmds.sets(ctrl_set, q=1)
    ts = cmds.keyframe(ctrls, q=1)
    ts = list(set(ts))
    ts = set([int(round(t)) for t in ts])
    new_frames, new_poses = [], []
    for frame, pose in zip(frames, poses):
        if frame not in ts:
            continue
        new_frames.append(frame)
        new_poses.append(pose)
    return new_frames, new_poses


def x3_55_poses_to_driver(ani_ns, ctrl_set):
    driver_ctrl = re_scene_node(ani_ns, "mh_low_ctrl_demo.ma", "QMeta_expressions")
    frames = read_text_targets("mh_low_frames")
    frames = [int(f) for f in frames]
    poses = read_text_targets("mh_low_targets")
    frames += [1, 81]
    poses += ["base",  "jawOpen25"]
    attrs = get_attrs_by_set(ctrl_set)
    frames, poses = filter_frame_poses(frames, poses, ctrl_set)
    data = get_base_pose_data(frames, poses, attrs)
    sub_data(data["pose_data"], ["jawOpen", "mouthLipsTogetherU", "mouthLipsTogetherD"])
    sub_data(data["pose_data"], ["jawOpen25", "mouthSticky", "mouthStickyC"])
    comb_data = get_comb_data_by_targets(poses)
    re_pose_comb_data(data["pose_data"], comb_data)
    build_bridge_driver(ani_ns, driver_ctrl, data["pose_data"], data["attrs"])


def test():
    x3_55_poses_to_driver("ST_BODY_drama_rig1:", "face_ctrl_set")
