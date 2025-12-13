# -*- coding: UTF-8 -*-
import json
from .adPose2 import ADPose
from .adPose2.ADPose import ADPoses
from . import sdr
from .adPose2.general_ui import *
from functools import partial
from . import get_bs_info
from . import tools
from . import fk_data
from maya import cmds
from maya.api.OpenMaya import *
INFO = ""


def to_unity_bs_data_and_successful_info(ifFullPath):
    global INFO
    INFO = ""
    successful = True
    data = to_unity_bs_data(ifFullPath)
    if isinstance(data, (str, unicode)):
        INFO += data
        successful = False
        data = {}
    return data, successful, INFO




def to_unity_bs_data(ifFullPath):
    all_targets = ADPoses.get_targets() + tools.get_twist_targets()
    bsMeshs_path_list, bs_nodes = get_bs_info.get_bsMeshs_list(all_targets, ifFullPath)

    targets = []
    for target in all_targets:
        for bs_node in bs_nodes:
            if bs_node.hasAttr(target):
                targets.append(target)
    real_targets = list(set(targets))
    real_targets.sort()

    target_name_comb_id = dict()
    comb_joint_id = 0

    # get pose to unity data
    joint_elements = []
    ad_poses = ADPoses.targets_to_ad_poses(real_targets)
    for ad, poses in ad_poses:
        target_names = [ad.target_name(pose) for pose in poses]
        driver_node = sdr.node_name(ad.joint)
        axis = 0
        driver_pose_data, up = sdr.driven_poses(ad.joint, poses)
        target_names.insert(0, "bindPose")
        bsinfo_list = [get_bs_info.search_bsinfo(target, bs_nodes) for target in target_names]
        rbf_poses = [dict(driverPose=driver, bsInfo=bsinfo)
                     for driver, bsinfo in zip(driver_pose_data, bsinfo_list)]

        joint_elements.append(dict(
            driverNode=driver_node,
            rbfPoses=rbf_poses,
            axis=axis,
            driverUpPose=up,
            k=2,
            isADsolveMode=True,
            is2DsolveMode=False
        ))

        for comb_target_id, target_name in enumerate(target_names):
            target_name_comb_id[target_name] = [comb_joint_id, comb_target_id]
        comb_joint_id += 1
    # comb data
    all_driven_nodes = []
    fk_sdk_set = fk_data.find_node_by_name("FkSdkJointSet")
    fk_sdk_joints = []
    joint_bind_pose = {}
    if fk_sdk_set is not None:
        fk_sdk_joints = pm.ls(fk_sdk_set.elements(), type="joint")
        for joint in fk_sdk_joints:
            name = fk_data.node_name(joint)
            joint_bind_pose[name] = joint.getMatrix()

    comb_elements = []
    comb_targets = [target_name for target_name in real_targets if ADPose.target_is_comb(target_name)]
    real_comb_targets = []
    for comb_target in comb_targets:
        for target_name in comb_target.split("_COMB_"):
            if target_name not in target_name_comb_id:
                message = u"导出模型缺失目标体：" + target_name
                pm.warning(message)
                return message
        ids = [target_name_comb_id[target_name] for target_name in comb_target.split("_COMB_")]
        ids = {"driverId%i" % i: {"elementId": element_id, "poseId": pose_id}
               for i, (element_id, pose_id) in enumerate(ids)}
        bs_info = get_bs_info.search_bsinfo(comb_target, bs_nodes)
        row = dict(
            drivenNodes=[],
            drivenPose=[],
            bsInfo=bs_info,
        )
        real_comb_targets.append(comb_target)
        row.update(ids)
        comb_elements.append(row)
        # comb joint data
        target_name = comb_target
        if len(fk_sdk_joints) == 0:
            continue
        ADPoses.set_pose_by_targets([target_name])
        matrix_list = []
        name_list = []
        for joint in fk_sdk_joints:
            name = fk_data.node_name(joint)
            bind_pose_matrix = joint_bind_pose[name]
            current_matrix = joint.getMatrix()
            if fk_data.matrix_eq(bind_pose_matrix, current_matrix):
                continue
            matrix_list.append(current_matrix * bind_pose_matrix.inverse())
            name_list.append(name)
            if name not in all_driven_nodes:
                all_driven_nodes.append(name)
        driven_pose = [fk_data.matrix_to_unity_position_rotation(matrix) for matrix in matrix_list]
        driven_nodes = [all_driven_nodes.index(name) for name in name_list]
        row["drivenNodes"] = driven_nodes
        row["drivenPose"] = driven_pose
        ADPoses.set_pose_by_targets([])

    ib_targets = [target_name for target_name in real_targets if ADPose.target_is_ib(target_name)]
    inbetween_elements = []
    for ib_target in ib_targets:
        comb_target, ib = ADPoses.ib_target_split(ib_target)
        if comb_target not in real_comb_targets:
            continue
        comb_id = real_comb_targets.index(comb_target)
        inbetween_value = float(ib)/60.0
        bs_info = get_bs_info.search_bsinfo(ib_target, bs_nodes)
        row = dict(
            drivenNodes=[],
            drivenPose=[],
            bsInfo=bs_info,
            combId=comb_id,
            inbetweenValue=inbetween_value,
        )
        inbetween_elements.append(row)
    twist_data, info = tools.twist_to_unity_data(bs_nodes)
    global INFO
    INFO += info
    data = dict(
        rbfElements=joint_elements,
        allDrivenNodes=[],
        bsMeshs=bsMeshs_path_list,
        twistElements=twist_data,
        combElements=comb_elements,
        inbetweenElements=inbetween_elements,
    )
    fk_data.update_fk_data(data)
    update_point_data(data, ifFullPath)
    update_untwist_data(data)
    check_joint_set_skin(data)
    return data


