# -*- coding: utf-8 -*-
import os
import datetime
import base64
import getpass
import time
import shutil
from lib.common import jsonio

from lib.common.md5 import Md5

DATA_DIR = 'Z:/Data/AI_Marker_Clean_Up'
DeadlineExe = 'C:/Program Files/Thinkbox/Deadline10/bin'
JOB_INFO_FILE='Z:/Data/AI_Marker_Clean_Up/deadline/job_info.job'
PLUGIN_INFO_FILE='Z:/Data/AI_Marker_Clean_Up/deadline/plugin_info.job'
from database.deadline.run_deadline import RunDeadline

def sub_mark_data_to_sg():
    pass


def sub_mark_to_deadline(_path, _file_type, _save_path):
    __sub_files = get_files_from_dir(_path, _file_type)
    __sub_file_list = []
    __error_files = []
    __error_sub_files = []
    __ok_sub_files = []
    if not os.path.exists(_path):
        return False, 'Path {} not exists'.format(_path)
    __local_dir_list = ['D:/', 'C:/', 'E:/', 'F:/']
    for __dir in __local_dir_list:
        if _path.startswith(__dir):
            return False, 'Path {} is local path,Please Check'.format(_path)
        if _save_path.startswith(__dir):
            return False, 'Path {} is local path,Please Check'.format(_save_path)

    if not __sub_files:
        return False, 'No files of type {} found in {}'.format(_file_type, _path)
    for __sub_file in __sub_files:
        __sub_file = __sub_file.replace('\\', '/')
        if not os.path.exists(__sub_file):
            __error_files.append(__sub_file)
            continue
        __sub_file_list.append(__sub_file)

    if __error_files:
        return False, 'Files {} not exists'.format(__error_files)
    if not __sub_file_list:
        return False, 'No files of type {} found in {}'.format(_file_type, _path)
    for __sub_file in __sub_file_list:
        ok, result = sub_task_to_deadline(__sub_file, _file_type, _save_path,JOB_INFO_FILE,PLUGIN_INFO_FILE)
        if not ok:
            __error_sub_files.append({'file': __sub_file, 'error': result})
        else:
            __ok_sub_files.append(__sub_file)

    if __error_sub_files:
        print(u'以下文件提交失败,请检查')
        for __error_sub_file in __error_sub_files:
            print(__error_sub_file['file'])
            print(__error_sub_file['error'])
    if __ok_sub_files:
        print(u'以下文件提交成功')
        for __ok_sub_file in __ok_sub_files:
            print(__ok_sub_file)
    if __error_sub_files:
        __error_result=''
        for __error_sub_file in __error_sub_files:
            __error_result=__error_result+'{}\n{}'.format(__error_sub_file['file'],__error_sub_file['error'])
        return False, u'以下文件提交失败,请检查\n{}'.format(__error_result)
    return True, 'Success'


def sub_task_to_deadline(_path, _file_type, _save_path,job_info_file,plugin_info_file):
    job_info = {
        "Plugin": "MarkerCleanUp",
        "Name": 'Sub_{}'.format(os.path.splitext(os.path.basename(_path))[0]),
        "Comment": "AIMarkerCleanUp Sub",
        "Department": "Tools",
        "Pool": "shogun",
        "Group": "shogun",
        "Priority": "50"

    }

    # Plugin info
    plugin_info = {
        "FileType": _file_type,
        "FilePath": '~{}~'.format(_path) if '~' not in _path else _path,
        "SavePath": '~{}~'.format(_save_path) if '~' not in _save_path else _save_path
    }
    deadline_runner = RunDeadline(DeadlineExe)
    success, message = deadline_runner.submit_deadline(job_info, plugin_info,job_info_file=job_info_file,plugin_info_file=plugin_info_file)
    if not success:
        success, message = deadline_runner.submit_deadline(job_info, plugin_info, job_info_file=job_info_file,
                                                           plugin_info_file=plugin_info_file)

    return success, message


def sub_mark_data_to_json(source_dir, save_dir, file_type):
    status, data = get_sub_mark_data(source_dir, save_dir, file_type)
    if not status:
        return False, data
    ok, result = __get_json_dir('X3')
    if not ok:
        return False, result
    json_dir = result
    file_id = data['id']
    sub_json_dir = os.path.join(json_dir, 'sumssion')
    data_json_dir = os.path.join(json_dir, 'data')
    json_file = os.path.join(sub_json_dir, "{}.json".format(file_id))
    sub_date = data['sub_date']
    id = data['id']
    user = data['sub_user']
    # data_files=get_files_from_data(id, data_json_dir)
    # data=get_sub_mark_data_except_data(data, data_files)
    if os.path.exists(json_file):
        his_json_dir = os.path.join(sub_json_dir, 'his', sub_date)
        if not os.path.exists(his_json_dir):
            try:
                os.makedirs(his_json_dir)
            except Exception as e:
                pass
        his_json_file = os.path.join(his_json_dir, "{}.json".format(file_id))
        ok, result = remove_json_file(json_file, his_json_file)
        if not ok:
            return False, result

    __write_json(json_file, data)
    __write_file_data_from_data(data, data_json_dir, id, sub_date)
    return True, (json_file, data)


