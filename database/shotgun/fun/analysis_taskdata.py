# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       : analysis_taskdata
# Describe   : 说明描述
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2022/11/17__15:34
# -------------------------------------------------------
from method.shotgun import get_task


class AnalysisTaskData(object):
    def __init__(self, project='X3', entity_name='', task_name='', dcc='', tag='', is_lastversion=False):
        super(AnalysisTaskData, self).__init__()
        self._project = project
        # 实体名,这里指(Asset Shot 类型的实体名)
        self._entity_name = entity_name
        # 任务名
        self._task_name = task_name
        #
        self._dcc = dcc
        #
        self._tag = tag
        #
        self._is_lastversion = is_lastversion
        # 虚拟文件名
        _finelname = '{}.{}.v001.ma'.format(self._entity_name, self._task_name)
        #
        self.TaskData = get_task.TaskInfo(_finelname, project, dcc, tag, is_lastversion=False)
