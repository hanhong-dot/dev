# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       : sg_sequence
# Describe   : 说明描述
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2022/5/23__18:51
# -------------------------------------------------------
import database.shotgun.core.sg_base as sg_base


def select_sequence_ID(sg, project_name, sequence_name, episode_name=''):
    u"""
    根据场次名获得相应ID号
    :param sg: sg实体
    :param project_name: 项目名
    :param sequence_name: 场次号
    :param episode_name: 集数
    :return:
    """
    if not sequence_name:
        raise Exception("Parameter error,'sequence_name' should not be none!")
    fields = ['id']
    if episode_name:
        filters = [
            ['project.Project.name', 'is', project_name],
            ['sg_sequence.Sequence.episode.Episode.code', 'is', episode_name],
            ['code', 'is', sequence_name],
        ]
    else:
        filters = [
            ['project.Project.name', 'is', project_name],
            ['code', 'is', sequence_name],
        ]

    return sg.find('Sequence', filters, fields)


def create_sequence(sg, project_data, sequence_name, episode_data={}, return_fields=None, **kwargs):
    '''
    创建场次信息
    :param sg:sg实体
    :param project_data:项目实体
    :param sequence_name: 场次名
    :param return_fields:返回的其他字段值的可选列表
    :param kwargs:其他字段
    :return:字典
    '''
    if episode_data:
        data = {'project': project_data,
                'code': sequence_name,
                'episode': episode_data
                }
    else:
        data = {'project': project_data,
                'code': sequence_name,
                }
    data.update(kwargs)
    return sg.create("Sequence", data, return_fields)


def select_sequence_episode(sg, sequence_id, episode_name='', episode_fields=[]):
    '''
    查询场次链接的集数的信息
    :param sg: sg实体
    :param sequence_id: 场次ID
    :param episode_name: 集数名
    :param episode_fields: 集数字段
    :return: 集数字典 {'code': 'ep006', 'type': 'Episode', 'id': 183}
    '''
    episode_dict = sg_base.select_entity(sg, "Sequence", sequence_id, ['episode'])
    if episode_dict:
        if episode_name:
            if episode_name != episode_dict['name']:
                raise Exception("Parameter error,Episode '{}' isn't the link of the sequenceID {}".format(
                    episode_name, sequence_id))
        return sg_base.select_entity(sg, 'Episode', episode_dict['id'], ['code'] + episode_fields)
    else:
        return None


def select_sequence_shot(sg, sequence_id, shot_name='', shot_fields=[]):
    '''
    查询场次链接的镜头相对应的信息
    :param sg: sg实体
    :param sequence_id: 场次ID
    :param shot_name: 镜头名
    :param shot_fields: 镜头字段
    :return: 镜头列表 例如：[{'type': 'Shot', 'id': 1228}]
    '''
    result_shot = []
    shots_infos = sg_base.select_entity(sg, "Sequence", sequence_id, ['shots'])["shots"]
    if shots_infos:
        if shot_name:
            shot_ids = [shot_dict['id'] for shot_dict in shots_infos if shot_name == shot_dict['name']]
        else:
            shot_ids = [shot_dict['id'] for shot_dict in shots_infos]
        if shot_ids:
            for shot_id in shot_ids:
                result_shot.append(sg_base.select_entity(sg, 'Shot', shot_id, ['name'] + shot_fields))
            return result_shot if result_shot else []
        else:
            raise Exception("Parameter error,Shot '{}' isn't the link of the sequenceID {}".format(shot_name,
                                                                                                   sequence_id))
    else:
        if shot_name:
            raise Exception("Parameter error,SequenceID {} has not linked any shots".format(sequence_id))
        else:
            return shots_infos


def select_sequence_shot2(sg, sequence_id, shot_fields=[]):
    '''
    查询场次链接的镜头相对应的信息
    :param sg: sg实体
    :param sequence_id: 场次ID
    :param shot_name: 镜头名
    :param shot_fields: 镜头字段
    :return: 镜头列表 例如：[{'type': 'Shot', 'id': 1228}]
    '''
    filters = [
        ['sg_sequence.Sequence.id', 'is', sequence_id]
    ]
    fields = shot_fields
    return sg.find("Shot", filters, fields)



