from maya import cmds
from maya.api.OpenMaya import *
try:
    import numpy as np
except ImportError:
    np = None
import json
import os
import sys
from .anim_driver import load_json_data
from .aiMetaExe import ai_meta_exe
from maya import mel


keep_targets = [
    "eyeLookUpR",
    "eyeLookLeftR",
    "eyeLookLeftL",
    "eyeLookUpL",
    "eyeLookDownR",
    "eyeLookDownL",
    "eyeLookRightR",
    "eyeLookRightL",
    "jawOpen",
    "jawLeft",
    "jawRight",
    "jawFwd",
    "eyeParallelLookDirection",
]


def api_ls(*names):
    selection_list = MSelectionList()
    for name in names:
        selection_list.add(name)
    return selection_list


def get_ctrl_expressions():
    return "CTRL_expressions"


def get_st_et():
    st = cmds.playbackOptions(q=1, min=1)
    et = cmds.playbackOptions(q=1, max=1)
    st, et = int(round(st)), int(round(et))
    return st, et


def get_orig_targets():
    ctrl = get_ctrl_expressions()
    attrs = cmds.listAttr(ctrl, ud=1)
    pres = ["neck", "head", "look", "teeth"]
    attrs = [attr for attr in attrs if not any([attr.startswith(pre) for pre in pres])]
    return attrs


def get_comb_data():
    with open(os.path.abspath(__file__ + "/../data/targets_comb_data.json"), "r") as fp:
        return json.load(fp)


def get_base_orig_anis():
    ctrl = get_ctrl_expressions()
    data = {attr: cmds.getAttr(ctrl + "." + attr) for attr in get_orig_targets()}
    return data


def get_x3_91_orig_anis():
    ctrl = get_ctrl_expressions()
    data = {attr: cmds.getAttr(ctrl + "." + attr) for attr in get_orig_targets()}
    data["jawOpen_jawOpenExtreme"] = min(data["jawOpen"], data["jawOpenExtreme"])
    data["jawOpen"] -= data["jawOpen_jawOpenExtreme"]
    comb_data = load_json_data("mh_91_comb_data")
    for comb_target, base_targets in comb_data.items():
        values = [data.get(base_target, 0) for base_target in base_targets]
        data[comb_target] = sum(values)/len(values)
    return data


def export_polygon_anis(path, get_orig_anis):
    path = path.replace("\\", "/")
    ctrl = get_ctrl_expressions()
    polygon = "head_lod2_mesh"
    st, et = get_st_et()
    fn_mesh = MFnMesh(api_ls(polygon).getDagPath(0))
    points_anis = []
    keep_weight_anis = []
    orig_weight_anis = []
    for i in range(st, et+1):
        cmds.currentTime(i)
        points = fn_mesh.getPoints(MSpace.kWorld)
        points_anis.append(points)
        keep_weight_anis.append({attr: cmds.getAttr(ctrl + "." + attr) for attr in keep_targets})
        orig_weight_anis.append(get_orig_anis())
    np_points_anis = np.array(points_anis)[:, :, :3]
    dir_path = os.path.dirname(path)
    if not os.path.isdir(dir_path):
        os.makedirs(dir_path)
    np.save(path+".npy", np_points_anis)
    anim_info = dict(
        keep_weight_anis=keep_weight_anis,
        st=st,
        et=et,
        fps=cmds.currentUnit(query=True, time=True),
        python_version=sys.version,
        maya_version=cmds.about(v=1),
        orig_weight_anis=orig_weight_anis,
    )
    with open(path+".json", "w") as fp:
        json.dump(anim_info, fp, indent=4)


