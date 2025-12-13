# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       :
# Describe   :
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2025/3/3__16:37
# -------------------------------------------------------
from database.deadline import maya_submission
import os
from database.deadline.run_deadline import RunDeadline
import method.common.dir as common_dir

def sub_cover_files_to_maya2018_to_deadline(input_path, save_path):
    process_files = []
    __error_list = []
    if os.path.isdir(input_path):
        process_files = __get_ma_files(input_path)
    elif os.path.isfile(input_path):
        if input_path.endswith('.ma'):
            process_files.append(input_path)
    if not os.path.exists(save_path):
        try:
            os.makedirs(save_path)
        except:
            return False, u'无法创建保存路径,请检查'

    if not os.path.isdir(save_path):
        return False, u'保存路径不是文件夹,请检查'

    if not process_files:
        return False, u'输入的文件夹中没有ma文件\n或输入的文件不是ma文件,请检查'
    for ma_file in process_files:
        base_name = os.path.basename(ma_file)
        job_name = 'cover_to_maya2018——{}'.format(os.path.splitext(base_name)[0])
        save_file = '{}/{}'.format(save_path, base_name)
        __result = sub_cover_to_deadline(ma_file, save_file, job_name)
        if not __result:
            __error_list.append(ma_file)
    if __error_list:
        __text = ''
        for i in range(len(__error_list)):
            __text += '{}\n'.format(__error_list[i])
        if __text:
            return False, u'以下文件提交失败:\n{}'.format(__text)

    return True, u'提交成功'


def sub_cover_to_deadline(file_path, save_file, job_name):
    job_info = {
        "Plugin": "MayaCoverVersion",
        "Name": job_name,
        "Department": "Cover Maya 2023 to Maya 2018",
        "Pool": 'pipline',
        "Group": "maya",
        "Priority": "80"

    }

    # Plugin info
    plugin_info = {
        "FilePath": file_path,
        "SavePath": save_file
    }

    __dir=common_dir.get_localtemppath('cover_to_maya2018/{}'.format(job_name.split('——')[0]))
    if not os.path.exists(__dir):
        os.makedirs(__dir)
    job_info_file = '{}/{}'.format(__dir, 'job_info.job')
    plugin_info_file = '{}/{}'.format(__dir, 'plugin_info.job')

    # Submit job
    local_deadline='"C:/Program Files/Thinkbox/Deadline10/bin"'
    server_deadlien='Z:/netrende/Thinkbox/Deadline10/bin'
    if os.path.exists(local_deadline):
        deadline_runner = RunDeadline(local_deadline)
    elif os.path.exists(server_deadlien):
        deadline_runner = RunDeadline(server_deadlien)
    else:
        print("Deadline executable not found")
        return False
    success, message = deadline_runner.submit_deadline(job_info, plugin_info,job_info_file,plugin_info_file)

    if success:
        print("Job submitted successfully!")
        return True
    else:
        print("Job submission failed: {}".format(message))
        return False




def __get_ma_files(source_dir):
    __list = []
    for file in os.listdir(source_dir):
        if file.endswith('.ma'):
            __list.append('{}/{}'.format(source_dir, file))
    return __list

# if __name__ == '__main__':
#     _path='Z:/netrender/animation/save/ry'
#     print(os.path.isdir(_path))
