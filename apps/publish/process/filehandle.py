# -*- coding: utf-8 -*-#
# Python       : python 2.7.16
#-------------------------------------------------------------------------------
# NAME         : filehandle
# Describe     : 获取文件路径
# Version      : v0.01
# Author       : linhuan
# Email        : hanhong@papegames.net
# DateTime     : 2022/6/10__15:44
#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
# example:
# 
#-------------------------------------------------------------------------------


import re,os

import method.maya.common.project_info as projectinfo

def get_publishfilepath(TaskData):
	'''
	获取publish服务器文件路径
	:param TaskData:
	:return:
	'''
	return TaskData.des_path

def get_backpublishpath(TaskData):
	u"""
	获取备份的publish文件路径
	Args:
		TaskData:

	Returns:

	"""
	_des_path=TaskData.des_path
	_path,_basefile=os.path.split(_des_path)
	return '{}/back/{}'.format(_path,_basefile)

def get_backpublishdir(TaskData):
	_des_path = TaskData.des_path
	_path, _basefile = os.path.split(_des_path)
	return '{}/back'.format(_path)

def get_assetlocalMastername(TaskData):
	'''
	获取资产的master文件名  按固定规则解析的，不能重用
	:param TaskData:
	:return: ca001001xiongda.ma
	'''
	return TaskData.entity_name + os.path.splitext(TaskData.filename)[-1]


def get_shotlocalMastername(TaskData):
	'''
	获取资产的master文件名  按固定规则解析的，不能重用
	:param TaskData:
	:return: ep001_seq001_sc001.ani_animation.mb
	'''
	_name = remove_version(TaskData.filename)
	return re.sub(_name.split('.')[0] + '.', '', _name)
	





def get_loacalfile(TaskData,filename,addpath = ''):
	'''
	获取存储到本地temp下的文件路径
	:param TaskData:
	:param filename: 文件名
	:param addpath: 补充路径 如 '/data/fbx'
	:return:返回本地的路径
	'''
	_tempdir = 'D:/Info_Temp'
	
	_project = TaskData.project_name
	_dcc = TaskData.task_launch_soft
	_task_type = TaskData.task_type
	_entity_name = TaskData.entity_name
	_task_name = TaskData.task_name
	_asset_type = TaskData.asset_type
	_task_step = TaskData.task_type
	_shot_name = TaskData.shot_name
	_sequence_name = TaskData.sequence_name
	_episode_name = TaskData.episode_name
	# 本地基础路径
	if _task_type == 'asset':
		_tempdir = '{}asset/{}/{}/{}/{}/{}/work{}/'.format(projectinfo.ProjectInfo(_project).workpath(),_asset_type,
		                                                   _entity_name,_task_step,_task_name,_dcc,addpath)
			# projectinfo.ProjectInfo(_project).workpath() + 'asset/' + _asset_type + '/' + _entity_name + '/' + \
		    #        _task_step + '/' + _task_name + '/' + _dcc + '/work' + addpath + '/'
	if _task_type == 'shot':
		_tempdir = '{}shot/{}/{}/{}/{}/{}/{}/work{}/'.format(projectinfo.ProjectInfo(_project).workpath(),
		                                                     _episode_name,_sequence_name,_entity_name,_task_step,
		                                                     _task_name,_dcc,addpath)
			# projectinfo.ProjectInfo(_project).workpath() + 'shot/' + _episode_name + '/' + \
		    #        _sequence_name + '/' + _entity_name + '/' + _task_step + '/' + _task_name + '/' + _dcc + '/work' + addpath + '/'
	_tempfile = r"{}{}".format(_tempdir, filename)
	if not os.path.exists(_tempdir):
		os.makedirs(_tempdir)
	return _tempfile




def remove_version(str=''):
	'''
	移除版本号
	:param str: 字符串中带'.v005'版本字样的字符串
	:return: 移除版本号的字符串
	'''
	_versionsign = re.findall('.v\w+', str)
	return str.replace(_versionsign[-1], '') if _versionsign else str


def insert_version(filename, insert_str):
	'''
	在版本号前插入字符串
	:param filename:带版本号的文件名
	:param insert_str:插入的字符串
	:return: 插入后的字符串
	'''
	_startIndexs = []
	_versions = re.finditer('.v\w+', filename)
	if _versions:
		for i in _versions:
			_startIndexs.append(i.start())
	if _startIndexs:
		str_list = list(filename)
		str_list.insert(_startIndexs[0], insert_str)
		return ''.join(str_list)
	else:
		return None


def replace_version(filename, repalce_str):
	'''
	替换版本号
	:param filename:带版本号的文件名
	:param repalce_str:替换的字符串
	:return:替换后的字符串
	'''
	_versions = re.findall('.v\w+', filename)
	if _versions:
		new = filename.replace(_versions[0], repalce_str)
		return new
	else:
		return None


# if __name__ == '__main__':
# 	import python.code_lib.get_task as get_task
	# temp_task_data = get_task.TaskInfo('asset.ca001008.srf_hig.v001.ma', 'xcm_test', 'maya', 'version')
	# print(get_loacalfile(temp_task_data, 'aaa.json', '/data/fbx'))
	# print(get_publishfilepath(temp_task_data))
