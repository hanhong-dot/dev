from maya import cmds
from .bs import *
import os
from .anim_driver import *

def load_objs_to_bs(obj_dir):
    polygon = cmds.ls(sl=1)[0]
    bs = get_bs(polygon)
    for name in os.listdir(obj_dir):
        if not name.endswith(".obj"):
            continue
        obj_path = os.path.join(obj_dir, name).replace("\\", "/")
        name = name.replace(".obj", "")
        # if name == "base":
        #     continue
        tops = set(cmds.ls("|*", type="transform"))
        cmds.file(obj_path, i=1, type="OBJ", iv=1, ns=":")
        obj_geos = set(cmds.ls("|*", type="transform")) - tops
        if not obj_geos:
            continue
        if name.isdigit():
            name = "f" + name
        obj_geo = obj_geos.pop()
        target = cmds.rename(obj_geo, name)
        re_real_target(polygon, bs, target, name)
        cmds.delete(target)


def reset_bs(bs):
    for attr in cmds.listAttr(bs+".weight", m=1):
        cmds.setAttr(bs + "." + attr, 0)


def export_obj(path):
    dir_name = os.path.dirname(path)
    if not os.path.isdir(dir_name):
        os.makedirs(dir_name)
    options = "groups=1;ptgroups=1;materials=0;smoothing=1;normals=0"
    cmds.file(path, options=options, pr=1, es=1, type="OBJexport", f=1)


def export_bs_obj(path):
    polygon = cmds.ls(sl=1)[0]
    bs = find_bs(polygon)
    bs = "target_polygon_bs"
    reset_bs(bs)
    name = "base"
    obj_path = os.path.join(path, name + ".obj").replace("\\", "/")
    export_obj(obj_path)
    for name in cmds.listAttr(bs+".weight", m=1):
        cmds.setAttr(bs+"."+name, 1)
        obj_path = os.path.join(path, name+".obj").replace("\\", "/")
        export_obj(obj_path)
        cmds.setAttr(bs+"."+name, 0)


def find_sdk_1(uu):
    driver_values = cmds.keyframe(uu, fc=1, q=1, index=(0, 2))
    driven_values = cmds.keyframe(uu, vc=1, q=1, index=(0, 2))
    sdk_values = list(zip(driver_values, driven_values))
    sdk_values.sort(key=lambda x: x[1])
    return sdk_values[-1][0]


def get_bridge_sdk_data():
    bridge = "CTRL_expressions"
    sdk_data = load_json_data("arkit_sdk")

    base_target_ctrl_data = {}
    for base_target in cmds.listAttr(bridge, ud=1):
        attr = bridge + '.' + base_target
        uu = cmds.listConnections(attr, s=1, d=0)
        if not uu:
            continue
        uu = uu[0]
        if cmds.nodeType(uu) != "animCurveUU":
            continue
        driver_attr = cmds.listConnections(uu, s=1, d=0, p=1)[0]
        driver_value = find_sdk_1(uu)
        base_target_ctrl_data[base_target] = {driver_attr: driver_value}
        if "eyeLook" not in base_target:
            continue
        driver_attr = sdk_data[base_target]["ctrl"] + "." + sdk_data[base_target]["attr"]
        driver_attr = driver_attr.replace(".tx", ".translateX")
        driver_attr = driver_attr.replace(".ty", ".translateY")
        driver_value = sdk_data[base_target]["ts"][-1]
        base_target_ctrl_data[base_target] = {driver_attr: driver_value}
    return base_target_ctrl_data


def get_speak_data(targets, base_data, comb_data):
    speak_data = {}
    for target in targets:
        if target not in comb_data:
            speak_data[target] = base_data[target]
        elif isinstance(comb_data[target], list):
            ctrl_data = {}
            for comb_target in comb_data[target]:
                for t in comb_target.split("_"):
                    ctrl_data.update(base_data[t])
            speak_data[target] = ctrl_data
        elif isinstance(comb_data[target], dict):
            ctrl_data = {}
            for comb_target, v in comb_data[target].items():
                for t in comb_target.split("_"):
                    if t == "jawOpen":
                        continue
                    for ct, cv in base_data[t].items():
                        ctrl_data[ct] = cv*v
            speak_data[target] = ctrl_data
    return speak_data


def get_bridge_data():
    base_data = get_bridge_sdk_data()
    # targets = read_text_targets("mh_low_targets")[:55]
    # comb_data = load_json_data("mh_low_comb")
    # save_json_data(get_speak_data(targets, base_data, comb_data), "aiMetaCtrlData")

    targets = read_text_targets("arkit_targets")
    comb_data = load_json_data("arkit_comb")
    save_json_data(get_speak_data(targets, base_data, comb_data), "arKitCtrlData")



def doit():
    # load_objs_to_bs(r"C:/Users/mengya/Documents/maya/scripts/lushTools/aiMetaTool/aiMetaExe/config/data/low/targets")
    # export_bs_obj(r"D:\work\ai_ue_speak\solve_bs_anim_new\aiMeta55BS")
    # load_objs_to_bs(r"D:\work\ai_ue_speak\solve_bs_anim_new\aiMeta55BS")
    get_bridge_data()

