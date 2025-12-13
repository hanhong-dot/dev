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
import re
import apps.batch.xmlio as xmlio

class EntityData(object):

    def __init__(self):
        self.project_name = ''
        self.project_type = ''
        self.task_type = ''
        self.step = ''
        self.asset_type = ''
        self.task_engine = ''
        self.task_name = ''


class GetXMLData(object):

    def __init__(self, entity_data):
        super(GetXMLData, self).__init__()
        self._project_name = entity_data.project_name
        self._project_type = entity_data.project_type
        self._task_type = entity_data.task_type
        self._step = entity_data.step
        self._asset_type = entity_data.asset_type
        self._task_engine = entity_data.task_engine
        self._task_name = entity_data.task_name

    def _get_batch_xml_path(self, xml_name):

        _common_path = ('Z:/dev/apps/batch/config/{}').format(self._project_name).replace('\\', '/')
        return ('{}/{}').format(_common_path, xml_name)

    def batch_process_data(self, xml_name):
        """
        从xml获取process的数据 当配置文件中project有值后会额外加载project项目的item，当project为common时额外先加载common的item，直到当project
        为空时只加载当前项目；会按order排序
        :return: 列表
        """
        xml_path = self._get_batch_xml_path(xml_name)
        if not xml_path:
            return []
        datas = []
        xml_data = xmlio.SelectXML(xml_path)
        xml_datas = xml_data.select_iterattr2('process_tab')
        datas.append(sorted(xml_datas, key=(lambda keys: int(keys['order_id']))))
        return sum(datas, [])

    def process_data(self, xml_name):
        """
        从xml获取process的数据 当配置文件中project有值后会额外加载project项目的item，当project为common时额外先加载common的item，直到当project
        为空时只加载当前项目；会按order排序
        :return: 列表
        """
        xml_path = self._get_xml_path(xml_name)
        if not xml_path:
            return []
        datas = []
        while True:
            xml_data = xmlio.SelectXML(xml_path)
            project = xml_data.root.attrib['project']
            xml_datas = xml_data.select_iterattr2('process_tab')
            datas.append(sorted(xml_datas, key=(lambda keys: int(keys['order_id']))))
            if project and project != 'common':
                xml_path = xml_path.replace(re.findall('projects/.*?/', xml_path)[0].split('/')[1], project)
            elif project and project == 'common':
                xml_path = xml_path.replace(re.findall('projects/.*?/', xml_path)[0], 'common/')
            else:
                break

        datas.reverse()
        return sum(datas, [])

    def _remove_specialfactor(self, list_datas):
        """
        移除xml中key为 except_project和except_projectType的元素
        :param list_datas:原始列表
        :return:移除掉元素的列表
        """
        del_index = []
        for i in range(len(list_datas)):
            for key, value in list_datas[i].items():
                if key == 'except_project' and value == self._project_name:
                    del_index.append(i)
                if key == 'projectType' and value != 'all' and value != self._project_type:
                    del_index.append(i)
                if key == 'except_projectType' and value == self._project_type:
                    del_index.append(i)

        del_index = list(set(del_index))
        del_index.sort()
        remove_list = list_datas
        if del_index:
            for num, i in enumerate(del_index):
                remove_list.pop(i - num)

        return remove_list

    def get_launch_process_data(self, xml_name):
        """
        获取最终process数据
        :return: 列表
        """
        processlist = self.launch_process_data(xml_name)
        if processlist:
            return self._remove_specialfactor(processlist)
        return []

    def get_batch_process_data(self, xml_name):
        """
        获取最终process数据
        :return: 列表
        """
        processlist = self.batch_process_data(xml_name)
        if processlist:
            return self._remove_specialfactor(processlist)
        return []

    def get_process_data(self, xml_name):
        """
        获取最终process数据
        :return: 列表
        """
        processlist = self.process_data(xml_name)
        if processlist:
            return self._remove_specialfactor(processlist)
        return []

    def get_launch_process_cmds(self):
        """
        按顺序获取process_comnand
        :return: 列表
        """
        _process_cmds = []
        _processdata = self.get_launch_process_data()
        for obj in _processdata:
            if isinstance(obj, dict):
                if 'process_command' in obj.keys():
                    _process_cmds.append(obj['process_command'])

        return _process_cmds

    def get_right_process_cmds(self):
        """
        按顺序获取process_comnand
        :return: 列表
        """
        _process_cmds = []
        _processdata = self.get_process_data(False)
        for obj in _processdata:
            if isinstance(obj, dict):
                if 'process_command' in obj.keys():
                    _process_cmds.append(obj['process_command'])

        return _process_cmds

