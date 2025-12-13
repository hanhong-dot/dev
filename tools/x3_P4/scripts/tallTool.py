# coding=utf-8
u"""
可选择单个或多个骨骼，模型或曲线
自动生成一串或多串骨骼
模型识别仅支持对细长弯曲度不大
"""
import functools

from maya import cmds
from PySide2.QtWidgets import *
from maya.api.OpenMaya import *
try:
    import numpy as np
except:
    np = None

# ----------- copy from rename tool --------------


def i_to_abc(i=100):
    u"""
    将数字换成36进制并用ABC表示， A=0, B=1, C=3, BC=26*1+3
    """
    abc = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    if i >= 26:
        j = i % 26
        i = i // 26
        return i_to_abc(i) + i_to_abc(j)
    else:
        return abc[i]


def re_abc(name, i):
    """
    name为tall#时，替换#为A， B
    name为tall##时，替换##为AA， AB
    """
    if "#" not in name:
        return name
    count = name.count("#")
    src = "#" * count
    if src not in name:
        return name
    dst = i_to_abc(i)
    if len(src) > len(dst):
        dst = ("A" * (len(src) - len(dst))) + dst
    name = name.replace(src, dst)
    return name


def re_i(name, i):
    """
    name为tall**时，替换**为01， 02
    name为tall***时，替换***为001， 002
    """
    if "*" not in name:
        return name
    count = name.count("*")
    src = "*" * count
    if src not in name:
        return name
    dst = "%0" + str(count) + "d"
    dst = dst % (i + 1)
    name = name.replace(src, dst)
    return name


def re_i_or_abc(name, i):
    """
    name为tall#**时替换#
    name为tall**#时替换**
    """
    if "#" not in name:
        return name
    if "*" not in name:
        return name
    if name.index("#") > name.index("*"):
        return re_i(name, i)
    else:
        return re_abc(name, i)


def re_i_and_abc(name, i):
    """
    name为tall#时替换#
    name为tall**#时替换**,并加1
    """
    return re_abc(re_i(name, i), i)


def is_matrix_fmt(fmt):
    return "#" in fmt and "*" in fmt


def get_selected_object_matrix():
    # 获取所有选择物体的子物体
    return [[top] + list(reversed(cmds.listRelatives(top, ad=1, f=1))) for top in cmds.ls(sl=1, o=1, l=1)]


def get_selected_objects():
    # 获取选择物体列表，若选择物体只有一个，则返回所有子物体
    selected = cmds.ls(sl=1, o=1, l=1)
    if len(selected) == 1:
        return get_selected_object_matrix()[0]
    else:
        return selected


def re_prefix(name):
    return name.replace("#", "").replace("*", "")


# ------------ copy form sdr k-mean ------------

def k_means(points, k):
    # 对points进行聚类
    # 求所有点的中心点，并转为相对于中心点的坐标
    center = np.mean(points, axis=0)
    points = points - center
    # 选取一个距离中心点最远的点作为第一个簇点
    distances = np.linalg.norm(points, axis=1)
    vtx_id = np.argmax(distances)
    cluster_points = points[None, vtx_id]
    # 多次循环，选出尽可能分散的簇点
    for _ in range(k-1):
        # 选取距离已最近簇点距离最大的点为新簇点。
        distances = np.linalg.norm(points[:, None]-cluster_points[None, ], axis=2)
        vtx_id = np.argmax(np.min(distances, axis=1))
        cluster_points = np.concatenate([cluster_points, points[None, vtx_id]], axis=0)
    # 多次循环，进行分类居中
    for i in range(10):
        # 将点分给最近的簇点
        distances = np.linalg.norm(points[:, None] - cluster_points[None,], axis=2)
        weights = np.eye(k)[np.argmin(distances, axis=1)]
        # 分类后的中心点作为新簇点
        cluster_points = np.sum(points[:, None] * weights[:, :, None], axis=0)/np.sum(weights, axis=0)[:, None]
    # 加上中心点，转化为真实坐标
    cluster_points += center
    return cluster_points


