# -*- coding: utf-8 -*-#
# Python     :
# -------------------------------------------------------
# NAME       :
# Describe   :
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2025/03/06 14:06
# -------------------------------------------------------

import subprocess
import sys


PYTHONPATH = r'C:\Program Files\Autodesk\Maya2018\bin\mayapy.exe'


def main(*args):
    if not args:
        print('error,not input args,please check')
        return
    return run_process_cover_to_maya2018(args[0][0], args[0][1])


def run_process_cover_to_maya2018(source_path, targe_path):
    py = r'Z:\dev\apps\tools\maya\sub_animation_cover\process_cover_maya_2018.py'
    cmd = []
    cmd.append(PYTHONPATH)
    cmd.append(py)
    cmd.append(source_path)
    cmd.append(targe_path)
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p.wait()
    print(p.stdout.read())


def run():
    data = main(sys.argv[1:])
    data = '{}'.format(data)
    return data


if __name__ == '__main__':
    run()
