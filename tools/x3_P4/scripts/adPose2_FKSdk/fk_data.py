# coding:utf-8
import json

import pymel.core as pm
from .adPose2 import ADPose
from .adPose2 import bs
from .adPose2 import twist


def find_node_by_name(name):
    nodes = pm.ls(name)
    if len(nodes) == 1:
        return nodes[0]


def get_sdk_plane():
    pass


def matrix_eq(m1, m2):
    u"""
    :param m1: 矩阵1
    :param m2: 矩阵2
    :return:
    判断两个矩阵是否相等，误差小于0.001
    """
    return all([abs(m1[i][j] - m2[i][j]) < 0.001 for i in range(4) for j in range(4)])


def node_name(joint):
    names = joint.fullPath().split("|")
    if names[0] == u"":
        names.pop(0)
    if names[0] != "Roots":
        names.pop(0)
    return "/".join(names)


def maya_matrix_to_unity_matrix(matrix):
    matrix = pm.datatypes.Matrix(matrix)
    matrix.a01 *= -1
    matrix.a02 *= -1
    matrix.a10 *= -1
    matrix.a20 *= -1
    matrix.a30 *= -0.01
    matrix.a31 *= 0.01
    matrix.a32 *= 0.01
    return matrix


def driven_poses(joint, poses):
    matrix_list = [pm.datatypes.EulerRotation(joint.jointOrient.get()).asMatrix()]
    for pose in poses:
        matrix = ADPose.pose_to_matrix(pose)
        matrix_list.append(matrix*matrix_list[0])
    vectors = []
    for matrix in matrix_list:
        v = pm.datatypes.Vector(1, 0, 0) * maya_matrix_to_unity_matrix(matrix)
        vectors.append(dict(
            x=v.x,
            y=v.y,
            z=v.z,
        ))
    up = pm.datatypes.Vector(0, 1, 0) * maya_matrix_to_unity_matrix(matrix_list[0])
    up = dict(
            x=up.x,
            y=up.y,
            z=up.z,
        )
    return vectors, up


def matrix_to_unity_position_rotation(matrix):
    matrix = maya_matrix_to_unity_matrix(matrix)
    trans = pm.datatypes.TransformationMatrix(matrix)
    position = trans.getTranslation("world")
    rotate = trans.getRotation().asQuaternion()
    return dict(position=dict(x=position.x, y=position.y, z=position.z),
                rotation=dict(x=rotate.x, y=rotate.y, z=rotate.z, w=rotate.w))


def get_target_names():
    target_names = []
    for name in ["FKSdk_BodyDeformSdkPlane", "BodyDeformSdkPlane"]:
        fk_sdk_plane = find_node_by_name(name)
        if fk_sdk_plane is None:
            continue
        _bs = bs.get_bs(fk_sdk_plane)
        for target_name in _bs.weight.elements():
            if target_name not in target_names:
                target_names.append(target_name)
    combs = list(filter(ADPose.target_is_comb, target_names))
    _target_names = []
    for ad, _ in ADPose.ADPoses.targets_to_ad_poses(target_names):
        for pose in ad.get_poses():
            _target_names.append(ad.target_name(pose))
    return _target_names + combs


def update_twist_data(data):
    fk_sdk_set = find_node_by_name("FkSdkJointSet")
    if fk_sdk_set is None:
        return
    joint_target_matrix = {}
    fk_sdk_joints = pm.ls(fk_sdk_set.elements(), type="joint")
    for joint in fk_sdk_joints:
        name = node_name(joint)
        joint_target_matrix[name] = dict(
            bindPose=joint.getMatrix()
        )

    for twist_elem in data["twistElements"]:
        driver_joint_name = twist_elem["driverNode"].split("/")[-1]
        if not pm.objExists(driver_joint_name):
            continue
        tw = twist.Twist(joint=pm.ls(driver_joint_name, type="joint")[0])
        for twist_pose in twist_elem["twistPoses"]:
            value = twist_pose["driverPose"]
            if value == 0:
                continue
            target_name = tw.value_to_target_name(value)
            twist.to_target(target_name, 60)
            pm.refresh()
            for joint in fk_sdk_joints:
                name = node_name(joint)
                bind_pose_matrix = joint_target_matrix[name]["bindPose"]
                current_matrix = joint.getMatrix()
                if matrix_eq(bind_pose_matrix, current_matrix):
                    continue
                joint_target_matrix[name][target_name] = current_matrix
            twist.to_target(target_name, 0)

    all_driven_nodes = data.setdefault("allDrivenNodes", [])

    for name in list(joint_target_matrix.keys()):
        if len(joint_target_matrix[name].keys()) == 1:
            del joint_target_matrix[name]

    for joint in joint_target_matrix.keys():
        if joint in all_driven_nodes:
            continue
        all_driven_nodes.append(joint)

    for twist_elem in data["twistElements"]:
        driver_joint_name = twist_elem["driverNode"].split("/")[-1]
        if not pm.objExists(driver_joint_name):
            continue
        tw = twist.Twist(joint=pm.ls(driver_joint_name, type="joint")[0])
        target_names = []
        for twist_pose in twist_elem["twistPoses"]:
            value = twist_pose["driverPose"]
            if value == 0:
                continue
            target_name = tw.value_to_target_name(value)
            target_names.append(target_name)
        driven_nodes = []
        twist_elem["drivenNodes"] = driven_nodes
        for joint in fk_sdk_joints:
            name = node_name(joint)
            if name not in joint_target_matrix:
                continue
            for target_name in target_names:
                if target_name not in joint_target_matrix[name]:
                    continue
                index = all_driven_nodes.index(name)
                if index in driven_nodes:
                    continue
                driven_nodes.append(index)

        matrix_data = []
        target_names.insert(0, "bindPose")
        for target_name in target_names:
            matrix_list = []
            for i in driven_nodes:
                target_matrix = joint_target_matrix[all_driven_nodes[i]]
                bind_pose = target_matrix.get("bindPose")
                if target_name == "bindPose":
                    matrix_list.append(bind_pose)
                else:
                    matrix_list.append(target_matrix.get(target_name, bind_pose) * bind_pose.inverse())
            matrix_data.append(matrix_list)
        driven_pose_data = [[matrix_to_unity_position_rotation(matrix) for matrix in matrix_list]
                            for matrix_list in matrix_data]
        for twist_pose, driven_pose in zip(twist_elem["twistPoses"], driven_pose_data):
            twist_pose["drivenPoses"] = driven_pose