def sort_points(points):
    # 聚类出两个中心，通常为两端的中心点
    st_point, et_point = k_means(points, 2)
    # 如果et_point数值大，调换断电
    if np.mean(et_point-st_point) > 0:
        st_point, et_point = et_point, st_point
    # 求排序方向
    v = et_point - st_point
    # 按点在排序方向上的坐标排序
    points = list(points)
    points.sort(key=lambda x: np.dot(v, x-st_point) / np.dot(v, v))
    return points


def get_joint_point_by_polygon(polygon_name, k=10):
    # 获取模型点坐标
    points = np.array(cmds.xform(polygon_name + ".vtx[*]", q=1, ws=1, t=1))
    points = points.reshape([int(points.shape[0]/3), 3])
    # 聚类出多个中心点
    cluster_points = k_means(points, k)
    # 对点按同一方向排序
    cluster_points = sort_points(cluster_points)
    cluster_points[0] += (cluster_points[0] - cluster_points[1]) * 0.4
    cluster_points[-1] += (cluster_points[-1] - cluster_points[-2]) * 0.4
    return cluster_points


#  ------------- tall tool ---------

def is_shape(polygon_name, typ="mesh"):
    # 判断物体是否存在
    if not cmds.objExists(polygon_name):
        return False
    # 判断类型是否为transform
    if cmds.objectType(polygon_name) != "transform":
        return False
    # 判断是否有形节点
    shapes = cmds.listRelatives(polygon_name, s=1, f=1)
    if not shapes:
        return False
    # 判断形节点类型是否时typ
    if cmds.objectType(shapes[0]) != typ:
        return False
    return True


def create_curve_by_joints(points):
    # 创建经过点points的曲线
    # 创建多个线段，移至points处
    curves = []
    for p in points:
        curve = cmds.curve(p=[[1, 0, 0], [-1, 0, 0]], d=1)
        cmds.xform(curve, ws=1, t=p)
        curves.append(curve)
    # 将线段放样成曲面
    surface = cmds.loft(curves, ch=1, u=1)[0]
    # 从曲面上复制曲线
    curve = cmds.duplicateCurve(surface+".v[0.5]", ch=0, rn=0, local=0)[0]
    cmds.delete(curves, surface)
    return curve


