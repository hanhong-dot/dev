# -*- coding: UTF-8 -*-
import maya.cmds as cmds
import pymel.core as pm

speakBS_Ty_list = [u'UpperLipRaiser', u'LowerLipDepressor', u'MouthStretch', u'LipZipUp', u'LipZipDn']
jnt_name = ['eye*Joint', 'brow*Joint', 'Nose*Joint', 'nose*Joint', 'lip*Joint', 'jawJoint', 'face*Joint', 'fk*Joint']
jnt_list = cmds.ls(jnt_name)

def get_scale(_scale=None):
    '''
    获取某个轴向的缩放值
    :param _scale: str   某个轴向的缩放属性名称，如'scaleX'
    :return: dict   记录有缩放值的骨骼及对应的值
    '''
    scale_list = {}
    for jnt in jnt_list:
        scale_value = cmds.getAttr(jnt + '.' + _scale)
        if not abs(scale_value - 1.0) < 0.00001:
            scale_list[jnt] = scale_value

    return scale_list

def get_blendnode(jnt=None, _scale=None):
    '''
    创建blendWeighted节点，做属性连接
    :param jnt: str   骨骼名
    :param _scale: str   某个轴向的缩放属性名称，如'scaleX'
    :return: 该blendWeighted节点
    '''
    if cmds.listConnections(jnt + '.scale'):
        input = cmds.listConnections(jnt + '.scale')[0]
        blendnode = pm.createNode('blendWeighted', n=jnt+'_'+_scale + '_blendWeighted')
        pm.disconnectAttr(input + '.scale', jnt + '.scale')
        pm.connectAttr(input + '.scaleX', jnt + '.scaleX')
        pm.connectAttr(input + '.scaleY', jnt + '.scaleY')
        pm.connectAttr(input + '.scaleZ', jnt + '.scaleZ')
        pm.connectAttr(input + '.' + _scale, blendnode + '.weight[0]')
        pm.connectAttr(blendnode + '.output', jnt + '.' + _scale, f=1)
        pm.setAttr(blendnode + '.input[0]', 1)
        pm.aliasAttr('Default', blendnode + '.w[0]')
    elif cmds.listConnections(jnt+'.'+_scale, type='blendWeighted'):
        blendnode = cmds.listConnections(jnt+'.'+_scale, type='blendWeighted')[0]
    else:
        input = cmds.listConnections(jnt+'.'+_scale)[0]
        blendnode = pm.createNode('blendWeighted', n=jnt+'_'+_scale + '_blendWeighted')
        pm.connectAttr(input + '.' + _scale, blendnode + '.weight[0]')
        pm.connectAttr(blendnode + '.output', jnt + '.' + _scale, f=1)
        pm.setAttr(blendnode + '.input[0]', 1)
        pm.aliasAttr('Default', blendnode + '.w[0]')

    return blendnode

def connect_scale(attr=None):
    '''
    连接xyz三个轴向上的缩放
    :param attr: str   属性名
    '''
    cmds.undoInfo(openChunk=1)

    if get_scale('scaleX'):
        connect_one_scale(attr=attr, _scale='scaleX')
    if get_scale('scaleY'):
        connect_one_scale(attr=attr, _scale='scaleY')
    if get_scale('scaleZ'):
        connect_one_scale(attr=attr, _scale='scaleZ')

    reset_fake_scale(attr)

    cmds.undoInfo(closeChunk=1)

def connect_one_scale(attr=None, _scale=None):
    '''
    连接一个轴向上的缩放
    :param attr: str   属性名，即口型
    :param _scale: str   某个轴向的缩放属性名称，如'scaleX'
    '''
    bridge = pm.PyNode("SpeakBlendShapeBridge")

    scale_list = get_scale(_scale)

    for i, jnt in enumerate(scale_list):
        jnt_value = scale_list[jnt]
        blendnode = get_blendnode(jnt=jnt, _scale=_scale)
        weight_list = pm.aliasAttr(blendnode, query=True)
        if attr not in weight_list:
            num = len(weight_list)
            pm.connectAttr(bridge + '.' + attr, blendnode + '.weight[%d]' % num)
            pm.aliasAttr(attr, blendnode + '.weight[%d]' % num)
            pm.setAttr(blendnode + '.input[%d]' % num, 0)
        else:
            num = pm.PyNode(blendnode + '.' + attr).logicalIndex()
        old_value = pm.getAttr(blendnode + '.input[%d]' % num)
        ctrl_value = jnt_value - old_value
        if ctrl_value != 1:
            pm.setAttr(blendnode + '.input[%d]' % num, jnt_value-1)

def reset_scale(attr=None):
    '''
    还原某个口型上所有骨骼的的缩放值
    :param attr: str   属性名，即口型
    '''
    for jnt in jnt_list:
        for _scale in ['scaleX', 'scaleY', 'scaleZ']:
            if cmds.listConnections(jnt+'.'+_scale, type='blendWeighted'):
                blendnode = cmds.listConnections(jnt + '.' + _scale, type='blendWeighted')[0]
                if cmds.objExists(blendnode + '.' + attr):
                    num = pm.PyNode(blendnode + '.' + attr).logicalIndex()
                    pm.setAttr(blendnode + '.input[%d]' % num, 0)

def reset_fake_scale(attr=None):
    '''
    针对某些创建过scale连接后被再一次修改时缩放值归1了的特殊情况，需要额外处理，将blendWeighted节点上的输入值打为0，
    需要每次修改后都检查一遍有没有这种情况，否则再次修改后缩放值会不对
    :param attr: str   属性名，即口型
    '''
    for jnt in jnt_list:
        for _scale in ['scaleX', 'scaleY', 'scaleZ']:
            scale_value = cmds.getAttr(jnt + '.' + _scale)
            if abs(scale_value - 1.0) < 0.00001:
                if cmds.listConnections(jnt + '.' + _scale, type='blendWeighted'):
                    blendnode = cmds.listConnections(jnt + '.' + _scale, type='blendWeighted')[0]
                    if cmds.objExists(blendnode + '.' + attr):
                        num = pm.PyNode(blendnode + '.' + attr).logicalIndex()
                        pm.setAttr(blendnode + '.input[%d]' % num, 0)

