# -*- coding: UTF-8 -*-

import maya.cmds as cmds
import pymel.core as pm
import maya.mel as mm
import reset_controls
import scalefunc

speakBS_list = ['LipCornerPuller', 'LipFunneler', 'LipPressor', 'LipPucker', 'LipStercher', 'LipSuck', 'LipTightener',
                'LowerLipDepressor', 'MouthStretch', 'SharpLipPuller', 'UpperLipRaiser', 'ChinRaiser', 'Dimpler',
                'LipCornerDepressor', 'JawDrop', 'MouthCloseDn', 'MouthCloseUp', 'LipZipUp', 'LipZipDn']


speakBS_list += ['LipSuckUp', 'LipSuckDn', 'LipPuckerUp', 'LipPuckerDn']

speakBS_list += ['III', 'OOO', 'PPP']
tongue_bs_list = [u'tgUp', u'tgDown', u'tgBack', u'tgFront']

teeth_bs_list = [u'tg_MouthStretch', u'tg_LowerLipDepressor']


def get_BS_info():
    """
    设置默认值，暂时仅用于面片绑定法的口型修改
    :return:
    """
    BS_node = 'FaceDriverBS'
    ifNPC = 1
    BS_geo = 'Driver'

    return BS_node, ifNPC, BS_geo


def add_BS(attr=None):
    """
    添加bs口型
    :param attr: str   属性名，即口型
    """

    BS_node = get_BS_info()[0]
    ifNPC = get_BS_info()[1]
    BS_geo = get_BS_info()[2]
    weight_list = cmds.aliasAttr(BS_node, query=True)

    if not weight_list:
        num_BS = 0
    else:
        i = 1
        weight_id_list = []
        max_id = 0
        while i <= len(weight_list):
            weight_id_list.append(weight_list[i])
            i += 2
        for j in weight_id_list:
            if int(j.strip('weight[]')) > int(max_id):
                max_id = int(j.strip('weight[]'))
        num_BS = max_id + 1

    if not attr:
        for i in range(len(speakBS_list)):
            if not cmds.objExists(BS_node + '.' + speakBS_list[i]):
                if not ifNPC:
                    skin_node = cmds.listConnections(BS_node, type='skinCluster')[0]
                    cmds.setAttr(skin_node + '.envelope', 0)
                cmds.setAttr(BS_node + '.envelope', 0)

                cmds.duplicate(BS_geo, n=speakBS_list[i] + '_m')
                cmds.blendShape(BS_node, edit=True, t=(BS_geo, num_BS + i, speakBS_list[i] + '_m', 1.0))
                cmds.aliasAttr(speakBS_list[i], BS_node + '.w[%d]' % (num_BS + i))

                if not ifNPC:
                    skin_node = cmds.listConnections(BS_node, type='skinCluster')[0]
                    cmds.setAttr(skin_node + '.envelope', 1)
                cmds.setAttr(BS_node + '.envelope', 1)

                cmds.delete(speakBS_list[i] + '_m')
    else:
        if not cmds.objExists(BS_node + '.' + attr):
            if not ifNPC:
                skin_node = cmds.listConnections(BS_node, type='skinCluster')[0]
                cmds.setAttr(skin_node + '.envelope', 0)
            cmds.setAttr(BS_node + '.envelope', 0)

            cmds.duplicate(BS_geo, n=attr + '_m')
            cmds.blendShape(BS_node, edit=True, t=(BS_geo, num_BS, attr + '_m', 1.0))
            cmds.aliasAttr(attr, BS_node + '.w[%d]' % num_BS)

            if not ifNPC:
                skin_node = cmds.listConnections(BS_node, type='skinCluster')[0]
                cmds.setAttr(skin_node + '.envelope', 1)
            cmds.setAttr(BS_node + '.envelope', 1)

            cmds.delete(attr + '_m')

def add_attribute(ctrl, attr):
    """
    给控制器添加一个0-1的属性
    :param ctrl: transform   控制器
    :param attr: str   属性名
    """
    if not ctrl.hasAttr(attr):
        pm.addAttr(ctrl, ln=attr, at='double', min=0, max=1, dv=0)
        pm.setAttr(ctrl + '.' + attr, e=1, keyable=1)
        pm.setAttr(ctrl + '.' + attr, 0)

