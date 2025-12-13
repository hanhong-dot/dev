from maya import cmds

from maya.api.OpenMaya import *
from maya.api.OpenMayaAnim import *


class Shape(object):
    mesh = "mesh"
    nurbsSurface = "nurbsSurface"
    nurbsCurve = "nurbsCurve"


def is_shape(polygon_name, typ="mesh"):
    if not cmds.objExists(polygon_name):
        return False
    if cmds.objectType(polygon_name) != "transform":
        return False
    shapes = cmds.listRelatives(polygon_name, s=1, f=1)
    if not shapes:
        return False
    if cmds.objectType(shapes[0]) != typ:
        return False
    return True


def get_skin_cluster(polygon_name):
    if not is_shape(polygon_name, "mesh"):
        return
    shapes = cmds.listRelatives(polygon_name, s=1, f=1)
    for skin_cluster in cmds.ls(cmds.listHistory(polygon_name), type="skinCluster"):
        for shape in cmds.skinCluster(skin_cluster, q=1, geometry=1):
            for long_shape in cmds.ls(shape, l=1):
                if long_shape in shapes:
                    return skin_cluster


def py_to_m_array(cls, _list):
    result = cls()
    for elem in _list:
        result.append(elem)
    return result


def api_ls(*names):
    selection_list = MSelectionList()
    for name in names:
        selection_list.add(name)
    return selection_list


def swap_skin(polygon_name, src_joint, dst_joint):
    if cmds.referenceQuery(polygon_name, isNodeReferenced=1):
        return
    skin_cluster = get_skin_cluster(polygon_name)
    if not skin_cluster:
        return
    joints = cmds.skinCluster(skin_cluster, q=1, influence=1)
    if src_joint not in joints:
        return
    if dst_joint not in joints:
        cmds.skinCluster(skin_cluster, e=1, lw=True, ai=dst_joint, wt=0)
    joints = cmds.skinCluster(skin_cluster, q=1, influence=1)
    shape, components = api_ls(polygon_name + ".vtx[*]").getComponent(0)
    fn_skin = MFnSkinCluster(api_ls(get_skin_cluster(polygon_name)).getDependNode(0))
    influences = MIntArray([joints.index(src_joint), joints.index(dst_joint)])
    weights = fn_skin.getWeights(shape, components, influences)
    for i in range(0, len(weights), 2):
        weights[i+1] = weights[i] + weights[i+1]
        weights[i] = 0
    fn_skin.setWeights(shape, components, influences, MDoubleArray(weights))


def swap_skin_all(joints):
    for src_joint, dst_joint in joints:
        ls_joints = cmds.ls(src_joint, dst_joint, type="joint")
        if len(ls_joints) != 2:
            continue
        skin_clusters = cmds.listConnections(src_joint, dst_joint, s=0, d=1, type="skinCluster") or []
        skin_clusters = list(set(skin_clusters))
        for skin_cluster in skin_clusters:
            mesh = cmds.skinCluster(skin_cluster, q=1, geometry=1)[0]
            polygon_name = cmds.listRelatives(mesh, p=1)[0]
            swap_skin(polygon_name, src_joint, dst_joint)


def add_scale_joint(joint):
    scale_joint = joint + "_Scale"
    if not cmds.objExists(scale_joint):
        scale_joint = cmds.joint(joint, n=joint+"_Scale")
    for attr in ["s", "sx", "sy", "sz"]:
        joint_attr = joint+"."+attr
        scale_attr = scale_joint+"."+attr
        for src_attr in cmds.listConnections(joint+"."+attr, s=1, d=0, p=1) or []:
            cmds.disconnectAttr(src_attr, joint_attr)
            cmds.connectAttr(src_attr, scale_attr, f=1)
        cmds.setAttr(joint+".s", 1, 1, 1)
    swap_skin_all([[joint, scale_joint]])


def add_selected_scale_joint():
    for joint in cmds.ls(sl=1, type="joint"):
        if joint.endswith("_Scale"):
            continue
        add_scale_joint(joint)


def doit():
    add_selected_scale_joint()


if __name__ == '__main__':
    doit()