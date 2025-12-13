# coding:utf-8
from maya.OpenMaya import *
import pymel.core as pm
from . import bs_api


def get_fn_mesh_by_name(name):
    selection_list = MSelectionList()
    selection_list.add(name)
    dag_path = MDagPath()
    selection_list.getDagPath(0, dag_path)
    fn_mesh = MFnMesh(dag_path)
    return fn_mesh


def get_polygon_points_by_name(name, points):
    fn_mesh = get_fn_mesh_by_name(name)
    fn_mesh.getPoints(points)


def set_polygon_points_by_name(name, points):
    fn_mesh = get_fn_mesh_by_name(name)
    fn_mesh.setPoints(points)


def get_bs_ipt_ict(bs, index):
    selection_list = MSelectionList()
    selection_list.add(bs)
    depend_node = MObject()
    selection_list.getDependNode(0, depend_node)
    fn_depend_node = MFnDependencyNode(depend_node)
    iti = fn_depend_node.findPlug("it").elementByLogicalIndex(0).child(0).elementByLogicalIndex(index).child(0).\
        elementByLogicalIndex(6000)
    ipt = iti.child(3)
    ict = iti.child(4)
    return ipt, ict


def is_polygon(polygon):
    if polygon.type() != "transform":
        return False
    shape = polygon.getShape()
    if not shape:
        return False
    if shape.type() != "mesh":
        return False
    return True


def get_bs(polygon):
    bs = polygon.listHistory(type="blendShape")
    if bs:
        bs = bs[0]
    else:
        try:
            bs = pm.blendShape(polygon, automatic=True, n=polygon.name().split("|")[-1] + "_bs")[0]
        except TypeError:
            dup = polygon.duplicate()[0]
            bs = pm.blendShape(dup, polygon, frontOfChain=1, n=polygon.name().split("|")[-1] + "_bs")[0]
            pm.delete(dup)
            delete_target(bs.weight[0])
    return bs


def add_target(polygon, name):
    bs = get_bs(polygon)
    if bs.hasAttr(name):
        return
    ids = [bs.weight.elementByPhysicalIndex(i).logicalIndex() for i in range(bs.weight.numElements())]
    index = -1
    while True:
        index += 1
        if index not in ids:
            break
    bs.weight[index].set(1)
    pm.aliasAttr(name, bs.weight[index])
    bs_api.init_target(bs.name(), index)


def delete_target(weight_attr):
    index = weight_attr.logicalIndex()
    bs = weight_attr.node()
    pm.aliasAttr(weight_attr, rm=1)
    pm.removeMultiInstance(weight_attr, b=1)
    pm.removeMultiInstance(bs.it[0].itg[index], b=1)


def get_orig(polygon):
    # for shape in polygon.getShapes():
    #     if shape.io.get():
    #         if not shape.outputs(type="groupParts"):
    #             pm.delete(shape)
    # for shape in polygon.getShapes():
    #     if shape.io.get():
    #         if shape.outputs(type="groupParts"):
    #             return shape
    orig_list = [shape for shape in polygon.getShapes() if shape.io.get()]
    orig_list.sort(key=lambda x: len(set(x.outputs())))
    if orig_list:
        return orig_list[-1]


def cache_static_target(src, dst, target_name):
    bs = get_bs(dst)
    if not bs.hasAttr(target_name):
        add_target(dst, target_name)
        bs.attr(target_name).set(0)
    index = bs.attr(target_name).logicalIndex()
    orig = get_orig(dst)
    bs_api.edit_static_target(bs.name(), index, src.name(), orig.name())


def tool_cache_static_target(target_name):
    for polygon in pm.ls(sl=1, type="transform", o=1):
        if not is_polygon(polygon):
            continue
        cache_static_target(polygon, polygon, target_name)
