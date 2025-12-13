import os
import json
from maya import cmds
import numpy as np


def load_json_data(name):
    with open(os.path.abspath(__file__ + "/../data/%s.json" % name), "r") as fp:
        return json.load(fp)


def save_json_data(data, name):
    path = os.path.abspath(__file__+"/../data/%s.json" % name).replace("\\", "/")
    with open(path, "w") as fp:
        json.dump(data, fp, indent=4)


def save_anim_data():
    gui_names = load_json_data("gui_names")
    anim_data = {}
    for i in range(1, 3000, 10):
        cmds.currentTime(i)
        for attr in gui_names:
            anim_data.setdefault(attr, []).append(cmds.getAttr(attr))
    save_json_data(anim_data, "anim_data")


def selected_no_anim():
    anim_data = load_json_data("anim_data")
    no_anim_ctrl = []
    for attr, values in anim_data.items():
        var = np.var(values)
        if var > 1e-6:
            continue
        ctrl = attr.split(".")[0]
        no_anim_ctrl.append(ctrl)
    cmds.select(no_anim_ctrl)


def check_use_gui_names():
    remove_ctrl = ['CTRL_C_tongue_press', 'CTRL_C_tongue_narrowWide', 'CTRL_C_tongue_roll', 'CTRL_C_tongue_tip',
                   'CTRL_C_tongue_inOut', 'CTRL_C_tongue']
    remove_ctrl += [u'CTRL_C_teethU', 'CTRL_C_teeth_fwdBackU', 'CTRL_C_teethD', 'CTRL_C_teeth_fwdBackD']
    remove_ctrl += ['CTRL_L_neck_mastoidContract', 'CTRL_R_neck_stretch', 'CTRL_R_neck_mastoidContract',
                    'CTRL_neck_throatExhaleInhale', 'CTRL_neck_throatUpDown', 'CTRL_neck_digastricUpDown',
                    'CTRL_L_neck_stretch']
    remove_ctrl += [u'CTRL_R_mouth_thicknessD', u'CTRL_L_mouth_thicknessD', u'CTRL_R_mouth_thicknessU',
                    u'CTRL_L_mouth_thicknessU', u'CTRL_R_mouth_pushPullU', u'CTRL_R_mouth_pushPullD',
                    u'CTRL_L_mouth_pushPullD', u'CTRL_L_mouth_pushPullU', u"CTRL_C_jaw_openExtreme"]

    remove_ctrl += [
        'CTRL_L_ear_up', 'CTRL_R_ear_up', 'CTRL_L_eye_lidPress', 'CTRL_R_eye_lidPress', 'CTRL_L_eye_eyelidU',
        'CTRL_R_eye_eyelidU', 'CTRL_L_eye_eyelidD', 'CTRL_R_eye_eyelidD', 'CTRL_L_eye_pupil', 'CTRL_R_eye_pupil',
        'CTRL_C_eye_parallelLook', 'CTRL_L_eyelashes_tweakerIn', 'CTRL_R_eyelashes_tweakerIn',
        'CTRL_L_eyelashes_tweakerOut', 'CTRL_R_eyelashes_tweakerOut', 'CTRL_L_nose_wrinkleUpper',
        'CTRL_R_nose_wrinkleUpper', 'CTRL_L_mouth_lipsBlow', 'CTRL_R_mouth_lipsBlow',
        'CTRL_L_mouth_stretchLipsClose', 'CTRL_R_mouth_stretchLipsClose', 'CTRL_L_mouth_pressU', 'CTRL_R_mouth_pressU',
        'CTRL_L_mouth_pressD', 'CTRL_R_mouth_pressD', 'CTRL_L_mouth_lipSticky', 'CTRL_R_mouth_lipSticky',
        'CTRL_L_mouth_lipsTowardsTeethU', 'CTRL_R_mouth_lipsTowardsTeethU', 'CTRL_L_mouth_lipsTowardsTeethD',
        'CTRL_R_mouth_lipsTowardsTeethD',  'CTRL_L_jaw_clench', 'CTRL_R_jaw_clench', 'CTRL_C_neck_swallow']

    remove_ctrl = list(map(str, remove_ctrl))
    gui_names = load_json_data("gui_names")
    remove_attr = []
    for attr in gui_names:
        if not cmds.objExists(attr):
            remove_attr.append(attr)
            continue
        ctrl = attr.split(".")[0]
        if ctrl in remove_ctrl:
            remove_attr.append(attr)
    use_gui_names = [name for name in gui_names if name not in remove_attr]
    save_json_data(use_gui_names, "use_gui_names")


def get_use_raw_names():
    print("get_use_raw_names")
    gui_names = load_json_data("gui_names")
    use_gui_names = load_json_data("use_gui_names")
    gui_raw_map = load_json_data("gui_to_raw_map")
    raw_names = load_json_data("raw_names")
    gr = {}
    for row in gui_raw_map:
        gui_id, row_id, _from, _to, slope, cut = row
        gr.setdefault(gui_id, []).append(row_id)
    use_raw_names = []
    for use_gui in use_gui_names:
        index = gui_names.index(use_gui)
        for raw_index in gr[index]:
            use_raw_names.append(raw_names[raw_index])
    use_raw_names = [name for name in raw_names if name in use_raw_names]
    save_json_data(use_raw_names, "use_raw_names")


def cf_doit():
    get_use_raw_names()