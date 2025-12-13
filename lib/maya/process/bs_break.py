# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       : bs_break
# Describe   : 引处P4工修,断开bs连接
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2022/12/13__14:26
# -------------------------------------------------------
import maya.cmds as cmds


def breakConnection(attr):
    upstream = cmds.listConnections(attr, s=True, d=False, p=True)
    if upstream:
        print upstream
        cmds.disconnectAttr(upstream[0], attr)


def checkIfmesh(sels):
    meshs = []
    for ii in sels:
        shapes = cmds.listRelatives(ii, s=True,f=1)
        if shapes:
            if cmds.objectType(shapes[0]) == 'mesh':
                meshs.append(ii)
    return meshs


def listBlendshapeName(mesh):
    his = cmds.listHistory(mesh, pdo=1, il=2)
    bs_name = []
    if his:
        for ii in his:
            if cmds.objectType(ii) == 'blendShape':
                bs_name.append(ii)
    if bs_name:
        return bs_name


def mainFunc():
    sel = cmds.ls(sl=True,l=1)
    if sel:
        mesh = checkIfmesh(sel)
        if mesh:
            for ii in mesh:
                bs = listBlendshapeName(ii)
                if bs:
                    for hh in bs:
                        attrs = cmds.listAttr(hh + '.w', m=True)
                        if attrs :
                            for atr in attrs:

                                breakConnection(hh + '.' + atr)
