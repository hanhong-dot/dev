# -*- coding: utf-8 -*-
# author: linhuan
# file: sg_fun.py
# time: 2025/11/27 16:17
# description:
import os
from database.shotgun.core import sg_asset
import database.shotgun.core.sg_analysis as sg_analysis

sg = sg_analysis.Config().login()
PROJECTNAME = 'X3'


def check_maping(maping_data):
    if not maping_data:
        return False, u'Mapping data is empty'
    error_list = []
    for k, v in maping_data.items():
        if not v:
            error_list.append(u'{} 没有输入映射资产名,请检查'.format(k))
        else:
            ok, result = get_rig_task_by_asset_name(v)
            if not ok:
                error_list.append(u'{}映射资产名不正确:{}'.format(k, result))
    if error_list:
        return False, '\n'.join(error_list)
    return True, 'Mapping data is valid'


def check_asset_from_name(asset_name):
    asset = sg_asset.select_asset_entity_by_name(sg, PROJECTNAME, asset_name, fields=['id', 'sg_asset_type'])
    if not asset:
        return False, u'资产:{}不存在，请检查'.format(asset_name)
    asset_type = asset.get('sg_asset_type')
    if asset_type.lower() not in ['body', 'role','npc']:
        return False, u'资产:{} 资产类型不是Body或Role或npc，请检查'.format(asset_name)
    return True, asset


def get_rig_task_by_asset_name(asset_name):
    ok, asset = check_asset_from_name(asset_name)
    if not ok:
        return False, asset
    filters = [['project.Project.name', 'is', PROJECTNAME],
               ['entity', 'is', asset],
               ['content', 'is', 'rbf']]
    fields = ['id', 'sg_status_list', 'sg_work']
    rbf_tasks = sg.find_one('Task', filters, fields)
    work = rbf_tasks.get('sg_work') if rbf_tasks else None
    status = rbf_tasks.get('sg_status_list') if rbf_tasks else None
    if not rbf_tasks or not work or status in ['omt']:
        filters = [['project.Project.name', 'is', PROJECTNAME],
                   ['entity', 'is', asset],
                   ['content', 'is', 'drama_rig']]
        rbf_tasks = sg.find_one('Task', filters, fields)
        if not rbf_tasks:
            return False, u'资产:{} 没有找到绑定任务，请检查'.format(asset_name)
        work = rbf_tasks.get('sg_work') if 'sg_work' in rbf_tasks else None
        if not work:
            return False, u'资产:{} 绑定任务没有上传过文件，请检查'.format(asset_name)
    return True, rbf_tasks


def get_publish_file_by_task(task):
    if not task:
        return False, u'Task is None'
    task_id = task.get('id')
    if not task_id:
        return False, u'Task id is None'
    filters = [['project.Project.name', 'is', PROJECTNAME], ['task', 'is', {'type': 'Task', 'id': task_id}],
               ['published_file_type', 'name_is', 'Maya Scene']]
    fields = ['id', 'path']
    publishes = sg.find_one('PublishedFile', filters, fields)
    path = publishes.get('path') if publishes else None
    path = path.get('local_path_windows') if path else None
    return True, path


def rig_publish_file_by_asset_name(asset_name):
    ok, task = get_rig_task_by_asset_name(asset_name)
    if not ok:
        return False, task
    return get_publish_file_by_task(task)


if __name__ == '__main__':
    asset_name = 'PL_Body'
    ok, task = get_rig_task_by_asset_name(asset_name)
    print(get_publish_file_by_task(task))
