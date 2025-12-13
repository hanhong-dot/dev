from maya import cmds
import os

try:
    from PySide.QtGui import *
    from PySide.QtCore import *
except ImportError:
    from PySide2.QtGui import *
    from PySide2.QtCore import *
    from PySide2.QtWidgets import *

from ..bs import find_bs
from ..anim_driver import read_text_targets
from ..poses_to_bs import *

def export_obj(export_path):
    options = "groups=1;ptgroups=1;materials=0;smoothing=1;normals=0"
    cmds.file(export_path, options=options, pr=1, es=1, type="OBJexport", f=1)

def export_bs_obj(polygon, obj_dir, targets):
    _bs = find_bs(polygon)
    cmds.select(polygon)
    for target in targets:
        cmds.setAttr(_bs+"."+target, 0)
    path = os.path.join(obj_dir, "base" + ".obj")
    export_obj(path)
    for target in targets:
        cmds.setAttr(_bs+"."+target, 1)
        path = os.path.join(obj_dir, target+".obj")
        export_obj(path)
        cmds.setAttr(_bs+"."+target, 0)

def export_x3_55_objs(obj_dir):
    polygons = get_selected_polygons()
    comb = convert_comb()
    cmds.select(comb)
    dup_polygons = ai_meta_convert_sel_blend_shape()


def x3_face_convert_sel_blend_shape():
    polygons = get_selected_polygons()
    frames = [1, 3, 5, 7, 9]
    poses = ["anger", "confused", "smile", "sad", "surprise"]
    dup_polygons = []
    cmds.currentTime(0)
    for polygon in polygons:
        dup_polygon = cmds.duplicate(polygon, n=polygon.split("|")[-1].split(":")[-1])[0]
        dup_polygons.append(dup_polygon)
    for frame, pose in zip(frames, poses):
        cmds.currentTime(frame)
        for polygon, dup_polygon in zip(polygons, dup_polygons):
            temp = cmds.duplicate(polygon)[0]
            _bs = bs.get_bs(dup_polygon)
            bs.re_real_target(dup_polygon, _bs, temp, pose)
            cmds.delete(temp)
    cmds.currentTime(0)
    print(dup_polygons)
    return dup_polygons




def export_x3_face_objs(obj_dir):
    polygon = convert_comb()
    # cmds.polyTriangulate(polygon, ch=1)
    cmds.select(polygon)
    dup_polygon = x3_face_convert_sel_blend_shape()[0]
    # cmds.select(dup_polygon)
    # targets = ["anger", "confused", "smile", "sad", "surprise"]
    # export_bs_obj(dup_polygon, obj_dir, targets)
    # cmds.delete(polygon)



def doit():
    cmds.select("ST_BODY:ST_Head")
    export_x3_55_objs(r"D:\work\x3_ai_face\st_aiMeta_55")
    # export_x3_face_objs("D:/work/x3_ai_face/st_faces")
