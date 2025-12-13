# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       : sg_asset
# Describe   : 说明描述
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2022/5/27__17:13
# -------------------------------------------------------
import database.shotgun.core.sg_base as sg_base

def select_asset_entity(sg, asset_id, asset_fields=['sg_asset_type']):
    """
    查询资产信息
    :param sg: sg实体
    :param asset_id: 资产ID
    :param asset_fields: asset字段列表
    :return:资产字典 例如：{'sg_asset_type': 'Chr', 'type': 'Asset', 'id': 1972}
    """
    return sg_base.select_entity(sg, "Asset", asset_id, asset_fields)


def select_asset_entity_by_name(sg, project_name, asset_name, fields=['sg_asset_type']):
    """
    查询资产信息
    :param sg: sg实体
    :param project_name: 项目名
    :param asset_name: 资产名
    :param asset_fields: asset字段列表
    :return:资产字典 例如：{'sg_asset_type': 'Chr', 'type': 'Asset', 'id': 1972}
    """
    filters = [
        ['project.Project.name', 'is', project_name],
        ['code', 'is', asset_name]
    ]
    return sg.find_one('Asset', filters, fields)


def create_asset(sg, project_data, asset_name, asset_type, return_fields=None, **kwargs):
    '''
    创建资产信息
    :param sg:sg实例
    :param project_data:项目entity 字典
    :param asset_name:资产名称
    :param asset_type:资产类型
    :param return_fields: 返回的其他字段值的可选列表
    :param kwargs:其他字段
    :return:字典
    '''
    data = {'project': project_data,
            'code': asset_name,
            'sg_asset_type': asset_type,
            }

    data.update(kwargs)
    return sg.create("Asset", data, return_fields)


def select_asset_assetID(sg, project_name, asset_name):
    """
    获取资产ID
    :param sg: sg实体
    :param project_name:项目名
    :param asset_name: 资产名
    :return: 获取资产ID的列表，否则为[] 如：[{'type': 'Asset', 'id': 1972}]
    """
    return sg_base.select_entity_id(sg, project_name, "Asset", asset_name)


def update_asset_asset(sg, asset_id, **kwargs):
    """
    更新资产信息
    :param sg: sg实体
    :param asset_id: 资产id
    :param kwargs: 资产字段  例如: sg_chr_leval = 'D'
    :return: True代表更新成功，False代表更新失败
    """
    result = sg_base.update_entity(sg, "Asset", asset_id, kwargs)
    if result:
        return True
    else:
        return False


def select_asset_shot(sg, asset_id, shot_name='', shot_fields=[]):
    """
    查询资产链接的镜头的信息
    :param sg: sg实体
    :param asset_id:资产id
    :param shot_name:镜头名
    :param shot_fields:镜头字段
    :return:镜头列表 例如：[{'id': 61381, 'shot.Shot.sg_cut_in': 789, 'type': 'AssetShotConnection', 'shot.Shot.code': 'seq000_sc001', 'shot.Shot.id': 10361}]
    """
    sign = False
    filters = [
        ['asset.Asset.id', 'is', asset_id]
    ]
    fields = ['shot.Shot.id', 'shot.Shot.code']
    if shot_fields:
        for obj in shot_fields:
            fields.append('shot.Shot.' + obj)
    shot_infos = sg.find("AssetShotConnection", filters, fields)
    if shot_name:
        if shot_infos:
            for obj in shot_infos:
                if shot_name == obj['shot.Shot.code']:
                    sign = True
                    return [obj]
        else:
            raise Exception("Parameter error,AssetID {} has not linked any shots".format(asset_id))

        if sign == False:
            raise Exception("Parameter error,Shot '{}' isn't the link of the assetID {}".format(
                shot_name, asset_id
            ))

    else:
        return shot_infos


def update_asset_shot(sg, asset_id, shot_name='', **kwargs):
    """
    更新资产所链接镜头的信息
    :param sg: sg实体
    :param asset_id:资产id
    :param shot_name:镜头名称，如果为空，则更新所有链接的镜头
    :param kwargs:镜头字段 例如：sg_cut_in = 105
    :return:Ture成功，False失败
    """
    result = []
    shots_infos = select_asset_shot(sg, asset_id, shot_name)
    shot_ids = [_info['shot.Shot.id'] for _info in shots_infos if shots_infos]
    if shot_ids:
        for shot_id in shot_ids:
            update_data = sg_base.update_entity(sg, "Shot", shot_id, kwargs)
            if update_data:
                result.append(True)
            else:
                result.append(False)
        return False if False in result else True
    else:
        return False