def connect_one_BS(attr):
    """
    连接一个bs口型
    :param attr: str   属性名，即口型
    """
    BS_node = pm.PyNode(get_BS_info()[0])
    ctrl = pm.PyNode('speakControl')
    bridge = pm.PyNode('SpeakBlendShapeBridge')

    add_BS(attr)
    if attr in speakBS_list:
        if not pm.listConnections(BS_node.attr(attr), d=0, s=1):
            bridge.attr(attr).connect(BS_node.attr(attr))
    elif attr in tongue_bs_list:
        add_attribute(ctrl, attr)
        add_attribute(bridge, attr)
        if not pm.objExists(attr + '_BW'):
            BW = pm.createNode('blendWeighted', n=attr + '_BW')
            ctrl.attr(attr).connect(BW.input[0], f=1)
            BW.output.connect(bridge.attr(attr), f=1)
            for BS in BS_node.listAliases():
                if BS[0] == attr:
                    bridge.attr(attr).connect(BS[1], f=1)
    elif attr in teeth_bs_list:
        for BS in BS_node.listAliases():
            if BS[0] == attr:
                if not pm.objExists(attr + '_BW'):
                    BW = pm.createNode('blendWeighted', n=attr + '_BW')
                    bridge.attr(attr[3:]).connect(BW.input[0], f=1)
                    BW.output.connect(BS[1], f=1)

def connect_BS():
    """
    连接所有的口型、舌头的bs，并分离口腔bs
    """
    cmds.undoInfo(openChunk=1)
    for attr_i in speakBS_list + tongue_bs_list:
        connect_one_BS(attr_i)
    split_tgBS()
    print 'Connect successfully'
    cmds.undoInfo(closeChunk=1)

def set_tongueBS(value=None, attr=None):
    """
    设置舌头某个口腔bs的数值
    :param value: float   值
    :param attr: str   属性名，即口腔bs
    """
    if attr in tongue_bs_list:
        connect_one_BS(attr)
        ctrl = pm.PyNode('speakControl')
        pm.setAttr(ctrl.attr(attr), value)

def set_speakBS_value(value):
    """
    设置口型控制器的tx、ty数值
    :param value: float   值
    """
    ctrl = pm.PyNode('speakControl')
    pm.setAttr(ctrl.tx, value)
    pm.setAttr(ctrl.ty, value)


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


def select_BS(attr='Default', ifitem=0, value=1.0):
    """
    设置为某个数值的某种口型
    :param attr: str/QListWidgetItem的实例   属性名，即口型
    :param ifitem: bool   True：输入的attr是QListWidgetItem的实例；False：输入的attr是str
    :param value: float   值
    :return:
    """
    ctrl = pm.PyNode('speakControl')
    for attr_i in speakBS_list:
        set_ctrl_attr(ctrl, attr_i, 0)

    if ifitem:
        if attr.text() in speakBS_list:
            if attr.text() != 'Default':
                pm.setAttr(ctrl.attr(attr.text()), value)
        elif attr.text() == 'LipZipDn + LipZipUp':
            pm.setAttr(ctrl.attr('LipZipDn'), value)
            pm.setAttr(ctrl.attr('LipZipUp'), value)
            pm.setAttr(ctrl.attr('MouthStretch'), value * 0.5)
        elif attr.text() == 'MouthCloseDn + MouthCloseUp':
            pm.setAttr(ctrl.attr('MouthCloseDn'), value)
            pm.setAttr(ctrl.attr('MouthCloseUp'), value)
            pm.setAttr(ctrl.attr('MouthStretch'), value * 1)
        elif attr.text() in teeth_bs_list:
            if pm.objExists(attr.text() + '_BW'):
                BW = pm.PyNode(attr.text() + '_BW')
                pm.setAttr(BW.input[1], 0)
                pm.setAttr(BW.w[0], 1)
            cmds.setAttr("speakControl." + attr.text()[3:], value)
        elif attr.text() in tongue_bs_list:
            for attr_name in tongue_bs_list:
                if ctrl.hasAttr(attr_name):
                    set_tongueBS(attr_name, 0)
            set_tongueBS(attr.text(), value)
    else:
        if attr in speakBS_list:
            if attr != 'Default':
                pm.setAttr(ctrl.attr(attr), value)
        elif attr in teeth_bs_list:
            if pm.objExists(attr + '_BW'):
                BW = pm.PyNode(attr + '_BW')
                pm.setAttr(BW.input[1], 0)
                pm.setAttr(BW.w[0], 1)
            cmds.setAttr("speakControl." + attr[3:], value)
        elif attr in tongue_bs_list:
            for attr_name in tongue_bs_list:
                if ctrl.hasAttr(attr_name):
                    set_tongueBS(attr_name, 0)
            set_tongueBS(attr, value)

