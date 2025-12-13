# -*- coding: utf-8 -*-#
# -------------------------------------------------------
# NAME       : create_collision_mesh
# Describe   : 说明描述
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2025/6/17__下午7:27
# -------------------------------------------------------
SPHERE_ID = 0
OBB_ID = 1
AABB_ID = 2
CAPSULE_X_ID = 3
CAPSULE_Y_ID = 4
CAPSULE_Z_ID = 5
CAPSULE_R_ID = 6
CYLINDER_Y_ID = 7
OBB_Y_ID = 8

CAPSULE_R_PRE = 'UCP'
OBB_PRE = 'UBX'
SPHERE_PRE = 'USP'
import maya.cmds as cmds
import math

import maya.mel as mel
from apps.tools.maya.ai_collider_tool import get_resource

import numpy as np


def create_collision_mesh_by_data(mesh_data, mesh_name):
    if not mesh_data:
        return None
    __type_list = mesh_data['type'] if 'type' in mesh_data else []
    __origin = mesh_data['origin'] if 'origin' in mesh_data else []
    __scale = mesh_data['scale'] if 'scale' in mesh_data else []
    para = mesh_data['para'] if 'para' in mesh_data else []
    if not __type_list or not __origin or not __scale or not para:
        return None
    __meshs = []
    __mesh_name = ''
    __capsule_r = False
    __capsule_r_mesh_name = ''
    __obb_mesh_name = ''

    for i in range(len(__type_list)):
        if int(__type_list[i][0]) == OBB_ID:
            __obb_mesh_name = '{}_{}_0{}'.format(OBB_PRE, mesh_name, str(i))
            __mesh = create_obb(para[i], __obb_mesh_name, __origin, __scale)
            if not __mesh:
                return False, u'创建OBB失败，请检查输入数据是否正确'
            if __mesh and cmds.objExists(__mesh):
                __meshs.append(__mesh)
        elif int(__type_list[i][0]) == CAPSULE_R_ID:
            __capsule_r_mesh_name = u'{}_{}_0{}'.format(CAPSULE_R_PRE, mesh_name, str(i + 1))
            __mesh = create_capsule_r(para[i], __capsule_r_mesh_name, __origin, __scale)
            if not __mesh:
                return False, u'创建胶囊体失败，请检查输入数据是否正确'
            __meshs.append(__mesh)

    if not __meshs:
        return False, u'未成功创建任何碰撞体，请检查输入数据是否正确'
    cmds.select(__meshs, r=1)

    cmds.xform(__meshs, cpc=1)

    # aiClolid_group = cmds.group(__meshs, name='AiColider_grp'.format(mesh_name), empty=True)
    # cmds.parent(__meshs, aiClolid_group)
    return True, __meshs


def create_obb(para, name, origin, scale):
    obj_path = get_resource.get('obj', 'cube.obj')

    __mesh = import_file(obj_path)
    if not __mesh:
        raise ValueError("No mesh found after importing the OBJ file. Please check the file path and content.")
    __mesh = cmds.rename(__mesh, name)
    if len(para) != 12:
        raise ValueError("OBB parameters must contain 12 values,Please check the input data.")
    tx, ty, tz, qx, qy, qz, qw, sx, sy, sz, xx, yy = para
    rx, ry, rz = quaternion_to_euler(qx, qy, qz, qw)

    cmds.xform(__mesh, translation=(tx, ty, tz), rotation=(rx, ry, rz),
               scale=(sx, sy, sz))

    cmds.xform(__mesh, rp=(0, 0, 0), sp=(0, 0, 0), piv=(0, 0, 0), ws=1)

    tx, ty, tz = cmds.xform(__mesh, q=True, ws=True, t=True)
    sx, sy, sz = cmds.xform(__mesh, q=True, ws=True, s=True)
    cmds.xform(__mesh, translation=(tx + origin[0], ty + origin[1], tz + origin[2]),
               scale=(sx * scale, sy * scale, sz * scale))

    return __mesh


def get_mesh_tr():
    trs = []
    meshs = cmds.ls(type='mesh', l=1)
    if not meshs:
        return trs
    for mesh in meshs:
        tr = cmds.listRelatives(mesh, parent=True, fullPath=True, type='transform')
        if tr:
            trs.append(tr[0])
    if trs:
        trs = list(set(trs))
    return trs


