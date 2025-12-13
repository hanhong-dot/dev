# vim:ts=4:sw=4:expandtab
# -*- coding: utf-8 -*-
# @brief
# @author huangsheng@papegames.net
# @version v1.0.0
# @file: handle_controller_curve.py
# @time: 2025/8/22 16:34


import sys
from maya import cmds, mel
from maya.api.OpenMaya import *
from maya.api.OpenMayaAnim import *
import numpy as np


from .jitter_detector import JitterDetector


def find_anim_curve(attr):
    if not cmds.objExists(attr):
        return None
    anim_curves = cmds.listConnections(attr, type="animCurve", s=1, d=0)
    if not anim_curves:
        return None
    return anim_curves[0]


def get_time_values(anim_curve_name, time=()):
    tc = cmds.keyframe(anim_curve_name, time=time, query=True, timeChange=True)
    vc = cmds.keyframe(anim_curve_name, time=time, query=True, valueChange=True)
    return tc, vc


def api_ls(*names):
    selection_list = MSelectionList()
    for name in names:
        selection_list.add(name)
    return selection_list


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


def set_attr_anis(attr, frames, values):
    if not cmds.objExists(attr):
        return
    anim_curve = get_anim_curve(attr)
    if not anim_curve:
        return
    mel.eval('cutKey -clear -time ":" '+attr)
    node, at = attr.split(".")
    cmds.setKeyframe(node, at=at, t=frames[0], v=values[0])
    typ = cmds.getAttr(attr, type=1)
    if typ == "doubleAngle":
        values /= (180.0/np.pi)
    anim_curve = MFnAnimCurve(api_ls(attr).getPlug(0))
    fps = MTime.uiUnit()
    offset = 0
    times = [MTime(f+offset, fps) for f in frames]
    anim_curve.addKeys(times, values)


# if __name__ == "__main__":
#     print("extract curve")
#     controller_curve_info = {}
#     for controller in ["CTRL_R_eye_blink", "CTRL_R_eye", "CTRL_C_jaw"]:
#         controller_curve = {}
#         for attr in ["translateX", "translateY"]:
#             controller_attr = f"{controller}.{attr}"
#             anim_curve_name = find_anim_curve(controller_attr)
#             if anim_curve_name is not None:
#                 tc, vc = get_time_values(anim_curve_name)
#                 controller_curve[f"tc_{attr[-1].lower()}"] = np.array(tc).astype(int)
#                 controller_curve[f"vc_{attr[-1].lower()}"] = np.array(vc)
#
#         controller_curve_info[controller] = controller_curve
#
#     print("smooth curve")
#     cleanup_controller_curve_info = JitterDetector.smooth_controller_curve(controller_curve_info)
#
#     print("save curve")
#     for controller, curve_info in cleanup_controller_curve_info.items():
#         for tc_name, vc_name in [["tc_x", "vc_x"], ["tc_y", "vc_y"]]:
#             tc = curve_info.get(tc_name)
#             vc = curve_info.get(vc_name)
#             if tc is not None and vc is not None:
#                 controller_attr = f"{controller}.translate{tc_name[-1].upper()}"
#                 set_attr_anis(controller_attr, tc, vc)
