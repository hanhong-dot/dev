# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       : get_task_data
# Describe   : 获取task 信息
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2023/5/4__13:59
# -------------------------------------------------------
import os
import sys
# BASEDIR=os.path.dirname(os.path.abspath(__file__)).split('method')[0].replace('\\', '/')

# sys.path.append('{}/database/shotgun/toolkit/x3'.format(BASEDIR)

try:
    import sgtk
except:
    sys.path.append(r'Z:\dev\database\shotgun\toolkit\x3\install\core\python')
    import sgtk

TKPATH = r'Z:\dev\database\shotgun\toolkit\x3'

import database.shotgun.core.sg_task as sg_task




class TaskData(object):
    def __init__(self, _task_id=None, _task_type='Task', _path=TKPATH, _dcc='maya'):
        '''

        :param filename: 文件
        :param project: 项目名
        :param dcc: dcc
        :param thumbnail_down:
        :param is_lastversion:
        :param ui:
        '''
        self._entity_id = _task_id
        self._entity_type = _task_type
        self._path = _path
        self._tk = sgtk.sgtk_from_path(self._path)
        if self._entity_id and self._entity_type:
            self._context = self._get_context(self._entity_id, self._entity_type)
        else:
            self._context = self.get_current_context
        if not self._context:
            raise Exception('no context')
        self.ctx = self.get_context_f(self._context)
        self.project = self.ctx.project
        self.project_id = self.project['id']
        self.project_name = self.project['name']
        self.task_launch_soft = _dcc
        self.sg = self._tk.shotgun
        self.task_id = self.ctx.task['id']
        self.task_name = self.ctx.task['name']
        self.task_type = self.ctx.task['type']
        self.task_step = self.ctx.step['name']
        self.step_name= self.ctx.step['name']
        self.task_step_id = self.ctx.step['id']
        self.task_step_type = self.ctx.step['type']
        self.entity_id = self.ctx.entity['id']
        self.entity_name = self.ctx.entity['name']
        self.entity_type = self.ctx.entity['type']
        self.asset_type = self.get_asset_type()
        self.dcc = _dcc
        self.user = self.ctx.user


        self.sequence_name =self.get_seqence()

        self._version = self.get_laster_version()
        if self._version:
            self.version_name = self._version[0]['code']
            self.version_id = self._version[0]['id']
            self.version_type = self._version[0]['type']

            self.last_version_num = self.get_last_version_num()
        else:
            self.version_name = None
            self.version_id = None
            self.version_type = None
            self.last_version_num = 0
        self.next_version_num = self.last_version_num + 1

        self.next_publish_path = self.get_publish_path()
        self.next_work_path = self.get_work_path()

        self.laster_publish_path = self.get_publish_path(next=False)
        self.laster_work_path = self.get_work_path(next=False)

        self.publish_dir = self.get_publish_dir()
        self.work_dir = self.get_work_dir()

        self.publish_data_dir = self.get_publish_data()
        self.work_data_dir = self.get_work_data()

    def get_asset_type(self):
        u"""
        获取资产类型
        :return:
        """
        import database.shotgun.core.sg_asset as sg_asset
        import database.shotgun.core.sg_analysis as sg_analysis
        if self.entity_type== 'Asset':
            sg=sg_analysis.Config().login()
            return sg_asset.select_asset_entity(sg, self.entity_id)['sg_asset_type']
        else:
            return ''


    def get_publish_data(self):
        u"""
        获取publish路径
        :return:
        """
        _temp_key = 'publish_{}_data_{}'.format(self.entity_type.lower(), self.dcc)
        return self._get_path(self.ctx, _temp_key, self.last_version_num)

    def get_seqence(self):
        u"""
        获取场次号
        :return:
        """
        import database.shotgun.core.sg_base as sg_base
        import database.shotgun.core.sg_analysis as sg_analysis
        if self.entity_type == 'Shot':
            sg = sg_analysis.Config().login()
            _seqence = sg_base.select_entity(sg, "Shot", self.entity_id, ['sg_sequence'])
            if 'sg_sequence' in _seqence:
                return _seqence['sg_sequence']['name']



    def get_work_data(self):
        u"""
        获取work路径
        :return:
        """
        _temp_key = 'work_{}_data_{}'.format(self.entity_type.lower(), self.dcc)
        return self._get_path(self.ctx, _temp_key, self.last_version_num)

    def get_work_dir(self):
        u"""
        获取work路径
        :return:
        """
        _temp_key = '{}_work_area_{}'.format(self.entity_type.lower(), self.dcc)
        return self._get_path(self.ctx, _temp_key, self.last_version_num)

    def get_publish_dir(self):
        u"""
        获取publish路径
        :return:
        """
        _temp_key = '{}_publish_area_{}'.format(self.entity_type.lower(), self.dcc)
        return self._get_path(self.ctx, _temp_key, self.last_version_num)

    def get_work_path(self, next=True):
        u"""
        获取work路径
        :return:
        """
        _temp_key = '{}_{}_work'.format(self.dcc, self.entity_type.lower())
        _version_num = self._get_next_version_number(_temp_key)
        if next == True:
            return self._get_path(self.ctx, _temp_key, (_version_num + 1))
        else:
            return self._get_path(self.ctx, _temp_key, _version_num)

    def get_publish_path(self, next=True):
        u"""
        获取publish路径(新版本)
        :return:
        """
        _temp_key = '{}_{}_publish'.format(self.dcc, self.entity_type.lower())
        if next == True:
            return self._get_path(self.ctx, _temp_key, self.next_version_num)
        else:
            return self._get_path(self.ctx, _temp_key, self.last_version_num)

    def _get_context(self, _entity_name, _entity_type):
        '''
        获取context
        :return:
        '''
        return self._tk.context_from_entity(_entity_type, _entity_name)

    def _get_template(self, temp_key):
        u"""

        :param temp_key:
        :return:
        """
        try:
            return self._tk.templates[temp_key]
        except:
            pass

    def _get_fields(self, ctx, temp_key, version_num=1):
        u"""

        :param temp_key:
        :return:
        """
        fields = ctx.as_template_fields(self._get_template(temp_key))
        fields['version'] = version_num
        return fields

    def get_last_version_num(self):
        try:
            return self._get_vernum(self.version_name)
        except:
            return 0

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
                return int(reg.search(_filename).group(0).zfill(3))
            except:
                return 0

    def _get_next_version_number(self, template_key):
        fields = self._get_fields(self.ctx, template_key)
        template = self._tk.templates[template_key]

        # Get a list of existing file paths on disk that match the template and provided fields
        # Skip the version field as we want to find all versions, not a specific version.
        skip_fields = ["version"]
        file_paths = self._tk.paths_from_template(
            template,
            fields,
            skip_fields,
            skip_missing_optional_keys=True
        )

        versions = []
        for a_file in file_paths:
            # extract the values from the path so we can read the version.
            path_fields = template.get_fields(a_file)
            versions.append(path_fields["version"])

        # find the highest version in the list and add one.
        try:
            return max(versions)
        except:
            return 0

    def get_laster_version(self):
        u"""
        获取最新版本
        :param temp_key:
        :return:
        """
        return sg_task.select_task_version(self.sg, self.task_id, ['code'], add='latest')

    def _get_path(self, ctx, temp_key, num=1):
        u"""

        :param taskdata:
        :param temp_key:
        :return:
        """
        _template = self._get_template(temp_key)
        _fields = self._get_fields(ctx, temp_key, num)
        return _template.apply_fields(_fields)

    def get_context_f(self, ctx):
        u"""

        :return:
        """
        _user_data = self.get_user
        try:
            _user_data.pop('name')
        except:
            pass
        _ctx = ctx.create_copy_for_user(_user_data)
        return _ctx

    @property
    def get_user(self):
        """
        Return the current user
        """
        try:
            return self.get_current_engine.context.user
        except:
            import getpass
            return getpass.getuser()

    @property
    def get_current_engine(self):
        """
        Return the current engine
        """
        return sgtk.platform.current_engine()

    @property
    def get_current_context(self):
        """
        Return the current context
        """
        return self.get_current_engine.context


# if __name__ == '__main__':
#     _entity_id = 92635
#     _handle = TaskData(_task_id=_entity_id)
#     print _handle.get_publish_dir()
#     print _handle.laster_publish_path()
#     print _handle.project_name
#
#     ctx = _handle.ctx
#
#     # _key = 'mobu_shot_publish'
#     # _key='asset_publish_area_mobu'
#     # _key='mobu_asset_work'
#     # _key='asset_work_area_mobu'
#     # temp_key = 'maya_asset_publish'
#     temp_key = 'maya_asset_work'
#
#     # print(_handle.last_version_num)
#     print(_handle.next_publish_path)
#     print(_handle.next_work_path)
#     print(_handle.laster_work_path)
#     print(_handle.laster_publish_path)
#     # print(_handle.user)
