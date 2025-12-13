# -*- coding: utf-8 -*-
# -----------------------------------
# @File    : server.py
# @Author  : linhuan
# @Time    : 2025/7/10 16:51
# @Description : 
# -----------------------------------

LOGGININFO = {"host": "https://shotgun.nikkigames.cn",
          "api_script": "x3_ai_video_compute",
          "api_key": "ylgblr!kmhiahsltuaqmxyI4t",
          "http_proxy": "null"
          }

class Login(object):
    def __init__(self, login=None):
        u"""

        """
        self.login = login
        if not self.login:
            self.login = LOGGININFO
        self.host = self.login["host"]
        self.script = self.login["api_script"]
        self.key = self.login["api_key"]
        self.proxy = self.login["http_proxy"]