def create_capsule_r(para, name, origin, scale):
    if len(para) < 9:
        raise ValueError("Capsule parameters must contain at least 9 values,Please check the input data.")

    tx, ty, tz, r, l, qx, qy, qz, qw = para[:9]
    rx, ry, rz = quaternion_to_euler(qx, qy, qz, qw)

    capsule_mesh = __create_capsule_mesh(name, r, l * 2)
    cmds.xform(capsule_mesh, translation=(tx, ty, tz), rotation=(rx, ry, rz))
    cmds.xform(capsule_mesh, rp=(0, 0, 0), sp=(0, 0, 0), piv=(0, 0, 0), ws=1)
    tx, ty, tz = cmds.xform(capsule_mesh, q=True, ws=True, t=True)
    cmds.xform(capsule_mesh, translation=(tx + origin[0], ty + origin[1], tz + origin[2]), scale=(scale, scale, scale))
    return capsule_mesh


def __create_capsule_mesh(name, radius, length):
    mesh = \
        cmds.polyCylinder(name=name, radius=radius, height=length, axis=(0, 1, 0), subdivisionsAxis=20,
                          subdivisionsCaps=6,
                          createUVs=1, roundCap=1)[0]
    cmds.setAttr('{}.rotateZ'.format(mesh), 90)
    cmds.makeIdentity(mesh, apply=True, t=1, r=1, s=1, n=0, pn=1)
    return mesh


def euler_matrix_xyz(x, y, z):
    cx, cy, cz = np.cos([x, y, z])
    sx, sy, sz = np.sin([x, y, z])

    Rx = np.array([
        [1, 0, 0],
        [0, cx, -sx],
        [0, sx, cx]
    ])

    Ry = np.array([
        [cy, 0, sy],
        [0, 1, 0],
        [-sy, 0, cy]
    ])

    Rz = np.array([
        [cz, -sz, 0],
        [sz, cz, 0],
        [0, 0, 1]
    ])

    return np.dot(Rz, np.dot(Ry, Rx))


def get_pos_by_rot(pos, dis, rot_deg):
    rot_rad = np.radians(rot_deg)
    R = euler_matrix_xyz(rot_rad[0], rot_rad[1], rot_rad[2])
    forward = np.dot(R, np.array([1, 0, 0]))

    pos = np.asarray(pos)
    if pos.ndim == 1:
        pos = pos.reshape(1, 3)
    return pos + dis * forward


def import_file(obj_path):
    befor_mesh = get_mesh_tr()
    import_obj_file(obj_path)
    after_mesh = get_mesh_tr()
    mesh_list = list(set(after_mesh) - set(befor_mesh))
    if not mesh_list:
        return None
    return mesh_list[0]


def import_obj_file(obj_path, namespace=':'):
    return cmds.file(obj_path, i=True, type="OBJ", ignoreVersion=True, ra=True, mergeNamespacesOnClash=False,
                     namespace=namespace, options="mo=1;lo=0", pr=True, importTimeRange="combine")


def quaternion_to_euler(x, y, z, w):
    q = normalize_quaternion_math(x, y, z, w)
    euler = [0.0, 0.0, 0.0]
    qx, qy, qz, qw = q
    euler[0] = math.atan2(2 * (qw * qx + qy * qz), 1 - 2 * (qx * qx + qy * qy))
    euler[1] = math.asin(clamp(2 * (qw * qy - qx * qz), -1, 1))
    euler[2] = math.atan2(2 * (qw * qz + qx * qy), 1 - 2 * (qy * qy + qz * qz))
    Rad2Deg = 180.0 / math.pi
    euler = [euler[0] * Rad2Deg, euler[1] * Rad2Deg, euler[2] * Rad2Deg]
    return (euler[0], euler[1], euler[2])


def clamp(value, minValue, maxValue):
    # type: (float, float, float) -> float
    return max(minValue, min(maxValue, value))


def normalize_quaternion_math(qx, qy, qz, qw):
    norm = math.sqrt(qx ** 2 + qy ** 2 + qz ** 2 + qw ** 2)
    if norm == 0:
        raise ValueError("Cannot normalize a zero-length quaternion")
    return qx / norm, qy / norm, qz / norm, qw / norm

# if __name__ == '__main__':
#     mesh_data = {u'origin': [-2.7134837562629652, -1.4343047973389353, -1.3463235144053503],
#                  u'scale': 4.155882836981186, u'type': [[6]], u'para': [
#             [0.49922701716423035, 0.4885149896144867, 0.32756033539772034, 0.25178468227386475, 0.2360420674085617,
#              -0.008238709531724453, -0.014029833488166332, 0.9303725361824036, 0.3662540912628174, 0.0, 0.0, 0.0]]}
#     create_collision_mesh_by_data(mesh_data, 'test_mesh')
#     para = mesh_data['para'][0]
#     create_capsule_r(para, name='test_capsule_r', origin=mesh_data['origin'], scale=mesh_data['scale'])
