# -*- coding: utf-8 -*-#
# Python       : python 2.7.16
# -------------------------------------------------------------------------------
# NAME         : get_data
# Describe     : 说明描述
# Version      : v0.01
# Author       : linhuan
# Email        : hanhong@papegames.net
# DateTime     : 2022/5/11__14:43
# -------------------------------------------------------------------------------
# -------------------------------------------------------------------------------
# example:
# 
# -------------------------------------------------------------------------------

__AUTHORZH__ = u"韩虹"
__AUTHOR__ = "linhuan"
__EMAIL__ = "hanhong@papegames.net"

import re, os
import lib.common.xmlio as xmlio
import lib.common as code_lib


class GetXLMData(object):
    def __init__(self, task_data=None, project_name='', task_type='', step='', asset_type='',
                 task_engine='', task_name='', entity_type=''):
        super(GetXLMData, self).__init__()
        if task_data:
            self.task_data = task_data
            self._project_name = self.task_data.project_name
            # self._project_type = self.task_data.project_type
            self._task_type = self.task_data.entity_type
            self._step = self.task_data.step_name
            self._asset_type = self.task_data.asset_type
            self._task_engine = self.task_data.task_launch_soft
            self._task_name = self.task_data.task_name
            self._entity_type = self.task_data.entity_type

        else:
            self._project_name = project_name
            self._task_type = entity_type
            self._step = step
            self._asset_type = asset_type
            self._task_engine = task_engine
            self._task_name = task_name
            self._entity_type = entity_type

    def _get_xml_path(self, xml_name):
        '''
        获取 xml的配置文件
        :return:
        '''
        _conf_dir_dict = self._get_xml_dir()
        if _conf_dir_dict and 'project_dir' in _conf_dir_dict and 'common_dir' in _conf_dir_dict:
            _project_xml_file = u"{}/{}".format(_conf_dir_dict['project_dir'], xml_name)
            _common_xml_file = u"{}/{}".format(_conf_dir_dict['common_dir'], xml_name)
            _base_xml_file = u"{}/{}".format(_conf_dir_dict['base_dir'], xml_name)
            if _project_xml_file and os.path.exists(_project_xml_file):
                return _project_xml_file
            else:
                if _common_xml_file and os.path.exists(_common_xml_file):
                    return _common_xml_file
                else:
                    if _base_xml_file and os.path.exists(_base_xml_file):
                        return _base_xml_file
                    else:
                        try:
                            raise Exception(u'没找到相关的{}配置文件，请TD检查下'.format(xml_name).encode('gbk'))
                        except:
                            raise Exception(u'没找到相关的{}配置文件，请TD检查下'.format(xml_name))

    def _get_xml_dir(self):
        u"""
        根据任务获取配置路径
        :return:
        """
        _dict = {}
        _base_dir = code_lib.publish_config_path().replace('\\', '/')
        if self._entity_type.lower() == 'asset':
            _dict['base_dir'] = u'{}/common/{}/{}/{}/{}'.format(_base_dir, self._entity_type.lower(),
                                                                self._step, self._task_name, self._task_engine)
            _dict['common_dir'] = u'{}/common/{}/{}/{}/{}/{}'.format(_base_dir, self._entity_type.lower(),
                                                                     self._asset_type,
                                                                     self._step, self._task_name, self._task_engine)
            _dict['project_dir'] = u'{}/projects/{}/{}/{}/{}/{}/{}'.format(_base_dir, self._project_name.lower(),
                                                                           self._entity_type.lower(),
                                                                           self._asset_type,
                                                                           self._step, self._task_name,
                                                                           self._task_engine)
        else:
            _dict['base_dir'] = u'{}/common/{}/{}/{}'.format(_base_dir, self._entity_type.lower(), self._task_name,
                                                             self._task_engine)
            _dict['common_dir'] = u'{}/common/{}/{}/{}/{}'.format(_base_dir, self._entity_type.lower(),
                                                                  self._step, self._task_name, self._task_engine)
            _dict['project_dir'] = u'{}/projects/{}/{}/{}/{}/{}'.format(_base_dir, self._project_name.lower(),
                                                                        self._entity_type.lower(),
                                                                        self._step, self._task_name, self._task_engine)

        return _dict

    def _check_data(self):
        '''
        从xml获取check的数据 当配置文件中project有值后会额外加载project项目的item，当project为common时额外先加载common的item，直到当project
        为空时只加载当前项目；会按order排序
        :return: 列表
        '''
        # xml_data = xmlio.SelectXML(self.xml_path + '/check_config.xml')
        # return sorted(xml_data.select_iterattr('checkItem'), key=lambda keys: keys['order_id'])

        datas = []
        xml_path = self._get_xml_path('check_config.xml')
        if not xml_path:
            try:
                raise Exception(u'没找到相关的check_config.xml配置文件，请TD检查下'.encode('gbk'))
            except:
                raise Exception('没找到相关的check_config.xml配置文件，请TD检查下')
        while True:
            xml_data = xmlio.SelectXML(xml_path)
            project = xml_data.root.attrib['project']
            if project and project != 'common':
                datas.append(sorted(xml_data.select_iterattr('checkItem'), key=lambda keys: int(keys['order_id'])))
                xml_path = xml_path.replace(re.findall(r"projects/.*?/", xml_path)[0].split('/')[1],
                                            project)
            elif project and project == 'common':
                datas.append(sorted(xml_data.select_iterattr('checkItem'), key=lambda keys: int(keys['order_id'])))
                xml_path = xml_path.replace(re.findall(r"projects/.*?/", xml_path)[0], 'common/')
            else:
                datas.append(sorted(xml_data.select_iterattr('checkItem'), key=lambda keys: int(keys['order_id'])))
                break

        datas.reverse()
        return sum(datas, [])

    def _process_data(self):

        '''
        从xml获取process的数据 当配置文件中project有值后会额外加载project项目的item，当project为common时额外先加载common的item，直到当project
        为空时只加载当前项目；会按order排序
        :return: 列表
        '''
        xml_path = self._get_xml_path('process_config.xml')
        if not xml_path:
            try:
                raise Exception(u'没找到相关的process_config.xml配置文件，请TD检查下'.encode('gbk'))
            except:
                raise Exception('没找到相关的process_config.xml配置文件，请TD检查下')
        datas = []
        while True:
            xml_data = xmlio.SelectXML(xml_path)
            project = xml_data.root.attrib['project']
            if project and project != 'common':
                datas.append(sorted(xml_data.select_iterattr('processItem'), key=lambda keys: int(keys['order_id'])))
                xml_path = xml_path.replace(re.findall(r"projects/.*?/", xml_path)[0].split('/')[1],
                                            project)
            elif project and project == 'common':
                datas.append(sorted(xml_data.select_iterattr('processItem'), key=lambda keys: int(keys['order_id'])))
                xml_path = xml_path.replace(re.findall(r"projects/.*?/", xml_path)[0], 'common/')
            else:
                datas.append(sorted(xml_data.select_iterattr('processItem'), key=lambda keys: int(keys['order_id'])))
                break

        datas.reverse()
        return sum(datas, [])

    def _meidadata(self):
        '''
        从xml获取media的数据 当配置文件中project有值后会额外加载project项目的item，当project为common时额外先加载common的item，直到当project
        为空时只加载当前项目；会按order排序
        :return: 列表
        '''
        # xml_data = xmlio.SelectXML(self.xml_path + '/check_config.xml')
        # return sorted(xml_data.select_iterattr('checkItem'), key=lambda keys: keys['order_id'])

        datas = []
        xml_path = self._get_xml_path('media_config.xml')
        if xml_path:
            while True:
                xml_data = xmlio.SelectXML(xml_path)
                project = xml_data.root.attrib['project']
                if project and project != 'common':
                    datas.append(sorted(xml_data.select_iterattr('checkItem'), key=lambda keys: int(keys['order_id'])))
                    xml_path = xml_path.replace(re.findall(r"projects/.*?/", xml_path)[0].split('/')[1],
                                                project)
                elif project and project == 'common':
                    datas.append(sorted(xml_data.select_iterattr('checkItem'), key=lambda keys: int(keys['order_id'])))
                    xml_path = xml_path.replace(re.findall(r"projects/.*?/", xml_path)[0], 'common/')
                else:
                    datas.append(sorted(xml_data.select_iterattr('checkItem'), key=lambda keys: int(keys['order_id'])))
                    break

        datas.reverse()
        return sum(datas, [])

    def _remove_specialfactor(self, list_datas):
        '''
        移除xml中key为 except_project和except_projectType的元素
        :param list_datas:原始列表
        :return:移除掉元素的列表
        '''
        del_index = []
        if list_datas:
            for i in range(len(list_datas)):
                for key, value in list_datas[i].items():
                    if key == 'except_project' and value == self._project_name:
                        del_index.append(i)
                    if key == 'projectType' and value != 'all':
                        del_index.append(i)
                # if key == 'except_projectType' and value == self._project_type:
                # 	del_index.append(i)

        del_index = list(set(del_index))

        remove_list = list_datas
        if del_index:
            for num, i in enumerate(del_index):
                remove_list.pop(i - num)

        return remove_list

    def get_checkdata(self):
        '''
        获取最终check数据
        :return: 列表
        '''
        checklist = self._check_data()
        return self._remove_specialfactor(checklist) if checklist else None

    def get_processdata(self):
        '''
        获取最终process数据
        :return: 列表
        '''
        processlist = self._process_data()
        return self._remove_specialfactor(processlist) if processlist else None

    def get_processcmds(self):
        '''
        按顺序获取process_comnand
        :return: 列表
        '''
        _process_cmds = []
        _processdata = self.get_processdata()
        if _processdata:
            for obj in _processdata:
                if isinstance(obj, dict):
                    if 'process_command' in obj.keys():
                        _process_cmds.append(obj['process_command'])
        return _process_cmds

    def get_publishdata(self):
        '''
        从xml获取publish基础数据
        :return: 元组 元素一代表状态列表，元素二代表媒体后缀列表,元素三代表sub代码(当projectType为all和获取的task_data.projectType相同时才生效) 元素四代表新标签名字
        '''

        xml_path = self._get_xml_path('publish_config.xml')
        if not xml_path:
            try:
                raise Exception(u'没找到相关的publish_config.xml配置文件，请TD检查下'.encode('gbk'))
            except:
                raise Exception('没找到相关的publish_config.xml配置文件，请TD检查下')
        xml_data = xmlio.SelectXML(xml_path)
        _sub_commond = xml_data.select_findallattr('sub_widget')[0]['widget_command'] if xml_data.select_findallattr(
            'sub_widget') else ''
        _sub_projectType = xml_data.select_findallattr('sub_widget')[0]['projectType'] if xml_data.select_findallattr(
            'sub_widget') else None
        _sub_name = xml_data.select_findallattr('sub_widget')[0]['widget_name'] if xml_data.select_findallattr(
            'sub_widget') else None
        if _sub_commond:
            if _sub_projectType == 'all':
                pass
            else:
                _sub_commond = ''
                _sub_name = None
        else:
            _sub_name = None

        return eval(xml_data.root.attrib['status_list']), eval(
            xml_data.root.attrib['media_suffix']), _sub_commond, _sub_name

    def get_meidadata(self):
        '''
        获取最终check_version数据
        :return: 列表
        '''
        checklist = self._meidadata()
        return self._remove_specialfactor(checklist) if checklist else None

