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
import fbx

def load_fbx_file(fbx_file):
    manager, scene = FbxCommon.InitializeSdkObjects()
    FbxCommon.LoadScene(manager, scene, fbx_file)


def get_child(parent_node):
    child_count = parent_node.GetChildCount()
    tree = {}
    for i in range(child_count):
        child_node = parent_node.GetChild(i)
        tree[child_node.GetName()] = get_child(child_node)
    return tree


def get_root_node(scene):
    return scene.GetRootNode()


def get_tree(scene):
    root_node = get_root_node(scene)
    return get_child(root_node)


def get_tree_from_fbx_file(fbx_file):
    manager, scene = FbxCommon.InitializeSdkObjects()
    FbxCommon.LoadScene(manager, scene, fbx_file)
    return get_tree(scene)


def get_all_nodes(scene):
    root_node = scene.GetRootNode()
    nodes = []

    def get_all_nodes(node):
        nodes.append(node)
        for i in range(node.GetChildCount()):
            get_all_nodes(node.GetChild(i))

    get_all_nodes(root_node)
    return nodes


def get_all_nodes_from_fbx_file(fbx_file):
    manager, scene = FbxCommon.InitializeSdkObjects()
    FbxCommon.LoadScene(manager, scene, fbx_file)
    return get_all_nodes(scene)


def get_node_local_transform(node):

    transform = node.EvaluateLocalTransform()
    translation = transform.GetT()
    rotation = transform.GetQ()
    scale = transform.GetS()
    return translation, rotation, scale

def get_node_world_transform(node):
    transform = node.EvaluateGlobalTransform()
    translation = transform.GetT()
    rotation = transform.GetQ()
    scale = transform.GetS()
    return translation, rotation, scale


def get_node_by_node_name(node_name):
    # type: (str) -> FbxNode
    manager, scene = FbxCommon.InitializeSdkObjects()
    all_nodes = get_all_nodes(scene)
    for node in all_nodes:
        if node.GetName() == node_name:
            return node
    return None

def rename_node(node, new_name):
    node.SetName(new_name)
    return node


def save_fbx(scene, fbx_file):
    manager, exporter = FbxCommon.InitializeSdkObjects()
    FbxCommon.SaveScene(manager, scene, fbx_file)


def get_blendshape_node(model_node):

    blendshape_nodes = []
    for i in range(model_node.GetDeformerCount()):
        deformer = model_node.GetDeformer(i)
        if deformer.GetDeformerType() == FbxCommon.FbxDeformer.eBlendShape:
            blendshape_nodes.append(deformer)
    return blendshape_nodes
