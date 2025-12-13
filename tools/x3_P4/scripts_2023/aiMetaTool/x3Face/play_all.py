import json
import os.path

from maya import cmds
from .load_bs_anim import load_bs_anim

def play_mp4(path, st, et, sound):
    # "playblast  -format qt -filename "D:/work/AI_mh/x6/x6_anis/v2/aaa.mov" -sequenceTime 0 -clearCache 0 -viewer 0 -showOrnaments 0 -fp 4 -percent 100 -compression "MPEG-4 Video" -quality 100 -widthHeight 1920 1080;"
    # st = int(round(cmds.playbackOptions(q=1, min=1)))
    # et = int(round(cmds.playbackOptions(q=1, max=1)))
    cmds.playblast(
        filename=path,
        format="qt",
        wh=(1920, 1080),
        st=st,
        et=et,
        sound=sound,
        compression="MPEG-4 Video",
        showOrnaments=False,
        viewer=False,
    )


def play_one(name):
    for polygon in ["rom55", "face_v1", "face_v2", "face_v3", "face_v4"]:
        path = f"D:/work/x3_ai_face/x3_face_to_xinghuo/iphone_anim/{polygon}/{name}_aiMeta.json"
        cmds.select(polygon)
        load_bs_anim(path)
    image_path = f"D:/work/x3_ai_face/x3_face_anim/{name}_iPhone/frame.00001.jpg"
    cmds.currentTime(1)
    cmds.setAttr("imagePlaneShape1.useFrameExtension", False)
    cmds.setAttr("imagePlaneShape1.imageName", image_path, type="string")
    cmds.setAttr("imagePlaneShape1.useFrameExtension", True)
    st = 1
    frames = set(cmds.keyframe(cmds.ls(type="animCurveTU"), q=1, tc=1))
    et = max(map(int, frames))
    mp4_path = f"D:/work/x3_ai_face/x3_face_to_xinghuo/play_mp4/{name}.mp4"
    sound = f"{name}_iPhone"
    cmds.select(cl=1)
    play_mp4(mp4_path, st, et, sound=sound)


def play_all():
    for i in [3, 4, 5, 6, 7]:
        play_one(f"MySlate_{i}")


def doit():
    play_all()
    # play_one("MySlate_4")