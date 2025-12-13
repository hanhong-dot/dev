# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       : templates_analysis
# Describe   : 说明描述
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2022/5/23__19:00
# -------------------------------------------------------
import os

import sys
# reload(sys)
# sys.setdefaultencoding('utf8')
# import sys
#
# sys.path.append('Y:/development/Module/Ide/Python/2.7.18-x64/Lib/site-packages')

BASH_DIR = os.path.dirname(os.path.abspath(__file__))
import lib.common.yamlio as yamlio
try:
    import root_path as root_path
except:
    import database.shotgun.core.root_path as root_path


class AnalysisTemplates(object):
    def __init__(self, _project=None, _dcc='maya'):
        self._project = _project
        self._templates_info = yamlio.read2(self._templates_path())
        self.project_root = root_path.RoothPath(self._project).project_root
        self._dcc = _dcc

        if not self._templates_info:
            return

    def asset_root(self):
        """
        asset 变量目录
        """
        return self._templates_info['paths']['asset_root']

    def shot_root(self):
        """
        shot 变量目录

        """
        return self._templates_info['paths']['shot_root']

    def asset_work_maya(self):
        """
        资产work 路径
        """
        return self._templates_info['paths']['maya_asset_work']['definition'].replace('@asset_root',
                                                                                      self.asset_root())

    def asset_work_data(self):
        """
        资产work data 数据路径
        """
        return self._templates_info['paths']['work_asset_data_{}'.format(self._dcc)]['definition'].replace(
            '@asset_root',
            self.asset_root())

    def shot_work_data(self):
        """
        镜头work data 数据路径
        """
        return self._templates_info['paths']['work_shot_data_{}'.format(self._dcc)]['definition'].replace('@shot_root',
                                                                                                          self.shot_root())

    def asset_work_path(self):
        u"""
        获取work 路径
        """
        return self._templates_info['paths']['asset_work_area_{}'.format(self._dcc)]['definition'].replace(
            '@asset_root',
            self.asset_root())

    def shot_work_path(self):
        u"""
        获取work 路径
        """
        return self._templates_info['paths']['shot_work_area_{}'.format(self._dcc)]['definition'].replace('@shot_root',
                                                                                                          self.shot_root())

    def asset_thumbnail_work(self):
        u"""
        获取 缩略图 数据路径
        :return:
        """
        return self._templates_info['paths']['asset_thumbnail_work']['definition'].replace('@asset_root',
                                                                                           self.asset_root())

    def asset_thumbnail_publish(self):
        u"""
        获取 缩略图 数据路径
        :return:
        """
        return self._templates_info['paths']['asset_thumbnail_publish']['definition'].replace('@asset_root',
                                                                                              self.asset_root())

    def asset_version(self):
        u"""
        获取 缩略图 数据路径
        :return:
        """
        return self._templates_info['paths']['asset_version_dir']['definition'].replace('@asset_root',
                                                                                              self.asset_root())

    def shot_version(self):
        """

        :return:
        """
        return self._templates_info['paths']['shot_version_dir']['definition'].replace('@shot_root',
                                                                                             self.shot_root())


    def shot_thubnail_work(self):
        u"""

        :return:
        """
        return self._templates_info['paths']['shot_thumbnail_work']['definition'].replace('@shot_root',
                                                                                          self.shot_root())

    def shot_thubnail_publish(self):
        """

        :return:
        """
        return self._templates_info['paths']['shot_thumbnail_publish']['definition'].replace('@shot_root',
                                                                                             self.shot_root())

    def asset_publish_data(self):
        """
        资产work data 数据路径
        """
        return self._templates_info['paths']['publish_asset_data_{}'.format(self._dcc)]['definition'].replace(
            '@asset_root',
            self.asset_root())

    def shot_publish_data(self):
        """
        资产work data 数据路径
        """
        return self._templates_info['paths']['publish_shot_data_{}'.format(self._dcc)]['definition'].replace(
            '@shot_root',
            self.shot_root())

    def shot_publish_dir(self):
        return self._templates_info['paths']['shot_publish_area_{}'.format(self._dcc)]['definition'].replace('@shot_root',self.shot_root())
    def asset_publish_dir(self):
        return self._templates_info['paths']['asset_publish_area_{}'.format(self._dcc)]['definition'].replace('@asset_root',self.asset_root())

    def shot_work(self):
        """
        镜头work路径
        """
        return self._templates_info['paths']['{}_shot_work'.format(self._dcc)]['definition'].replace('@shot_root',
                                                                                                     self.shot_root())

    def asset_publish(self):
        """
        资产publish路径
        """
        return self._templates_info['paths']['{}_asset_publish_des'.format(self._dcc)]['definition'].replace('@asset_root',
                                                                                                         self.asset_root())

    def shot_publish(self):
        """
        资产publish路径
        """
        return self._templates_info['paths']['{}_shot_publish_des'.format(self._dcc)]['definition'].replace('@shot_root',
                                                                                                        self.shot_root())

    def _templates_path(self):
        u"""
        templates 模板文件
        """
        return u'{}/database/shotgun/toolkit/x3/config/core/templates.yml'.format(self._roothpath(),
                                                                                         self._project)

    def asset_work_tex_dir(self):
        u"""
        资产贴图 work路径
        """
        return self._templates_info['paths']['work_asset_tex']['definition'].replace('@asset_root',
                                                                                     self.asset_root())

    def asset_publish_tex_dir(self):
        u"""
        资产贴图 work路径
        """
        return self._templates_info['paths']['publish_asset_tex']['definition'].replace('@asset_root',
                                                                                        self.asset_root())

    def  asset_thumbnail(self):
        u"""
        资产缩略图路径
        :return:
        """

        return self._templates_info['paths']['asset_thumbnail']['definition'].replace('@asset_root',
                                                                                           self.asset_root())


    def shot_thubnail(self):
        u"""

        :return:
        """
        return self._templates_info['paths']['shot_thumbnail']['definition'].replace('@shot_root',
                                                                                          self.shot_root())

    def asset_task_thumbnail(self):
        u"""
        资产缩略图路径
        :return:
        """

        return self._templates_info['paths']['asset_task_thumbnail']['definition'].replace('@asset_root',
                                                                                      self.asset_root())
    def shot_task_thumbnail(self):
        u"""
        资产缩略图路径
        :return:
        """

        return self._templates_info['paths']['shot_task_thumbnail']['definition'].replace('@shot_root',
                                                                                      self.asset_root())


    def _roothpath(self):
        return BASH_DIR.split('database')[0]



    def asset_cover(self, _file, _assetname, _asset_type, _step, _taskname, _version, _ext):
        u"""
        资产模板转换
        """
        _dict = {'{Asset}': _assetname, '{asset_name}': _assetname, '{sg_asset_type}': _asset_type, '{Step}': _step,
                 '{task_name}': _taskname, '{version}': str(_version).zfill(3),
                 '{maya_extension}': _ext}
        for k, v in _dict.items():
            _file = _file.replace(k, v)

        return u"{}/{}".format(self.project_root, _file)

    def shot_cover(self, _file, _sequence, _shotname, _step, _taskname, _version, _ext):
        u"""
        镜头模板转换
        """
        _dict = {'{Sequence}': _sequence, '{Shot}': _shotname, '{Step}': _step, '{task_name}': _taskname,
                 '{version}': str(_version).zfill(3),
                 '{maya_extension}': _ext}
        for k, v in _dict.items():
            _file = _file.replace(k, v)
        return u"{}/{}".format(self.project_root, _file)




