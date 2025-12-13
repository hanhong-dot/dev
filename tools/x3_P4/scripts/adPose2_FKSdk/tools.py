# coding:utf-8
import os
import json
from .adPose2 import ADPose
from .adPose2 import bs
from .adPose2.general_ui import *
import re
from .adPose2 import twist
from . import get_bs_info



def get_selected_polygons():
    polygons = []
    for polygon in pm.selected(type="transform"):
        shape = polygon.getShape()
        if shape is None:
            continue
        if shape.type() != "mesh":
            continue
        polygons.append(polygon)
    return polygons


def get_blend_shape_sdk_data():
    polygons = get_selected_polygons()
    exist_target_names = []
    for polygon in polygons:
        _bs = bs.get_bs(polygon)
        for name in _bs.weight.elements():
            if name not in exist_target_names:
                exist_target_names.append(name)
    target_names = [target_name for target_name in ADPose.ADPoses.get_targets() if target_name in exist_target_names]
    ad_pose = list(target_names)
    twist_data = twist.get_twist_data()
    target_names = list(target_names) + [row["target_name"] for row in twist_data]
    bs_data = [bs.get_blend_shape_data_use_scale(polygon, target_names) for polygon in polygons]
    data = dict(
        ad_pose=ad_pose,
        bs_data=bs_data,
        twist_data=twist_data,
    )
    return data


def get_old_ad_pose_blend_shape_sdk_data():
    polygons = get_selected_polygons()
    exist_target_names = []
    for polygon in polygons:
        _bs = bs.get_bs(polygon)
        for name in _bs.weight.elements():
            pattern = re.match("^(.+)_a([0-9]{1,3})_d([0-9]{1,3})$", name)
            if pattern is None:
                continue
            if name not in exist_target_names:
                exist_target_names.append(name)
    ad_pose = exist_target_names
    twist_data = []
    bs_data = [bs.get_blend_shape_data_use_scale(polygon, ad_pose) for polygon in polygons]
    data = dict(
        ad_pose=ad_pose,
        bs_data=bs_data,
        twist_data=twist_data,
    )
    return data


def write_json_data(path, data):
    with open(path, "w") as fp:
        json.dump(data, fp, indent=4)


def read_json_data(path):
    with open(path, "r") as fp:
        return json.load(fp)


def default_scene_path():
    base_path, _ = os.path.splitext(pm.sceneName())
    default_path = base_path+".json"
    return default_path


def save_data_ui(get_default_path, get_data):
    default_path = get_default_path()
    path, _ = QFileDialog.getSaveFileName(get_host_app(), "Export To Unity", default_path, "Json (*.json)")
    if not path:
        return
    data = get_data()
    write_json_data(path, data)
    QMessageBox.about(get_host_app(), u"提示", u"导出成功！")


def load_data_ui(get_default_path, load_data):
    default_path = get_default_path()
    path, _ = QFileDialog.getOpenFileName(get_host_app(), "Load Poses", default_path, "Json (*.json)")
    if not path:
        return
    data = read_json_data(path)
    load_data(data)
    QMessageBox.about(get_host_app(), u"提示", u"导入成功！")


def export_blend_shape_sdk_data_ui():
    save_data_ui(default_scene_path, get_blend_shape_sdk_data)


def export_old_blend_shape_sdk_data_ui():
    save_data_ui(default_scene_path, get_old_ad_pose_blend_shape_sdk_data)


def load_blend_shape_sdk_data(data):
    polygons = get_selected_polygons()
    ADPose.ADPoses.add_by_targets(data["ad_pose"], polygons)
    twist.set_twist_data(data["twist_data"], polygons)
    for polygon, bs_data in zip(polygons, data["bs_data"]):
        bs.set_blend_shape_data(polygon, bs_data)


def load_blend_shape_sdk_data_ui():
    load_data_ui(default_scene_path, load_blend_shape_sdk_data)


def node_name(joint):
    names = joint.fullPath().split("|")
    if names[0] == u"":
        names.pop(0)
    if names[0] != "Roots":
        names.pop(0)
    return "/".join(names)


def maya_matrix_to_unity_matrix(matrix):
    matrix.a01 *= -1
    matrix.a02 *= -1
    matrix.a10 *= -1
    matrix.a20 *= -1
    matrix.a30 *= -0.01
    matrix.a31 *= 0.01
    matrix.a32 *= 0.01
    return matrix


def matrix_to_unity_rotation(matrix):
    matrix = maya_matrix_to_unity_matrix(matrix)
    trans = pm.datatypes.TransformationMatrix(matrix)
    rotate = trans.getRotation().asQuaternion()
    return dict(x=rotate.x, y=rotate.y, z=rotate.z, w=rotate.w)


def get_twist_targets():
    twist_targets = []
    axis = "X"
    for joint in pm.ls(type="joint"):
        if not joint.hasAttr("twist"+axis):
            continue
        joint_name = joint.name().split("|")[-1].split(":")[-1]
        target_re = r"^{joint_name}_twist{axis}_(plus|minus)[0-9]+$".format(**locals())
        twistPoses = []
        driverNode = joint
        for attr in joint.listAttr():
            target_name = attr.name().split(".")[-1]
            if re.match(target_re, target_name):
                twist_targets.append(target_name)
    return twist_targets


def twist_to_unity_data(bs_nodes):
    twistElements = []
    axis = "X"
    info = ""
    for joint in pm.ls(type="joint"):
        if not joint.hasAttr("twist"+axis):
            continue
        joint_name = joint.name().split("|")[-1].split(":")[-1]
        target_re = r"^{joint_name}_twist{axis}_(plus|minus)[0-9]+$".format(**locals())
        twistPoses = []
        driverNode = joint
        for attr in joint.listAttr():
            target_name = attr.name().split(".")[-1]
            if not re.match(target_re, target_name):
                continue
            driverPose = twist.Twist(joint=joint).get_value_by_target(target_name)
            if driverPose is None:
                pm.warning(target_name + " is error pose")
                info += (target_name + " is error pose")
                info += "\r\n"
                continue
            drivenPoses = []
            bsinfo = get_bs_info.search_bsinfo(target_name, bs_nodes)
            twistPoses.append(dict(
                driverPose=driverPose,
                drivenPoses=drivenPoses,
                bsInfo=bsinfo,
            ))
        if len(twistPoses) == 0:
            continue
        bindPose = dict(bsInfo=u'bindPose', drivenPoses=[], driverPose=0.0)
        twistPoses.insert(0, bindPose)
        driverNode = node_name(joint)
        driverBasePose = matrix_to_unity_rotation(joint.getMatrix())
        twistElements.append(dict(
            driverNode=driverNode,
            driverBasePose=driverBasePose,
            axis=dict(x=1, y=0, z=0),
            twistPoses=twistPoses,
            drivenNodes=[],
        ))
    return twistElements, info


def add_selected_joint_to_fk_sdk_set():
    joints = pm.selected(type="joint")
    set_node = pm.ls("FkSdkJointSet")
    if set_node:
        set_node = set_node[0]
    else:
        set_node = pm.sets(name="FkSdkJointSet", em=1)
    for joint in joints:
        pm.sets(set_node, e=1, fe=joint)



# def export_twist_to_unit_ui():
#     save_data_ui(default_scene_path, twist_to_unity_data)


