# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       : sg_base
# Describe   : 说明描述
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2022/5/27__17:14
# -------------------------------------------------------
def select_entity_task(sg, entity_type, entity_id, task_fields=[]):
    """
    查询实体链接的任务的字段
    :param entity_type: 实体类型,比如'Asset','Shot'
    :param entity_id:实体id
    :param task_fields:任务字段
    :return:任务名对应的字段字典(资产/镜头下 任务名唯一)
    """

    fields = ['content'] + task_fields
    filters = [
        ['entity.' + entity_type + '.id', 'is', entity_id]
    ]
    return sg.find("Task", filters, fields)


def delete_entity(sg, entity_type, entity_id):
    '''
    删除实体,进入回收站
    :param sg: sg实体
    :param entity_type: 实体类型
    :param entity_id: 实体id
    :return: True or Fault(实体不存在)
    '''
    return sg.delete(entity_type, entity_id)


def revive_entity(sg, entity_type, entity_id):
    '''
    恢复先前已删除的实体
    :param sg:sg实体
    :param entity_type: 实体类型
    :param entity_id: 实体id
    :return:True表示恢复成功，否则为False
    '''
    return sg.revive(entity_type, entity_id)


def select_entity_id(sg, project_name, entity_type, entity_name):
    """
    通过Entity名获取EntityID
    :param sg: sg实体
    :param project_name:项目名
    :param entity_type: 实体类型（Asset|Shot|Sequence|Episode...）
    :param entity_name: 实体名
    :return: 获取到ID列表
    """
    fields = ['id']
    filters = [
        ['project.Project.name', 'is', project_name],
        ['code', 'is', entity_name]
    ]
    return sg.find(entity_type, filters, fields)


def select_entity_id2(sg, project_name, entity_type, key, value):
    """
    通过Entity名获取EntityID
    :param sg: sg实体
    :param project_name:项目名
    :param entity_type: 实体类型（Asset|Shot|Sequence|Episode...）
    :param key: 字段名
    :param value: 字段值
    :return: 获取到ID列表
    """
    fields = ['id']
    filters = [
        ['project.Project.name', 'is', project_name],
        [key, 'is', value]
    ]
    return sg.find(entity_type, filters, fields)


def select_entity(sg, entity_type, entity_id, fields=[]):
    """
    查询某实体下的某个字段的数据
    :param entity_type: 实体类型
    :param entity_id: 实体ID
    :param fields: 实体页所需要获得的字段值列表
    :return:对应字段的列表
    """
    filters = [
        ['id', 'is', entity_id]
    ]
    return sg.find_one(entity_type, filters, fields)


def update_entity(sg, entity_type, entity_id, data={}):
    """
    更新某实体类型下的某个字段的数据
    :param entity_type: Entity类型
    :param entity_id: entity id
    :param data: 该实体的字段 例如：{sg_chr_leval:'D'}
    :return: 有数据代表成功，否则失败
    """
    return sg.update(entity_type, entity_id, data)


def select_entity_version(sg, entity_type, entity_id, task_name='', version_fields=[]):
    """
    查询实体（某个任务）链接的version字段
    :param project_name: 项目名
    :param entity_type: 实体类型
    :param entity_id: 实体idf
    :param task_name: 任务名（可以为空）
    :param version_fields: 要获取的version字段
    :return: version字段列表，否则为None
    """
    if not task_name:
        filters = [
            ['entity.' + entity_type + '.id', 'is', entity_id]
        ]
        return sg.find("Version", filters, version_fields)
    else:
        tasks_infos = select_entity_task(sg, entity_type, entity_id)
        if task_name in [task_dict['content'] for task_dict in tasks_infos if tasks_infos]:
            filters = [
                ['entity.' + entity_type + '.id', 'is', entity_id],
                ['sg_task.Task.content', 'is', task_name]
            ]
            return sg.find("Version", filters, version_fields)
        else:
            return []


def select_entity_publish(sg, entity_type, entity_id, task_name='', publish_fields=[]):
    '''
    查询实体（某个任务）链接的publish字段
    :param sg: sg实体
    :param entity_type: 实体类型
    :param entity_id: 实体id
    :param task_name: 任务名
    :param publish_fields: 要获取的publish字段
    :return: publish字段列表，否则为None
    '''
    if not task_name:
        filters = [
            ['entity.' + entity_type + '.id', 'is', entity_id]
        ]
        return sg.find("PublishedFile", filters, publish_fields)
    else:
        tasks_infos = select_entity_task(sg, entity_type, entity_id)
        if task_name in [task_dict['content'] for task_dict in tasks_infos if tasks_infos]:
            filters = [
                ['entity.' + entity_type + '.id', 'is', entity_id],
                ['task.Task.content', 'is', task_name]
            ]
            return sg.find("PublishedFile", filters, publish_fields)
        else:
            return []