class AnalysisMayaTemplates(AnalysisTemplates):
    def __init__(self, _project='', _filetype='', _entitiename='', _step='', _task='', _version=1, _assettype=None, _dcc='maya'):
        AnalysisTemplates.__init__(self, _project,_dcc)
        # 项目名
        self._project = _project
        # 文件类型(shot,asset)
        self._filetype = _filetype
        # 资产名(镜头号)
        self._entitiename = _entitiename
        # 环节名
        self._step = _step
        # 任务名
        self._task = _task
        # 版本号
        self._version = _version
        # 资产类型
        self._assettype = _assettype

        # 文件后缀
        self._ext = ''

        self._dcc=_dcc
        if self._dcc == 'maya':
            self._ext = 'ma'
        elif self._dcc=='motionbuilder':
            self._ext='fbx'
        else:
            self._ext='fbx'



    def get_work_entitiename(self):
        u"""
        获得work文件(文件路径+文件名)
        """
        if self._filetype.lower() in ['asset']:
            _templates_asset = self.asset_work_maya()
            return self.asset_cover(_templates_asset, self._entitiename, self._assettype, self._step, self._task,
                                    self._version, self._ext)
        if self._filetype.lower() in ['shot']:
            _templates_shot = self.shot_work()
            _sequence = self._entitiename.split('_')[0]
            return self.shot_cover(_templates_shot, _sequence, self._entitiename, self._step, self._task,
                                   self._version, self._ext)

    def get_publish_entitiename(self):
        u"""
        获得publish文件(文件路径+文件名)
        """
        if self._filetype.lower() in ['asset']:
            _templates_asset = self.asset_publish()
            return self.asset_cover(_templates_asset, self._entitiename, self._assettype, self._step, self._task,
                                    self._version, self._ext)
        if self._filetype.lower() in ['shot']:
            _templates_shot = self.shot_publish()
            _sequence = self._entitiename.split('_')[0]
            return self.shot_cover(_templates_shot, _sequence, self._entitiename, self._step, self._task,
                                   self._version, self._ext)

    def get_work_root(self):
        u"""
        获得work 根目录
        """
        if self._filetype.lower() in ['asset']:
            _templates_asset = self.asset_root()
            return self.asset_cover(_templates_asset, self._entitiename, self._assettype, self._step, self._task,
                                    self._version, self._ext)
        if self._filetype.lower() in ['shot']:
            _templates_shot = self.shot_root()
            _sequence = self._entitiename.split('_')[0]
            return self.shot_cover(_templates_shot, _sequence, self._entitiename, self._step, self._task,
                                   self._version, self._ext)

    def get_publish_dir(self):
        u"""
        获取work 路径
        """
        if self._filetype.lower() in ['asset']:
            return self.asset_cover(self.asset_publish_dir(), self._entitiename, self._assettype, self._step,
                                    self._task,
                                    self._version, self._ext)
        if self._filetype.lower() in ['shot']:
            _templates_shot = self.shot_publish_dir()
            _sequence = self._entitiename.split('_')[0]
            return self.shot_cover(_templates_shot, _sequence, self._entitiename, self._step, self._task,
                                   self._version, self._ext)


    def get_work_dir(self):
        u"""
        获取work 路径
        """
        if self._filetype.lower() in ['asset']:
            return self.asset_cover(self.asset_work_path(), self._entitiename, self._assettype, self._step,
                                    self._task,
                                    self._version, self._ext)
        if self._filetype.lower() in ['shot']:
            _templates_shot = self.asset_work_path()
            _sequence = self._entitiename.split('_')[0]
            return self.shot_cover(_templates_shot, _sequence, self._entitiename, self._step, self._task,
                                   self._version, self._ext)

    def get_work_data(self):
        u"""
        获取work data数据路径
        """
        if self._filetype.lower() in ['asset']:
            return self.asset_cover(self.asset_work_data(), self._entitiename, self._assettype, self._step,
                                    self._task,
                                    self._version, self._ext)
        if self._filetype.lower() in ['shot']:
            _templates_shot = self.shot_work_data()
            _sequence = self._entitiename.split('_')[0]
            return self.shot_cover(_templates_shot, _sequence, self._entitiename, self._step, self._task,
                                   self._version, self._ext)

    def get_publish_data(self):
        u"""
        获取work data数据路径
        """
        if self._filetype.lower() in ['asset']:
            return self.asset_cover(self.asset_publish_data(), self._entitiename, self._assettype, self._step,
                                    self._task,
                                    self._version, self._ext)
        if self._filetype.lower() in ['shot']:
            _templates_shot = self.shot_publish_data()
            _sequence = self._entitiename.split('_')[0]
            return self.shot_cover(_templates_shot, _sequence, self._entitiename, self._step, self._task,
                                   self._version, self._ext)

    def get_thubnail_publish(self):
        u"""
        获取 缩略图数据路径
        :return:
        """

        if self._filetype.lower() in ['asset']:
            return self.asset_cover(self.asset_thumbnail_publish(), self._entitiename, self._assettype, self._step,
                                    self._task, self._version, self._ext)
        if self._filetype.lower() in ['shot']:
            _templates_shot = self.shot_thubnail_publish()
            _sequence = self._entitiename.split('_')[0]
            return self.shot_cover(_templates_shot, _sequence, self._entitiename, self._step, self._task,
                                   self._version, self._ext)

    def get_version_dir(self):
        u"""
        获取 缩略图数据路径
        :return:
        """

        if self._filetype.lower() in ['asset']:
            return self.asset_cover(self.asset_version(), self._entitiename, self._assettype, self._step,
                                    self._task, self._version, self._ext)
        if self._filetype.lower() in ['shot']:
            _templates_shot = self.shot_version()
            _sequence = self._entitiename.split('_')[0]
            return self.shot_cover(_templates_shot, _sequence, self._entitiename, self._step, self._task,
                                   self._version, self._ext)

    def get_thumbnail(self):
        u"""
        获取 缩略图数据路径
        :return:
        """

        if self._filetype.lower() in ['asset']:
            return self.asset_cover(self.asset_thumbnail(), self._entitiename, self._assettype, self._step,
                                    self._task, self._version, self._ext)
        if self._filetype.lower() in ['shot']:
            _templates_shot = self.shot_thumbnail()
            _sequence = self._entitiename.split('_')[0]
            return self.shot_cover(_templates_shot, _sequence, self._entitiename, self._step, self._task,
                                   self._version, self._ext)

    def get_task_thumbnail(self):
        u"""
        获取 缩略图数据路径
        :return:
        """

        if self._filetype.lower() in ['asset']:
            return self.asset_cover(self.asset_task_thumbnail(), self._entitiename, self._assettype, self._step,
                                    self._task, self._version, self._ext)
        if self._filetype.lower() in ['shot']:
            _templates_shot = self.shot_task_thumbnail()
            _sequence = self._entitiename.split('_')[0]
            return self.shot_cover(_templates_shot, _sequence, self._entitiename, self._step, self._task,
                                   self._version, self._ext)


    def get_work_data_path(self, _type):
        u"""
        获取 work data 下类型数据路径，比如贴图 tex
        """
        return os.path.join(self.get_work_data(), _type)

    def get_publish_data_path(self, _type):
        u"""
        获取 publish data 下类型数据路径，比如贴图 tex
        """
        return os.path.join(self.get_publish_data(), _type).replace('\\', '/')


