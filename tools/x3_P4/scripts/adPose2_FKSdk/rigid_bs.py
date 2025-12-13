# coding:utf-8
try:
    import numpy as np
except:
    print "can not import numpy"
try:
    from PySide.QtGui import *
    from PySide.QtCore import *
except ImportError:
    from PySide2.QtGui import *
    from PySide2.QtCore import *
    from PySide2.QtWidgets import *
from maya.api.OpenMaya import *
from maya.api.OpenMayaAnim import *
from maya import cmds
import pymel.core as pm
from .adPose2 import ADPose
from .adPose2 import twist


def get_cluster_ids(part_ids, near_ids, cluster_ids):
    for i in range(part_ids.shape[0]):
        new_cluster_ids = part_ids[np.any(near_ids[cluster_ids], axis=0)]
        if cluster_ids.shape[0] == new_cluster_ids.shape[0]:
            break
        else:
            cluster_ids = new_cluster_ids
    return cluster_ids


def rigid_align(src_point, dst_point):
    src_center = np.mean(src_point, axis=0)
    dst_center = np.mean(dst_point, axis=1)
    q1 = src_point - src_center
    q2 = dst_point - dst_center[:, None]
    h = np.matmul(q1.T, q2)
    u, s, vt = np.linalg.svd(h)
    u[:, 2] = np.cross(u[:, 0], u[:, 1], axis=1)
    vt[:, 2] = np.cross(vt[:, 0], vt[:, 1], axis=1)
    r = np.matmul(u, vt)
    q1 = np.matmul(q1, r)
    return q1 + dst_center[:, None]


def np_part_rigid(orig_points, ids, distance_limit, target_points):
    orig_part_points = orig_points[ids, :3]
    distances = np.linalg.norm(orig_part_points[None] - orig_part_points[:, None], axis=2)
    vtx_count = ids.shape[0]
    near_ids = distances < distance_limit
    part_ids = np.arange(vtx_count)

    reset_ids = part_ids.copy()
    cluster_data = []
    for i in range(vtx_count):
        if reset_ids.shape[0] < 1:
            break
        cluster_ids = get_cluster_ids(part_ids, near_ids, reset_ids[:1])
        reset_ids = np.setdiff1d(reset_ids, cluster_ids)
        cluster_data.append(cluster_ids)

    target_part_points = target_points[:, ids, :3]
    for cluster_ids in cluster_data:
        if cluster_ids.shape[0] < 2:
            continue
        rigid_points = rigid_align(orig_part_points[cluster_ids], target_part_points[:, cluster_ids])
        target_part_points[:, cluster_ids] = rigid_points
    target_points[:, ids, :3] = target_part_points
    return target_points


def api_ls(*names):
    selection_list = MSelectionList()
    for name in names:
        selection_list.add(name)
    return selection_list


def get_points(name):
    points = MFnMesh(api_ls(name).getDagPath(0)).getPoints(MSpace.kWorld)
    return points


def set_points(name, points):
    points = MPointArray(points)
    MFnMesh(api_ls(name).getDagPath(0)).setPoints(points, MSpace.kWorld)


def get_shell_ids(polygon):
    cluster_data = []
    face_ids = set(range(cmds.polyEvaluate(polygon, f=1)))
    for i in range(cmds.polyEvaluate(polygon, shell=1)):
        face_ids -= set(cmds.polySelect(polygon, ets=face_ids.pop(), ns=0, r=1))
        cmds.select(cmds.polyListComponentConversion(ff=1, tv=1))
        selected = MGlobal.getActiveSelectionList()
        dag_path, component = selected.getComponent(0)
        fn_ids = MFnSingleIndexedComponent(component)
        ids = fn_ids.getElements()
        cluster_data.append(np.array(list(ids)))
    return cluster_data


def np_shell_rigid(orig_points, cluster_data, target_points):
    for cluster_ids in cluster_data:
        if cluster_ids.shape[0] < 2:
            continue
        rigid_points = rigid_align(orig_points[cluster_ids, :3], target_points[:, cluster_ids, :3])
        target_points[:, cluster_ids, :3] = rigid_points
    return target_points