# if __name__ == '__main__':
#     import method.shotgun.get_task as get_task
# # # #
# # # #     #
# # # #     xml_handle = GetXLMData(get_task.TaskInfo('PL003WST01.drama_rig.v001.ma', 'X3', 'maya', 'publish'))
# # # #     print(xml_handle._process_data())
# # # #     # shot_handle=GetXLMData(get_task.TaskInfo('seq000_sc001.ani_animation.v003.ma', 'testfn', 'maya', 'publish'))
# # # #     #
# # # #     #     # abc = GetXLMData(project_name='xcm_test',project_type='FILM',task_type='shot',step='ani',task_engine='maya',task_name='ani_animation')
# # # #     #     print xml_handle._meidadata()
# # # #     # print xml_handle._get_xml_dir()
# # # #     # print shot_handle._get_xml_path('check_config.xml')
# # # #     _filename = 'tdtest_roleacce.drama_mdl.v001.ma'
#     _filename=r'M:\projects\x3\work\shots\CutScene_ML_C10S1\CutScene_ML_C10S1_S01_P01\cts\mobu\CutScene_ML_C10S1_S01_P01.cts_rough.v004.fbx'
#     _project = 'X3'
#     _dcc = 'motionbuilder'
#     _taskdata= get_task.TaskInfo(_filename, _project, _dcc, 'publish')
#     xml_handle = GetXLMData(_taskdata)
#     print(xml_handle._get_xml_dir())
#     print(xml_handle._check_data())
#     print(xml_handle._get_xml_path())
