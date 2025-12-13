import json
import os.path
import shutil

import pymel.core as pm
from . import bs


def is_ctrl(ctrl):
    if ctrl.getShape() is None:
        return False
    if ctrl.getShape().type() not in ["nurbsCurve", "nurbsSurface"]:
        return False
    return True


def is_rig_attr(attr):
    if attr.isLocked():
        return False
    if not attr.isKeyable():
        return False
    # if attr.inputs():
    #     return False
    return True


def get_rig_attrs(ctrl):
    attr_list = [ctrl.attr(trs+xyz) for xyz in "xzy" for trs in "trs"]  # trs
    for attr in ctrl.listAttr(ud=1, k=1):
        if attr.type() != "double":
            continue
        attr_list.append(attr)
    return filter(is_rig_attr, attr_list)


def get_selected_ctrls():
    return filter(is_ctrl, pm.ls(sl=1, type="transform", o=1))


def find_ctrl_by_name(name):
    for ctrl in filter(is_ctrl, pm.ls(name, "*:"+name, type="transform", o=1)):
        return ctrl


def get_default_ctrls(char, typ):
    path = get_pose_path(char, typ, "base")
    if not os.path.isfile(path):
        return []
    with open(path, "r") as fp:
        data = json.load(fp)
    ctrls = filter(bool, [find_ctrl_by_name(ctrl_data["ctrl_name"]) for ctrl_data in data])
    return ctrls


def get_ctrls(char, typ, pose):
    if pose == "base":
        return get_selected_ctrls()
    else:
        return list(set(get_selected_ctrls()+get_default_ctrls(char, typ)))


def get_pose_data(ctrls):
    data = []
    for ctrl in ctrls:
        ctrl_name = ctrl.name().split("|")[-1].split(":")[-1]
        attr_data = []
        for attr in get_rig_attrs(ctrl):
            attr_name = attr.name().split(".")[-1]
            attr_value = attr.get()
            attr_data.append(dict(
                attr_name=attr_name,
                attr_value=attr_value
            ))
        data.append(dict(
            ctrl_name=ctrl_name,
            attr_data=attr_data
        ))
    return data


def set_pose_data(data):
    for ctrl_data in data:
        ctrl = find_ctrl_by_name(ctrl_data["ctrl_name"])
        if not ctrl:
            continue
        for attr_data in ctrl_data["attr_data"]:
            if not ctrl.hasAttr(attr_data["attr_name"]):
                continue
            ctrl.attr(attr_data["attr_name"]).set(attr_data["attr_value"])


def get_char_root():
    return os.path.abspath("{0}/LushCharPoses".format(os.path.expanduser("~"))).replace("\\", "/")


def get_char_path(char):
    return os.path.abspath("{0}/{1}/".format(get_char_root(), char)).replace("\\", "/")


def get_pose_path(char, typ, pose):
    return os.path.abspath("{0}/{1}/{2}/{3}.json".format(get_char_root(), char, typ, pose)).replace("\\", "/")


def tool_save_pose(char, typ, pose):
    if not all([char, typ, pose]):
        return
    ctrls = get_ctrls(char, typ, pose)
    data = get_pose_data(ctrls)
    path = get_pose_path(char, typ, pose)
    dir_path = os.path.dirname(path)
    if not os.path.isdir(dir_path):
        os.makedirs(dir_path)
    with open(path, "w") as fp:
        json.dump(data, fp, indent=4)


def tool_load_pose(char, typ, pose):
    path = get_pose_path(char, typ, pose)
    if not os.path.isfile(path):
        return
    with open(path, "r") as fp:
        data = json.load(fp)
    set_pose_data(data)


def tool_add_char(char):
    os.makedirs(get_char_path(char))


def tool_del_char(char):
    shutil.rmtree(get_char_path(char))


def tool_convert_bs_all(char, typ):
    from . import bs
    char_path = get_char_path(char) + '/' + typ
    for name in os.listdir(char_path):
        pose, ext = os.path.splitext(name)
        if ext != ".json":
            continue
        if pose == "base":
            continue
        tool_load_pose(char, typ, "base")
        tool_load_pose(char, typ, pose)
        bs.tool_cache_static_target(pose)


