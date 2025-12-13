import os
from maya import cmds
from .. anim_ctrl_driver import load_x6_anim, load_mh_low_ctrl_anim


def play_mp4(path):
    # "playblast  -format qt -filename "D:/work/AI_mh/x6/x6_anis/v2/aaa.mov" -sequenceTime 0 -clearCache 0 -viewer 0 -showOrnaments 0 -fp 4 -percent 100 -compression "MPEG-4 Video" -quality 100 -widthHeight 1920 1080;"
    st = int(round(cmds.playbackOptions(q=1, min=1)))
    et = int(round(cmds.playbackOptions(q=1, max=1)))
    cmds.playblast(
        filename=path,
        format="qt",
        wh=(1920, 1080),
        st=st,
        et=et,
        compression="MPEG-4 Video",
        showOrnaments=False,
        viewer=False,
    )


def load_all_bs_anim(path, load_anim):
    if not os.path.isdir(path):
        return
    sel = cmds.ls(sl=1)
    for name in os.listdir(path):
        if not name.endswith(".json"):
            continue
        json_path = os.path.join(path, name).replace("\\", "/")
        cmds.select(sel)
        load_anim(json_path)
        ma_path = json_path.replace("_ai_result", "").replace(".json", ".ma")
        cmds.file(ma_path, f=1, pr=1, ea=1, type="mayaAscii")
        mp4_path = ma_path.replace(".ma", ".mov")
        play_mp4(mp4_path)


def doit():
    load_all_bs_anim(r"D:\work\AI_mh\x6\x6_anis\v2", load_x6_anim)