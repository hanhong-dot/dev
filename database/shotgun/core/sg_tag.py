# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       : sg_tag
# Describe   : 说明描述
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2022/5/24__12:00
# -------------------------------------------------------
def create_tag(sg, tags_name, return_fields=None, **kwargs):
    '''
    创建标签
    :param sg: sg实体
    :param tags_name: 标签名
    :param return_fields: 回的其他字段值的可选列表
    :param kwargs: 其他字段
    :return:
    '''
    data = {'name': tags_name}

    data.update(kwargs)
    return sg.create("Tag", data, return_fields)


def get_tag_tagID(sg, tags_name):
    '''
    获取标签ID
    :param sg: sg实体
    :param tags_name: 标签名
    :return: 返回标签ID的列表 例如：
    '''
    filters = [
        ['name', 'is', tags_name]
    ]
    return sg.find_one("Tag", filters)


