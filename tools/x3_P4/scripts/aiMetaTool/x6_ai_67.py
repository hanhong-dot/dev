from .anim_ctrl_driver import *
from .anim_solve import *
from .load_runtime import *


def convert_mh_to_67(data):
    new_data = dict()
    x6_51_targets = read_text_targets("arkit_x6_targets")
    mh_51_targets = read_text_targets("arkit_mh_targets")
    map_target = {a: b for a, b in zip(mh_51_targets, x6_51_targets)}
    map_target["browLateralR"]  = "browLateral_R"
    map_target["browLateralL"]  = "browLateral_L"
    for mh_target, value in data.items():
        if mh_target in map_target:
            new_data[map_target[mh_target]] = value
        else:
            new_data[map_target[mh_target + "R"]] = value
            new_data[map_target[mh_target + "L"]] = value
    return new_data

def set_offset_value(data, name, offset):
    value = data.get(name, 0)
    value += offset
    value = min(max(value, 0.0), 1.0)
    data[name] = value

def re_sub_comb_value(data, src, dst, comb):
    value = min(data.get(src, 0), data.get(dst, 0))
    set_offset_value(data, src, -value*0.5)
    set_offset_value(data, dst, -value)
    set_offset_value(data, comb, value)

def re_brow(data):
    re_sub_comb_value(data, "BrowDown_L", "BrowOuterUp_L", "BrowDownIn_L")
    re_sub_comb_value(data, "BrowDown_R", "BrowOuterUp_R", "BrowDownIn_R")
    re_sub_comb_value(data, "BrowDown_L", "browLateral_L", "BrowDownIn_L")
    re_sub_comb_value(data, "BrowDown_R", "browLateral_R", "BrowDownIn_R")
    # data["BrowDownIn_L"] = data["browLateral_L"]
    # data["BrowDownIn_R"] = data["browLateral_R"]
    data.pop("browLateral_L")
    data.pop("browLateral_R")


def re_eye_ud_blink_rl(data, rl):
    blink_data = load_json_data('x6_ai_67_eye_blink')
    data.setdefault("EyeBlinkDn"+rl, 0)
    data.setdefault("EyeBlinkUp"+rl, 0)
    comb =  min(data["CheekSquint"+rl]*blink_data["CheekSquint"],
                data["EyeSquint"+rl]*blink_data["EyeSquint"])
    comb = comb * 0.7
    # set_offset_value(data, "EyeBlinkUp" + rl, comb * 0.6/blink_data["EyeBlinkUp"])
    set_offset_value(data, "EyeBlinkDn" + rl, comb * 0.8/blink_data["EyeBlinkDn"])
    set_offset_value(data, "CheekSquint" + rl, -comb/blink_data["CheekSquint"])
    set_offset_value(data, "EyeSquint" + rl, -comb/blink_data["EyeSquint"])

def same_orig_blink(orig):
    value = max(orig.get("eyeBlinkR", 0), orig.get("eyeBlinkL", 0))
    orig["eyeBlinkR"] = value
    orig["eyeBlinkL"] = value

def same_ai_67_blink(data):
    value = max(data.get("EyeBlink_R", 0), data.get("EyeBlink_L", 0))
    data["EyeBlink_R"] = value
    data["EyeBlink_L"] = value

    value = min(data.get("EyeWide_R", 0), data.get("EyeWide_L", 0))
    data["EyeWide_R"] = value
    data["EyeWide_L"] = value

    value = (data.get("EyeSquint_R", 0)+ data.get("EyeSquint_L", 0))/2
    data["EyeSquint_R"] = value
    data["EyeSquint_L"] = value


    value = (data.get("EyeBlinkDn_R", 0)+ data.get("EyeBlinkDn_L", 0))/2
    data["EyeBlinkDn_R"] = value
    data["EyeBlinkDn_L"] = value

    value = (data.get("CheekSquint_R", 0)+ data.get("CheekSquint_L", 0))/2
    data["CheekSquint_R"] = value
    data["CheekSquint_L"] = value



def re_orig_blink(orig, data, rl):
    # value = max(data.get("EyeBlink_"+rl, 0), orig.get("eyeBlink"+rl, 0))
    # offset = (value - data.get("EyeBlink_"+rl, 0))*0.5
    # offset += orig.get("eyeBlink"+rl, 0) * 0.5
    # set_offset_value(data, "EyeBlink_"+rl, offset)
    value = orig.get("eyeBlink"+rl, 0) * 1.1
    value = min(max(value, 0.0), 1.0)
    data["EyeBlink_"+rl] = value

def check_blink(data, rl):
    blink_data = load_json_data('x6_ai_67_eye_blink')
    blink = 0
    for pose, weight in blink_data.items():
        blink += data[pose+rl]*weight
    keep_value = data["EyeLookDown" + rl] * blink_data["EyeLookDown"]
    max_value = 1.02
    if blink > 1.02:
        scale = (max_value-keep_value) / (blink-keep_value)
        for pose, weight in blink_data.items():
            if pose == "EyeLookDown":
                continue
            data[pose + rl] *= scale

    blink = 0
    for pose, weight in blink_data.items():
        blink += data[pose + rl] * weight


