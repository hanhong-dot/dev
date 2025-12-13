# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       : down_select_asset_thumbnail
# Describe   : 下载选择的资产缩略图

# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2023/7/3__19:20
# -------------------------------------------------------
import os
import sys

sys.path.append('Z:/dev')


import database.shotgun.tools.actionitem.action_item_server as action_item_server

from database.shotgun.fun.get_entity import *

sg = action_item_server.action_login()


class DownSelectAssetThumbnail(object):
    def __init__(self):
        self.select_ids = sys.argv[2].split(',')
        self.entity_type = sys.argv[3]
        self.local_dir = get_local_thumbnail_dir()
        if not self.select_ids:
            return

    def down_thumbnail(self):
        down_true_files = []
        down_false_files = []
        for entity_id in self.select_ids:
            result = self.__down_thumbnail(entity_id, self.entity_type)
            if result[0]:
                down_true_files.append(result[1])
            else:
                down_false_files.append(result[1])
        if down_true_files:
            print u'以下缩略图下载成功：'
            for file in down_true_files:
                print file

        if down_false_files:
            print u'以下缩略图下载失败：'
            for file in down_false_files:
                print file
        cmd = 'cmd.exe /C start "Folder" "%s"' % self.local_dir
        os.system(cmd)

    def __down_thumbnail(self, entity_id, entity_type):
        sg_handler = BaseGetSgInfo(sg, int(entity_id),entity_type)
        entity_name = sg_handler.get_name()
        imagepath = '{}/{}.png'.format(self.local_dir, entity_name)

        try:
            _thumbnail = sg_handler.download_entity_thumbnail(imagepath)
            return True, _thumbnail
        except:
            return False, entity_name


def get_local_thumbnail_dir():
    '''
    获取写入位置
    :return: 返回可写入路径
    '''
    if os.path.exists("d:/"):
        # 查询写入路径
        if os.path.exists("d:/Info_Temp/asset_thumbnail"):
            return "d:/Info_Temp/asset_thumbnail"
        else:
            os.makedirs("d:/Info_Temp/asset_thumbnail")
            return "d:/Info_Temp/asset_thumbnail"

    elif os.path.exists("e:/"):
        # 查询写入路径
        if os.path.exists("e:/Info_Temp/asset_thumbnail"):
            return "e:/Info_Temp/asset_thumbnail"
        else:
            os.makedirs("e:/Info_Temp/asset_thumbnail")
            return "e:/Info_Temp/asset_thumbnail"

    elif os.path.exists("c:/"):
        # 查询写入路径
        if os.path.exists("c:/Info_Temp/asset_thumbnail"):
            return "c:/Info_Temp/asset_thumbnail"
        else:
            os.makedirs("c:/Info_Temp/asset_thumbnail")
            return "c:/Info_Temp/asset_thumbnail"


if __name__ == '__main__':
    # print sys.argv
    DownSelectAssetThumbnail().down_thumbnail()


    # from database.shotgun.core.sg_image import *
    # select_ids=[12685, 13844]
    # entity_type='Asset'
    # for entity_id in select_ids:
    #     entity_name = BaseGetSgInfo(sg, entity_id,entity_type).get_name()
    #
    #     # fields = ['image','code']
    #     # filters = [['id', 'is', entity_id]]
    #     # print sg.find_one(entity_type, filters, fields)
    #     imagepath = '{}/{}.png'.format(get_local_thumbnail_dir(), entity_name)
    #     # entity_thumbnail=sg_base.select_entity(sg, entity_type, entity_id, ['image'])
    #
    #     _thumbnail = BaseGetSgInfo(sg, entity_id,entity_type).download_entity_thumbnail(imagepath)
    #     print _thumbnail
