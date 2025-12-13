from maya import cmds, mel
import json
from maya.api.OpenMaya import *
from maya.api.OpenMayaAnim import *


def find_bs(polygon):
    if not cmds.objExists(polygon):
        return
    shapes = set(cmds.listRelatives(polygon, s=1, f=1) or [])
    for bs in cmds.ls(cmds.listHistory(polygon), type="blendShape"):
        if cmds.ls(cmds.blendShape(bs, q=1, g=1), l=1)[0] in shapes:
            return bs


def get_bs_anim_data(path):
    anim_curve_data = {}
    with open(path, "r") as fp:
        data = json.load(fp)
    for t, row in enumerate(data):
        for target, w in row.items():
            fvs = anim_curve_data.setdefault(target, dict(frames=[], values=[]))
            fvs["frames"].append(t+1)
            fvs["values"].append(w)
    return anim_curve_data


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

def load_bs_anim(path):
    data = get_bs_anim_data(path)
    bs = find_bs(cmds.ls(sl=1, l=1)[0])
    if not bs:
        return
    for target, fvs in data.items():
        if not cmds.objExists(bs + "." + target):
            continue
        set_attr_anis(bs + "." + target, fvs["frames"], fvs["values"])


def doit():
    load_bs_anim(r"D:/work/x3_ai_face/x3_face_to_xinghuo/iphone_anim/face_v4/MySlate_4_aiMeta.json")
    # load_bs_anim(r"D:/work/x3_ai_face/x3_face_to_xinghuo/iphone_anim/rom55/MySlate_4_aiMeta.json")
    # load_bs_anim(r"D:\work\x3_ai_face\predictions\predictions_neural_network_best_checkpoint.json")
    # load_bs_anim(r"D:/work/x3_ai_face/test_face_anim/rom55/base_face_anim.json")
    # load_bs_anim(r"D:/work/x3_ai_face/test_face_anim/face5/base_face_anim.json")
    # load_bs_anim(r"D:/work/x3_ai_face/x3_face_to_xinghuo/rom55_to_face5/face5/meta_nn_00000_task_aiMeta.json")
    # load_bs_anim(r"D:/work/x3_ai_face/x3_face_to_xinghuo/rom55_to_face5/rom55/meta_nn_00000_task_aiMeta.json")

if __name__ == '__main__':
    load_bs_anim("D:/work/x3_ai_face/x3_face_anim/MySlate_4_aiMeta.json")
