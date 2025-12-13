from .metahuman_api import *
import os
from ..anim_solve import solve_mh_low, arkit_solve
from . import metahuman_api as mh_api
from maya import cmds, mel


def open_file(path):
    ext = os.path.splitext(path)[-1][1:]
    typ = dict(ma="mayaAscii", mb="mayaBinary")[ext]
    try:
        cmds.file(path, o=1, f=1, typ=typ, ignoreVersion=True)
    except RuntimeError:
        pass
    cmds.currentUnit(time="30fps")


def open_myles():
    path = os.path.abspath(__file__+"/../scenes/Myles_full_rig_v3.ma")
    open_file(path)


def cut_mh_keys():
    cmds.select(cmds.ls("CTRL*", type="transform"))
    mel.eval('cutKey -clear -time ":"')
    cmds.select("DHIhead:head.r")
    mel.eval('cutKey -clear -time ":"')


def solve_all_bs_anim(path, solve_fun):
    if not os.path.isdir(path):
        return
    open_myles()
    for name in os.listdir(path):
        if not name.endswith((".fbx", ".FBX")):
            continue
        cut_mh_keys()
        fbx_path = os.path.join(path, name).replace("\\", "/")
        mh_api.retarget_metahuman_animation_sequence(fbx_path)
        solve_fun(os.path.splitext(fbx_path)[0]+".json")


def test_solve_all():
    path = r"D:/work/AI_mh/x6/x6_anis/v2"
    solve_all_bs_anim(path, solve_fun=arkit_solve)


def doit():
    test_solve_all()


