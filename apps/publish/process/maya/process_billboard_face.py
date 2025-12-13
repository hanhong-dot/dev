# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       : process_billboard_face
# Describe   :
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2024/8/15__19:30
# -------------------------------------------------------
import maya.cmds as cmds
from lib.maya.node.mesh import Mesh
import os


class ProcessBillboardFace(object):
    def __init__(self):
        super(ProcessBillboardFace, self).__init__()

    def process_billboard_face(self):
        billboard_meshs = self._get_billboard_mesh()

        if not billboard_meshs:
            return
        # __process_data=self.__process_copy_meshs(billboard_meshs)
        for mesh in billboard_meshs:
            self._copy_uv_set(mesh)

            billboard_face_data = self._get_pology_structur(mesh)
            if not billboard_face_data:
                continue
            self._triangulate_meshs([mesh])
            for k, v in billboard_face_data.items():
                self._process_billboard_face(k, v)
        # self.__process_process_data(__process_data)
        self.__set_meshs_vertex_display(billboard_meshs)
        self.__remove_history(billboard_meshs)

    def copy_uv_set(self, mesh):
        if not mesh:
            return
        return self._copy_uv_set(mesh)

    def set_meshs_vertex_display(self, meshs, size=10):
        if not meshs:
            return
        self.__set_meshs_vertex_display(meshs, size)

    def __set_meshs_vertex_display(self, meshs, size=10):
        if not meshs:
            return
        for mesh in meshs:
            mesh_shape = cmds.listRelatives(mesh, s=1, f=1, type='mesh')
            if not mesh_shape:
                continue
            self.__set_vertex_display(mesh_shape[0], size)

    def __set_vertex_display(self, mesh, size=10):
        cmds.setAttr('{}.displayVertices'.format(mesh), 1)
        cmds.setAttr('{}.vertexSize'.format(mesh), size)

    def __remove_history(self, meshs):
        cmds.bakePartialHistory(meshs, prePostDeformers=True)

    def _triangulate_meshs(self, meshs):
        if not meshs:
            return
        for mesh in meshs:
            self.__triangulate_mesh(mesh)

    def __triangulate_mesh(self, mesh):
        cmds.polyTriangulate(mesh, ch=1)

    def _copy_uv_set(self, mesh):
        cmds.select(mesh)
        uv_sets = cmds.polyUVSet(q=1, allUVSets=1)
        if len(uv_sets) > 1:
            cmds.polyUVSet(currentUVSet=True, uvSet=uv_sets[1])
            return uv_sets[1]
        else:
            current_uv_set = cmds.polyUVSet(q=1, currentUVSet=1)
            if not current_uv_set:
                return
            uv_set_new = cmds.polyUVSet(copy=True, nuv='map2', uvSet=current_uv_set[0])
            if not uv_set_new:
                return
            cmds.polyUVSet(currentUVSet=True, uvSet=uv_set_new[0])
            return uv_set_new[0]

    def __process_process_data(self, process_data):
        if not process_data:
            return
        for data in process_data:
            self.__process_parent(data['source'], data['target'])

    def __process_parent(self, obj, tart_obj):
        try:
            cmds.parent(tart_obj, obj)
        except:
            pass

    # def process_billboard_face(self, face, vertices, distance=0.00001):
    #     return self._process_billboard_face(face, vertices, distance)

    def process_billboard_face_by_data(self, face, vertices, distance=0.00001):
        if not face or not vertices or len(vertices) != 4:
            return
        self._process_billboard_face(face, vertices, distance)

    def _process_billboard_face(self, face, vertices, distance=0.00001):
        # if not face or not vertices or len(vertices) != 4:
        #     return
        ver_center_pos = [0, 0, 0]

        num = len(vertices)

        current_uv_set = cmds.polyUVSet(q=1, currentUVSet=1)

        for i in range(len(vertices)):
            pos = cmds.xform(vertices[i], q=1, t=1, ws=1)
            ver_center_pos[0] += pos[0]
            ver_center_pos[1] += pos[1]
            ver_center_pos[2] += pos[2]
        ver_center_pos[0] /= num
        ver_center_pos[1] /= num
        ver_center_pos[2] /= num
        w = self.__get_magnitue(ver_center_pos, cmds.xform(vertices[0], q=1, t=1, ws=1)) * 1.4142

        for i in range(len(vertices)):
            # self.__assign_vertex_color(vertices[i], [w, w, w, w])
            pos = cmds.xform(vertices[i], q=1, t=1, ws=1)
            pos_new = self.__get_position(ver_center_pos, pos, distance)

            self.__set_vertex_postion(vertices[i], pos_new)
            self.__set_vertex_uv(vertices[i], [w, w])

        # print(self.__get_magnitue(ver_center_pos,cmds.xform(vertices[0], q=1, t=1, ws=1)))

    def __get_position(self, pos01, pos02, distance):
        import numpy as np
        pos01 = np.array(pos01)
        pos02 = np.array(pos02)
        v = pos02 - pos01
        v_length = np.linalg.norm(v)
        if v_length == 0:
            return pos01
        v = v / v_length
        return pos01 + v * distance

    def __set_vertex_uv(self, ver, vue):
        _uv = cmds.polyListComponentConversion(ver, tuv=1)
        _uv_list = cmds.polyEditUV(_uv, query=True)
        cmds.select(_uv)
        cmds.polyEditUV(relative=False, uValue=vue[0], vValue=vue[1])

    def delete_copy_meshs(self):
        meshs = self.__get_copy_meshs()
        if not meshs:
            return
        for mesh in meshs:
            if cmds.objExists(mesh):
                cmds.delete(mesh)

    def __get_copy_meshs(self):
        meshs = []
        mesh_list = cmds.ls(type='mesh', l=1)
        for mesh in mesh_list:
            if cmds.listRelatives(mesh, p=1, type='transform', f=1):
                tr = cmds.listRelatives(mesh, p=1, type='transform', f=1)[0]
                tr_short = tr.split('|')[-1]
                if tr_short.startswith('display_') and tr_short.endswith('_Billboard'):
                    meshs.append(tr)
        return meshs

    def __process_copy_meshs(self, meshs):
        __process_data = []
        if not meshs:
            return
        for mesh in meshs:
            _data = self.__process_copy_obj(mesh)
            if _data:
                __process_data.append(_data)
        return __process_data

    def __process_copy_obj(self, obj, tart_name_pre='display_'):
        if not obj:
            return
        tarte_name = '{}_{}'.format(tart_name_pre, obj.split('|')[-1])
        if cmds.objExists(tarte_name):
            cmds.delete(tarte_name)
        tart_obj = cmds.duplicate(obj, n=tarte_name, rr=1)
        if not tart_obj or not cmds.objExists(tart_obj[0]):
            return
        # cmds.parent(tart_obj[0], obj)
        _attr = '{}.template'.format(tart_obj[0])
        cmds.setAttr(_attr, 1)
        return {'source': obj, 'target': tart_obj[0]}

    def __set_vertex_postion(self, ver, pos):
        cmds.xform(ver, t=pos, ws=1)

    def __assign_vertex_color(self, ver, color):

        cmds.polyColorPerVertex(ver, r=color[0], g=color[1], b=color[2], a=color[3])

    def __get_magnitue(self, v1, v2):
        return ((v1[0] - v2[0]) ** 2 + (v1[1] - v2[1]) ** 2 + (v1[2] - v2[2]) ** 2) ** 0.5

    def _get_billboard_face_data(self, mesh):
        __data = self._get_pology_structur(mesh)
        __face_data = {}
        if not __data:
            return
        __faces = __data.keys()

        __same_vers = []
        for i in range(len(__faces)):
            vers = __data[__faces[i]]
            same_vers = self._get_pology_same_vers(__faces[i])
            for k, v in __data.items():
                same_vers = []
                if v:
                    for ver in v:
                        if ver in vers:
                            same_vers.append(ver)
                if len(same_vers) >= 2:
                    vers.extend(v)
            vers = list(set(vers))
            result = False
            for ver in vers:
                if ver not in __same_vers:
                    __same_vers.append(ver)
                    result = True
            if result:
                __face_data[__faces[i]] = list(set(vers))

            # if vers!=4:
            #     print('mesh:',mesh)
            #     print('face:',__faces[i])
            #     print('vers:',vers)
            #     print('len:',len(vers))
        return __face_data

    def _get_pology_all_vers(self, mesh):
        if not mesh:
            return
        _ver = cmds.polyListComponentConversion(mesh, tv=1)
        ver_list = cmds.ls(_ver, fl=1)
        return ver_list

    def _get_pology_same_vers(self, mesh):
        _all_vers = self._get_pology_all_vers(mesh)
        if not _all_vers:
            return
        __same_vers = []
        for i in range(len(_all_vers)):
            ver = _all_vers[i]
            if ver not in __same_vers:
                __same_vers.append(ver)
                for j in range(i + 1, len(_all_vers)):
                    if ver == _all_vers[j]:
                        __same_vers.append(_all_vers[j])
        return __same_vers

    def _get_pology_structur(self, mesh):
        return Mesh(mesh).get_pology_structure()

    def _get_billboard_mesh(self):
        meshs = []
        mesh_list = cmds.ls(type='mesh', l=1)
        for mesh in mesh_list:
            if cmds.listRelatives(mesh, p=1, type='transform', f=1):
                tr = cmds.listRelatives(mesh, p=1, type='transform', f=1)[0]
                tr_short = tr.split('|')[-1]
                if tr_short.endswith('_Billboard'):
                    meshs.append(tr)
        return meshs


if __name__ == '__main__':
    handle = ProcessBillboardFace()
#     handle.process_billboard_face()
