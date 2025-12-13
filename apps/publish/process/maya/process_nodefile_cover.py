# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       : process_nodefile_cover
# Describe   : 主要用用模型贴图刷新到绑定的work 和publish路径
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2022/12/19__19:21
# -------------------------------------------------------
import os

import method.maya.common.collect_nodefile as collect_nodefile

reload(collect_nodefile)

import method.shotgun.get_task as get_task
import lib.maya.analysis.analyze_data as analyze_data

COVERTASK = {'fight_mdl': ['drama_rig', 'rbf'], 'drama_mdl': ['drama_rig', 'rbf'], 'ue_mdl': ['ue_rig']}
COVERTYPE = ["file", "aiImage", "dx11Shader"]


class ProcessCoverNodeFile(object):
    def __init__(self, _TaskData, _project_name='X3', _dcc='maya'):
        u"""
        主要用于模型文件刷新绑定文件的贴图,材质等
        @param _taskdata: 任务信息
        """
        super(ProcessCoverNodeFile, self).__init__()

        self._TaskData = _TaskData
        self._entity_name = self._TaskData.entity_name
        self._asset_type = self._TaskData.asset_type
        self._task_name = self._TaskData.task_name
        self._project_name = _project_name
        self._dcc = _dcc
        self._data = analyze_data.AnalyData().data
        self._fileattr_dict = self._data["FILE_ATTR"]
        self._filepath_dict = self._data["FILE_ATTR_PATH"]
        if self._task_name not in ['fight_mdl', 'drama_mdl', 'ue_mdl']:
            return

    def cover_mod_files(self):
        u"""
        将模型文件贴图及dx11 shader 刷到绑定路径(work,publish)
        :return:
        """
        for k, v in COVERTASK.items():
            if self._task_name == k and v:
                for _task in v:
                    self._cover_tex_files(_task, COVERTYPE)

    def _get_taskdata(self, _task_name):
        u"""
        获取相同资产不同任务的任务信息
        @param _task_name: 任务名
        @return:
        """
        try:
            return get_task.TaskInfo('{}.{}.v001.ma'.format(self._entity_name, _task_name), self._project_name,
                                     self._dcc,
                                     tag='publish', is_lastversion=False)
        except:
            return False

    def _cover_tex_files(self, _task_name, _filtyps=[]):
        u"""
        转换贴图及dx材质球文件
        :param _filtyps: 需要转换的文件类型列表
        :return:
        """
        _dict = {}
        _work_dict={}
        _pub_dict={}
        _dir_dict = self._get_task_dir(_task_name)
        _work_data_dir = ''
        _pub_data_dir = ''
        if _dir_dict and 'work_data_dir' in _dir_dict:
            _work_data_dir = _dir_dict['work_data_dir']
        if _dir_dict and 'publish_data_dir' in _dir_dict:
            _pub_data_dir = _dir_dict['publish_data_dir']

        # 转换work
        if _work_data_dir:
            _work_dict = self._cover_filetype(_work_data_dir, _filtyps)
        # 复制到publish路径
        if _pub_data_dir:
            _pub_dict = self._cover_filetype(_pub_data_dir, _filtyps)

    def _cover_filetype(self, _dir='', _filtyps=[]):
        u"""
        转换
        :param _dir: 基础路径
        :param _filtyps: 需要转换的文件类型列表
        :return:
        """
        _dict={}
        if _dir and _filtyps:
            for _filetype in _filtyps:
                _path = '{}/{}'.format(_dir, self._filepath_dict[_filetype])
                if _path and os.path.exists(_path):
                    _file_dict= collect_nodefile.CollectNodeFile(targepath=_path, nodetypelist=[_filetype]).collect_nodefiles(_set=False)
                    if _file_dict:
                        _dict[ _filetype]=_file_dict
        return _dict


    def _get_task_dir(self, _task_name):
        u"""
        获取任务的路径(work,publish)
        @param _task_name: 任务名
        @return:
        """

        _dict = {}
        _taskdata = self._get_taskdata(_task_name)
        if _taskdata and _taskdata != False:
            _work_dir = _taskdata.work_data_dir
            _publish_dir = _taskdata.publish_data_dir
            if _work_dir :
                _dict['work_data_dir'] = _work_dir
            if _publish_dir:
                _dict['publish_data_dir'] = _publish_dir
        return _dict


if __name__ == '__main__':
    _filename = cmds.file(q=1, exn=1)
    _taskdata = get_task.TaskInfo(_filename, 'X3', 'maya', tag='publish', is_lastversion=False)
    _handle = ProcessCoverNodeFile(_taskdata)
    _handle.cover_mod_files()
