# -*- coding: UTF-8 -*-
import pymel.core as pm
import maya.cmds as cmds
import os
import json
import main

speakBS_list = main.speakBS_list
path = __file__ + "/../data/"

# speakBS_list = [
#     'LipCornerPuller',
#      'LipStercher',
#      'LipTightener',
#      'LowerLipDepressor',
#      'MouthStretch',
#      'SharpLipPuller',
#      'UpperLipRaiser',
#      'Dimpler',
#      'LipCornerDepressor',
#      'JawDrop',
#      'MouthCloseDn',
#      'MouthCloseUp',
#      'LipZipUp',
#      'LipZipDn',
#      'LipFunnelerUp',
#      'LipFunnelerDn',
#      'LipPressorUp',
#      'LipPressorDn',
#      'LipPuckerUp',
#      'LipPuckerDn',
#      'LipSuckUp',
#      'LipSuckDn',
#      'ChinRaiserUp',
#      'ChinRaiserDn']


def add_blank_BS(attr='split_tempBS_down', BS_geo='Scale|base', ifDelete=1):
    '''
    新增一个空口型bs
    :param attr: str   属性名
    :param BS_geo: str   模型名
    :param ifDelete: 是否保留重建的bs模型
    :return: 该bs目标体属性
    '''
    BS_geo = pm.PyNode(BS_geo)
    BS_node = BS_geo.getShape().listHistory(type='blendShape')[0]
    weight_list = BS_node.listAliases()
    id_list = [weight[1].logicalIndex() for weight in weight_list]
    id_list.sort()
    if not weight_list:
        num = 0
    else:
        num = id_list[-1] + 1

    pm.setAttr(BS_node.envelope, 0)

    dup_BS_geo = pm.duplicate(BS_geo, n=attr)[0]
    pm.blendShape(BS_node, edit=True, t=(BS_geo, num, dup_BS_geo, 1.0))
    pm.setAttr(BS_node.envelope, 1)
    pm.setAttr(BS_node.weight[num], 1)
    pm.sculptTarget(BS_node, t=num, e=1)
    if ifDelete:
        pm.delete(dup_BS_geo)
    return BS_node.weight[num]


def ctrl_has_attr(ctrl, attr):
    if attr not in pm.listAttr(ctrl, ud=1):
        return False
    if ctrl.attr(attr).inputs():
        if "animCurve" in ctrl.attr(attr).inputs()[0].type():
            return True
        else:
            return False
    if ctrl.attr(attr).isLocked():
        return False
    return True


def set_ctrl_attr(ctrl, attr, value):
    if ctrl_has_attr(ctrl, attr):
        ctrl.attr(attr).set(value)


def duplicate_BS(attr, new_attr, BS_geo='Scale|base'):
    '''
    复制一个重复的bs目标体
    :param attr: str   属性名
    :param new_attr: str   新的属性名
    :param BS_geo: str   模型名
    :return: 该bs目标体属性
    '''
    BS_geo = pm.PyNode(BS_geo)
    BS_node = BS_geo.getShape().listHistory(type='blendShape')[0]
    weight_list = BS_node.listAliases()
    id_list = [weight[1].logicalIndex() for weight in weight_list]
    id_list.sort()
    num = id_list[-1] + 1

    ctrl = pm.PyNode('speakControl')
    for attr_i in speakBS_list:
        set_ctrl_attr(ctrl, attr_i, 0)
    for id in id_list:
        if not BS_node.weight[id].listConnections():
            pm.setAttr(BS_node.weight[id], 0)
    pm.setAttr(BS_node.attr(attr), 1)

    dup_BS_geo = pm.duplicate(BS_geo, n=new_attr)[0]
    pm.blendShape(BS_node, edit=True, t=(BS_geo, num, dup_BS_geo, 1.0))
    pm.setAttr(BS_node.envelope, 1)
    pm.setAttr(BS_node.weight[num], 1)
    pm.sculptTarget(BS_node, t=num, e=1)
    pm.delete(dup_BS_geo)
    return BS_node.weight[num]

