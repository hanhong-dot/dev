# coding:utf-8
import re

import pymel.core as pm
from functools import partial

try:
    from PySide.QtGui import *
    from PySide.QtCore import *
    from PySide.QtNetwork import *
except ImportError:
    from PySide2.QtGui import *
    from PySide2.QtCore import *
    from PySide2.QtWidgets import *


def find_node(name):
    nodes = pm.ls(name)
    if not len(nodes) == 1:
        return pm.warning("can not find " + name)
    return nodes[0]


def get_name_space():
    selected = pm.selected()
    if not selected:
        return ""
    if ":" in selected[0].name():
        return selected[0].name().split(":")[0]+":"
    else:
        return ""


def get_fit_label(joint):
    if joint.type() != "joint":
        return ""
    if not joint.drawLabel.get():
        return ""
    attr = joint.attr("type")
    typ = attr.getEnums()[attr.get()]
    if typ == "Other":
        return joint.otherType.get()
    return typ


def find_fits(joint):
    fits = [u""] * 7
    joints = [joint, joint.getParent()] + pm.listRelatives(joint, ad=1)
    joints.sort(key=lambda x: x.fullPath().count("|"), reverse=False)
    label_joint = [[get_fit_label(joint), joint] for joint in joints]
    res = ["LegAim", "(Hip)|(Shoulder)", "", "(Hand)|(Foot)", "Toes[^E]*$", "ToesEnd", "Heel"]
    for i, regx in enumerate(res):
        if not regx:
            continue
        for label, joint in label_joint:
            if not re.search(regx, label):
                continue
            if fits[i]:
                continue
            fits[i] = joint.name().split(":")[-1].split("|")[-1]
            if i == 3:
                fits[2] = joint.getParent().name().split(":")[-1].split("|")[-1]
            if i == 4:
                name = joint.getParent().name().split(":")[-1].split("|")[-1]
                if name == fits[3]:
                    continue
                fits.append(name)
    return fits


def ik_x(v, p):
    return sum(v[i] * p[i] for i in range(3)) / sum(v[i] ** 2 for i in range(3))


def set_matrix(node, matrix):
    if node is None:
        return
    if matrix is None:
        return
    node.setMatrix(matrix, ws=1)


def set_translate(node, matrix):
    if node is None:
        return
    if matrix is None:
        return
    node.setTranslation(pm.datatypes.Point()*matrix, space="world")


def get_matrix(node):
    if node is not None:
        return node.getMatrix(ws=1)


def set_offset_matrix(con, joint, matrix):
    if con is None:
        return
    con.setMatrix(con.getMatrix(ws=1) * joint.getMatrix(ws=1).inverse() * matrix, ws=1)


