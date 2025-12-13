# coding=utf-8
from . import curve_api
from . import compute_core
import numpy as np
from maya import cmds, mel



def undo(fun):
    u"""
    让函数一个单次ctrl+Z undo撤回操作
    """
    def undo_fun(*args, **kwargs):
        # 打开undo
        cmds.undoInfo(openChunk=1)
        fun(*args, **kwargs)
        cmds.undoInfo(closeChunk=1)
    return undo_fun

def add_test_attr(attr):
    if cmds.objExists(attr):
        return
    node, name = attr.split(".")
    cmds.addAttr(node, longName=name, attributeType='double', keyable=True)

def re_test_data(data):
    new_data = []
    for curve, frames, values in data:
        curve += "_temp_test"
        add_test_attr(curve)
        frames, values = np.array(frames), np.array(values)
        frames, values = compute_core.remove_nose_and_auto_smooth(frames, values)
        frames, values = frames.tolist(), values.tolist()
        new_data.append((curve, frames, values))
    return new_data


def re_test_data2(data):
    new_data = []
    for curve, frames, values in data:
        curve += "_2_temp_test"
        add_test_attr(curve)
        frames, values = np.array(frames), np.array(values)
        frames, values = compute_core.remove_nose_and_auto_smooth2(frames, values)
        frames, values = frames.tolist(), values.tolist()
        new_data.append((curve, frames, values))
    return new_data


def re_data(data):
    new_data = []
    for curve, frames, values in data:
        frames, values = np.array(frames), np.array(values)
        frames, values = compute_core.remove_nose_and_auto_smooth(frames, values)
        frames, values = frames.tolist(), values.tolist()
        new_data.append((curve, frames, values))
    return new_data

@undo
def tool_auto_smooth():
    curve_api.tool_auto_re_curve_selected(re_data)


def test():
    tool_auto_smooth()

    # curve_api.set_play_back_slider_range(1, 20)
    # curve_api.tool_auto_re_curve_selected(re_test_data)
    # curve_api.tool_auto_re_curve_selected(re_test_data2)
