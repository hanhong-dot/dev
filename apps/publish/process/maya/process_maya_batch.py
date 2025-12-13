# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       :
# Describe   :
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2024/7/17
# -------------------------------------------------------
import maya.cmds as cmds
import method.shotgun.get_task as get_task
def batch_republish_role_sub_republish(project_name='X3',tag='version',dcc='maya'):
    import apps.publish.process.maya.republish_role_sub_republish as republish_role_sub_republish
    reload(republish_role_sub_republish)
    file_path = cmds.file(q=1, exn=1)
    task_data = get_task.TaskInfo(file_path, project_name, dcc, tag, is_lastversion=True)
    return republish_role_sub_republish.RePubliSub(task_data).republish_sub_assets(open_file=False,copy_publish_file=False)


def batch_republish_role_weapon_sub_republish(project_name='X3',tag='version',dcc='maya'):
    import apps.publish.process.maya.republish_role_weapon_sub_republish as republish_role_weapon_sub_republish
    reload(republish_role_weapon_sub_republish)
    file_path = cmds.file(q=1, exn=1)
    task_data = get_task.TaskInfo(file_path, project_name, dcc, tag, is_lastversion=True)
    return republish_role_weapon_sub_republish.RePubRoleSub(task_data).republish_sub_assets(open_file=False,copy_publish_file=False,sub_asset_types=['weapon'])
def batch_republish_item_sub_republish(project_name='X3',tag='version',dcc='maya'):
    import apps.publish.process.maya.republish_item_sub_republish as republish_item_sub_republish
    reload(republish_item_sub_republish)
    file_path = cmds.file(q=1, exn=1)
    task_data = get_task.TaskInfo(file_path, project_name, dcc, tag, is_lastversion=True)
    return republish_item_sub_republish.ItemRePubSub(task_data).republish_sub_assets(open_file=False,sub_asset_types=['item'])

