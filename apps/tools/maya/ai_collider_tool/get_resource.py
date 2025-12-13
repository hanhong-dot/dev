# -*- coding: utf-8 -*-#
# -------------------------------------------------------
# NAME       : get_resource
# Describe   : 说明描述
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2025/6/18__下午2:17
# -------------------------------------------------------
import os

__all__ = ["Resources", "get"]


class Resources(object):
    '''config文件夹获取集
    '''

    def __init__(self, path=None):
        if not path:
            self._path = get_root_path() + '/resources'
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


def get_root_path():
    '''默认GUI的resources文件夹路径
    '''
    return '{}/ai_collider_tool'.format(os.path.dirname(os.path.abspath(__file__).split('ai_collider_tool')[0]))


if __name__ == "__main__":
    print(get('obj', 'cube.obj'))
