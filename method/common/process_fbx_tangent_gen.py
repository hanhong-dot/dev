# -*- coding: utf-8 -*-
# author: linhuan
# file: process_fbx_tangent_gen.py
# time: 2026/1/23 14:29
# description:

import sys
import os
import subprocess

FBX_TANGENT_GEN_EXE = r'Z:\dev\method\common\fbx_tangent_gen'


def run_fbx_tangent_gen(fbx_file, out_fbx_file):
    cmd = '{} "{}" "{}"'.format(FBX_TANGENT_GEN_EXE, fbx_file, out_fbx_file)
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = process.communicate()
    if err:
        return False, err
    return True, out
