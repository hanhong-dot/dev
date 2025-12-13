# coding:utf-8
import os
import json
from .adPose2 import ADPose
from .adPose2 import bs
from .adPose2.general_ui import *


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


def get_fk_sdk_data():
    polygons = [pm.PyNode('PlaneSdkSystem|FKSdk_BodyDeformSdkPlane')]
    exist_target_names = []
    for polygon in polygons:
        _bs = bs.get_bs(polygon)
        for name in _bs.weight.elements():
            if name not in exist_target_names:
                exist_target_names.append(name)
    target_names = [target_name for target_name in ADPose.ADPoses.get_targets() if target_name in exist_target_names]
    ad_pose = list(target_names)
    bs_data = [bs.get_blend_shape_data(polygon, target_names) for polygon in polygons]
    data = dict(
        ad_pose=ad_pose,
        bs_data=bs_data,
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


def export_fk_sdk_data_ui():
    save_data_ui(default_scene_path, get_fk_sdk_data)


def load_fk_sdk_data(data):
    polygons = [pm.PyNode('PlaneSdkSystem|FKSdk_BodyDeformSdkPlane')]
    ADPose.ADPoses.add_by_targets(data["ad_pose"], polygons)
    for polygon, bs_data in zip(polygons, data["bs_data"]):
        bs.get_blend_shape_data(polygon, bs_data)


def load_fk_sdk_data_ui():
    load_data_ui(default_scene_path, load_fk_sdk_data)
