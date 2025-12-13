# coding:utf-8
from maya.OpenMaya import *
from maya.OpenMayaAnim import *


def str_to_dag_path(name, dag_path):
    selection_list = MSelectionList()
    selection_list.add(name)
    selection_list.getDagPath(0, dag_path)


def str_to_depend_node(name, depend_node):
    selection_list = MSelectionList()
    selection_list.add(name)
    selection_list.getDependNode(0, depend_node)


def get_mesh_points(polygon_name,  points):
    dag_path = MDagPath()
    str_to_dag_path(polygon_name, dag_path)
    fn_mesh = MFnMesh(dag_path)
    fn_mesh.getPoints(points)


def set_mesh_points(polygon_name,  points):
    dag_path = MDagPath()
    str_to_dag_path(polygon_name, dag_path)
    fn_mesh = MFnMesh(dag_path)
    fn_mesh.setPoints(points)


def get_ipt_ict(bs_name, index):
    depend_node = MObject()
    str_to_depend_node(bs_name, depend_node)
    fn_depend_node = MFnDependencyNode(depend_node)
    iti = fn_depend_node.findPlug("it").elementByLogicalIndex(0).child(0).elementByLogicalIndex(index).child(0).\
        elementByLogicalIndex(6000)
    ipt = iti.child(iti.numChildren()-2)
    ict = iti.child(iti.numChildren()-1)
    return ipt, ict


def set_plug_ids(plug, ids):
    fn_ids = MFnSingleIndexedComponent()
    ids_obj = fn_ids.create(MFn.kMeshVertComponent)
    fn_ids.addElements(ids)
    fn_components = MFnComponentListData()
    obj = fn_components.create()
    fn_components.add(ids_obj)
    plug.setMObject(obj)


def set_plug_points(plug, points):
    fn_points = MFnPointArrayData()
    obj = fn_points.create(points)
    plug.setMObject(obj)


def set_bs_id_points(bs_name, index, ids, points):
    ipt, ict = get_ipt_ict(bs_name, index)
    set_plug_points(ipt, points)
    set_plug_ids(ict, ids)


def set_bs_points(bs_name, index, all_points):
    ids = MIntArray()
    points = MPointArray()
    vtx_length = all_points.length()
    for vtx_id in range(vtx_length):
        if all_points[vtx_id].distanceTo(MPoint()) < 0.00001:
            continue
        ids.append(vtx_id)
        points.append(all_points[vtx_id])
    set_bs_id_points(bs_name, index, ids, points)


def get_plug_ids(plug, ids):
    fn_components = MFnComponentListData(plug.asMObject())
    component_length = fn_components.length()
    for component_id in range(component_length):
        fn_ids = MFnSingleIndexedComponent(fn_components[component_id])
        append_ids = MIntArray()
        fn_ids.getElements(append_ids)
        ids_length = append_ids.length()
        for i in range(ids_length):
            ids.append(append_ids[i])


def init_target(bs_name, index):
    set_bs_id_points(bs_name, index, MIntArray(), MPointArray())



def edit_static_target(bs_name, index, target_name, polygon_name):
    init_target(bs_name, index)
    polygon_points = MPointArray()
    get_mesh_points(polygon_name, polygon_points)
    target_points = MPointArray()
    get_mesh_points(target_name, target_points)
    vtx_length = target_points.length()
    points = MPointArray(vtx_length)
    for vtx_id in range(vtx_length):
        vector = target_points[vtx_id]-polygon_points[vtx_id]
        point = MPoint(vector)
        points.set(point, vtx_id)
    set_bs_points(bs_name, index, points)
