# -*- coding: utf-8 -*-#
# Python       : python 2.7.16
# -------------------------------------------------------------------------------
# NAME         : get_task
# Describe     : shotgun 信息获取方法
# Version      : v0.01
# Author       : linhuan
# Email        : hanhong@papegames.net
# DateTime     : 2022/5/22__19:41
# -------------------------------------------------------------------------------
# -------------------------------------------------------------------------------
# example:
# 
# -------------------------------------------------------------------------------
from method.shotgun.task_data import TaskData

import database.shotgun.core.sg_project as _sg_project

import database.shotgun.core.sg_version as _sg_version

import method.shotgun.filename_analysis as _filename_analyze
try:
    reload(_filename_analyze)
except:
    pass

import re
import os


class TaskInfo(TaskData):
    def __init__(self, sg,filename, project, dcc, tag, thumbnail_down=False, is_lastversion=True,ui=False):
        '''
		:param filename: 文件名
		:param dcc: 软件名
		:param tag: 目前标记 publish,version 针对的templateas.yml文件
		:param thumbnail_down: 缩量图是否需要下载读取，默认是不下载读取的
		:param is_lastversion: 是否初始化版本等相关信息，影响到的属性有_last_version，des_path，des_name，des_dir，last_version_num，last_des
		'''
        super(TaskData, self).__init__()
        self.sg_login = sg

        self.filename = filename
        self.task_launch_soft = dcc
        self.project_name = project
        self.tag = tag
        self.thumbnail_down = thumbnail_down
        self.ui=ui


        self._analyzehandle = _filename_analyze.FilenameAnalyze(self.sg_login, filename=self.filename,
                                                                project=self.project_name,
                                                                dcc=self.task_launch_soft, tag=self.tag,ui=self.ui)

        self.project_id = self._get_projectID()
        self._project_info = self._get_project_info(self.project_id)
        # self.project_type = self._project_info['sg_type']
        self.entity_data = self._analyzehandle.get_tasktype_id()
        self.entity_name = self.entity_data['entity_name']
        self.entity_type = self.entity_data['entity_type']
        self.entity_id=self.entity_data['entity_id']
        self.task_data = self._analyzehandle.get_task()
        self.task_name = self.task_data['task_name']
        self.task_id=self.task_data['task_id']
        self.task_type=self.task_data['task_type']
        self.asset_type = self._analyzehandle.get_asset_type()
        self.step_name = self._analyzehandle.get_step()

        self.shot_name = self._analyzehandle.get_shot()
        self.current_user = self._analyzehandle.current_user_name
        self.current_user_data= self._analyzehandle.get_current_user_data()

        self.sequence_name = self._analyzehandle.get_seqence()

        self.project_dir = self._analyzehandle.get_projectdir()

        self.project_soft = self._analyzehandle.get_project_soft()

        self.work_dir = self._analyzehandle.get_workdir()

        self.work_data_dir = self._analyzehandle.get_workdata_dir()

        self.publish_data_dir = self._analyzehandle.get_publishdata_dir()

        self.publish_thubnail = self._analyzehandle.get_thubnail_publish()

        self.publish_version_dir = self._analyzehandle.get_publish_version()

        self.publish_dir=self._analyzehandle.get_publishdir()

        if is_lastversion:
            self._last_version = self._analyzehandle.last_version()

            self.des_path = self._analyzehandle.get_despath()
            self.des_name = os.path.basename(self.des_path)
            self.des_dir = os.path.dirname(self.des_path)
            self.last_version_num = self._analyzehandle.last_version_num()
            self.last_des = self._get_last_des()
            self.last_version_id = self._analyzehandle._last_version_id()
            self.task_thumbnail = self._get_taskthumbnail()
            self.work_path = self._analyzehandle.get_workpath()

    def _get_taskthumbnail(self):
        '''
		获取任务的缩量图，其实是从shotgun上下载最后一个版本的缩量图
		:return: 路径
		'''
        if self.last_version_id:
            return _sg_version.download_version_thumbnail(self.sg_login, self.last_version_id)
        else:
            return ''

    def _get_projectID(self):
        '''
		获取项目ID
		:return:
		'''
        _projectIDs = _sg_project.get_project_projectID(self.sg_login, self.project_name)
        if _projectIDs:
            return _projectIDs[0]['id']
        else:
            raise Exception(u'shotgun上没发现该项目'.encode('gbk'))

    def _get_project_info(self, project_id):
        return _sg_project.select_project_project(self.sg_login, project_id,
                                                  ['name', 'sg_type'])

    def _get_last_des(self):
        '''
		获取最新版本的路径
		:return: 字符串
		'''
        _version = 'v{}'.format(self._last_version)
        pattern = re.compile('v\d+', re.S)
        return re.sub(pattern, _version, self.des_path)

    def _replace_info(self, _info, _ver,_str):
        u"""
        变量转换基础函数
        Args:
            _info: 需要转换的信息
            _ver: 需要转换的变亮
            _str：转换的string

        Returns:

        """
        if not _info:
            return
        if isinstance(_info,str):
            return (_info.replace(_ver,_str))
        elif isinstance(_info,dict):
            return eval(str(_info).replace(_ver,_str))

if __name__ == '__main__':
    filename = 'FY_BODY.drama_mdl.v001.png'
    project = 'X3'
    dcc = 'maya'
    tag = 'publish'
    _task_handle = TaskInfo(filename, project, dcc, tag, is_lastversion=True)
    print(filename)
    print(_task_handle.last_version_num)
    print(_task_handle.entity_name)

# # 	#
# # 	#
# # 	# 	print(_task_handle.last_version_num)
# # 	# 	print(_task_handle.entity_name)
# # 	# 	print(_task_handle.sequence_name)
# # 	# 	print(_task_handle.task_name)
# # 	# 	print(_task_handle.task_type)
# # 	# 	print(_task_handle.step_name)
# # 	# 	print(_task_handle.project_type)
# # 	# 	print(_task_handle.task_thumbnail)
# # 	# 	print(_task_handle.des_dir)
# # 	# 	print(_task_handle._get_last_des())
# # 	# 	print(_task_handle._project_info)
# # 	# 	print(_task_handle.project_type)
# #
# 	filename = 'ST001S.drama_rig.v001.ma'
# 	project = 'X3_test04'
# 	dcc = 'maya'
# 	tag = 'publish'
# 	_task_handle = TaskInfo(filename, project, dcc, tag, is_lastversion=1)
# 	print _task_handle.current_user_name
# 	print _task_handle.step_name
# 	print _task_handle.work_path
# 	print _task_handle.work_dir
# 	print _task_handle.work_data_dir
# 	print _task_handle.publish_data_dir
# 	print _task_handle.project_soft

# _shot_handle=TaskInfo(filename, project, dcc, tag, is_lastversion=False)

# print(_shot_handle.last_version_num)
# print(_shot_handle.entity_name)
# print(_shot_handle.sequence_name)
# print(_shot_handle.task_name)
# print(_shot_handle.task_type)
# print(_shot_handle.step_name)
# print(_shot_handle.project_type)
# print(_shot_handle.task_thumbnail)
# print(_shot_handle.des_dir)
# print(_shot_handle._get_last_des())
# print(_shot_handle._project_info)
# print(_shot_handle.project_type)

# 获得资产信息

# cc = TaskInfo('test.drama_rig.v001.ma','X3_test04','maya','left')
# print(cc.project_dir)