def __paint_bs_weights(MouthStretch_value, attr_down, attr_up, target='base'):
    '''
    （已弃用）
    分离组合口型需要记录上下bs的权重，以下为绘制的bs权重以前的操作
    :param MouthStretch_value: float   该组合口型的MouthStretch的值
    :param attr_down: str   往下的属性名
    :param attr_up: str   往上的属性名
    :param target: str   目标模型的前缀，如"ST","base"
    '''
    pm.undoInfo(openChunk=1)

    BS_geo = pm.selected()[0]
    ctrl = pm.PyNode('speakControl')
    temp_grp = pm.group(em=1, w=1, n='temp_grp')

    def duplicate_temp_model(attr_list, name, v):
        if not attr_list:
            for attr_i in speakBS_list:
                set_ctrl_attr(ctrl, attr_i, 0)
            refer_model = pm.duplicate(BS_geo, n=name)[0]
            pm.parent(refer_model, temp_grp)
            pm.setAttr(refer_model.v, v)
        else:
            for attr_i in speakBS_list:
                set_ctrl_attr(ctrl, attr_i, 0)
                if attr_i in attr_list:
                    set_ctrl_attr(ctrl, attr_i, 1)
            refer_model = pm.duplicate(BS_geo, n=name)[0]
            pm.parent(refer_model, temp_grp)
            pm.setAttr(refer_model.v, v)
        return refer_model

    base_refer_model = duplicate_temp_model([], 'temp_base_refer_model', 1)
    down_refer_model = duplicate_temp_model([attr_down], 'temp_down_refer_model', 0)
    up_refer_model = duplicate_temp_model([attr_up], 'temp_up_refer_model', 0)
    MouthStretch_refer_model = duplicate_temp_model(['MouthStretch'], 'temp_MouthStretch_model', 0)
    updown_model = duplicate_temp_model(['MouthStretch', attr_down, attr_up], 'temp_updown_model', 0)

    refer_bs = pm.blendShape(down_refer_model, up_refer_model, MouthStretch_refer_model, base_refer_model)[0]
    pm.setAttr(refer_bs.attr('temp_down_refer_model'), 1)
    pm.setAttr(refer_bs.attr('temp_up_refer_model'), 0)
    pm.setAttr(refer_bs.attr('temp_MouthStretch_model'), 1)

    pm.setAttr(temp_grp.tx, -12)

    for attr_i in speakBS_list:
        set_ctrl_attr(ctrl, attr_i, 0)
        if attr_i == 'MouthStretch':
            set_ctrl_attr(ctrl, attr_i, MouthStretch_value)


    temp_bs_down = add_blank_BS(attr='split_tempBS_down', BS_geo=BS_geo)
    BS_geo.setPoints(updown_model.getPoints())
    xml = target + '_Updown_bs_weights.xml'
    pm.deformerWeights(xml, im=True, method="index", deformer=temp_bs_down, p=path)

    pm.undoInfo(closeChunk=1)

def __export_bs_weights(target):
    '''
    （已弃用）
    绘制bs权重之后的操作，记录bs权重并导出xml
    :param target: str   bs目标体
    '''
    xml = target + '_Updown_bs_weights.xml'
    BS_geo = pm.selected()[0]
    BS_node = BS_geo.getShape().listHistory(type='blendShape')[0]
    bs = BS_node.attr('split_tempBS_down')
    pm.deformerWeights(xml, ex=True, deformer=bs, p=path)

def export_mask_weights_json(target):
    '''
    记录mask权重并导出为json
    :param target: str   bs目标体
    '''
    sk = pm.PyNode("skinCluster1")
    joint = pm.PyNode("joint2")
    geo = sk.getGeometry()[0]
    index = sk.influenceObjects().index(joint)
    wts = sk.getWeights(geo, index)
    wts = list(wts)
    pm.select([geo.vtx[i] for i, w in enumerate(wts) if w > 0.1])
    json_name = target + '_Updown_bs_weights.json'
    json_path = path + json_name
    with open(json_path, "w") as fp:
        json.dump(wts, fp)
    print json_path

