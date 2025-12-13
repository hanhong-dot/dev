# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       : sg_shot
# Describe   : 说明描述
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2022/5/23__18:46
# -------------------------------------------------------
import database.shotgun.core.sg_base as sg_base


def create_shot(sg, project_data, shot_name, sequence_data, return_fields=None, **kwargs):
    '''
    创建镜头信息
    :param sg:sg实体
    :param project_data:项目实体
    :param shot_name:镜头号
    :param sequence_data: 场次实体
    :param return_fields:返回的其他字段值的可选列表
    :param kwargs:其他字段
    :return:字典 例如：{'code': 'seq001_sc050', 'sg_frame': 100.5, 'sg_sequence': {'type': 'Sequence', 'id': 361, 'name': 'seq001'}, 'project': {'type': 'Project', 'id': 89, 'name': 'XCM_Test'}, 'type': 'Shot', 'id': 35575}
    '''
    data = {'project': project_data,
            'code': shot_name,
            'sg_sequence': sequence_data,
            }

    data.update(kwargs)
    return sg.create("Shot", data, return_fields)


def select_shot_ID(sg, project_name, shot_name, sequence_name, episode_name=''):
    """
    获取镜头ID
    :param sg: sg实体
    :param project_name:项目名
    :param shot_name: 镜头名
    :param sequence_name: 场次名
    :param episode_name: 集数名
    :return: 获取到镜头ID的列表，否则为[] 例如：[{'type': 'Shot', 'id': 1227}] 注意：如果sequence和episode和shot有关联，则sequence和episode参数不能为空
    """
    if not sequence_name:
        raise Exception("Parameter error,'sequence_name' should not be none!")
    fields = ['id']
    if episode_name:
        filters = [
            ['project.Project.name', 'is', project_name],
            ['sg_sequence.Sequence.episode.Episode.code', 'is', episode_name],
            ['sg_sequence.Sequence.code', 'is', sequence_name],
            ['code', 'is', shot_name]
        ]
    else:
        filters = [
            ['project.Project.name', 'is', project_name],
            ['sg_sequence.Sequence.code', 'is', sequence_name],
            ['code', 'is', shot_name]
        ]

    return sg.find('Shot', filters, fields)


# return sg_base.get_entity_id(sg, project_name, "Shot", shot_name)


def select_shot_shot(sg, shot_id, shot_fields=[]):
    """
    查询镜头信息
    :param sg: sg实体
    :param shot_id: 镜头ID
    :param shot_fields: 镜头字段
    :return: 镜头字典 例如：{'sg_cut_duration': 10, 'type': 'Shot', 'id': 6330}
    """
    return sg_base.select_entity(sg, "Shot", shot_id, shot_fields)


def update_shot_shot(sg, shot_id, **kwargs):
    """
    更新镜头信息
    :param sg: sg实体
    :param shot_id: 镜头id
    :param kwargs: 镜头字段 例如：sg_cut_in = 101
    :return: True代表更新成功，False代表更新失败
    """
    result = sg_base.update_entity(sg, "Shot", shot_id, kwargs)
    if result:
        return True
    else:
        return False


def select_shot_sequence(sg, shot_id, sequence_name='', sequence_fields=[]):
    '''
    查询镜头链接的sequence的信息
    :param sg: sg实体
    :param shot_id: 镜头id
    :param sequence_name: 场次名
    :param sequence_fields:场次字段
    :return: 场次字典  例如：{'sg_status_list': 'ip', 'code': 'seq001', 'type': 'Sequence', 'id': 361}
    '''

    sequence_dict = sg_base.select_entity(sg, "Shot", shot_id, ['sg_sequence'])['sg_sequence']
    if sequence_dict:
        if sequence_name:
            if sequence_name != sequence_dict['name']:
                raise Exception("Parameter error,Sequence '{}' is not link of ShotID {}".format(sequence_name, shot_id))
        return sg_base.select_entity(sg, 'Sequence', sequence_dict['id'], ['code'] + sequence_fields)
    else:
        return None


