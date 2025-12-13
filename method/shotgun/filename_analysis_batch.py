# -*- coding: utf-8 -*-#
# Python       : python 2.7.16
# -------------------------------------------------------------------------------
# NAME         : filenae_analysis
# Describe     : 说明描述
# Version      : v0.01
# Author       : linhuan
# Email        : hanhong@papegames.net
# DateTime     : 2022/5/14__20:02
# -------------------------------------------------------------------------------
# -------------------------------------------------------------------------------
# example:
# 
# -------------------------------------------------------------------------------
import database.shotgun.core.sg_asset as sg_asset
import database.shotgun.core.sg_base as sg_base

import database.shotgun.core.sg_sequence as sg_sequence

import database.shotgun.core.sg_task as sg_task
import database.shotgun.core.sg_user as sg_user
import database.shotgun.core.sg_project as sg_project
import os
import database.shotgun.core.root_path as root_path

import database.shotgun.core.templates_analysis as temp_analysis




class FilenameAnalyze(object):

    def __init__(self, sg, filename, project, dcc, tag, delimiter='.', is_nextversion=True, ui=False):
        '''
        文件名解析
        :param sg sg实体
        :param filename: 文件名
        :param project: 项目名
        :param dcc: 软件
        :param tag: publish,version等templateas.yml的key中的标记
        :param delimiter: 分割符，现在以‘。’作为文件名分割
        :param is_nextversion: 从数据库上查询下个版本，默认是开启的
        '''

        super(FilenameAnalyze, self).__init__()
        self.sg = sg

        self._filename = os.path.basename(filename)

        self._delimiter = delimiter
        self._project = project
        self._dcc = dcc
        self._is_version = is_nextversion
        self.sg_login = sg
        self._tag = tag
        self.anlyzefilename = self._get_analyzefilename()
        self.current_user_name = self.get_current_user()
        self.ui = ui

        if not self.anlyzefilename or len(self.anlyzefilename.keys()) < 4:
            raise Exception(u'文件命名不正确，请检查'.encode('gbk'))
        self.entity_base = self.get_tasktype_id()

        if not self.entity_base:
            raise Exception(u'shotgun上没发现这个资产/镜头,请检查'.encode('gbk'))
        self.task_base = self.get_task()
        if not self.task_base:
            raise Exception(u'shotgun上没发现这个任务,请检查'.encode('gbk'))

    # if not self._project_id:
    # 	raise Exception(u'shotgun上没发现这个项目,请检查'.encode('GBK'))

    def get_current_user(self):
        u"""
        获得当月前用户名
        :return:
        """
        return sg_user.get_current_user()

    def get_current_user_data(self):
        u"""

        :return:
        """
        return sg_user.get_current_user_data(conf='Z:/dev/database/shotgun/toolkit/x3')

    def get_projectdir(self):
        u"""
        获得项目路径
        :return:
        """

        return root_path.RoothPath(self._project).project_root

    def get_entity_name(self):
        u"""
        获取实体名：例如资产名，镜头号
        :return:
        """
        return self.entity_base['entity_name']

    def get_entity_id(self):
        u"""
        获取实体id
        :return:
        """
        return self.entity_base['entity_id']

    def get_entity_type(self):
        u"""
        获取实体类型
        :return:
        """
        return self.entity_base['entity_type']

    def get_asset_type(self):
        u"""
        获取资产类型
        :return:
        """
        if self.get_entity_type() == 'Asset':
            return sg_asset.select_asset_entity(self.sg, self.get_entity_id())['sg_asset_type']
        else:
            return ''

    def get_shot(self):
        u"""
        获取镜头号
        :return:
        """
        if self.get_entity_type() and self.get_entity_type() == 'Shot':
            try:
                return self.get_entity_name()
            except:
                return ''
        else:
            return ''

    def get_seqence(self):
        u"""
        获取场次号
        :return:
        """
        if self.get_entity_type() == 'Shot':
            _seqence = sg_base.select_entity(self.sg, "Shot", self.get_entity_id(), ['sg_sequence'])
            if 'sg_sequence' in _seqence:
                return _seqence['sg_sequence']['name']
        if self.get_entity_type() == 'Sequence':
            return self.get_entity_name()

    def get_step(self):
        u"""
        获取环节名
        :return:
        """
        _task_id = self.get_taskid()

        _step = sg_base.select_entity(self.sg, 'Task', _task_id, fields=['step'])
        if _step:
            return _step['step']['name']

    def get_step_id(self):
        u"""
        获取环节id
        :return:
        """
        _task_id = self.get_taskid()

        _step = sg_base.select_entity(self.sg, 'Task', _task_id, fields=['step'])
        if _step:
            return _step['step']['id']

    def get_taskname(self):
        u"""
        获得任务名
        :return:
        """
        return self.task_base['task_name']

    def get_taskid(self):
        u"""
        获取任务id
        :return:
        """
        return self.task_base['task_id']

    def get_tasktype(self):
        u"""
        获取任务类型
        :return:
        """
        return self.entity_base['entity_type'].lower()

    def get_task(self):
        u"""
        获取任务名
        :return:
        """
        _entity_name = self.get_entity_name()
        try:
            _task_name = self.anlyzefilename[1]
            _id = sg_task.get_task_taskID(self.sg, self._project, _task_name, _entity_name)
            if _id:
                return {'task_name': _task_name, 'task_id': _id[0]['id'], 'task_type': _id[0]['type']}
        except:
            return

    def get_version(self):
        u"""
        获取版本
        :return:
        """
        return self.anlyzefilename[2]

    def get_versionnum(self):
        '''
        获取版本号
        :return:int型
        '''
        return self._get_vernum(self.get_version())

    def _get_vernum(self, filename):
        u"""
        根据命名获取版本号
        :param filename:文件名
        :return:
        """
        import re
        if filename:
            _filename = os.path.basename(filename)
            try:
                reg = re.compile(r"(?<=v)\d+")
                return reg.search(_filename).group(0).zfill(3)
            except:
                return 0

    def _get_analyzefilename(self):
        '''
        解析文件名
        :return:
        '''
        if self._filename and self._delimiter:
            temp = self._filename.split(self._delimiter)
            if temp:
                return {i: temp[i] for i in range(0, len(temp))}

    def get_project_type(self):
        u"""
        获取项目类型
        :return:
        """
        return sg_project.get_projecttype(self.sg, self._project_id)[0]['sg_type']

    def get_project_id(self):
        u"""
        获取项目id
        :return:
        """
        try:
            return sg_project.get_project_projectID(self.sg, self._project)[0]['id']
        except:
            return ''

    def get_project_soft(self):
        u"""
        获取项目软件及版本
        :return:
        """
        project_id = self.get_project_id()
        try:
            return eval(sg_project.select_project_project(self.sg, project_id, project_fields=['sg_software'])[
                            'sg_software'])
        except:
            return {}

    def get_tasktype_id(self):

        u"""
        获得文件类型(asset ,shot)
        """
        _entityname = self.anlyzefilename[0]

        try:
            _id = sg_asset.select_asset_assetID(self.sg, self._project, _entityname)
            if _id:

                return {'entity_type': _id[0]['type'], 'entity_id': _id[0]['id'], 'entity_name': _entityname}
            else:
                _id = sg_base.select_entity_id(self.sg, self._project, entity_type='Shot', entity_name=_entityname)
                if _id:
                    return {'entity_type': _id[0]['type'], 'entity_id': _id[0]['id'], 'entity_name': _entityname}
                else:
                    _id = sg_sequence.select_sequence_ID(self.sg, self._project, _entityname, episode_name='')
                    if _id:
                        return {'entity_type': _id[0]['type'], 'entity_id': _id[0]['id'],
                                'entity_name': _entityname}

        except:
            return

    def _last_version_info(self):
        # return 'asset.ca001008.mod_hig.v006.jpg'
        _entityname = self.get_entity_name()
        _taskIDs = sg_task.get_task_taskID(self.sg_login, self._project, self.get_taskname(), _entityname)
        if _taskIDs:
            return sg_task.select_task_version(self.sg_login, _taskIDs[0]['id'], ['code'], add='latest')
        else:
            try:
                raise Exception(u'数据库中无法找到该任务的ID，请检查'.encode("gbk"))
            except:
                raise Exception('数据库中无法找到该任务的ID，请检查')

    def _last_version_name(self):
        u"""
        最后版本version 名
        :return:
        """
        _last_version_info = self._last_version_info()
        try:
            return _last_version_info[0]['code']
        except:
            return ''

    def _last_version_id(self):
        u"""
        最后版本version id
        :return:
        """
        _last_version_info = self._last_version_info()
        try:
            return _last_version_info[0]['id']
        except:
            return ''

    def last_version_num(self):
        u"""
        获取最后版本
        :return:
        """
        code = self._last_version_name()
        if code:
            return self._get_vernum(code)
        else:
            return 0

    def get_publishdir(self):
        u"""
        获取work路径
        """

        _path_handle = temp_analysis.AnalysisMayaTemplates(self._project, self.get_entity_type().lower(),
                                                           self.get_entity_name(),
                                                           self.get_step(),
                                                           self.get_taskname(), False,
                                                           self.get_asset_type(),
                                                           self._dcc)
        return _path_handle.get_publish_dir()

    def get_workdir(self):
        u"""
        获取work路径
        """

        _path_handle = temp_analysis.AnalysisMayaTemplates(self._project, self.get_entity_type().lower(),
                                                           self.get_entity_name(),
                                                           self.get_step(),
                                                           self.get_taskname(), False,
                                                           self.get_asset_type(),
                                                           self._dcc)
        return _path_handle.get_work_dir()

    def get_workdata_dir(self):
        u"""
        获得work data 路径
        """
        _path_handle = temp_analysis.AnalysisMayaTemplates(self._project, self.get_entity_type().lower(),
                                                           self.get_entity_name(),
                                                           self.get_step(),
                                                           self.get_taskname(), False,
                                                           self.get_asset_type(),
                                                           self._dcc)
        return _path_handle.get_work_data()

    def get_publishdata_dir(self):
        u"""
        获得publish data 路径
        """
        _path_handle = temp_analysis.AnalysisMayaTemplates(self._project, self.get_entity_type().lower(),
                                                           self.get_entity_name(),
                                                           self.get_step(),
                                                           self.get_taskname(), False,
                                                           self.get_asset_type(),
                                                           self._dcc)
        return _path_handle.get_publish_data()

    def get_despath(self):
        '''
        获取上传的目标全路径
        :return:
        '''
        _path_handle = temp_analysis.AnalysisMayaTemplates(self._project, self.get_entity_type().lower(),
                                                           self.get_entity_name(),
                                                           self.get_step(),
                                                           self.get_taskname(), self.next_version(),
                                                           self.get_asset_type(),
                                                           self._dcc)

        return _path_handle.get_publish_entitiename()

    def get_workpath(self):
        '''
        获取work的目标全路径
        :return:
        '''
        _path_handle = temp_analysis.AnalysisMayaTemplates(self._project, self.get_entity_type().lower(),
                                                           self.get_entity_name(),
                                                           self.get_step(),
                                                           self.get_taskname(), self.next_version(),
                                                           self.get_asset_type(),
                                                           self._dcc)

        return _path_handle.get_work_entitiename()

    def last_version(self):
        '''
        获取最新版本号
        :return: 字符串
        '''
        return str(self.last_version_num()).zfill(3)

    def next_version(self):
        '''
        获取下一个版本号
        :return: 字符串
        '''
        return str(int(self.last_version_num()) + 1).zfill(3)

    def get_thubnail_publish(self):
        u"""
        获取publish 缩略图
        """
        _path_handle = temp_analysis.AnalysisMayaTemplates(self._project, self.get_entity_type().lower(),
                                                           self.get_entity_name(),
                                                           self.get_step(),
                                                           self.get_taskname(), self.next_version(),
                                                           self.get_asset_type(),
                                                           self._dcc)
        return _path_handle.get_thubnail_publish()

    def get_publish_version(self):
        u"""
        获取publish 缩略图
        """
        _path_handle = temp_analysis.AnalysisMayaTemplates(self._project, self.get_entity_type().lower(),
                                                           self.get_entity_name(),
                                                           self.get_step(),
                                                           self.get_taskname(), self.next_version(),
                                                           self.get_asset_type(),
                                                           self._dcc)
        return _path_handle.get_version_dir()

# if __name__ == '__main__':
#     import database.shotgun.core.sg_analysis as sg_analysis
# #
# #     # 获得资产信息
#     sg = sg_analysis.Config().login()
#
#     filename = 'book_ysroom_001c.drama_rig.v004.fbx'
#     project = 'X3'
#     dcc = 'unity'
#     tag = 'publish'
#     asset_handle = FilenameAnalyze(sg, filename, project, dcc, tag,ui=True)
#     # print(asset_handle._get_analyzefilename())
#     print(asset_handle.get_publish_version())
# #     filename = 'ST001S.drama_rig.v001.ma'
# #     print asset_handle.get_thubnail_publish()
# #     filename ='ML_C1S1_S01_P01.anim_final.v001.ma'
#     shot_handle=FilenameAnalyze(sg, filename, project, dcc, tag)
#     print shot_handle.get_step()
