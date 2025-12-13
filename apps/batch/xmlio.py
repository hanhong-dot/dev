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
import xml.etree.ElementTree as ET

class SelectXML(object):
    """
    解析 publish config XML文件信息的类
    """

    def __init__(self, xml_path):
        """
        输入 完整xml文件路径，初始化xml根节点信息
        Args:
            xml_path (str): publish config xml 文件完整路径
        """
        tree = ET.parse(xml_path)
        self.root = tree.getroot()

    def select_iterattr(self, tag):
        """
        传递指定的标签，其下的所有子树（其子代，子代等等）上进行递归迭代
        :param tag: 标签
        :return: 属性字典的列表
        """
        return [ obj.attrib for obj in self.root.iter(tag) ]

    def select_findallattr(self, tag):
        """
        仅查找带有标签的元素，这些标签是当前元素的直接子元素
        :param tag:标签
        :return:属性字典的列表
        """
        return [ obj.attrib for obj in self.root.findall(tag) ]

    def select_iterattr2(self, tag, tab_name=''):
        """
        仅查找带有标签的元素，这些标签是当前元素的直接子元素
        :param tag:标签
        :return:属性字典的列表
        """
        ret = []
        if tab_name:
            for obj in self.root.iter(tag):
                if obj.get('tab_name') == tab_name:
                    items = obj.getchildren()
                    for item in items:
                        temp_dict = item.attrib
                        temp_dict['tab_name'] = obj.get('tab_name')
                        ret.append(temp_dict)

        else:
            for obj in self.root.iter(tag):
                items = obj.getchildren()
                for item in items:
                    temp_dict = item.attrib
                    temp_dict['tab_name'] = obj.get('tab_name')
                    ret.append(temp_dict)

        return ret

    def select_findattr(self, tag):
        """
        查找具有特定标签的第一个孩子
        :param tag:标签
        :return:属性字典的列表
        """
        return [ obj.attrib for obj in self.root.find(tag) ]