# coding:utf-8
import re
from .adPose2 import ADPose
import math
from .adPose2.general_ui import *
import json
import os
from maya.OpenMaya import *
from maya.OpenMayaAnim import *
from .adPose2 import bs as bs_api

def find_history_node(polygon, typ):
    nodes = pm.listHistory(polygon, type=typ)
    if nodes is None or len(nodes) == 0:
        return pm.warning("can not find " + typ)
    node = nodes[0]
    return node


def dot_qq(q1, q2):
    return q1.x * q2.x + q1.y * q2.y + q1.z * q2.z + q1.w * q2.w


def mul_qd(q, w):
    return pm.datatypes.Quaternion(q.x*w, q.y*w, q.z*w, q.w*w)


def add_qq(q1, q2):
    return pm.datatypes.Quaternion(q1.x + q2.x, q1.y + q2.y, q1.z + q2.z, q1.w + q2.w)


def slerp(q1, q2, t):
    cos_a = dot_qq(q1, q2)
    if cos_a < 0:
        cos_a = - cos_a
        mul_qd(q2, -1)
    if cos_a > 0.999999999:
        w1, w2 = 1-t, t
    else:
        sin_a = math.sqrt(1-cos_a*cos_a)
        a = math.atan2(sin_a, cos_a)
        in_sin_a = 1.0/sin_a
        w1 = math.sin((1-t)*a) * in_sin_a
        w2 = math.sin(t * a) * in_sin_a
    return add_qq(mul_qd(q1, w1), mul_qd(q2, w2))


def matrix_to_position_rotation(matrix):
    trans = pm.datatypes.TransformationMatrix(matrix)
    translate = trans.getTranslation("world")
    rotation = trans.getRotation().asQuaternion()
    return translate, rotation


def position_rotation_to_matrix(position, rotation):
    trnas = pm.datatypes.TransformationMatrix(rotation.matrix)
    trnas.setTranslation(position, space="world")
    return trnas.matrix


def blend_trs(matrix_list, weight_list):
    out_translate = pm.datatypes.Point(0, 0, 0)
    out_rotation = pm.datatypes.Quaternion(pm.datatypes.Quaternion.identity)
    for matrix_value, weight_value in reversed(zip(matrix_list, weight_list)):
        if weight_value < 0.00001:
            continue
        position, rotation = matrix_to_position_rotation(matrix_value)
        out_translate += weight_value * position
        out_rotation *= slerp(pm.datatypes.Quaternion.identity, rotation, weight_value)
    return out_translate,  out_rotation


def create_attach(prefix, parent, i, pl):
    msa = pm.group(em=1, p=parent, n=prefix+"Attach")
    pm.createNode("cMuscleSurfAttach", p=msa, n=prefix+"AttachShape")
    pl.worldMesh.connect(msa.surfIn)
    msa.rotateOrder.connect(msa.inRotOrder)
    msa.outTranslate.connect(msa.translate)
    msa.outRotate.connect(msa.rotate)
    msa.edgeIdx1.set(i * 4 + 0)
    msa.edgeIdx2.set(i * 4 + 3)
    msa.uLoc.set(0.5)
    msa.vLoc.set(0.5)
    return msa


def create_plane(name, parent, transforms, r):
    u"""
    :param name: 前缀
    :param parent: 父对象
    :param transforms: 空组
    :param r: 半径
    :return: 面片模型
    """
    pl = pm.polyPlane(w=1, h=1, sx=1, sy=1, ch=1)[0]
    pl.r.set(90, 0, 90)
    pl.s.set(r, r, r)
    pm.makeIdentity(apply=1, r=1, s=1)
    planes = []
    for transform in transforms:
        dup = pl.duplicate()[0]
        dup.setMatrix(transform.getMatrix(ws=1), ws=1)
        planes.append(dup)
    pm.delete(pl)
    if len(planes) > 1:
        pl = pm.polyUnite(planes, ch=0)[0]
    else:
        pl = planes[0]
        pm.makeIdentity(pl, apply=1, t=1, r=1, s=1)
    pl.setParent(parent)
    pl.rename(name)
    pl.v.set(0)
    return pl


def get_shape(polygon):
    for shape in polygon.getShapes():
        if not shape.io.get():
            return shape


