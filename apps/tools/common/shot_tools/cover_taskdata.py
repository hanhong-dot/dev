# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       : cover_taskdata
# Describe   : 说明描述
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2023/3/20__20:40
# -------------------------------------------------------

FIELDS=['project','due_date','sg_custom_totalrealwork','entity.Asset.sg_asset_type','entity.Shot.sg_sequence.Sequence.code','entity','content','start_date','sg_status_list','est_in_mins','step','task_assignees']

import database.shotgun.core.sg_analysis as sg_config

def cover_taskdata(taskdata):
    _taskid=taskdata.task_id
    _sg=sg_config.Config().login()

    if _taskid:
        filters=[['id', 'is', _taskid]]
        return _sg.find("Task", filters, FIELDS)


# if __name__ == '__main__':
#     import method.shotgun.get_task as get_task
#     file='M:/projects/x3/work/shots/CutScene_ML_C10S1/CutScene_ML_C10S1_S01_P01/cts/mobu/CutScene_ML_C10S1_S01_P01.cts_rough.v001.fbx'
#     taskdata=get_task.TaskInfo(file, 'X3', 'motionbuilder', 'version',is_lastversion=False)
#     print(cover_taskdata(taskdata))

