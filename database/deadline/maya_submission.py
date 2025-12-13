# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       : maya_submission
# Describe   : 说明描述
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2024/1/15__19:21
# -------------------------------------------------------
import database.deadline.deadline_batch as deadline_batch

def maya_submission(file_path, cmd,job_name='',maya_version="2018"):
    return deadline_batch.runDeadline(maya_version=maya_version,
                                      plugin_name="MayaBatch",
                                      JobName=job_name,
                                      PollName='pipline',
                                      GroupName="maya",
                                      FileName=file_path,
                                      Priority="80",
                                      command=cmd
                                      )
