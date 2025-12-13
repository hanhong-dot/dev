# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       : action_item_server
# Describe   : 说明描述
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2023/10/26__18:28
# -------------------------------------------------------
import shotgun_api3


def loggin():
    return {"host": "https://shotgun.nikkigames.cn",
            "api_script": "sg_x3_action",
            "api_key": "a!t8qzsynvehmkgyojlmOutjs",
            "http_proxy": "null"
            }


def action_login():
    '''
    login to shotgun server
    :return: Shotgun instance
    '''

    log = loggin()
    return shotgun_api3.Shotgun(log["host"], script_name=log["api_script"], api_key=log["api_key"])

# if __name__ == '__main__':
#     sg = action_login()
