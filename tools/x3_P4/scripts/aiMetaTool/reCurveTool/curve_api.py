# coding=utf-8
from maya import cmds, mel
from maya.api.OpenMaya import *
from maya.api.OpenMayaAnim import *
import numpy as np

def find_anim_curve(attr):
    if not cmds.objExists(attr):
        return None
    anim_curves = cmds.listConnections(attr, type="animCurve", s=1, d=0)
    if not anim_curves:
        return None
    return anim_curves[0]


def api_ls(*names):
    selection_list = MSelectionList()
    for name in names:
        selection_list.add(name)
    return selection_list


def set_all_frame_data(attr, frames, values):
    if not cmds.objExists(attr):
        return
    mel.eval('cutKey -clear -time ":" '+attr)
    node, at = attr.split(".")
    cmds.setKeyframe(node, at=at, t=frames[0], v=values[0])
    typ = cmds.getAttr(attr, type=1)
    if typ == "doubleAngle":
        values = np.array(values)
        values /= (180.0/np.pi)
        values = values.tolist()
    anim_curve = find_anim_curve(attr)
    if not anim_curve:
        return
    anim_curve = MFnAnimCurve(api_ls(attr).getPlug(0))
    fps = MTime.uiUnit()
    offset = 0
    times = [MTime(f+offset, fps) for f in frames]
    anim_curve.addKeys(times, values)


def set_range_anim_data(attr, frames, values):
    # st, et = int(round(min(frames))), int(round(max(frames)))
    # cmds.cutKey(attr, clear=True, time=(st, et))
    for f, v in zip(frames, values):
        cmds.setKeyframe(attr, time=f, value=v)


def get_time_value(anim_curve, st, et):
    times = cmds.keyframe(anim_curve, query=True, timeChange=True, selected=True)
    values = cmds.keyframe(anim_curve, query=True, valueChange=True, selected=True)
    if times:
        return times, values
    if st is None:
        times = cmds.keyframe(anim_curve, query=True, timeChange=True)
        values = cmds.keyframe(anim_curve, query=True, valueChange=True)
    else:
        times = cmds.keyframe(anim_curve, query=True, t=(st, et), timeChange=True)
        values = cmds.keyframe(anim_curve, query=True, t=(st, et), valueChange=True)
    return times, values


def get_all_curve_data(st, et):
    result = []
    selected_names = cmds.keyframe(q=1, selected=True, name=1)
    if selected_names:
        for anim_curve in selected_names:
            times, values = get_time_value(anim_curve, st, et)
            result.append((anim_curve, times, values))
    else:
        for ctrl in cmds.ls(sl=1):
            attrs = cmds.listAttr(ctrl, keyable=True, unlocked=True)
            if not attrs:
                continue
            for attr in attrs:
                if attr.endswith("temp_test"):
                    continue
                full_attr = ctrl + "." + attr
                anim_curve = find_anim_curve(full_attr)
                if not anim_curve:
                    continue
                times, values = get_time_value(anim_curve, st, et)
                if times is None:
                    continue
                if len(values) < 3:
                    continue
                result.append((full_attr, times, values))
    return result


def get_play_back_slider_range():
    try:
        play_back_slider_name = mel.eval("$gPlayBackSlider = $gPlayBackSlider")
    except RuntimeError:
        return None, None
    time_range = cmds.timeControl(play_back_slider_name, query=True, range=True)
    time_range = time_range.replace('"', "")
    st, et = time_range.split(":")
    st, et = int(st), int(et)
    if et - st == 1:
        return None, None
    return st, et


def get_selected_curve_data():
    st, et = get_play_back_slider_range()
    return get_all_curve_data(st, et)

def set_curve_all_data(data):
    for attr, frames, values in data:
        set_range_anim_data(attr, frames, values)

def is_re_curve_all():
    if cmds.keyframe(q=1, selected=True):
        return False
    st, et = get_play_back_slider_range()
    if st is None:
        return True
    else:
        return False


def tool_auto_re_curve_selected(re_data, **kwargs):
    st, et = get_play_back_slider_range()
    data = get_all_curve_data(st, et)
    new_data = re_data(data, **kwargs)
    if is_re_curve_all():
        for curve, frames, values in new_data:
            set_all_frame_data(curve, frames, values)
    else:
        for curve, frames, values in new_data:
            set_range_anim_data(curve, frames, values)


def do_no_thing_compute(data):
    return data

def doit():
    tool_auto_re_curve_selected(do_no_thing_compute)
    # data = get_selected_curve_data()
    # set_curve_all_data(data)