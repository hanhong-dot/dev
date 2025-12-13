# -*- coding: utf-8 -*-
# author: linhuan
# file: fbx_process.py
# time: 2025/10/21 19:11
# description:
import FbxCommon
import fbx


def get_fbx_data(fbx_file, rig_name):
    manager, scene = FbxCommon.InitializeSdkObjects()
    loaded = FbxCommon.LoadScene(manager, scene, fbx_file)
    if not loaded:
        manager.Destroy()
        return False, "Failed to load FBX scene: {}".format(fbx_file)
    rig_node = None
    model_list = []
    all_nodes = get_all_nodes(scene)
    if not all_nodes:
        return False, 'No nodes found in the FBX scene:{}.'.format(fbx_file)
    for node in all_nodes:
        node_name = node.GetName()
        if ':' in node_name:
            node_name = node_name.split(':')[-1]
        if node_name.lower() == rig_name.lower():
            rig_node = node
    if not rig_node:
        return False, 'Rig name:{} not found in the FBX scene:{}'.format(rig_name, fbx_file)
    mod_child_nodes = get_mod_child_nodes(rig_node)
    rig_node_name = rig_node.GetName()
    scene.Destroy()
    manager.Destroy()

    return True, (rig_node_name, mod_child_nodes)


def get_mod_child_nodes(node):
    child_count = node.GetChildCount()
    child_nodes = []
    for i in range(child_count):
        child_node = node.GetChild(i)
        child_node_name = child_node.GetName()
        if ':' in child_node_name:
            child_node_name = child_node_name.split(':')[-1]
        if child_node_name != 'Roots' and child_node_name not in child_nodes:
            child_nodes.append(child_node_name)
    return child_nodes


def get_child(parent_node):
    child_count = parent_node.GetChildCount()
    tree = {}
    for i in range(child_count):
        child_node = parent_node.GetChild(i)
        tree[child_node.GetName()] = get_child(child_node)
    return tree


def get_all_nodes(scene):
    root_node = scene.GetRootNode()
    nodes = []

    def get_all_nodes(node):
        nodes.append(node)
        for i in range(node.GetChildCount()):
            get_all_nodes(node.GetChild(i))

    get_all_nodes(root_node)
    return nodes


def get_root_node(scene):
    return scene.GetRootNode()


if __name__ == '__main__':
    fbx_file = r"M:\projects\x3\publish\assets\role\FY001C\rbf\maya\data\fbx\FY001C_rm_MB.fbx"
    rig_name = 'FY_Rig'
    print(get_fbx_data(fbx_file, rig_name))