def check_joint_set_skin(data):
    if not cmds.objExists("FkSdkJointSet"):
        return
    set_joints = cmds.ls(cmds.sets("FkSdkJointSet", q=1), type="joint")
    set_joints = [joint.split("|")[-1] for joint in set_joints]
    export_joints = data.get("allDrivenNodes", [])
    export_joints = [joint.split("/")[-1] for joint in export_joints]
    global INFO
    for joint in set_joints:
        if joint in export_joints:
            continue
        INFO += (joint + " not in skinCluster")
        INFO += "\r\n"
        cmds.warning(joint + " not in skinCluster")


def is_polygon(polygon):
    if polygon.type() != "transform":
        return False
    shape = polygon.getShape()
    if not shape:
        return False
    if shape.type() != "mesh":
        return False
    return True


def add_attr(node, attr, *args, **kwargs):
    if cmds.objExists(node+"."+attr):
        return
    cmds.addAttr(node, ln=attr, *args, **kwargs)


def add_follow_mode_attr(joint):
    add_attr(joint, "pointFollowMode", at="enum", en="Point:Rotate:PointAndRotation:", k=1, dv=2)


def create_node(typ, name, parent=None):
    if cmds.objExists(name):
        return name
    if parent is not None:
        return cmds.createNode(typ, n=name, p=parent, ss=True)
    else:
        return cmds.createNode(typ, n=name, ss=True)


def connect_attr(src, dst):
    if cmds.isConnected(src, dst):
        return
    cmds.connectAttr(src, dst, f=1)


def link_by_follicle(plane, follicle, u, v):
    shape = create_node("follicle", follicle+"Shape", follicle)
    cmds.setAttr(shape+".v", 0)
    cmds.setAttr(follicle+".parameterU", u)
    cmds.setAttr(follicle+".parameterV", v)
    connect_attr(plane+".outMesh", shape+".inputMesh")
    connect_attr(plane+".worldMatrix", shape+".inputWorldMatrix")
    connect_attr(shape + ".outTranslate", follicle + ".translate")
    connect_attr(shape + ".outRotate", follicle + ".rotate")
    return follicle


def api_ls(*names):
    selection_list = MSelectionList()
    for name in names:
        selection_list.add(name)
    return selection_list


