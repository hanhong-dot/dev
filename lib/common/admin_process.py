# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       : animbot_setup
# Describe   : 读取animBot 工具(添加了识别)
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2023/1/10__19:56
# -------------------------------------------------------
import os
import ctypes
import sys
import subprocess
import time
import shutil

TOOLSPATH=os.path.dirname(os.path.abspath(__file__))


def _fix_path(_path):
    return _path.replace('/', '\\')


def admin_copy(source, targe):
    _cmd = "XCOPY {} {} /S /E /Y".format(source, targe)
    print(_cmd)
    try:
        _run_admin(_cmd)
        return True
    except:
        return False


def process_copy(source, targe):
    if _is_admin():
        admin_copy(source, targe)
    else:
        lpParameters = "_copy({}, {})".format(source, targe)
        if sys.version_info[0] == 3:
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, lpParameters, None, 1)
        else:
            ctypes.windll.shell32.ShellExecuteW(None, u"runas", unicode(sys.executable), unicode(lpParameters), None, 1)


def _is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def _run_admin(cmd):
    """
    exec command with administrator
    :param: cmd: command requiring administrator
    """
    cmd_bat = _get_bat()
    vbs_path = _get_vbs()
    try:
        with open(cmd_bat, "w") as f:
            f.write(cmd)
        # 执行vbs文件
        time.sleep(1)
        vbs_command = "wscript {}".format(vbs_path)
        # subprocess.call(vbs_command, shell=True)
        sp = subprocess.Popen(
            vbs_command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        print("[PID]: %s[cmd]: %s" % (sp.pid, cmd))
        return True
    except Exception as e:
        print("exec vbs fail:{e}")
        return False


def _get_vbs():
    _local_dir = _get_localtemppath('ambot')
    if not os.path.exists(_local_dir):
        os.makedirs(_local_dir)
    _vbs_server='{}/shell.vbs'.format(TOOLSPATH)
    _vbs='{}/shell.vbs'.format(_local_dir)
    try:
        shutil.copy(_vbs_server,_vbs)
    except:
        pass
    return _vbs


def _get_bat():
    _local_dir = _get_localtemppath('ambot')
    if not os.path.exists(_local_dir):
        os.makedirs(_local_dir)
    return '{}/cmd.bat'.format(_local_dir)


def _get_localtemppath(add_path):
    '''
    获取本地Info_temp所在盘符的路径
    :param add_path:添加的路径
    :return:返回整个路径
    '''
    if os.path.exists('D:\\'):
        localInfoPath = 'D:/temp_info/' + add_path
    elif os.path.exists('E:\\'):
        localInfoPath = 'E:/temp_info/' + add_path
    elif os.path.exists('F:\\'):
        localInfoPath = 'F:/temp_info/' + add_path
    elif os.path.exists('C:\\'):
        localInfoPath = 'C:/temp_info/' + add_path
    else:
        raise Exception(u'本地C,D,E,F盘都没有')
    return localInfoPath


# if __name__ == '__main__':
#     load_animbot()
    # _bat='D:\\temp_info\\ambot\\bat.bat'
    # with open(_bat, "w") as f:
    #     f.write('test')


    # source = "\\\\10.10.201.151\\share\\development\\dev\\tools\\maya\\animBotTools"
    # targe = "C:\\Users\\linhuan\\Documents\\maya\\scripts"
    # command = "XCOPY {} {} /S /E /Y".format(source, targe)
    # _run_admin(command)
