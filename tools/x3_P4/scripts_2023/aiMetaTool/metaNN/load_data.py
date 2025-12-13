from maya import cmds, mel
from maya.api.OpenMaya import *
from maya.api.OpenMayaAnim import *
from .config import *


def break_attr(attr):
    for src_attr in cmds.listConnections(attr, s=1, d=0, p=1) or []:
        cmds.disconnectAttr(src_attr, attr)


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


def break_ctrl(ctrl):
    link_data = []
    for attr in cmds.listAttr(ctrl, ud=1):
        dst_attr = ctrl + "." + attr
        if cmds.getAttr(dst_attr, type=1) != "float":
            continue
        for src_attr in cmds.listConnections(dst_attr, s=1, d=0, p=1) or []:
            cmds.disconnectAttr(src_attr, dst_attr)
            link_data.append([src_attr, dst_attr])
    return link_data

def load_iphone_data(path):
    lines = open(path).readlines()
    anim_data = []
    for i in range(0, len(lines), 269):
        frame_lines = lines[i:i + 270]
        if len(frame_lines) != 270:
            continue
        frame = "".join(frame_lines)
        if frame[-2] == "{":
            frame = frame[:-2]
        if frame[0] == "}":
            frame = frame[1:]
        frame_data = json.loads(frame)
        anim_data.append(frame_data)
    return anim_data


def load_runtime_data():
    path = r"D:\work\AI_mh\runtime\anim\yiqi\playerData.json"
    anim_data = load_iphone_data(path)
    max_int_16 = 65535.0
    ctrl = "CTRL_expressions"
    frames = list([i+1 for i in range(len(anim_data))])
    break_ctrl(ctrl)
    base_targets = load_json_data("raw_names")
    for i, target in enumerate(base_targets):
        values = [frame["ControlValues"][i]/max_int_16 for frame in anim_data]
        set_attr_anis(ctrl+"."+target[len("CTRL_expressions_"):], frames, values)


def clamp_value(value, min_value, max_value):
    if value > max_value:
        return max_value
    if value < min_value:
        return min_value
    return value


def calculate_raw_control(control_range, from_val, to_val, slope, cut, gui_value):
    value = clamp_value(gui_value, *control_range)
    value = clamp_value(value, from_val, to_val)
    return slope * value + cut


def load_runtime_anim_to_ctrl():
    path = r"D:\work\AI_mh\runtime\anim\yiqi\playerData.json"
    anim_data = load_iphone_data(path)

    gui_to_raw_map = load_json_data("gui_to_raw_map")
    gui_names = load_json_data("gui_names")
    raw_names = load_json_data("raw_names")
    gui_ranges = load_json_data("gui_ranges")
    gui_map = {}
    for sdk_data in gui_to_raw_map:
        gui_map.setdefault(sdk_data[0], []).append(sdk_data)
    for gui_index, gui_name in enumerate(gui_names):
        if len(gui_map[gui_index]) == 1:
            continue
        if len(gui_map[gui_index]) == 2:
            continue
        print(gui_name)
        print()
            # sdk_data = gui_map[gui_index]
            # input_index, output_index, from_val, to_val, slope, cut = sdk_data[-1]


        # print(from_val, to_val)
        # gui_range = gui_ranges[input_index]
        # for i in range(24):
        #     gui_value = -1.1+0.1*i
        #     raw_value = calculate_raw_control(gui_range, from_val, to_val, slope, cut, gui_value)
        #     print("%.2f" % gui_value, "%.2f" % raw_value)
        # print(sdk_data)
        # return
        # print(gui_index,gui_name)

    # for gr in gui_to_raw_map:
    #     input_index, output_index, from_val, to_val, slope, cut = gr


def doit():
    load_runtime_anim_to_ctrl()
