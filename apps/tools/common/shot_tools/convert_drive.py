# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       : convert_drive
# Describe   : 转换盘符
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2023/3/13__20:15
# -------------------------------------------------------



__all__ = ["drive2ip", "ip2drive"]

'''
转换路径中的地址与盘符
'''

global_config = {
    "Z:": "\\\\10.10.201.151\\share\development",
    "M:": "\\\\10.10.201.151\\share\product"
}


def drive2ip(fullpath, key):
    '''
    盘符转地址
    :param fullpath:
    :param key:
    :return:
    '''
    if key.replace("\\", "/") not in fullpath.replace("\\", "/"):
        return fullpath
    return u"{}{}".format(IPLink.drive2ip(key), fullpath[len(key):])


def ip2drive(fullpath, key=None):
    '''
    地址转盘符
    :param fullpath:
    :param key:
    :return:
    '''
    if not key:
        key = "Z:"
    if not fullpath:
        fullpath = ""
    if key.replace("\\", "/") not in fullpath.replace("\\", "/"):
        return fullpath
    return u"{}{}".format(IPLink.ip2drive(key), fullpath[len(key):])


class IPLink(object):
    _config = global_config
    if not _config:
        raise Exception(u"未能读取盘符配置信息")

    @classmethod
    def drive2ip(cls, key):
        # print cls._config[key.upper()]
        return cls._config[key.upper()]

    @classmethod
    def ip2drive(cls, key):
        newdict = dict(zip(cls._config.values(), cls._config.keys()))
        # print newdict[key.replace("/", "\\")]
        return newdict[key.replace("/", "\\")]


# if __name__ == '__main__':
#     path = "\\\\10.10.201.151\\share\\product"
#     _path = "Z:\\dev"
#     # print ip2drive(path)
#     # print ip2drive(path, "\\\\10.10.201.151\\share\dev")
#     print drive2ip(_path, "\\\\10.10.201.151\\share\development")
#     _path = "M:\\projects"
#     print drive2ip(_path, "\\\\10.10.201.151\\share\product")
