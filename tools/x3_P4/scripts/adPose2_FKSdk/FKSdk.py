# coding:utf-8
import pymel.core as pm
from .adPose2.joints import *
from .adPose2.ADPose import *
from .adPose2 import bs as bs_api


def get_controls(ifdone=False):
    '''
    获取FK控制器
    :param ifdone: bool   判断是否需要包含已经创建Attach面片的FK控制器，默认不包含
    :return: transform list   筛选后的FK控制器
    '''
    controls = []
    for child in pm.selected():
        if child.getShape().nodeType() == 'nurbsCurve':
            if pm.objExists("FKSdk_BodyDeformSdkPlane"):
                driver_plane = pm.PyNode('FKSdk_BodyDeformSdkPlane')
                if ifdone:
                    if child in get_FK_done_controls(driver_plane):
                        controls.append(child)
                else:
                    if child not in get_FK_done_controls(driver_plane):
                        controls.append(child)
            else:
                controls.append(child)
    return controls

def get_FK_done_joint(driver_plane):
    '''
    根据driver_plane获取所有创建完Attach面片后的transferJnt
    :param driver_plane: transform   FKSdk_BodyDeformSdkPlane
    :return: transform list   driver_plane有关的所有transferJnt
    '''
    attaches = []
    for attach in driver_plane.getShape().outputs(type="cMuscleSurfAttach"):
        attaches.append(attach)

    def key(_attach):
        return _attach.edgeIdx1.get()

    attaches = list(sorted(attaches, key=key))
    joints = []
    for attach in attaches:
        transfer = attach.r.outputs(type="parentConstraint")[0].constraintRotateX.outputs()[0].r.outputs()[0].r.outputs()
        jnt = transfer[0].getChildren(type='joint')[0]
        joints.append(jnt)
    return joints

def get_FK_done_controls(driver_plane):
    '''
    根据driver_plane获取所有创建完Attach面片后的FK控制器
    :param driver_plane: transform   FKSdk_BodyDeformSdkPlane
    :return: transform list   driver_plane有关的所有FK控制器
    '''
    joints = get_FK_done_joint(driver_plane)
    controls = []
    for jnt in joints:
        ctrl = jnt.r.inputs(type='transform')[0]
        if pm.objectType(ctrl.getShape()) == 'nurbsCurve':
            controls.append(ctrl)
    return controls

def create_FK_target_plane(driver_plane):
    '''
    根据driver_plane创建对应的target面片
    :param driver_plane: transform   FKSdk_BodyDeformSdkPlane
    '''
    joints = get_FK_done_joint(driver_plane)
    grp = sdk_group()
    if pm.objExists('Group'):
        pm.parent(grp, pm.PyNode('Group'))
    if pm.objExists("*|PlaneSdkSystem|FKSdk_BodyDeformSdkTarget"):
        pm.delete("*|PlaneSdkSystem|FKSdk_BodyDeformSdkTarget")
    target_plane = create_plane("FKSdk_BodyDeformSdkTarget", grp, joints, 1)
    skin = pm.skinCluster(joints, target_plane, mi=1, tsb=1)
    target_plane.inheritsTransform.set(0)
    wts = []
    for i in range(len(joints)):
        for j in range(4):
            for k in range(len(joints)):
                if i == k:
                    wts.append(1)
                else:
                    wts.append(0)
    skin.setWeights(skin.getGeometry()[0], range(len(joints)),  wts)

