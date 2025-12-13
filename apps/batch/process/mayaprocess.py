# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       : mayaprocess
# Describe   : maya 批处理
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2024/1/5__11:06
# -------------------------------------------------------
import pprint
import subprocess
import time
DCC_EXECUTEPATH="c:/Program Files/Autodesk/Maya2018/bin/mayabatch.exe"
def main(*args,**kwargs):
    fullpathname = args[0]

    configdic    = args[2]
    # command字符串
    mayafile = fullpathname
    executeCommand  = configdic["command"]
    dcc_executepath = DCC_EXECUTEPATH
    # 调用批处理
    mayaprocess = MayaProcess(mayafile, dcc_executepath, executeCommand)
    return mayaprocess.runProcess()

class MayaProcess(object):
    def __init__(self,filename,executeCommand,args):
        self.filename= filename
        self.executeCommand = executeCommand
        self.commandargs    = args

    def runProcess(self):
        #开始在进程里面调用maya程序。
        batch_info = u""
        if self.filename:
            args = [self.executeCommand, u"-file", u"%s"%self.filename, u"-command"
                    , "python(\""+self.commandargs+"\")"]
        else:
            args = [self.executeCommand, u"-command"
                    , "python(\""+self.commandargs+"\")"]
        cmd = []
        out = u""
        for arg in args:
            cmd.append(arg.encode("gbk"))
        popen_object = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        for info in popen_object.stdout:
            time.sleep(0.1)
            try:
                batch_info += u"{}".format(info)
            except:
                continue
        popen_object.wait()
        # 获取mayabatch处理后返回的代码
        if popen_object.returncode == 0:
            return True, batch_info
        else:
            return False, batch_info
# if __name__ == '__main__':
#     import sys
#     sys.path.append(r'Z:\dev\database\shotgun\toolkit\x3\install\core\python')
#     sys.path.append(r'z:\dev')
#
#     fullpathname='E:/p/card_cream_fx_003.drama_mdl.v002.ma'
#
#     dcc_executepath = DCC_EXECUTEPATH
#     executeCommand="import sys;sys.path.append('z/dev');from apps.publish.batch_publish.batch_item_publish import batch_item_publish;batch_item_publish('{}')".format(fullpathname)
#     # executeCommand=executeCommand.replace(';','\n')
#     mayaprocess = MayaProcess(fullpathname, dcc_executepath, executeCommand)
#
#     ok,result= mayaprocess.runProcess()
#     print ok
#     print result
