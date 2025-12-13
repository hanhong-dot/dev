# -*- coding: utf-8 -*-#
# Python       : python 2.7.16
# -------------------------------------------------------------------------------
# NAME         : check_bottom
# Describe     : 添加环境
# Version      : v0.01
# Author       : linhuan
# Email        : hanhong@papegames.net
# DateTime     : 2024/3/13__17:40
# -------------------------------------------------------------------------------
# -------------------------------------------------------------------------------
# example:
#
# -------------------------------------------------------------------------------
import os
import sys
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# 添加环境
def add_env():
    sys.path.append('{}/site-packages'.format(BASE_DIR))
    sys.path.append('{}/mod_check'.format(BASE_DIR))

def add_menu():
    import pipline_menu
    reload(pipline_menu)
    pipline_menu.create_pipline_menu()

def launch():
    add_env()
    add_menu()