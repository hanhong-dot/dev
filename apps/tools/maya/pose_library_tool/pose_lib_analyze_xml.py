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

import os

XML_FILE='pose_right_menu_config.xml'

class GetXMLData(object):

    def __init__(self, data=None):
        super(GetXMLData, self).__init__()
        self.__data=data

    def _get_batch_xml_path(self, xml_name):
        __base_path = os.path.dirname(os.path.abspath(__file__))

        _common_path = ('{}/config').format(__base_path).replace('\\', '/')
        return ('{}/{}').format(_common_path, xml_name)

    def batch_process_data(self, xml_name):

        xml_path = self._get_batch_xml_path(xml_name)
        if not xml_path:
            return []
        datas = []
        xml_data = xmlio.SelectXML(xml_path)
        xml_datas = xml_data.select_iterattr2('process_tab')
        datas.append(sorted(xml_datas, key=(lambda keys: int(keys['order_id']))))
        return sum(datas, [])

    def process_data(self, xml_name):

        xml_path = self._get_batch_xml_path(xml_name)
        if not xml_path:
            return []
        datas = []

        xml_data = xmlio.SelectXML(xml_path)
        xml_datas = xml_data.select_iterattr2('process_tab')
        datas.append(sorted(xml_datas, key=(lambda keys: int(keys['order_id']))))

        datas.reverse()
        return sum(datas, [])

    def _remove_specialfactor(self, list_datas):
        """
        移除xml中key为 except_project和except_projectType的元素
        :param list_datas:原始列表
        :return:移除掉元素的列表
        """
        del_index = []

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
        _processdata = self.get_right_process_data(XML_FILE)
        for obj in _processdata:
            if isinstance(obj, dict):
                if 'process_command' in obj.keys():
                    _process_cmds.append(obj['process_command'])

        return _process_cmds


    def get_right_process_data_by_tab_name(self, xml_name,tab_name):
        """
        按顺序获取process_comnand
        :return: 列表
        """
        _process_cmds = []
        _processdata = self.get_process_data(xml_name)
        for obj in _processdata:
            if isinstance(obj, dict):
                __tab_name = obj['tab_name']
                if __tab_name == tab_name:
                    _process_cmds.append(obj)

        return _process_cmds


# if __name__ == '__main__':
#     data = {'tab_name': 'test', 'entity_data': {}}
#     xml_name = 'pose_right_menu_config.xml'
#     handle = GetXMLData(data)
#     process_data = handle.get_right_process_data_by_tab_name(xml_name,'Pose Library')
#     print(process_data)
