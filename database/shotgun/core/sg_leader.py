# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       : sg_leader
# Describe   : step_leaders
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2022/8/1__15:17
# -------------------------------------------------------
import database.shotgun.core.sg_base as sg_base

LEADER_ENTITY = "CustomEntity09"
LEADER_FIELDS = ['sg_leader', 'sg_steps', 'sg_types', 'sg_entity_type_1']


def get_leaders_entity(sg):
    u"""
    获取leader表格基本信息
    Returns:

    """
    return sg.find(LEADER_ENTITY, filters=[], fields=[])


def select_leader_entity(sg, _id, _fields=['sg_types']):
    """
    查询资产信息
    :param sg: sg实体
    :param _id: ID
    :param _fields: 字段列表
    :return:
    """
    return sg_base.select_entity(sg, LEADER_ENTITY, _id, _fields)


def select_leader_ids(sg):
    u"""
    获取表格所有id信息
    Args:
        sg:

    Returns:

    """
    _idlist = get_leaders_entity(sg)
    _ids = []
    if _idlist:
        return [i['id'] for i in _idlist if (i and 'id' in i)]


def select_id_entity(sg, id, _fields=['sg_asset_type']):
    u"""
    从id 获得相应字段信息
    Args:
        sg:
        id: id
        _fields:

    Returns:

    """
    return sg_base.select_entity(sg, LEADER_ENTITY, id, fields=_fields)


def select_leaders_infos(sg):
    u"""
    获得leaders 表格信息
    Args:
        sg:

    Returns:

    """
    return sg.find(LEADER_ENTITY, filters=[], fields=LEADER_FIELDS)


def select_leaders_judiges(sg):
    u"""
    获得判断信息
    Args:
        sg:

    Returns:{id:{'step_name':'art'………………}

    """
    _info = select_leaders_infos(sg)
    _dict = {}
    if _info:
        return _package_infos(_info)


def _package_infos(_infos):
    u"""
    整理打包数据，便于调用
    Args:
        _infos:

    Returns:

    """
    _dict = {}
    if _infos:
        for i in range(len(_infos)):
            _id = _infos[i]['id']
            _dic = {}
            for j in range(len(LEADER_FIELDS)):
                if LEADER_FIELDS[j] in _infos[i]:
                    _inf = _infos[i][LEADER_FIELDS[j]]
                    if LEADER_FIELDS[j] == 'sg_entity_type_1':
                        _dic['entity_type'] = _infos[i][LEADER_FIELDS[j]]
                    elif LEADER_FIELDS[j] in ['sg_leader']:
                        _dic['leader_id'] = [k['id'] for k in _infos[i][LEADER_FIELDS[j]] if (k and 'id' in k)]
                    else:
                        _dic['{}_name'.format(LEADER_FIELDS[j])] = [k['name'].lower() for k in
                                                                    _infos[i][LEADER_FIELDS[j]] if
                                                                    (_infos[i][LEADER_FIELDS[j]] and k and 'name' in k)]
            if _dic:
                _dict[_id] = _dic
    return _dict

def get_step_leaders(sg,entity_type):
    u"""
    获取step的leaders
    Args:
        sg:
        entity_type: 类型(Asset,Shot)
        step: 环节('fight')
        asset_type: 资产类型(如'role')

    Returns:

    """
    filters = [
        ['sg_entity_type_1', 'is', entity_type]
    ]
    return sg.find_one(LEADER_ENTITY, filters, LEADER_FIELDS)