def export_base_anis(path, _et=None):
    mel.eval('cutKey -clear -time ":" CTRL_C_jaw_openExtreme')
    cmds.setAttr("CTRL_C_jaw_openExtreme.translateY", 0)
    path = path.replace("\\", "/")
    ctrl = get_ctrl_expressions()
    polygon = "head_lod2_mesh"
    st, et = get_st_et()
    if _et is not None:
        et = _et
    fn_mesh = MFnMesh(api_ls(polygon).getDagPath(0))
    points_anis = []
    keep_weight_anis = []
    orig_weight_anis = []
    for i in range(st, et+1):
        cmds.currentTime(i)
        points = fn_mesh.getPoints(MSpace.kWorld)
        points_anis.append(points)
        keep_weight_anis.append({attr: cmds.getAttr(ctrl + "." + attr) for attr in keep_targets})
        orig_weight_anis.append(get_base_orig_anis())
    np_points_anis = np.array(points_anis)[:, :, :3]
    dir_path = os.path.dirname(path)
    if not os.path.isdir(dir_path):
        os.makedirs(dir_path)
    np_points_anis = np.array(np_points_anis, dtype=np.float32)
    np.save(path+".npy", np_points_anis)
    anim_info = dict(
        keep_weight_anis=keep_weight_anis,
        st=st,
        et=et,
        fps=cmds.currentUnit(query=True, time=True),
        python_version=sys.version,
        maya_version=cmds.about(v=1),
        orig_weight_anis=orig_weight_anis,
    )
    with open(path+"_base.json", "w") as fp:
        json.dump(anim_info, fp, indent=4)


def x3_91_solve(path):
    path = os.path.splitext(path)[0]
    export_polygon_anis(path, get_x3_91_orig_anis)
    ai_meta_exe.solve_x3_91_bs(path)


def convert_base_anim(path, convert_fn):
    path = os.path.splitext(path)[0].replace("\\", "/")
    base_path = path + "_base.json"
    with open(base_path, "r") as fp:
        anim_info = json.load(fp)
    for row in anim_info["orig_weight_anis"]:
        convert_fn(row)
    with open(path+".json", "w") as fp:
        json.dump(anim_info, fp, indent=4)


def convert_low_data(data):
    comb_data = load_json_data("mh_low_comb")
    comb_data["mouthLipsTogetherD"] = ["mouthLipsTogetherDR", "mouthLipsTogetherDL"]
    comb_data["mouthLipsTogetherU"] = ["mouthLipsTogetherUR", "mouthLipsTogetherUL"]
    comb_data["mouthLowerLipRollIn"] = [u'mouthLowerLipRollInR', u'mouthLowerLipRollInL']
    comb_data["mouthUpperLipRollIn"] = [u'mouthUpperLipRollInR', u'mouthUpperLipRollInL']
    for comb_target, base_targets in comb_data.items():
        if isinstance(base_targets, list):
            values = [data.get(base_target, 0) for base_target in base_targets]
            data[comb_target] = sum(values)/len(values)
        elif isinstance(base_targets, dict):
            values = [data.get(base_target, 0) for base_target in base_targets.keys()]
            data[comb_target] = sum(values)/len(values)
    data["mouthLowerLipBite"] += data["mouthLowerLipRollIn"]
    data["mouthUpperLipBite"] += data["mouthUpperLipRollIn"]


tongue_convert_data = dict(
    tongueRollUp=dict(
        tongueDown=0.2,
        tongueTipUp=0.8,
    ),
    tongueRollDown=dict(
        tonguePress=0.5,
        tongueTipDown=0.5,
    ),
    tongueUp=dict(
        tonguePress=0.6,
        tongueTipUp=0.4,
    )
)


