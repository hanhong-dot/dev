# coding=utf-8
import argparse
import json
import os
import re
import glob
import subprocess
import multiprocessing
import time

WORKER = 6  # 同时开maya个数,建议比cpu个数少两三个
TIMEOUT = 60*20  # 超时强杀，防止maya报错卡死
maya_path = r'C:/Program Files/Autodesk/Maya2018/bin/mayabatch.exe'


def to_str(arg):
    if isinstance(arg, (str, u"".__class__)):
        return r"'%s'" % arg.replace("\\", "/")
    return str(arg)


def run_in_maya_prompt(module, fun, *args):
    cmd_format = r'"{maya_path}" -prompt -command "python(\"{command}\")"'
    args = ",".join(map(to_str, args))
    command = "import {module};{module}.{fun}({args});".format(module=module, fun=fun, args=args)
    cmd = cmd_format.format(command=command, maya_path=maya_path)
    proc = subprocess.Popen(cmd)

    for i in range(int(TIMEOUT)):
        time.sleep(1.0)
        if proc.poll() is None:
            continue
        else:
            return
    proc.terminate()
    try:
        proc.wait(timeout=5)  # 等待5秒
    except:
        proc.kill()


def run_one(path):
    run_in_maya_prompt("aiMetaTool2.metaNN.random_anim", "random_anim_100", path)

def main():
    anim_dir = "K:/mh_face_random/v2"
    anim_dir = anim_dir.replace("\\", "/")
    paths = []
    for i in range(0, 4000, 1):
        n = "meta_nn_%05i_task" % i
        path = os.path.join(anim_dir, n).replace("\\", "/")
        paths.append(path)
        # run_one(path)
        # break
    pool = multiprocessing.Pool(processes=WORKER)
    pool.map(run_one, paths)


if __name__ == '__main__':
    main()
