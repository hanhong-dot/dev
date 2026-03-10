# -*- coding: utf-8 -*-#
# -------------------------------------------------------
# NAME       : open_claw_fun
# Describe   : OpenClaw工具核心函数
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2026/3/10
# -------------------------------------------------------
import maya.cmds as cmds


def get_select_controls():
    """获取当前选择的控制器列表"""
    sel = cmds.ls(sl=True, long=True)
    controls = []
    for obj in sel:
        if cmds.objExists(obj):
            controls.append(obj)
    return controls


def get_claw_open_attr(ctrl):
    """获取控制器上的爪子张开属性名称"""
    for attr in ['Open', 'open', 'Claw_Open', 'claw_open', 'ClawOpen', 'clawOpen']:
        if cmds.attributeQuery(attr, node=ctrl, exists=True):
            return attr
    return None


def open_claw(controls, value=1.0):
    """张开爪子：将指定控制器的爪子属性设为张开值"""
    errors = []
    for ctrl in controls:
        if not cmds.objExists(ctrl):
            errors.append(u'{} 不存在'.format(ctrl))
            continue
        attr = get_claw_open_attr(ctrl)
        if attr is None:
            errors.append(u'{} 没有爪子张开属性'.format(ctrl))
            continue
        try:
            attr_min = cmds.attributeQuery(attr, node=ctrl, min=True)
            attr_max = cmds.attributeQuery(attr, node=ctrl, max=True)
            if attr_max:
                value = attr_max[0]
            cmds.setAttr('{}.{}'.format(ctrl, attr), value)
        except Exception as e:
            errors.append(u'{} 设置失败: {}'.format(ctrl, str(e)))
    return errors


def close_claw(controls, value=0.0):
    """闭合爪子：将指定控制器的爪子属性设为闭合值"""
    errors = []
    for ctrl in controls:
        if not cmds.objExists(ctrl):
            errors.append(u'{} 不存在'.format(ctrl))
            continue
        attr = get_claw_open_attr(ctrl)
        if attr is None:
            errors.append(u'{} 没有爪子张开属性'.format(ctrl))
            continue
        try:
            attr_min = cmds.attributeQuery(attr, node=ctrl, min=True)
            if attr_min:
                value = attr_min[0]
            cmds.setAttr('{}.{}'.format(ctrl, attr), value)
        except Exception as e:
            errors.append(u'{} 设置失败: {}'.format(ctrl, str(e)))
    return errors


def reset_claw(controls):
    """重置爪子：将指定控制器的爪子属性设为默认值"""
    errors = []
    for ctrl in controls:
        if not cmds.objExists(ctrl):
            errors.append(u'{} 不存在'.format(ctrl))
            continue
        attr = get_claw_open_attr(ctrl)
        if attr is None:
            errors.append(u'{} 没有爪子张开属性'.format(ctrl))
            continue
        try:
            default_val = cmds.attributeQuery(attr, node=ctrl, listDefault=True)
            if default_val:
                cmds.setAttr('{}.{}'.format(ctrl, attr), default_val[0])
            else:
                cmds.setAttr('{}.{}'.format(ctrl, attr), 0.0)
        except Exception as e:
            errors.append(u'{} 重置失败: {}'.format(ctrl, str(e)))
    return errors