def re_joints(joints, fmt, count, axis, typ, reverse):
    u"""
    重建骨骼
    :param joints: 源骨骼
    :param fmt: 新骨骼命名规范
    :param count: 新骨骼个数
    :param axis: 第二轴轴向
    :param typ: 第二轴朝向类型
    :param reverse: 是否翻转骨骼父子关系
    :return:
    """
    # 获取骨骼矩阵，避免骨骼删掉后无法获取
    joints = [joint for joint in joints if cmds.objectType(joint) in ["joint", "transform"]]
    matrix_list = [cmds.xform(joint, q=1, ws=1, m=1) for joint in joints]
    if is_shape(joints[0], "mesh"):
        # 如果选择了模型，则用聚类算法获取骨骼位置
        points = get_joint_point_by_polygon(joints[0], count)
    elif is_shape(joints[0], "nurbsCurve"):
        # 如果选择了曲线，则获取ep点坐标
        points = cmds.xform(joints[0]+".ep[*]", q=1, ws=1, t=1)
        points = [points[i:i+3] for i in range(0, len(points), 3)]
    else:
        # 如果选择了骨骼，获取选择骨骼的坐标
        points = [cmds.xform(joint, q=1, ws=1, t=1) for joint in joints]
        # cmds.delete(joints)

    # 如果需要反转骨骼，则反转坐标列表
    if reverse:
        points = list(reversed(points))
    # 创建经过points的曲线
    curve = create_curve_by_joints(points)
    # 按骨骼长度，创建等长骨骼
    length = cmds.arclen(curve, ch=0)
    step = length/(count-1)
    joint = None
    joints = []
    for i in range(count):
        joint = cmds.joint(joint, n=re_abc(re_i(fmt, i), i))
        cmds.setAttr(joint+".tx", step)
        joints.append(joint)
    cmds.xform(joints[0], ws=1, t=points[0])

    # 创建样条IK
    ik = cmds.ikHandle(sol="ikSplineSolver", ccv=0, sj=joints[0], ee=joints[-1], curve=curve)[0]

    for _ in range(3):
        # 在倒数第二个骨骼出，放止一个临时组，位置设置为points[-1]
        temp = cmds.group(em=1, p=joints[-2])
        cmds.xform(temp, ws=1, t=points[-1])
        # 此时，最后以跟x轴的坐标与临时组x轴坐标的差，越为线段长度与曲线长度的差
        err = (cmds.getAttr(joints[-1]+".tx") - cmds.getAttr(temp+".tx"))/(count-1)
        # 缩小tx的值，减少误差，让最后一根骨骼落地在曲线末短
        for joint in joints[1:]:
            cmds.setAttr(joint + ".tx", cmds.getAttr(joint + ".tx")-err)
        cmds.delete(temp)

    # 设置骨骼第二轴朝向
    if axis == "y":
        cmds.setAttr(ik + ".dWorldUpAxis", 0)
    elif axis == "z":
        cmds.setAttr(ik + ".dWorldUpAxis", 3)
    up_map = {
        "+x": [1, 0, 0],
        "-x": [-1, 0, 0],
        "+y": [0, 1, 0],
        "-y": [0, -1, 0],
        "+z": [0, 0, 1],
        "-z": [0, 0, -1]
    }
    if typ in up_map:
        # 设置up为世界正方向
        up1, up2 = up_map[typ], up_map[typ]
    else:
        # 设置up为首尾骨骼的y/z轴朝向
        axis_index = slice(4, 7) if axis == "y" else slice(8, 11)
        joint_index = -1 if typ == u"首尾骨骼" else 0
        print("selected", joint_index)
        up1, up2 = matrix_list[0][axis_index], matrix_list[joint_index][axis_index]
    # 设置ik高级旋转
    cmds.setAttr(ik + ".dTwistControlEnable", True)
    cmds.setAttr(ik + ".dWorldUpType", 4)
    cmds.setAttr(ik + ".dWorldUpAxis", 0 if axis == "y" else 3)
    cmds.setAttr(ik + ".dWorldUpVector", *up1)
    cmds.setAttr(ik + ".dWorldUpVectorEnd", *up2)
    # 获取骨骼矩阵，触发ik计算更新
    cmds.xform(joints[0], q=1, ws=1, m=1)
    cmds.delete(ik, curve)
    # 显示轴向，冻结旋转
    cmds.toggle(joints, la=1)
    cmds.makeIdentity(joints, apply=1, r=1)
    return joints


def undo(fun):
    def undo_fun(*args, **kwargs):
        cmds.undoInfo(openChunk=1)
        fun(*args, **kwargs)
        cmds.undoInfo(closeChunk=1)
    return undo_fun


@undo
def re_all_joints(fmt, count, axis, typ, reverse):
    selected = []
    if is_matrix_fmt(fmt):
        for i, joints in enumerate(get_selected_object_matrix()):
            current_fmt = re_i_or_abc(fmt, i)
            joints = re_joints(joints, current_fmt, count, axis, typ, reverse)
            selected.append(joints[0])
    else:
        joints = re_joints(get_selected_objects(), fmt, count, axis, typ, reverse)
        selected.append(joints[0])
    cmds.select(selected)


# ----------------- adv ---------------


@undo
def hide_toggle():
    # 显示隐藏物体轴向
    joints = sum(get_selected_object_matrix(), [])
    if cmds.toggle(joints[0], q=1, la=1):
        for joint in joints:
            if cmds.toggle(joint, q=1, la=1):
                cmds.toggle(joint, la=True)
    else:
        for joint in joints:
            if not cmds.toggle(joint, q=1, la=1):
                cmds.toggle(joint, la=True)


