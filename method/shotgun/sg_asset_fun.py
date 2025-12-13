# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       : sg_fun
# Describe   : 说明描述
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2023/12/7__10:12
# -------------------------------------------------------


def get_asset_sub_sub_assets_info(sg, asset_id):
    asset_sub_assets_info = {}
    asse_sub_assets = get_asset_sub_sub_assets(sg, asset_id)
    if not asse_sub_assets:
        return asset_sub_assets_info
    for k, v in asse_sub_assets.items():

        asset_name = get_asset_code_from_id(sg, k)

        __list = []
        for asset in v:
            if isinstance(asset, dict):
                if 'id' in asset.keys():
                    __list.append(asset['name'])
                else:
                    for m, n in asset.items():
                        __asset_name = get_asset_code_from_id(sg, m)

                        __sub = get_asset_sub_sub_assets_info(sg, m)
                        __list.append(__sub)

            if isinstance(asset, list):
                for _asset in asset:
                    __dict = get_asset_sub_sub_assets_info(sg, _asset['id'])
                    __list.append(__dict)
        asset_sub_assets_info[asset_name] = __list
    return asset_sub_assets_info


def get_asset_from_asset_name(sg, asset_name, project_name='X3'):
    '''
    获取资产的id
    :return:
    '''
    filters = [
        ['project.Project.name', 'is', project_name],
        ['code', 'is', asset_name]
    ]
    fields = ['id', 'code', 'sg_asset_type']
    return sg.find_one('Asset', filters, fields)


def get_asset_from_asset_id(sg, asset_id):
    '''
    获取资产的id
    :return:
    '''
    filters = [
        ['id', 'is', asset_id]
    ]
    fields = ['id', 'code', 'sg_asset_type']
    return sg.find_one('Asset', filters, fields)


def get_task_data_from_task_name(sg, task_name, asset_id):
    from method.shotgun import get_task_data
    task = get_task_from_task_name(sg, task_name, asset_id)
    if not task:
        return
    try:
        return get_task_data.TaskData(task['id'])
    except:
        return


def get_task_from_task_name(sg, task_name, asset_id):
    '''
    获取任务的data
    :return:
    '''
    filters = [
        ["entity.Asset.id", 'is', asset_id],
        ['content', 'is', task_name]
    ]
    fields = ['id', 'content', 'entity', 'sg_status_list', 'sg_task_type', 'step', 'entity.Asset.sg_asset_type',
              'sg_work']
    return sg.find_one('Task', filters, fields)


def get_asset_sub_sub_assets(sg, asset_id):
    '''
    获取资产的子资产的子资产
    :return:
    '''
    asset_sub_assets = {}
    asset_sub_sub_assets = []
    sub_assets_list = get_asset_sub_assets(sg, asset_id)
    if not sub_assets_list:
        return asset_sub_sub_assets
    for sub_asset in sub_assets_list:
        __dict = get_asset_sub_sub_assets(sg, sub_asset['id'])
        if __dict:
            asset_sub_sub_assets.append(__dict)
        else:
            asset_sub_sub_assets.append(sub_asset)
    if asset_sub_sub_assets:
        asset_sub_assets[asset_id] = asset_sub_sub_assets

    return asset_sub_assets


def get_asset_sub_sub_asset_ids(sg, asset_id):
    '''
    获取资产的子资产的子资产
    :return:
    '''
    asset_sub_assets = {}
    asset_sub_sub_assets = []
    sub_assets_list = get_asset_sub_asset_ids(sg, asset_id)
    if asset_id in sub_assets_list:
        sub_assets_list.remove(asset_id)
    if not sub_assets_list:
        return asset_sub_sub_assets
    for sub_asset in sub_assets_list:

        __dict = get_asset_sub_sub_asset_ids(sg, sub_asset)

        if __dict:
            asset_sub_sub_assets.append(__dict)
        else:
            asset_sub_sub_assets.append(sub_asset)
    if asset_sub_sub_assets:
        asset_sub_assets[asset_id] = asset_sub_sub_assets

    return asset_sub_assets


def get_asset_sub_type_assset_ids(sg, asset_id, sub_asset_type='weapon'):
    '''
    获取资产的子资产
    :return:
    '''
    sub_assetss = []
    asset = sg.find_one('Asset', [['id', 'is', asset_id]], ['code', 'sg_asset_type', 'assets'])
    if not asset:
        return sub_assetss
    if asset and asset['assets'] and asset['assets']:
        sub_assets= asset['assets']
        if not sub_asset_type:
            return sub_assets
        for sub_asset in sub_assets:
            __sub_asset_type=get_asset_type_by_id(sg, sub_asset['id'])
            if __sub_asset_type==sub_asset_type:
                sub_assetss.append(sub_asset)
    return sub_assetss