class Switch(object):
    ikx = "IKX{fit}"
    joint = "{fit}"
    fk = "FK{fit}"
    roll = "Roll{fit}"
    pole = "Pole{self.name}"
    hand = "IK{self.name}"
    ik = "IK{fit}"
    switch = "FKIK{self.name}"
    fit = "fit"
    cons = "cons"
    q_toe = "q_toe"
    axis = "axis"
    ik_hand = "IK{self.name}Handle"

    @classmethod
    def all(cls):
        switches = []
        namespace = get_name_space()
        root = find_node(namespace + "FitSkeleton")
        label_joint = {get_fit_label(joint): joint for joint in pm.listRelatives(root, ad=1)}
        for switch in pm.ls(namespace+"FKIK*_R", namespace+"FKIK*_L", type="transform"):
            if not switch.hasAttr("FKIKBlend"):
                continue
            match = re.search(r"(\w+:)?FKIK(?P<name>\w+)_(?P<rl>R|L)$", switch.name())
            if match is None:
                continue
            label = match.groupdict().get("name", "").replace("Leg", "Hip").replace("Arm", "Shoulder")
            if label not in label_joint:
                continue
            fits = find_fits(label_joint[label])
            switches.append(cls(fits=fits, namespace=namespace, **match.groupdict()))
        switches.sort(key=lambda sw: ik_x([0.0, 1.0, 1.0], sw.get(sw.fit, 1).getTranslation(space="world")))
        if len(switches) > 4:
            switches = [sw for sw in switches if sw.name in ["Leg", "Arm", "LegBack", "LegFront"]]

        switches[0].ud = "dn"
        switches[1].ud = "dn"
        switches[-1].ud = "up"
        switches[-2].ud = "up"
        return switches

    def __init__(self, **kwargs):
        self.namespace = kwargs.get("namespace", "")
        self.name = kwargs.get("name", "")
        self.rl = kwargs.get("rl", "")
        self.fits = kwargs.get("fits", [])
        self.fmt = ""
        self.i = 1
        self.ud = ""
        self.__cache = dict()

    def get_q_toe(self):
        toe = self.get(self.fit, 4)
        if toe is None:
            return False
        label = get_fit_label(toe)
        return "QToe" in label

    def get_cons(self):
        cons = [self.get(self.fk, i) for i in range(5)]
        cons += [self.get(self.roll, i) for i in [4, 5, 6, 7]]
        cons += [self.get(self.hand), self.get(self.pole), self.get(self.ik, 4), self.get(self.switch)]
        return list(filter(bool, cons))

    def get_axis(self):
        rl_axis = dict(R=1.0, L=-1.0)[self.rl]
        v = pm.datatypes.Vector(1, 0, 0) * self.get(self.fit, 2).getMatrix(ws=0)
        if v.y > 0:
            return rl_axis
        else:
            return -rl_axis

    def get_node(self):
        if self.i >= len(self.fits):
            return
        fit = self.fits[self.i]
        if not fit:
            return
        node_name = self.fmt.format(**locals())
        return find_node("{self.namespace}{node_name}_{self.rl}".format(**locals()))

    def get_fit(self):
        if self.i >= len(self.fits):
            return
        if not self.fits[self.i]:
            return
        return find_node(self.namespace + self.fits[self.i])

    def get(self, fmt, i=1):
        if (fmt, i) in self.__cache:
            return self.__cache[(fmt, i)]
        self.fmt = fmt
        self.i = i
        if not hasattr(self, "get_" + fmt):
            fmt = "node"
        result = getattr(self, "get_" + fmt)()
        self.__cache[(fmt, i)] = result
        return result

    def get_data(self):
        matrix_list = [get_matrix(self.get(self.joint, i)) for i in range(8)]
        ps = [self.get(self.joint, i).getTranslation(space="world") for i in range(1, 4)]
        mid_point = (ps[1] + (ps[0] - ps[1]).normal() + ps[1] + (ps[2] - ps[1]).normal()) / 2
        length = (ps[0] - ps[1]).length() + (ps[2] - ps[1]).length()
        if (mid_point - ps[1]).length() < 0.01:
            point = pm.datatypes.Point([0, self.get(self.axis), 0])
            mid_point = point * self.get(self.joint, 2).getMatrix(ws=1)
        pole = ps[1] + (ps[1] - mid_point).normal() * length
        return dict(matrix_list=matrix_list, pole=pole)

    def set_data(self, data, value=None):
        if value is None:
            value = self.get(self.switch).FKIKBlend.get()
        for attr in ["rock", "roll"]:
            if hasattr(self.get(self.hand), attr):
                self.get(self.hand).attr(attr).set(0)
        for i in [4, 5, 6, 7]:
            roll = self.get(self.roll, i)
            if roll is None:
                continue
            roll.t.set(0, 0, 0)
            roll.r.set(0, 0, 0)
            roll.s.set(1, 1, 1)

        self.get(self.switch).FKIKBlend.set(10)

        if len(self.fits) == 8:
            set_translate(self.get(self.hand), data["matrix_list"][4])
            set_matrix(self.get(self.fk, 0), data["matrix_list"][0])
            self.get(self.pole).setTranslation(data["pole"], space="world")

            inv = self.get(self.roll, 4).getMatrix(ws=1).inverse()
            v1 = pm.datatypes.Point(self.get(self.roll, 7).getTranslation(space="world"))
            v1 = pm.datatypes.Vector(v1 * inv)
            v2 = pm.datatypes.Vector(pm.datatypes.Point() * data["matrix_list"][7] * inv)
            rotate = pm.datatypes.Quaternion(v1, v2)
            self.get(self.roll, 4).rotateBy(rotate)

            inv = self.get(self.roll, 7).getMatrix(ws=1).inverse()
            v1 = self.get(self.ik_hand).getTranslation(space="transform")
            v2 = pm.datatypes.Vector(pm.datatypes.Point() * data["matrix_list"][3] * inv)
            rotate = pm.datatypes.Quaternion(v1, v2)
            self.get(self.roll, 7).rotateBy(rotate)

        elif self.get(self.q_toe):
            set_translate(self.get(self.hand), data["matrix_list"][4])
            set_matrix(self.get(self.fk, 0), data["matrix_list"][0])
            self.get(self.pole).setTranslation(data["pole"], space="world")
            inv = self.get(self.roll, 4).getMatrix(ws=1).inverse()
            v1 = self.get(self.ik_hand).getTranslation(space="transform").normal()
            v2 = pm.datatypes.Vector(pm.datatypes.Point() * data["matrix_list"][3] * inv).normal()
            rotate = pm.datatypes.Quaternion(v1, v2)
            self.get(self.roll, 4).rotateBy(rotate)
        else:
            set_translate(self.get(self.hand), data["matrix_list"][3])
            set_matrix(self.get(self.fk, 0), data["matrix_list"][0])
            set_offset_matrix(self.get(self.hand), self.get(self.joint, 3), data["matrix_list"][3])
            self.get(self.pole).setTranslation(data["pole"], space="world")
        set_offset_matrix(self.get(self.ik, 4), self.get(self.joint, 4), data["matrix_list"][4])

        data["matrix_list"][1] = get_matrix(self.get(self.ikx, 1))
        data["matrix_list"][2] = get_matrix(self.get(self.ikx, 2))
        self.get(self.switch).FKIKBlend.set(value)
        for i in [0, 1, 2, 3, 7, 4]:
            set_matrix(self.get(self.fk, i), data["matrix_list"][i])

        pm.setKeyframe(self.get(self.cons))

    def pre_switch(self, t):
        pm.setKeyframe(self.get(self.switch), t=t - 1, at="FKIKBlend")
        if self.fits[0]:
            pm.setKeyframe(self.get(self.fk, 0), t=t - 1, at="rx")
            pm.setKeyframe(self.get(self.fk, 0), t=t - 1, at="ry")
            pm.setKeyframe(self.get(self.fk, 0), t=t - 1, at="rz")
            pm.setKeyframe(self.get(self.fk, 0), t=t - 1, at="tx")
            pm.setKeyframe(self.get(self.fk, 0), t=t - 1, at="ty")
            pm.setKeyframe(self.get(self.fk, 0), t=t - 1, at="tz")


