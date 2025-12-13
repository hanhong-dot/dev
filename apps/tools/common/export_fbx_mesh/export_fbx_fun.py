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
import os
import json


def load_fbx_file(fbx_file):
    manager, scene = FbxCommon.InitializeSdkObjects()
    FbxCommon.LoadScene(manager, scene, fbx_file)
    return manager, scene


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


def get_mesh_node(model_node):
    # type: (FbxNode) -> FbxMesh
    if model_node.GetNodeAttribute() and model_node.GetNodeAttribute().GetAttributeType() == fbx.FbxNodeAttribute.eMesh:
        return model_node.GetMesh()
    return None


def clone_mesh(src_mesh, dst_scene):
    dst_mesh = fbx.FbxMesh.Create(dst_scene, src_mesh.GetName())
    # 复制顶点
    num_verts = src_mesh.GetControlPointsCount()
    dst_mesh.InitControlPoints(num_verts)
    for i in range(num_verts):
        dst_mesh.SetControlPointAt(src_mesh.GetControlPointAt(i), i)
    # 复制多边形
    for i in range(src_mesh.GetPolygonCount()):
        poly_size = src_mesh.GetPolygonSize(i)
        dst_mesh.BeginPolygon()
        for j in range(poly_size):
            idx = src_mesh.GetPolygonVertex(i, j)
            dst_mesh.AddPolygon(idx)
        dst_mesh.EndPolygon()
    # 复制UV
    for uv_index in range(src_mesh.GetElementUVCount()):
        src_uv = src_mesh.GetElementUV(uv_index)
        dst_uv = fbx.FbxLayerElementUV.Create(dst_mesh, src_uv.GetName())
        dst_uv.SetMappingMode(src_uv.GetMappingMode())
        dst_uv.SetReferenceMode(src_uv.GetReferenceMode())
        for i in range(src_uv.GetDirectArray().GetCount()):
            dst_uv.GetDirectArray().Add(src_uv.GetDirectArray().GetAt(i))
        if src_uv.GetReferenceMode() == fbx.FbxLayerElement.eIndexToDirect:
            for i in range(src_uv.GetIndexArray().GetCount()):
                dst_uv.GetIndexArray().Add(src_uv.GetIndexArray().GetAt(i))
        dst_mesh.GetLayer(0).SetUVs(dst_uv)
    return dst_mesh


def copy_material_and_texture(src_node, dst_node, dst_scene):
    for i in range(src_node.GetMaterialCount()):
        material = src_node.GetMaterial(i)
        # 拷贝材质

        new_material = material.Clone(dst_scene)
        dst_node.AddMaterial(new_material)
        # 拷贝贴图
        for prop in [new_material.FindProperty(fbx.FbxSurfaceMaterial.sDiffuse),
                     new_material.FindProperty(fbx.FbxSurfaceMaterial.sNormalMap),
                     new_material.FindProperty(fbx.FbxSurfaceMaterial.sBump)]:
            if prop.IsValid():
                layered_texture_count = prop.GetSrcObjectCount(fbx.FbxLayeredTexture.ClassId)
                for j in range(layered_texture_count):
                    layered_texture = prop.GetSrcObject(fbx.FbxLayeredTexture.ClassId, j)
                    prop.ConnectSrcObject(layered_texture)
                texture_count = prop.GetSrcObjectCount(fbx.FbxTexture.ClassId)
                for j in range(texture_count):
                    texture = prop.GetSrcObject(fbx.FbxTexture.ClassId, j)
                    prop.ConnectSrcObject(texture)


def copy_uv(src_mesh, dst_mesh):
    for uv_index in range(src_mesh.GetElementUVCount()):
        src_uv = src_mesh.GetElementUV(uv_index)
        dst_uv = fbx.FbxLayerElementUV.Create(dst_mesh, src_uv.GetName())
        dst_uv.SetMappingMode(src_uv.GetMappingMode())
        dst_uv.SetReferenceMode(src_uv.GetReferenceMode())
        for i in range(src_uv.GetDirectArray().GetCount()):
            dst_uv.GetDirectArray().Add(src_uv.GetDirectArray().GetAt(i))
        if src_uv.GetReferenceMode() == fbx.FbxLayerElement.eIndexToDirect:
            for i in range(src_uv.GetIndexArray().GetCount()):
                dst_uv.GetIndexArray().Add(src_uv.GetIndexArray().GetAt(i))
        dst_mesh.GetLayer(0).SetUVs(dst_uv)  # 只传dst_uv


def export_single_mesh(mesh, export_path):
    manager, new_scene = FbxCommon.InitializeSdkObjects()
    root = new_scene.GetRootNode()
    src_node = mesh.GetNode()
    new_node = fbx.FbxNode.Create(new_scene, src_node.GetName())
    mesh_node = get_mesh_node(src_node)
    if not mesh_node:
        return False, u'No mesh found in the source node.'

    new_mesh = clone_mesh(mesh_node, new_scene)
    new_node.SetNodeAttribute(new_mesh)
    root.AddChild(new_node)

    FbxCommon.SaveScene(manager, new_scene, export_path)
    return True, export_path


