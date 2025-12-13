# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       : entity_unregister_folder
# Describe   : 清理实体缓存路径(用于实体删除或更名)
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2023/8/15__16:13
# -------------------------------------------------------
import sys

sys.path.append('Z:/dev')

import database.shotgun.tools.actionitem.action_item_server as action_item_server

ShotgunPath = r'Z:\dev\database\shotgun\toolkit\x3'


class UnregisterFolder(object):

    def __init__(self):
        self.project = sys.argv[1]
        self.select_ids = sys.argv[2].split(',')
        self.entity_type = sys.argv[3]
        self.sg = action_item_server.action_login()
        if not self.select_ids:
            return

    def unregister_folders(self):
        u"""
        清理实体缓存路径
        """
        for entity_id in self.select_ids:
            entity_name = self.sg.find_one(self.entity_type, [['id', 'is', int(entity_id)]], ['code'])['code']

            self.entity_ungister_folder(entity_name, self.entity_type)



    def entity_ungister_folder(self, entity_name, entity_type):
        import os
        cmd = '{}\\tank  {} {} unregister_folders '.format(ShotgunPath, entity_type, entity_name)
        return os.system(cmd)


if __name__ == '__main__':
    # print sys.argv
    UnregisterFolder().unregister_folders()
    # print  sys.argv[2].split(',')
    # print  sys.argv[3]
