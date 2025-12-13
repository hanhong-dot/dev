import os
import json
from maya import cmds
import numpy as np


def load_json_data(name):
    with open(os.path.abspath(__file__ + "/../data/%s.json" % name), "r") as fp:
        return json.load(fp)


def export_raw_anim(path):
    use_raw_names = load_json_data("use_raw_names")
    st = int(round(cmds.playbackOptions(q=1, ast=1)))
    et = int(round(cmds.playbackOptions(q=1, aet=1)))
    ctrl_exp_names = [name.replace("CTRL_expressions_", "CTRL_expressions.") for name in use_raw_names]
    raw_anim = []
    for i in range(st, et):
        cmds.currentTime(i + 1)
        raw_values = [cmds.getAttr(name) for name in ctrl_exp_names]
        raw_anim.append(raw_values)
    raw_anim = np.array(raw_anim, dtype=np.float32)
    np.save(path + "_raw_anim.npy", raw_anim)


def doit():
    export_raw_anim(r"E:/aiClothData/mh_runtime/test_data/rom_v2")

