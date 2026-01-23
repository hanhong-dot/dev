# -*- coding: utf-8 -*-
# author: linhuan
# file: judge_online_version_entity.py
# time: 2026/1/23 15:23
# description:
import lib.common.config as config
import lib.common.jsonio as jsonio


def get_online_entity_version():
    _configpath = config.GetConfig(dcc='shotgun', configfile="oline_entity_version.json").get_config()
    return jsonio.read(_configpath)


def judge_is_online_entity(sg, task_id):
    online_entity_version = get_online_entity_version()
    judge = False
    for entity_version in online_entity_version:
        __judge = judge_is_online_entity_version(sg, task_id, entity_version)
        if __judge and __judge == True:
            judge = True
            break
    return judge


def judge_is_online_entity_version(sg, task_id, entity_version='obt-251231'):
    entity_info = get_entity_by_task_id(sg, task_id)

    if not entity_info:
        return False
    entity_type = entity_info['type']
    entity_id = entity_info['id']
    entity_r = get_entity_entity_r(sg, entity_type, entity_id)
    if not entity_r:
        return False


    online_entity_num = get_entity_num_by_entity_r(entity_version)
    if not online_entity_num:
        if entity_r == entity_version:
            return True
        else:
            return False
    entity_num = get_entity_num_by_entity_r(entity_r)
    if entity_num is None:
        return False

    if int(entity_num) <= int(online_entity_num):
        return True
    return False


def get_entity_entity_r(sg, entity_type, entity_id):
    filters = [
        ['id', 'is', entity_id]
    ]
    if entity_type == 'Asset':
        fields = ['sg_text_4']
    elif entity_type == 'Shot':
        fields = ['sg_text_1']
    elif entity_type == 'Sequence':
        fields = ['sg_text']
    else:
        return None
    entity_info = sg.find_one(entity_type, filters, fields)
    if entity_info and entity_info.get(fields[0]):
        return entity_info[fields[0]]
    return None


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
    # 判断字符串是否全为数字
    return name.isdigit()


def get_entity_by_task_id(sg, task_id):
    filters = [
        ['id', 'is', task_id]
    ]
    fields = ['entity']
    task_info = sg.find_one('Task', filters, fields)
    if task_info and task_info.get('entity'):
        return task_info['entity']
    return None


if __name__ == '__main__':

    import database.shotgun.core.sg_analysis as sg_analysis
    #
    sg = sg_analysis.Config().login()
    task_id=155830

    print(judge_is_online_entity(sg, task_id))
    #
    # entity_r = get_entity_entity_r(sg, 'Asset', 24022)
    # print(get_entity_num_by_entity_r(entity_r))
