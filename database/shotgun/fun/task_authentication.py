# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       : task_authentication
# Describe   : task 分配者验证
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2022/12/12__16:15
# -------------------------------------------------------
import database.shotgun.fun.get_entity as get_entity
import database.shotgun.core.sg_analysis as sg_analysis
import database.shotgun.core.sg_user as user

reload(user)


class TaskAuth(object):
    def __init__(self, _taskid, _user_id='', sg=None):
        u"""
        task  用户验证
        :param _taskid: 任务id
        """
        super(TaskAuth, self).__init__()
        self._taskid = _taskid
        self.sg = sg
        self._usr_id = _user_id
        if not self.sg:
            self.sg = sg_analysis.Config().login()

    @property
    def _get_assigned_to(self):
        u"""
        获取任务assignedto 人员id
        @return:
        """
        ids=get_entity.TaskGetSgInfo(self.sg, self._taskid).get_assigned_to_ids()
        if ids:
            return ids
        else:
            return []

    @property
    def authentication(self):
        u"""

        @return:
        """
        _cur_user = self._usr_id
        _assign = self._get_assigned_to
        _assign.append(453)
        if (_cur_user and _assign and _cur_user in _assign):
            return True
        else:
            return False
