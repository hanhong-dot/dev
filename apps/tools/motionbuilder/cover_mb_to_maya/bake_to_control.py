# -*- coding: utf-8 -*-
# author: linhuan
# file: bake_to_control.py
# time: 2025/12/1 16:20
# 修改自 MaxToMaya_kami (python/MaxToMaya_kami)
# description:

import maya.cmds as cmds
import maya.mel as mel

import maya.OpenMaya as om

def bake_to_control_by_name_space(name_space, start_frame, end_frame):
    timemin = float(start_frame)
    timemax = float(end_frame)
    cmds.currentTime(timemin)
    FKcon = [u'FKHip_L',
             u'FKToes_R',
             u'FKAnkle_R',
             u'FKKnee_R',
             u'FKHip_R',
             u'FKMiddleFinger1_R',
             u'FKToes_L',
             u'FKAnkle_L',
             u'FKKnee_L',
             u'FKIndexFinger3_L',
             u'FKIndexFinger2_L',
             u'FKIndexFinger1_L',
             u'FKThumbFinger3_L',
             u'FKPinkyFinger3_L',
             u'FKPinkyFinger2_L',
             u'FKPinkyFinger1_L',
             u'FKCup_L',
             u'FKRingFinger1_R',
             u'FKPinkyFinger3_R',
             u'FKPinkyFinger2_R',
             u'FKPinkyFinger1_R',
             u'FKElbow_R',
             u'FKShoulder_R',
             u'FKRingFinger3_R',
             u'FKRingFinger2_R',
             u'FKThumbFinger3_R',
             u'FKThumbFinger2_R',
             u'FKThumbFinger1_R',
             u'FKMiddleFinger3_R',
             u'FKMiddleFinger2_R',
             u'FKCup_R',
             u'FKIndexFinger3_R',
             u'FKIndexFinger2_R',
             u'FKIndexFinger1_R',
             u'FKRingFinger3_L',
             u'FKRingFinger2_L',
             u'FKRingFinger1_L',
             u'FKWrist_L',
             u'FKElbow_L',
             u'FKShoulder_L',
             u'FKScapula_R',
             u'FKWrist_R',
             u'FKSpine1_M',
             u'FKRoot_M',
             u'FKScapula_L',
             u'FKNeck_M',
             u'FKNeckPart1_M',
             u'FKHead_M',
             u'FKChest_M',
             u'FKSpine3_M',
             u'FKSpine2_M',
             u'FKThumbFinger2_L',
             u'FKThumbFinger1_L',
             u'FKMiddleFinger3_L',
             u'FKMiddleFinger2_L',
             u'FKMiddleFinger1_L',
             u'RootX_M',
             u'FKPinkyFinger0_L',
             u'FKRingFinger0_L',
             u'FKMiddleFinger0_L',
             u'FKIndexFinger0_L',
             u'FKPinkyFinger0_R',
             u'FKRingFinger0_R',
             u'FKMiddleFinger0_R',
             u'FKIndexFinger0_R',
             u'FKToe_a_0_R',
             u'FKToe_a_1_R',
             u'FKToe_b_0_R',
             u'FKToe_b_1_R',
             u'FKToe_b_2_R',
             u'FKToe_c_0_R',
             u'FKToe_c_1_R',
             u'FKToe_c_2_R',
             u'FKToe_d_0_R',
             u'FKToe_d_1_R',
             u'FKToe_d_2_R',
             u'FKToe_e_0_R',
             u'FKToe_e_1_R',
             u'FKToe_e_2_R',
             u'FKToe_a_0_L',
             u'FKToe_a_1_L',
             u'FKToe_b_0_L',
             u'FKToe_b_1_L',
             u'FKToe_b_2_L',
             u'FKToe_c_0_L',
             u'FKToe_c_1_L',
             u'FKToe_c_2_L',
             u'FKToe_d_0_L',
             u'FKToe_d_1_L',
             u'FKToe_d_2_L',
             u'FKToe_e_0_L',
             u'FKToe_e_1_L',
             u'FKToe_e_2_L'
             ]

    fk_js = [u'FKAnkle_L', u'FKAnkle_R', u'FKWrist_L', u'FKWrist_R']
    ik_cons = [u'IKLeg_L', u'IKLeg_R', u'IKArm_L', u'IKArm_R']
    ik_vector = [u'PoleLeg_L', u'PoleLeg_R', u'PoleArm_L', u'PoleArm_R']

    NameSpace = str(name_space)

    if ':' in NameSpace:
        nametext = NameSpace.split(':')[0]
        FKcon = [nametext + ':' + ii for ii in FKcon]
        fk_js = [nametext + ':' + ii for ii in fk_js]
        ik_cons = [nametext + ':' + ii for ii in ik_cons]
        ik_vector = [nametext + ':' + ii for ii in ik_vector]

    # print FKcon

    constrains = []
    locs = []
    for item in FKcon:
        if 'FK' in item:
            extra = item.replace('FK', 'FKExtra')
        elif 'RootX' in item:
            extra = item.replace('Root', 'RootExtra')
        if cmds.objExists(extra):
            parent = cmds.listRelatives(extra, p=True)[0]
            loc = cmds.spaceLocator(n=item + '_fixOrder_locs')[0]
            cmds.parent(loc, parent)
            mel.eval('ResetTransformations("{0}")'.format(loc))
            cmds.setAttr(loc + '.rotateOrder', cmds.getAttr(item + '.rotateOrder'))
            cons = cmds.parentConstraint(extra, loc)[0]
            constrains.append(cons)
            locs.append(loc)

    if locs:
        # 2023-12-19
        # add function  setAttr "FKNeck_M.bend_atte" 1 at bake pre

        # 2024-08-07
        # add function  setAttr "FKHead_M.autoTwist" 0 at bake pre
        neck_sub=''
        head_auto_twist=''
        for gg in FKcon:
            if 'FKNeck_M' in gg:
                neck_sub = gg
            if 'FKHead_M' in gg:
                head_auto_twist = gg

        if neck_sub:
            if cmds.objExists(neck_sub + '.bend_atte'):
                cmds.setAttr(neck_sub + '.bend_atte', 1)
            elif cmds.objExists(neck_sub + '.BendAtte'):
                cmds.setAttr(neck_sub + '.BendAtte', 1)
        if head_auto_twist:
            if cmds.objExists(head_auto_twist + '.autoTwist'):
                cmds.setAttr(head_auto_twist + '.autoTwist', 0)

        cmds.bakeResults(locs, sm=True, t=(timemin, timemax), sb=1)
        cmds.delete(constrains)
        for ll in locs:
            mainFK = ll.split('_fixOrder_locs')[0]
            cmds.connectAttr(ll + '.translateX', mainFK + '.translateX')
            cmds.connectAttr(ll + '.translateY', mainFK + '.translateY')
            cmds.connectAttr(ll + '.translateZ', mainFK + '.translateZ')

            cmds.connectAttr(ll + '.rotateX', mainFK + '.rotateX')
            cmds.connectAttr(ll + '.rotateY', mainFK + '.rotateY')
            cmds.connectAttr(ll + '.rotateZ', mainFK + '.rotateZ')

        FKCon_ex = []
        for dd in FKcon:
            if cmds.objExists(dd):
                FKCon_ex.append(dd)
            else:
                cmds.warning('{} Non-Ex !! please check your scenes'.format(dd))

        cmds.bakeResults(FKCon_ex, sm=True, t=(timemin, timemax), sb=1)
        cmds.delete(locs)
        cleanMocapjoint(NameSpace)



