#  coding:utf-8
from maya import cmds
import maya.api.OpenMaya as OM
import maya.api.OpenMayaRender as OMR
import json
import pprint

mergedControllers = []
faceConstraintCtrs = []
transfromAttr = {'translateX': 0, 'translateY': 1, 'translateZ': 2,
                 'rotateX': 3, 'rotateY': 4, 'rotateZ': 5,
                 'scaleX': 6, 'scaleY': 7, 'scaleZ': 8}


def getControllerInfo(controllerName,headInverseMat,isLookAt = False,lookAtLocalPosition = [0,0,0],isFaceConstraint = False,limit = None):
    if controllerName==None:
        return {"name": ""}
    if not cmds.objExists(controllerName):
        return {"name": ""}
    isMerged = controllerName in mergedControllers
    controlMat = OM.MMatrix(cmds.xform(controllerName, q=True, m=True, ws=True))
    controlMat[1] *= -1
    controlMat[2] *= -1
    controlMat[4] *= -1
    controlMat[8] *= -1
    worldPivot = cmds.xform(controllerName, q=True, rp=True, ws=True)
    controlMat[12] = worldPivot[0] * -0.01
    controlMat[13] = worldPivot[1] * 0.01
    controlMat[14] = worldPivot[2] * 0.01
    controlMat = controlMat * headInverseMat
    transMat = OM.MTransformationMatrix(controlMat)
    r = transMat.rotation(asQuaternion=True)
    scalse = transMat.scale(OM.MSpace.kWorld)

    limitX = [-1e+7, 1e+7]
    limitY = [-1e+7, 1e+7]
    limitZ = [-1e+7, 1e+7]

    if limit:
        limitX = [0,0]
        limitY = [0,0]
        limitZ = [0,0]
        for i in range(len(limit)):
            attr = limit[i][0]
            v = limit[i][1]

            if attr in transfromAttr:
                id = transfromAttr[attr]
                if id<3:
                    if id ==0:
                        v *= -0.01
                    else:
                        v*=0.01
                    if v>0:
                        [limitX,limitY,limitZ][id][1] = v
                    else:
                        [limitX, limitY, limitZ][id][0] = v

    else :
        for attr, limit in [['tx', limitX], ['ty', limitY], ['tz', limitZ]]:
            if cmds.getAttr(controllerName + '.' + attr, lock=True):
                limit[0] = 0
                limit[1] = 0
            else:
                limitMin, limitMax = eval('cmds.transformLimits(controllerName, q=True, {0}=True)'.format(attr))
                # enableMin,enableMax = cmds.transformLimits(controllerName, q=True, etx=True)
                enableMin, enableMax = eval('cmds.transformLimits(controllerName, q=True, e{0}=True)'.format(attr))
                if attr == 'tx':
                    if enableMin:
                        limit[0] = limitMax * -0.01
                    if enableMax:
                        limit[1] = limitMin * -0.01
                else:
                    if enableMin:
                        limit[0] = limitMin * 0.01
                    if enableMax:
                        limit[1] = limitMax * 0.01
    localPivot = cmds.xform(controllerName, q=True, rp=True, os=True)
    curveShape = []

    if cmds.listRelatives(controllerName, s=True, f=True) == None:
        print controllerName + "  has not shape"
    for shape in cmds.listRelatives(controllerName, s=True, f=True):
        if not cmds.getAttr(shape + '.io'):
            for i in cmds.getAttr(shape + '.controlPoints', mi=True):
                controlPoint = cmds.getAttr(shape + '.controlPoints[{0}]'.format(i))[0]
                curveShape.append(
                    {'x': (controlPoint[0] - localPivot[0]) * -0.01*scalse[0], 'y': (controlPoint[1] - localPivot[1]) * 0.01*scalse[1],
                     'z': (controlPoint[2] - localPivot[2]) * 0.01*scalse[2]})

    slls = OM.MSelectionList()
    for shape in cmds.listRelatives(controllerName, s=True, f=True):
        if not cmds.getAttr(shape + '.io'):
            slls.add(shape)
    color = OMR.MGeometryUtilities.wireframeColor(slls.getDagPath(0))
    if not isFaceConstraint:
        isFaceConstraint =True if cmds.listRelatives(controllerName,p=True)[0].find('Subtract')>=0 else False
    if not isFaceConstraint:
        isFaceConstraint = controllerName in faceConstraintCtrs
    return {"name": controllerName, 'customAttrs': [],'isFaceConstraint':isFaceConstraint,'isLookAt':isLookAt,
                        'isMerged':isMerged,
                        'position': {'x': controlMat[12], 'y': controlMat[13], 'z': controlMat[14]},
                        'rotation': {'x': r.x, 'y': r.y, 'z': r.z, 'w': r.w, },
                        'scale': {'x': scalse[0], 'y': scalse[1], 'z': scalse[2]},
                        'lookAtLocalPosition': {'x': lookAtLocalPosition[0], 'y': lookAtLocalPosition[1], 'z': lookAtLocalPosition[2]},
                        'controllerInfo': {'limitMinX': limitX[0],
                                           'limitMaxX': limitX[1],
                                           'limitMinY': limitY[0],
                                           'limitMaxY': limitY[1],
                                           'limitMinZ': limitZ[0],
                                           'limitMaxZ': limitZ[1],
                                           'shape': curveShape,
                                           'color': {'r': color.r, 'g': color.g, 'b': color.b, 'a': color.a}},
                        'mirrorId':-1
                        }


