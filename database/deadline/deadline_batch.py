# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       : deadline_batch
# Describe   : 说明描述
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2024/1/15__14:27
# -------------------------------------------------------
import os
import time
import sys
import subprocess
import lib.common.jsonio as jsonio

USER_JSON = 'Z:/netrende/submit/maya/json/user.json'

Server_Deadline_10 = "Z:/netrende/Thinkbox/Deadline10/bin"
def runDeadline(maya_version="2018", process_code=0, plugin_name="MayaBatchTake", JobName="", PollName="pipeline",
                GroupName="maya", FileName="", Priority="80", command="import sys"):
    '''
    新版Deadline提交工具，优化代码流程
    :param maya_version:
    :param process_code:
    :param plugin_name:
    :param JobName:
    :param PollName:
    :param GroupName:
    :param FileName:
    :param Priority:
    :return:
    '''
    # 放置临时生成的mel文件
    mel_script_path = checktempPath()
    if mel_script_path == False:
        # 临时文件失败
        return False
    mel_command = build_python_command(command)
    if not JobName:
        JobName = os.path.basename(FileName)
    mel_str = mel_command
    jobdic = {"Version": "2018", "Build": "64bit", "StartupScript": "",
              "SceneFile": "",
              "Plugin": "MayaBatch", "JobName": "my_job", "Pool": "pipline",
              "Group": "maya"}
    jobdic["Version"] = maya_version
    jobdic["StartupScript"] = mel_str
    jobdic["SceneFile"] = FileName
    jobdic["Pool"] = PollName
    jobdic["Group"] = GroupName
    jobdic["Plugin"] = plugin_name
    jobdic["JobName"] = JobName
    jobdic["Priority"] = Priority
    jobdic["Build"] = "64bit"
    writ_user_json()

    # print jobdic
    return submit_deadline(job_location=mel_script_path, deadline_dic=jobdic)


def writ_user_json():
    import getpass
    user = getpass.getuser()
    if os.path.exists(USER_JSON):
        os.remove(USER_JSON)
    jsonio.write({'user': user},USER_JSON)


def checktempPath():
    '''

    :return:
    '''
    if os.path.exists("d:/"):
        # 存在D盘
        if os.path.exists("d:/Info_Temp/temp/Deadline"):
            return "d:/Info_Temp/temp/Deadline"
        else:
            os.makedirs("d:/Info_Temp/temp/Deadline")
            if os.path.exists("d:/Info_Temp/temp/Deadline"):
                return "d:/Info_Temp/temp/Deadline"

            else:
                return False


    elif os.path.exists("e:/"):
        if os.path.exists("e:/Info_Temp/temp/Deadline"):
            return "e:/Info_Temp/temp/Deadline"

        else:
            os.makedirs("e:/Info_Temp/temp/Deadline")
            if os.path.exists("e:/Info_Temp/temp/Deadline"):
                return "e:/Info_Temp/temp/Deadline"

            else:
                return False

    elif os.path.exists("c:/"):
        if os.path.exists("c:/Info_Temp/temp/Deadline"):
            return "c:/Info_Temp/temp/Deadline"

        else:
            os.makedirs("c:/Info_Temp/temp/Deadline")
            if os.path.exists("c:/Info_Temp/temp/Deadline"):
                return "c:/Info_Temp/temp/Deadline"

            else:
                return False


def build_temp_mel(command_str="import sys;print(sys.path)", temp_path="d:/"):
    '''
    根据python命令字符串生成mel文件
    :param command_str: python命令字符串
    :param temp_path: 临时路径
    :return:
    '''
    time_str = int(time.time())
    python_statement_list = command_str.split(";")
    file_name = "deadline_submit_{}.mel".format(time_str)
    if not os.path.exists(temp_path):
        os.makedirs(temp_path)
    file_path = os.path.join(temp_path, file_name)

    with open(file_path, 'a') as fielc:
        for command in python_statement_list:
            fielc.writelines("python(\"{}\");\n".format(command))

    if os.path.exists(file_path):
        return file_path
    else:
        return False


def build_python_command(command_str="", file_name=""):
    '''
    构建mel中的python命令
    :param command_str: 命令字符串
    :param file_name: 文件名，省略
    :return:
    '''
    new_command_str = command_str.replace("\n", "\\n").replace(";", "\\n")

    return new_command_str


