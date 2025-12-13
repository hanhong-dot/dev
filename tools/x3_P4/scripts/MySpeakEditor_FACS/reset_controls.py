# -*- coding: UTF-8 -*-
from maya import cmds


def reset_ctrls(ctrls_list=None):
    '''
    控制器属性归零
    :param ctrls_list: str list   控制器列表，无输入则取所选的控制器列表
    :return: str list   被改变了的控制器列表
    '''

    if ctrls_list is None:
        ctrls_list = cmds.ls(sl=True)

    for ctrl in ctrls_list:
        changed_ctrl_list = []
        ctrl_attrs_list = cmds.listAttr(ctrl, unlocked=True, connectable=False, keyable=True, settable=True, visible=True)
        for ctrl_attr in ctrl_attrs_list:
            if cmds.connectionInfo(ctrl+'.'+ctrl_attr, isDestination=True):
                if cmds.listConnections(ctrl+'.'+ctrl_attr, d=0, s=1, type='animCurveTL') \
                        or cmds.listConnections(ctrl+'.'+ctrl_attr, d=0, s=1, type='animCurveTA') \
                        or cmds.listConnections(ctrl+'.'+ctrl_attr, d=0, s=1, type='animCurveTU'):
                    changed_ctrl_list.append(ctrl_attr)
            else:
                 changed_ctrl_list.append(ctrl_attr)
        for ctrl_attr in changed_ctrl_list:
            ctrl_attr_default = cmds.attributeQuery(ctrl_attr, node=ctrl, listDefault=True)
            if cmds.getAttr(ctrl + '.' + ctrl_attr) == ctrl_attr_default[0]:
                pass
            else:
                cmds.setAttr(ctrl + '.' + ctrl_attr, ctrl_attr_default[0])

    return changed_ctrl_list


def get_face_ctrls():
    '''
    获取脸部所有的控制器，排除口型控制器
    :return: str list   控制器列表
    '''
    face_ctrls = []
    FaceRigGroup = "FaceGroup"
    for ctrl_longname_shape in cmds.ls(dag=1, l=1, type='nurbsCurve'):
        if '|%s|'%FaceRigGroup in ctrl_longname_shape and not '|Fits|' in ctrl_longname_shape:
            if cmds.getAttr(ctrl_longname_shape+'.overrideDisplayType') == 0:
                ctrl = cmds.listRelatives(ctrl_longname_shape, parent=True)[0]
                if u'speak' not in ctrl:
                    face_ctrls.append(ctrl)
    return face_ctrls


def reset_face_ctrls():
    '''
    将脸部控制器归零
    '''
    reset_ctrls(get_face_ctrls())