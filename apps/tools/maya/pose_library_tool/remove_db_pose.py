# -*- coding: utf-8 -*-
# author: linhuan
# file: remove_db_pose.py
# time: 2025/12/11 18:25
# description:
import os.path

from apps.tools.maya.pose_library_tool import pose_lib_fun

reload(pose_lib_fun)
from apps.publish.ui.message.messagebox import msgview
import time


def remove_db_pose(pose_name, ui=True):
    result = msgview(u'请确定要删除{}DBPose资产'.format(pose_name), 1, 1)
    if result == 0:
        return
    json_file = '{}/db_pose/{}.json'.format(pose_lib_fun.get_lib_root_data_path(), pose_name)
    if os.path.exists(json_file):
        try:
            os.remove(json_file)
            time.sleep(1)
            if ui:
                message = '删除DBPose资产成功,请检查'
                msgview(message, 2)
        except Exception as e:
            if ui:
                message = '删除DBPose资产失败,请检查:{}'.format(e)
                msgview(message, 0)