def set_mask_weights_json(base, shape, weights):
    '''
    用json里的mask权重，为模型的形状增加一个mask
    :param base: transform   基础模型/要设置形状的模型
    :param shape: transform   （权重全为1时）目标形状的模型
    :param weights: float list   权重列表
    '''
    vector_weights = []
    index_list = []
    for i, weight in enumerate(weights):
        if weight > 0.00001:
            index_list.append(i)
        vector = [weight, weight, weight]
        vector_weights.append(vector)
    for i, point in enumerate(shape.getPoints()):
        if i in index_list:
            base_point = base.getPoint(i)
            shape_point = shape.getPoint(i)
            vector = vector_weights[i]
            point = base_point + (shape_point - base_point) * vector
            print i, point
            base.setPoint(i, point)
    pm.select([base.vtx[i] for i in index_list])

def split_up_and_down(MouthStretch_value=0.5, attr_down='LipZipDn', attr_up='LipZipUp', target='base'):
    '''
    选择一个组合口型分离上下口型
    :param MouthStretch_value: float   该组合口型的MouthStretch的值
    :param attr_down: str   往下的属性名
    :param attr_up: str   往上的属性名
    :param target: str   目标模型的前缀，如"ST","base"
    :return: 成功返回True,''；失败返回False,reason
    '''
    pm.undoInfo(openChunk=1)

    if not pm.selected():
        return False, u'第一步，请选择你要分离的组合口型：MouthStretch%.1f + %s1.0 + %s1.0' % (MouthStretch_value, attr_down, attr_up)
    elif pm.selected()[0].getShape().type() != 'mesh':
        return False, u'第一步，请选择你要分离的组合口型：MouthStretch%.1f + %s1.0 + %s1.0' % (MouthStretch_value, attr_down, attr_up)
    elif len(pm.selected()) != 2:
        return False, u'第二步，请加选一个带口型BlendShape的原模型'
    elif pm.selected()[1].getShape().type() != 'mesh':
        return False, u'第二步，请加选一个带口型BlendShape的原模型'
    json_name = target + '_Updown_bs_weights.json'
    if not os.path.exists(path + json_name):
        return False, u'路径%s中，缺少与%s有关的bs权重' % (path, target)

    updown_model = pm.selected()[0]
    BS_geo = pm.selected()[1]
    ctrl = pm.PyNode('speakControl')
    BS_node = BS_geo.getShape().listHistory(type='blendShape')[0]

    for attr_i in speakBS_list:
        set_ctrl_attr(ctrl, attr_i, 0)
        if attr_i == 'MouthStretch':
            set_ctrl_attr(ctrl, attr_i, MouthStretch_value)
    temp_bs_down = add_blank_BS(attr='temp_bs_down', BS_geo=BS_geo)
    BS_geo.setPoints(updown_model.getPoints())

    with open(path + json_name, "r") as f:
        weights = json.load(f)
    pm.setAttr(temp_bs_down, 1)
    set_ctrl_attr(ctrl, "MouthStretch", 0)
    shape = pm.duplicate(BS_geo, n='temp_shape')[0]

    pm.setAttr(temp_bs_down, 0)
    temp_bs_up_rebuild = pm.duplicate(BS_geo, n='temp_bs_up_rebuild')[0]

    set_mask_weights_json(temp_bs_up_rebuild, shape, weights)
    pm.delete(shape)

    weight_list = BS_node.listAliases()
    id_list = [weight[1].logicalIndex() for weight in weight_list]
    id_list.sort()
    num = id_list[-1] + 1
    pm.blendShape(BS_node, edit=True, t=(BS_geo, num, temp_bs_up_rebuild, 1.0))
    temp_bs_up = BS_node.w[num]

    pm.setAttr(temp_bs_up, -1)
    pm.setAttr(temp_bs_down, 1)
    temp_bs_down_rebuild = pm.duplicate(BS_geo, n='temp_bs_down_rebuild')[0]
    temp_bs_rebuild = [temp_bs_down_rebuild, temp_bs_up_rebuild]

    for i, attr in enumerate([attr_down, attr_up]):
        if pm.objExists(attr):
            rebuild = pm.PyNode(target + '*|' + attr)
        else:
            rebuild = pm.PyNode(pm.sculptTarget(BS_node, e=True, r=1, t=BS_node.attr(attr).logicalIndex())[0])
        rebuild.setPoints(temp_bs_rebuild[i].getPoints())

    pm.delete(temp_bs_rebuild)
    pm.mel.eval('blendShapeDeleteTargetGroup %s %d;' % (BS_node, temp_bs_down.logicalIndex()))
    pm.mel.eval('blendShapeDeleteTargetGroup %s %d;' % (BS_node, temp_bs_up.logicalIndex()))
    for attr_i in speakBS_list:
        set_ctrl_attr(ctrl, attr_i, 0)
        if attr_i == 'MouthStretch':
            set_ctrl_attr(ctrl, attr_i, MouthStretch_value)
        elif attr_i in [attr_down, attr_up]:
            set_ctrl_attr(ctrl, attr_i, 1)

    pm.undoInfo(closeChunk=1)

    return True, ''

