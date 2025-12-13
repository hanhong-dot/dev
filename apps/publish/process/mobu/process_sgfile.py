# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       : process_sgfile
# Describe   : 处理
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2023/4/20__21:43
# -------------------------------------------------------
import apps.publish.process.process_package as processPackage
import method.shotgun.get_task_data as get_task_data
import lib.mobu.mbfile as mbfile
import os
import apps.publish.process.filehandle as filehandle
import method.common.dir as dircommon
import method.common.file as common_file
import re
import lib.common.jsonio as jsonio


def processPublish(TaskData, down=False, up=True):
    '''
    处理publish文件
    :param TaskData: Task类
    :return: 返回publish字典
    '''

    '''获取路径
    '''
    _publish_dict = {}
    _task_id = TaskData.task_id
    _handle = get_task_data.TaskData(_task_id, _dcc='mobu')

    des_publish = filehandle.remove_version(_handle.next_publish_path)
    work_file = mbfile.mb_current_file()
    src_publish = '{}\\{}'.format(os.path.dirname(work_file), os.path.basename(des_publish))
    if TaskData.entity_type in ['Asset']:
        src_publish='{}\\{}_MB.fbx'.format(os.path.dirname(work_file),TaskData.entity_name)
        des_publish='{}\\{}_MB.fbx'.format(os.path.dirname(des_publish),TaskData.entity_name)

    mbfile.mb_save_file(src_publish)

    return processPackage.datapack([(src_publish, des_publish)], 'mbfbx', down, up)


def back_publish(TaskData):
    u"""
    处理备份publish 文件
    Args:
        TaskDat:
        down:
        up:

    Returns:

    """
    _publish_dict = {}
    _file = mbfile.mb_current_file()
    _basefile = os.path.basename(_file)

    mbfile.mb_save_file(_file)
    _back_dir = get_backdir(get_publish(TaskData)).replace('/', '\\')
    _suffix = os.path.splitext(_basefile)[-1]

    des_publish = _get_next_file(_basefile, _back_dir, _suffix)

    return processPackage.datapack([(_file, des_publish)], 'back')


def _get_laster(_dir, _suffix):
    u"""
    获得路径下最新文件
    :param _dir:
    :return:
    """
    return dircommon.get_laster_file(_dir, _suffix)


def _get_next_file(_basename, _dir, _suffix):
    u"""
    获得路径下一版本文件
    :param _dir:
    :return:
    """
    _version_num = ''
    _base = os.path.basename(_basename).split('.v')[0]
    _laster_file = _get_laster(_dir, _suffix)
    if _laster_file:
        _version_num = str(common_file.get_next_ver_fil(_laster_file)).zfill(3)
    else:
        _version_num = '1'.zfill(3)
    _versionsign = re.findall('.v\w+', _basename)

    return ('{}/{}'.format(_dir, _basename.replace(_versionsign[-1], '.v{}'.format(_version_num)))).replace('/', '\\')


def get_publish(TaskData):
    '''
    获取publish文件
    :param TaskData: Task类
    :return: 返回publish字典
    '''
    return filehandle.remove_version(get_task_data.TaskData(TaskData.task_id, _dcc='mobu').next_publish_path)


def get_backdir(_des_path):
    '''
    获取备份路径
    :param _des_path: publish路径
    :return: 返回备份路径
    '''
    _path, _basefile = os.path.split(_des_path)
    return '{}/back'.format(_path)


def _get_work_file(TaskData):
    u"""
    获得当前work 文件
    :param TaskData:
    :return:
    """
    try:
        return jsonio.read(_get_work_jsonfile(TaskData))['work_file']
    except:
        return


def save_work(TaskData):
    u"""
    保存当前work文件，并将work信息写入work 描述文件中
    :param TaskData: Task 类
    :return: 无返回
    """
    json_file = _get_work_jsonfile(TaskData)
    if json_file and os.path.exists(json_file):
        os.remove(json_file)
    # 保存到当前文件
    _file = mbfile.mb_current_file()
    mbfile.mb_save_file(_file)
    # 删除存在的json文件
    try:
        os.remove(json_file)
    except:
        pass
    # 写出json文件
    _file = mbfile.mb_current_file()

    _info = {'work_file': _file}

    jsonio.write(_info, json_file)


def _get_work_jsonfile(TaskData):
    u"""
    获取 work json 文件
    :param TaskData: Task 类
    :return:
    """
    local_dir = dircommon.set_localtemppath('temp_info/work_json')
    if not os.path.exists(local_dir):
        os.makedirs(local_dir)
    _entity_name = TaskData.entity_name
    _task_name = TaskData.task_name
    _json_file = u"{}.{}.json".format(_entity_name, _task_name)
    return u"{}/{}".format(local_dir, _json_file)

def open_work(TaskData):
    u"""
    打开work文件
    :param TaskData:
    :return:
    """

    _work_file =str(_get_work_file(TaskData))
    if _work_file and os.path.exists(_work_file):
        mbfile.mb_open_file(_work_file)

if __name__ == '__main__':
    import pprint
    import method.shotgun.get_task as get_task

    _file = mbfile.mb_current_file()
    _taskdata = get_task.TaskInfo(_file, 'X3', 'mobu', 'publish', is_lastversion=False)
    pprint.pprint(processPublish(_taskdata))