def assert_geometry(geometry=None, shape_type="mesh"):
    u"""
    :param geometry: 几何体
    :param shape_type: 形节点类型
    :return:
    判断物体是否为集合体
    """
    if geometry is None:
        selected = pm.selected(o=1)
        if len(selected) == 0:
            return pm.warning("please select a " + shape_type)
        geometry = selected[0]
    if geometry.type() == shape_type:
        return geometry.getParent()
    if geometry.type() != "transform":
        return pm.warning("please select a " + shape_type)
    shape = get_shape(geometry)
    if not shape:
        return pm.warning("please select a " + shape_type)
    if shape.type() != shape_type:
        return pm.warning("please select a " + shape_type)
    return geometry


def get_skin_cluster(polygon=None):
    u"""
    :param polygon: 多边形
    :return: 蒙皮节点
    """
    if polygon is None:
        polygon = assert_geometry(shape_type="mesh")
    if polygon is None:
        return
    for history in polygon.history(type="skinCluster"):
        return history
    pm.warning("\ncan not find skinCluster")


def get_weight_data(polygon):
    polygon = assert_geometry(polygon, shape_type="mesh")
    if polygon is None:
        return
    sk = get_skin_cluster(polygon)
    joints = sk.getInfluence()
    indices = MIntArray()
    indices.setLength(len(joints))
    for i, _ in enumerate(joints):
        indices[i] = i
    selected = MSelectionList()
    selected.add(sk.name())
    selected.add(get_shape(polygon).name()+".vtx[*]")
    depend_node = MObject()
    selected.getDependNode(0, depend_node)
    fn_skin = MFnSkinCluster(depend_node)
    path = MDagPath()
    components = MObject()
    weights = MDoubleArray()
    selected.getDagPath(1, path, components)
    fn_skin.getWeights(path, components, indices, weights)
    return weights, len(joints), polygon.getShape().numVertices()


def set_weight_data(polygon=None, weights=None):
    polygon = assert_geometry(polygon, shape_type="mesh")
    if polygon is None:
        return pm.warning("can not find polygon")
    sk = get_skin_cluster(polygon)
    joints = sk.getInfluence()
    indices = MIntArray()
    indices.setLength(len(joints))
    for i, _ in enumerate(joints):
        indices[i] = i
    selected = MSelectionList()
    selected.add(sk.name())
    selected.add(get_shape(polygon).name()+".vtx[*]")
    depend_node = MObject()
    selected.getDependNode(0, depend_node)
    fn_skin = MFnSkinCluster(depend_node)
    path = MDagPath()
    components = MObject()
    selected.getDagPath(1, path, components)
    fn_skin.setWeights(path, components, indices, weights)


def init_plane_weights(plane=None):
    weights, joint_len, vtx_len = get_weight_data(plane)
    for face_id in range(vtx_len/4):
        for joint_id in range(joint_len):
            sum_weights = 0.0
            for i in range(4):
                vtx_id = face_id * 4 + i
                weight_id = vtx_id * joint_len + joint_id
                weight = weights[weight_id]
                sum_weights += weight
            weight = sum_weights / 4.0
            for i in range(4):
                vtx_id = face_id * 4 + i
                weight_id = vtx_id * joint_len + joint_id
                weights[weight_id] = weight
    set_weight_data(plane, weights)


class SdrJointDriver(Tool):
    title = u"自动骨骼驱动"
    button_text = u"解算"

    def __init__(self, parent):
        Tool.__init__(self, parent)
        self.bc = Number(1, 10000000, 6)
        self.mi = Number(1, 10000000, 8)
        self.opt = Number(1, 10000000, 50)
        self.it = Number(1, 10000000, 35)
        self.kwargs_layout.addLayout(PrefixWeight(u"bonesCount：", self.bc, 100))
        self.kwargs_layout.addLayout(PrefixWeight(u"maxInfluence：", self.mi, 100))
        self.kwargs_layout.addLayout(PrefixWeight(u"optSteps：", self.opt, 100))
        self.kwargs_layout.addLayout(PrefixWeight(u"iterTimes：", self.it, 100))

    def apply(self):
        bc = self.bc.value()
        mi = self.mi.value()
        opt = self.opt.value()
        it = self.it.value()
        convert_joint_sdk(bc=bc, mi=mi, opt=opt, it=it)