def reset_BS(attr):
    """
    还原某个口型为模型初始形状
    :param attr: str   属性名，即口型
    """
    BS_node = get_BS_info()[0]
    ifNPC = get_BS_info()[1]
    BS_geo = get_BS_info()[2]
    num = pm.PyNode(BS_node + '.' + attr).logicalIndex()
    cmds.sculptTarget(BS_node, e=True, r=1, t=num)
    if not ifNPC:
        skin_node = cmds.listConnections(BS_node, type='skinCluster')[0]
        cmds.setAttr(skin_node + '.envelope', 0)
    cmds.setAttr(BS_node + '.envelope', 0)
    cmds.duplicate(BS_geo, n=attr + '_default')
    if not ifNPC:
        skin_node = cmds.listConnections(BS_node, type='skinCluster')[0]
        cmds.setAttr(skin_node + '.envelope', 1)
    cmds.setAttr(BS_node + '.envelope', 1)
    src = pm.PyNode(attr + '_default')
    dst = pm.PyNode(attr)
    dst.setPoints(src.getPoints())
    scalefunc.reset_scale(attr)

def edit_BS(attr):
    """
    编辑某个口型
    :param attr: str   属性名，即口型
    """
    cmds.undoInfo(openChunk=1)

    BS_node = get_BS_info()[0]
    ifNPC = get_BS_info()[1]
    BS_geo = get_BS_info()[2]
    ctrl = pm.PyNode('speakControl')

    connect_one_BS(attr)

    if ifNPC:
        target = 'FaceGroup|Planes|Target'
    else:
        target = BS_geo

    changed_attr_list = []
    for attr_i in speakBS_list + tongue_bs_list:
        if ctrl.hasAttr(attr_i):
            attr_value = cmds.getAttr("speakControl." + attr_i)
            if abs(attr_value - 1.0) < 0.00001:
                changed_attr_list.append(attr_i)

    if attr in tongue_bs_list:
        select_BS()
    modify = cmds.duplicate(target, n=attr + '_modify')[0]
    if attr not in changed_attr_list:
        reset_BS(attr)
    scalefunc.connect_scale(attr)
    select_BS(attr)

    reset_controls.reset_face_ctrls()

    num = pm.PyNode(BS_node + '.' + attr).logicalIndex()
    pm.sculptTarget(BS_node, t=num, e=1)
    src = pm.PyNode(modify)
    dst = pm.PyNode(BS_geo)
    dst.setPoints(src.getPoints())

    pm.sculptTarget(BS_node, t=-1, e=1)
    cmds.delete(attr + '_modify')
    if cmds.objExists(attr + '_default'):
        cmds.delete(attr)
        cmds.delete(attr + '_default')

    select_BS(attr)
    reset_controls.reset_face_ctrls()
    print 'Edit successfully'

    cmds.undoInfo(closeChunk=1)

def rebuild_BS(attr):
    """
    重建某个口型
    :param attr: str   属性名，即口型
    """
    cmds.undoInfo(openChunk=1)

    BS_node = get_BS_info()[0]

    select_BS(attr)
    connect_one_BS(attr)

    if not cmds.objExists(attr):
        num = pm.PyNode(BS_node+'.' + attr).logicalIndex()
        cmds.sculptTarget(BS_node, e=True, r=1, t=num)
        cmds.setAttr(attr + '.translateX', -12)
        cmds.setAttr(attr + '.visibility', 1)
        cmds.select(attr)
        print 'Rebuild successfully'
    else:
        return cmds.warning(u'%s已经存在' % attr)

    cmds.undoInfo(closeChunk=1)

