# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       : base_fun
# Describe   : 说明描述
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2023/12/8__11:26
# -------------------------------------------------------
import os.path
import sys

import yaml
from apps.tools.maya.sub_assets_republish import config
def read_center_action_config():
    '''
    给资产，素材库，中间部件配置菜单
    :param config_path: 菜单配置文件路径
    :return:  配置文件list列表
    '''
    menu_list = []
    config_path = config.get("config/common", 'center_widget_menu.yml')
    data_info = open(config_path, 'r').read()
    # yaml 模块版本最终会更新
    config_info = yaml.load(data_info)
    # print config_info
    # 读取菜单排序
    menu_order = config_info['tools_order']
    for menu_name in menu_order:
        temp_menu_list = (menu_name, [])
        for action in config_info[menu_name]:
            temp_action_name = action[0]
            temp_action_icon = action[1]
            temp_action_cmd = action[2]
            temp_menu_list[1].append([temp_action_name, temp_action_icon, temp_action_cmd])
        menu_list.append(temp_menu_list)

    return menu_list

def open_work_file(task_data):
    import maya.cmds as cmds

    import  method.maya.common.file as common_file
    if not task_data:
        cmds.confirmDialog(title=u'报错提示', message=u'没有任务数据,请选择任务', button=['Yes'], defaultButton='Yes')
        raise Exception(u'没有任务数据,请选择任务')
    task_data_list=task_data.split(';')
    task_data_new=eval(task_data_list[0])

    work_file=task_data_new['work_file']
    common_file.BaseFile().open_file(work_file)

def open_work_dir(task_data):
    import maya.cmds as cmds
    if not task_data:
        cmds.confirmDialog(title=u'报错提示', message=u'没有任务数据,请选择任务', button=['Yes'], defaultButton='Yes')
        raise Exception(u'没有任务数据,请选择任务')
    task_data_list=task_data.split(';')
    task_data_new=eval(task_data_list[0])

    work_file=task_data_new['work_file']
    work_dir=os.path.dirname(work_file)
    os.startfile(work_dir)

def publish_work_file(task_data):
    import maya.cmds as cmds
    import method.maya.common.file as common_file
    import method.shotgun.get_task as get_task
    import datetime
    import apps.publish.ui.layout.batch_publish as batch_publish

    current_time= datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    description=u'次级资产工具上传,{}'.format(current_time)


    currenter_file=cmds.file(q=1,exn=1)
    # common_file.BaseFile().save_file(currenter_file)
    if not task_data:
        cmds.confirmDialog(title=u'报错提示', message=u'没有任务数据,请选择任务', button=['Yes'], defaultButton='Yes')
        raise Exception(u'没有任务数据,请选择任务')
    task_datas=[]
    task_data_list=task_data.split(';')

    for data in task_data_list:
        task_datas.append(eval(data))

    if len(task_datas)>1:
        cmds.confirmDialog(title=u'报错提示', message=u'只能选择一个任务', button=['Yes'], defaultButton='Yes')
        raise Exception(u'只能选择一个任务')

    task_data_new=task_datas[0]
    work_file=task_data_new['work_file']
    task_id=task_data_new['task_id']
    version_file=task_data_new['version_file']

    taskdata = get_task.TaskInfo(work_file, 'X3', 'maya', 'publish')

    common_file.BaseFile().open_file(work_file)
    batch_publish.PPublishWidget(taskdata).do_publish(version_file, description)
    common_file.BaseFile().open_file(currenter_file)
    cmds.confirmDialog(title=u'完成提示', message=u'已上传,请检查', button=['Yes'], defaultButton='Yes')










# if __name__ == '__main__':
#     print read_center_action_config()