import json

from .limit_driver import get_limit_data_by_attrs, get_anim_attrs
from .poses_obj import export_obj
from .anim_solve import get_st_et, api_ls
from maya.api.OpenMaya import *
from maya import cmds
import os
import numpy as np


def export_max_targets(path, polygon, data):
    cmds.select(polygon)
    export_obj(os.path.join(path, "base.obj").replace("\\", "/"))
    print(len(data))
    for row in data:
        cmds.setAttr(row["attr"], row["value"])
        obj_path = os.path.join(path, row["name"].split(":")[-1] + ".obj").replace("\\", "/")
        print(obj_path)
        export_obj(obj_path)
        cmds.setAttr(row["attr"], row["default_value"])


def export_point_anim(polygon, path):
    st, et = get_st_et()
    fn_mesh = MFnMesh(api_ls(polygon).getDagPath(0))
    points_anis = []
    for i in range(st, et+1):
        cmds.currentTime(i)
        points = fn_mesh.getPoints(MSpace.kWorld)
        points_anis.append(points)
    np_points_anis = np.array(points_anis)[:, :, :3]
    dir_path = os.path.dirname(path)
    if not os.path.isdir(dir_path):
        os.makedirs(dir_path)
    np.save(path+".npy", np_points_anis)


def pose_to_ctrl():
    set_name = "base_rig:face_main_set"
    path = r"D:/work/AI_mh/n4/max_objs"
    rig_polygon = "base_rig:Head_geo"
    anim_polygon = "Head_geo"
    data = get_limit_data_by_attrs(get_anim_attrs(cmds.sets(set_name, q=1)))
    data = [row for row in data if row["name"][-6] in "tr"]
    export_max_targets(os.path.join(path, "targets"), rig_polygon, data)
    export_point_anim(anim_polygon, os.path.join(path, "anim"))
    from .aiMetaExe import ai_meta_exe
    ai_meta_exe.solve_max_ctrl(path)
    load_pose_anim()


def load_pose_anim():
    ns = "base_rig:"
    path = r"D:/work/AI_mh/n4/max_objs/ai_result.json"
    with open(path, "r") as fp:
        data = json.load(fp)

    for i, row in enumerate(data):
        cmds.currentTime(i+1)
        attr_values = {}
        ctrls = set()
        for k, v in row.items():
            if abs(v) < 0.002:
                v = 0
            if k[-3:] == "min":
                v *= -1
            attr = k[:-4]
            attr_values.setdefault(attr, 0)
            attr_values[attr] += v
            ctrls.add(attr[:-3])
        for attr, value in attr_values.items():
            attr = ns + attr[:-3] + "." + attr[-2:]
            max_values = sorted([row["value"] for row in get_limit_data_by_attrs([attr])])
            if value > 0:
                value *= abs(max_values[-1])
            elif value < 0:
                value *= abs(max_values[0])
            cmds.setAttr(attr, value)
        cmds.setKeyframe(cmds.ls([ns+ctr for ctr in list(ctrls)]))


jc_map = {
    u'L_dn_lip01_jnt': u'L_lwrLip1_sec_ctrl',
    u'L_dn_lip02_jnt': u'L_lwrLip2_sec_ctrl',
    u'L_dn_lip03_jnt': u'L_cornerLip_sec_ctrl',
    u'L_up_lip01_jnt': u'L_uprLip1_sec_ctrl',
    u'L_up_lip02_jnt': u'L_uprLip2_sec_ctrl',
    u'M_dn_lip01_jnt': u'M_lwrLip_sec_ctrl',
    u'M_up_lip01_jnt': u'M_uprLip_sec_ctrl',
    u'R_dn_lip01_jnt': u'R_lwrLip1_sec_ctrl',
    u'R_dn_lip02_jnt': u'R_lwrLip2_sec_ctrl',
    u'R_dn_lip03_jnt': u'R_cornerLip_sec_ctrl',
    u'R_up_lip01_jnt': u'R_uprLip1_sec_ctrl',
    u'R_up_lip02_jnt': u'R_uprLip2_sec_ctrl',
    u"L_cornerLip_jnt": u"L_cornerLip2_sec_ctrl",
    u"R_cornerLip_jnt": u"R_cornerLip2_sec_ctrl",
    u"jaw_jnt": u"jaw_root_FK_ctrl"
}


def find_ctrl(joint):
    joint = joint.split(":")[-1]
    if joint in jc_map:
        ctrl = jc_map[joint]
        if cmds.ls("*:"+ctrl):
            return cmds.ls("*:"+ctrl)[0]

    ctrl = joint.replace("_jnt", "_sec_ctrl")
    if cmds.ls("*:"+ctrl):
        return cmds.ls("*:"+ctrl)[0]
    ctrl = joint.replace("_jnt", "_ctrl")
    if cmds.ls("*:"+ctrl):
        return cmds.ls("*:"+ctrl)[0]


def auto_parent_connect():
    joints = cmds.ls("sdr_poses:*", type="joint")
    joints = cmds.ls(sl=1, type="joint")
    root = "LushJointCtrlParentGroup"
    if cmds.objExists(root):
        cmds.delete(root)
    cmds.group(n=root, em=1)
    ctrls = []
    for joint in joints:
        if "jnt" not in joint:
            continue
        ctrl = find_ctrl(joint)
        ctrls.append(ctrl)
        try:
            pc = cmds.parentConstraint(joint, ctrl, mo=1)[0]
        except RuntimeError:
            pc = cmds.parentConstraint(joint, ctrl, mo=1, sr=("x", "y", "z"))[0]
        cmds.parent(pc, root)
    cmds.select(ctrls)


def check_max():
    ctrls = cmds.sets("se_ctrl", q=1)
    for i in range(104, 109, 1):
        cmds.currentTime(i+1)
        err_ctrls = []
        for ctrl in ctrls:
            r = cmds.getAttr(ctrl +".r")[0]
            for v in r:
                if abs(v) > 30:
                    err_ctrls.append(ctrl)
        if err_ctrls:
            cmds.select(err_ctrls)
            return


def doit():
    # auto_parent_connect()
    check_max()
    # load_pose_anim()
    # pose_to_ctrl()

