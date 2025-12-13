# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       : check_face_joins
# Describe   : 检测绑定文件面部骨骼
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2023/4/21__11:27
# -------------------------------------------------------
import lib.common.loginfo as info
import maya.cmds as cmds
import lib.maya.analysis.analyze_config as analyze_config

EXJOIT='jawJoint'
class Check(object):
    """
    """

    def __init__(self, TaskData):
        """
        实例初始化
        """
        super(Check, self).__init__()
        self.entity_name = TaskData.entity_name
        self.assettype = TaskData.asset_type
        self.task_name = TaskData.task_name

        self.tooltip = u'已检测面部骨骼'

    def checkinfo(self):
        """
        显示检查信息
        :return:
        """
        _error = self.run()
        _error_list = []
        if _error:
            for k,v in _error.items():
                _error_list.append(k)
                _error_list.extend(v)
            return False, info.displayErrorInfo(title=self.tooltip, objList=_error_list)
        else:
            return True, info.displayInfo(title=self.tooltip)

    def run(self):
        _data = self._get_data
        if _data:
            for k, v in _data.items():
                if self.assettype and self.assettype.lower() == k and "face_joins" in v and v["face_joins"] and self.task_name.lower() in v[
                    "task_name"] and  "PL_Body" not in self.entity_name and (self.assettype.lower() not in ['npc'] or (self.assettype.lower() in ['npc'] and cmds.ls(EXJOIT))):
                    return self._judge(v["face_joins"])

    def _judge(self, _head_joins):
        """
        判断是否存在
        :param _head_joins:
        :return:
        """
        error = {}
        _error_exist = []
        _error_count = []
        _error_type = []
        if not _head_joins:
            return
        for _join in _head_joins:
            if not cmds.objExists(_join):
                _error_exist.append(_join)
            else:
                if len(cmds.ls(_join)) != 1:
                    _error_count.append(_join)
                else:
                    if cmds.nodeType(_join) != "joint":
                        _error_type.append(_join)
        if _error_exist:
            error[u"缺少以下骨骼,请检查"] = _error_exist
        if _error_count:
            error[u"以下节点有重名,请检查"] = _error_count
        if _error_type:
            error[u"以下节点类型不是joint,请检查"] = _error_type
        return error

    @property
    def _get_data(self):
        """
        获取数据
        :return:
        """
        return self._cover_data(analyze_config.AnalyConfigBase(configfile="head_joins.json", dcc="maya").data)

    def _cover_data(self, data):
        """
        转换数据s
        :param data:
        :return:
        """
        return eval(str(data).replace("{entity_name}", self.entity_name).replace("{ad}",self.entity_name.split("_")[0]))

if __name__ == '__main__':
    import method.shotgun.get_task as get_task
    _file=cmds.file(q=True, exn=True)

    taskdata = get_task.TaskInfo(_file, 'X3', 'maya', 'version')
    _handle = Check(taskdata)
    print(_handle.checkinfo())