def current_itme():
    return int(round(pm.currentTime()))


def key_data(switches, vs, times, data):
    if not isinstance(vs, list):
        vs = [vs] * len(switches)
    for t, row in zip(times, data):
        if t != current_itme():
            pm.currentTime(t)
        for switch, v, elem in zip(switches, vs, row):
            switch.set_data(elem, v)


def bake_ik_fk(switches, times, vs):
    data = []
    for t in times:
        if t != current_itme():
            pm.currentTime(t)
        data.append([switch.get_data() for switch in switches])
    key_data(switches, None, [times[0]], [data[0]])
    map(lambda sw: sw.pre_switch(times[0]), switches)
    key_data(switches, vs, times, data)


def auto_switches(switches):
    vs = []
    _switches = []
    for sw in switches:
        if sw.get(sw.switch).FKIKBlend.get() < 0.01:
            vs.append(10)
            _switches.append(sw)
        elif sw.get(sw.switch).FKIKBlend.get() > 9.99:
            vs.append(0)
            _switches.append(sw)
        else:
            continue
    bake_ik_fk(_switches, [current_itme()], vs)


def tool_auto_switch_selected():
    auto_switches(list(filter(lambda sw: bool(pm.ls(sw.get(sw.cons), sl=1)), Switch.all())))


def tool_auto_switch_rl_ud(rl, ud):
    auto_switches([sw for sw in Switch.all() if sw.rl == rl and sw.ud == ud])


def tool_switch_all(v):
    bake_ik_fk(Switch.all(), [current_itme()], v)


def tool_bake_all(st, et, ud_rl_v):
    vs = []
    bake_switches = []
    switches = Switch.all()
    for ud, rl, v in ud_rl_v:
        ud_rl_sws = [sw for sw in switches if sw.rl == rl and sw.ud == ud]
        if not ud_rl_sws:
            continue
        bake_switches.append(ud_rl_sws[0])
        vs.append(v)
    times = sorted(set([int(round(t)) for sw in bake_switches
                        for con in sw.get(sw.cons)
                        for t in pm.keyframe(con, q=1, tc=1)
                        if st <= t <= et]+[st, et]))
    bake_ik_fk(bake_switches, times, vs)


