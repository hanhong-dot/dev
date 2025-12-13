# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       : process_mb_sub_deadline
# Describe   : 说明描述
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2024/1/15__19:29
# -------------------------------------------------------

import database.deadline.maya_submission as maya_submission

reload(maya_submission)
import maya.cmds as cmds

import method.shotgun.get_task as get_task
import apps.publish.process.maya.process_export_rig_mb_fbx as process_export_rig_mb_fbx

reload(process_export_rig_mb_fbx)

from apps.publish.batch_publish import batch_publish

reload(batch_publish)
import database.shotgun.fun.get_entity as get_entity

import method.common.dir as common_dir
import os
import lib.common.jsonio as jsonio
USER_JSON='Z:/netrende/submit/maya/json/user.json'

def batch_process_mb_export(maya_file,user,send_jenkins=False):
    base_name = os.path.basename(maya_file)
    if 'v00' not in base_name:
        info = base_name.split('.')
        if len(info) >= 3:
            maya_file = '{}.{}.v000.ma'.format(info[0], info[1])

    task_data = get_task.TaskInfo(maya_file, 'X3', 'maya', 'version')
    version_file = get_entity_thumbnail(task_data)

    publish_dict = process_export_rig_mb_fbx.ProcessExportRigMbFbx(task_data,ui=False).export_mb_fbx()
    if publish_dict:
        ok, result = batch_publish.BatchPublish(task_data, version_file, u"MB提交农场处理").do_batch_publish_dict(
            publish_dict,user,send_jenkins)
        print 'ok', ok
        print 'result', result
        if ok==True and result ==True:
            return True
        if ok!=True:
            print(u"文件未正确上传,请检查")
            return False
        if result!=True:
            print(u"文件未正确上传shotgun,请检查")
            return False

    return True


def get_entity_thumbnail(task_data):
    import database.shotgun.core.sg_analysis as sg_analysis

    sg = sg_analysis.Config().login()
    entity_id = task_data.entity_id
    entity_name = task_data.entity_name
    entity_type = task_data.entity_type
    handle = get_entity.BaseGetSgInfo(sg, entity_id, entity_type)
    img_dir = common_dir.get_localtemppath('thumbnail')

    imagepath = '{}/{}.png'.format(img_dir, entity_name)
    return handle.download_entity_thumbnail(imagepath)

def get_user_from_json():

    user_info=jsonio.read(USER_JSON)
    if user_info and 'user' in user_info:
        return user_info['user']




def batch_mb_export():
    file_path = cmds.file(q=1, exn=1)
    user=get_user_from_json()
    return batch_process_mb_export(file_path,user)
