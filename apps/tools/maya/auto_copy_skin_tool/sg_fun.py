# -*- coding: utf-8 -*-
# author: linhuan
# file: copy_skin_fun.py
# time: 2025/12/13 15:28
# description:

import method.shotgun.get_task as get_task
from apps.publish.process.filehandle import remove_version



PROJECTNAME = 'X3'

import os


def check_targe_asset_type(sg,asset_name):
    u"""
    获取角色body资产名称
    :param asset_name: 角色资产名称
    :return: body资产名称
    """
    filters = [
        ['project.Project.name', 'is', PROJECTNAME],
        ['code', 'is', asset_name]
    ]
    fields = ['sg_asset_type', 'id']
    result = sg.find_one('Asset', filters, fields)
    if not result:
        return False, u"无法在shotgun中找到该资产信息，请检查资产名称是否正确！"
    asset_type = result['sg_asset_type']
    if asset_type != 'body':
        return False, u"当前资产类型为{0}，无法进行蒙皮复制操作，请填写body类型资产！".format(asset_type)
    return True, result['id']


def get_rig_publish_file_by_asset_name(asset_name):
    __file_name='{}.drama_rig.v001.ma'.format(asset_name)
    task_data = get_task.TaskInfo(__file_name, PROJECTNAME, 'maya', 'publish')
    if not task_data:
        return False, u"无法获取角色{}的drama_rig发布文件，请检查该资产是否已发布rig文件！".format(asset_name)
    publish_file= task_data.last_des
    publish_file=remove_version(publish_file)
    if not publish_file or not os.path.exists(publish_file):
        return False, u"无法获取角色{}的drama_rig发布文件，请检查该资产是否已发布rig文件！".format(asset_name)
    return True, publish_file

if __name__ == '__main__':
    print(get_rig_publish_file_by_asset_name('PL_Body'))


