# -*- coding: utf-8 -*-#
# Python       : python 2.7.16
# -------------------------------------------------------------------------------
# NAME         : process_publish
# Describe     : 通用处理publish和master文件
# Version      : v0.01
# Author       : linhuan
# Email        : hanhong@papegames.net
# DateTime     : 2022/5/16__20:30
# -------------------------------------------------------------------------------
# -------------------------------------------------------------------------------
# example:  处理文件返回字典 {u'publish': [{u'des_path': u'Y:/Project/AD/Asset/tt/sg_base.py',
#                       u'src_path': u'E:/lib/Develop/db/shotgun/core/sg_base.py'}],
#             u'master': [{u'des_path': u'E:/test/abc.fbx',
#                       u'src_path': u'D:/Info_Temp/abc.fbx'}]}
#
# -------------------------------------------------------------------------------
import os
import apps.publish.process.filehandle as filehandle

import method.maya.common.mayafile as mayafile
import apps.publish.process.process_package as processPackage

import method.maya.common.file as filecommon
import lib.common.jsonio as jsonio
import method.common.dir as dir

REFFILE = 'M:/projects/x3/publish'


def processPublish(TaskData, down=False, up=True):
    '''
    处理publish文件
    :param TaskData: Task类
    :return: 返回publish字典
    '''

    '''获取路径
    '''
    _publish_dict = {}
    task_name = TaskData.task_name
    asset_type = TaskData.asset_type

    src_publish = mayafile.Maya_File(TaskData).save_localfile(
        os.path.basename(filehandle.remove_version(TaskData.des_path)))
    des_publish = filehandle.remove_version(filehandle.get_publishfilepath(TaskData))
    work_file = _get_work_file(TaskData)
    ref_info = str(_get_refinfo(TaskData))
    file_data = _get_file_data(TaskData)
    if file_data:
        file_data = str(file_data)
    if task_name in ['faceld_rig']:
        return processPackage.datapack([(src_publish, des_publish)], 'mocap', down, up, work_file, ref_info)
    elif task_name.startswith('ue_') == True:
        return processPackage.datapack([(src_publish, des_publish)], 'ue', down, up, work_file, ref_info)
    elif task_name in ['drama_rig', 'rbf'] and asset_type and asset_type in ['role', 'item'] and file_data:
        return processPackage.datapack([(src_publish, des_publish)], 'publish', down, up, work_file, ref_info,
                                       file_data)
    else:
        return processPackage.datapack([(src_publish, des_publish)], 'publish', down, up, work_file, ref_info)


def back_publish(TaskData):
    u"""
    处理备份publish 文件
    Args:
        TaskDat:
        down:
        up:

    Returns:

    """
    import maya.cmds as cmds
    _publish_dict = {}
    _file = cmds.file(q=1, exn=1)
    _basefile = os.path.basename(_file)
    _current_dir = _get_current_data_time_dir()

    src_publish = mayafile.Maya_File(TaskData).save_localfile(_basefile)
    des_publish = '{}/{}/{}'.format(filehandle.get_backpublishdir(TaskData), _current_dir, _basefile)

    return processPackage.datapack([(src_publish, des_publish)], 'back')


def _get_current_data_time_dir():
    u"""

    :return:
    """
    import datetime
    _time = datetime.datetime.now()
    _time_dir = '{}-{}-{}-{}-{}-{}'.format(_time.year, _time.month, _time.day, _time.hour, _time.minute, _time.second)
    return _time_dir


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


def _get_refinfo(TaskData):
    u"""
    获取work 参考信息
    :param TaskData:
    :return:
    """
    _json_file = _get_work_jsonfile(TaskData)
    if _json_file and os.path.exists(_json_file):
        _info = jsonio.read(_json_file)
        if _info and 'ref_info' in _info:
            return _info['ref_info']


def _f(TaskData):
    _json_file = _get_work_jsonfile(TaskData)
    if _json_file and os.path.exists(_json_file):
        _info = jsonio.read(_json_file)
        if _info and 'file_data' in _info:
            return _info['file_data']