def link_polygon_joint(polygon, joint):
    joint = joint.name()
    polygon = polygon.name()
    add_follow_mode_attr(joint)
    for attr in ["t", "tx", "r", "rx"]:
        if cmds.listConnections(joint+"."+attr, s=1, d=0):
            return
    pff = create_node("transform", "PointFollowFollicles")
    cmds.setAttr(pff+".v", 0)
    cmds.setAttr(pff+".inheritsTransform", 0)
    fol = create_node("transform", joint+"PointFollowFollicle", pff)

    fn_mesh = MFnMesh(api_ls(polygon).getDagPath(0))
    point = fn_mesh.getClosestPoint(MPoint(cmds.xform(joint, q=1, ws=1, t=1)))[0]
    u, v, _ = fn_mesh.getUVAtPoint(point)
    link_by_follicle(polygon, fol, u, v)

    offset = create_node("transform", joint+"PointFollowOffset", fol)
    cmds.xform(offset, ws=1, m=cmds.xform(joint, q=1, ws=1, m=1))

    orig_t = cmds.getAttr(joint+".t")[0]
    orig_r = cmds.getAttr(joint+".r")[0]

    pc = cmds.parentConstraint(offset, joint)[0]
    bcp = create_node("blendColors", joint+"PointFollowPoint")
    bcr = create_node("blendColors", joint+"PointFollowRotation")
    connect_attr(pc+".constraintTranslate", bcp+".color1")
    cmds.setAttr(bcp+".color2", *orig_t)
    connect_attr(pc+".constraintRotate", bcr+".color1")
    cmds.setAttr(bcr+".color2", *orig_r)
    connect_attr(bcp+".outputR", joint+".tx")
    connect_attr(bcp+".outputG", joint+".ty")
    connect_attr(bcp+".outputB", joint+".tz")
    connect_attr(bcr+".outputR", joint+".rx")
    connect_attr(bcr+".outputG", joint+".ry")
    connect_attr(bcr+".outputB", joint+".rz")

    cd = joint+".pointFollowMode"
    cmds.setDrivenKeyframe(bcp + '.blender', cd=cd, dv=0, v=1, itt="linear", ott="linear")
    cmds.setDrivenKeyframe(bcp + '.blender', cd=cd, dv=1, v=0, itt="linear", ott="linear")
    cmds.setDrivenKeyframe(bcp + '.blender', cd=cd, dv=2, v=1, itt="linear", ott="linear")
    cmds.setDrivenKeyframe(bcr + '.blender', cd=cd, dv=0, v=0, itt="linear", ott="linear")
    cmds.setDrivenKeyframe(bcr + '.blender', cd=cd, dv=1, v=1, itt="linear", ott="linear")
    cmds.setDrivenKeyframe(bcr + '.blender', cd=cd, dv=2, v=1, itt="linear", ott="linear")


def tool_add_point_drive():
    joints = pm.selected(type="joint")
    polygons = filter(is_polygon, pm.selected(o=1, type="transform"))
    if len(joints) == 0:
        return pm.warning("please select a joint and polygon")
    tools.add_selected_joint_to_fk_sdk_set()
    polygon = polygons[0]
    for polygon in polygons:
        for joint in joints:
            link_polygon_joint(polygon, joint)
            if not joint.hasAttr("UnityPointDrivePolygon"):
                joint.addAttr("UnityPointDrivePolygon", at="message", m=1)
            if not pm.addAttr(joint.UnityPointDrivePolygon, q=1, m=1):
                pm.deleteAttr(joint.UnityPointDrivePolygon)
            if not joint.hasAttr("UnityPointDrivePolygon"):
                joint.addAttr("UnityPointDrivePolygon", at="message", m=1)
            if polygon not in joint.UnityPointDrivePolygon.inputs():
                for i in range(100):
                    if joint.UnityPointDrivePolygon[i].inputs():
                        continue
                    polygon.message.connect(joint.UnityPointDrivePolygon[i], f=1)
                    break


def find_point_drive_data():
    if not pm.ls("FkSdkJointSet"):
        return []
    set_node = pm.ls("FkSdkJointSet")[0]
    joint_polygon_data = []
    for joint in set_node.elements():
        if not joint.hasAttr("UnityPointDrivePolygon"):
            continue
        polygons = joint.UnityPointDrivePolygon.inputs(type="transform")
        if not polygons:
            continue
        for polygon in polygons:
            if not is_polygon(polygon):
                continue
            joint_polygon_data.append([joint, polygon])
    return joint_polygon_data


def get_skin_polygons():
    '''
    筛选所选中带bs的模型
    :return: transform list   模型列表
    '''
    mod_list = []
    select_list = pm.selected(type='transform')
    for sel in pm.selected(type='transform'):
        select_list.extend(sel.getChildren(ad=1, type='transform'))
    for select_mod in select_list:
        if select_mod.getShape():
            if select_mod.getShape().type() == 'mesh':
                if select_mod.listHistory(type="skinCluster"):
                    mod_list.append(select_mod)
    return list(set(mod_list))


def get_selected_polygons(ifFullPath):
    bsMeshs_path_list = [get_bs_info.get_mesh_full_path(mesh) for mesh in get_skin_polygons()]
    real_bsMeshs_path_list = []
    for mesh_path in bsMeshs_path_list:
        if not ifFullPath:
            real_bsMeshs_path_list.append(mesh_path.split('/')[-1])
        else:
            real_bsMeshs_path_list.append('/'.join(mesh_path.split('/')[1:]))
    return real_bsMeshs_path_list