def get_skin_joints():
    from maya import cmds
    joints = set()
    for polygon in cmds.ls(sl=1, type="transform"):
        for skin_cluster in cmds.ls(cmds.listHistory(polygon), type="skinCluster"):
            joints.update(cmds.skinCluster(skin_cluster, q=1, influence=1))
    return list(joints)


def update_fk_data(data=None):
    if data is None:
        data = dict()
    target_names = get_target_names()
    fk_sdk_set = find_node_by_name("FkSdkJointSet")
    if fk_sdk_set is None:
        return
    joint_target_matrix = {}
    fk_sdk_joints = pm.ls(fk_sdk_set.elements(), type="joint")
    skin_joints = pm.ls(get_skin_joints())
    fk_sdk_joints = [joint for joint in fk_sdk_joints if joint in skin_joints]
    if len(fk_sdk_joints) == 0:
        return
    for joint in fk_sdk_joints:
        name = node_name(joint)
        joint_target_matrix[name] = dict(
            bindPose=joint.getMatrix()
        )

    for target_name in target_names:
        ADPose.ADPoses.set_pose_by_targets([target_name])
        for joint in fk_sdk_joints:
            name = node_name(joint)
            bind_pose_matrix = joint_target_matrix[name]["bindPose"]
            current_matrix = joint.getMatrix()
            if matrix_eq(bind_pose_matrix, current_matrix):
                continue
            joint_target_matrix[name][target_name] = current_matrix
        pm.refresh()
    ADPose.ADPoses.set_pose_by_targets([])
    for name in list(joint_target_matrix.keys()):
        if len(joint_target_matrix[name].keys()) == 1:
            pass
            # del joint_target_matrix[name]
    joint_elements = data.setdefault("rbfElements", [])
    all_driven_nodes = data.setdefault("allDrivenNodes", [])
    targets = [target_name for target_name in target_names if "_COMB_" not in target_name]
    ad_poses = ADPose.ADPoses.targets_to_ad_poses(targets)
    target_name_data = []
    for joint in joint_target_matrix.keys():
        if joint in all_driven_nodes:
            continue
        all_driven_nodes.append(joint)
    for ad, poses in ad_poses:
        target_names = [ad.target_name(pose) for pose in poses]
        driven_nodes = []
        for joint in fk_sdk_joints:
            name = node_name(joint)
            if name not in joint_target_matrix:
                continue
            for target_name in target_names:
                if target_name not in joint_target_matrix[name]:
                    continue
                index = all_driven_nodes.index(name)
                if index in driven_nodes:
                    continue
                driven_nodes.append(index)
        driver_node = node_name(ad.joint)
        axis = 0

        driver_pose_data, up = driven_poses(ad.joint, poses)
        matrix_data = []
        target_names.insert(0, "bindPose")
        target_name_data.append(target_names)
        for target_name in target_names:
            matrix_list = []
            for i in driven_nodes:
                target_matrix = joint_target_matrix[all_driven_nodes[i]]
                bind_pose = target_matrix.get("bindPose")
                if target_name == "bindPose":
                    matrix_list.append(bind_pose)
                else:
                    matrix_list.append(target_matrix.get(target_name, bind_pose) * bind_pose.inverse())
            matrix_data.append(matrix_list)
        driven_pose_data = [[matrix_to_unity_position_rotation(matrix) for matrix in matrix_list]
                            for matrix_list in matrix_data]
        rbf_poses = [dict(driverPose=driver, drivenPoses=driven)
                     for driver, driven in zip(driver_pose_data, driven_pose_data)]
        new_element = dict(
            driverNode=driver_node,
            drivenNodes=driven_nodes,
            rbfPoses=rbf_poses,
            axis=axis,
            driverUpPose=up,
            k=2,
            isADsolveMode=True,
            is2DsolveMode=False
        )
        update_elem = find_update_elem(joint_elements, new_element)
        if update_elem is None:
            joint_elements.append(new_element)
        else:
            del new_element["rbfPoses"]
            update_elem.update(new_element)
            for new_pose in rbf_poses:
                update_pose = find_update_pose(update_elem["rbfPoses"], new_pose)
                if update_pose is None:
                    update_elem["rbfPoses"].append(new_pose)
                else:
                    update_pose["drivenPoses"] = new_pose["drivenPoses"]
    update_twist_data(data)


def find_update_elem(joint_elements, new_element):
    for old_elem in joint_elements:
        if old_elem["driverNode"] == new_element["driverNode"]:
            return old_elem


def find_update_pose(rfb_poses, new_pose):
    for old_pose in rfb_poses:
        if all([abs(old_pose["driverPose"][xyz]-new_pose["driverPose"][xyz]) < 0.0001 for xyz in "xyz"]):
            return old_pose