def get_sub_mark_data_except_data(data, files_data):
    if not files_data:
        return data
    __files_data = data['sub_files_data']
    __sub_files = data['sub_files']
    for i in range(len(__files_data)):
        __file_data = __files_data[i]
        __file_path = __file_data['path']
        __file_md5 = __file_data['md5']
        __file_date = __file_data['date']
        for j in range(len(files_data)):
            __files_data = files_data[j]
            __files_data_path = __files_data['path']
            __files_data_md5 = __files_data['md5']
            __files_data_date = __files_data['date']
            if __file_path == __files_data_path and __file_md5 == __files_data_md5 and __file_date == __files_data_date:
                __files_data.pop(j)
                __sub_files.pop(j)
                break
    return data


def __write_file_data_from_data(data, data_dir, id, date_id):
    __dir = os.path.join(data_dir, id)
    if not os.path.exists(__dir):
        try:
            os.makedirs(__dir)
        except Exception as e:
            pass
    json_file = os.path.join(__dir, '{}.json'.format(date_id))
    __user = data['sub_user'] if 'sub_user' in data else ''
    __files_data = data['sub_files_data'] if 'sub_files_data' in data else []
    __info = {}
    __info['sub_user'] = __user
    __info['sub_files_data'] = __files_data
    __info['file_type'] = data['file_type']
    jsonio.write(__info, json_file)
    return json_file


def get_files_from_data(id, data_dir):
    __data = []
    id_data_dir = os.path.join(data_dir, id)
    if not os.path.exists(id_data_dir):
        return []
    json_files = get_files_from_dir(id_data_dir, file_type='json')
    if not json_files:
        return []
    for json_file in json_files:
        __json_data = jsonio.read(json_file)
        __files_data = __json_data['sub_files_data'] if 'sub_files_data' in __json_data else []
        if not __files_data:
            continue
        if not __data:
            __data.extend(__files_data)
        else:
            for i in range(len(__files_data)):
                __file_data = __files_data[i]
                __file_path = __file_data['path']
                __file_md5 = __file_data['md5']
                __file_date = __file_data['date']
                __result = True
                for j in range(len(__data)):
                    __data_file = __data[j]
                    __data_file_path = __data_file['path']
                    __data_file_md5 = __data_file['md5']
                    __data_file_date = __data_file['date']
                    if __file_path == __data_file_path and __file_md5 == __data_file_md5 and __file_date == __data_file_date:
                        __result = False
                        break
                if __result:
                    __data.append(__file_data)
    return __data


def get_sub_mark_data_ex_json_data(sub_data, json_data, p4_project, net):
    if not json_data:
        return sub_data
    __files_data = sub_data['sub_files_data']
    __sub_files = sub_data['sub_files']
    __json_files_data = json_data['sub_files_data'] if 'sub_files_data' in json_data else []
    if not __json_files_data:
        return sub_data
    _ex_file_list = []
    for i in range(len(__json_files_data)):
        __json_sub_file_data = __json_files_data[i]
        __json_sub_file_path = __json_sub_file_data['path']
        __json_sub_file_md5 = __json_sub_file_data['md5']
        __json_sub_file_date = __json_sub_file_data['date']
        for j in range(len(__files_data)):
            __sub_file_data = __files_data[j]
            __sub_file_path = __sub_file_data['path']
            __sub_file_md5 = __sub_file_data['md5']
            __sub_file_date = __sub_file_data['date']
            if __json_sub_file_path == __sub_file_path and __json_sub_file_md5 == __sub_file_md5 and __json_sub_file_date == __sub_file_date:
                __files_data.pop(j)
                _ex_file_list.append(__json_sub_file_path)
                break
    if not _ex_file_list:
        return sub_data
    for i in range(len(_ex_file_list)):
        __file = cover_net_path_to_p4_path(_ex_file_list[i], p4_project, net)
        for j in range(len(__sub_files)):
            if __sub_files[j] == __file:
                __sub_files.pop(j)
                break
    sub_data['sub_files'] = __sub_files
    sub_data['sub_files_data'] = __files_data
    return sub_data


def cover_net_path_to_p4_path(net_path, p4_project, net):
    return net_path.replace(net, p4_project)


def remove_json_file(source_json_file, target_json_file):
    try:
        shutil.copy(source_json_file, target_json_file)
    except Exception as e:
        return False, "Failed to copy file: " + str(e)
    try:
        os.remove(source_json_file)
    except Exception as e:
        return False, "Failed to delete file: " + str(e)
    return True, "Success"


