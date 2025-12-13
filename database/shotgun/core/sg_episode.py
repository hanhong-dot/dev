# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       : sg_episode
# Describe   : 说明描述
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2022/5/23__18:52
# -------------------------------------------------------
import database.shotgun.core.sg_base as sg_base


def get_episode_episodeID(sg, project_name, episode_name):
    """
    获取集数ID
    :param sg: sg实体
    :param project_name:项目名
    :param episode_name: 集数名
    :return: 获取集数ID列表 例如：[{'type': 'Episode', 'id': 407}]
    """

    return sg_base.select_entity_id(sg, project_name, "Episode", episode_name)


def select_episode_episode(sg, episode_id, episode_fields=[]):
    """
    查询集数信息
	:param sg: sg实体
    :param entity_id: id
    :param entity_fields: 实体页所需要获得的字段值列表
    :return:集数字典 例如：{'sg_status_list': 'ip', 'type': 'Episode', 'id': 407}
    """
    return sg_base.select_entity(sg, "Episode", episode_id, episode_fields)