def rebuild_all_BS():
    """
    重建所有的口型
    """
    cmds.undoInfo(openChunk=1)
    clean_rebuild_BS()
    for attr_i in speakBS_list:
        rebuild_BS(attr_i)
    cmds.group(speakBS_list, n='all_BS_grp')
    select_BS()
    cmds.undoInfo(closeChunk=1)

def rename_func(name):
    """
    重命名选择的第一个物体为name
    :param name: str   名称，一般为口型名称
    """
    select_list = cmds.ls(sl=1)
    if not select_list:
        return cmds.warning(u'请选择一个模型')
    elif len(select_list) == 1:
        cmds.rename(select_list[0], name)
    else:
        return cmds.warning(u'一次只能修改一个模型的名称')

def __get_image():
    """
    为口型选择面板获取截图
    """
    path = __file__ + "/../data/icon/"
    cmds.currentTime(0, edit=1)
    for i in range(len(speakBS_list)):
        for attr in speakBS_list:
            cmds.setAttr("speakControl." + attr, 0)
        if speakBS_list[i] == 'MouthCloseDn':
            cmds.setAttr("speakControl.MouthStretch", 1)
            cmds.setAttr("speakControl.MouthCloseDn", 1)
            cmds.setAttr("speakControl.MouthCloseUp", 1)
        elif speakBS_list[i] == 'MouthCloseUp':
            continue
        elif speakBS_list[i] == 'LipZipDn':
            cmds.setAttr("speakControl.MouthStretch", 0.5)
            cmds.setAttr("speakControl.LipZipDn", 1)
            cmds.setAttr("speakControl.LipZipUp", 1)
        elif speakBS_list[i] == 'LipZipUp':
            continue
        else:
            cmds.setAttr("speakControl." + speakBS_list[i], 1)
        cmds.modelEditor('modelPanel4', edit=1, allObjects=False, polymeshes=True)
        cmds.modelEditor('modelPanel1', edit=1, allObjects=False, polymeshes=True)
        cmds.select(clear=1)
        cmds.playblast(frame=[0], format="image", viewer=0, filename=path + speakBS_list[i], compression="png", quality=70, percent=100, fp=4, clearCache=1, orn=0)
        for attr in speakBS_list:
            cmds.setAttr("speakControl." + attr, 0)

    cmds.modelEditor('modelPanel4', edit=1, allObjects=False, polymeshes=True)
    cmds.modelEditor('modelPanel1', edit=1, allObjects=False, polymeshes=True)
    cmds.playblast(frame=[0], format="image", viewer=0, filename=path + "Default", compression="png", quality=70, percent=100, fp=4, clearCache=1, orn=0)
    cmds.modelEditor('modelPanel4', edit=1, allObjects=True, joints=False)
    cmds.modelEditor('modelPanel1', edit=1, allObjects=True, joints=False)

def clean_anim():
    """
    删除场景内的动画关键帧
    """
    cmds.undoInfo(openChunk=1)
    speakBS_other_list = [u'HeadRealWeight', u'eyebrowsTime', u'eyebrowsWeight',
                          u'fastblinkTime', u'fastblinkWeight', u'headTime', u'headWeight']
    anim_node_list = []
    anim_node_list.extend(cmds.ls(type='animCurveTL'))
    anim_node_list.extend(cmds.ls(type='animCurveTU'))
    anim_node_list.extend(cmds.ls(type='animCurveTA'))
    if anim_node_list:
        for anim_node in anim_node_list:
            cmds.delete(anim_node)
        for attr_i in speakBS_list:
            if not cmds.getAttr('speakControl.'+attr_i, l=1):
                cmds.setAttr('speakControl.'+attr_i, 0)
        # for attr_i in speakBS_other_list:
        #     cmds.setAttr('speakControl.'+attr_i, 0)
        print 'Clean successfully'
    else:
        for attr_i in speakBS_list:
            if not cmds.getAttr('speakControl.' + attr_i, l=1):
                cmds.setAttr('speakControl.' + attr_i, 0)
        # for attr_i in speakBS_other_list:
        #     cmds.setAttr('speakControl.' + attr_i, 0)
        print 'No anim'
    cmds.undoInfo(closeChunk=1)

