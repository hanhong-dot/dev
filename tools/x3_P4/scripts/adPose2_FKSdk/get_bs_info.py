# -*- coding: UTF-8 -*-
import pymel.core as pm


def get_mesh_full_path(mesh):
    names = mesh.fullPath().split("|")
    if names[0] == u"":
        names.pop(0)
    return "/".join(names)


def get_selected_bsMeshes():
    '''
    筛选所选中带bs的模型
    :return: transform list   模型列表
    '''
    mod_list = []
    select_list = pm.selected(type='transform')
    for sel in pm.selected(type='transform'):
        select_list.extend(sel.getChildren(ad=1, type='transform'))
    for select_mod in select_list:
        if select_mod.getShape():
            if select_mod.getShape().type() == 'mesh':
                if select_mod.listHistory(type="skinCluster"):
                    if select_mod.listHistory(type='blendShape'):
                        mod_list.append(select_mod)
    return list(set(mod_list))


def get_bsMeshs_list(targets, ifFullPath):
    '''
    从get_selected_bsMeshes()中，通过targets筛选模型，获取mesh列表和对应的bs列表（排除Group组下的）
    :param targets: str list   bs目标体
    :param ifFullPath: bool   是否要求完整路径（NPC需要，主角不需要）
    :return: (str list,节点list)   最终的模型路径列表和bs节点列表
    '''
    bsMeshs_path_list = [get_mesh_full_path(mesh) for mesh in get_selected_bsMeshes()]
    bs_nodes = [mesh.getShape().listHistory(type='blendShape')[0] for mesh in get_selected_bsMeshes()]

    real_bs_nodes = []
    real_bsMeshs_path_list = []
    for i, mesh_path in enumerate(bsMeshs_path_list):
        if 'Group' not in mesh_path and 'GRP' not in mesh_path:
            for target in targets:
                if bs_nodes[i].hasAttr(target):
                    real_bs_nodes.append(bs_nodes[i])
                    if not ifFullPath:
                        real_bsMeshs_path_list.append(mesh_path.split('/')[-1])
                    else:
                        real_bsMeshs_path_list.append('/'.join(mesh_path.split('/')[1:]))
                    break
    return real_bsMeshs_path_list, real_bs_nodes


def get_real_weight_list(bs_node):
    '''
    （空目标体会被FBX会自动优化掉，ID会有误，故已弃用）
    为与FBX中的targetID一致，bs的weight需要重新排序
    :param bs_node: bs节点
    :return: 重新排序的bs权重列表
    '''
    weight_origin_connected_list = [weight for weight in bs_node.listAliases() if weight[1].isConnected()]
    id_list = [weight[1].logicalIndex() for weight in weight_origin_connected_list]
    weight_name_list = [weight[0] for weight in weight_origin_connected_list]
    weight_list = zip(id_list, weight_name_list)
    weight_list.sort()
    return weight_list


def get_targetID(target, bs_node):
    '''
    （空目标体会被FBX会自动优化掉，ID会有误，故已弃用）
    获取目标体ID
    :param target: str   bs目标体
    :param bs_node: bs节点
    :return: 目标体ID
    '''
    if target != 'bindPose':
        if bs_node.hasAttr(target):
            weight_list = get_real_weight_list(bs_node)
            for i, weight in enumerate(weight_list):
                if target == weight[1]:
                    targetID = i
                    return targetID


def search_bsinfo(target, bs_nodes):
    '''
    收集bs信息
    :param target: str   bs目标体
    :param bs_nodes: 节点list   bs节点的列表
    :return: dict list   bs信息的字典列表
    '''
    if target == 'bindPose':
        bsinfo = target
    else:
        bsinfo = []
        for bs_node in bs_nodes:
            if bs_node.hasAttr(target) and target in bs_node.weight.elements():
                meshID = bs_nodes.index(bs_node)
                # targetID = get_targetID(target, bs_node)
                targetInfo = bs_node.name() + '.' + target
                bsinfo.append(dict(meshID=meshID, target=targetInfo))
        bsinfo.sort()
    return bsinfo