def save_work(TaskData):
    u"""
    保存当前work文件，并将work信息写入work 描述文件中
    :param TaskData: Task 类
    :return: 无返回
    """
    import apps.tools.maya.work_save as work_save
    import maya.cmds as cmds
    json_file = _get_work_jsonfile(TaskData)
    if json_file and os.path.exists(json_file):
        os.remove(json_file)

    task_name = TaskData.task_name
    asset_type = TaskData.asset_type
    # 升版本保存
    _file = cmds.file(q=1, exn=1)
    filecommon.BaseFile().open_file(_file)

    _path, _basename = os.path.split(_file)
    _suffix = os.path.splitext(_basename)[-1]
    _next_version_file = ''
    _base_name = os.path.basename(_file)

    _laster_version_file = get_laster(_path, _suffix, _base_name)
    if _laster_version_file:
        _next_version_file = get_next_version_file(_laster_version_file)

    if _next_version_file:

        filecommon.BaseFile().save_file(_next_version_file)
    else:
        filecommon.BaseFile().save_file(_file)
    work_save.work_write_json_maya()
    # 删除存在的json文件
    try:
        os.remove(json_file)
    except:
        pass
    # 写出json文件
    _file = cmds.file(q=1, exn=1)
    _refinfo = _get_ref_info()
    _info = {'work_file': _file}
    if _refinfo:
        _info['ref_info'] = _refinfo
    if asset_type and asset_type in ['role', 'item']:
        __file_data = get_file_data(TaskData)
        if __file_data:
            _info['file_data'] = __file_data

    jsonio.write(_info, json_file)


def get_file_data(TaskData):
    u"""
    获取文件数据
    :param TaskData: Task 类
    :return: 返回文件数据字典
    """
    # import lib.maya.analysis.analyze_structure as structure
    # import database.shotgun.fun.get_entity as get_entity
    import database.shotgun.core.sg_analysis as sg_analysis
    import lib.maya.analysis.analyze_fbx as analyze_fbx
    asset_type = TaskData.asset_type
    task_name = TaskData.task_name
    entity_id = TaskData.entity_id
    entity_type = TaskData.entity_type
    sg = sg_analysis.Config().login()
    _fbx_info = analyze_fbx.AnalyFbx(TaskData).get_fbx()
    __mod_grp_list = []
    if not _fbx_info:
        return {}
    for i in range(len(_fbx_info)):
        __grps = _fbx_info[i].get('fbx_objs')
        if __grps:
            __mod_grp_list.extend(__grps)
    if not __mod_grp_list:
        return {}
    __mod_grp_list = list(set(__mod_grp_list))
    __data = _get_mod_grps_children(__mod_grp_list)
    return __data
    # structure_data = structure.AnalyStrue(TaskData).get_structure()
    # asset_level = get_entity.BaseGetSgInfo(sg, entity_id, entity_type).get_asset_level()
    # if not asset_level:
    #     asset_level = 'level_0'
    # else:
    #     asset_level = 'level_{}'.format(asset_level)
    # if asset_level in structure_data:
    #     __structure_data = structure_data[asset_level]
    # else:
    #     __structure_data = structure_data
    # mod_grps = get_mod_grps(__structure_data)
    # if not mod_grps:
    #     return {}
    # __data = _get_mod_grps_children(mod_grps)
    # return __data


def _get_mod_grps_children(mod_grps):
    __data = []
    if not mod_grps:
        return __data
    for mod_grp in mod_grps:
        __child_dict = get_mod_grp_meshs(mod_grp)
        if __child_dict:
            __data.append(__child_dict)
    return __data


def get_mod_grp_meshs(mod_grp):
    import maya.cmds as cmds
    __dict = {}
    if not mod_grp or not cmds.objExists(mod_grp):
        return __dict
    children = cmds.listRelatives(mod_grp, ad=1, type='mesh', f=1)
    if not children:
        return __dict
    meshs = __get_mesh_by_shape(children)
    if not meshs:
        return __dict
    meshs = list(set(meshs))
    __dict['mod_grp'] = mod_grp
    __dict['meshs'] = meshs
    return __dict


def __get_mesh_by_shape(shapes):
    import maya.cmds as cmds
    meshs = []
    if not shapes:
        return meshs
    for shape in shapes:
        if not cmds.objExists(shape):
            continue
        tr = cmds.listRelatives(shape, parent=1, fullPath=1)
        if tr:
            meshs.append(tr[0])
    return meshs