def tool_rigid_bake(targets):
    selected = MGlobal.getActiveSelectionList()
    dag_path, component = selected.getComponent(0)
    if component.apiTypeStr == "kMeshVertComponent":
        polygon_name = cmds.listRelatives(dag_path.fullPathName(), p=1)[0]
    else:
        polygon_name = dag_path.fullPathName()
    fn_mesh = MFnMesh(api_ls(polygon_name).getDagPath(0))
    target_points = []
    targets = [t for t in targets if "_COMB_" not in t] + [t for t in targets if "_COMB_" in t]
    ADPose.ADPoses.all_to_zero()
    orig_points = fn_mesh.getPoints(MSpace.kWorld)
    for target in targets:
        ADPose.ADPoses.set_pose_by_targets([target], all_targets=[])
        target_points.append(fn_mesh.getPoints(MSpace.kWorld))
        ADPose.ADPoses.set_pose_by_targets([target], all_targets=[], ib=0)
    if component.apiTypeStr == "kMeshVertComponent":
        radius = cmds.softSelect(q=1, ssd=1) * 2
        fn_ids = MFnSingleIndexedComponent(component)
        ids = fn_ids.getElements()
        rigid_points = np_part_rigid(np.array(orig_points), np.array(ids), radius, np.array(target_points))
    else:
        rigid_points = np_shell_rigid(np.array(orig_points), get_shell_ids(polygon_name), np.array(target_points))
    dst_polygon = pm.PyNode(polygon_name)
    src_polygon = pm.duplicate(dst_polygon)[0]
    src_fn = MFnMesh(api_ls(src_polygon.name()).getDagPath(0))
    for target, points in zip(targets, rigid_points):
        ADPose.ADPoses.set_pose_by_targets([target], all_targets=[])
        src_fn.setPoints(MPointArray(points))
        pm.select(src_polygon, dst_polygon)
        ADPose.ADPoses.edit_by_selected_target(target)
        ADPose.ADPoses.set_pose_by_targets([target], all_targets=[], ib=0)
    ADPose.ADPoses.all_to_zero()
    pm.delete(src_polygon)


def tool_bake_twist(targets):
    selected = MGlobal.getActiveSelectionList()
    dag_path, component = selected.getComponent(0)
    if component.apiTypeStr == "kMeshVertComponent":
        polygon_name = cmds.listRelatives(dag_path.fullPathName(), p=1)[0]
    else:
        polygon_name = dag_path.fullPathName()
    fn_mesh = MFnMesh(api_ls(polygon_name).getDagPath(0))
    target_points = []
    targets = [t for t in targets if "_COMB_" not in t] + [t for t in targets if "_COMB_" in t]
    ADPose.ADPoses.all_to_zero()
    orig_points = fn_mesh.getPoints(MSpace.kWorld)
    for target in targets:
        twist.to_target(target, 0)
    for target in targets:
        twist.to_target(target, 60)
        target_points.append(fn_mesh.getPoints(MSpace.kWorld))
        twist.to_target(target, 0)
    if component.apiTypeStr == "kMeshVertComponent":
        radius = cmds.softSelect(q=1, ssd=1) * 2
        fn_ids = MFnSingleIndexedComponent(component)
        ids = fn_ids.getElements()
        rigid_points = np_part_rigid(np.array(orig_points), np.array(ids), radius, np.array(target_points))
    else:
        rigid_points = np_shell_rigid(np.array(orig_points), get_shell_ids(polygon_name), np.array(target_points))
    dst_polygon = pm.PyNode(polygon_name)
    src_polygon = pm.duplicate(dst_polygon)[0]
    src_fn = MFnMesh(api_ls(src_polygon.name()).getDagPath(0))
    for target, points in zip(targets, rigid_points):
        twist.to_target(target, 60)
        src_fn.setPoints(MPointArray(points))
        pm.select(src_polygon, dst_polygon)
        twist.edit_target(target)
        twist.to_target(target, 0)
    ADPose.ADPoses.all_to_zero()
    pm.delete(src_polygon)


def doit():
    cmds.select("PL014C_HD_A_03")
    tool_rigid_bake(["Scapula_L_a40_d90"])