def create_FK_attach(controls=None):
    '''
    创建FK面片及其对应连接
    :param controls: transform list   输入控制器或者选择控制器
    '''

    pm.undoInfo(openChunk=1)

    if not controls:
        controls = get_controls(False)

    grp = sdk_group()
    if pm.objExists('Group'):
        pm.parent(grp, pm.PyNode('Group'))
    action_grp = action_group()

    driver_plane = create_plane("FKSdk_BodyDeformSdkPlane", grp, controls, 1)

    if not pm.objExists('FKSdk_StaticSkin'):
        static_jnt = pm.joint(grp, n='FKSdk_StaticSkin')
        static_jnt.v.set(0)
    else:
        static_jnt = pm.PyNode('FKSdk_StaticSkin')
    pm.skinCluster(static_jnt, driver_plane, mi=1, tsb=1)

    for i, ctrl in enumerate(controls):
        prefix = ctrl.name().replace('_ctrl', '_')
        if not pm.objExists(prefix+"AttachShape"):
            attach = create_attach(prefix, action_grp, i, driver_plane)
            attach.v.set(0)
            local_grp = pm.group(em=1, n=prefix + "localGrp", p=attach)
            pm.parent(local_grp, action_grp)
            local = pm.group(em=1, n=prefix + "local", p=local_grp)
            transferGrp = pm.duplicate(local_grp, n=prefix + "transferGrp")[0]
            transfer = transferGrp.listRelatives(c=1)[0]
            pm.rename(transfer, prefix + "transfer")
            jnt = pm.joint(transfer, n=prefix + "transferJnt")
            pm.parentConstraint(attach, local)
            ctrl.t.connect(jnt.t, f=1)
            ctrl.r.connect(jnt.r, f=1)
            ctrlFKSdkGrp = ctrl.duplicate(n=prefix + 'FKSdkGrp', to=1, po=1)[0]
            pm.parent(ctrl, ctrlFKSdkGrp)
            local.t.connect(ctrlFKSdkGrp.t, f=1)
            local.r.connect(ctrlFKSdkGrp.r, f=1)
            ctrlFKSdkGrp.t.connect(transfer.t, f=1)
            ctrlFKSdkGrp.r.connect(transfer.r, f=1)

    driver_planes = pm.ls('*|PlaneSdkSystem|FKSdk_BodyDeformSdkPlane*', type='transform')
    if pm.objExists("FKSdk_BodyDeformSdkPlane"):
        driver_planes.sort()
    else:
        driver_planes[0].rename("FKSdk_BodyDeformSdkPlane")
    if len(driver_planes) > 1:
        driver_plane = comb_plane_dk(driver_planes)
        if driver_plane.listHistory(type="blendShape"):
            pm.rename(driver_plane.listHistory(type="blendShape")[0], 'FKSdk_BodyDeformSdkPlane_bs')
    else:
        driver_plane = driver_planes[0]

    create_FK_target_plane(driver_plane)

    pm.select(clear=True)

    pm.undoInfo(closeChunk=1)

def FKSdk_body_deform_sdk(joints=None):
    '''
    用ADPose对FK控制器进行sdk
    :param joints: str list   驱动骨骼的列表
    '''
    pm.undoInfo(openChunk=1)

    target_plane = pm.ls("*|PlaneSdkSystem|FKSdk_BodyDeformSdkTarget", type="transform")
    driver_plane = pm.ls("*|PlaneSdkSystem|FKSdk_BodyDeformSdkPlane", type="transform")
    if len(target_plane) != 1:
        return pm.warning("can not find target plane")
    if len(driver_plane) != 1:
        return pm.warning("can not find driver plane")
    temp = target_plane[0].duplicate()[0]
    pm.select(temp, driver_plane[0])
    ADPose.ADPoses.auto_edit_by_selected_target(joints)
    pm.delete(temp)

    controls = get_FK_done_controls(driver_plane[0])
    for ctrl in controls:
        ctrl.t.set(0, 0, 0)
        ctrl.r.set(0, 0, 0)

    pm.select(clear=True)

    pm.undoInfo(closeChunk=1)

def mirror_FK_attach():
    '''
    镜像FK面片
    '''
    pm.undoInfo(openChunk=1)

    target_plane = pm.ls("*|PlaneSdkSystem|FKSdk_BodyDeformSdkTarget", type="transform")
    driver_plane = pm.ls("*|PlaneSdkSystem|FKSdk_BodyDeformSdkPlane", type="transform")
    if len(target_plane) != 1:
        return pm.warning("can not find target plane")
    if len(driver_plane) != 1:
        return pm.warning("can not find driver plane")
    ctrl_names = [ctrl.name() for ctrl in get_FK_done_controls(driver_plane[0])]
    mirror_ctrls = [pm.PyNode(config.get_rl_names(name)[0]) for name in ctrl_names]
    create_FK_attach(mirror_ctrls)

    pm.undoInfo(closeChunk=1)

# def FKSdk_body_deform_sdk_mirror(targets=None):
#     target_plane = pm.ls("*|PlaneSdkSystem|FKSdk_BodyDeformSdkTarget", type="transform")
#     driver_plane = pm.ls("*|PlaneSdkSystem|FKSdk_BodyDeformSdkPlane", type="transform")
#     if len(target_plane) != 1:
#         return pm.warning("can not find target plane")
#     if len(driver_plane) != 1:
#         return pm.warning("can not find driver plane")
#
#     mirror_FK_attach()
#
#     if not targets:
#         targets = bs.get_bs(driver_plane[0]).weight.elements()
#     target_mirrors = ADPose.ADPoses.targets_to_mirror(targets)
#     ADPose.ADPoses.add_by_targets([m for _, m in target_mirrors], [driver_plane[0]])
#
#     bs.mirror_targets(driver_plane[0], target_mirrors)

def FKSdk_body_deform_sdk_setToZero(targets):
    '''
    FK sdk 归零
    :param targets: str list   bs目标体
    '''
    if not get_selected_polygons():
        return pm.warning(u"请选择一个带blendShape的模型, 如FKSdk_BodyDeformSdkPlane")
    polygon = get_selected_polygons()[0]
    bs_node = bs_api.get_bs(polygon)
    for target in targets:
        if bs_node.hasAttr(target):
            index = bs_node.attr(target).logicalIndex()
            bs_api.init_bs_target_points(bs_node, index)







