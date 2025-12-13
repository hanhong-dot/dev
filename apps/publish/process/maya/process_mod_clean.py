# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       :
# Describe   : 说明描述
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2024/5/25__19:18
# -------------------------------------------------------
import os
import sys
import maya.cmds as cmds
from lib.maya.node.grop import BaseGroup
from method.maya.common.file import BaseFile

TASKS = ['fight_mdl', 'drama_mdl', 'lan_mdl', 'ue_low', 'ue_mdl']


def process_mod_clean(TaskData):
    task_name = TaskData.task_name
    if task_name in TASKS:
        file_= cmds.file(q=1, exn=1)
        clean_file(file_)
        BaseFile().open_file(file_)
        BaseFile().save_file(file_)
    return


def clean_file(file_name):
    groups = BaseGroup().get_root_groups()
    if groups:
        try:
            BaseFile().export_file(groups, file_name)
            return True
        except:
            return False
    return False
