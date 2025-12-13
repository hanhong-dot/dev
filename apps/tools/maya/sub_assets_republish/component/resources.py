# -*- coding: utf-8 -*-#
# Python       : python2 2.7.16
# -------------------------------------------------------------------------------
# NAME         : __init__
# Describe     : 默认路径的一些方法
# Version      : v0.01
# Author       : linhuan
# Email        : hanhong@papegames.net
# DateTime     : 2020/9/18__19:40
# -------------------------------------------------------------------------------
# -------------------------------------------------------------------------------
# example:
#
# -------------------------------------------------------------------------------

import os

__all__ = ["Resources", "get"]


class Resources(object):
    '''config文件夹获取集
    '''

    def __init__(self, path=None):
        if not path:
            self._path = ui_path() + '/resources'
        else:
            self._path = path
        self._sep = os.sep

    def get(self, *args):
        '''获取路径
        '''
        path = os.path.join(self._path, *args)
        return self.repath(path)

    def repath(self, path):
        '''统一分隔符
        '''
        return path.replace("/", self._sep)


def get(*args):
    return Resources().get(*args)


def ui_path():
    '''默认GUI的resources文件夹路径
    '''
    return os.path.dirname(os.path.abspath(__file__).split('basewindow')[0])


if __name__ == "__main__":
    print get()
