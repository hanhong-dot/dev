# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       : config
# Describe   : 说明描述
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2023/3/14__16:16
# -------------------------------------------------------
import os
__all__ = ["Resources", "get"]

class Resources(object):
    '''config文件夹获取集
    '''

    def __init__(self, path=None):
        if not path:
            self._path = ui_path()
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
    return os.path.dirname(os.path.abspath(__file__))


# if __name__ == "__main__":
#     print get('config/projects', 'X3')
