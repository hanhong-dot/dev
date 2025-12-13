# -*- coding: utf-8 -*-#
# -------------------------------------------------------
# NAME       : mesh_fun
# Describe   : 说明描述
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2025/6/17__下午6:42
# -------------------------------------------------------

from lib.maya.node.mesh import Mesh
import uuid
import maya.cmds as cmds
import time


def get_mesh_data(mesh, convex_type, max_count):
    mesh_obj = Mesh(mesh)
    vertices = mesh_obj.get_pology_Vertices()
    faces = mesh_obj.topologyStructure
    timestamp_ms = int(time.time() * 1000)
    return {
        'file_name': '{}_{}'.format(mesh.split('|')[-1], timestamp_ms),
        'vertices': vertices,
        'faces': faces,
        'convex_type': convex_type,
        'max_count': max_count
    }


def get_meshs_data(meshs):
    vertices = []
    faces = []
    mesh_data = {}
    __uuid = uuid.uuid4().get_hex()
    for mesh in meshs:
        cmds.makeIdentity(mesh, apply=True, t=1, r=1, s=1, n=2)

        mesh_obj = Mesh(mesh)
        vertices = mesh_obj.get_pology_Vertices()
        faces = mesh_obj.topologyStructure
        vertices.extend(vertices)
        faces.extend(faces)
    if not vertices or not faces:
        return None
    mesh_data['file_name'] = '{}__{}'.format(meshs[0].split('|')[-1], __uuid)
    mesh_data['vertices'] = vertices
    mesh_data['faces'] = faces
    return mesh_data


if __name__ == '__main__':
    print(uuid.uuid4().get_hex())


def get_select_meshs():
    meshs = cmds.ls(sl=1)
    meshs = get_meshs(meshs)
    return meshs


def get_meshs(objs):
    meshs = []
    for obj in objs:
        shape = cmds.listRelatives(obj, s=1, type='mesh')
        if shape:
            meshs.append(obj)
    return meshs
