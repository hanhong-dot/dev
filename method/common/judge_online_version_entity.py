# -*- coding: utf-8 -*-
# author: linhuan
# file: judge_online_version_entity.py
# time: 2026/1/23 15:23
# description:
import json

import lib.common.config as config
import lib.common.jsonio as jsonio


#


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


def get_all_online_mod_modify_assets(project_name='X3'):
    import database.shotgun.core.sg_analysis as sg_analysis
    sg = sg_analysis.Config().login()
    online_entity_version = get_online_entity_version()
    filter = [['project.Project.name', 'is', project_name], ['sg_text_4', 'is_not', None],
              ['sg_asset_type', 'in', ['role', 'hair']]]
    fields = ['sg_text_4', 'code', 'id']
    assets = sg.find('Asset', filter, fields)
    __mod_modify_assets = []
    if not assets:
        return []
    for asset in assets:
        entity_r = asset.get('sg_text_4')
        result = judge_is_online_entity_by_entity_r(entity_r, entity_version=online_entity_version[0])
        if not result or result == False:
            continue
        ok,result= judge_asset_is_mod_modify(sg, asset.get('id'))
        if ok and ok== True:
            __updata_time=result
            __mod_modify_assets.append({'id': asset.get('id'), 'name': asset.get('code'), 'entity_r': entity_r,'updata_time':__updata_time})
    return __mod_modify_assets

def get_updata_model_time(sg,task_id):
    updata_time=''
    new_time=0
    filters = [
        ["task","is",{'type':'Task','id':task_id}]
    ]
    fileds=["created_at","published_file_type"]
    publishs=sg.find("PublishedFile",filters,fileds)

    if not publishs:
        return updata_time
    for publish in publishs:
        published_file_type=publish.get("published_file_type")
        if not published_file_type:
            continue
        created_at=publish.get("created_at")
        if not created_at:
            continue
        created_at_str=covert_time_to_str(created_at)
        timestamp=cover_time_to_timestamp(created_at)
        if timestamp>new_time and published_file_type.get("name")=='Maya Scene':
            new_time=timestamp
            updata_time=created_at_str
    return updata_time



def cover_time_to_timestamp(time):
    if not time:
        return 0
    return int(time.strftime('%Y%m%d%H%M%S'))


def covert_time_to_str(time):
    if not time:
        return ''
    return time.strftime('%Y%m%d-%H%M%S')


def judge_asset_is_mod_modify(sg, asset_id):
    rig_task_names = ['rbf', 'drama_rig']
    for task_name in rig_task_names:
        filters = [
            ['entity', 'is', {'type': 'Asset', 'id': asset_id}],
            ['content', 'is', task_name]
        ]
        fields = ['id', 'sg_send_jenkins']
        task = sg.find_one('Task', filters, fields)
        if not task:
            continue
        __jekins_data = task.get('sg_send_jenkins', None)
        if not __jekins_data:
            continue
        __jekins_data = eval(__jekins_data)
        __update_model = __jekins_data.get('update_model', 0)

        if __update_model  and int(__update_model) == 1:
            __updata_time=get_updata_model_time(sg,  task.get('id'))
            return True,__updata_time
    return False,'not modify'


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


def judge_is_online_entity_by_entity_r(entity_r, entity_version='obt-251231'):
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

    print(get_all_online_mod_modify_assets())

    # sg = sg_analysis.Config().login()
    # task_id=81745
    # print(get_updata_model_time(sg, task_id))
    # asset_id=35026
    # judge_asset_is_mod_modify(sg, asset_id)

    # online_entity_version = get_online_entity_version()
    # print(online_entity_version)
    # import database.shotgun.core.sg_analysis as sg_analysis
    #
    # #
    # sg = sg_analysis.Config().login()
    # task_id = 155830
    #
    # print(judge_is_online_entity(sg, task_id))
    #
    # get_all_online_mod_modify_assets()
    #
    # entity_r = get_entity_entity_r(sg, 'Asset', 24022)
    # print(get_entity_num_by_entity_r(entity_r))
