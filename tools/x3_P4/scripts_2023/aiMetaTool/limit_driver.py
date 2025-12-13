from maya import cmds
from maya.api.OpenMaya import *


def is_ctrl(ctrl):
    if cmds.objectType(ctrl) == "joint":
        return False
    if not cmds.listRelatives(ctrl, s=1):
        return False
    shapes = cmds.listRelatives(ctrl, s=1)
    shape = shapes[0]
    if cmds.objectType(shape) not in ["nurbsCurve"]:
        return False
    return True


def is_anim_attr(attr):
    typ = cmds.getAttr(attr, type=True)
    if typ not in ["double", "doubleAngle", "doubleLinear"]:
        return False
    if cmds.getAttr(attr, l=1):
        return False
    if not cmds.getAttr(attr, k=1):
        return False
    inputs = cmds.listConnections(attr, s=1, d=0)
    if inputs:
        if not cmds.objectType(inputs[0]).startswith("animCurve"):
            return False
    return True


def get_anim_attrs(controls):
    attrs = []
    for ctrl in controls:
        for attr in cmds.listAttr(ctrl, k=True) or []:
            attr = cmds.attributeQuery(attr, node=ctrl, sn=1)
            ctrl_attr = ctrl + "." + attr
            if not is_anim_attr(ctrl_attr):
                continue
            attrs.append(ctrl_attr)
    return attrs


def get_limit_data_by_attrs(attrs):
    data = []
    for attr in attrs:
        node, sn = attr.split(".")
        max_value, min_value = 0, 0
        default_value = cmds.getAttr(attr)
        if cmds.attributeQuery(sn, node=node,  mxe=1):
            max_value = cmds.attributeQuery(sn, node=node,  max=1)[0]
        if cmds.attributeQuery(sn, node=node, mne=1):
            min_value = cmds.attributeQuery(sn, node=node,  min=1)[0]
        if cmds.attributeQuery(sn, node=node, sxe=1):
            max_value = cmds.attributeQuery(sn, node=node,  smx=1)[0]
        if cmds.attributeQuery(sn, node=node, sme=1):
            min_value = cmds.attributeQuery(sn, node=node, smn=1)[0]
        if sn in [trs+xyz for xyz in "xyz" for trs in "trs"]:
            limit_enable = cmds.transformLimits(node, q=1, **{str("e"+sn): 1})
            limit_value = cmds.transformLimits(node, q=1, **{str(sn): 1})
            if limit_enable[0]:
                min_value = limit_value[0]
            if limit_enable[1]:
                max_value = limit_value[1]
        for value, suf in [[max_value, "max"], [min_value, "min"]]:
            if abs(value - default_value) < 0.0001:
                continue
            data.append(dict(
                attr=attr,
                name=attr.replace(".", "_")+"_"+suf,
                default_value=default_value,
                value=value,
            ))
    return data


def api_ls(*names):
    selection_list = MSelectionList()
    for name in names:
        selection_list.add(name)
    return selection_list


def find_bs(polygon):
    if not cmds.objExists(polygon):
        return
    shapes = set(cmds.listRelatives(polygon, s=1, f=1) or [])
    for bs in cmds.ls(cmds.listHistory(polygon), type="blendShape"):
        if cmds.ls(cmds.blendShape(bs, q=1, g=1), l=1)[0] in shapes:
            return bs


def get_bs(polygon):
    bs = find_bs(polygon)
    if bs is None:
        bs = cmds.blendShape(polygon, automatic=True, n=polygon.split("|")[-1] + "_bs")[0]
    return bs


def get_next_index(bs):
    elem_indexes = cmds.getAttr(bs + ".weight", mi=1) or []
    index = len(elem_indexes)
    for i in range(index):
        if i == elem_indexes[i]:
            continue
        index = i
        break
    return index


def get_index(bs, target):
    return api_ls(bs + "." + target).getPlug(0).logicalIndex()


def add_real_target(polygon, bs, target, target_polygon):
    if cmds.objExists(bs + "." + target):
        index = get_index(bs, target)
    else:
        index = get_next_index(bs)
    cmds.blendShape(bs, e=1, t=[polygon, index, target_polygon, 1])
    bs_attr = bs + '.weight[%i]' % index
    cmds.aliasAttr(bs_attr, rm=1)
    cmds.aliasAttr(target, bs_attr)