def find_kwargs():
    targets = ADPose.ADPoses.get_targets()
    polygons = ADPose.get_selected_polygons()
    if len(polygons) != 1:
        return pm.warning("please selected one polygon")
    polygon = polygons[0]
    skin = find_history_node(polygon, "skinCluster")
    ads = []
    unlocks = []
    for joint in skin.influenceObjects():
        if joint.liw.get():
            continue
        if "sdBones_" in joint.name():
            continue
        unlocks.append(joint)
        ad = ADPose.ADPoses.load_by_name(joint.name())
        if ad is None:
            continue
        if not ad.joint.hasAttr("angle"):
            continue
        ads.append(ad)
    joint_names = [ad.prefix for ad in ads]
    key_targets = []
    for target in targets:
        if any([prefix in target for prefix in joint_names]):
            key_targets.append(target)
    key_targets = [[]] + [[t] for t in key_targets if "_COMB_" not in t] + [[t] for t in key_targets if "_COMB_" in t]
    return polygon, unlocks, targets, ads, key_targets


def auto_key():
    polygon, unlocks, targets, ads, key_targets = find_kwargs()
    ctrl_list = [ad.control for ad in ads]
    for i, t in enumerate(key_targets):
        pm.currentTime(i + 1)
        ADPose.ADPoses.set_pose_by_targets(t, targets)
        pm.setKeyframe(ctrl_list)
    tr = [1, len(key_targets)]
    pm.playbackOptions(max=tr[0], min=tr[1], ast=tr[0], aet=tr[1])


def convert_joint_ani(bc=8, mi=8, opt=50, it=35):
    polygon, unlocks, targets, ads, key_targets = find_kwargs()
    st = int(round(pm.playbackOptions(q=1, min=1)))
    et = int(round(pm.playbackOptions(q=1, max=1)))
    tr = [st, et]
    s = polygon.name()
    t = polygon.name()
    m = 0
    fps = [u'film', u'ntsc', u'palf', u'40fps', u'ntscf'].index(pm.currentUnit(q=1, t=1))
    wb = [inf.name() for inf in unlocks]
    kwargs = dict(s=s, t=t, m=m, fps=fps, wb=wb, tr=tr, bc=bc, mi=mi, opt=opt, it=it)
    pm.SSDR2(s=s, t=t, m=m, fps=fps, wb=wb, tr=tr, bc=bc, mi=mi, opt=opt, it=it)
    bs_node = find_history_node(polygon, "blendShape")
    bs_node.envelope.set(0)


def sdk_group():
    if pm.objExists("PlaneSdkSystem"):
        group = pm.PyNode("PlaneSdkSystem")
    else:
        group = pm.group(em=1, n="PlaneSdkSystem")
    group.inheritsTransform.set(1)
    return group


