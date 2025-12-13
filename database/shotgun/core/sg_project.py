# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       : sg_project
# Describe   : 说明描述
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2022/5/23__9:40
# -------------------------------------------------------
import database.shotgun.core.sg_base as sg_base


def create_project(sg, project_name, return_fields=None,
                   **kwargs):
    '''
    创建项目信息
    :param sg:sg实体
    :param project_name:项目名
    :param return_fields:返回的其他字段值的可选列表
    :param kwargs:其他字段的字典
    :return: 创建project实体的字典 {'type': 'Project', 'id': 115, 'name': 'ly_test'}
    '''
    data = {'name': project_name}
    data.update(kwargs)
    return sg.create("Project", data, return_fields)


def get_projecttype(sg, project_id):
    u"""
    获取 项目类型
    :param sg: sg 实体
    :param project_id: 项目id
    :return:
    """
    fields = ['sg_type']
    filters = [
        ['id', 'is', project_id],
    ]
    return sg.find('Project', filters, fields)


def get_current_project():
    u"""
    获取当前项目名
    """
    import sgtk
    return sgtk.platform.current_engine().context.project


def get_project_projectID(sg, project_name):
    '''
    获取项目ID
    :param sg: sg实例
    :param project_name: 项目名
    :return: 项目列表 例如：[{'type': 'Project', 'id': 95}]
    '''

    fields = ['id', 'name']
    filters = [
        ['name', 'is', project_name]
    ]
    return sg.find('Project', filters, fields)


def select_project_project(sg, project_id, project_fields=[]):
    '''
    查询项目信息
    :param sg: sg实体
    :param project_id: 项目ID
    :param project_fields: 项目字段列表
    :return:项目字典 例如：{'duration': 58, 'type': 'Project', 'id': 105}
    '''
    return sg_base.select_entity(sg, "Project", project_id, project_fields)


def update_project_project(sg, project_id, **kwargs):
    '''
    更新项目信息
    :param sg: sg实体
    :param project_id: 项目ID
    :param kwargs: 项目字段 例如：sg_project_frame = 25.0
    :return: True
    '''
    result = sg_base.update_entity(sg, "Project", project_id, kwargs)
    if result:
        return True
    else:
        return False


def get_current_project():
    u"""
    获取当前项目名
    :return:
    """
    import sgtk
    return sgtk.platform.current_engine().context.project['name']


