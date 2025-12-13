# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       : md5
# Describe   : 说明描述
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2022/7/5__17:38
# -------------------------------------------------------
import os
import hashlib


class Md5(object):
    u"""
    Md5码相关函数
    """

    def __init__(self):
        # hashlib md5 class
        pass

    def get_file_md5(self, filename):
        u"""
        获得文件MD5码
        :param filename: 文件夹+文件名
        :return: md5码
        """
        if not filename or not os.path.isfile(filename):
            return
        hash = hashlib.md5()
        with open(filename, 'rb') as f:
            while True:
                b = f.read(8096)
                if not b:
                    break
                hash.update(b)
        return hash.hexdigest()

    def get_md5(self, source):
        u"""
        获得字符串MD5码
        :param source: 字符串
        :return: md5码
        """
        if not source:
            return
        hash = hashlib.md5()
        hash.update(source)
        return hash.hexdigest()

    def contrast_md5(self, sourcefile, targefile):
        u"""

        两个文件进行哈希码对比
        :param sourcefile:原始文件
        :param targefile:进行对比的目标文件
        :return:为True时，两个文件一致,为False时，两个文件不一致
        """
        source_md5 = self.get_file_md5(sourcefile)
        targe_md5 = self.get_file_md5(targefile)
        if source_md5 and targe_md5 and source_md5 == targe_md5:
            return True
        else:
            return False
