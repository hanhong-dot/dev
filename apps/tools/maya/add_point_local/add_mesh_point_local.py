# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       :
# Describe   : 模型每个点创建一个local
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2024/1019
# -------------------------------------------------------
from lib.maya.node.mesh import Mesh
import maya.cmds as cmds


def add_select_meshs_point_local():
    meshs=cmds.ls(sl=1)
    meshs=get_meshs(meshs)
    grp=cmds.group(em=True, name='local_grp')

    locals=add_meshs_point_local(meshs)

    if locals:
        cmds.parent(locals,grp)


def add_meshs_point_local_grp(meshs,grp_name='local_grp',start_num=0):
    grps=add_meshs_point_local(meshs,start_num)

    if not grps:
        return
    if cmds.ls(grp_name):
        cmds.parent(grps,cmds.ls(grp_name)[0])
    else:
        grp=cmds.group(em=True, name=grp_name)
        cmds.parent(grps,grp)



def get_select_meshs():
    meshs=cmds.ls(sl=1)
    meshs=get_meshs(meshs)
    return meshs


def get_meshs(objs):
    meshs=[]
    for obj in objs:
        shape=cmds.listRelatives(obj,s=1,type='mesh')
        if shape:
            meshs.append(obj)
    return meshs


def add_meshs_point_local(meshs,start_num=0):
    grps=[]
    for mesh in meshs:
        grps.append(add_mesh_point_local(mesh,start_num))
    return grps


def add_mesh_point_local(mesh,start_num=0):
    points=Mesh(mesh).get_pology_points()
    locals=[]
    grp_name='{}_local_grp'.format(mesh.split('|')[-1])
    if cmds.ls(grp_name):
        cmds.delete(cmds.ls(grp_name))
    if not points:
        return
    for i in range(len(points)):
        local=creat_point_local(points[i],i+int(start_num))
        if local and local not in locals:
            locals.append(local)

    grp=cmds.group(em=True, name=grp_name)
    cmds.parent(locals,grp)
    return grp



def creat_point_local(point,num):
    local_name='local_{}'.format(num)
    local=cmds.spaceLocator(n=local_name)[0]
    cmds.xform(local, s=[0.2, 0.2, 0.2])
    cmds.select(point)
    cmds.select(local, add=True)
    __constraint=cmds.pointOnPolyConstraint()
    point_pos=cmds.xform(point, q=1, ws=1, t=1)
    local_pos=cmds.xform(local, q=1, ws=1, t=1)
    offset_x=point_pos[0]-local_pos[0]
    offset_y=point_pos[1]-local_pos[1]
    offset_z=point_pos[2]-local_pos[2]
    if offset_x!=0:
        cmds.setAttr(__constraint[0]+'.offsetTranslateX',offset_x)
    if offset_y!=0:
        cmds.setAttr(__constraint[0]+'.offsetTranslateY',offset_y)
    if offset_z!=0:
        cmds.setAttr(__constraint[0]+'.offsetTranslateZ',offset_z)


    return local


