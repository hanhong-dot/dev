# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       : batch_ui
# Describe   : 说明描述
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2023/12/30__14:54
# -------------------------------------------------------


import copy, datetime, json, shutil, socket, tempfile, time, urllib
from PySide2.QtWidgets import *
import apps.batch.analyze_xml as analyze_xml
import os
import enum


def convert_None_to_Str(x):
    ret = copy.deepcopy(x)
    if isinstance(x, dict):
        for k, v in ret.items():
            ret[k] = convert_None_to_Str(v)

    if x is None:
        ret = ''
    return ret


def json_datetime_converter(j):
    if isinstance(j, datetime.datetime):
        return j.__str__()


def json_dumps(dict_data):
    return json.dumps(dict_data, default=json_datetime_converter)


def json_dumps_ascii(dict_data):
    return json.dumps(dict_data, default=json_datetime_converter, ensure_ascii=False)


def json_loads(str_data):
    return json.loads(str_data)


def get_host_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()

    return ip


def get_treeview_level(treeview_indexes):
    treeview_level = -1
    if treeview_indexes:
        index = treeview_indexes[0]
        treeview_level = 0
        while index.parent().isValid():
            index = index.parent()
            treeview_level += 1

    return treeview_level


def get_right_filter_after_list(entity, dcc, item_attr_type, entity_list):
    project_name = ''
    project_type = ''
    task_type = ''
    asset_type = ''
    step = ''
    task_name = ''
    task_engine = dcc
    if entity:
        entity_type = entity['type']
        if entity_type == 'Task':
            project_name = entity['project']['name']
            project_type = entity['project.Project.sg_type']
            task_type = entity['entity']['type']
            asset_type = entity['entity.Asset.sg_asset_type']
            step = entity['step']['name']
            task_name = entity['content']
    entity_data = analyze_xml.EntityData()
    entity_data.project_name = project_name
    entity_data.project_type = project_type
    entity_data.task_type = task_type.lower()
    entity_data.asset_type = asset_type.lower() if asset_type else None
    entity_data.step = step.lower()
    entity_data.task_name = task_name.lower()
    entity_data.task_engine = task_engine.lower()
    xml_name = 'right_process_filter_config.xml'
    action_list = analyze_xml.GetXMLData(entity_data).get_process_data(xml_name)
    if action_list:
        for action_info in action_list:
            tab_name = action_info['tab_name']
            if tab_name and tab_name == item_attr_type.lower():
                entity_list_temp = list()
                for entity_temp in entity_list:
                    entity_list_temp.append(convert_None_to_Str(entity_temp))

                commands = action_info['process_command']
                result_list = process_filter(commands, entity_list_temp)
                return result_list

            return entity_list
        return entity_list
    return


def create_menu(menu_dict):
    project_name = ''
    project_type = ''
    task_type = ''
    asset_type = ''
    step = ''
    task_name = ''
    task_engine = menu_dict['dcc']
    level_entity = menu_dict['level_entity']
    entity_list = menu_dict['entity_list']
    if level_entity:
        entity = level_entity
        entity_type = entity['type']
        if entity_type == 'Task':
            project_name = entity['project']['name']
            project_type = entity['project.Project.sg_type']
            task_type = entity['entity']['type']
            asset_type = entity['entity.Asset.sg_asset_type']
            step = entity['step']['name']
            task_name = entity['content']
        elif entity_type == 'Asset':
            project_name = entity['project']['name']
            project_type = entity['project.Project.sg_type']
            task_type = entity['type']
            asset_type = entity['sg_asset_type']
        if entity_type == 'Shot':
            project_name = entity['project']['name']
            project_type = entity['project.Project.sg_type']
            task_type = entity['type']
        else:
            if entity_type == 'Sequence':
                project_name = entity['project']['name']
                project_type = entity['project.Project.sg_type']
                task_type = entity['type']
            elif entity_type == 'Episode':
                project_name = entity['project']['name']
                project_type = entity['project.Project.sg_type']
                task_type = entity['type']
    entity_data = analyze_xml.EntityData()
    entity_data.project_name = project_name
    entity_data.project_type = project_type
    entity_data.task_type = task_type.lower()
    entity_data.asset_type = asset_type.lower() if asset_type else None
    entity_data.step = step.lower()
    entity_data.task_name = task_name.lower()
    entity_data.task_engine = task_engine.lower()
    if menu_dict['is_left']:
        xml_name = 'left_process_config.xml'
    else:
        xml_name = 'right_process_config.xml'
    action_list = analyze_xml.GetXMLData(entity_data).get_process_data(xml_name)
    if action_list:
        add_menu_action(menu_dict, action_list, entity_list)
        return True
    else:
        return False


def add_menu_action(menu, action_list, entity_list):
    for action_info in action_list:
        text = action_info['item_name']
        tool_tip = action_info['toolTip']
        tab_name = action_info['tab_name']
        if tab_name:
            if tab_name == menu['widget_type']:
                data = dict()
                data['commands'] = action_info['process_command']
                data['entity_list'] = entity_list
                action = QAction(menu['menu_obj'])
                action.setText(text)
                action.setData(data)
                action.setToolTip(tool_tip)
                menu['menu_obj'].addAction(action)
        else:
            data = dict()
            data['commands'] = action_info['process_command']
            data['entity_list'] = entity_list
            action = QAction(menu['menu_obj'])
            action.setText(text)
            action.setData(data)
            action.setToolTip(tool_tip)
            menu['menu_obj'].addAction(action)


