# coding:utf-8
from .anim_driver import *


def get_base_sdk_data(attr):
    if not cmds.objExists(attr):
        return
    uu = cmds.listConnections(attr, s=1, d=0) or []
    if len(uu) != 1:
        return
    uu = uu[0]
    attr = cmds.listConnections(uu, s=1, d=0, p=1)
    if len(attr) != 1:
        return
    attr = attr[0]
    ctrl, attr = attr.split(".")
    attr = cmds.attributeQuery(attr, sn=1, n=ctrl)
    ts = cmds.keyframe(uu, fc=1, q=1, index=(0, 2))
    vs = cmds.keyframe(uu, q=1, vc=1, index=(0, 2))
    tvs = list(zip(ts, vs))
    tvs.sort(key=lambda x: x[1])
    ts, vs = zip(*tvs)
    ts, vs = list(ts), list(vs)
    return dict(ctrl=ctrl, attr=attr, ts=ts, vs=vs)


def find_target_name():
    bridge = "CTRL_expressions"
    for target_name in cmds.listAttr(bridge, ud=1):
        value = cmds.getAttr(bridge + "." + target_name)
        if value > 0.9:
            return target_name


def get_eye_data():
    data = dict()
    ctrls = ['CTRL_R_eye', 'CTRL_L_eye']
    for ctrl in ctrls:
        for attr in ["tx", "ty"]:
            for value in [+1, -1]:
                cmds.setAttr(ctrl+"."+attr, value)
                target_name = find_target_name()
                cmds.setAttr(ctrl + "." + attr, 0)
                data[target_name] = dict(ctrl=ctrl, attr=attr, ts=[0.0, value], vs=[0.0, 1.0])
    return data


def get_q_meta_bridge():
    if cmds.objExists("QMeta_expressions"):
        cmds.delete("QMeta_expressions")
    cmds.group(em=1, n="QMeta_expressions", p="GRP_faceGUI")
    return "QMeta_expressions"


def is_ctrl(node):
    if not node:
        return False
    if not cmds.objectType(node) == "transform":
        return False
    shapes = cmds.listRelatives(node, s=1)
    if not shapes:
        return False
    if not cmds.objectType(shapes[0]) == "nurbsCurve":
        return False
    return True


def get_sdk_data():
    with open(os.path.abspath(__file__ + "/../targets_sdk.json"), "r") as fp:
        return json.load(fp)


def save_mutex_data():
    sdk_data = get_sdk_data()
    attr_targets = {}
    for target, row in sdk_data.items():
        attr = row["ctrl"]+"."+row["attr"]
        attr_targets.setdefault(attr, []).append(target)
    mutex_targets = []
    for targets in attr_targets.values():
        if len(targets) == 2:
            mutex_targets.append(targets)
    with open(os.path.abspath(__file__ + "/../targets_mutex.json"), "w") as fp:
        json.dump(mutex_targets, fp, indent=4)


def get_orig_sdk_data(base_targets, comb_data):
    sdk_targets = set(base_targets)
    for targets in comb_data.values():
        if isinstance(targets, list):
            sdk_targets.update(targets)
        else:
            sdk_targets.update(targets.keys())
    bridge = "CTRL_expressions"
    data = {}
    for target_name in sdk_targets:
        sdk_data = get_base_sdk_data(bridge+"."+target_name)
        if sdk_data is None:
            continue
        ctrl = sdk_data["ctrl"]
        if not ctrl.startswith("CTRL"):
            continue
        data[target_name] = sdk_data
    data.update(get_eye_data())
    return data


def get_mh_sdk_data(base_targets, comb_data, real_target_map):
    orig_data = get_orig_sdk_data(base_targets, comb_data)
    data = {}
    for target in base_targets:
        if target in real_target_map:
            data[target] = orig_data[real_target_map[target]]
        elif target in orig_data:
            data[target] = orig_data[target]
        elif isinstance(comb_data[target], list):
            real_target = sorted(comb_data[target])[0]
            data[target] = orig_data[real_target]
        else:
            real_target = sorted(comb_data[target].keys())[0]
            data[target] = orig_data[real_target]
    return data


