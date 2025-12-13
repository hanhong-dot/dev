# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       : loginfo
# Describe   : 说明描述
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2022/6/24__16:21
# -------------------------------------------------------

def displayErrorInfo(title='', objList=[], endString='<+++ErrorInfoEnd+++'):
    """
    用于显示异常信息。
    :param title: 标题——说明该异常信息的主要内容。
    :param objList: 物体列表。
    :param endString: 返回末尾字符串。
    :return: 返回——title + '\n'.join(objList) + '\n%s' % endString
    """
    # import maya.OpenMaya as om
    # title + '\n' + '\n'.join(objList) + '\n%s' % endString
    if title:
        try:
            errorInfo = (u'%s\n%s\n%s' % (title, '\n'.join(objList), endString)).encode("gbk")
        except:
            errorInfo = (u'%s\n%s\n%s' % (title, '\n'.join(objList), endString))
    else:
        try:
            errorInfo = (u'%s\n%s' % ('\n'.join(objList), endString)).encode("gbk")
        except:
            errorInfo = (u'%s\n%s' % ('\n'.join(objList), endString))
    # om.MGlobal.displayError(errorInfo)
    return errorInfo


def displayInfo(title='', objList=[], endString='<===InfoEnd===>'):
    u"""
    显示信息
    """
    if title:
        try:
            Info = (u'%s\n%s\n%s' % (title, '\n'.join(objList), endString)).encode("gbk")
        except:
            Info = (u'%s\n%s\n%s' % (title, '\n'.join(objList), endString))
    else:
        try:
            Info = (u'%s\n%s' % ('\n'.join(objList), endString)).encode("gbk")
        except:
            Info = (u'%s\n%s' % ('\n'.join(objList), endString))
    return Info


if __name__ == '__main__':
    print(displayErrorInfo(title='test', objList=['obj01'], endString='<+++ErrorInfoEnd+++'))