def clean_audio():
    """
    删除场景内的音频
    """
    audio_list = cmds.ls(type='audio')
    if audio_list:
        for i in audio_list:
            cmds.delete(i)
        print 'Clean successfully'
    else:
        print 'No audio'

def clean_rebuild_BS():
    """
    删除被重建出来的模型
    """
    cmds.undoInfo(openChunk=1)

    rebuild_BS_list = []
    for attr_i in speakBS_list:
        if cmds.objExists(attr_i):
            rebuild_BS_list.append(attr_i)
        if cmds.objExists('all_BS_grp'):
            rebuild_BS_list.append('all_BS_grp')
    if rebuild_BS_list:
        for attr_i in rebuild_BS_list:
            cmds.delete(attr_i)
        print 'Clean successfully'
    else:
        print 'No anim'

    cmds.undoInfo(closeChunk=1)

def transfer_vertex():
    """
    传递点序
    """
    select_list = cmds.ls(sl=1)
    src = pm.PyNode(select_list[0])
    dst = pm.PyNode(select_list[1])
    dst.setPoints(src.getPoints())
    print 'Transfer successfully'


def repair_scale_connect():
    """
    修复缩放连接
    """
    ctrl = pm.PyNode("speakControl")
    bridge = pm.PyNode("SpeakBlendShapeBridge")
    for src, dst in ctrl.outputs(c=1, p=1):
        if "scale" not in dst.node().name():
            continue
        src_attr_name = src.name().split(".")[-1]
        bridge.attr(src_attr_name).connect(dst, f=1)

def duplicate_BS(attr):
    """
    复制某个bs
    :param attr: str   属性名，即口型
    """
    BS_node = get_BS_info()[0]
    BS_geo = get_BS_info()[2]

    weight_list = pm.PyNode(BS_node).listAliases()
    id_list = [int(weight[1].name().replace(BS_node + '.weight', '').strip('[]')) for weight in weight_list]
    max_id = id_list[0]
    for i in id_list:
        if i > int(max_id):
            max_id = i
    num = max_id + 1

    select_BS(attr)
    old_num = pm.PyNode(BS_node + '.' + attr).logicalIndex()
    old_rebuild = pm.sculptTarget(BS_node, e=True, r=1, t=old_num)[0]
    select_BS()

    pm.blendShape(BS_node, edit=True, t=(BS_geo, num, attr, 1.0))
    cmds.aliasAttr(attr+'_dup', BS_node + '.w[%d]' % num)
    pm.delete(old_rebuild)

def split_tgBS():
    """
    把口腔bs从口型bs中分离出来
    """

    select_BS()
    reset_controls.reset_face_ctrls()

    for tg_attr in teeth_bs_list:
        duplicate_BS(tg_attr[3:])

    reset_old_tgbs()

    for tg_attr in teeth_bs_list:
        create_new_tgBS(tg_attr)

    select_BS()
    print 'Edit successfully'

def reset_old_tgbs():
    """
    在原本的所有口型中，还原口腔的形状
    """

    reset_controls.reset_face_ctrls()

    if pm.objExists('FaceDriverBS'):
        num_tongue_jnt = len(pm.listRelatives('fkGroup', ad=1, type='nurbsCurve'))
        zero_name_list = ['faceGroup|*|faceMdToothDnZero', 'faceGroup|*|faceMdToothUpZero', 'fkGroup|fk01Zero']
        for i in range(num_tongue_jnt - 1):
            zero_name_list.append('fk%02dZero|*|fk%02dZero' % (i + 1, i + 2))
        tg_ctrls = []
        for zero in [pm.PyNode(zero) for zero in zero_name_list]:
            ctrlShape = pm.listRelatives(zero, ad=1, type='nurbsCurve')[0]
            ctrl = ctrlShape.getParent()
            tg_ctrls.append(ctrl)
        tg_ctrls.sort()

        zero_list = [ctrl.getParent() for ctrl in tg_ctrls]

        ctrl_default_list = []
        for ctrl in tg_ctrls:
            ctrl_default = pm.duplicate(ctrl, n=ctrl.name().split('|')[-1] + '_default', rr=1, po=1, to=1)[0]
            pm.parent(ctrl_default, world=True)
            ctrl_default_list.append(ctrl_default)

        for attr in speakBS_list:
            select_BS(attr)
            for i, ctrl in enumerate(tg_ctrls):
                pm.parent(ctrl, ctrl_default_list[i])
                reset_controls.reset_ctrls([ctrl.name()])
                pm.parent(ctrl, zero_list[i])
            edit_BS(attr)

        for ctrl_default in ctrl_default_list:
            pm.delete(ctrl_default)
        pm.select(clear=1)
        select_BS()