def set_fit_radius():
    # 获取软选半径
    radius = cmds.softSelect(q=1, ssd=1) / 2
    joints = sum(get_selected_object_matrix(), [])
    for joint in joints:
        # 为骨骼创建fat属性
        for name in [".fat", ".fatY", ".fatZ"]:
            if cmds.objExists(joint+name):
                continue
            cmds.addAttr(joint, ln=name[1:], min=0, k=1, at="double", dv=1)
        # 设置fat为软选半径
        cmds.setAttr(joint+".fat", radius)


def set_joint_label(joint, label):
    # 设置骨骼标签
    cmds.setAttr(joint + ".drawLabel", 1)
    cmds.setAttr(joint + ".type", 18)
    cmds.setAttr(joint + ".otherType", label, type="string")


def remove_label(joint):
    # 移除骨骼标签
    cmds.setAttr(joint + ".drawLabel", 0)
    cmds.setAttr(joint + ".type", 0)
    cmds.setAttr(joint + ".otherType", "", type="string")


@undo
def follow_to_fk():
    # 用hybrid控制器约束ik的组
    for con in cmds.ls(sl=1, type="transform"):
        if not con.startswith("FKIK"):
            continue
        if not is_shape(con, "nurbsCurve"):
            continue
        rml = con[-2:]
        ik = con[4:-2]
        fk_list = cmds.ls("IKhybrid{ik}*{rml}".format(**locals()))[1:-1]
        offset_list = cmds.ls("IKExtra{ik}*{rml}".format(**locals()))[1:-1]
        for fk, offset in zip(fk_list, offset_list):
            cmds.parentConstraint(fk, offset, mo=1)


@undo
def set_tall_label(count):
    # 设置adv尾巴标签
    for i, joints in enumerate(get_selected_object_matrix()):
        # 移除所有标签
        for joint in joints:
            remove_label(joint)
        # 将第二到第count-1个骨骼，设置成1， 2， 3...
        for j in range(1, count-1):
            set_joint_label(joints[j], str(j))
        # 移除骨骼命名中的数字
        label = joints[0].split("|")[-1]
        for j in range(10):
            label = label.replace(str(j), "")
        # 设置第一个骨骼标签为0label
        set_joint_label(joints[0], "0" + label)
        # 设置最后一个骨骼标签为count-1
        set_joint_label(joints[-1], str(count-1))

# --------- fast rig -----------


def list_range(*args, **kwargs):
    return list(range(*args, **kwargs))


def do_boor(knots, i, degree, u):
    u"""
    :param knots: 节点
    :param i: 第i个控制点
    :param degree: 次数
    :param u: parm/u,所在曲线百分比
    :return:
    """
    if degree == 0:
        if knots[i] < u <= knots[i+1]:
            return 1.0
        elif u == 0.0 and knots[i] <= u <= knots[i+1]:
            return 1.0
        else:
            return 0
    else:
        u0 = u - knots[i]
        scale = knots[i+degree]-knots[i]
        if scale == 0:
            scale = 1
        u0 /= scale
        b0 = do_boor(knots, i, degree-1, u)
        u1 = knots[i+degree+1] - u
        scale = knots[i+degree+1]-knots[i+1]
        if scale == 0:
            scale = 1
        u1 /= scale
        b1 = do_boor(knots, i+1, degree-1, u)
        return u0 * b0 + u1 * b1


def re_range(in_value, src_min, src_max, dst_min, dst_max):
    w = (in_value-src_min)/(src_max-src_min)
    return dst_min*(1-w) + dst_max*w