def split_combined_BS(target, attr):
    '''
    分离组合口型
    :param target: str   目标模型的前缀，如"ST","base"
    :param attr: str   不加"Up"或者"Down"的属性名
    :return: 成功打印“分离成功”；失败打印理由
    '''
    if attr == 'MouthClose':
        ok, reason = split_up_and_down(1, attr+'Dn', attr+'Up', target)
    elif attr == 'LipZip':
        ok, reason = split_up_and_down(0.5, attr+'Dn', attr+'Up', target)
    elif attr in ['LipFunneler', 'LipPressor', 'LipPucker', 'LipSuck', 'ChinRaiser']:
        ok, reason = split_up_and_down(0, attr+'Dn', attr+'Up', target)

    else:
        ok = None
        reason = None
    if not ok:
        pm.warning(reason)
        return
    else:
        print u'分离成功！'

def export_all_bs(obj_path=__file__ + "/../data/model"):
    '''
    导出所有的口型obj
    :param obj_path: str   obj导出路径
    '''
    if not pm.selected(type='transform'):
        return pm.warning(u'请选择一个带口型BlendShape的原模型')
    elif pm.selected(type='transform')[0].getShape().type() != 'mesh':
        return pm.warning(u'请选择一个带口型BlendShape的原模型')

    obj_list = []
    BS_geo = pm.selected()[0]
    ctrl = pm.PyNode('speakControl')
    BS_node = BS_geo.getShape().listHistory(type='blendShape')[0]

    pm.select(clear=1)
    obj_grp = pm.group(w=1, n='obj_grp')

    pm.setAttr(BS_node.envelope, 0)
    base_dup = pm.duplicate(BS_geo, n='base_dup')[0]
    obj_list.append(base_dup)
    pm.parent(base_dup, obj_grp)
    pm.rename(base_dup, 'base')
    pm.setAttr(BS_node.envelope, 1)

    for attr in speakBS_list:
        for attr_i in speakBS_list:
            set_ctrl_attr(ctrl, attr_i, 0)
        if not ctrl_has_attr(ctrl, attr):
            continue
        set_ctrl_attr(ctrl, attr, 1)
        dup = pm.duplicate(BS_geo, n=attr)[0]
        pm.parent(dup, obj_grp)
        pm.rename(dup, attr)
        obj_list.append(dup)

    for i in obj_list:
        for attr_i in ['t', 'tx', 'ty', 'tz', 'r', 'rx', 'ry', 'rz', 's', 'sx', 'sy', 'sz']:
            i.attr(attr_i).unlock()
        pm.setAttr(i.t, (0, 0, 0))
        pm.setAttr(i.r, (0, 0, 0))
        pm.setAttr(i.s, (1, 1, 1))
        pm.select(i)
        name = str(i.name().split('|')[-1])
        cmds.file(obj_path + '/%s.obj' % name, f=1, op='groups=1;ptgroups=1;materials=0;smoothing=1;normals=1', type='OBJexport', pr=1, es=1)

    for attr_i in speakBS_list:
        set_ctrl_attr(ctrl, attr_i, 0)
    pm.delete(obj_grp)