def to_local_global(switch, v1, v2):
    matrix1 = switch.getMatrix(ws=1)
    pm.setKeyframe(switch)
    pm.currentTime(current_itme() - 1)
    matrix2 = switch.getMatrix(ws=1)

    switch.Global.set(v1)
    switch.setMatrix(matrix2, ws=1)
    pm.setKeyframe(switch)

    pm.currentTime(current_itme() + 1)
    switch.Global.set(v2)
    switch.setMatrix(matrix1, ws=1)
    pm.setKeyframe(switch)


qss = u"""
QWidget{
    background: #353535;
    font-size: 14px;
    font-family: 楷体;
}

QDialog{
    background-color: #404040
}

QGroupBox{
border:1px solid #242424;
border-radius:5px;
margin-top: 5px;
}

QGroupBox::title{
subcontrol-origin:margin;
position:relative;
left:10px;
}



QPushButton{
border-style:none;
border:1px solid #242424;
color:#DCDCDC;
padding:4px;
min-height:15px;
border-radius:5px;
background:qlineargradient(spread:pad,x1:0,y1:0,x2:0,y2:1,stop:0 #484848,stop:1 #383838);
}

QPushButton:hover{
background:qlineargradient(spread:pad,x1:0,y1:0,x2:0,y2:1,stop:0 #646464,stop:1 #525252);
}

QPushButton:pressed{
background:qlineargradient(spread:pad,x1:0,y1:0,x2:0,y2:1,stop:0 #484848,stop:1 #383838);
}

QSpinBox,QComboBox{
    padding:3px;
    border: 1px solid #404040;
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                 stop: 0.0 #202020,
                                 stop: 1.0 #505050);
}
QSpinBox::hover,QComboBox::hover{
    border-color:#606060;
}

QSpinBox,QComboBox{
    border-radius: 5px;
}
"""


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

# -----------2023.03.20 大牛添加--------------↓


def get_spine_all_fk(joints):
    all_fk = list()
    for joint in joints:
        pm.select(joint)
        name_space = get_name_space()
        if len(name_space) != 0:
            fk_name = str(joint).replace(name_space, name_space+'FK')
        else:
            fk_name = 'FK' + str(joint)
        if pm.objExists(fk_name):
            all_fk.append(pm.PyNode(fk_name))
    return all_fk


def get_spine_joints(FKIKBlend_Node):
    blendUnitNode = list(filter(lambda x: type(x) == pm.nodetypes.UnitConversion, pm.listConnections(FKIKBlend_Node.FKIKBlend, s=0, d=1)))[0]

    allScaleBlendNode_ForFindJoint = list(filter(lambda x: type(x) == pm.nodetypes.BlendColors, pm.listConnections(blendUnitNode.output, s=0, d=1)))
    Spine0_Joint = pm.PyNode(str(allScaleBlendNode_ForFindJoint[0]).replace('ScaleBlend', ''))
    Spine1_Joint = pm.PyNode(str(allScaleBlendNode_ForFindJoint[1]).replace('ScaleBlend', ''))

    if Spine1_Joint in pm.listRelatives(Spine0_Joint, c=1):
        joints = [pm.PyNode(str(node).replace('ScaleBlend', '')) for node in allScaleBlendNode_ForFindJoint]
    else:
        joints = [pm.PyNode(str(node).replace('ScaleBlend', '')) for node in reversed(allScaleBlendNode_ForFindJoint)]
    return joints


def get_point_by_parm(curve, parm):
    length = curve.getShape().length()*parm
    return curve.getShape().getPointAtParam(curve.getShape().findParamFromLength(length))


def get_ik_cons_by_type(FKIKBlend_Node, con_type=''):
    '''
    :param FKIKBlend_Node:
    :param con_type: empty:Return IK Control, cv:Return cv control, hybrid:Return hybrid control
    :return:
    '''
    replaceName = 'FKIK'

    name_space = FKIKBlend_Node.namespace()
    side = str(FKIKBlend_Node).split('_')[-1]
    all_ik = list()
    i = 1
    while pm.objExists(str(FKIKBlend_Node).replace(name_space+replaceName, name_space+'IK'+con_type).replace('_'+side, str(i)+'_'+side)):
        all_ik.append(pm.PyNode(str(FKIKBlend_Node).replace(name_space+replaceName, name_space+'IK'+con_type).replace('_'+side, str(i)+'_'+side)))
        i += 1
    return all_ik


