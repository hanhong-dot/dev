# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       : sg_version
# Describe   : 说明描述
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2022/5/23__18:45
# -------------------------------------------------------
import tempfile
import urllib
import os
import traceback
import database.shotgun.core.sg_base as sg_base


def create_version(sg, version_file, description='', project_data=None, link_entity_date=None,
                   task_data=None, user_data=None,
                   sg_status_list='rev'):
    '''
    创建版本信息
    :param sg:sg实体
    :param version_file:版本文件
    :param project_data: 项目数据
    :param link_type: 本地链接:local,url格式:url,上传shotgun服务器：upload[这里需要用upload_version_version方法去实现]
    :param url_path: url路径地址，只有当link_type='url'时候再传该值才有效
    :param task_data: 任务数据
    :param link_entity_data: 资产或者镜头（场次，集数）实体
    :param user_data: 用户实体
    :param return_fields: 返回的其他字段值的可选列表
    :param kwargs: 其他字段的字典
    :return:创建version实体的字典
    '''

    data = {'project': project_data,
            'code': os.path.basename(version_file),
            'description': description,
            'sg_path_to_frames': version_file,
            'sg_status_list': sg_status_list,
            'entity': link_entity_date,
            'sg_task': task_data,
            'user': user_data,
            }
    return sg.create("Version", data)


def update_version_version(sg, version_id, upload_thumbnail='', upload_movie='',field_name="sg_uploaded_movie", **kwargs):
    '''
    更新版本信息
    :param sg: sg实体
    :param version_id:version id
    :param upload_thumbnail: 缩略图路径
    :param upload_movie: 视频或者图片文件，视频/图片会在shotgun服务器进行处理压缩，并自动生成缩略图，因此如果传入改值时候没必要手动上传缩略图
    :param kwargs: version字段
    :return:True
    '''
    if upload_thumbnail and not kwargs and not upload_movie:
        try:
            sg.upload_thumbnail('Version', version_id, upload_thumbnail)
            return True
        except Exception as e:
            traceback.print_exc(e)

    elif kwargs and not upload_thumbnail and not upload_movie:
        try:
            sg_base.update_entity(sg, 'Version', version_id, kwargs)
            return True
        except Exception as e:
            traceback.print_exc(e)
    elif upload_movie and not upload_thumbnail and not kwargs:
        try:

            sg.upload("Version", version_id, upload_movie, field_name=field_name)
            return True
        except Exception as e:
            traceback.print_exc(e)
    elif upload_thumbnail and upload_movie and not kwargs:
        try:
            sg.upload("Version", version_id, upload_movie, field_name=field_name)
            return True
        except Exception as e:
            traceback.print_exc(e)
    elif upload_thumbnail and kwargs and not upload_movie:
        try:
            sg.upload_thumbnail('Version', version_id, upload_thumbnail)
            sg_base.update_entity(sg, 'Version', version_id, kwargs)
            return True
        except Exception as e:
            traceback.print_exc(e)
    elif upload_movie and kwargs and not upload_thumbnail:
        try:
            sg.upload("Version", version_id, upload_movie, field_name=field_name)
            sg_base.update_entity(sg, 'Version', version_id, kwargs)
            return True
        except Exception as e:
            traceback.print_exc(e)
    elif upload_thumbnail and upload_movie and kwargs:
        try:
            sg.upload_thumbnail('Version', version_id, upload_thumbnail)
            sg_base.update_entity(sg, 'Version', version_id, kwargs)
            return True
        except Exception as e:
            traceback.print_exc(e)


def update_version_thumbnail(sg, version_id, upload_thumbnail):
    '''
    更新版本缩略图
    :param sg: sg实体
    :param version_id: version id
    :param upload_thumbnail: 缩略图路径
    :return: True
    '''
    return update_version_version(sg, version_id, upload_thumbnail=upload_thumbnail)

def select_version_version(sg, version_id, version_fields=[]):
    """
    查询version信息
    :param sg: sg实体
    :param version_id: version ID
    :param version_fields: version字段列表
    :return: version字典
    """
    return sg_base.select_entity(sg, "Version", version_id, version_fields)


def download_version_thumbnail(sg, version_id):
    """
    下载version缩略图
    :param sg: sg实体
    :param version_id: version ID
    :return: 缩略图路径地址
    """
    version_entity = select_version_version(sg, version_id, ['code', 'image'])
    if not version_entity:
        return ""
    url = version_entity['image']
    version_name = version_entity['code']
    version_name = os.path.splitext(version_name)[0]

    temp_image_file = tempfile.gettempdir() + "\\" + version_name + ".jpg"

    if url:
        try:
            urllib.request.urlretrieve(url, temp_image_file)
            return temp_image_file
        except:
            urllib.urlretrieve(url, temp_image_file)
            return temp_image_file

    else:
        return ''


def remove_version_thubnail(sg,version_id):
    u"""
    删除缩略图
    Args:
        sg: sg 实体
        version_id:  version ID

    Returns:

    """
    data = {'image': None}
    try:
        sg.update('Version', version_id, data)
    except:
        pass