def plane_sdk():
    # auto key
    polygon, unlocks, targets, ads, key_targets = find_kwargs()
    tr = [1, len(key_targets)]
    wb = [inf.name() for inf in unlocks]

    mtj_joints = pm.ls("|sdBones_*", type="joint")
    bs_node = find_history_node(polygon, "blendShape")
    bs_node.envelope.set(0)

    mtj_matrix_data = [[] for _ in mtj_joints]
    unlock_matrix_data = [[] for _ in wb]

    pose_attr_list = []

    for key_target in key_targets:
        if not key_target:
            pose_attr_list.append(None)
        else:
            key_target = key_target[0]
            pose_attr = ADPose.ADPoses.add_by_target(key_target)
            pose_attr_list.append(pose_attr)

    pose_weight_data = []
    planes = []
    prefix = "_".join(sorted(wb))
    group = sdk_group()
    for t in range(tr[0], tr[1]+1):
        pm.currentTime(t)
        for mtj_joint, mtj_matrix_list in zip(mtj_joints, mtj_matrix_data):
            mtj_matrix_list.append(mtj_joint.getMatrix(ws=1))
        for unlock_joint, unlock_matrix_list in zip(unlocks, unlock_matrix_data):
            unlock_matrix_list.append(unlock_joint.getMatrix(ws=1))
        weight_list = [1] + [attr.get() for attr in pose_attr_list if attr is not None]
        pose_weight_data.append(weight_list)
        pose_attr = pose_attr_list[t-1]
        if pose_attr is None:
            plane_name = "_".join(wb)
        else:
            plane_name = pose_attr.name().split(".")[-1]
        plane = create_plane(plane_name+"_PL", group, mtj_joints, 0.1)
        planes.append(plane)
    pm.currentTime(1)
    bs_plane = planes[0].duplicate()[0]
    bs = pm.blendShape(planes[1:], bs_plane)[0]
    for t, name in enumerate(bs.weight.elements()):
        pm.setKeyframe(bs, attribute=name, v=0, t=t + 1)
        pm.setKeyframe(bs, attribute=name, v=1, t=t + 2)
        pm.setKeyframe(bs, attribute=name, v=0, t=t + 3)

    m = 2
    s = bs_plane.name()
    t = planes[0].name()
    fps = [u'film', u'ntsc', u'palf', u'40fps', u'ntscf'].index(pm.currentUnit(q=1, t=1))
    bc = 8
    mi = 8
    opt = 50
    it = 35
    pm.SSDR2(s=s, t=t, m=m, fps=fps, wb=wb, tr=tr, bc=bc, mi=mi, opt=opt, it=it)

    init_plane_weights(planes[0])
    for t in range(tr[0]+1, tr[1]+1):
        pm.currentTime(t)
        target = pose_attr_list[t-1].name().split(".")[-1]
        pm.select(planes[t-1], planes[0])
        ADPose.ADPoses.edit_by_selected_target(target)
    pm.delete(bs_plane)
    mtj_parent_list = []

    for mtj_joint, mtj_matrix_list in zip(mtj_joints, mtj_matrix_data):
        offset_length_unlock = {}
        for unlock_joint, unlock_matrix_list in zip(unlocks, unlock_matrix_data):
            offset_length = 0.0
            pre_point = pm.datatypes.Point() * (mtj_matrix_list[0] * unlock_matrix_list[0].inverse())
            for mtj_matrix, unlock_matrix in zip(mtj_matrix_list, unlock_matrix_list):
                offset_point = (pm.datatypes.Point() * (mtj_matrix * unlock_matrix.inverse())) - pre_point
                offset_length += offset_point.length()
            offset_length_unlock[offset_length] = unlock_joint
        parent = offset_length_unlock[min(offset_length_unlock.keys())]
        parent_id = unlocks.index(parent)
        mtj_parent_list.append(parent_id)

    prefix = "_".join(sorted(wb))
    pm.delete(planes[1:])
    index = - 1
    for mtj_joint, parent_id, mtj_matrix_list in zip(mtj_joints, mtj_parent_list, mtj_matrix_data):
        attrs = ["tx", "ty", "tz", "rx", "ry", "rz"]
        for attr in attrs:
            pm.delete(mtj_joint.attr(attr).inputs())
        mtj_joint.setParent(unlocks[parent_id])
        mtj_joint.rename("corrective_"+unlocks[parent_id].name()+"_sd_0")
        mtj_joint.jointOrient.set(0, 0, 0)

        index += 1
        attach = create_attach(prefix + "%02d" % (index+1), group, index, planes[0])
        attach.rename(mtj_joint.name().replace("_sd_", "_attach_"))
        attrs = ["tx", "ty", "tz", "rx", "ry", "rz"]
        for attr in attrs:
            pm.delete(mtj_joint.attr(attr).inputs())
        mtj_joint.setParent(unlocks[parent_id])
        # mtj_joint.rename(prefix+"_%02d_joint" % (index+1))
        mtj_joint.jointOrient.set(0, 0, 0)
        pm.parent(pm.parentConstraint(attach, mtj_joint), attach)
        pose_matrix_list = []
        for mtj_matrix, parent_matrix, t in zip(mtj_matrix_list, unlock_matrix_data[parent_id], range(tr[0], tr[1]+1)):
            matrix = mtj_matrix * parent_matrix.inverse()
            pose_matrix_list.append(matrix)
        bind_matrix_inverse = pose_matrix_list[0].inverse()
        for i, matrix in enumerate(pose_matrix_list[1:]):
            pose_matrix_list[i+1] = pose_matrix_list[i+1] * bind_matrix_inverse
        for pose_attr, pose_matrix in zip(pose_attr_list, pose_matrix_list):
            if pose_attr is None:
                name = "bindPoseMatrix"
            else:
                name = pose_attr.name().split(".")[-1]+"Matrix"
            mtj_joint.addAttr(name, at="matrix", k=1)
            mtj_joint.attr(name).set(pose_matrix)


