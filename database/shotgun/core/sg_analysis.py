# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       : sg_analysis
# Describe   : 说明描述
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2022/5/23__18:15
# -------------------------------------------------------



try:
    import shotgun_api3
except:
    import sys
    sys.path.append(r'Z:\dev\Ide\Python\2.7.11\Lib\site-packages')
    import shotgun_api3


try:
    import database.shotgun.core.server as server
except:
    import database.shotgun.core.server3 as server



class Config(object):
    u"""
    解析shotgun基本信息
    """

    def __init__(self):
        self.server = server.Login()
        self.host = self.server.host
        self.api_script = self.server.script
        self.api_key = self.server.key
        self.http_proxy = self.server.proxy

    def login(self):
        '''
        login to shotgun server
        :return: Shotgun instance
        '''
        return shotgun_api3.Shotgun(self.host, script_name=self.api_script, api_key=self.api_key)

