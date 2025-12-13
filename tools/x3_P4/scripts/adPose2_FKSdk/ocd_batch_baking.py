# coding:utf-8
from .adPose2.general_ui import *
from .adPose2 import ADPose
from . import sdr
from .adPose2 import bs as bs_api
import json
import os
import re


def import_poses_data(json_filename):
    if os.path.exists(json_filename):
        json_filename = os.path.abspath(json_filename)
        with open(json_filename, 'r') as f:
            poses_data = json.load(f)
        return poses_data


def zero_ads(joints):
    ads = []
    for name in joints:
        ad = ADPose.ADPoses.load_by_name(name)
        if ad is None:
            continue
        ad.control.r.set(0, 0, 0)
        ads.append(ad)
    return ads


def get_poses_dict(poses_data):
    poses_dict = {}
    if poses_data:
        for one_pose in poses_data:
            match = re.match("(.+)_a([0-9]{1,3})_d([0-9]{1,3})", one_pose)
            if match:
                jnt_name, angle, direction = match.groups()
                angle, direction = int(angle), int(direction)
                if pm.objExists(jnt_name):
                    # if pm.PyNode(jnt_name).hasAttr(one_pose):
                    poses_dict.setdefault(jnt_name, [])
                    poses_dict[jnt_name].append(tuple([angle, direction]))
    return poses_dict


class DirLine(QLineEdit):
    def __init__(self):
        QLineEdit.__init__(self)
        self.setReadOnly(False)
        self.default_root = os.path.abspath(__file__ + "/../data/base_poses.json")
        self.setText(self.default_root)

    def mouseDoubleClickEvent(self, event):
        QLineEdit.mouseDoubleClickEvent(self, event)
        path, _ = QFileDialog.getOpenFileName(get_host_app(), u'选择一个json文件')
        if not path:
            return
        self.setText(path.replace("\\", "/"))


class BakeDeform_batch(Tool):
    title = u"烘焙修型自定义方案"
    button_text = u"导出蒙皮模型上的pose"

    def __init__(self, parent):
        Tool.__init__(self, parent)
        self.deform = MayaObjLayout(u"变形模型:")
        self.skin = MayaObjLayout(u"蒙皮模型:")
        self.kwargs_layout.addLayout(self.skin)
        self.kwargs_layout.addLayout(self.deform)

        self.poses_plan = QComboBox()
        self.plan_path = DirLine()
        self.kwargs_layout.addLayout(PrefixWeight(u"方案路径:", self.plan_path))
        self.plan_path.textChanged.connect(self.change_poses_plan)
        self.refresh_button = QPushButton(u'载入骨骼')
        self.kwargs_layout.addWidget(self.refresh_button)
        self.refresh_button.clicked.connect(self.change_poses_plan)

        self.joints = JointList()
        self.kwargs_layout.addLayout(self.joints)
        self.button = button(u"烘焙", self.bake_try_apply)
        self.kwargs_layout.addWidget(self.button)

    def change_poses_plan(self, json_filename=__file__ + "/../data/base_poses.json"):
        poses = import_poses_data(json_filename)
        self.poses_dict = {}
        self.poses_dict = get_poses_dict(poses)

        self.joints.list.clear()
        joint_list = self.poses_dict.keys()
        joint_list.sort()
        self.joints.list.addItems(joint_list)

    def increase_poses(self):
        joints = self.joints.get_joints()
        increased_joints = list(set(joints).difference(set(self.poses_dict.keys())))
        if increased_joints:
            increased_ads = zero_ads(increased_joints)
            for i, ad in enumerate(increased_ads):
                self.poses_dict[increased_joints[i]] = ad.get_poses()

    def get_targets(self):
        skin = self.skin.obj
        bs_node = bs_api.get_bs(skin)
        targets = ADPose.ADPoses.get_targets()
        targets = [t for t in targets if "_COMB_" not in t] + [t for t in targets if "_COMB_" in t]
        real_targets = [target for target in targets if bs_node.hasAttr(target)]
        return real_targets

    def apply(self):
        # 选择模型，导出蒙皮模型上的pose
        if not self.skin.obj:
            return pm.warning(u"请先加入蒙皮模型")
        sdr.save_data_ui(sdr.default_scene_path, self.get_targets)

    def bake_apply(self):
        # 从变形模型烘焙pose到蒙皮模型
        deform = self.deform.obj
        skin = self.skin.obj
        joints = self.joints.get_joints()
        self.increase_poses()

        ads = zero_ads(joints)
        for i, ad in enumerate(ads):
            poses = self.poses_dict[joints[i]]
            for pose in poses:
                ad.set_pose(pose)
                pm.select(deform, skin)
                pm.refresh()
                ad.edit_by_selected_ctrl_pose()
            pm.select(deform, skin)
            ad.control.r.set(0, 0, 0)

    def bake_try_apply(self):
        pm.undoInfo(openChunk=1)
        try:
            self.bake_apply()
        except Exception:
            pm.undoInfo(closeChunk=1)
            raise
        pm.undoInfo(closeChunk=1)

