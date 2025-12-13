# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       : process_nodefile
# Describe   : 打包节点文件(例如贴图，abc,ass等)
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2022/7/6__10:15
# -------------------------------------------------------
import lib.maya.analysis.analyze_data as analyze_data
import os

import method.maya.common.collect_nodefile as collect_nodefile

reload(collect_nodefile)
import apps.publish.process.process_package as process_package


class ProcessNodeFile(object):
    def __init__(self, _taskdata):
        """
        收集节点文件
        """
        self.taskdata = _taskdata
        self.publish_data_dir = self.taskdata.publish_data_dir
        self._data = analyze_data.AnalyData().get_data_info()

    def _get_publish_dir(self, nodetypes=[]):
        u"""
        文件work文件夹路径
        nodetypes:节点类型列表
        """
        _dict = {}
        if self.publish_data_dir:
            for _nodetyp in nodetypes:
                _dir = self._data["FILE_ATTR_PATH"][_nodetyp]
                if self.publish_data_dir and _dir:
                    _node_dir = os.path.join(self.publish_data_dir, _dir).replace('\\', '/')
                    _dict[_nodetyp] = _node_dir
        return _dict

    def collect_work_nodefile(self, nodetyplist=[]):
        u"""
        收集文件到work
        """
        if nodetyplist:
            nodetypes = nodetyplist
        else:
            nodetypes = self._data["FILE_ATTR"].keys()
        work_dir_dict = self._get_publish_dir(nodetypes)
        source_targe_dict = {}

        if work_dir_dict:
            for k, v in work_dir_dict.items():
                _collect_dict = collect_nodefile.CollectNodeFile(targepath=v,nodetypelist=[k]).collect_nodefiles(_copy=False)
                if _collect_dict:
                    source_targe_dict.update(_collect_dict)


        if source_targe_dict:
            return {'tex': process_package.datapack_dict(source_targe_dict)}
