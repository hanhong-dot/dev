# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       : sg_publish
# Describe   : 说明描述
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2022/5/24__11:54
# -------------------------------------------------------
import database.shotgun.core.sg_base as sg_base
import os
import traceback


def create_publish(sg, publish_file, project_data, link_type='local', url_path=None, task_data=None,
                   link_entity_data=None, sg_status_list=None,
                   user_data=None,
                   return_fields=None, publish_file_type=None, down_path=None, up_path=None, thumbnail=None,
                   description='', work_file='', ref_info='', file_data='',
                   **kwargs):
    '''
    创建publish file信息
    :param sg: sg实体
    :param publish_file: publish文件路径
    :param link_type: 本地链接:local,url格式:url,上传shotgun服务器：upload[这里需要用upload_publish_publish方法去实现]
    :param url_path: url路径地址，只有当link_type='url'时候再传该值才有效
    :param project_data: 项目数据
    :param task_data: 任务数据
    :param link_entity_data: 链接的publish数据
    :param user_data: 用户数据
    :param return_fields: 返回的其他字段值的可选列表
    :param kwargs: 其他字段的字典
    :return publish字典
    '''
    if link_type == 'local':
        _path_data = {
            'content_type': "string",
            'link_type': 'local',
            'local_path': publish_file,
            'local_path_linux': None,
            'local_path_mac': None,
            'local_path_windows': publish_file,
            'name': os.path.basename(publish_file),
        }
    if link_type == 'url':
        _path_data = {
            'content_type': "string",
            'link_type': 'url',
            'name': os.path.basename(publish_file),
            'url': url_path
        }
    if link_type == 'upload':
        _path_data = None

    data = {'project': project_data,
            'code': os.path.basename(publish_file),
            'task': task_data,
            'entity': link_entity_data,
            'created_by': user_data,
            'path': _path_data,
            'sg_status_list': sg_status_list
            }
    if publish_file_type:
        data['published_file_type'] = publish_file_type

    if thumbnail:
        data['image'] = thumbnail
    if description:
        data['description'] = description
    if work_file:
        _work_data = {
            'content_type': "string",
            'link_type': 'local',
            'local_path': work_file,
            'local_path_linux': None,
            'local_path_mac': None,
            'local_path_windows': work_file,
            'name': os.path.basename(work_file),
        }
        data['sg_workfile'] = _work_data
    if ref_info:
        data['sg_rferenceinfo'] = ref_info

    if file_data:
        data['sg_data'] = file_data

    data.update(kwargs)
    return sg.create("PublishedFile", data, return_fields)


def select_publish_publish(sg, publish_id, publish_fields=[]):
    """
    查询publish信息
    :param sg: sg实体
    :param publish_id: publish ID
    :param publish_fields: publish字段
    :return:publish字典 例如：{'type': 'PublishedFile', 'id': 74171, 'description': '\xe7\x89\x88\xe6\x9c\xac\xe6\xb5\x8b\xe8\xaf\x95'}
    """
    return sg_base.select_entity(sg, "PublishedFile", publish_id, publish_fields)


def update_publish_attachments(sg, publish_id, upload_path=''):
    u"""
    上传附件
    """
    sg.upload("PublishedFile", publish_id, upload_path, field_name="sg_attachments")


def update_publish_publish(sg, publish_id, upload_thumbnail='', upload_path='', **kwargs):
    '''
    更新publish信息
    :param sg: sg实体
    :param publish_id:publish_id
    :param upload_thumbnail: 缩略图路径
    :param upload_path: 文件上传到shotgun服务器
    :param kwargs: publish字段
    :return: true
    '''
    if upload_thumbnail and not kwargs and not upload_path:
        try:
            sg.upload_thumbnail('PublishedFile', publish_id, upload_thumbnail)
            return True
        except Exception as e:
            traceback.print_exc()
    elif kwargs and not upload_thumbnail and not upload_path:
        try:
            sg_base.update_entity(sg, 'PublishedFile', publish_id, kwargs)
            return True
        except Exception as e:
            traceback.print_exc()
    elif upload_path and not upload_thumbnail and not kwargs:
        try:
            sg.upload("PublishedFile", publish_id, upload_path, field_name="path")
            return True
        except Exception as e:
            traceback.print_exc()
    elif upload_thumbnail and upload_path and not kwargs:
        try:
            sg.upload_thumbnail('PublishedFile', publish_id, upload_thumbnail)
            sg.upload("PublishedFile", publish_id, upload_path, field_name="path")
            return True
        except Exception as e:
            traceback.print_exc()
    elif upload_thumbnail and kwargs and not upload_path:
        try:
            sg.upload_thumbnail('PublishedFile', publish_id, upload_thumbnail)
            sg_base.update_entity(sg, 'PublishedFile', publish_id, kwargs)
            return True
        except Exception as e:
            traceback.print_exc()
    elif upload_path and kwargs and not upload_thumbnail:
        try:
            sg.upload("PublishedFile", publish_id, upload_path, field_name="path")
            sg_base.update_entity(sg, 'PublishedFile', publish_id, kwargs)
            return True
        except Exception as e:
            traceback.print_exc()
    elif upload_thumbnail and upload_path and kwargs:
        try:
            sg.upload_thumbnail('PublishedFile', publish_id, upload_thumbnail)
            sg.upload("PublishedFile", publish_id, upload_path, field_name="path")
            sg_base.update_entity(sg, 'PublishedFile', publish_id, kwargs)
            return True
        except Exception as e:
            traceback.print_exc()