def select_asset_sequence(sg, asset_id, sequence_name='', sequence_fields=[]):
    '''
    查询asset链接的场次信息
    :param sg: sg实体
    :param asset_id: 资产id
    :param sequence_name: 场次名
    :param sequence_fields: 场次字段
    :return: 场次列表 如：[{'sequence.Sequence.code': 'seq000', 'type': 'AssetSequenceConnection', 'sequence.Sequence.id': 288, 'sequence.Sequence.description': 'bbbb', 'id': 4556}]
    '''
    sign = False
    filters = [
        ['asset.Asset.id', 'is', asset_id]
    ]
    fields = ['sequence.Sequence.id', 'sequence.Sequence.code']
    if sequence_fields:
        for obj in sequence_fields:
            fields.append('sequence.Sequence.' + obj)
    sequence_infos = sg.find("AssetSequenceConnection", filters, fields)
    if sequence_name:
        if sequence_infos:
            for obj in sequence_infos:
                if sequence_name == obj['sequence.Sequence.code']:
                    sign = True
                    return [obj]
        else:
            raise Exception("Parameter error,AssetID {} has not linked any sequence".format(asset_id))

        if sign == False:
            raise Exception("Parameter error,Sequence '{}' isn't the link of the assetID {}".format(
                sequence_name, asset_id
            ))

    else:
        return sequence_infos


def update_asset_sequence(sg, asset_id, sequence_name='', **kwargs):
    """
    更新资产所链接场次的信息
    :param sg: sg实体
    :param asset_id:资产id
    :param sequence_name:场次名称，如果为空，则更新所有链接的场次
    :param kwargs:场次字段
    :return:True成功，False失败
    """
    result = []
    sequence_infos = select_asset_sequence(sg, asset_id, sequence_name)
    sequence_ids = [_info['sequence.Sequence.id'] for _info in sequence_infos if sequence_infos]
    if sequence_ids:
        for sequence_id in sequence_ids:
            update_data = sg_base.update_entity(sg, "Sequence", sequence_id, kwargs)
            if update_data:
                result.append(True)
            else:
                result.append(False)
        return False if False in result else True
    else:
        return False


def select_asset_episode(sg, asset_id, episode_name='', episode_fields=[]):
    '''
    查询asset链接的集数信息
    :param sg: sg实体
    :param asset_id: 资产id
    :param episode_name: 集数名
    :param episode_fields: 集数字段
    :return: 集数列表 如：[{'sequence.Sequence.code': 'seq000', 'type': 'AssetSequenceConnection', 'sequence.Sequence.id':
    288, 'sequence.Sequence.description': 'bbbb', 'id': 4556}]
    '''
    sign = False
    filters = [
        ['asset.Asset.id', 'is', asset_id]
    ]
    fields = ['episode.Episode.id', 'episode.Episode.code']
    if episode_fields:
        for obj in episode_fields:
            fields.append('episode.Episode.' + obj)
    episode_infos = sg.find("AssetEpisodeConnection", filters, fields)
    if episode_name:
        if episode_infos:
            for obj in episode_infos:
                if episode_name == obj['episode.Episode.code']:
                    sign = True
                    return [obj]
        else:
            raise Exception("Parameter error,AssetID {} has not linked any episodes".format(asset_id))

        if sign == False:
            raise Exception("Parameter error,Episode '{}' isn't the link of the assetID {}".format(
                episode_name, asset_id
            ))

    else:
        return episode_infos



def asset_Unregister_folders(asset_name):
    u"""
    更新资产的注册路径
    :param sg:
    :param asset_name:
    :return:
    """
    import os
    _path=r'Z:\dev\database\shotgun\toolkit\x3'
    cmd='{}\\tank  Asset {} unregister_folders '.format(_path,asset_name)
    print(cmd)
    return os.system(cmd)



def update_asset_episode(sg, asset_id, episode_name='', **kwargs):
    """
    更新资产所链接集数信息
    :param sg: sg实体
    :param asset_id:资产id
    :param episode_name:集数名称，如果为空，则更新所有链接的集数
    :param kwargs:集数字段
    :return:True成功，False失败
    """
    result = []
    episode_infos = select_asset_episode(sg, asset_id, episode_name)
    episode_ids = [_info['episode.Episode.id'] for _info in episode_infos if episode_infos]
    if episode_ids:
        for episode_id in episode_ids:
            update_data = sg_base.update_entity(sg, "Episode", episode_id, kwargs)
            if update_data:
                result.append(True)
            else:
                result.append(False)
        return False if False in result else True
    else:
        return False