def get_x3_npc_face_rom():
    name = "X3NpcFaceRom"
    if pm.objExists(name):
        return pm.PyNode(name)
    else:
        return pm.circle(ch=0, n=name)[0]


def connect(src, dst):
    if not src.isConnectedTo(dst):
        src.connect(dst, f=1)


def find_m_face_plane(name):
    planes = pm.ls("FaceGroup|Planes|%s" % name, type="transform")
    if not planes:
        return
    return planes[0]


def tool_convert_joint_drive(pose_name):
    drive = find_m_face_plane("Driver")
    target = find_m_face_plane("Target")
    if drive is None or target is None:
        return "can not find Drive and Target"
    ctrl = get_x3_npc_face_rom()
    if not ctrl.hasAttr(pose_name):
        ctrl.addAttr(pose_name, min=0, max=1, k=1, at="double")
    bs.cache_static_target(target, drive, pose_name)
    connect(ctrl.attr(pose_name), bs.get_bs(drive).attr(pose_name))


def tool_convert_joint_drive_all(char, typ):
    char_path = get_char_path(char) + '/' + typ
    for name in os.listdir(char_path):
        pose, ext = os.path.splitext(name)
        if ext != ".json":
            continue
        if pose == "base":
            continue
        tool_load_pose(char, typ, pose)
        pm.refresh()
        tool_convert_joint_drive(pose)


x3_npc_rom = [
    u'base',
    u'eyeBlinkLeft',
    u'eyeLookDownLeft',
    u'eyeLookInLeft',
    u'eyeLookOutLeft',
    u'eyeLookUpLeft',
    u'eyeSquintLeft',
    u'eyeWideLeft',
    u'eyeBlinkRight',
    u'eyeLookDownRight',
    u'eyeLookInRight',
    u'eyeLookOutRight',
    u'eyeLookUpRight',
    u'eyeSquintRight',
    u'eyeWideRight',
    u'jawForward',
    u'jawLeft',
    u'jawRight',
    u'jawOpen',
    u'mouthClose',
    u'mouthFunnel',
    u'mouthPucker',
    u'mouthLeft',
    u'mouthRight',
    u'mouthSmileLeft',
    u'mouthSmileRight',
    u'mouthFrownLeft',
    u'mouthFrownRight',
    u'mouthDimpleLeft',
    u'mouthDimpleRight',
    u'mouthStretchLeft',
    u'mouthStretchRight',
    u'mouthRollLower',
    u'mouthRollUpper',
    u'mouthShrugLower',
    u'mouthShrugUpper',
    u'mouthPressLeft',
    u'mouthPressRight',
    u'mouthLowerDownLeft',
    u'mouthLowerDownRight',
    u'mouthUpperUpLeft',
    u'mouthUpperUpRight',
    u'browDownLeft',
    u'browDownRight',
    u'browInnerUp',
    u'browOuterUpLeft',
    u'browOuterUpRight',
    u'cheekPuff',
    u'cheekSquintLeft',
    u'cheekSquintRight',
    u'noseSneerLeft',
    u'noseSneerRight'
]


def anim_to_cache():
    for i, pose_name in enumerate(x3_npc_rom):
        pm.currentTime(i)
        tool_save_pose("Tao", "X3NpcRom", pose_name)


def tool_load_x3_face_rom_anim(path):
    name = "X3NpcFaceRom"
    ctrl = find_ctrl_by_name(name)
    if ctrl is None:
        return pm.warning("can not find " + name)
    with open(path, "r") as fp:
        data = json.load(fp)

    for target_id, property_name in enumerate(data["Property"]):
        target_name = property_name.split(".")[-1]
        if not ctrl.hasAttr(target_name):
            pm.warning(name + " has not " + target_name)
            continue
        for frame_id, values in enumerate(data["FrameValues"]):
            pm.setKeyframe(ctrl, at=target_name, v=values["Values"][target_id]*0.01, t=frame_id+1)
    pm.playbackOptions(min=1, ast=1, aet=len(data["FrameValues"]), max=len(data["FrameValues"]))


def test():
    # anim_to_cache()
    # tool_convert_joint_drive("browDownLeft")
    tool_load_x3_face_rom_anim("D:/work/x3_npc_rom/07-25-17-27_Cha_ST_Daily_01_faceBS.json")

if __name__ == '__main__':
    pass