def get_points_len(point1, point2):
    d = ((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2 + (point1[2] - point2[2]) ** 2) ** 0.5
    return d


def get_percent(points1):
    len_list = []
    # 求上下边的每个点到上一个点的长度
    for j in range(len(points1)):
        if j == range(len(points1))[-1]:
            continue
        else:
            len_list.append(get_points_len(points1[j], points1[j + 1]))

    each_len_percent = [0]
    # 求每个点到上一个点长度在整条曲线长度所占的百分比位置
    for j in range(len(len_list) + 1):
        if j == 0:
            continue
        else:
            each_len_percent.append(sum(len_list[0:j]) / sum(len_list))

    return each_len_percent


def get_section_list(each_len_percent):  # 根据传入的百分比，求一个百分比区间
    # 例如传入了3个百分比的位置，那么会返回4个百分比的区间
    # 因为3个点，有2个区间，加上(0, 0)和(1, 1)的区间，所以返回了4个区间
    section_list = [(0, 0)]
    # 求曲线上点的位置区间
    for i in range(len(each_len_percent)):
        if i == range(len(each_len_percent))[-1]:
            section_list.append((1.0, 1.0))
        else:
            section_list.append((each_len_percent[i], each_len_percent[i + 1]))
    return section_list


def get_point_in_section(percent_list, section_list):  # 传入目标百分比和源曲线的百分比，返回目标百分比所在的源曲线百分比区间的开头
    # 例如目标百分比A为0.1，B为0.5，区间为[(0, 0), (0, 0.2), (0.2, 1)]，则返回[(0, 0.2), (0.2, 1)]
    point_in_section = []
    # 求根据百分比，在曲线上居于何区间，得出区间的开头
    for each_item in percent_list:
        for section in section_list:
            if section[0] <= each_item < section[1]:
                point_in_section.append(section)
    point_in_section.append((1, 1))
    return point_in_section


def switch_spine_to_ik(FKIKBlend_Node):
    namespace = get_name_space()
    all_joint = get_spine_joints(FKIKBlend_Node)
    all_joint_position = [joint.getTranslation(space='world') for joint in all_joint]
    all_joint_matrix = [joint.getMatrix(ws=1) for joint in all_joint]
    root_m = [joint for joint in all_joint if 'Root_M' in str(joint)][0]

    hips_joint = [joint for joint in pm.listRelatives(root_m, c=1) if 'Hip' in str(joint)]
    hips_joint_matrix = [joint.getMatrix(ws=1) for joint in hips_joint]
    if len(namespace) != 0:
        hips_fk = [pm.PyNode(str(joint).replace(namespace, namespace+'FK')) for joint in hips_joint]
    else:
        hips_fk = [pm.PyNode('FK'+str(joint)) for joint in hips_joint]

    ik_cons = get_ik_cons_by_type(FKIKBlend_Node)
    ik_hybrids = get_ik_cons_by_type(FKIKBlend_Node, 'hybrid')
    ik_cvs = get_ik_cons_by_type(FKIKBlend_Node, 'cv')

    joint_percent = get_percent([joint.getTranslation(space='world') for joint in all_joint])
    joint_section = get_section_list(joint_percent)

    num = len(ik_cons)

    parm = [1.0 / (num - 1) * i for i in range(num - 1)]
    parm.append(1)

    FKIKBlend_Node.FKIKBlend.set(10)

    for joint, matrix, con in zip([all_joint[0], all_joint[-1]], [all_joint_matrix[0], all_joint_matrix[-1]], [ik_cons[0], ik_cons[-1]]):
        set_offset_matrix(con, joint, matrix)

    for m, fk in zip(hips_joint_matrix, hips_fk):
        fk.setMatrix(m, ws=1)

    # for point, cv_con in zip(all_joint_position[1:-1], ik_cvs):
    #     cv_con.setTranslation(point, space='world')

    for con in ik_cons:
        pm.setKeyframe(con.t, t=pm.currentTime())
        pm.setKeyframe(con.r, t=pm.currentTime())
    for cv in ik_cvs:
        pm.setKeyframe(cv.t, t=pm.currentTime())
    for fk in hips_fk:
        pm.setKeyframe(fk.t, t=pm.currentTime())
        pm.setKeyframe(fk.r, t=pm.currentTime())


    FKIKBlend_Node.FKIKBlend.set(10)


def switch_spine_to_fk(FKIKBlend_Node):
    all_joint = get_spine_joints(FKIKBlend_Node)
    fks = get_spine_all_fk(all_joint)
    root_m = [joint for joint in all_joint if 'Root_M' in str(joint)][0]

    namespace = get_name_space()
    hips_joint = [joint for joint in pm.listRelatives(root_m, c=1) if 'Hip' in str(joint)]
    hips_joint_matrix = [joint.getMatrix(ws=1) for joint in hips_joint]
    if len(namespace) != 0:
        hips_fk = [pm.PyNode(str(joint).replace(namespace, namespace + 'FK')) for joint in hips_joint]
    else:
        hips_fk = [pm.PyNode('FK' + str(joint)) for joint in hips_joint]

    FKIKBlend_Node.FKIKBlend.set(0)

    for m, fk in zip(hips_joint_matrix, hips_fk):
        fk.setMatrix(m, ws=1)

    for joint, fk in zip(all_joint, fks):
        fk.setMatrix(joint.getMatrix(ws=1), ws=1)

    for fk in fks:
        pm.setKeyframe(fk.t, t=pm.currentTime())
        pm.setKeyframe(fk.r, t=pm.currentTime())

    for fk in hips_fk:
        pm.setKeyframe(fk.t, t=pm.currentTime())
        pm.setKeyframe(fk.r, t=pm.currentTime())
    pm.select(FKIKBlend_Node)


def get_spine_ikfk_blend():
    selected = pm.selected()
    name_space = get_name_space()
    if len(selected) == 0:
        return pm.warning(u'未选择控制器，请选择FKIKBlend')
    elif len(selected) > 1:
        return pm.warning(u'选择了过多的对象')
    else:
        # if not str(selected[0]).startswith(name_space + 'FKIKSpine') and not str(selected[0]).startswith(name_space + 'FKIKSpline'):
        if not str(selected[0]).startswith(name_space + 'FKIKSpine'):
            return pm.warning(u'选择了错误的控制器，请选择FKIKBlend')
        else:
            return selected[0]
# -----------2023.03.20 大牛添加--------------↑


class IKFkTool(QDialog):

    def __init__(self):
        QDialog.__init__(self, get_host_app())
        self.setWindowTitle(u"IkFk工具")
        self.setStyleSheet(qss)
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.setMinimumWidth(320)
        box = QGroupBox(u"自动切换")
        layout.addWidget(box)
        v_layout = QVBoxLayout()
        box.setLayout(v_layout)

        h_layout = QHBoxLayout()
        v_layout.addLayout(h_layout)
        button = QPushButton(u"右臂")
        h_layout.addWidget(button)
        button.clicked.connect(partial(tool_auto_switch_rl_ud, "R", "up"))
        button = QPushButton(u"左臂")
        h_layout.addWidget(button)
        button.clicked.connect(partial(tool_auto_switch_rl_ud, "L", "up"))

        h_layout = QHBoxLayout()
        v_layout.addLayout(h_layout)
        button = QPushButton(u"右腿")
        h_layout.addWidget(button)
        button.clicked.connect(partial(tool_auto_switch_rl_ud, "R", "dn"))
        button = QPushButton(u"左腿")
        h_layout.addWidget(button)
        button.clicked.connect(partial(tool_auto_switch_rl_ud, "L", "dn"))

        button = QPushButton(u"选择")
        v_layout.addWidget(button)
        button.clicked.connect(tool_auto_switch_selected)

        box = QGroupBox(u"全部切换")
        layout.addWidget(box)
        v_layout = QVBoxLayout()
        box.setLayout(v_layout)

        button = QPushButton(u"IK")
        v_layout.addWidget(button)
        button.clicked.connect(partial(tool_switch_all, 10))

        button = QPushButton(u"FK")
        v_layout.addWidget(button)
        button.clicked.connect(partial(tool_switch_all, 0))

        box = QGroupBox(u"烘焙")
        layout.addWidget(box)
        v_layout = QVBoxLayout()
        box.setLayout(v_layout)

        grid_layout = QGridLayout()
        v_layout.addLayout(grid_layout)
        self.st = QSpinBox()
        self.st.setRange(-10000000, +1000000)
        grid_layout.addWidget(QLabel(u"开始:"), 0, 0, 1, 1)
        grid_layout.addWidget(self.st, 0, 1, 1, 1)
        self.et = QSpinBox()
        self.et.setRange(-10000000, +1000000)
        grid_layout.addWidget(QLabel(u"结束:"), 0, 3, 1, 1)
        grid_layout.addWidget(self.et, 0, 4, 1, 1)

        self.up_R_check = QCheckBox()
        self.up_R_check.setChecked(True)
        self.up_R_comb = QComboBox()
        self.up_R_comb.addItems([u"IK", u"FK"])
        grid_layout.addWidget(QLabel(u"右臂:"), 1, 0, 1, 1)
        grid_layout.addWidget(self.up_R_comb, 1, 1, 1, 1)
        grid_layout.addWidget(self.up_R_check, 1, 2, 1, 1)
        self.up_L_check = QCheckBox()
        self.up_L_check.setChecked(True)
        self.up_L_comb = QComboBox()
        self.up_L_comb.addItems([u"IK", u"FK"])
        grid_layout.addWidget(QLabel(u"左臂:"), 1, 3, 1, 1)
        grid_layout.addWidget(self.up_L_comb, 1, 4, 1, 1)
        grid_layout.addWidget(self.up_L_check, 1, 5, 1, 1)

        self.dn_R_check = QCheckBox()
        self.dn_R_check.setChecked(True)
        self.dn_R_comb = QComboBox()
        self.dn_R_comb.addItems([u"IK", u"FK"])
        grid_layout.addWidget(QLabel(u"右腿:"), 2, 0, 1, 1)
        grid_layout.addWidget(self.dn_R_comb, 2, 1, 1, 1)
        grid_layout.addWidget(self.dn_R_check, 2, 2, 1, 1)
        self.dn_L_check = QCheckBox()
        self.dn_L_check.setChecked(True)
        self.dn_L_comb = QComboBox()
        self.dn_L_comb.addItems([u"IK", u"FK"])
        grid_layout.addWidget(QLabel(u"左腿:"), 2, 3, 1, 1)
        grid_layout.addWidget(self.dn_L_comb, 2, 4, 1, 1)
        grid_layout.addWidget(self.dn_L_check, 2, 5, 1, 1)

        button = QPushButton(u"烘焙")
        grid_layout.addWidget(button, 3, 0, 1, 6)
        button.clicked.connect(self.bake)

        box = QGroupBox(u"脊柱切换")
        layout.addWidget(box)
        h_layout = QHBoxLayout()
        box.setLayout(h_layout)
        button = QPushButton(u'FK')
        h_layout.addWidget(button)
        button.clicked.connect(self.spine_to_fk)

        button = QPushButton(u'IK(慎用)')
        h_layout.addWidget(button)
        button.clicked.connect(self.spine_to_ik)

    def spine_to_ik(self):
        FKIKBlendNode = get_spine_ikfk_blend()
        if FKIKBlendNode is not None:
            switch_spine_to_ik(FKIKBlendNode)

    def spine_to_fk(self):
        FKIKBlendNode = get_spine_ikfk_blend()
        if FKIKBlendNode is not None:
            switch_spine_to_fk(FKIKBlendNode)

    def bake(self):
        st = self.st.value()
        et = self.et.value()
        ud_rl_v = []
        for ud, rl in [["up", "R"], ["up", "L"], ["dn", "R"], ["dn", "L"]]:
            name = "_".join([ud, rl])
            if getattr(self, name+"_check").isChecked():
                v_data = dict(IK=10, FK=0)
                v = v_data.get(getattr(self, name + "_comb").currentText(), 0)
                ud_rl_v.append([ud, rl, v])
        tool_bake_all(st, et, ud_rl_v)

    def showNormal(self):
        self.st.setValue(int(round(pm.playbackOptions(q=1, min=1))))
        self.et.setValue(int(round(pm.playbackOptions(q=1, max=1))))
        QDialog.showNormal(self)


window = None


def show():
    global window
    if window is None:
        window = IKFkTool()
    window.showNormal()

def doit():
    tool_auto_switch_rl_ud("R", "up")


if __name__ == '__main__':
    app = QApplication([])
    window = IKFkTool()
    window.showNormal()
    app.exec_()