def get_bs_info(bs_node_name=""):
    bsInfo = []
    if not cmds.objExists(bs_node_name):
        return []
    for target_name in cmds.listAttr(bs_node_name+".weight", m=1):
        target = bs_node_name+"."+target_name
        weight = cmds.getAttr(bs_node_name+"."+target_name)
        if weight > 0.01:
            bsInfo.append(dict(target=target, weight=weight))
    return bsInfo


def get_joint_matrix(joint, ws=0):
    if ws:
        mat = OM.MMatrix(cmds.xform(joint, q=True, m=True, ws=True))
    else:
        mat = OM.MMatrix(cmds.xform(joint, q=True, m=True, os=True))
    mat[1] *= -1
    mat[2] *= -1
    mat[4] *= -1
    mat[8] *= -1
    mat[12] *= -0.01
    mat[13] *= 0.01
    mat[14] *= 0.01
    return mat


class Shape(object):
    mesh = "mesh"
    nurbsSurface = "nurbsSurface"
    nurbsCurve = "nurbsCurve"


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


def get_selected_polygons():
    return list(filter(is_shape, cmds.ls(sl=1, o=1)))


def find_bs(polygon):
    # 查找 模型 blend shape
    if not cmds.objExists(polygon):
        return
    shapes = set(cmds.listRelatives(polygon, s=1, f=1) or [])
    for bs in cmds.ls(cmds.listHistory(polygon), type="blendShape"):
        if cmds.ls(cmds.blendShape(bs, q=1, g=1), l=1)[0] in shapes:
            return bs


def find_bs_ctrls():
    ctrls = cmds.ls("CTRL_*")
    ctrls = [ctrl for ctrl in ctrls if is_shape(ctrl, Shape.nurbsCurve)]
    return ctrls


def is_anim_attr(attr):
    typ = cmds.getAttr(attr, type=True)

    if typ not in ["double", "doubleAngle", "doubleLinear"]:
        return False
    if cmds.getAttr(attr, l=1):
        return False

    inputs = cmds.listConnections(attr, s=1, d=0)
    if inputs:
        if not cmds.objectType(inputs[0]).startswith("animCurve"):
            return False
    # if not cmds.getAttr(attr, cb=1):
    #     return False
    # if attr == "CTRL_C_jaw_fwdBack.translateY":
    #     print "is attr", attr, cmds.getAttr(attr, se=1)
    # if attr == "CTRL_C_jaw_fwdBack.scaleX":
    #     print "is attr", cmds.getAttr(attr, se=1)
    return True


def get_anim_attrs(ctrl):
    # trs = ["translate", "rotate", "scale"]
    trs = ["translate"]
    attrs = []
    for XYZ in "XYZ":
        for tr in trs:
            attr_name = ctrl + "." + tr + XYZ
            if not is_anim_attr(attr_name):
                continue
            attrs.append(attr_name)
    for attr in cmds.listAttr(ctrl, ud=1, k=1) or []:
        attr_name = ctrl + "." + attr
        attrs.append(attr_name)

    return attrs


