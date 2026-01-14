from .anim_ctrl_driver import *
from maya import cmds
import os
import json


def get_fps():
    fps = cmds.currentUnit(query=True, time=True)
    if fps.endswith("fps"):
        fps = int(fps[:-3])
    else:
        fps = dict(
            film=24,
            ntsc=30,
            ntscf=60,
        ).get(fps)
    return fps


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
    frames = []
    for i in range(st, et + 1):
        cmds.currentTime(i)
        frame = [cmds.getAttr(bridge + "." + target) for target in targets]
        frames.append(frame)
    data = dict(
        keyFrames=frames,
        frameRate=get_fps(),
        blendShapes=targets,
    )
    return data


def export_unity_anim(path, st, et):
    data = get_anim_data(st, et)
    dir_name = os.path.dirname(path)
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)
    with open(path, "w") as f:
        json.dump(data, f, indent=4)


def load_unity_anim(path, st):
    data = json.load(open(path, "r"))
    anim_curve_data = {}
    frames = list(range(st, st + len(data["keyFrames"])))
    for i, target in enumerate(data["blendShapes"]):
        values = [frame[i] for frame in data["keyFrames"]]
        anim_curve_data[target] = dict(frames=frames, values=values)
    set_ctrl_anim(anim_curve_data, load_json_data("mh_low_sdk"))

def doit():
    # export_unity_anim(r"D:/work/AI_mh/x3/export/new_export.json", 1, 266)
    load_unity_anim(r"D:/work/AI_mh/x3/export/new_export.json", 1)

if __name__ == '__main__':
    data = json.load(open("D:/work/AI_mh/x3/export/new_export.json", "r"))
    i = data["blendShapes"].index("eyeLookUpR")
    print(data["keyFrames"][107][i])
    print(data)