def update_point_data(data, ifFullPath):
    selected_polygons = get_selected_polygons(ifFullPath)
    data["pointElements"] = []
    mesh_names = data["bsMeshs"]
    joint_names = data["allDrivenNodes"]
    bone_ids = set()
    for row in data["rbfElements"]:
        bone_ids.update(row.get("drivenNodes", []))
    for joint, polygon in find_point_drive_data():
        joint_name = sdr.node_name(joint)
        mesh_name = get_bs_info.get_mesh_full_path(polygon)
        if not ifFullPath:
            mesh_name = mesh_name.split('/')[-1]
        else:
            mesh_name = '/'.join(mesh_name.split('/')[1:])
        if joint_name not in joint_names:
            joint_names.append(joint_name)
        if mesh_name not in selected_polygons:
            continue
        if mesh_name not in mesh_names:
            mesh_names.append(mesh_name)
        mode_pos, mode_rot, mode_pos_rot = range(3)
        bone_id = joint_names.index(joint_name)
        if bone_id in bone_ids:
            mode = mode_pos
        else:
            mode = mode_pos_rot
        if cmds.objExists(joint.name()+".pointFollowMode"):
            mode = cmds.getAttr(joint.name()+".pointFollowMode")
            print ("get attr")
        data["pointElements"].append(dict(
            drivenBoneId=joint_names.index(joint_name),
            bsMeshId=mesh_names.index(mesh_name),
            mode=mode,
        ))


def update_untwist_data(data):
    untwist_data = []
    joints = [
        "Neck_M", "NeckPart1_M", "ElbowPart1_R", "ElbowPart2_R", "KneePart1_R", "KneePart2_R", "ElbowPart1_L",
        "ElbowPart2_L", "KneePart1_L", "KneePart2_L"]
    for name in joints:
        if len(pm.ls(name, type="joint")) != 1:
            continue
        if not pm.objExists(name):
            continue
        driver = pm.PyNode(name)
        driven_name = name[:-2]+"_No_Twist_Skin"
        if len(pm.ls(driven_name, type="joint")) != 1:
            driven_name = name + "_No_Twist_Skin"
        if len(pm.ls(driven_name, type="joint")) != 1:
            driven_name = "REG_" + name + "_No_Twist_Skin"
        if len(pm.ls(driven_name, type="joint")) != 1:
            continue
        driven = pm.PyNode(driven_name)
        space = driver.getParent()
        if "Part2" in name:
            space = space.getParent()
        untwist_data.append(dict(
            spaceBone=fk_data.node_name(space),
            driverBone=fk_data.node_name(driver),
            drivenBone=fk_data.node_name(driven),
            weight=1,
            axis=0
        ))
    data["untwistElements"] = untwist_data



class ExportBSToUnityTool(Tool):
    title = u"导出bs信息到unity"
    button_text = u"导出"

    def __init__(self, parent):
        Tool.__init__(self, parent)
        self.label = QLabel(u'请选择导出的角色是：')
        self.radioButton_1 = QRadioButton(u'主角', self)
        self.radioButton_2 = QRadioButton(u'NPC', self)
        self.buttonGrp = QButtonGroup()
        self.buttonGrp.addButton(self.radioButton_1)
        self.buttonGrp.addButton(self.radioButton_2)
        radiolayout = QHBoxLayout()
        self.kwargs_layout.addWidget(self.label)
        radiolayout.addWidget(self.radioButton_1)
        radiolayout.addWidget(self.radioButton_2)
        radiolayout.setContentsMargins(10, 5, 10, 5)
        self.kwargs_layout.addLayout(radiolayout)
        self.resize(200, 50)
        self.buttonGrp.buttonClicked.connect(self.checkRadioButton)
        self.radioButton_1.setChecked(1)
        self.info = 0

    def checkRadioButton(self):
        if self.radioButton_1.isChecked():
            self.info = 0
        elif self.radioButton_2.isChecked():
            self.info = 1
        return self.info

    def apply(self):
        if not pm.selected(type='transform'):
            return pm.warning(u'请选择带blendShape的模型或者模型组')
        self.close()
        sdr.save_data_ui(sdr.default_scene_path, partial(to_unity_bs_data, self.info))


