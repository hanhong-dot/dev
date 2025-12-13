from .anim_driver import read_text_targets
from maya import cmds
import os
import json

def get_name_space():
    selected = cmds.ls(sl=1, l=0)
    if not selected:
        return ""
    if ":" in selected[0]:
        return selected[0][:-len(selected[0].split(":")[-1])]
    else:
        return ""

def get_anim_data(st, et):
    targets = read_text_targets("mh_low_targets")
    targets = targets[:59]
    data = []
    ns = get_name_space()
    bridge = ns + "QMeta_expressions"
    if not cmds.objExists(bridge):
        return data
    for i in range(st, et + 1):
        cmds.currentTime(i)
        data.append({target: cmds.getAttr(bridge + "." + target) for target in targets})
    return data


def export_unity_anim(path, st, et):
    data = get_anim_data(st, et)
    dir_name = os.path.dirname(path)
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)
    with open(path, "w") as f:
        json.dump(data, f, indent=4)


def doit():
    export_unity_anim(r"D:\work\x3_npc_auto_55\anim/export.json", 1, 538)