def convert_joint_sdk(bc=8, mi=8, opt=50, it=35):
    auto_key()
    convert_joint_ani(bc, mi, opt, it)
    plane_sdk()


class SdrJointAnim(SdrJointDriver):
    title = u"转成骨骼动画"
    button_text = u"解算"

    def apply(self):
        bc = self.bc.value()
        mi = self.mi.value()
        opt = self.opt.value()
        it = self.it.value()
        convert_joint_ani(bc=bc, mi=mi, opt=opt, it=it)


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


def default_pose_path():
    return os.path.abspath(__file__ + "/../data/poses/default.json").replace("\\", "/")


def save_data_ui(get_default_path, get_data):
    default_path = get_default_path()
    path, _ = QFileDialog.getSaveFileName(get_host_app(), "Export To Unity", default_path, "Json (*.json)")
    if not path:
        return
    data = get_data()
    if isinstance(data, (str, u"".__class__)):
        QMessageBox.about(get_host_app(), u"提示", data)
        return
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


def get_pose_data():
    targets = ADPose.ADPoses.get_targets()
    targets = [t for t in targets if "_COMB_" not in t] + [t for t in targets if "_COMB_" in t]
    return targets


def export_pose_data_ui():
    save_data_ui(default_pose_path, get_pose_data)


def import_pose_data_ui():
    load_data_ui(default_pose_path, ADPose.ADPoses.dup_targets)


def mirror_matrix(matrix):
    p, r = matrix_to_position_rotation(matrix)
    p *= -1
    return position_rotation_to_matrix(p, r)


def matrix_to_unity_position_rotation(matrix):
    matrix = maya_matrix_to_unity_matrix(matrix)
    trans = pm.datatypes.TransformationMatrix(matrix)
    position = trans.getTranslation("world")
    rotate = trans.getRotation().asQuaternion()
    return dict(position=dict(x=position.x, y=position.y, z=position.z),
                rotation=dict(x=rotate.x, y=rotate.y, z=rotate.z, w=rotate.w))


def matrix_to_maya_position_rotation_test(matrix):
    trans = pm.datatypes.TransformationMatrix(matrix)
    position = trans.getTranslation("world")
    rotate = trans.getRotation().asQuaternion()
    return dict(position=dict(x=position.x, y=position.y, z=position.z),
                rotation=dict(x=rotate.x, y=rotate.y, z=rotate.z, w=rotate.w))


def world_fip_matrix(matrix):
    matrix.a01 *= -1
    matrix.a11 *= -1
    matrix.a21 *= -1
    matrix.a02 *= -1
    matrix.a12 *= -1
    matrix.a22 *= -1
    matrix.a30 *= -1
    return matrix


