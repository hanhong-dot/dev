# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       : sg_common
# Describe   : sg 相关命令
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2024/2/18__11:42
# -------------------------------------------------------
import os.path

import database.shotgun.core.sg_analysis as sg_analysis
import method.shotgun.get_task_data as get_task_data
import method.common.dir as _dir

reload(_dir)

PRP_ASSET_TYPES = ['item', 'plant', 'environment', 'envmodel', 'scn']


def get_assets(project='X3', asset_type='all'):
    '''
    获取资产
    :param project: 项目名
    :param asset_type: 资产类型
    :return: 返回资产列表
    '''
    sg = sg_analysis.Config().login()
    if asset_type == 'all':
        filters = [['project.Project.name', 'is', project]]
    else:
        filters = [['project.Project.name', 'is', project], ['sg_asset_type', 'is', asset_type]]
    fields = ['code']
    assets = sg.find('Asset', filters, fields)
    return assets


def copy_publish_files(_dict, project='X3'):
    asset_type = _dict['asset_type']
    asset_name = _dict['asset_name']
    task_name = _dict['task_name']
    file_type = _dict['file_type']
    local_map = _dict['check_local_map']
    sg = sg_analysis.Config().login()
    task_ids = []
    errors = []

    filters = [
        ["entity.Asset.sg_asset_type", "is", asset_type],
        ['project.Project.name', 'is', project],
        ['content', 'is', task_name]
    ]
    if not asset_name:
        tasks = sg.find('Task', filters, ['entity', 'content'])
        if tasks:
            task_ids = [task['id'] for task in tasks if (task and task['id'])]
    else:
        asset_names = asset_name.split('\n')

        for asset_name in asset_names:
            filters_new = []
            filters_new.extend(filters)

            filters_new.append(['entity.Asset.code', 'is', asset_name])

            tasks = sg.find('Task', filters_new, ['entity', 'content'])
            if tasks:
                task_id = tasks[0]['id']
                task_ids.append(task_id)
    if not task_ids:
        return False, u'未找到任务,请检查资产类型，资产名或任务名是否正确'

    publish_local_dir = _dir.get_localtemppath('collect_files/publish')
    work_local_dir = _dir.get_localtemppath('collect_files/work')
    fbx_local_dir = _dir.get_localtemppath('collect_files/fbx')

    copy_files = []

    for task_id in task_ids:
        try:
            task_data = get_task_data.TaskData(task_id)
        except:
            task_data = None

        if task_data:
            if file_type == 'all':
                publish_dir = task_data.publish_dir
                task_name = task_data.task_name
                fbx_dir = '{}/fbx'.format(task_data.publish_data_dir)
                entity_name = task_data.entity_name
                publish_file = _dir.get_laster_file(publish_dir, _suffixs=['.ma'])
                fbx_files = _dir.get_files(fbx_dir, _suffixs=['.fbx'])
                if asset_type not in PRP_ASSET_TYPES:
                    local_publish_dir = '{}/{}/{}'.format(publish_local_dir, entity_name, task_name)
                else:
                    local_publish_dir = publish_local_dir
                if not os.path.exists(local_publish_dir):
                    os.makedirs(local_publish_dir)
                if asset_type not in PRP_ASSET_TYPES:
                    local_publish_fbx_dir = '{}/fbx'.format(local_publish_dir)
                else:
                    local_publish_fbx_dir = fbx_local_dir
                if not os.path.exists(local_publish_fbx_dir):
                    os.makedirs(local_publish_fbx_dir)
                if publish_file and os.path.exists(publish_file):
                    pub_result = copy_file(publish_file, local_publish_dir)
                    if pub_result == True:
                        copy_files.append('{}/{}'.format(local_publish_dir, os.path.basename(publish_file)))
                if fbx_files:
                    for fbx_file in fbx_files:
                        fbx_result = copy_file(fbx_file, local_publish_fbx_dir)
                        if fbx_result == True:
                            copy_files.append('{}/{}'.format(local_publish_fbx_dir, os.path.basename(fbx_file)))

                ok, work_file = get_work_file(task_id)
                if ok == True and work_file and os.path.exists(work_file):
                    if asset_type not in PRP_ASSET_TYPES:
                        local_work_dir = '{}/{}/{}'.format(work_local_dir, entity_name, task_name)
                    else:
                        local_work_dir = work_local_dir
                    if not os.path.exists(local_work_dir):
                        os.makedirs(local_work_dir)
                    work_result = copy_file(work_file, local_work_dir)
                    if work_result == True:
                        copy_files.append('{}/{}'.format(local_work_dir, os.path.basename(work_file)))


            elif file_type == 'ma(publish)':
                publish_dir = task_data.publish_dir

                entity_name = task_data.entity_name

                task_name = task_data.task_name

                publish_file = _dir.get_laster_file(publish_dir, _suffixs=['.ma'])

                if asset_type not in PRP_ASSET_TYPES:
                    local_publish_dir = '{}/{}/{}'.format(publish_local_dir, entity_name, task_name)
                else:
                    local_publish_dir = publish_local_dir
                if not os.path.exists(local_publish_dir):
                    os.makedirs(local_publish_dir)

                if publish_file and os.path.exists(publish_file):
                    pub_result = copy_file(publish_file, local_publish_dir)
                    if pub_result == True:
                        copy_files.append('{}/{}'.format(local_publish_dir, os.path.basename(publish_file)))

            elif file_type == 'ma(work)':
                ok, work_file = get_work_file(task_id)
                if ok == True and work_file and os.path.exists(work_file):
                    entity_name = task_data.entity_name
                    task_name = task_data.task_name
                    if asset_type not in PRP_ASSET_TYPES:
                        local_work_dir = '{}/{}/{}'.format(work_local_dir, entity_name, task_name)
                    else:
                        local_work_dir = work_local_dir
                    if not os.path.exists(local_work_dir):
                        os.makedirs(local_work_dir)
                    work_result = copy_file(work_file, local_work_dir)
                    if work_result == True:
                        copy_files.append('{}/{}'.format(local_work_dir, os.path.basename(work_file)))


            elif file_type == 'fbx':
                fbx_dir = '{}/fbx'.format(task_data.publish_data_dir)
                entity_name = task_data.entity_name
                task_name = task_data.task_name

                fbx_files = _dir.get_files(fbx_dir, _suffixs=['.fbx'])

                if asset_type not in PRP_ASSET_TYPES:
                    local_publish_fbx_dir = '{}/{}/{}/fbx'.format(publish_local_dir, entity_name, task_name)
                else:
                    local_publish_fbx_dir = fbx_local_dir

                if not os.path.exists(local_publish_fbx_dir):
                    os.makedirs(local_publish_fbx_dir)
                if fbx_files:
                    for fbx_file in fbx_files:
                        fbx_result = copy_file(fbx_file, local_publish_fbx_dir)
                        if fbx_result == True:
                            copy_files.append('{}/{}'.format(local_publish_fbx_dir, os.path.basename(fbx_file)))

    if copy_files:
        return True, copy_files
    else:
        return False, u'未收集到文件,请检查'


