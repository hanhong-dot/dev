# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       :
# Describe   :
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2024/10/29
# -------------------------------------------------------
import FbxCommon

from apps.tools.common.export_fbx_mesh import fbx_import

import fbx


class FbxImport(object):
    def __init__(self, file_path):
        self.__file_path = file_path
        ok, result = self.import_fbx()
        if not ok:
            raise ValueError(result)
        self.__scene, self.__manager = result
        self.__all_nodes = self.get_all_nodes()

    def import_fbx(self):
        return self.__import_fbx()

    def get_all_nodes(self):
        return self.__get_all_nodes()

    def __import_fbx(self):
        lSdkManager, lScene = FbxCommon.InitializeSdkObjects()
        lResult = FbxCommon.LoadScene(lSdkManager, lScene, self.__file_path)
        if not lResult:
            return False, u'导入失败'
        return True, (lScene, lSdkManager)

    def __get_root_node(self):
        return self.__scene.GetRootNode()

    def __get_all_nodes(self):
        return fbx_fun.get_all_nodes(self.__scene)

    def get_node_by_name(self, name):
        return self.__get_node_by_name(name)

    def __get_node_by_name(self, name):
        if not self.__all_nodes or not name:
            return None
        for node in self.__all_nodes:
            if node.GetName() == name:
                return node
        return None

    def get_node_world_transform(self, node):
        return self.__get_node_world_transform(node)

    def __get_node_world_transform(self, node):
        return fbx_fun.get_node_world_transform(node)

    def get_node_local_transform(self, node):
        return self.__get_node_local_transform(node)

    def __get_node_local_transform(self, node):
        return fbx_fun.get_node_local_transform(node)

    def rename_node(self, node, name):
        return self.__rename_node(node, name)

    def __rename_node(self, node, name):
        return fbx_fun.rename_node(node, name)

    def save_fbx(self, file_path):
        return self.__save_fbx(file_path)

    def __save_fbx(self, file_path):
        return FbxCommon.SaveScene(self.__manager, self.__scene, file_path)

    def __get_mesh_bs_nodes(self, mesh_node):
        return fbx_fun.get_blendshape_node(mesh_node)

    def get_bs_nodes_from_node(self, node):
        if isinstance(node, fbx.FbxMesh):
            return self.__get_mesh_bs_nodes(node)
        else:
            mesh_node = node.GetMesh()
            if mesh_node:
                return self.__get_mesh_bs_nodes(mesh_node)