def get_degree_2_weight_data(control_count, joint_count):
    degree = 2
    knot_count = control_count+degree*2-1
    knot_step = 1.0 / (knot_count - 1)
    knots = [knot_step*i for i in range(knot_count)]
    control_step = 1.0 / (control_count - 1)
    joint_step = 1.0/(joint_count-1)
    range_args = (0.5 * control_step, 1-0.5 * control_step, knot_step*2, 1-knot_step*2)
    weight_data = []
    for i in range(joint_count):
        u = joint_step*i
        ws = [0] * control_count
        if u <= range_args[0]:
            ws[1], ws[0] = u / control_step, 1 - u / control_step
        elif u >= range_args[1]:
            ws[-2], ws[-1] = (1 - u) / control_step, 1 - (1 - u) / control_step
        else:
            re_u = re_range(u, *range_args)
            ws = [do_boor(knots, j, degree, re_u) for j in range(control_count)]
        weight_data.append(ws)
    return weight_data


class Color(object):
    red = 13
    green = 14
    blue = 6
    cyan = 18
    yellow = 17


def as_ctrl(n, r, c):
    ctrl = cmds.circle(ch=0, nr=[1, 0, 0], n="temp_"+n)[0]
    cmds.setAttr(ctrl+".s", r, r, r)
    cmds.makeIdentity(ctrl, apply=True, s=1)
    for shape in cmds.listRelatives(ctrl, s=1):
        cmds.setAttr(shape + ".overrideEnabled", True)
        cmds.setAttr(shape + ".overrideColor", c)
        shape = cmds.rename(shape, n+"Shape")
        cmds.parent(shape, n, s=1, add=1)
    cmds.delete(ctrl)


def create_hierarchy_groups(parent, pre, *suffixes):
    result = []
    for suffix in suffixes:
        parent = cmds.group(em=1, p=parent, n=pre+suffix)
        result.append(parent)
    return result


def create_children_groups(parent, pre, *suffixes):
    result = []
    for suffix in suffixes:
        result.append(cmds.group(em=1, p=parent, n=pre+suffix))
    return result


def create_point_constraint(src_groups, dst, weights):
    use_control_weights = [(ctrl, w) for ctrl, w in zip(src_groups, weights) if w > 0.00001]
    use_controls, use_weights = zip(*use_control_weights)
    pc = cmds.pointConstraint(use_controls, dst)[0]
    wal = cmds.pointConstraint(pc, q=1, wal=1)
    for a, w in zip(wal, use_weights):
        cmds.setAttr(pc + "." + a, w)


def fast_tall_rig(fits, fmt, joint_count):
    pre = re_prefix(fmt)
    control_count = len(fits)
    v1 = MVector(cmds.xform(fits[0], ws=1, q=1, t=1))
    v2 = MVector(cmds.xform(fits[1], ws=1, q=1, t=1))
    r = (v1-v2).length() * 0.2
    weight_data = get_degree_2_weight_data(control_count, joint_count)
    root = cmds.group(em=1, n=pre+"Group")
    parent = root
    src_curve_groups = []
    connects = cmds.group(em=1, n=pre+"Connects", p=root)
    for i in range(control_count):
        _pre = re_i_and_abc(fmt, i)
        groups = create_hierarchy_groups(parent, _pre, "Offset", "FkExtra", "FkCtrl", "IkExtra", "IkCtrl", "Up")
        offset, _, fk_ctrl, _, ik_ctrl, up = groups
        cmds.xform(groups[0], ws=1, m=cmds.xform(fits[i], q=1, ws=1, m=1))
        as_ctrl(fk_ctrl, r, Color.yellow)
        as_ctrl(ik_ctrl, r*0.6, Color.red)
        parent = fk_ctrl
        cmds.setAttr(up+".ty", r*0.1)
        src_curve_groups.append([ik_ctrl, up])
    src_curve_groups = list(zip(*src_curve_groups))
    cvs = []
    joint = root
    for i, ws in enumerate(weight_data):
        _pre = re_i_and_abc(fmt, i)
        aim, up = create_children_groups(connects, _pre, "CvAim", "CvUp")
        create_point_constraint(src_curve_groups[0], aim, ws)
        create_point_constraint(src_curve_groups[1], up, ws)
        joint = cmds.joint(joint, n=_pre+"Joint")
        cvs.append((aim, up, joint))
        cmds.parent(cmds.pointConstraint(aim, joint), connects)
    for i in range(len(cvs)-1):
        cmds.parent(cmds.aimConstraint(cvs[i+1][0], cvs[i][2], wuo=cvs[i][1], wut="object"), connects)
    cmds.parent(cmds.aimConstraint(cvs[-2][0], cvs[-1][2], wuo=cvs[-1][1], wut="object", aim=[-1, 0, 0]), connects)