def find_bs(polygon):
    # 查找 模型 blend shape
    shapes = set(cmds.listRelatives(polygon, s=1) or [])
    for bs in cmds.ls(cmds.listHistory(polygon), type="blendShape"):
        if cmds.blendShape(bs, q=1, g=1)[0] in shapes:
            return bs


def get_attr_index(node, attr):
    parent_attr = cmds.attributeQuery(attr, node=node, ln=1)
    parent_name = "{node}.{parent_attr}".format(**locals())
    elem_names = cmds.listAttr(parent_name, m=1)
    elem_indexes = cmds.getAttr(parent_name, mi=1)
    if attr in elem_names:
        return elem_indexes[elem_names.index(attr)]
    return


def rebuild_target(bs_name, target_name):
    index = get_attr_index(bs_name, target_name)
    if index is None:
        return
    cmds.sculptTarget(bs_name, e=1, regenerate=1, target=index)
    igt_name = "{bs_name}.it[0].itg[{index}].iti[6000].igt".format(**locals())
    target_polygon_name = cmds.listConnections(igt_name, s=1, d=1)[0]
    return target_polygon_name


def get_bs_attr(bs, target):
    return bs + "." + target


def add_target(bs, target):
    if cmds.objExists(get_bs_attr(bs, target)):
        return
    elem_indexes = cmds.getAttr(bs+".weight", mi=1) or []
    index = len(elem_indexes)
    for i in range(index):
        if i == elem_indexes[i]:
            continue
        index = i
        break
    bs_attr = bs+'.weight[%i]' % index
    cmds.aliasAttr(target, bs_attr)
    cmds.setAttr(bs_attr, 0)


def get_bs(polygon):
    bs = find_bs(polygon)
    if bs is None:
        bs = cmds.blendShape(polygon, automatic=True, n=polygon.split("|")[-1] + "_bs")[0]
    return bs


def import_all_bs(obj_path):
    '''
    导入并修改所有口型
    :param obj_path: str   obj所在路径
    :return: 成功则打印每个属性名称
    '''
    if not pm.selected(type='transform'):
        return pm.warning(u'请选择一个带口型BlendShape的原模型')
    elif pm.selected(type='transform')[0].getShape().type() != 'mesh':
        return pm.warning(u'请选择一个带口型BlendShape的原模型')

    if not os.listdir(obj_path):
        return pm.warning(u'路径下找不到obj文件')
    elif not [name for name in os.listdir(obj_path) if name.split('.')[-1] == 'obj']:
        return pm.warning(u'路径下找不到obj文件')
    polygon = cmds.ls(sl=1, o=1)[0]
    prefix = polygon.split('_')[0]
    root = prefix + "_BS_grp"
    if not cmds.objExists(root):
        cmds.group(em=1, n=root)

    bs_name = get_bs(polygon)

    for attr in speakBS_list:
        obj_file = os.path.join(obj_path, attr+".obj").replace("\\", "/")
        if not os.path.isfile(obj_file):
            continue
        add_target(bs_name, attr)
        target = rebuild_target(bs_name, attr)
        if root not in (cmds.listRelatives(target, p=1) or []):
            target = cmds.parent(target, root)
        target = cmds.rename(target, attr)
        cmds.file(obj_file, i=1, type="OBJ", iv=1, ns=":")
        new = pm.PyNode(attr + 'obj_grp')
        old = pm.PyNode(target)
        old.setPoints(new.getPoints())
        pm.delete(new)
        old.v.set(0)



def test():
    # pm.mel.eval('''file -f -new;''')
    # pm.mel.eval('''file -f -options "v=0;"  -ignoreVersion  -typ "mayaAscii" -o "D:/kouxing/new_FACS/model/model_newbase_split_v01_r01.ma";addRecentFile("D:/kouxing/new_FACS/model/model_newbase_split_v02_r01.ma", "mayaAscii");''')
    attr_list = ['LipFunneler', 'LipPressor', 'LipPucker', 'LipSuck', 'ChinRaiser']
    split_combined_BS('base', attr_list[4])
    # export_all_bs()