def update_shot_sequence(sg, shot_id, sequence_name='', **kwargs):
    '''
    更新镜头链接的场次的信息
    :param sg: sg实体
    :param shot_id: 镜头id
    :param sequence_name: 场次名
    :param kwargs: 场次字段 例如：sg_status_list ='apr'
    :return: True 成功
    '''
    result = []
    sequence_dict = select_shot_sequence(sg, shot_id, sequence_name)
    sequence_id = sequence_dict['id'] if sequence_dict else None
    if sequence_id:
        update_data = sg_base.update_entity(sg, "Sequence", sequence_id, kwargs)
        if update_data:
            result.append(True)
        else:
            result.append(False)
    return False if False in result else True


def select_shot_episode(sg, shot_id, sequece_name='', episode_name='', episode_fields=[]):
    '''
    查询镜头链接的集数信息
    :param sg:sg实体
    :param shot_id: 镜头id
    :param episode_name: 集数名
    :param episode_fields: 集数字段
    :return:集数字典 例如：{'sg_status_list': 'rdy', 'code': 'ep006', 'type': 'Episode', 'id': 183}
    '''
    sequence_dict = select_shot_sequence(sg, shot_id, sequece_name)
    episode_dict = sg_base.select_entity(sg, "Sequence", sequence_dict['id'], ['episode'])['episode'] if sequence_dict \
        else None
    if episode_dict:
        if episode_name:
            if episode_name != episode_dict['name']:
                raise Exception("Parameter error,Episode '{}' is not link of ShotID {}".format(episode_name, shot_id))
        return sg_base.select_entity(sg, 'Episode', episode_dict['id'], ['code'] + episode_fields)
    else:
        return None


def update_shot_episode(sg, shot_id, sequence_name='', episode_name='', **kwargs):
    '''
    更新镜头链接的集数信息
    :param sg: sg实体
    :param shot_id: 镜头id
    :param sequence_name: 场次名
    :param episode_name: 集数名
    :param kwargs: 集数字段 例如：description = u'测试集数'
    :return: True 成功
    '''
    result = []
    episode_dict = select_shot_episode(sg, shot_id, sequence_name, episode_name)
    episode_id = episode_dict['id'] if episode_dict else None
    if episode_id:
        update_data = sg_base.update_entity(sg, "Episode", episode_id, kwargs)
        if update_data:
            result.append(True)
        else:
            result.append(False)
    return False if False in result else True


def select_shot_asset(sg, shot_id, asset_name='', asset_fields=[]):
    '''
    查询镜头链接下的资产信息
    :param sg: sg实体
    :param shot_id: 镜头id
    :param asset_name: 资产名
    :param asset_fields: 资产字段
    :return: 资产列表  例如：[{'asset.Asset.id': 2349, 'asset.Asset.sg_asset_type': 'Snt', 'type': 'AssetShotConnection', 'id': 13791, 'asset.Asset.code': 'NB002005fz'}]
    '''
    sign = False
    filters = [
        ['shot.Shot.id', 'is', shot_id]
    ]
    fields = ['asset.Asset.id', 'asset.Asset.code']
    if asset_fields:
        for obj in asset_fields:
            fields.append('asset.Asset.' + obj)
    asset_infos = sg.find("AssetShotConnection", filters, fields)
    if asset_name:
        if asset_infos:
            for obj in asset_infos:
                if asset_name == obj['asset.Asset.code']:
                    sign = True
                    return [obj]
        else:
            raise Exception("Parameter error,ShotID {} has not linked any assets".format(shot_id))
        if sign == False:
            raise Exception("Parameter error,Asset '{}' isn't the link of the shotID {}".format(
                asset_name, shot_id
            ))
    else:
        return asset_infos


def update_shot_asset(sg, shot_id, asset_name='', **kwargs):
    '''
    更新镜头链接资产信息
    :param sg: sg实体
    :param shot_id: 镜头id
    :param asset_name: 资产名
    :param kwargs: 资产字段  例如：description = 'bbb'
    :return: True成功
    '''
    result = []
    assets_infos = select_shot_asset(sg, shot_id, asset_name)
    asset_ids = [_info['asset.Asset.id'] for _info in assets_infos if assets_infos]
    if asset_ids:
        for asset_id in asset_ids:
            update_data = sg_base.update_entity(sg, "Asset", asset_id, kwargs)
            if update_data:
                result.append(True)
            else:
                result.append(False)
        return False if False in result else True
    else:
        return False