def get_asset_type_by_id(sg, asset_id):
    asset = sg.find_one('Asset', [['id', 'is', asset_id]], ['sg_asset_type'])
    if asset and 'sg_asset_type' in asset.keys():
        return asset['sg_asset_type']
    else:
        return ''


def get_asset_sub_asset_ids(sg, asset_id):
    '''
    获取资产的子资产
    :return:
    '''
    sub_assets = []
    assets = sg.find_one('Asset', [['id', 'is', asset_id]], ['code', 'sg_asset_type', 'assets'])
    if not assets:
        return sub_assets
    if assets and assets['assets'] and assets['assets']:
        for asset in assets['assets']:
            sub_assets.append(asset['id'])
    return sub_assets


def get_asset_code_from_id(sg, asset_id):
    '''
    获取资产的code
    :return:
    '''
    asset_code = ''
    assets = sg.find('Asset', [['id', 'is', asset_id]], ['code'])

    if not assets:
        return asset_code

    asset_code = assets[0]['code']

    return asset_code


def get_task_info_from_task_name(sg, task_name, asset_id):
    '''
    获取任务的data
    :return:
    '''
    import os
    result = {}
    task = get_task_from_task_name(sg, task_name, asset_id)
    if task and 'sg_work' in task.keys():
        work_dict = task['sg_work']
        if work_dict and 'work_file' in eval(work_dict).keys():
            work_file = eval(work_dict)['work_file']
            if not work_file:
                return
            work_file = work_file.replace('\\', '/')
            work_dir = os.path.dirname(work_file)
            publish_dir = work_dir.replace('/work/', '/publish/')
            version_file = get_laster_version_file(publish_dir, ['png', 'jpg', 'mp4'])
            if not version_file:
                return
            publish_file = get_laster_version_file(publish_dir, ['ma'])
            if not publish_file:
                return
            result['work_file'] = work_file.replace('\\', '/')
            result['publish_file'] = publish_file.replace('\\', '/')
            result['version_file'] = version_file.replace('\\', '/')
            result['task_name'] = task_name
            result['task_id'] = task['id']
    return result


def get_laster_version_file(file_dir, suffixs=[]):
    import os
    import glob
    if not os.path.isdir(file_dir):
        return
    files = []
    for suffix in suffixs:
        files = glob.glob(file_dir + '/*.' + suffix)
        if files:
            break
    if not files:
        return
    files.sort(key=lambda x: os.path.getmtime(x))
    return files[-1]


def get_asset_sub_assets(sg, asset_id):
    '''
    获取资产的子资产
    :return:
    '''
    sub_assets = []
    assets = sg.find('Asset', [['id', 'is', asset_id]], ['code', 'sg_asset_type', 'assets'])
    if not assets:
        return sub_assets
    if assets[0]['assets']:
        return assets[0]['assets']


def get_version_file(sg, version_id):
    version = sg.find_one('Version', [['id', 'is', version_id]], ['sg_path_to_frames'])
    return version['sg_path_to_frames']


if __name__ == '__main__':
    import database.shotgun.core.sg_analysis as sg_analysis

    A = ['PL018S']
    asset_id = 37085

    sg = sg_analysis.Config().login()
    print(get_asset_sub_type_assset_ids(sg, asset_id,sub_asset_type='weapon'))
    # assets = sg.find_one('Asset', [['id', 'is', asset_id]], ['code', 'sg_asset_type', 'assets'])
    # print(assets)
    # asset_id = 13809
    # # print get_asset_sub_sub_assets(sg, asset_id)
    # print get_asset_sub_sub_assets_info(sg, asset_id)

    # asset_name = 'FY001C'
    # task_name = 'rbf'
    # asset_id = 13809
    # print get_asset_from_asset_name(sg, asset_name)

    # asset_data = {'code': 'FY001C', 'type': 'Asset', 'id': 12858, 'sg_asset_type': 'role'}
    # asset_id = asset_data['id']
    # task_data = get_task_data_from_task_name(sg, task_name, asset_id)
    # print task_data.laster_publish_path
    # task=get_task_from_task_name(sg, task_name, asset_id)
    # get_task_info_from_task_name(sg, task_name, asset_id)
    # file_dir='M:/projects/X3/work/assets/role/FY001C/rbf/maya'
    # suffix='FY001C.rbf.v'
    # print get_task_info_from_task_name(sg, task_name, asset_id)
    # asset_id=20319
    # print(get_asset_sub_sub_asset_ids(sg, asset_id))
    # print task
