# coding=utf-8
from .anim_ctrl_driver import *


def key_target_name(bs, target, frame, value=1.0):
    if not cmds.objExists(bs + "." + target):
        return
    cmds.setKeyframe(bs + "." + target, v=0, t=frame - 1)
    cmds.setKeyframe(bs + "." + target, v=value, t=frame)
    cmds.setKeyframe(bs + "." + target, v=0, t=frame + 1)


def init_frames(bs, frame):
    for target in cmds.listAttr(bs+".weight", m=1):
        cmds.setKeyframe(bs + "." + target, v=0, t=frame - 1)
        cmds.setKeyframe(bs + "." + target, v=0, t=frame)
        cmds.setKeyframe(bs + "." + target, v=0, t=frame + 1)


def create_node(typ, name, parent=None):
    if cmds.objExists(name):
        return name
    if parent is not None:
        return cmds.createNode(typ, n=name, p=parent, ss=True)
    else:
        return cmds.createNode(typ, n=name, ss=True)


def build_label(name):
    labels = create_node("transform", "labels_group", None)
    label = name+"label"
    if cmds.objExists(label):
        return label
    if cmds.ls("typeMesh*"):
        cmds.delete(cmds.ls("typeMesh*"))
    mel.eval("createTypeCallback()")
    label = cmds.rename("typeMesh1", label)
    typ = cmds.ls(cmds.listHistory(label), type="type")[0]
    values = []
    name = name.lower()
    txt = "61 62 63 64 65 66 67 68 69 6A 6B 6C 6D 6E 6F 70 71 72 73 74 75 76 77 78 79 7A 30 31 32 33 34 35 36 37 38 39 5F"
    abcs = txt.split(" ")
    for i in range(len(name)):
        values.append(abcs["abcdefghijklmnopqrstuvwxyz0123456789_".index(name[i])])
    cmds.setAttr(typ+".textInput", " ".join(values), type="string")
    cmds.select(label)
    cmds.DeleteHistory()
    cmds.parent(label, labels)
    return label


def key_build_label(name, frame, pose_id=None):
    if pose_id is not None:
        name = "P%02d_"% pose_id + name
    label = build_label(name)
    key_target_name(label, "v", frame)


def get_zero_data(targets):
    return {t: 0 for t in targets if "_" not in t}


def auto_key_mh_low_poses():
    targets = read_text_targets("mh_low_targets")
    sdk_data = load_json_data("mh_low_sdk")
    targets = targets[:59] + targets[65:]
    anim_data = []
    label_data = dict()
    for target in targets:
        if target not in ["mouthStickyC", "mouthLipsTogetherU", "mouthLipsTogetherD"]:
            anim_data.append(get_zero_data(targets))
            label_data[len(anim_data)] = "base"
        if target in ["mouthSticky"]:
            anim_data[-1]["jawOpen"] = 0.25
            label_data[len(anim_data)] = "jawOpen25"
        current_data = dict(anim_data[-1])
        if "_" in target:
            for base_target in target.split("_"):
                current_data[base_target] = 1
            print("")
        else:
            current_data[target] = 1
        anim_data.append(current_data)
        label_data[len(anim_data)] = target
    anim_curve_data = {}
    for t, row in enumerate(anim_data):
        for target, w in row.items():
            fvs = anim_curve_data.setdefault(target, dict(frames=[], values=[]))
            fvs["frames"].append(t+1)
            fvs["values"].append(w)
    set_ctrl_anim(anim_curve_data, sdk_data)
    # for frame, target in label_data.items():
    #     key_build_label(target, frame)
    # target_frame = {v: k for k, v in label_data.items()}
    # for target in targets:
    #     print(target_frame[target])
    print ("auto set key")
    bs = find_bs(cmds.ls(sl=1)[0])
    if bs:
        for target, fvs in anim_curve_data.items():
            set_attr_anis(bs+"."+target, fvs["frames"], fvs["values"])


def auto_key_arkit_poses():
    targets = read_text_targets("arkit_x6_targets")
    sdk_data = load_json_data("arkit_sdk")
    anim_data = []
    # label_data = dict()
    mh_targets = read_text_targets("arkit_mh_targets")
    arkit_targets = read_text_targets("arkit_x6_targets")
    real_targets = read_text_targets("arkit_targets")
    label_targets = ["base"]
    for arkit_target, mh_target in zip(arkit_targets, mh_targets):
        if mh_target in real_targets:
            real_target = mh_target
        else:
            real_target = mh_target[:-1]
        current_data = get_zero_data(real_targets)
        current_data[real_target] = 1
        anim_data.append(current_data)
        label_targets.append(arkit_target)
    anim_curve_data = {}
    for t, row in enumerate(anim_data):
        for target, w in row.items():
            fvs = anim_curve_data.setdefault(target, dict(frames=[], values=[]))
            fvs["frames"].append(t+1)
            fvs["values"].append(w)
    set_ctrl_anim(anim_curve_data, sdk_data)
    for frame, target in enumerate(label_targets):
        key_build_label(target, frame)