def node_name(joint):
    names = cmds.ls(joint, l=1)[0].split("|")
    if names[0] == u"":
        names.pop(0)
    if names[0] != "Roots":
        names.pop(0)
    return "/".join(names)


def get_max_min_value(attr_name):
    ctrl, attr = attr_name.split(".")
    attr = str(cmds.attributeQuery(attr, sn=1, n=ctrl))
    base_attr = ["tx", "ty", "tz", "rx", "ry", "rz"]
    if attr in base_attr:
        min_value, max_value = cmds.transformLimits(ctrl, q=1, **{attr: True})
    else:
        min_value = cmds.addAttr(attr_name, q=1, min=1)
        max_value = cmds.addAttr(attr_name, q=1, max=1)
    return [min_value, max_value]


def get_all_bs_info(bs_nodes):
    return sum([get_bs_info(bs_node) for bs_node in bs_nodes], [])


def get_plane_ctrls(head_inverse):
    ctrls = cmds.ls("*faceFrame*", type="transform")
    ctrls = [ctrl for ctrl in ctrls if is_shape(ctrl, Shape.nurbsCurve)]
    ctrls = [getControllerInfo(ctrl, head_inverse) for ctrl in ctrls]
    return ctrls


def export_npc_55_bs_rig(path):
    polygons = get_selected_polygons()
    bs_nodes = [find_bs(polygon) for polygon in polygons]
    bs_nodes = [bs for bs in bs_nodes if bs]
    ctrls = find_bs_ctrls()
    head_joint = "Head_M"
    head_inverse = get_joint_matrix(head_joint, ws=1).inverse()
    blend_controls = [getControllerInfo(ctrl, head_inverse) for ctrl in ctrls]
    pprint.pprint(blend_controls[0])
    value_weight_map = []
    face_elements = []
    weight_ctrl_map = []
    for control_id, ctrl_data in enumerate(blend_controls):
        for attr in get_anim_attrs(ctrl_data["name"]):
            if attr.split(".")[-1] in transfromAttr:
                attribute_id = transfromAttr[attr.split(".")[-1]]
            else:
                min_value, max_value = get_max_min_value(attr)
                attribute_id = 9 + len(ctrl_data["customAttrs"])
                ctrl_data["customAttrs"].append(dict(min=min_value, max=max_value, attrName=attr))

            weight_ctrl_map_id = len(weight_ctrl_map)
            weight_ctrl_map.append(dict(controlId=control_id, attributeId=attribute_id))
            for value in get_max_min_value(attr):
                cmds.setAttr(attr, value)
                bs_info = get_all_bs_info(bs_nodes)
                if not bs_info:
                    continue
                cmds.setAttr(attr, 0)
                face_elements.append(dict(bsInfo=bs_info))
                if attr.split(".")[-1] == "translateX":
                    value *= -1
                value_weight_map.append(dict(id=weight_ctrl_map_id, a=1.0/value, b=0))
    plane_ctrls = get_plane_ctrls(head_inverse)
    print plane_ctrls
    face_parameter = dict(
        headJoint=node_name(head_joint),
        blendControllers=blend_controls,
        planeControllers=plane_ctrls,
        weightControllerMap=weight_ctrl_map,
        faceElements=face_elements,
        valueWeightMap=value_weight_map,
        rigType=2,
    )
    with open(path, "wb") as f:
        json.dump(face_parameter, f, indent=4)


def doit():
    # , u'QST_Head_01', u'QST_Head_02', u'QST_Head_03'
    # cmds.select([u'QRY_Head'])
    # cmds.select([u'NPC_EM03_Head', u'NPC_EM03_Eyelashes', u'NPC_EM03_Eyeshell', u'NPC_EM03_Eyes', u'NPC_EM03_Teeth'])
    export_npc_55_bs_rig("D:/work/x3_npc_auto_55/rig_export/NPC_EF07.rbf.json")


if __name__ == '__main__':
    doit()