def mirror_sdr_joints(mirror_skin=True):
    polygons = ADPose.get_selected_polygons()
    if len(polygons) != 1:
        return pm.warning("please selected joint plane")
    plane = polygons[0]
    sk = get_skin_cluster(plane)
    if sk is None:
        return pm.warning("can not find skin")
    skins = sk.influenceObjects()
    for skin in skins:
        mirror_joint = ADPose.find_mirror_joint(skin)
        if mirror_joint is None:
            continue
        if mirror_joint not in skins:
            skins.append(mirror_joint)
    joints = []
    for attach in plane.getShape().outputs(type="cMuscleSurfAttach"):
        for parent in list(set(attach.outputs(type="parentConstraint"))):
            for joint in list(set(parent.outputs(type="joint"))):
                if joint not in joints:
                    joints.append(joint)
    pm.currentTime(1)
    mirror_joints = []
    targets = bs_api.get_bs(plane).weight.elements()
    mirror_targets = ADPose.ADPoses.targets_to_mirror(targets)
    for joint in joints:
        parent = joint.getParent()
        matrix = world_fip_matrix(joint.bindPoseMatrix.get() * parent.getMatrix(ws=1))
        mirror_parent = ADPose.find_mirror_joint(parent)
        if mirror_parent is not None:
            parent = mirror_parent
        matrix = matrix * parent.getMatrix(ws=1).inverse()
        mirror_joint = pm.joint(parent)
        mirror_joint.setMatrix(matrix)
        mirror_joint.rename("corrective_"+parent.name() + "_sd_0")
        mirror_joints.append(mirror_joint)
        mirror_joint.addAttr("bindPoseMatrix", at="matrix", k=1)
        mirror_joint.bindPoseMatrix.set(matrix)
        mirror_joint.radius.set(joint.radius.get())
        for src, dst in mirror_targets:
            if not joint.hasAttr(src+"Matrix"):
                continue
            mirror_joint.addAttr(dst+"Matrix", at="matrix", k=1)
            mirror_joint.attr(dst+"Matrix").set(mirror_matrix(joint.attr(src+"Matrix").get()))
    group = sdk_group()
    mirror_plane = create_plane("Mirror_Temp_PL", group, mirror_joints, 0.1)
    for i, joint in enumerate(mirror_joints):
        attach = create_attach("Mirror_", group, i, mirror_plane)
        attach.rename(joint.name().replace("_sd_", "_attach_"))
        pm.parent(pm.parentConstraint(attach, joint), attach)
    pm.skinCluster(skins, mirror_plane, tsb=1)
    pm.copySkinWeights(ss=find_history_node(plane, "skinCluster"), ds=find_history_node(mirror_plane, "skinCluster"), mirrorMode="YZ")
    plane = comb_plane_dk([plane, mirror_plane])
    pm.select(plane)
    ADPose.ADPoses.mirror_by_targets(targets)
    # skin = find_history_node(plane, "skinCluster")
    # pm.copySkinWeights(ss=skin, ds=skin, mirrorMode="YZ")


def comb_plane_dk(planes=None):
    if planes is None:
        planes = ADPose.get_selected_polygons()
    if len(planes) <= 1:
        return pm.warning("can not find plane")
    group = sdk_group()
    # combine planes
    dup_pls = []
    for polygon in planes:
        dup = polygon.duplicate()[0]
        for s in dup.getShapes():
            if s.io.get():
                pm.delete(s)
        dup.setParent(w=1)
        dup_pls.append(dup)
    combine_polygon = pm.polyUnite(dup_pls, ch=0)[0]
    combine_polygon.setParent(group)
    combine_polygon.v.set(0)
    # comb blend shape
    bs_names = []
    bs_inputs = []
    for pl in planes:
        bs = bs_api.get_bs(pl)
        for name in bs.weight.elements():
            if name in bs_names:
                continue
            bs_names.append(name)
            inputs = bs.attr(name).inputs(p=1)
            if len(inputs) == 1:
                bs_inputs.append(inputs[0])
            else:
                bs_inputs.append(None)

    for index, name in enumerate(bs_names):
        ids = MIntArray()
        points = MPointArray()
        count = 0
        for pl in planes:
            _ids, _points = bs_api.get_bs_ids_points(pl, name)
            for i in range(_ids.length()):
                ids.append(_ids[i]+count)
            for i in range(_points.length()):
                points.append(_points[i])
            count += pl.getShape().numEdges()
        bs_api.add_target(combine_polygon, name)
        bs_api.set_bs_ids_points(combine_polygon, name, ids, points)
        attr = bs_inputs[index]
        if attr is None:
            continue
        bs_api.bridge_connect(attr, combine_polygon)
    # replace attach
    count = 0
    for pl in planes:
        attaches = pl.getShape().worldMesh[0].outputs(type="cMuscleSurfAttach")
        for att in attaches:
            combine_polygon.getShape().worldMesh[0].connect(att.surfIn, f=1)
            att.edgeIdx1.set(att.edgeIdx1.get() + count)
            att.edgeIdx2.set(att.edgeIdx2.get() + count)
        count += pl.getShape().numVertices()
    # comb weights
    joints = []
    for polygon in planes:
        sks = polygon.getShape().inputs(type="skinCluster")
        if sks:
            sk = sks[0]

            influences = sk.influenceObjects()
            for jnt in influences:
                if jnt not in joints:
                    joints.append(jnt)
    if not joints:
        return
    combine_sk = pm.skinCluster(joints, combine_polygon, tsb=1)
    weights = []
    for polygon in planes:
        sks = polygon.getShape().inputs(type="skinCluster")
        number = polygon.getShape().numVertices()
        wts = []
        if sks:
            sk = sks[-1]
        else:
            sk = None
        for jnt in joints:
            if sk is None:
                if jnt.name().split("|")[-1] == "StaticSkin":
                    wts.append([1.0] * number)
                else:
                    wts.append([0.0] * number)
            else:
                influences = sk.influenceObjects()
                if jnt in influences:
                    wts.append(list(sk.getWeights(sk.getGeometry()[0], influences.index(jnt))))
                else:
                    wts.append([0.0] * number)
        weights.extend([w for ws in zip(*wts) for w in ws])
    combine_sk.setWeights(combine_sk.getGeometry()[0], range(len(joints)), weights)
    # comb bs
    name = planes[0].name()
    pm.delete(planes)
    combine_polygon.rename(name)
    return combine_polygon


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


