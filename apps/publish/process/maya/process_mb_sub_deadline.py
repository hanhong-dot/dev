# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       : process_mb_sub_deadline
# Describe   : 说明描述
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2024/1/16__11:22
# -------------------------------------------------------

from database.deadline import maya_submission

reload(maya_submission)

import os

ADASSETS = ['M3011_Puppet01', 'M3111_Obsidian01', 'M3013_Puppet05', 'M3017_Puppet09', 'M3011_Puppet01_test',
            'M3011_Puppet01_Card', 'M3451_STCardSkeleton01', 'M3451_STCardSkeleton01_Card', 'M3121_DirewolfCard01','NPC_Ecat01','NPC_Ecat02','NPC_Ecat02']
EXASSETTYPE = ['item', 'enemy', 'weapon', 'rolaccesory', 'hair','npc']


def process_mb_sub_deadline(TaskData, mb_export=True):
    '''
    maya批处理提交deadline
    :param file_path:
    :param cmd:
    :return:
    '''
    import maya.cmds as cmds
    entity_name = TaskData.entity_name
    task_name = TaskData.task_name
    asset_type = TaskData.asset_type
    file_path = cmds.file(q=1, exn=1)
    if task_name not in ['drama_rig', 'rbf', 'out_rig', 'rbf_rm', 'out_rig_rm']:
        mb_export = False

    if asset_type in EXASSETTYPE:
        mb_export = False

    if entity_name in ADASSETS:
        mb_export = True

    if mb_export == True:
        job_name = 'export_mb--{}'.format(os.path.basename(file_path))
        cmd = 'from apps.publish.process.maya import process_mb_batch;reload(process_mb_batch);process_mb_batch.batch_mb_export()'
        return maya_submission.maya_submission(file_path, cmd, job_name)
    else:
        return {}


def process_republish_role_weapon_sub_deadline():
    import maya.cmds as cmds
    file_path = cmds.file(q=1, exn=1)
    base_name = os.path.basename(file_path)
    job_name = 'republish_role_weapon_sub_assets--{}'.format(base_name)
    cmd = 'from apps.publish.process.maya import process_maya_batch;reload(process_maya_batch);process_maya_batch.batch_republish_role_weapon_sub_republish()'
    return maya_submission.maya_submission(file_path, cmd, job_name)


def process_republish_role_sub_deadline():
    '''
    maya批处理提交deadline
    :param file_path:
    :param cmd:
    :return:
    '''
    import maya.cmds as cmds
    process_assets = ['XL_BODY']
    file_path = cmds.file(q=1, exn=1)
    base_name = os.path.basename(file_path)
    if base_name.split('.')[0] in process_assets:
        job_name = 'republish_sub_assets--{}'.format(base_name)
        cmd = 'from apps.publish.process.maya import process_maya_batch;reload(process_maya_batch);process_maya_batch.batch_republish_role_sub_republish()'
        return maya_submission.maya_submission(file_path, cmd, job_name)


def process_republish_item_sub_deadline():
    '''
    maya批处理提交deadline
    :param file_path:
    :param cmd:
    :return:
    '''
    import maya.cmds as cmds
    file_path = cmds.file(q=1, exn=1)
    base_name = os.path.basename(file_path)

    job_name = 'republish_item_sub_assets--{}'.format(base_name)
    cmd = 'from apps.publish.process.maya import process_maya_batch;reload(process_maya_batch);process_maya_batch.batch_republish_item_sub_republish()'
    return maya_submission.maya_submission(file_path, cmd, job_name)


def batch_process_mb_sub_deadline(file_path, mb_export=True):
    if mb_export == True:
        job_name = 'export_mb--{}'.format(os.path.basename(file_path))
        cmd = 'from apps.publish.process.maya import process_mb_batch;reload(process_mb_batch);process_mb_batch.batch_mb_export()'
        return maya_submission.maya_submission(file_path, cmd, job_name)
    else:
        return {}


def batch_republish_item_variant_asset_deadline(asset_id, asset_name):
    '''
    maya批处理提交deadline
    :param file_path:
    :param cmd:
    :return:
    '''
    job_name = 'republish_item_variant_asset--{}'.format(asset_name)
    cmd = 'from apps.publish.process.maya import republish_item_variant_asset_rig;reload(republish_item_variant_asset_rig);republish_item_variant_asset_rig.RepublishItemVariantAssetRig({}).run()'.format(
        asset_id)
    file_path = r'Z:\Data\Maya\batch.ma'

    return maya_submission.maya_submission(file_path, cmd, job_name)