def get_sub_mark_data(source_dir, save_dir, file_type):
    data = {}

    # 检查路径合法性
    if not source_dir:
        return False, "Source directory is empty."
    if not save_dir:
        return False, "Save directory is empty."
    source_dir = normalize_path(source_dir)
    save_dir = normalize_path(save_dir)

    # 生成 ID 和当前时间
    file_id = get_id_from_dir(source_dir)
    current_time = get_current_time()
    current_user = get_current_user()

    # 查找文件
    files = get_files_from_dir(source_dir, file_type)
    if not files:
        return False, "No files of type '" + file_type + "' found in '" + source_dir + "'."
    if not files:
        return False, "No files of type '" + file_type + "' found in '" + source_dir + "'."

    # 构造数据字典
    data['id'] = file_id
    data['sub_files'] = files
    data['sub_date'] = current_time
    data['sub_user'] = current_user
    data['file_type'] = file_type
    data['save_path'] = save_dir
    # 暂停获取文件元数据
    # data['sub_files_data'] = get_files_data(files)

    return True, data


def get_p4_path(source_dir, p4_project, path_key=u'Animation'):
    if isinstance(source_dir, str):
        source_dir = source_dir.decode('utf-8')
    if isinstance(p4_project, str):
        p4_project = p4_project.decode('utf-8')
    if isinstance(path_key, str):
        path_key = path_key.decode('utf-8')

    path_key = u'{}/'.format(path_key)
    source_dir = source_dir.split(path_key)[-1]
    p4_path = u'{}/{}'.format(p4_project, source_dir)
    return normalize_path(p4_path)


def normalize_path(path):
    if isinstance(path, bytes):
        path = path.decode('utf-8', errors='ignore')
    return path.replace('\\', '/')


def get_files_data(files):
    return [__get_file_data(__file) for __file in files if __file and os.path.exists(__file)]


def __read_json(json_file):
    return jsonio.read(json_file)


def __write_json(json_file, data):
    jsonio.write(data, json_file)


def __get_json_dir(project='X3'):
    json_dir = ''
    if project.lower() == 'x3':
        json_dir = DATA_DIR
    if not json_dir:
        return False, "Project '" + project + "' is not supported."
    return True, json_dir


def get_current_user():
    return getpass.getuser()


def get_files_from_dir(source_dir, file_type):
    files = []
    for root, _, filenames in os.walk(source_dir):
        for filename in filenames:
            if filename.lower().endswith(file_type.lower()):
                files.append(u'{}'.format(os.path.join(root, filename)))
    return files


def get_files_from_dir_by_json_file(source_dir, file_type, json_file):
    __files = __read_json(json_file)
    files = []
    if not __files:
        return files
    for __file in __files:
        if __file.lower().endswith(file_type.lower()):
            files.append(u'{}'.format(os.path.join(source_dir, __file)))
        __dir, __file_name = os.path.split(__file)
        __base_name, __ext = os.path.splitext(__file_name)

        __dir = __dir.replace('\\', '/')
        if not __dir.endswith('/'):
            __dir = __dir + '/'
        source_dir = source_dir.replace('\\', '/')
        if not source_dir.endswith('/'):
            source_dir = source_dir + '/'
        if __dir.lower() == source_dir.lower() and __ext.lower() == file_type.lower():
            files.append(u'{}'.format(os.path.join(source_dir, __file)))
    return files


def get_id_from_dir(source_dir):
    return Md5().get_md5(base64.b64encode(source_dir.encode('utf-8')))


def get_current_time():
    return datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S')


def convert_p4_to_net_path(p4_path, net_path, p4_project):
    return p4_path.replace(p4_project, net_path)


def convert_files_to_p4_paths(files, p4_project, net):
    return [convert_p4_to_net_path(__file, p4_project, net) for __file in files]


def __get_file_data(__file):
    """获取文件的元数据"""
    if __file and os.path.exists(__file):
        data = {
            # 'md5': Md5().get_file_md5(__file),文件过大,暂时不获取md5
            'date': time.strftime('%Y_%m_%d_%H_%M_%S', time.localtime(os.path.getmtime(__file))),
            'path': normalize_path(__file),
            'status': 'wtg'
        }
        return data

# if __name__ == '__main__':
#     source_dir = "Animation/动捕拍摄/2024年/11月/20241101_1号棚FY解体重捕III/数据/20241101X3/Project 2/Capture day 1/Session 1/"
#     save_dir = "Animation/动捕拍摄/2024年/11月/20241101_3号棚YS_0035下/FBX/"
#     file_type = 'mcp'
#     p4_project = "//depot/X3_RawData/Animation"
#
#     status, result = sub_mark_data_to_json(source_dir, save_dir, file_type, p4_project)
#     if status:
#         print("Success:", result)
#     else:
#         print("Failed:", result)