def select_shot_task(sg, shot_id, task_name='', task_fields=[]):
    '''
    查询镜头链接的任务信息
    :param sg: sg实体
    :param shot_id: 镜头id
    :param task_name: 任务名
    :param task_fields:任务字段
    :return: 任务列表 例如:[{'content': 'Ani_ani', 'sg_status_list': 'rev', 'type': 'Task', 'id': 56652}]
    '''
    warings = []
    result_task = []
    task_infos = sg_base.select_entity_task(sg, "Shot", shot_id)
    for i in range(0, len(task_infos)):
        for j in range(i + 1, len(task_infos)):
            if task_infos[i]['content'] == task_infos[j]['content']:
                warings.append(task_infos[i]['content'])
    if warings:
        raise Exception(
            "Parameter error,Task {} has repeated task of the shotID {}".format(warings, shot_id))
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
            raise Exception("Parameter error,Task '{}' isn't the link of the shotID {}".format(task_name,
                                                                                               shot_id))
    else:
        if task_name:
            raise Exception(
                "Parameter error,ShotID {} has not linked any task".format(shot_id))
        else:
            return task_infos


def select_shot_task2(sg, shot_id, task_fields=[]):
    '''
    查询镜头链接的任务信息
    :param sg: sg实体
    :param shot_id: 镜头id
    :param task_fields:任务字段
    :return: 任务列表 例如:[{'content': 'Ani_ani', 'sg_status_list': 'rev', 'type': 'Task', 'id': 56652}]
    '''
    return sg_base.select_entity_task(sg, "Shot", shot_id, task_fields)


def update_shot_task(sg, shot_id, task_name='', **kwargs):
    '''
    更新镜头链接的任务信息
    :param sg: sg实体
    :param shot_id: 镜头id
    :param task_name: 任务名称，如果为空，则更新所有链接的任务
    :param kwargs: 任务字段 sg_priority_1 = '1_Tier'
    :return: 成功返回True
    '''
    result = []
    tasks_infos = select_shot_task(sg, shot_id, task_name)
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


def select_shot_version(sg, shot_id, task_name='', version_fields=[]):
    """
    查询镜头（某个任务）链接的version信息
    :param sg: sg实体
    :param shot_id: 镜头id
    :param task_name: 任务名（可以为空）
    :param version_fields: version字段
    :return: version列表 例如：[{'type': 'Version', 'id': 138178, 'description': 'aaaaa'}]
    """
    tasks_infos = select_shot_task(sg, shot_id, task_name)
    return sg_base.select_entity_version(sg, "Shot", shot_id, task_name=task_name, version_fields=
    version_fields) if tasks_infos else []


def update_shot_version(sg, shot_id, task_name='', **kwargs):
    '''
    更新镜头链接的（某个任务的）version信息
    :param sg: sg实体
    :param shot_id: 镜头id
    :param task_name: 任务名
    :param kwargs: version字段
    :return: True
    '''
    result = []
    version_infos = select_shot_version(sg, shot_id, task_name)
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


def select_shot_publish(sg, shot_id, task_name='', publish_fields=[]):
    """
    查询镜头（某个任务）链接的publish信息
    :param shot_id: 镜头id
    :param task_name: 任务名（可以为空）
    :param publish_fields: publish字段
    :return: publish列表 例如：[{'code': '002', 'type': 'PublishedFile', 'id': 73466}]
    """
    tasks_infos = select_shot_task(sg, shot_id, task_name)
    return sg_base.select_entity_publish(sg, "Shot", shot_id, task_name=task_name, publish_fields=
    publish_fields) if tasks_infos else []


def update_shot_publish(sg, shot_id, task_name='', **kwargs):
    '''
    更新镜头链接的（某个任务的）publish信息
    :param sg: sg实体
    :param shot_id: 镜头id
    :param task_name: 任务名
    :param kwargs: publish字段
    :return: True
    '''
    result = []
    publish_infos = select_shot_publish(sg, shot_id, task_name)
    publish_ids = [_info['id'] for _info in publish_infos if publish_infos]
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

