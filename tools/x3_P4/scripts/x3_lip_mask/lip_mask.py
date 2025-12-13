import json
import os.path

import pymel.core as pm


def load_mask_weight():
    path = os.path.abspath(__file__+"/../data/mask.json")
    with open(path, "r") as fp:
        data = json.load(fp)
    return {row["name"].split("/")[-1]: row["weight"] for row in data}

def get_ani_bind_dst(name):
    name = name.split("/")[-1]
    ani, bind, dst = None, None, None
    joints = pm.ls(name, "*:"+name, "*:*:"+name, "*:*:*:"+name)
    for joint in joints:
        if joint.name().startswith("BindPose"):
            bind = joint
        elif joint.name().startswith("BaseAni"):
            ani = joint
        else:
            dst = joint
    return ani, bind, dst


def follow_head():
    name = "Head_M_spare"
    ani, bind, dst = get_ani_bind_dst(name)
    if ani is None or bind is None or dst is None:
        return None, None, None
    pm.parentConstraint(ani, bind)


def blend_link(name, weight):
    name = name.split("/")[-1]
    ani, bind, dst = get_ani_bind_dst(name)
    if ani is None or bind is None or dst is None:
        return
    pm.cutKey(dst, clear=1, time=":")
    pc = pm.parentConstraint(bind, ani, dst)
    w1, w2 = pm.parentConstraint(pc, q=1, wal=1)
    pm.parent(pc, ani)
    w1.set(weight)
    w2.set(1-weight)
    return ani, bind, dst


def remove_lip_ani(anim_path, bind_pose_path):
    pm.openFile(anim_path, f=1, type="FBX")
    base_path, _ = os.path.splitext(anim_path)
    new_anim_path = base_path + "_remove_lip.fbx"
    pm.renameFile(new_anim_path, f=1)
    pm.createReference(bind_pose_path, f=1, type="FBX", ns="BindPose")
    pm.createReference(anim_path, f=1, type="FBX", ns="BaseAni")
    path = os.path.abspath(__file__+"/../data/mask.json")
    with open(path, "r") as fp:
        data = json.load(fp)

    follow_head()
    ani_joints = []
    dst_joints = []
    for row in data:
        ani, bind, dst = blend_link(**row)
        if ani:
            ani_joints.append(ani)
            dst_joints.append(dst)
    times = pm.keyframe(ani_joints, q=1, tc=1)
    start = int(round(min(times)))
    end = int(round(max(times)))
    pm.bakeResults(dst_joints, t=(start, end), sampleBy=1)
    pm.delete(pm.ls(type="parentConstraint"))
    pm.mel.file(anim_path, rr=1)
    pm.mel.file(bind_pose_path, rr=1)
    pm.exportAll(new_anim_path, type="FBX export", f=1)


def remove_all_lip_amin(anim_paths, bind_pose_path):
    for anim_path in anim_paths:
        remove_lip_ani(anim_path, bind_pose_path)


def doit():
    bind_pose_path = "C:/Users/mengya/Documents/maya/scripts/lushTools/x3_lip_mask/data/RY_Base_Head.fbx"
    anim_paths = ["D:/work/x3_face_remove_lip/anim2.fbx"]
    remove_all_lip_amin(anim_paths, bind_pose_path)
