# -*- coding: utf-8 -*-
# author: linhuan
# file: entity_r_fun.py
# time: 2026/2/2 16:05
# description:


import database.shotgun.core.sg_analysis as sg_analysis


def get_all_asset_entity_r(project_name='X3'):
    """
    获取所有资源的实体版本R
    :param project_name:
    :return:
    """
    sg = sg_analysis.Config().login()
    filters = [['project.Project.name', 'is', project_name]]
    fields = ['sg_text_4']
    assets = sg.find('Asset', filters, fields)
    entity_r_list = []
    for asset in assets:
        entity_r = asset.get('sg_text_4')
        if entity_r and entity_r not in entity_r_list:
            entity_r_list.append(entity_r)
    return entity_r_list


def judge_entity_r_in_online(entity_r, project_name='X3'):
    """
    判断实体版本R是否在在线版本中
    :param entity_r:
    :param project_name:
    :return:
    """
    result = judge_entity_r_exist_number(entity_r)
    if not result:
        return False, u'输入的版本没有数字结尾,请检查后重新输入'
    online_entity_r_list = get_all_asset_entity_r(project_name)
    if entity_r in online_entity_r_list:
        return True, u'输入的版本在在线版本中已存在'
    return False, u'资产不存在{}版本号,请检查后重新输入'.format(entity_r)


def judge_entity_r_exist_number(entity_r):
    entity_r_num = get_entity_num_by_entity_r(entity_r)
    if entity_r_num is not None:
        return True
    return False


def get_entity_num_by_entity_r(entity_r):
    if not entity_r:
        return None
    end_index = entity_r.split('-')[-1]
    if not end_index:
        return None
    if judge_num(end_index):
        return int(end_index)
    return None


def judge_num(name):
    return name.isdigit()