def submit_deadline(job_location="", deadlinebin="C:/Program Files/Thinkbox/Deadline10/bin",
                    deadline_dic={"Version": "2018"}):
    '''

    :param job_location: deadline jog 位置
    :param deadlinebin:  deadline安装目录
    :param deadline_dic: deadline的生成字典
    :return:
    '''
    mayabatch_i_location = ""
    mayabatch_j_location = ""
    job_info_str = ""
    plugin_info_str = ""
    maya_env = "import sys;sys.path.append('z:/dev');import apps.launch.maya.interface.maya_launch as maya_launch;maya_launch.launch('batch')"

    if "Version" in deadline_dic.keys():
        Version = deadline_dic["Version"]
        job_info_str += "Version=%s" % Version
        job_info_str += "\n"

    if "Build" in deadline_dic.keys():
        Build = deadline_dic["Build"]
        job_info_str += "Build=%s" % Build
        job_info_str += "\n"

    if "StartupScript" in deadline_dic.keys():
        StartScript = deadline_dic["StartupScript"]
        # StartScript = 'python(\\"{}\\n{}\\")'.format(maya_env, StartScript)
        StartScript = "{};{}".format(maya_env, StartScript)
        # StartScript = 'python(\\"{}\\")'.format(maya_env)
        start_mel = build_temp_mel(command_str=StartScript, temp_path='Z:/netrende/submit/maya/mel')
        start_mel = start_mel.replace("\\", "/")
        print('start_mel', start_mel)
        job_info_str += "StartupScript=%s" % start_mel
        job_info_str += "\n"

    if "SceneFile" in deadline_dic.keys():
        SceneFile = deadline_dic["SceneFile"]
        job_info_str += "SceneFile=%s" % SceneFile
        job_info_str += "\n"

    if "Jobdicargs" in deadline_dic.keys():
        Jobdic = deadline_dic["Jobdicargs"]
        job_info_str += "Jobdicargs=%s" % Jobdic
        job_info_str += "\n"

    # 查看路径是否存在
    if os.path.exists(job_location) == False:
        os.makedirs(job_location)
        # 信息数据写入路径有问题
    JobInfo_file = job_location + "/" + "maya_batch_takecare_j.job"
    with open(JobInfo_file, "w") as file_object:
        file_object.write(job_info_str)

    # 写入插件信息
    if "Plugin" in deadline_dic.keys():
        # 插件名称
        Plugin = deadline_dic["Plugin"]
        plugin_info_str += "Plugin=%s" % Plugin
        plugin_info_str += "\n"

    if "JobName" in deadline_dic.keys():
        # 作业名称
        JobName = deadline_dic["JobName"]
        plugin_info_str += "Name=%s" % JobName
        plugin_info_str += "\n"

    if "Pool" in deadline_dic.keys():
        # 池子
        PoolName = deadline_dic["Pool"]
        plugin_info_str += "Pool=%s" % PoolName
        plugin_info_str += "\n"

    if "Group" in deadline_dic.keys():
        # Groups
        group = deadline_dic["Group"]
        plugin_info_str += "Group=%s" % group
        plugin_info_str += "\n"

    if "Priority" in deadline_dic.keys():
        # Priority
        priority = deadline_dic["Priority"]
        plugin_info_str += "Priority=%s" % priority
        plugin_info_str += "\n"

    if os.path.exists(job_location) == False:
        os.makedirs(job_location)

    plugin_info = job_location + "/" + "maya_batch_takecare_i.job"
    with open(plugin_info, "w") as file_object:
        file_object.write(plugin_info_str)

    if not os.path.exists(JobInfo_file) or not os.path.exists(plugin_info):
        return False
    # print job_info_str, plugin_info_str

    deadline_exe=deadlinebin + "/deadlinecommand.exe"
    if not os.path.exists(deadline_exe):
        deadline_exe=Server_Deadline_10+"/deadlinecommand.exe"
    cmds = [deadlinebin + "/deadlinecommand.exe", plugin_info, JobInfo_file]


    result = subprocess.Popen(cmds, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    result.stdin.close()
    print(result.stdout.read())
    return True


if __name__ == "__main__":
    # build_temp_mel()
    filename = "Z:/TD/test/card_cream_fx_003.drama_mdl.v002.ma"
    log_file = None
    runDeadline(maya_version="2018",
                plugin_name="MayaBatch",
                JobName="",
                PollName='pipline',
                GroupName="maya",
                FileName=filename,
                Priority="99",
                # command="print(sys.path)"
                command="import maya.cmds as cmds;maya_file=cmds.file(q=1,exn=1);print 'maya_file',maya_file"
                )