def create_point_constraint_power(src_groups, dst, weights):
    use_control_weights = [(ctrl, w) for ctrl, w in zip(src_groups, weights) if w > 0.00001]
    use_controls, use_weights = zip(*use_control_weights)
    pc = cmds.pointConstraint(use_controls, dst)[0]
    wal = cmds.pointConstraint(pc, q=1, wal=1)
    for a, w in zip(wal, use_weights):
        cmds.setAttr(pc + "." + a, w)
    mul = cmds.createNode("multiplyDivide", n=dst+"WeightMul")
    cmds.addAttr(dst, ln="weight", dv=1, at="double", k=1)
    cmds.setAttr(mul+".operation", 3)
    for a, w, xyz in zip(wal, use_weights, "XYZ"):
        cmds.setAttr(mul + ".input1" + xyz, w)
        cmds.connectAttr(dst+".weight", mul+".input2"+xyz)
        cmds.connectAttr(mul+".output"+xyz, pc + "." + a)


@undo
def power_tall_rig(fmt, joint_count):
    fits = get_selected_objects()
    pre = re_prefix(fmt)
    control_count = len(fits)
    v1 = MVector(cmds.xform(fits[0], ws=1, q=1, t=1))
    v2 = MVector(cmds.xform(fits[1], ws=1, q=1, t=1))
    r = (v1-v2).length() * 0.2
    weight_data = get_degree_2_weight_data(control_count, joint_count)
    root = cmds.group(em=1, n=pre+"Group")

    src_curve_groups = []
    connects = cmds.group(em=1, n=pre+"Connects", p=root)
    controls = cmds.group(em=1, n=pre+"Controls", p=root)
    parent = controls
    for i in range(control_count):
        _pre = re_i_and_abc(fmt, i)
        groups = create_hierarchy_groups(parent, _pre, "Offset", "FkExtra", "FkCtrl", "IkExtra", "IkCtrl", "Up")
        offset, _, fk_ctrl, _, ik_ctrl, up = groups
        cmds.xform(groups[0], ws=1, m=cmds.xform(fits[i], q=1, ws=1, m=1))
        as_ctrl(fk_ctrl, r, Color.yellow)
        as_ctrl(ik_ctrl, r*0.6, Color.red)
        parent = fk_ctrl
        cmds.setAttr(up+".ty", r*0.1)
        src_curve_groups.append([ik_ctrl, up])

    src_curve_groups = list(zip(*src_curve_groups))
    cvs = []
    joint = root
    for i, ws in enumerate(weight_data):
        _pre = re_i_and_abc(fmt, i)
        aim, up = create_children_groups(connects, _pre, "CvAim", "CvUp")
        create_point_constraint_power(src_curve_groups[0], aim, ws)
        create_point_constraint_power(src_curve_groups[1], up, ws)

        follow, _, jk_ctrl = create_hierarchy_groups(controls, _pre, "JkFollow", "JkExtra", "JkCtrl")
        cmds.addAttr(jk_ctrl, ln="power", dv=1, at="double", k=1, min=1, max=10)
        cmds.connectAttr(jk_ctrl + ".power", aim+".weight")
        cmds.connectAttr(jk_ctrl + ".power", up + ".weight")

        joint = cmds.joint(joint, n=_pre+"Joint")
        as_ctrl(jk_ctrl, r*0.3, Color.blue)
        cmds.parent(cmds.parentConstraint(jk_ctrl, joint), connects)
        cvs.append((aim, up, follow))
        cmds.parent(cmds.pointConstraint(aim, follow), connects)
    for i in range(len(cvs)-1):
        cmds.parent(cmds.aimConstraint(cvs[i+1][0], cvs[i][2], wuo=cvs[i][1], wut="object"), connects)
    cmds.parent(cmds.aimConstraint(cvs[-2][0], cvs[-1][2], wuo=cvs[-1][1], wut="object", aim=[-1, 0, 0]), connects)