def convert_tongue_data(path):
    path = os.path.splitext(path)[0].replace("\\", "/")
    base_path = path + "_base.json"
    with open(base_path, "r") as fp:
        orig_weight_anis = json.load(fp)["orig_weight_anis"]
    solve_path = path + "_ai_result.json"
    with open(solve_path, "r") as fp:
        solve_weight_anis = json.load(fp)
    for orig, solve in zip(orig_weight_anis, solve_weight_anis):
        tongue_targets = ["tongueDown", "tonguePress", "tongueTipDown", "tongueTipUp"]
        data = {k: orig.get(k, 0) for k in tongue_targets}
        for eff, target_values in tongue_convert_data.items():
            additive = orig.get(eff, 0)
            for target, value in target_values.items():
                data[target] += value*additive
        for k, v in data.items():
            data[k] = min(max(v, 0.0), 1.0)
        solve.update(data)
    with open(solve_path, "w") as fp:
        json.dump(solve_weight_anis, fp, indent=4)


def scale_anim():
    st, et = get_st_et()
    for i in range(st, et+1):
        cmds.currentTime(i)
        for ctrl in cmds.ls(sl=1):
            for attr in cmds.listAttr(ctrl, k=1):
                if attr not in ["translateX", "translateY"]:
                    continue
                node_attr = ctrl + "." + attr
                try:
                    cmds.setAttr(node_attr, cmds.getAttr(node_attr)*1.3)
                except RuntimeError:
                    pass
            cmds.setKeyframe(ctrl)


def sub_low_solve(path):
    convert_base_anim(path, convert_low_data)
    # sub = ai_meta_exe.solve_mh_low(path)
    # sub.wait()
    convert_tongue_data(path)


def clear_orig_detail():
    ctrls = [u'CTRL_R_mouth_thicknessD', u'CTRL_L_mouth_thicknessD', u'CTRL_R_mouth_thicknessU',
             u'CTRL_L_mouth_thicknessU', u'CTRL_R_mouth_pushPullU', u'CTRL_R_mouth_pushPullD',
             u'CTRL_L_mouth_pushPullD', u'CTRL_L_mouth_pushPullU', u"CTRL_C_jaw_openExtreme"]
    for ctrl in ctrls:
        mel.eval('cutKey -clear -time ":" %s' % ctrl)
        cmds.setAttr(ctrl+".translateY", 0)


def convert_x6_data(data):
    comb_data = load_json_data("arkit_comb")
    comb_data["mouthLipsTogether"] = ["mouthLipsTogetherUR", "mouthLipsTogetherUL", "mouthLipsTogetherDR",
                                      "mouthLipsTogetherDL"]
    comb_data["mouthStretchLipsCloseR"] = ["mouthStretchR"]
    comb_data["mouthStretchLipsCloseL"] = ["mouthStretchL"]
    for comb_target, base_targets in comb_data.items():
        if isinstance(base_targets, list):
            values = [data.get(base_target, 0) for base_target in base_targets]
            data[comb_target] = sum(values)/len(values)
        elif isinstance(base_targets, dict):
            values = [data.get(base_target, 0) for base_target in base_targets.keys()]
            data[comb_target] = sum(values)/len(values)
    return data


def rename_file(src, dst):
    if not os.path.isfile(src):
        return
    if os.path.isfile(dst):
        os.remove(dst)
    os.rename(src, dst)


def arkit_solve(path):
    path = os.path.splitext(os.path.splitext(path)[0])[0]
    clear_orig_detail()
    export_base_anis(path)
    convert_base_anim(path, convert_x6_data)
    sub = ai_meta_exe.solve_x6_52_bs(path)
    sub.wait()
    os.remove(path+".json")
    os.remove(path+".npy")
    os.remove(path+"_base.json")
    rename_file(path+"_ai_result.json", path+"_arkit.json")


def solve_mh_low(path):
    path = os.path.splitext(os.path.splitext(path)[0])[0]
    clear_orig_detail()
    export_base_anis(path)
    convert_base_anim(path, convert_low_data)
    sub = ai_meta_exe.solve_mh_low(path)
    sub.wait()
    convert_tongue_data(path)
    os.remove(path+".json")
    os.remove(path+".npy")
    os.remove(path+"_base.json")
    rename_file(path+"_ai_result.json", path+"_aiMeta.json")