def get_mod_grps(structure_data):
    mod_grps = []
    if not structure_data:
        return mod_grps
    if isinstance(structure_data, str):
        mod_grps.append(structure_data)
    elif isinstance(structure_data, list):
        mod_grps = structure_data
    elif isinstance(structure_data, dict):
        for k, v in structure_data.items():
            if isinstance(v, str):
                mod_grps.append(v)
            elif isinstance(v, list):
                mod_grps.extend(v)
            elif isinstance(v, dict):
                mod_grps.extend(get_mod_grps(v))
    return mod_grps


def export_file(TaskData):
    u"""
    导出文件
    :param TaskData: Task 类
    :return:
    """
    import maya.cmds as cmds
    from lib.maya.node.grop import BaseGroup
    from method.maya.common.file import BaseFile
    if TaskData.task_name in ['drama_mdl', 'fight_mdl', 'lan_mdl', 'ue_mdl', 'ue_low']:
        file_name = cmds.file(q=1, exn=1)
        groups = BaseGroup().get_root_groups()
        if groups:
            BaseFile().export_file(groups, file_name)
            BaseFile().open_file(file_name)


def get_next_version_file(file_name):
    u"""
    获取下一个版本文件
    :param file_name:
    :return:
    """
    import method.common.file as common_file
    _get_vernum = common_file.get_vernum(file_name)
    _next_version = common_file.get_next_ver_fil(file_name)
    return file_name.replace('.v{}.'.format(_get_vernum), '.v{}.'.format(_next_version))


def get_laster(dir, suffix, basename):
    import method.common.dir as dircommon
    reload(dircommon)
    return dircommon.get_laster_file_base(dir, suffix, basename)


def _get_ref_info():
    u"""
    获取当前文件参考信息
    :return:
    """
    _dict = {}
    refinfo = filecommon.BaseFile().reference_info_dict()
    if refinfo:
        for k, v in refinfo.items():
            if v and len(v) > 1:
                refpath = v[-1]
                if REFFILE in refpath:
                    basename = os.path.basename(refpath)
                    _entity = basename.split('.')[0]
                    _task = basename.split('.')[1]
                    if _entity and _task:
                        _dict[_entity] = _task
    return _dict


def open_work(TaskData):
    u"""
    打开work文件
    :param TaskData:
    :return:
    """

    _work_file = _get_work_file(TaskData)
    if _work_file and os.path.exists(_work_file):
        filecommon.BaseFile().open_file(_work_file)


def _get_work_jsonfile(TaskData):
    u"""
    获取 work json 文件
    :param TaskData: Task 类
    :return:
    """
    local_dir = dir.set_localtemppath('temp_info/work_json')
    if not os.path.exists(local_dir):
        os.makedirs(local_dir)
    _entity_name = TaskData.entity_name
    _task_name = TaskData.task_name
    _json_file = u"{}.{}.json".format(_entity_name, _task_name)
    return u"{}/{}".format(local_dir, _json_file)


def processMaster(TaskData):
    '''
    处理master文件
    :param TaskData: Task类
    :return: 返回master字典
    '''
    src_master = ''
    des_master = ''
    if TaskData.task_type == 'asset':
        src_mastername = filehandle.get_assetlocalMastername(TaskData)
        src_master = mayafile.Maya_File(TaskData).save_localfile(src_mastername)
        des_master = filehandle.get_assetmaterpath(TaskData)
    if TaskData.task_type == 'shot':
        src_mastername = filehandle.get_shotlocalMastername(TaskData)
        src_master = mayafile.Maya_File(TaskData).save_localfile(src_mastername)
        des_master = filehandle.get_shotmaterpath(TaskData)

    return processPackage.datapack([(src_master, des_master)], 'master')


def processEmptyPublish(TaskData):
    u"""
    生成空的publish文件
    :param TaskData: Task类
    :return: 返回空字典
    """
    # 创建新文件
    filecommon.BaseFile().new_file()
    # 保存文件
    mayafile.Maya_File(TaskData).save_localfile(os.path.basename(TaskData.des_path))

# if __name__ == '__main__':
#     import method.shotgun.get_task as get_task
#
#     _taskdata = get_task.TaskInfo('common_fish_001.drama_rig.v002.ma', 'X3', 'maya', 'publish')
#     print(processPublish(_taskdata, down=True, up=True))