def duplicate_blend_shape_by_limit(polygon, data):
    bs_polygon = cmds.duplicate(polygon, n="face_targets_polygon")[0]
    bs = get_bs(bs_polygon)
    for row in data:
        cmds.setAttr(row["attr"], row["value"])
        target_polygon = cmds.duplicate(polygon, n=row["name"])[0]
        add_real_target(bs_polygon, bs, row["name"], target_polygon)
        cmds.setAttr(row["attr"], row["default_value"])
        cmds.delete(target_polygon)
    return bs_polygon


def get_selected_limit_polygon():
    ctrls = cmds.ls(sl=1, o=1, type="transform")
    polygon = ctrls.pop(-1)
    ctrls = list(filter(is_ctrl, ctrls))
    attrs = get_anim_attrs(ctrls)
    data = get_limit_data_by_attrs(attrs)
    return data, polygon


def duplicate_limit_blend_shape_by_selected():
    data, polygon = get_selected_limit_polygon()
    bs_polygon = duplicate_blend_shape_by_limit(polygon, data)
    connect_limit_driver_by_data(data, bs_polygon)


def create_node(typ, name, parent=None):
    if cmds.objExists(name):
        return name
    if parent is not None:
        return cmds.createNode(typ, n=name, p=parent, ss=True)
    else:
        return cmds.createNode(typ, n=name, ss=True)


def add_attr(node, attr, **kwargs):
    if cmds.objExists(node+"."+attr):
        return
    cmds.addAttr(node, ln=attr, **kwargs)


def connect_attr(src, dst):
    if not src:
        return
    if not dst:
        return
    if not cmds.objExists(src):
        return
    if not cmds.objExists(dst):
        return
    if cmds.isConnected(src, dst):
        return
    cmds.connectAttr(src, dst, f=1)


def connect_limit_driver_by_selected():
    data, polygon = get_selected_limit_polygon()
    connect_limit_driver_by_data(data, polygon)


def connect_limit_driver_by_data(data, polygon):
    bs = find_bs(polygon)
    if not bs:
        return
    bridge = create_node("transform", "FaceLimitDriverBridge")
    for row in data:
        name = row["name"]
        bs_attr = bs+"."+row["name"]
        if not cmds.objExists(bs_attr):
            continue
        bridge_attr = bridge+"."+name
        add_attr(bridge, name, k=1, min=0, max=1)
        connect_attr(bridge_attr, bs_attr)
        cmds.setDrivenKeyframe(bridge_attr, cd=row["attr"], dv=row["value"], v=1, itt="linear", ott="linear")
        cmds.setDrivenKeyframe(bridge_attr, cd=row["attr"], dv=row["default_value"], v=0, itt="linear", ott="linear")


def find_ctrl_by_target(target):
    names = target.split("_")
    names = names[:-1]
    for i in range(len(names)):
        if not names:
            return
        ctrl = "_".join(names)
        if cmds.objExists(ctrl):
            if is_ctrl(ctrl):
                return ctrl
        names.pop(-1)


def auto_limit_driver(polygon):
    bs = find_bs(polygon)
    ctrls = set()
    for target in cmds.listAttr(bs+".weight", m=1):
        ctrl = find_ctrl_by_target(target)
        if ctrl:
            ctrls.add(ctrl)
    data = get_limit_data_by_attrs( get_anim_attrs(ctrls))
    connect_limit_driver_by_data(data, polygon)
    print(ctrls)


def limit_sel_translate(value=1):
    for sel in cmds.ls(sl=1):
        cmds.transformLimits(sel, tx=[-value, value], etx=[True, True])
        cmds.transformLimits(sel, ty=[-value, value], ety=[True, True])
        cmds.transformLimits(sel, ty=[-value, value], etz=[True, True])


def doit():
    # cmds.select("set1")
    # cmds.select("face_targets_polygon1", add=1)
    duplicate_limit_blend_shape_by_selected()
    # cmds.select("ctrlBrow_R", "Napoleon")
    # data, polygon = get_selected_limit_polygon()
    # for row in data:
    #     print(row)
