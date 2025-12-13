# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       : yamlio.py
# Describe   : 说明描述
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2022/5/20__21:11
# -------------------------------------------------------
import os
import yaml

__all__ = ["read", "write", "read2", "write2"]

'''
yml读写集合
ruamel.yml对比yaml可以精简文本显示
'''


def read(path, rtype="r"):
    '''读取yml文件信息
    参数：
        path-->路径
        rtype-->文件读取方式
    '''
    if not os.path.exists(path):
        return None
    with open(path, rtype) as f:
        # 版本变化时再改回注释版本
        # _data = yaml.load(f,Loader = yaml.FullLoader)
        try:
            _data = yaml.load(f, Loader=yaml.FullLoader)
        except:
            _data = yaml.load(f)
        f.close()
    return _data


def write(info, path, wtype="w"):
    '''写入yml文件信息
    参数：
        info-->信息
        path-->路径
        wtype-->文件写入方式
    '''
    _path = os.path.dirname(path)
    if not os.path.exists(_path):
        os.makedirs(_path)
    with open(path, wtype) as f:
        yaml.dump(info, f, indent=4, encoding="utf-8", default_flow_style=False)
        f.close()
    return True


def read2(path, rtype="r"):
    '''使用ruamel.yaml读取yml文件信息
    参数：
        path-->路径
        rtype-->文件读取方式
    '''
    import ruamel.yaml as yaml2
    if not os.path.exists(path):
        return None
    with open(path, rtype) as f:
        _data = yaml2.load(f, Loader=yaml2.Loader)
        f.close()
    return _data


def write2(info, path, wtype="w"):
    '''使用ruamel.yaml写入yml文件信息
    参数：
        info-->信息
        path-->路径
        wtype-->文件写入方式
    '''
    import ruamel.yaml as yaml2
    _path = os.path.dirname(path)
    if not os.path.exists(_path):
        os.makedirs(_path)
    with open(path, wtype) as f:
        yaml2.dump(info, f, indent=4, encoding="utf-8", Dumper=yaml2.RoundTripDumper)
        f.close()
    return True