def BakeIKcontroler( fk_js, ik_cons, ik_vector, timemin, timemax):
    sp_locs = []
    constrains = []

    objtest = fk_js[0] + '_FKIK_switch'
    if cmds.objExists(objtest):
        # print '============'
        # print objtest
        # print '============'
        for ii in fk_js:
            sploc = cmds.spaceLocator(n=ii + '_joint_loc')[0]
            cons = cmds.parentConstraint(ii + '_FKIK_switch', sploc, mo=False)[0]
            sp_locs.append(sploc)
            constrains.append(cons)

        vec_locs = []
        for ii in range(4):
            cmds.setAttr(ik_vector[ii] + '.follow', 0)
            sploc = cmds.spaceLocator(n=fk_js[ii] + '_vector_sp_loc')[0]
            cons = cmds.parentConstraint(fk_js[ii] + '_FKIK_switch_pole', sploc, mo=False)[0]

            constrains.append(cons)
            vec_locs.append(sploc)

        cmds.bakeResults(sp_locs + vec_locs, sm=True, t=(timemin, timemax), sb=1)
        cmds.delete(constrains)

        constrains = []
        for ii in range(4):
            pp = cmds.parentConstraint(sp_locs[ii], ik_cons[ii], mo=False)[0]
            po = cmds.pointConstraint(vec_locs[ii], ik_vector[ii], mo=False)[0]
            constrains.append(pp)
            constrains.append(po)

        cmds.bakeResults(ik_vector + ik_cons, sm=True, t=(timemin, timemax), sb=1)
        cmds.delete(constrains, vec_locs, sp_locs)
        om.MGlobal.displayInfo('Bake HIK to maya already over!!!')
    else:
        om.MGlobal.displayError('ik bake failure, maybe the rigging not completely, please call kami!')


def cleanMocapjoint(name_space):
    NameSpace = str(name_space)
    if ':' in NameSpace:
        nametext = NameSpace.split(':')[0]
        root = [nametext + ':' + 'Root_MoCap_M', nametext + ':' + 'Mocap_Root_M']
    else:
        root = ['Root_MoCap_M', 'Mocap_Root_M']
    for uu in root:
        if cmds.objExists(uu):
            joint = [uu]
            sel = cmds.listRelatives(uu, ad=True)
            for ii in sel:
                if cmds.objectType(ii) == 'joint':
                    joint.append(ii)
            for ii in joint:
                disConnnectAttr(ii + '.tx')
                disConnnectAttr(ii + '.ty')
                disConnnectAttr(ii + '.tz')
                disConnnectAttr(ii + '.rx')
                disConnnectAttr(ii + '.ry')
                disConnnectAttr(ii + '.rz')
            cmds.joint(uu, e=True, apa=True, ch=True)
            cmds.setAttr(uu + '.translateX', 0)
            cmds.setAttr(uu + '.translateY', 0)
            cmds.setAttr(uu + '.translateZ', 0)
        else:
            cmds.warning('{0} Non-Ex , check it!!'.format(uu))


def disConnnectAttr(attr):
    source = cmds.listConnections(attr, p=True, s=True, d=False)
    if source:
        cmds.disconnectAttr(source[0], attr)