def node_name(joint):
    names = joint.fullPath().split("|")
    if names[0] == u"":
        names.pop(0)
    if names[0] != "Roots":
        names.pop(0)
    return "/".join(names)


def to_unity_data():
    joint_elements = []

    # find corrective joints
    driven_joints = []
    for joint in pm.ls("corrective_*_sd_*", type="joint"):
        if not joint.hasAttr("bindPoseMatrix"):
            continue
        driven_joints.append(joint)
    # get target joints dict
    target_joints = {}
    for driven_joint in driven_joints:
        for attr in driven_joint.listAttr(ud=1):
            attr_name = attr.name().split(".")[-1]
            if attr_name == "bindPoseMatrix":
                continue
            if attr_name[-6:] != "Matrix":
                continue
            target_name = attr_name[:-6]
            target_joints.setdefault(target_name, []).append(driven_joint)
    all_driven_nodes = list(set(node_name(joint) for joint in sum(target_joints.values(), [])))

    # get pose to unity data
    targets = [target_name for target_name in target_joints.keys() if "_COMB_" not in target_name]
    ad_poses = ADPose.ADPoses.targets_to_ad_poses(targets)
    target_name_data = []
    for ad, poses in ad_poses:
        target_names = [ad.target_name(pose) for pose in poses]
        driven_joints = list(set(sum([target_joints.get(target_name, []) for target_name in target_names], [])))
        driver_node = node_name(ad.joint)
        axis = 0
        driven_nodes = [node_name(jnt) for jnt in driven_joints]
        driven_nodes = [all_driven_nodes.index(name) for name in driven_nodes]
        driver_pose_data, up = driven_poses(ad.joint, poses)
        matrix_data = []
        target_names.insert(0, "bindPose")
        target_name_data.append(target_names)
        for target_name in target_names:
            matrix_list = []
            for joint in driven_joints:
                attr_name = target_name + "Matrix"
                matrix = pm.datatypes.Matrix.identity
                if joint.hasAttr(attr_name):
                    matrix = joint.attr(attr_name).get()
                matrix_list.append(matrix)
            matrix_data.append(matrix_list)
        driven_pose_data = [[matrix_to_unity_position_rotation(matrix) for matrix in matrix_list]
                            for matrix_list in matrix_data]

        rbf_poses = [dict(driverPose=driver, drivenPoses=driven)
                     for driver, driven in zip(driver_pose_data, driven_pose_data)]
        joint_elements.append(dict(
            driverNode=driver_node,
            drivenNodes=driven_nodes,
            rbfPoses=rbf_poses,
            axis=axis,
            driverUpPose=up,
            k=2,
            isADsolveMode=True,
            is2DsolveMode=False
        ))
    # get comb pose to unity
    comb_elements = []
    comb_targets = [target_name for target_name in target_joints.keys() if "_COMB_" in target_name]
    for comb_target in comb_targets:
        ids = []
        driven_joints = target_joints.get(comb_target, [])
        driven_nodes = [node_name(jnt) for jnt in driven_joints]
        driven_nodes = [all_driven_nodes.index(name) for name in driven_nodes]
        for target_name in comb_target.split("_COMB_"):
            ids.append(find_target_id(target_name, target_name_data))
        ids = {"driverId%i" % i: {"elementId": element_id, "poseId": pose_id}
               for i, (element_id, pose_id) in enumerate(ids)}
        matrix_list = []
        for joint in driven_joints:
            attr_name = comb_target + "Matrix"
            matrix = pm.datatypes.Matrix.identity
            if joint.hasAttr(attr_name):
                matrix = joint.attr(attr_name).get()
            matrix_list.append(matrix)
        poses = [matrix_to_unity_position_rotation(m) for m in matrix_list]
        row = dict(
            drivenNodes=driven_nodes,
            drivenPose=poses,
        )
        row.update(ids)
        comb_elements.append(row)
    data = dict(
        rbfElements=joint_elements,
        combElements=comb_elements,
        allDrivenNodes=all_driven_nodes,
    )
    return data