def export_meshes_from_fbx(fbx_file, export_dir):
    if not os.path.exists(export_dir):
        os.makedirs(export_dir)
    manager, scene = load_fbx_file(fbx_file)
    all_nodes = get_all_nodes(scene)
    fbx_base_name = os.path.splitext(os.path.basename(fbx_file))[0]
    meshs = []
    errors = []
    export_fbx_files = []
    for node in all_nodes:
        mesh_node = get_mesh_node(node)
        if mesh_node:
            meshs.append(mesh_node)
    for mesh in meshs:
        mesh_node = mesh.GetNode()
        mesh_name = mesh_node.GetName()
        mesh_name = mesh_name.replace('.', '_').replace(' ', '_')

        fbx_export_file = '{}/{}/{}.fbx'.format(export_dir, fbx_base_name, mesh_name)
        __dir = os.path.dirname(fbx_export_file)
        if not os.path.exists(__dir):
            os.makedirs(__dir)
        fbx_export_file = fbx_export_file.replace('\\', '/')
        ok, reslut = export_single_mesh(mesh, fbx_export_file)
        if not ok:
            errors.append(reslut)
            continue
        export_fbx_files.append(fbx_export_file)
    if errors:
        return False, u'{}导出失败,请检查错误信息:\n{}'.format(fbx_file, '\n'.join(errors))
    if not export_fbx_files:
        return False, u'没有导出任何fbx，请检查FBX文件中是否有mesh节点:{}'.format(fbx_file)
    return True, export_fbx_files


def export_meshes_from_fbx_files(fbx_files, export_dir):
    if not os.path.exists(export_dir):
        os.makedirs(export_dir)
    errors = []
    export_infos = []

    for fbx_file in fbx_files:
        fbx_file = fbx_file.replace('\\', '/')
        if not os.path.exists(fbx_file):
            continue
        ok, result = export_meshes_from_fbx(fbx_file, export_dir)
        if not ok:
            errors.append(result)
            continue
        if result and isinstance(result, list):
            export_infos.append([fbx_file, result])
    return export_infos, errors


def export_single_mesh_from_fbx_dir(fbx_dir, export_dir):
    if not os.path.exists(fbx_dir):
        return False, u'FBX directory does not exist: {}'.format(fbx_dir)
    if not os.path.exists(export_dir):
        os.makedirs(export_dir)
    fbx_files = get_fbx_files_from_dir(fbx_dir)
    if not fbx_files:
        return False, u'输入的文件夹路径中没有fbx文件,请检查: {}'.format(fbx_dir)
    export_infos, errors = export_meshes_from_fbx_files(fbx_files, export_dir)

    return True, (export_infos, errors)


def get_fbx_files_from_dir(dir_path, ext='.fbx'):
    if not os.path.exists(dir_path):
        return []
    fbx_files = []
    fbx_file_list = os.listdir(dir_path)
    for file_name in fbx_file_list:
        if file_name.endswith(ext):
            __fbx_file = os.path.join(dir_path, file_name).replace('\\', '/')
            if __fbx_file and os.path.exists(__fbx_file):
                fbx_files.append(__fbx_file)

    return fbx_files


def get_local_json_path():
    local_dir = get_localtemppath('/export_single_fbx_mesh/json')
    if not os.path.exists(local_dir):
        os.makedirs(local_dir)
    return '{}/path.json'.format(local_dir)


def save_path_info_to_json(path_info):
    json_path = get_local_json_path()
    write_json_file(path_info, json_path)


def get_path_info_from_json():
    json_path = get_local_json_path()
    path_info = read_json_file(json_path)
    if not path_info:
        path_info = {}
    return path_info


def read_json_file(file_path):
    if not os.path.exists(file_path):
        return None
    with open(file_path, 'r') as f:
        data = json.load(f)
    return data


def write_json_file(data, file_path):
    dir_path = os.path.dirname(file_path)
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def get_localtemppath(add_path):
    if os.path.exists('D:\\'):
        localInfoPath = 'D:/temp_info/' + add_path
    elif os.path.exists('E:\\'):
        localInfoPath = 'E:/temp_info/' + add_path
    elif os.path.exists('F:\\'):
        localInfoPath = 'F:/temp_info/' + add_path
    elif os.path.exists('C:\\'):
        localInfoPath = 'C:/temp_info/' + add_path
    else:
        raise Exception(u'本地C,D,E,F盘都没有')
    return localInfoPath


if __name__ == '__main__':
    fbx_file = r'E:\fbx_test\fx_trail_007.fbx'
    export_dir = r'E:\fbx_test\output'
    export_meshes_from_fbx(fbx_file, export_dir)

    # manager, scene = load_fbx_file(fbx_file)
    # all_nodes = get_all_nodes(scene)
    # meshs = []
    # for node in all_nodes:
    #     mesh_node = get_mesh_node(node)
    #     if mesh_node:
    #         meshs.append(mesh_node)
    # for mesh in meshs:
    #     mesh_node = mesh.GetNode()
    #     mesh_name = mesh_node.GetName()
    #
    #     fbx_export_file = '{}/{}.fbx'.format(dir, mesh_name)
    #     print('Exporting mesh: {} to {}'.format(mesh_name, fbx_export_file))
    #     export_single_mesh(mesh, fbx_export_file)
