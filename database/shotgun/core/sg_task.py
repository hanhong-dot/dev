# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       : sg_task
# Describe   : 说明描述
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2022/5/23__18:52
# -------------------------------------------------------
import database.shotgun.core.sg_base as sg_base


def get_task_taskID(sg, project_name, task_name, link_entity_name):
    '''
    获取任务ID
    :param sg: sg实体
    :param project_name: 项目名
    :param task_name: 任务名
    :param link_entity_name: 资产/镜头/场次/集数等链接的实体名
    :return: 获取task ID的列表,否则为[] 如：[{'type': 'Task', 'id': 335062}]
    '''
    fields = ['id']
    filters = [
        ['project.Project.name', 'is', project_name],
        ['content', 'is', task_name],
        {
            "filter_operator": "any",
            "filters": [
                ["entity.Asset.code", "is", link_entity_name],
                ["entity.Shot.code", "is", link_entity_name],
                ["entity.Sequence.code", "is", link_entity_name],
                ["entity.Episode.code", "is", link_entity_name]
            ]
        }
    ]
    return sg.find('Task', filters, fields)


def select_task_version(sg, task_id, version_fields=['code'], add=None, tag='version'):
    """
    查询某任务链接的version信息
    :param sg:sg实体
    :param task_id:任务ID
    :param version_fields:version字段
    :param add: ‘lastest’筛选出最新版本文件
    :param tag:
    :return: version列表 例如：[{'type': 'Version', 'id': 30303}]
    """

    filters = [
        ['sg_task.Task.id', 'is', task_id]
    ]
    if add == 'latest':
        additional_filter_presets = [
            {
                "preset_name": "LATEST",
                "latest_by": "ENTITIES_CREATED_AT"
            }
        ]
        return sg.find("Version", filters, version_fields, additional_filter_presets=additional_filter_presets)
    else:
        return sg.find("Version", filters, version_fields)


def upadata_task(sg, task_id, data={}):
    try:
        sg_base.update_entity(sg, 'Task', task_id, data=data)
        return True
    except:
        return False




def creat_task(sg, projectname, step_id, entity_type, entity_id, task_name, return_fields=['id']):
    import database.shotgun.core.sg_project as sg_project
    task_dict = {}
    projectdata = sg_project.get_project_projectID(sg, projectname)[0]
    entity_data = {'type': entity_type, 'id': entity_id}
    step_data = {'type': 'Step', 'id': step_id}

    task_dict['project'] = projectdata
    task_dict['entity'] = entity_data
    task_dict['content'] = task_name
    task_dict['step'] = step_data

    return sg.create("Task", task_dict, return_fields=return_fields)