def convert_ai_67_frame(orig, solve):
    data = convert_mh_to_67(solve)
    re_brow(data)
    same_orig_blink(orig)
    re_orig_blink(orig, data, "R")
    re_orig_blink(orig, data, "L")
    re_eye_ud_blink_rl(data, "_R")
    re_eye_ud_blink_rl(data, "_L")
    check_blink(data, "_R")
    check_blink(data, "_L")
    same_ai_67_blink(data)
    return data

def convert_ai_67_data(path):
    path = os.path.splitext(path)[0].replace("\\", "/")
    base_path = path + "_base.json"
    with open(base_path, "r") as fp:
        orig_weight_anis = json.load(fp)["orig_weight_anis"]
    solve_path = path + "_ai_result.json"
    with open(solve_path, "r") as fp:
        solve_weight_anis = json.load(fp)
    new_weight_anis = []
    for orig, solve in zip(orig_weight_anis, solve_weight_anis):
        new_weight_anis.append(convert_ai_67_frame(orig, solve))
    new_path = path + "_x6_67.json"
    with open(new_path, "w") as fp:
        json.dump(new_weight_anis, fp, indent=4)



def x6_ai_67_solve(path):
    path = os.path.splitext(os.path.splitext(path)[0])[0]
    clear_orig_detail()
    export_base_anis(path)
    convert_base_anim(path, convert_x6_data)
    sub = ai_meta_exe.solve_x6_67_bs(path)
    sub.wait()
    convert_ai_67_data(path)
    # os.remove(path+".json")
    # os.remove(path+".npy")
    # os.remove(path+"_base.json")
    # rename_file(path+"_ai_result.json", path+"_arkit.json")

def convert_bs_data(data):
    anim_curve_data = {}
    for t, row in enumerate(data):
        for target, w in row.items():
            fvs = anim_curve_data.setdefault(target, dict(frames=[], values=[]))
            fvs["frames"].append(t+1)
            fvs["values"].append(w)
    return anim_curve_data

def load_ai_67_anim(path):
    data = json.load(open(path))
    anim_curve_data = convert_bs_data(data)
    set_ctrl_anim(anim_curve_data, load_json_data("x6_ai_67_sdk"))


def get_orig_weight_anis(iphone_data):
    raw_names = load_json_data("raw_names")
    raw_names = [name.replace("CTRL_expressions_", "") for name in raw_names]
    full_driver_data = [frame_data["ControlValues"] for frame_data in iphone_data]
    full_driver_data = np.array(full_driver_data, dtype=np.float32)
    max_int_16 = 65535.0
    full_driver_data = full_driver_data / max_int_16
    return [dict(zip(raw_names, values.tolist())) for values in full_driver_data]

def load_runtime_ai_67(iphone_data_path, st):
    iphone_data = load_iphone_data2(iphone_data_path)
    output_data = predict_iphone_data(iphone_data, "x6_ai_67_runtime_nn")
    output_targets = load_json_data("ai_67_train_targets") + load_json_data("ai_meta_keep_targets")
    solve_weight_anis = [dict(zip(output_targets, values.tolist())) for values in output_data]
    orig_weight_anis = get_orig_weight_anis(iphone_data)
    new_weight_anis = []
    for orig, solve in zip(orig_weight_anis, solve_weight_anis):
        new_weight_anis.append(convert_ai_67_frame(orig, solve))
    anim_curve_data = convert_bs_data(new_weight_anis)
    frames = [frame_data["FrameNumber"] for frame_data in iphone_data]
    st = frames[0] - st
    frames = [frame - st for frame in frames]
    for row in anim_curve_data.values():
        row["frames"] = frames
    set_ctrl_anim(anim_curve_data, load_json_data("x6_ai_67_sdk"))


def find_anim_curve(attr):
    if not cmds.objExists(attr):
        return None
    anim_curves = cmds.listConnections(attr, s=1, d=0, type="animCurve")
    if not anim_curves:
        return None
    return anim_curves[0]


def doit():
    # attr = "rig_plane_0002:CTRL_R_mouth_dimple.translateY"
    # re_target_attr(attr)
    # load_runtime_ai_67()
    path = r"D:\work\AI_mh\x6\AI67\anim\json\C_ceshi_seq040_C150_V03_LZJ.json"
    load_runtime_ai_67(path, 1)
    # path = r"D:/work/AI_mh/x6/AI67/test_open_eye/20250813_MySlate_36"
    # convert_ai_67_data(path)
    # convert_ai_67_data(path)

    # convert_ai_67_data("D:/work/AI_mh/x6/rom_v2/ai_67/rom_v2")
    # load_ai_67_anim("D:/work/AI_mh/x6/rom_v2/ai_67/rom_v2_x6_67.json")