def collect_map_files_by_file(file_path, local_dir, nodetypes=[]):
    import method.maya.common.collect_nodefile as collect_nodefile
    reload(collect_nodefile)
    from method.maya.common.file import BaseFile
    import lib.maya.analysis.analyze_data as analyze_data
    __collect_dict = {}

    BaseFile().open_file(file_path)
    _data = analyze_data.AnalyData().get_data_info()
    if not nodetypes:
        nodetypes = _data["FILE_ATTR"].keys()
    for node_type in nodetypes:
        __local_path = '{}/data/{}'.format(local_dir, _data["FILE_ATTR_PATH"][node_type])
        _source_targe_dict = collect_nodefile.CollectNodeFile(targepath=__local_path,
                                                              nodetypelist=[node_type]).collect_nodefiles(ex=True,
                                                                                                          _cover=None)
        __collect_dict.update(_source_targe_dict)
    BaseFile().save_file(file_path)
    return __collect_dict


def collect_map_files(copy_files):
    if not copy_files:
        return
    __dict = {}
    for _file in copy_files:
        if _file.endswith('.ma'):
            _dir, _basename = os.path.split(_file)
            __collect_dict = collect_map_files_by_file(_file, _dir, nodetypes=[])
            if __collect_dict:
                __dict.update(__collect_dict)
    return __dict


def collect_map_files_from_file(file_path):
    if not file_path or not os.path.exists(file_path):
        return False, u'{} not exist'.format(file_path)
    if file_path.endswith('.ma'):
        _dir, _basename = os.path.split(file_path)
        __collect_dict = collect_map_files_by_file(file_path, _dir, nodetypes=[])
        if __collect_dict:
            return True, __collect_dict
    return False, u'{} not ma file'.format(file_path)


def get_work_file(task_id):
    if not task_id:
        return False, u'未找到任务id'
    sg = sg_analysis.Config().login()
    work = sg.find('Task', [['id', 'is', task_id]], ['sg_work'])

    if work and work[0] and work[0]['sg_work']:
        result = work[0]['sg_work']

        if result and 'work_file' in eval(result) and eval(result)['work_file']:
            return True, eval(result)['work_file']
    return False, u'未找到work文件'


def copy_file(source_file, target_dir):
    '''
    复制文件
    :param source_file: 源文件
    :param target_file: 目标文件
    :return:
    '''
    import shutil
    try:
        shutil.copy(source_file, target_dir)
        return True
    except Exception as e:
        print(e)
        return False


if __name__ == '__main__':
    copy_files = [r'D:\temp_info\collect_files\work\FY_BODY\FY_BODY.drama_mdl.v056.ma']
    collect_map_files(copy_files)
