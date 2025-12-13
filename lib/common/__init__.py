# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       : __init__.py
# Describe   : 说明描述
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2022/5/5__21:26
# -------------------------------------------------------
import os


def getRootPath():
	rootPath = os.path.dirname(os.path.abspath(__file__)).split('lib')[0].replace('\\', '/')
	return rootPath

def ico_path():
	return os.path.join(root_path(), "ico")


def apps_path():
	'''默认app文件夹路径
	'''
	return os.path.join(root_path(), "apps")


def database_path():
	'''
	默认数据库路径
	:return:
	'''
	return os.path.join(root_path(), "db")


def root_path():
	'''lib根目录
	'''
	return os.path.dirname(os.path.abspath(__file__).split('lib')[0])


def config_path():
	'''
	环境配置路径
	:return:
	'''
	return os.path.join(root_path(), "conf")


def publish_config_path():
	u"""
	publish 配置基本路径
	:return:
	"""
	return os.path.join(root_path(), "apps/publish/config")


def workfile_config_path():
	"""
	workfile配置路徑
	"""
	return os.path.join(root_path(), "apps/workfile/config")


def appdata_path():
	'''用户配置信息文件夹路径
	'''
	import getpass
	_path = os.getenv("APPDATA")
	# _user = getpass.getuser()

	_path_ele = _path.split(os.sep)
	return os.sep.join(_path_ele)


def pipedata_path():
	'''pipeline用户配置信息文件夹路径
	'''
	return os.path.join(appdata_path(), "ftpipeline")


# if __name__ == '__main__':
# 	print(ico_path())