def test_pose():
    joints = pm.ls("corrective_*", type="joint")
    for joint in joints:
        attr_name = "Arm01_L_a90_d0_COMB_Arm02_L_a120_d0Matrix"
        bind_matrix = joint.bindPoseMatrix.get()
        if not joint.hasAttr(attr_name):
            joint.setMatrix(bind_matrix)
            continue
        pose_matrix = joint.attr(attr_name).get()
        joint.setMatrix(pose_matrix*bind_matrix)


def unity_matrix_to_maya_matrix(matrix):
    matrix.a01 *= -1
    matrix.a02 *= -1
    matrix.a10 *= -1
    matrix.a20 *= -1
    matrix.a30 *= -100
    matrix.a31 *= 100
    matrix.a32 *= 100
    return matrix


def unity_position_rotation_to_matrix(data):
    xyz = [data["position"][i] for i in "xyz"]
    xyzw = [data["rotation"][i] for i in "xyzw"]
    p = pm.datatypes.Point(xyz)
    r = pm.datatypes.Quaternion(xyzw)
    matrix = position_rotation_to_matrix(p, r)
    return unity_matrix_to_maya_matrix(matrix)


def out_matrix(m):
    m = [[m[i][j] for j in range(4)] for i in range(4)]
    # import pprint
    # pprint.pprint(m)


def read_test():
    path = "D:/work/adPose/to_unity_test/to_unity_test/comb_test.0002.json"
    data = read_json_data(path)
    bind_matrix_dict = {}
    for i, name in enumerate(data["allDrivenNodes"]):
        if "corrective_Arm02_R_sd_1" in name:
            pass
    for rbf in data["rbfElements"]:
        for name, pose in zip(rbf["drivenNodes"],
                              rbf["rbfPoses"][0]["drivenPoses"]):
            bind_matrix_dict[name] = unity_position_rotation_to_matrix(pose)

    for name, pose in zip(data["combElements"][0]["drivenNodes"],
                          data["combElements"][0]["drivenPose"]):
        joint = pm.ls(data["allDrivenNodes"][name].split("/")[-1])[0]
        comb_matrix = unity_position_rotation_to_matrix(pose)
        bind_matrix = bind_matrix_dict[name]
        joint.setMatrix(bind_matrix)
        if "corrective_Arm02_R_sd_1" in data["allDrivenNodes"][name]:
            import pprint
            out_matrix(bind_matrix)
            out_matrix(comb_matrix)
            out_matrix(comb_matrix * bind_matrix)
    """
    corrective_Arm02_R_sd_1
    id: 6
    [0.364706039429, -0.437500029802, -0.705882370472]
    [0.837455548198, 0.00417146908884, -0.339740574511]
    [-0.472749509608, -0.441671342777, -1.04562294483]
    """


def find_target_id(target_name, target_name_data):
    for i, target_name_list in enumerate(target_name_data):
        if target_name in target_name_list:
            return [i, target_name_list.index(target_name)]
    pm.warning("can not fin comb ids" + target_name)
    return [-1, -1]


def get_host_app():
    try:
        main_window = QApplication.activeWindow()
        while True:
            last_win = main_window.parent()
            if last_win:
                main_window = last_win
            else:
                break
        return main_window
    except:
        pass


def export_to_unity_ui():
    save_data_ui(default_scene_path, to_unity_data)