def select_publish_entity(sg, publish_id, entity_name='', entity_fields=[]):
    """
    查询publish链接的实体字段（资产/镜头/场次/集数）的信息
    :param sg: sg实体
    :param publish_id: publish ID
    :param entity_name: 实体名 资产名/镜头名/场次名/集数名
    :param entity_fields: 实体字段
    :return:链接实体的字典，否则为None 例如：{'code': 'ep001_seq001', 'type': 'Sequence', 'id': 57}
    """
    try:
        entity_dict = sg_base.select_entity(sg, "PublishedFile", publish_id, ['entity'])['entity']
    except:
        raise Exception("Parameter error,maybe the publishID {} is not exist".format(publish_id))
    if entity_dict:
        if entity_name:
            if entity_name != entity_dict['name']:
                raise Exception("Parameter error,Entity '{}' is not link of the publishID {}".format(entity_name,
                                                                                                     str(publish_id)))
        return sg_base.select_entity(sg, entity_dict['type'], entity_dict['id'], ['code'] + entity_fields)
    else:
        return None


def update_publish_entity(sg, publish_id, entity_name='', **kwargs):
    '''
    更新publish链接的实体的信息
    :param sg: sg实体
    :param publish_id: publish id
    :param entity_name: 实体名
    :param kwargs: 实体字段 例如：sg_cut_in = 500
    :return: True成功
    '''
    result = []
    entity_dict = select_publish_entity(sg, publish_id, entity_name)
    entity_id = entity_dict['id'] if entity_dict else None
    if entity_id:
        update_data = sg_base.update_entity(sg, entity_dict['type'], entity_id, kwargs)
        if update_data:
            result.append(True)
        else:
            result.append(False)
    return False if False in result else True


def select_publish_task(sg, publish_id, task_name='', task_fields=[]):
    """
    查询publish链接的task信息
    :param sg: sg实体
    :param publish_id: publish ID
    :param task_name: 任务名
    :param task_field: 任务字段
    :return: 任务字典，例如：{'sg_status_list': 'rev', 'type': 'Task', 'id': 20898}
    """
    task_dict = sg_base.select_entity(sg, "PublishedFile", publish_id, ['task'])['task']
    if task_dict:
        if task_name:
            if task_name != task_dict['name']:
                raise Exception("Parameter error,Task '{}' is not link of the publishID {}".format(task_name,
                                                                                                   str(publish_id)))
        return sg_base.select_entity(sg, task_dict['type'], task_dict['id'], ['code'] + task_fields)
    else:
        return None


def update_publish_task(sg, publish_id, task_name='', **kwargs):
    '''
    更新publish链接的任务的信息
    :param sg: sg实体
    :param publish_id: publish ID
    :param task_name: 任务名
    :param kwargs: task字段 例如：start_date = '2020-11-17'
    :return: True成功
    '''
    result = []
    entity_dict = select_publish_task(sg, publish_id, task_name)
    entity_id = entity_dict['id'] if entity_dict else None
    if entity_id:
        update_data = sg_base.update_entity(sg, entity_dict['type'], entity_id, kwargs)
        if update_data:
            result.append(True)
        else:
            result.append(False)
    return False if False in result else True


def get_publish_type(sg):
    '''
    获取publish类型
    :param sg: sg实体
    :return: publish类型列表
    '''
    _entity_type = 'PublishedFileType'
    _fields = ['code']
    _filters = []
    _datas = sg.find(_entity_type, filters=_filters, fields=_fields)
    return _datas