def right_menu_action_clicked_process(action):
    action_data = action.data()
    commands = action_data['commands']
    file_list = []
    entity_list = action_data['entity_list']
    call_back_func = None
    entity_list_temp = []
    for entity in entity_list:
        if 'call_back_func' in entity:
            call_back_func = entity['call_back_func']
            entity.pop('call_back_func', None)
        if 'sg_src_path' in entity:
            file_list.append(entity['sg_src_path'])
        entity_list_temp.append(convert_None_to_Str(entity))

    process_action(commands, file_list, entity_list_temp, call_back_func)
    return


def process_action(commands, file_list, entity_list, call_back_func):
    """
    :param commands:
    :param file_list:
    :param entity_list:
    :param call_back_func:
    #接收相关的数据并进行相应的处理
    """
    can_do = False
    if 'entity_list' in commands and entity_list:
        exec_order = commands.replace('entity_list',
                                      json.dumps(entity_list, default=json_datetime_converter, ensure_ascii=False))
        can_do = True
    elif 'filename_list' in commands and file_list:
        exec_order = commands.replace('filename_list', json.dumps(file_list))
        can_do = True
    if can_do:
        exec(exec_order)
        if call_back_func:
            call_back_func()


def process_filter(commands, entity_list):
    can_do = False
    result_list = list()
    import_path = str()
    import_path_list = commands.split(';')[:-1]
    for import_path_temp in import_path_list:
        import_path += import_path_temp
        import_path += ';'

    command = commands.split(';')[-1]
    if 'entity_list' in command and entity_list:
        exec_order = command.replace('entity_list',
                                     json.dumps(entity_list, default=json_datetime_converter, ensure_ascii=False))
        can_do = True
    if can_do:
        exec(import_path)
        result_list = eval(exec_order)
    return result_list


def timestamp_to_time(timestamp):
    return time.strftime('%Y/%m/%d %H:%M:%S', time.localtime(timestamp))


def timestamp_to_datetime(timestamp):
    return datetime.datetime.fromtimestamp(timestamp)


def download_thumbnail(entity_id, thumbnail_path):
    url = thumbnail_path
    temp_image_file = tempfile.gettempdir() + '\\' + str(entity_id) + '.jpg'
    if url:
        urllib.urlretrieve(url, temp_image_file)
        return temp_image_file
    else:
        return ''


def write_list_to_file(file_name, file_data_list):
    if file_data_list:
        with open(file_name, 'w') as (f):
            json.dump(file_data_list, f)


def read_list_from_file(file_name):
    file_data_list = list()
    if os.path.exists(file_name):
        with open(file_name, 'r') as (f):
            file_data_list = json.load(f)
    return file_data_list


def call_back_function(call_function):
    call_function()


def get_file_path_list(urls):
    """
    get file path from listwidget item
    :param urls: from MyQListWidget signal
    :return: file full path list
    """
    full_paths = []
    urls[0] = unicode(urls[0], 'utf-8')
    if os.path.isdir(urls[0]):
        for file_name in os.listdir(urls[0]):
            full_path = os.path.join(urls[0], file_name)
            if os.path.isfile(full_path):
                full_path = full_path.replace('\\', '/')
                full_paths.append(full_path)

    else:
        for url in urls:
            full_paths.append(url)

    return full_paths


def show_messagebox(msg_type, msg_text, msg_info=None):
    msg = QMessageBox()
    if msg_type == 'I':
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle('Information')
    elif msg_type == 'W':
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle('Warning')
    elif msg_type == 'E':
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle('Error')
    msg.setText(msg_text)
    msg.setInformativeText(msg_info)
    msg.setStandardButtons(QMessageBox.Ok)
    msg.exec_()


def match_extension_file(file_paths, extensions):
    for file_path in file_paths:
        if not file_path.lower().endswith(extensions):
            return False

    return True


def copy_file(src_path, dest_path):
    if not os.path.isfile(src_path):
        print('%s not exit!' % src_path)
    else:
        fpath, fname = os.path.split(dest_path)
        if not os.path.exists(fpath):
            os.makedirs(fpath)
        if not os.path.exists(dest_path):
            shutil.copyfile(src_path, dest_path)


def delete_file(file_path):
    if os.path.exist(file_path):
        os.remove(file_path)
    else:
        print('no such file: %s' % file_path)


def get_file_size_in_bytes(file_path):
    """ Get size of file at given path in bytes"""
    size = os.path.getsize(file_path)
    return size


def get_file_size_in_bytes_2(file_path):
    """ Get size of file at given path in bytes"""
    stat_info = os.stat(file_path)
    size = stat_info.st_size
    return size


def get_file_size_in_bytes_3(file_path):
    """ Get size of file at given path in bytes"""
    size = os.stat(file_path).st_size
    return size


class SIZE_UNIT(enum.Enum):
    BYTES = 1
    KB = 2
    MB = 3
    GB = 4


def convert_unit(size_in_bytes, unit):
    """ Convert the size from bytes to other units like KB, MB or GB"""
    if unit == SIZE_UNIT.KB:
        return size_in_bytes / 1024
    else:
        if unit == SIZE_UNIT.MB:
            return size_in_bytes / 1048576
        if unit == SIZE_UNIT.GB:
            return size_in_bytes / 1073741824
        return size_in_bytes


def get_file_size(file_name, size_type=SIZE_UNIT.BYTES):
    size = os.path.getsize(file_name)
    return convert_unit(size, size_type)
