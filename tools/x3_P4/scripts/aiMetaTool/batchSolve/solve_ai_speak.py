import json
import os.path
from maya.api.OpenMaya import *
from maya.api.OpenMayaAnim import *
from .solve_anim_all import *


def get_ctrl_atts(json_file):
    json_data = json.load(open(json_file, 'r'))
    ctrl_attrs = []
    ctrl_names = set([])
    for ctrl_data in json_data:
        ctrl_name = ctrl_data['ctrl_name']
        attr_datas = ctrl_data['attr_data']
        for attr_data in attr_datas:
            name = attr_data['attr_name']
            ctrl_attrs.append(ctrl_name + "." + name)
            ctrl_names.add(ctrl_name)
    return ctrl_names, ctrl_attrs


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


def load_ai_speak_ue_ctrl_anim(json_path):
    json_data = json.load(open(json_path))
    cmds.currentUnit(t="ntscf")
    frames = list(range(len(json_data['weight_data'])))
    frames = [f+1 for f in frames]
    for attr, values in zip(json_data["attr_names"], zip(*json_data['weight_data'])):
        set_attr_anis(attr, frames, values)
    # et = int(round(len(frames)/2.0))
    # cmds.currentUnit(t="ntsc")
    et = len(frames)
    cmds.playbackOptions(e=1, ast=1, min=1, max=et, aet=et)


def ctrl_to_bs_anim(json_path, solve_bs):
    load_ai_speak_ue_ctrl_anim(json_path)
    dir_path, file_name = os.path.split(json_path)
    ai_path = os.path.join(dir_path, "ai_result", file_name).replace("\\", "/")
    solve_bs(ai_path)


def batch_convert_speak(root, solve_bs):
    open_myles()
    for name in os.listdir(root):
        if not name.endswith(".json"):
            continue
        json_path = os.path.join(root, name).replace("\\", "/")
        ctrl_to_bs_anim(json_path, solve_bs)


def save_speak(json_path):
    load_ai_speak_ue_ctrl_anim(json_path)
    ma_path = json_path.replace(".json", ".ma")
    cmds.file(ma_path, f=1, pr=1, ea=1, type="mayaAscii")


def batch_save_speak(root):
    for name in os.listdir(root):
        if not name.endswith(".json"):
            continue
        json_path = os.path.join(root, name).replace("\\", "/")
        save_speak(json_path)


def doit():
    batch_convert_speak(r"D:\work\ai_ue_speak\batch_solve_test", solve_mh_low)
    # load_ai_speak_ue_ctrl_anim(r"D:\work\ai_ue_speak\ai_speak_test\sentence_034.json")
    # load_ai_speak_ue_ctrl_anim(r"D:\work\ai_ue_speak\ai_speak_test\MySlate_13_iPhone.json")
    # ctrl_to_bs_anim2(r"D:/work/AI_mh/x6/NN/pnn/CV_LS0100_SC201_Line_2_CharLouise_StoneField_LevelSequence.json")
    # path = "D:/work/ue_ai_speak/hm_speak/speak_final"
    # batch_convert_speak("D:/work/ai_ue_speak/ai_speak_test", arkit_solve)
    # batch_convert_speak("D:/work/ai_ue_speak/ai_speak_test", solve_mh_low)
    # batch_save_speak("D:/work/ue_ai_speak/hm_speak/speak_final")