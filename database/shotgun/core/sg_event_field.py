# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       : sg_event_field
# Describe   : 说明描述
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2022/5/26__22:26
# -------------------------------------------------------
import database.shotgun.core.sg_analysis as sg_analysis

class ShotgunEventFind(object):

    def __init__(self):
        self._sg = sg_analysis.Config().login()

    def get_Meta_Data(self,id):
        '''
        :return: 返回event的meta字段
        '''
        filters = [
            ['id', 'is', id]
        ]
        field = ["meta"]
        return self._sg.find('EventLogEntry',filters, field)