def clear_sdk_ctrl(data):
    ctrls = [row["ctrl"] for row in data.values()]
    remove_ctrls = [ctrl for ctrl in cmds.ls("CTRL*", type="transform") if ctrl not in ctrls]
    remove_ctrls = list(filter(is_ctrl, remove_ctrls))
    for remove_ctrl in list(set(remove_ctrls)):
        cmds.delete(cmds.listRelatives(remove_ctrl, p=1))
    bridge = get_q_meta_bridge()
    for target_name, sdk in data.items():
        cmds.addAttr(bridge, ln=target_name, k=1, min=0, max=1)
        cd = sdk["ctrl"]+"."+sdk["attr"]
        cmds.setDrivenKeyframe(bridge+"."+target_name, cd=cd, dv=sdk["ts"][0], v=sdk["vs"][0], itt="linear", ott="linear")
        cmds.setDrivenKeyframe(bridge + "." + target_name, cd=cd, dv=sdk["ts"][1], v=sdk["vs"][1], itt="linear", ott="linear")
    for ctrl in ctrls:
        cmds.xform(ctrl, ws=0, t=[0, 0, 0])
    cmds.select(ctrls)


def convert_low_plane():
    base_targets = read_text_targets("mh_low_targets")
    comb_data = load_json_data("mh_low_comb")
    comb_data["mouthLipsTogetherD"] = ["mouthLipsTogetherDR", "mouthLipsTogetherDL"]
    comb_data["mouthLipsTogetherU"] = ["mouthLipsTogetherUR", "mouthLipsTogetherUL"]
    comb_data["mouthStickyC"] = ["mouthStickyUC", "mouthStickyDC"]
    sdk_data = get_mh_sdk_data(base_targets[:59], comb_data, {})
    save_json_data(sdk_data, "mh_low_sdk")
    clear_sdk_ctrl(sdk_data)
    cmds.delete([u'GRP_neckGUI', u'GRP_switchesGUI', u'GRP_faceTweakersGUI',
                 u'FRM_WMmultipliers', u'GRP_faceAndEyesAimFollowHeadGUI', u'GRP_C_eyesAim', u'headRigging_grp',
                 u'CTRL_expressions', u'CTRL_GUIswitch', u'FRM_chinRaise'])
    connect_driver_comb("QMeta_expressions", get_comb_data_by_targets(base_targets[59:]))


def x6_convert_low_plane():
    base_targets = read_text_targets("arkit_targets")
    # comb_data = load_json_data("arkit_comb")
    # comb_data["mouthLipsTogether"] = ["mouthLipsTogetherDR", "mouthLipsTogetherDL",
    #                                    "mouthLipsTogetherUR", "mouthLipsTogetherUL"]
    # comb_data["mouthStretchLipsCloseR"] = ["mouthStretchR"]
    # comb_data["mouthStretchLipsCloseL"] = ["mouthStretchL"]
    # real_target_map = dict(mouthStretchLipsCloseR="mouthStretchR", mouthStretchLipsCloseL="mouthStretchL")
    # sdk_data = get_mh_sdk_data(base_targets[:59], comb_data, real_target_map)
    # save_json_data(sdk_data, "arkit_sdk")
    # clear_sdk_ctrl(sdk_data)
    # cmds.delete([u'GRP_neckGUI', u'GRP_switchesGUI', u'GRP_faceTweakersGUI',
    #              u'FRM_WMmultipliers', u'GRP_faceAndEyesAimFollowHeadGUI', u'GRP_C_eyesAim', u'headRigging_grp',
    #              u'CTRL_expressions', u'CTRL_GUIswitch'])  # u'FRM_chinRaise'
    from .anim_driver import init_locator_driver_ctrl

    mh_bridge = "QMeta_expressions"
    mh_targets = read_text_targets("arkit_mh_targets")
    arkit_targets = read_text_targets("arkit_x6_targets")
    arkit_bridge = init_locator_driver_ctrl("ARKitDriver", arkit_targets)
    for arkit_target, mh_target in zip(arkit_targets, mh_targets):
        if not cmds.objExists(mh_bridge+"."+mh_target):
            mh_target = mh_target[:-1]
        if cmds.objExists(mh_bridge+"."+mh_target):
            connect_attr(mh_bridge+"."+mh_target, arkit_bridge+"."+arkit_target)

        # if mh_target in anim_curve_48:
        #     fvs = anim_curve_48[mh_target]
        # else:
        #     fvs = anim_curve_48[mh_target[:-1]]
        # set_attr_anis(ctrl+"."+x6_target, fvs["frames"], fvs["values"])

    # connect_driver_comb("QMeta_expressions", get_comb_data_by_targets(base_targets[59:]))


def doit():
    # connect_driver_comb("QMeta_expressions", get_comb_data_by_targets(["browRaiseInL_browRaiseInR"]))
    #
    connect_driver_comb("QMeta_expressions", get_comb_data_by_targets(["browDownL_browDownR",
                                                                       "browLateralL_browLateralR"]))
    # browRaiseInL_browRaiseInR
    # browDownL_browDownR
    # browLateralL_browLateralR