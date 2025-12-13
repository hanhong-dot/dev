# -*- coding: utf-8 -*-
# -----------------------------------
# @File    : sg_login.py
# @Author  : linhuan
# @Time    : 2025/7/10 18:36
# @Description : 
# -----------------------------------
import shotgun_api3

import apps.tools.common.ai_video_match_tool.server as server


class Config(object):

    def __init__(self):
        self.server = server.Login()
        self.host = self.server.host
        self.api_script = self.server.script
        self.api_key = self.server.key
        self.http_proxy = self.server.proxy

    def login(self):
        return shotgun_api3.Shotgun(self.host, script_name=self.api_script, api_key=self.api_key)
