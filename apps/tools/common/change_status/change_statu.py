# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       : change_status
# Describe   : 修改当前文件ip
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2022/11/9__19:05
# -------------------------------------------------------
import method.shotgun.get_task as get_task
reload(get_task)
import database.shotgun.core.sg_analysis as sg_analysis
import database.shotgun.core.sg_task as sg_task
import database.shotgun.fun.task_authentication as task_authentication
from PySide2.QtWidgets import *
def change_status(_filename, _data={'sg_status_list': 'ip'}, _project='X3', _dcc='maya', _tag='version',ui=True):
    u"""
    更新状态
    :param _filename:
    :param project:
    :param dcc:
    :param tag:
    :return:
    """
    sg = sg_analysis.Config().login()
    _Taskdata = get_taskdata(_filename, _project, _dcc, _tag)
    _task_id = get_task_id(_Taskdata)
    _user_id=_Taskdata.current_user_data['id']
    _aut=task_authentication.TaskAuth(_task_id,_user_id).authentication


    # 更新任务状态
    if _aut and _aut==True:
        return _change_task_status(sg, _task_id, _data)
    else:
        if ui == True:
            messagebox_error(u'这个任务没有分配给你,无法修改任务状态,请联系leader或PM')
        raise Exception("This task is not assigned to you, please contact leader or PM")

def messagebox_error(x=""):
    u"""
    弹出
    """
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Information)
    msg.setText(u"{}".format(x))
    msg.setWindowTitle(u"报错信息")
    msg.exec_()


def get_taskdata(_filename, project='X3', dcc='maya', tag='version', is_lastversion=False):
    u"""
    解板获得taskdata
    :param _filename:文件名
    :param project:项目名
    :param dcc:dcc 软件
    :param tag:
    :param is_lastversion:True 时
    :return:
    """
    return get_task.TaskInfo(_filename, project, dcc, tag, is_lastversion=is_lastversion)


def get_task_id(_taskdata):
    u"""
    获取任务信息
    :param _taskdata: task 任务信息类
    :return:
    """
    return _taskdata.task_id


def _change_task_status(sg, _entity_id, _data):
    u"""
    修改任务状态
    :param sg:
    :param _entity_type:
    :param _entity_id:
    :return:
    """
    return sg_task.upadata_task(sg, _entity_id, data=_data)


# if __name__ == '__main__':
#     _filename = 'TDTEST_ROLEACCE.drama_rig.v002.ma'
#     change_status(_filename)
