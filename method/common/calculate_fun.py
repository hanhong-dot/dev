# -*- coding: utf-8 -*-
# -----------------------------------
# @File    : calculate_fun.py
# @Author  : linhuan
# @Time    : 2025/7/14 21:02
# @Description : 
# -----------------------------------
import numpy as np
import math


def get_quaternion_from_vectors(v1, v2):
    v1 = v1 / np.linalg.norm(v1)
    v2 = v2 / np.linalg.norm(v2)

    dot = np.dot(v1, v2)
    dot = np.clip(dot, -1.0, 1.0)
    theta = math.acos(dot)

    axis = np.cross(v1, v2)
    axis_norm = np.linalg.norm(axis)

    if axis_norm < 1e-8:
        if dot > 0.99999:
            quat = np.array([1.0, 0.0, 0.0, 0.0])
        else:
            orthogonal = np.array([0.0, 1.0, 0.0]) if abs(v1[0]) < 0.9 else np.array([0.0, 0.0, 1.0])
            axis = np.cross(v1, orthogonal)
            axis = axis / np.linalg.norm(axis)
            quat = np.concatenate(([0.0], axis))
    else:
        axis = axis / axis_norm
        half_theta = theta / 2
        sin_half_theta = math.sin(half_theta)
        quat = np.concatenate(([math.cos(half_theta)], axis * sin_half_theta))
    return quat


def quaternion_to_euler_xyz(q):
    w, x, y, z = q
    t0 = 2.0 * (w * x + y * z)
    t1 = 1.0 - 2.0 * (x * x + y * y)
    roll_x = math.atan2(t0, t1)

    t2 = 2.0 * (w * y - z * x)
    t2 = np.clip(t2, -1.0, 1.0)
    pitch_y = math.asin(t2)

    t3 = 2.0 * (w * z + x * y)
    t4 = 1.0 - 2.0 * (y * y + z * z)
    yaw_z = math.atan2(t3, t4)
    roll_x = math.degrees(roll_x)
    pitch_y = math.degrees(pitch_y)
    yaw_z = math.degrees(yaw_z)

    return roll_x, pitch_y, yaw_z


def normalize(v):
    norm = np.linalg.norm(v)
    return v / norm if norm != 0 else v


def matrix_to_euler_xyz(m):
    # 从3x3旋转矩阵提取欧拉角（XYZ顺序）
    if abs(m[0, 2]) < 1.0:
        y = math.asin(-m[0, 2])
        x = math.atan2(m[1, 2], m[2, 2])
        z = math.atan2(m[0, 1], m[0, 0])
    else:
        y = math.pi / 2 if m[0, 2] <= -1.0 else -math.pi / 2
        x = math.atan2(-m[1, 0], -m[1, 1])
        z = 0.0
    return [math.degrees(a) for a in (x, y, z)]


def get_normal_euler_xyz(v1, v2):
    v1 = normalize(np.array(v1))
    v2 = normalize(np.array(v2))

    z_axis = normalize(np.cross(v1, v2))

    # 选个合适的up向量
    up_hint = np.array([0, 1, 0]) if abs(z_axis[1]) < 0.99 else np.array([0, 0, 1])

    x_axis = normalize(np.cross(up_hint, z_axis))
    y_axis = np.cross(z_axis, x_axis)

    rot_matrix = np.column_stack((x_axis, y_axis, z_axis))

    return matrix_to_euler_xyz(rot_matrix)


def get_rotation_by_two_vectors(v1, v2):
    quat = get_quaternion_from_vectors(np.array(v1), np.array(v2))
    euler = quaternion_to_euler_xyz(quat)
    return euler

    # if vector_length(euler)< 1e-6:
    #     angles = [0, 0, 0]
    # else:
    #     try:
    #         angles = get_normal_euler_xyz(v1, v2)
    #     except:
    #         angles = [0, 0, 0]
    # return [euler[0] - angles[0], euler[1] - angles[1], euler[2] - angles[2]]


def vector_length(v):
    return math.sqrt(v[0] ** 2 + v[1] ** 2 + v[2] ** 2)


if __name__ == '__main__':
    v1 = [1, 0, 0]
    v2 = [0.8595142267985325, 0.28378150771838256, -0.4250921662510406]

    print(get_rotation_by_two_vectors(v1, v2))
