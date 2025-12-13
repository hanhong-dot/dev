# -*- coding: utf-8 -*-#
# Python     : 
# -------------------------------------------------------
# NAME       :batch_collect.py
# Describe   :
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2024/11/20 16:11
# -------------------------------------------------------
import subprocess

# -*- coding: utf-8 -*-

import subprocess
import os

maya_batch = r"C:\Program Files\Autodesk\Maya2018\bin\mayabatch.exe"


def run_maya_batch(file_path):
    command = (
        "python(\"import sys\\n"
        "sys.path.append(\\\"Z:/dev\\\")\\n"
        "import apps.tools.collect.collect_fun as collect_fun\\n"
        "reload(collect_fun)\\n"
        "collect_fun.collect_map_files_from_file(r'{}')\")"
    ).format(file_path.replace("\\", "/"))

    args = [
        maya_batch,
        "-file",
        file_path.replace("\\", "/"),
        "-command",
        command
    ]

    subprocess.Popen(args, stdin=subprocess.PIPE).communicate()


if __name__ == "__main__":
    file_path = r"D:\temp_info\collect_files\work\FY_BODY\FY_BODY.drama_rig.v073.ma"
    if os.path.exists(file_path):
        run_maya_batch(file_path)
    else:
        print("文件不存在：{file_path}")