def select_asset_task(sg, asset_id, task_name='', task_fields=[]):
    """
    查询资产链接任务的信息
    :param sg: sg实体
    :param asset_id:资产id
    :param task_fields:任务字段
    :return:任务列表 例如:[{'content': 'Srf_hig',
                          'id': 10724,
                          'step': {'id': 174, 'name': 'Srf', 'type': 'Step'},
                          'type': 'Task'}]
    """
    warings = []
    result_task = []
    task_infos = sg_base.select_entity_task(sg, "Asset", asset_id)
    for i in range(0, len(task_infos)):
        for j in range(i + 1, len(task_infos)):
            if task_infos[i]['content'] == task_infos[j]['content']:
                warings.append(task_infos[i]['content'])
    if warings:
        raise Exception("Parameter error,Task {} has repeated task of the assetID {}".format(warings, asset_id))

    if task_infos:
        if task_name:
            task_ids = [tasks_dict['id'] for tasks_dict in task_infos if task_name == tasks_dict['content']]
        else:
            task_ids = [tasks_dict['id'] for tasks_dict in task_infos]
        if task_ids:
            for task_id in task_ids:
                result_task.append(sg_base.select_entity(sg, 'Task', task_id, ['content'] + task_fields))
            return result_task
        else:
            raise Exception("Parameter error,Task '{}' isn't the link of the assetID {}".format(task_name, asset_id))
    else:
        if task_name:
            raise Exception("Parameter error,AssetID {} has not linked any task".format(asset_id))
        else:
            return task_infos


def select_asset_task2(sg, asset_id, task_fields=[]):
    """
    查询资产链接任务的信息
    :param sg: sg实体
    :param asset_id:资产id
    :param task_fields:任务字段
    :return:任务列表
    """
    return sg_base.select_entity_task(sg, "Asset", asset_id, task_fields)


def update_asset_task(sg, asset_id, task_name='', **kwargs):
    '''
    更新资产链接的任务信息
    :param sg: sg实体
    :param asset_id: 资产id
    :param task_name: 任务名称，如果为空，则更新所有链接的任务
    :param kwargs: 任务字段 sg_priority_1 = '1_Tier'
    :return:成功返回True
    '''
    result = []
    tasks_infos = select_asset_task(sg, asset_id, task_name)
    task_ids = [_info['id'] for _info in tasks_infos]
    if task_ids:
        for task_id in task_ids:
            update_data = sg_base.update_entity(sg, "Task", task_id, kwargs)
            if update_data:
                result.append(True)
            else:
                result.append(False)
        return False if False in result else True
    else:
        return False


def select_asset_version(sg, asset_id, task_name='', version_fields=[]):
    """
    查询资产（某个任务）链接的version信息
    :param sg: sg实体
    :param asset_id: 资产id
    :param task_name: 任务名（可以为空）
    :param version_fields: version字段 ['description']
    :return: version列表 例如：[{'type': 'Version', 'id': 8104}, {'type': 'Version', 'id': 8106}, {'type': 'Version',
    'id': 8205}]
    """

    tasks_infos = select_asset_task(sg, asset_id, task_name)
    return sg_base.select_entity_version(sg, "Asset", asset_id, task_name=task_name, version_fields=
    version_fields) if tasks_infos else []


def update_asset_version(sg, asset_id, task_name='', **kwargs):
    '''
    更新资产链接的（某个任务的）所有version信息
    :param sg: sg实体
    :param asset_id: 资产id
    :param task_name: 任务名
     :param kwargs: version字段 例如：description = u'测试一下'
    :return: True
    '''
    result = []
    version_infos = select_asset_version(sg, asset_id, task_name)
    version_ids = [version_dict['id'] for version_dict in version_infos if version_infos]
    if version_ids:
        for version_id in version_ids:
            update_data = sg_base.update_entity(sg, 'Version', version_id, kwargs)
            if update_data:
                result.append(True)
            else:
                result.append(False)
        return False if False in result else True
    else:
        return False


def select_asset_publish(sg, asset_id, task_name='', publish_fields=[]):
    """
    查询资产（某个任务）链接的publish信息
    :param asset_id: 资产id
    :param task_name: 任务名（可以为空）
    :param publish_fields: publish字段
    :return: publish列表，否则为None  例如：[{'sg_src_path': None, 'type': 'PublishedFile', 'id': 73886}, {'sg_src_path': None, 'type': 'PublishedFile', 'id': 73887}]
    """
    tasks_infos = select_asset_task(sg, asset_id, task_name)
    return sg_base.select_entity_publish(sg, "Asset", asset_id, task_name=task_name, publish_fields=
    publish_fields) if tasks_infos else []


def update_asset_publish(sg, asset_id, task_name='', **kwargs):
    '''
    更新资产链接的（某个任务的）publish信息
    :param sg: sg实体
    :param asset_id: 资产id
    :param task_name: 任务名
    :param kwargs: publish字段
    :return: True
    '''
    result = []
    publish_infos = select_asset_publish(sg, asset_id, task_name)
    publish_ids = [publish_dict['id'] for publish_dict in publish_infos if publish_infos]
    if publish_ids:
        for publish_id in publish_ids:
            update_data = sg_base.update_entity(sg, 'PublishedFile', publish_id, kwargs)
            if update_data:
                result.append(True)
            else:
                result.append(False)
        return False if False in result else True
    else:
        return False



