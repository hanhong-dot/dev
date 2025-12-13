# -*- coding: utf-8 -*-#
# Python       : python 2.7.16
# -------------------------------------------------------------------------------
# NAME         : dir
# Describe     : 说明描述
# Version      : v0.01
# Author       : linhuan
# Email        : hanhong@papegames.net
# DateTime     : 2022/5/25__10:21
# -------------------------------------------------------------------------------
# -------------------------------------------------------------------------------
# example:
# 
# -------------------------------------------------------------------------------
import os
import re


def get_laster_file_base(_dir, _suffixs, _basename):
    u"""
    获取最新版本文件
    :param _dir:文件夹
    :parm _suffix：后缀
    """
    if _dir and os.path.exists(_dir):
        _filelist = [_i for _i in os.listdir(_dir) if
                     (os.path.splitext(_i)[-1] and os.path.splitext(_i)[-1] in _suffixs) and os.path.basename(
                         _i) == _basename]
        if _filelist:
            _lastfile = sorted(_filelist)[-1]
            if _lastfile:
                return '{}/{}'.format(_dir, _lastfile)

def get_files_by_basename_exr_laster(_dir, _suffixs, _basename,version_num=4):
    u"""
    获取除最新版本的所有文件
    """
    _file_list=[]
    if _dir and os.path.exists(_dir):
        _filelist = [_i for _i in os.listdir(_dir) if
                     (os.path.splitext(_i)[-1] and os.path.splitext(_i)[-1] in _suffixs) and _basename in _i and len(_i.split('.'))==4]
        if _filelist:
            _filelist=list(set(_filelist))
            _filelist=sorted(_filelist)
            if len(_filelist)>version_num:
                _filelist=_filelist[0:len(_filelist)-version_num]
                for file in _filelist:
                    path=os.path.join(_dir,file).replace('\\','/')
                    if os.path.exists(path):
                        _file_list.append(path)
    return _file_list






def get_laster_file(_dir, _suffixs):
    u"""
    获取最新版本文件
    :param _dir:文件夹
    :parm _suffix：后缀
    """
    if _dir and os.path.exists(_dir):
        _filelist = [_i for _i in os.listdir(_dir) if
                     (os.path.splitext(_i)[-1] and os.path.splitext(_i)[-1] in _suffixs)]
        if _filelist:
            _lastfile = sorted(_filelist)[-1]
            if _lastfile:
                return '{}/{}'.format(_dir, _lastfile)


def get_files(_dir, _suffixs):
    _files = []
    if _dir and os.path.exists(_dir):
        _filelist = [_i for _i in os.listdir(_dir) if
                     (os.path.splitext(_i)[-1] and os.path.splitext(_i)[-1] in _suffixs)]
        if _filelist:
            for _file in _filelist:
                _files.append('{}/{}'.format(_dir, _file))
    return _files


def set_localtemppath(sub_dir='Info_Temp/'):
    '''
    在本地d盘（没有d盘，则是e盘，f盘，c盘）创建文件夹
    :param sub_dir: 子文件夹名
    :return:成功返回创建的路径，否则返回False
    '''
    _root = ''
    if os.path.exists('D:/'):
        _root = 'D:/'
    elif os.path.exists('E:/'):
        _root = 'E:/'
    elif os.path.exists('F:/'):
        _root = 'F:/'
    elif os.path.exists('C:/'):
        _root = 'C:/'
    if not _root:
        return False
    _tempPath = _root + sub_dir
    if not os.path.exists(_tempPath):
        try:
            os.makedirs(_tempPath)
        except:
            return False
    return _tempPath


def getip(driver):
    '''
    通过注册表查找映射盘路径
    :param driver: 映射盘符
    :return: 地址
    '''
    import _winreg
    ip = ''
    machineREG = r'Network'
    key = _winreg.OpenKey(_winreg.HKEY_CURRENT_USER, machineREG)

    for i in range(_winreg.QueryInfoKey(key)[0]):
        getDriver = _winreg.EnumKey(key, i)
        if str(driver).upper() == getDriver.upper():
            programREG = machineREG + r'\\' + getDriver

            programKey = _winreg.OpenKey(_winreg.HKEY_CURRENT_USER, programREG)
            ip = _winreg.QueryValueEx(programKey, "RemotePath")[0]
    if '//' in ip:
        ip = ip.replace('//', "\\\\")
    if '/' in ip:
        ip = ip.replace('/', '\\')
    return ip


def getlocaldisk():
    '''
    获取本地盘符
    :return:字符串
    '''
    local_disk = os.popen('wmic logicaldisk where "drivetype=3" get name').read()
    if not local_disk:
        local_disk = 'C: D: E: F:'
    return local_disk


def _get_ralation_ipdriver(ipdrivers, path):
    '''
    读取project_set.json的配置文件中的relation_ipdriver来获取ip和映射盘符的关系
    :param project: 项目名
    :param path:ip路径或者映射盘符
    :return:如果参数是ip路径则返回映射盘符，如果参数是映射盘符则返回ip路径
    '''
    if '/' in path:
        path = path.replace('/', '\\')
    for obj in ipdrivers:
        for k, v in obj.items():
            if k == path:
                return v
            elif v == path:
                return k


def get_localtemppath(add_path):
    '''
    获取本地Info_temp所在盘符的路径
    :param add_path:添加的路径
    :return:返回整个路径
    '''
    if os.path.exists('D:\\'):
        localInfoPath = 'D:/temp_info/' + add_path
    elif os.path.exists('E:\\'):
        localInfoPath = 'E:/temp_info/' + add_path
    elif os.path.exists('F:\\'):
        localInfoPath = 'F:/temp_info/' + add_path
    elif os.path.exists('C:\\'):
        localInfoPath = 'C:/temp_info/' + add_path
    else:
        raise Exception(u'本地C,D,E,F盘都没有')
    return localInfoPath

# if __name__ == '__main__':
#     _dir=r'M:\projects\x3\work\assets\body\FY_BODY\mod\maya'
#     _suffixs=['.ma']
#     _basename='FY_BODY.drama_mdl'


