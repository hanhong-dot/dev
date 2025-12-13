# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       : process_mobu_fbx
# Describe   : 说明描述
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2023/8/7__19:18
# -------------------------------------------------------
import os
import sys
import time

MOTIONBUILDER_PATH = 'C:\\Program Files\\Autodesk\\MotionBuilder 2019\\bin\\x64'
MOTIONBUILDER_EXE = 'C:\\"Program Files"\\Autodesk\\"MotionBuilder 2019"\\bin\\x64\\motionbuilder.exe'
sys.path.append(MOTIONBUILDER_PATH)
__dir__ = 'Z:/dev/apps/publish/process/maya'
FBX_FILE_EVENT = 'FBX_FILE_PATH'
import threading

PYTHON_FILE = '{}/mobu/process_mb_fbx.py'.format(__dir__.split('maya')[0])
import subprocess
import lib.common.fileio as fileio
reload(fileio)
import method.common.dir as _dir


def process_mobu_fbx(fbx_file, ui=True):
    judge_result = judge_mobu(ui=ui)
    if not judge_result:
        return

    if not os.path.exists(fbx_file):
        print('file not found')
        return

    time.sleep(5)
    write_info(fbx_file)
    _cmd = '{} -batch -noconsole -noprompt -f {} -verbosePython {}'.format(MOTIONBUILDER_EXE, fbx_file, PYTHON_FILE)
    result=os.system(_cmd)
    if result==0:
        return True
    # p = subprocess.Popen(_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    # _info,_error=p.communicate()
    # kill_th = threading.Thread(target=kill_command, args=(p, timeout))
    # try:
    #     kill_th.start()
    #     p.wait()
    #     while True:
    #         line = p.stdout.readline()
    #         if not line:
    #             break
    #
    #     # stdout, stderr = p.communicate()
    #     # return_code = p.returncode
    #     # _logger.info(return_code)
    #     # _logger.info(stdout)
    # except Exception as ex:
    #     print ex
    #
    # # return os.system(_cmd)
    # return True


def kill_command(p, timeout):
    import time
    time.sleep(timeout)
    p.kill


def write_info(fbx_file):
    """
    写入info.txt文件
    :param fbx_file:
    :return:
    """
    info_file = get_local_file()
    if  os.path.exists(info_file):
        try:
            os.remove(info_file)
        except :
            pass
    fileio.write(u'{}'.format(fbx_file), info_file, wtype="w")


def get_local_file():
    import shutil
    local_dir=_dir.get_localtemppath("MB_FBX_INFO")
    if not os.path.exists(local_dir):
        os.makedirs(local_dir)
    return '{}/info.txt'.format(local_dir)

def del_event():
    if FBX_FILE_EVENT in os.environ:
        del os.environ[FBX_FILE_EVENT]


def judge_mobu(ui):
    import maya.cmds as cmds
    if not os.path.exists(MOTIONBUILDER_PATH):
        if ui:
            cmds.confirmDialog(title='error', message='MotionBuilder is not installed correctly,please check',
                               button=['OK'], defaultButton='OK')
        print 'MotionBuilder is not installed correctly,please check'
        cmds.error('MotionBuilder is not installed correctly,please check')
        return False
    else:
        return True



# if __name__ == '__main__':
#     fbx_file=r'M:\projects\x3\work\assets\body\YS_BODY\rig\maya\data\fbx\YS_BODY_MB.fbx'
#     process_mobu_fbx(fbx_file, ui=True)
#
#     _cmd = '{} -batch -noconsole -noprompt -f {} -verbosePython {} {}'.format(MOTIONBUILDER_EXE, fbx_file, PYTHON_FILE,fbx_file)
#     p = subprocess.Popen(_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
#     _info, _error = p.communicate()
#     print _info
#     print _error

#     # print process_mobu_fbx(fbx_file)
