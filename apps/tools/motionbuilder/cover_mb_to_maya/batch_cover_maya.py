# -*- coding: utf-8 -*-
# author: linhuan
# file: batch_cover_maya.py
# time: 2025/12/1 19:22
# description:
import subprocess
import sys

import sys


def main(*args):
    if not args:
        print('error,not input args,please check')
        return
    return process_cover_to_maya2018(args[0][0])


def process_cover_to_maya2018(json_file):
    import sys
    LAUNCHPATH = 'Z:/dev'
    sys.path.append(LAUNCHPATH)
    from apps.tools.motionbuilder.cover_mb_to_maya import ma_process_fun
    reload(ma_process_fun)
    import apps.launch.maya.interface.maya_launch as maya_launch
    maya_launch.launch('batch')
    import maya.standalone
    maya.standalone.initialize()
    return ma_process_fun.ma_process_file(json_file)


def run():
    data = main(sys.argv[1:])
    data = '{}'.format(data)
    print(data)
    return data


if __name__ == '__main__':
    run()