@undo
def fast_tall_rig_all(fmt, count):
    if is_matrix_fmt(fmt):
        for i, joints in enumerate(get_selected_object_matrix()):
            current_fmt = re_i_or_abc(fmt, i)
            fast_tall_rig(joints, current_fmt, count)
    else:
        fast_tall_rig(get_selected_objects(), fmt, count)


# ----------------- ui -----------------


def get_app():
    top = QApplication.activeWindow()
    if top is None:
        return
    while True:
        parent = top.parent()
        if parent is None:
            return top
        top = parent


def q_add(layout, *elements):
    for elem in elements:
        if isinstance(elem, QLayout):
            layout.addLayout(elem)
        elif isinstance(elem, QWidget):
            layout.addWidget(elem)
    return layout


def q_button(text, action):
    but = QPushButton(text)
    but.clicked.connect(action)
    return but


class Tool(QDialog):

    def __init__(self, parent):
        QDialog.__init__(self, parent)
        self.setLayout(QVBoxLayout())
        self.setWindowTitle(u"尾巴工具")
        self.line = QLineEdit()
        self.count = QSpinBox()
        self.count.setRange(0, 99999999)
        self.count.setValue(5)
        self.axis = QComboBox()
        self.axis.addItems(["y", "z"])
        self.typ = QComboBox()
        self.typ.addItems(["+x", "-x", "+y", "-y", "+z", "-z", u"首骨骼", u"首尾骨骼"])
        self.line.setText("tall**")
        self.reverse = QCheckBox()
        q_add(
            self.layout(),
            q_add(QHBoxLayout(), QLabel(u"命名规范:"), self.line),
            q_add(QHBoxLayout(), QLabel(u"骨骼个数:"), self.count),
            q_add(QHBoxLayout(), QLabel(u"第二轴向:"), self.axis),
            q_add(QHBoxLayout(), QLabel(u"轴向类型:"), self.typ),
            q_add(QHBoxLayout(), QLabel(u"反转骨骼:"), self.reverse),
            q_button(u"创建骨骼", self.apply),
            q_button(u"隐藏/显示轴向", hide_toggle),
            q_button(u"设置adv控制器半径", set_fit_radius),
            q_button(u"设置adv标签", self.set_adv_ik),
            q_button(u"移除IK主控", follow_to_fk),
            q_button(u"尾巴绑定极简版", self.fast_tall_rig),
            q_button(u"尾巴绑定折角版", self.power_tall_rig),
        )
        self.setWhatsThis(__doc__)
        for label in self.findChildren(QLabel):
            label.setFixedWidth(60)

    def apply(self):
        fmt = self.line.text()
        count = self.count.value()
        axis = self.axis.currentText()
        typ = self.typ.currentText()
        reverse = self.reverse.isChecked()
        re_all_joints(fmt, count, axis, typ, reverse)

    def set_adv_ik(self):
        count = self.count.value()
        set_tall_label(count)

    def fast_tall_rig(self):
        fmt = self.line.text()
        count = self.count.value()
        fast_tall_rig_all(fmt, count)

    def power_tall_rig(self):
        fmt = self.line.text()
        count = self.count.value()
        power_tall_rig(fmt, count)


window = None


def show():
    global window
    if window is None:
        window = Tool(parent=get_app())
    window.show()


def doit():
    cmds.select("tall01")
    re_all_joints("tall**", 5, "y", "+y", False)


if __name__ == '__main__':
    app = QApplication([])
    show()
    app.exec_()
