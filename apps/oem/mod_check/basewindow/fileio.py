# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       : fileio
# Describe   : 说明描述
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2022/5/24__10:15
# -------------------------------------------------------
import os, io

__all__ = ["read", "write"]


def read(path, rtype="r"):
	'''读取json文件信息
	参数：
		path-->路径
		rtype-->文件读取方式
	'''
	if not os.path.exists(path):
		return None
	with open(path, rtype) as f:
		_data = f.read()
		try:
			_data = _data.decode('utf-8')
		except:
			pass
		f.close()
	return _data


def write(info, path, wtype="w"):
	'''写入json，txt,log等文件信息
	参数：
		info-->信息
		path-->路径
		wtype-->文件写入方式,"w"覆盖，“a”添加模式
	'''
	_path = os.path.dirname(path)
	if not os.path.exists(_path):
		os.makedirs(_path)
	with io.open(path, wtype, encoding='utf-8') as f:
		f.write(info)
		f.close()
	return True


# if __name__ == '__main__':
# 	path = r'D:\temp_info\publishInfo\publish_2023-09-07_17-09-09.bat'
# 	data = read(r'D:\temp_info\publishInfo\publish_2023-09-07_17-09-09.bat')
# 	print type(data)
# 	write(u'test', path, wtype="w")


