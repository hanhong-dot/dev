# coding=utf-8
import pymel.core as pm
import maya.cmds as cmds
import os
import maya.mel as mm
'''
给冬豪出的一个在干净口型文件中新增自定义bs口型的脚本
'''

def get_BS(BS_geo):
    '''
    获取bs节点
    :param BS_geo: transform   带bs的模型
    :return: bs节点
    '''
    BS_geo = pm.PyNode(BS_geo)
    if BS_geo.getShape():
        if BS_geo.getShape().listHistory(type='blendShape'):
            BS_node = BS_geo.getShape().listHistory(type='blendShape')[0]
            return BS_node

def add_blank_BS(au_num, BS_geo='mod|ST_Head', parent='ST_Head_BS_grp', ifDelete=False):
    '''
    增加一个空的bs口型
    :param au_num: int   目标bs数量
    :param BS_geo: transform   带bs的模型
    :param parent: 指定重建的bs放在哪个组下
    :param ifDelete: bool   True：删除重建的bs模型；False：保留重建的bs模型
    :return: str list   新的口型列表
    '''
    BS_node = get_BS(BS_geo)
    weight_list = BS_node.listAliases()
    if not weight_list:
        old_num = 0
    else:
        old_num = max([weight[1].logicalIndex() for weight in weight_list]) + 1

    old_attr_list = get_new_list('Au_', 1, old_num + 1, 1)
    attr_list = get_new_list('Au_', 1, au_num + 1, 1)
    new_attr_list = list(set(attr_list).difference(set(old_attr_list)))
    new_attr_list.sort()
    if new_attr_list:
        for i, attr in enumerate(new_attr_list):
            pm.setAttr(BS_node.envelope, 0)
            dup_BS_geo = pm.duplicate(BS_geo)[0]
            if not pm.objExists(parent):
                parent = pm.group(em=1, w=1, n=parent)
                parent.v.set(0)
            pm.parent(dup_BS_geo, pm.PyNode(parent))
            dup_BS_geo.rename(attr)
            pm.blendShape(BS_node, edit=True, t=(BS_geo, old_num + i, dup_BS_geo, 1.0))
            pm.setAttr(BS_node.envelope, 1)
            pm.sculptTarget(BS_node, t=-1, e=1)
            if ifDelete:
                pm.delete(dup_BS_geo)
    return new_attr_list

def add_attribute(ctrl, attr):
    '''
    给控制器新增一个0-1的属性
    :param ctrl: transform   控制器
    :param attr: str   属性名
    '''
    if not ctrl.hasAttr(attr):
        pm.addAttr(ctrl, ln=attr, at='double', min=0, max=1, dv=0)
        pm.setAttr(ctrl + '.' + attr, e=1, keyable=1)
        pm.setAttr(ctrl + '.' + attr, 0)

def connect_bs(attr, BS_node):
    '''
    连接属性
    :param attr: str   属性名
    :param BS_node: bs节点
    '''
    src = pm.PyNode("SpeakBlendShapeBridge")
    dst = BS_node
    ctrl = pm.PyNode('speakControl')
    add_attribute(src, attr)
    add_attribute(ctrl, attr)
    if not src.attr(attr).isLocked() and dst.hasAttr(attr) and not dst.attr(attr).inputs():
        src.attr(attr).connect(dst.attr(attr))
        if not pm.objExists(attr + 'BW'):
            pm.createNode('blendWeighted', n=attr + 'BW')
        BW = pm.PyNode(attr + 'BW')
        if not BW.input[0].listConnections():
            ctrl.attr(attr).connect(BW.input[0])
        if attr in ['UpperLipRaiser', 'LowerLipDepressor', 'MouthStretch', 'LipZipUp',
                    'LipZipDn', 'JawDrop', 'MouthCloseDn', 'MouthCloseUp']:
            if not BW.weight[0].listConnections():
                ctrl.ty.connect(BW.weight[0])
                print attr, 'ty'
        else:
            if not BW.weight[0].listConnections():
                ctrl.tx.connect(BW.weight[0])
                print attr, 'tx'
        if not BW.output.listConnections():
            BW.output.connect(src.attr(attr))

def get_new_list(prefix, start, end, ifzero=0):
    '''
    获取一个有固定格式的新名称列表，如get_new_list('base', 1, 5, 1)，即['base01', 'base02', 'base03', 'base04']
    :param prefix: str   前缀名
    :param start: int   开始数
    :param end: int   结束数
    :param ifzero: 后缀是否需要%02d格式
    :return: str list   新列表
    '''
    new_list = []
    for i in range(start, end):
        if ifzero:
            new_list.append(prefix+'%02d' % i)
        else:
            new_list.append(prefix+'%d' % i)
    if new_list:
        if start == 0:
            new_list[0] = new_list[0].replace('0', '')
    return new_list


def transfer_vertex(old_list, new_list):
    '''
    传递点序给原来的口型
    :param old_list: str list   原本的口型列表
    :param new_list: str list   新的口型列表
    '''
    for i in range(len(new_list)):
        BS_node = cmds.blendShape(new_list[i], old_list[i])[0]
        cmds.setAttr(BS_node+'.w[0]', 1)
        cmds.delete(new_list[i])
        cmds.bakePartialHistory(old_list[i], pc=True)


def add_Au(au_num):
    '''
    增加口型至一定数量
    :param au_num: int   目标口型数量
    :return: str list   新的口型列表
    '''
    head_name = 'ST_Head'
    teeth_name = 'ST_Teeth'
    add_blank_BS(au_num, head_name, head_name + '_BS_grp')
    add_blank_BS(au_num, teeth_name, teeth_name + '_BS_grp')
    new_au_list = get_new_list('Au_', 1, au_num + 1, 1)

    for attr in new_au_list:
        connect_bs(attr, get_BS(head_name))
        a = get_BS(head_name)
        b = get_BS(teeth_name)
        if not pm.isConnected(a.attr(attr), b.attr(attr)):
            a.attr(attr).connect(b.attr(attr), f=1)

    return new_au_list

def change_Au(au_num, path):
    '''
    输入现有口型数和obj路径，改变所有口型
    :param au_num: int   现有口型数量
    :param path: str   obj所在路径
    '''
    obj_name_list = os.listdir(path)

    for i, obj in enumerate(obj_name_list):
        mm.eval(
            '''file -import -type "OBJ"  -ignoreVersion -ra true -rdn -mergeNamespacesOnClash true -namespace ":" 
            -options "mo=1;lo=0"  -pr  -importTimeRange "combine" "{}";'''.format(os.path.realpath(path + '/' + obj)
                                                                                  .replace('\\', '/')))

    attr_list = get_new_list('ST_Head_BS_grp|Au_', 1, au_num + 1, 1)
    new_list = get_new_list('ST_Headbase', 0, au_num)
    transfer_vertex(attr_list, new_list)
    attr_list = get_new_list('ST_Teeth_BS_grp|Au_', 1, au_num + 1, 1)
    new_list = get_new_list('ST_Teethbase', 0, au_num)
    transfer_vertex(attr_list, new_list)


def test():
    # 增加bs到20个
    from wuwu.MySpeakTool import new_au
    reload(new_au)
    new_au.add_Au(20)

    # 输入现有bs数和路径，改变bs
    path = r'C:\Users\wuwu\Downloads\ST_character(1)\model'
    new_au.change_Au(20, path)