def create_new_tgBS(tg_attr):
    """
    创建新的口腔bs
    :param tg_attr:str   属性名，即口腔bs
    """
    BS_node = get_BS_info()[0]
    BS_geo = get_BS_info()[2]

    attr = tg_attr + '_temp'
    add_BS(attr)
    num = pm.PyNode(BS_node + '.' + attr).logicalIndex()
    pm.sculptTarget(BS_node, t=num, e=1)

    dup_attr = tg_attr[3:] + '_dup'
    dup_num = pm.PyNode(BS_node + '.' + dup_attr).logicalIndex()
    dup_rebuild = pm.sculptTarget(BS_node, e=True, r=1, t=dup_num)[0]

    select_BS(tg_attr[3:])
    src = pm.PyNode(dup_rebuild)
    dst = pm.PyNode(BS_geo)
    dst.setPoints(src.getPoints())

    pm.delete(src)
    pm.sculptTarget(BS_node, t=-1, e=1)

    rebuild = pm.sculptTarget(BS_node, e=True, r=1, t=num)[0]

    connect_one_BS(tg_attr)
    tg_num = pm.PyNode(BS_node + '.' + tg_attr).logicalIndex()
    tg_rebuild = pm.sculptTarget(BS_node, e=True, r=1, t=tg_num)[0]

    src = pm.PyNode(rebuild)
    dst = pm.PyNode(tg_rebuild)
    dst.setPoints(src.getPoints())

    pm.delete(src)
    pm.delete(dst)
    mm.eval('blendShapeDeleteTargetGroup %s %d;' % (BS_node, num))
    mm.eval('blendShapeDeleteTargetGroup %s %d;' % (BS_node, dup_num))

    BW = pm.PyNode(tg_attr + '_BW')
    pm.setAttr(BW.attr('w[0]'), 1)

def speakBS_correction(attr):
    """
    在蒙皮模型上添加口型矫正的bs，用于最终绑定文件
    :param attr: str   属性名，即口型
    """
    cmds.undoInfo(openChunk=1)

    correction_geo = pm.selected()[0]
    BS_geo = pm.selected()[1]
    bridge = pm.PyNode('SpeakBlendShapeBridge')

    if BS_geo.getShape().type() != 'mesh':
        cmds.warning(u'请选择一个带蒙皮的模型')
    else:
        if not BS_geo.getShape().listHistory(type='blendShape'):
            cmds.warning(u'请选择一个带蒙皮的模型')

    BS_node = BS_geo.getShape().listHistory(type='blendShape')[0]

    if BS_node.hasAttr(attr + '_correction'):
        num = BS_node.attr(attr + '_correction').logicalIndex()
        mm.eval('blendShapeDeleteTargetGroup %s %d;' % (BS_node, num))

    weight_list = BS_node.listAliases()
    id_list = [int(weight[1].name().replace(BS_node.name()+'.weight', '').strip('[]')) for weight in weight_list]
    max_id = id_list[0]
    for i in id_list:
        if i > int(max_id):
            max_id = i
    num = max_id + 1

    invert_geo = pm.invertShape(BS_geo, correction_geo)
    pm.blendShape(BS_node, edit=True, t=(BS_geo, num, invert_geo, 1.0))
    cmds.aliasAttr(attr + '_correction', BS_node + '.w[%d]' % num)
    bridge.attr(attr).connect(BS_node.attr(attr + '_correction'))
    pm.delete(correction_geo)
    pm.delete(invert_geo)

    Roots = pm.PyNode('Roots')
    add_attribute(Roots, attr + '_correction')
    BS_node.attr(attr + '_correction').connect(Roots.attr(attr + '_correction'))

    cmds.undoInfo(closeChunk=1)







