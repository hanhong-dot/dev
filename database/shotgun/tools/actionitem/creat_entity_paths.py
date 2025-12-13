# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       : creat_entity_paths
# Describe   : 创建路径
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2023/8/15__17:26
# -------------------------------------------------------
import sys
import database.shotgun.tools.actionitem.action_item_server as action_item_server

class MakeFolders(object):
    def __init__(self):
        self.project = sys.argv[1]
        self.select_ids = sys.argv[2].split(',')
        self.entity_type = sys.argv[3]
        self.sg = action_item_server.action_login()
        if not self.select_ids:
            return
