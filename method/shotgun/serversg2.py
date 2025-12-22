# -*- coding: utf-8 -*-#
# Python       : python 2.7.16
# -------------------------------------------------------------------------------
# NAME         : serversg
# Describe     : 文件到文件服务器与shotgun数据库的相关操作
# Version      : v0.01
# Author       : linhuan
# email        : hanhong@papegames.net
# DateTime     : 2022/02/25
# -------------------------------------------------------------------------------
# -------------------------------------------------------------------------------
# example:
# """
# # *************特别注意*************
# 'entity_name': 实体名称（跟实体类型必须对应）
# 'task_name': 任务名称
# 'task_type': 实体类型必填（asset|shot|sequence|episode）
# # *************特别注意*************
# """

'''
{'collect': {'ass': [{'des_path': 'Y:/Project/AD/Asset/tt/sg_base.py',
                      'src_path': u'e:/lib/Develop/db/shotgun/core/sg_base.py'}],
             'tex': [{'des_path': u'e:/test/abc.fbx',
                      'src_path': u'D:/Info_Temp/abc.fbx'},
                     {'des_path': u'S:/Images/fIlM/XCM_2021DY/seq000/seq000_sc0708A/efx/efx_broken/l/de/untitled.mantra1.0001.exr',
                      'src_path': u'Q:/fIlM/XCM_2021DY/efxcache/img/seq001/seq001_sc006/efx/efx_particle/v001/l/de/untitled.mantra1.0001.exr'}]},
 'shotgun': {'publish': [{'des_path': 'Y:/Project/AD/Asset/tt/groups.conf',
                          'description': 'publsh_asset01_test',
                          'entity_name': 'CA003002xe',
                          'task_name': 'Mod_hig',
                          'task_type': 'Asset',
                          'episode_name': '',
                          'file_link_type': 'local',
                          'project_name': 'xcm_test',
                          'relationship': 0,
                          'sequence_name': '',
                          'src_path': u'e:/data/groups.conf',
                          'status': 'fin',
                          'tags': 'publish',
                          'task_thumbnail': 'e:/data/2531170_085604363000_2.jpg'},
                         {'des_path': 'Y:/Project/AD/Asset/tt/111.txt',
                          'description': 'publsh_shot02_test',
                          'entity_name': 'seq000_sc001',
                           'task_name': 'Ani_ani',
                          'task_type': 'Shot',
                          'episode_name': '',
                          'file_link_type': 'local',
                          'project_name': 'xcm_test',
                          'relationship': 0,
                          'sequence_name': 'seq000',
                          'src_path': u'D:/Info_Temp/111.txt',
                          'status': 'ip',
                          'tags': 'publish',
                          'task_thumbnail': ''}],
             'version': [{'des_path': 'Y:/Project/AD/Asset/tt/test_asset.v001.gif',
                          'description': 'version_asset01_test',
                          'entity_name': 'CA003002xe',
                          'task_name': 'Cfx_cth',
                          'task_type': 'Asset',
                          'episode_name': '',
                          'file_link_type': 'local',
                          'project_name': 'xcm_test',
                          'relationship': 1,
                          'sequence_name': '',
                          'src_path': u'e:/test/Cao_A_Render.gif',
                          'status': 'rev',
                          'tags': 'version',
                          'task_thumbnail': 'e:/data/2531170_085604363000_2.jpg'},
                         {'des_path': 'Y:/Project/AD/Asset/tt/test_shot.v001.jpg',
                          'description': 'version_shot02_test',
                          'entity_name': 'seq000_sc001',
                          'task_name': 'Ani_ani',
                          'task_type': 'Shot',
                          'episode_name': '',
                          'file_link_type': 'local',
                          'project_name': 'xcm_test',
                          'relationship': 0,
                          'sequence_name': 'seq000',
                          'src_path': u'e:/test/b3a8f8df-3efc-4223-b989-be9cd3a5727b.jpg',
                          'status': 'mdf',
                          'tags': 'publish',
                          'task_thumbnail': ''}]}}

'''
# -------------------------------------------------------------------------------

__AUTHORZH__ = u"韩虹"

__AUTHOR__ = 'linhuan'

__eMAIl__ = 'hanhong@papegames.net'

import os, io, traceback
import method.common.dir as dir
import lib.common as libs
import lib.common.timedate as timedate
import database.shotgun.core.sg_base as sg_base

import database.shotgun.core.sg_analysis as sg_analysis
import database.shotgun.core.sg_project as sg_project
import database.shotgun.core.sg_user as sg_user
import database.shotgun.core.sg_asset as sg_asset
import database.shotgun.core.sg_shot as sg_shot
import database.shotgun.core.sg_sequence as sg_sequence
import database.shotgun.core.sg_episode as sg_episode
import database.shotgun.core.sg_task as sg_task
import database.shotgun.core.sg_publish as sg_publish
import database.shotgun.core.sg_version as sg_version

try:
    reload(sg_version)
except:
    pass

try:
    reload(sg_publish)
except:
    pass
import database.shotgun.core.sg_tag as sg_tag

import database.shotgun.core.sg_publishfile as sg_publishfile

sg_login = sg_analysis.Config().login()

FASTCOPY_CMD = '\\\\10.10.201.151\\share\\development\\dev\\tools\\fastcopy\\fastCopy.exe'
import subprocess

RUNAS_CMD = 'Z:\\dev\\tools\\runas\\runas.exe'
from threading import Thread, Lock
import time


class ServerSG(object):
    def __init__(self, _dict_data, user='', timepath=''):
        '''
        上传文件到文件服务器并写入sg数据库
        :param _dict_data:字典
        :param user: 用户名
        :param timepath:当前时间的字符串
        '''

        self._dict_data = _dict_data
        self._timepath = timepath
        self._path = dir.set_localtemppath('temp_info/publishInfo/')
        self._localDriver = dir.getlocaldisk()
        self.log = self._path + 'publish_' + self._timepath + '.log'
        self._dict_log = self._path + 'dict_' + self._timepath + '.log'
        self.up_down_log = self._path + 'up_down_' + self._timepath + '.log'

        self.bat_file = self._path + 'publish_' + self._timepath + '.bat'
        self._updict_log = self._path + 'updict_' + self._timepath + '.log'
        self.user = user
        if not self.user:
            self.user = self.get_username(user)

        self.runas = RUNAS_CMD

        self.files = []
        self.delarray = []
        self.errorInfo = []

        if self._dict_data:
            with open(self._dict_log, 'a') as f:
                f.write(str(self._dict_data))

    def get_username(self, username):
        if username:
            if not sg_user.get_current_userid(sg_login, username):
                raise Exception('username is not in shotgun,please check!')
        return username

    def _trans_path(self, path):
        path = path.replace("/", "\\") if '/' in path else path
        path = path.replace("M:", "\\\\10.10.201.151\\share\\product") if 'M:' in path else path
        path = path.replace("Z:", "\\\\10.10.201.151\\share\\development") if 'Z:' in path else path
        path = path.replace("z:", "\\\\10.10.201.151\\share\\development") if 'z:' in path else path
        return path

    def _set_batinfo(self, src, des):
        """
        设置bat文件内容格式
        :param src: 原始路径
        :param des: 目标路径
        :param is_fastcopy: 默认使用fastCopy
        :return:返回bat文件内容信息
        """
        cmd = ''
        if os.path.isfile(src):
            _des_dir = self._trans_path(os.path.dirname(des))
        else:
            _des_dir = self._trans_path(des)

        _src = self._trans_path(src)
        ip_des = self._trans_path(des)
        ip_src = self._trans_path(src)
        _log = self._trans_path(self.log)

        if os.path.exists(src):
            if os.path.basename(src) == os.path.basename(des):
                # cmd = '{} /no_ui /cmd=diff /auto_close /balloon=FAlSE /filelog="{}" "{}" /to="{}"'.format(
                # 		self._set_ippath(FASTCOPY_CMD), _log, self._set_ippath(_src), self._set_ippath(_des_dir))
                cmd = u'{} /no_ui /cmd=diff /auto_close /balloon=FAlSE /filelog="{}" "{}" /to="{}"'.format(
                    FASTCOPY_CMD, _log, _src, _des_dir)
                cmd = cmd + '\n'
            else:
                if os.path.isfile(src):
                    cmd = u'echo f | xcopy \"%s\" \"%s\" /y ' % (ip_src, ip_des)
                else:
                    cmd = u'echo d | xcopy \"%s\" \"%s\" /s /e /y ' % (ip_src, ip_des)
                cmd = cmd + '\n'
                cmd = cmd + u'if %%errorlevel%%==0 (echo "------%s to ===> %s update success------%%date:~0,-3%% %%time%%" >> %s\n' % (
                    ip_src, ip_des, _log)
                cmd = cmd + u')else (echo "++++++%s update failed++++++" >> %s)\n' % (ip_src, _log)
                cmd = cmd + '\n'
        return cmd

    def _bat_addInfo(self, type=''):
        """
        在bat文件中追加的内容
        :param type: 在增加一句话中添加的内容
        :return:bat文件增加的一句话
        """
        batInfo = ''
        batInfo = batInfo + 'echo "-----------------------------------\"%s\" files to fileSystem is ' \
                            'started-----------------------------------" >> %s\r\n' % (
                      type, self.log)
        return batInfo

    def _analyze_batinfo(self):
        """
        解析字典获取bat内容信息
        :return:返回bat内容的列表
        """
        for first_k, first_v in self._dict_data.items():
            if first_k and first_v:
                second_keys = list(first_v.keys())
                if second_keys:
                    for second_key in second_keys:
                        addInfo = self._bat_addInfo(second_key)
                        self.files.append(addInfo)
                        third_list = first_v[second_key]
                        if third_list:
                            for obj in third_list:
                                src_path = obj['src_path']
                                des_path = obj['des_path']
                                infos = self._set_batinfo(src_path, des_path)
                                self.files.append(infos)
        return self.files

    def _bat_create(self, infos=[]):
        """
        在客户端本地创建bat文件
        """
        fileInfo = ''
        if infos:
            for obj in infos:
                fileInfo = fileInfo + obj

        if fileInfo:
            fileInfo = fileInfo + '\r\necho "-----------------------------------*Publish All files to fileSystem has ' \
                                  'finished*-----------------------------------" >> %s' % self.log
        # else:
        #     fileInfo = fileInfo + '\r\necho "-----------------------------------*Step:%s publish files to fileSystem is continued*-----------------------------------" >> %s' % (
        #         self.str_num, self.log)

        # fileInfo = fileInfo + '\r\nset scriptname=%~n0\r\nset scriptpath=%~dp0\r\nset "nfile=%scriptpath%%scriptname%.ly"\r\ntype nul>%nfile%\r\npause'
        fileInfo = fileInfo + '\r\nset scriptname=%~n0\r\nset scriptpath=%~dp0\r\nset "nfile=%scriptpath%%scriptname%.ly"\r\ntype nul>%nfile%'
        # if '/' in fileInfo:
        # 	fileInfo = fileInfo.replace("/", "\\")
        if '\\y ' in fileInfo:
            fileInfo = fileInfo.replace('\\y ', '/y')

        if isinstance(fileInfo, str):
            fileInfo = u'{}'.format(fileInfo)

        # with io.open(self.bat_file, 'w', encoding="utf-8") as f:

        with io.open(self.bat_file, 'w', encoding="gbk") as f:
            f.write(fileInfo)

        return self.bat_file

    def bat_run(self):
        """
        提交文件到文件服务器程序入口
        :return: True成功，否则失败
        """
        import time

        self._bat_create(self._analyze_batinfo())
        time.sleep(2)
        import getpass
        user = getpass.getuser()

        log_endTime = timedate.set_endtime(hours=1)

        # os.system(self.bat_file)
        procmd = "{} {}".format(self.runas, self.bat_file)

        # os.system(procmd)
        # lock=Lock()
        # lock.acquire()
        try:
            subprocess.call(procmd, shell=True)
        except:
            os.system(procmd)
        # lock.release()
        # subprocess.Popen(procmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # p = subprocess.Popen(procmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        #
        # try:
        #     out, err = p.communicate(timeout=300)
        #     print("子进程的标准输出：", out.decode())
        #     print("子进程的标准错误：", err.decode())
        # except :
        #     p.kill()
        #     out, err = p.communicate()
        #     print("子进程超时退出！")

        # subprocess.call(self.bat_file, shell=True)

        if os.path.exists(self.log):
            with open(self.log) as file:
                log = file.read()
                try:
                    log_info = log.decode("gbk").rstrip()
                except Exception as e:
                    log_info = log.rstrip()

                if log_info:
                    if '++++++' in log_info:
                        return False
                    if '"-----------------------------------*Publish All files to fileSystem has ' \
                       'finished*-----------------------------------"' in log_info:
                        return True
                if timedate.get_currentdate().strftime('%Y-%m-%d %H:%M') == log_endTime.strftime('%Y-%m-%d %H:%M'):
                    return False

    def _get_entity_data(self, project_name, task_type, entity_name, sequence_name='', episode_name=''):
        """
        根据实体类型获取实体信息
        :param project_name:项目名
        :param task_type:实体类型
        :param entity_name: 实体名
        :param sequence_name: 场次名
        :param episode_name: 集数名
        :return:
        """
        if task_type.lower() == 'asset':
            return sg_asset.select_asset_assetID(sg_login, project_name, entity_name)[
                0] if sg_asset.select_asset_assetID(
                sg_login, project_name, entity_name) else None
        elif task_type.lower() == 'shot':
            return sg_shot.select_shot_ID(sg_login, project_name, entity_name, sequence_name, episode_name)[0] if \
                sg_shot.select_shot_ID(sg_login, project_name, entity_name, sequence_name, episode_name) else None
        elif task_type.lower() == 'sequence':
            return sg_sequence.select_sequence_ID(sg_login, project_name, entity_name, episode_name)[0] if \
                sg_sequence.select_sequence_ID(sg_login, project_name, entity_name, episode_name) else None
        elif task_type.lower() == 'episode':
            return sg_episode.get_episode_episodeID(sg_login, project_name, entity_name)[0] if \
                sg_episode.get_episode_episodeID(sg_login, project_name, entity_name) else None

    def _get_drama_mdl_user(self, asset_id, task_name='drama_mdl'):
        publishs = sg_asset.select_asset_publish(sg_login, asset_id, task_name=task_name, publish_fields=['created_by'])
        __user_data = {}
        __publish_id = 0
        if publishs:
            for __publish_data in publishs:
                if __publish_data['id'] > __publish_id:
                    __user_data = __publish_data['created_by'] if 'created_by' in __publish_data else None
        return __user_data

    def _dbfile_create(self, db_type, db_file, project_name, task_type, entity_name, task_name, link_type,
                       sequence_name='', episode_name='', description='', sg_status_list='', down_path='', up_path='',
                       returnfields=None, publish_file_type='', work_file='', ref_info='', **kwargs):

        """w'd'd
        :param db_type: publish,version
        :param db_file: 已上传服务器上的文件路径
        :param project_name: 项目名
        :param task_type: 实体类型
        :param entity_name: 实体名字
        :param task_name: 实体任务
        :param user_name: 用户名
        :param link_type: local,upload,url 等上传数据库的类型
        :param sequence_name: 场次名
        :param episode_name: 集数名
        :param returnfields: 返回的字段
        :param args: 其他参数
        :param kwargs: 其他字段
        :return:
        """

        _project_data = sg_project.get_project_projectID(sg_login, project_name)[0] if sg_project.get_project_projectID(
            sg_login, project_name) else None

        _entity_data = self._get_entity_data(project_name, task_type, entity_name, sequence_name, episode_name)
        _user_data = sg_user.get_current_userid(sg_login, self.user)[0] if self.user else None
        _task_data = sg_task.get_task_taskID(sg_login, project_name, task_name, entity_name)[0] if \
            sg_task.get_task_taskID(sg_login, project_name, task_name, entity_name) else None
        if task_name in ['drama_rig', 'rbf']:

            __drama_mdl_user = ''
            __drama_mdl_user_data = self._get_drama_mdl_user(_entity_data['id'], task_name='drama_mdl')
            if __drama_mdl_user_data and 'name' in __drama_mdl_user_data:
                __drama_mdl_user = __drama_mdl_user_data['name']
            tex = u' @{}'.format(self.user)
            if tex not in description:
                description = description + tex
            tex_drama_mdl = u' @{}'.format(__drama_mdl_user)
            if __drama_mdl_user and tex_drama_mdl not in description:
                description = description + tex_drama_mdl

        _publish_file_data = sg_publishfile.get_publishfile_type(name=publish_file_type)
        _down_path = down_path,
        _up_path = up_path,
        sg_status_list = sg_status_list
        work_file = work_file
        if db_type == 'publish':
            sg_status_list = 'pub'
            # print('publish_file={}'.format(db_file))
            # print('project_data={}'.format(_project_data))
            # print('link_type={}'.format(_task_data))
            # print('link_entity_data={}'.format(_entity_data))
            #
            #
            # print('user_data={}'.format(_user_data))
            # print('return_fields={}'.format(returnfields))
            # print('publish_file_type={}'.format(_publish_file_data))
            # print('down_path={}'.format(_down_path))
            # print('up_path={}'.format(_up_path))
            return sg_publish.create_publish(sg_login, publish_file=db_file, project_data=_project_data,
                                             link_type=link_type, sg_status_list=sg_status_list,
                                             task_data=_task_data, link_entity_data=_entity_data, user_data=_user_data,
                                             return_fields=returnfields, publish_file_type=_publish_file_data,
                                             down_path=_down_path, up_path=_up_path, description=description,
                                             work_file=work_file, ref_info=ref_info)

        if db_type == 'version':
            return sg_version.create_version(sg_login, version_file=db_file, description=description,
                                             project_data=_project_data, link_entity_date=_entity_data,
                                             task_data=_task_data,
                                             user_data=_user_data, sg_status_list=sg_status_list)

    def dbinfo_upload(self):
        """
        更新数据到shotgun数据库入口
        :return: 成功返回True,失败返回false
        """
        version_list = []
        publish_list = []
        result_list = []
        _version_id = None
        publish_updown_dict = {}
        _task_name = ''
        _entity_name = ''
        _entity_type = ''
        _entity_id = None
        _project_name = ''
        _thumbnail_dict = {}
        __thumbnail = ''
        _update_publish_dict = {}
        _status = ''
        _work_data = {}
        _publish_files = []
        _description = ''
        _send_jenkins = ''
        __parent_asset = ''
        _wbx = ''
        for first_k, first_v in self._dict_data.items():
            if first_k == 'shotgun':
                for second_k, second_v in first_v.items():
                    if second_k == 'version':
                        if second_v:
                            for obj in second_v:
                                try:
                                    version_dict = self._dbfile_create(db_type='version',
                                                                       db_file=self._set_sgpath(obj['des_path']),
                                                                       project_name=obj['project_name'],
                                                                       task_type=obj['task_type'],
                                                                       entity_name=obj['entity_name'],
                                                                       task_name=obj['task_name'],
                                                                       link_type=obj['file_link_type'],
                                                                       sequence_name=obj['sequence_name'],
                                                                       episode_name=obj['episode_name'],
                                                                       description=obj['description'],
                                                                       sg_src_path=obj['des_path'],
                                                                       sg_path_to_movie=obj['des_path'],
                                                                       tags=[
                                                                           sg_tag.get_tag_tagID(sg_login, obj['tags'])],
                                                                       sg_status_list=obj['status'])
                                    version_list.append({obj['relationship']: version_dict['id']})
                                    _version_id = version_dict['id']
                                    self.delarray.append({'Version': version_dict['id']})
                                    if version_dict and obj['file_link_type'] == 'upload':
                                        movie_path = self._set_sgpath(obj['des_path']).replace('M:/projects/',
                                                                                               '/Volumes/share/product/projects/').replace(
                                            'M:\\projects\\', '/Volumes/share/product/projects/').replace(
                                            "\\\\10.10.201.151\\share\\product\\projects\\",
                                            '/Volumes/share/product/projects/')

                                        kwargs = {'sg_path_to_movie': movie_path}

                                        sg_version.update_version_version(sg_login, version_dict['id'],
                                                                          upload_movie=self._set_sgpath(
                                                                              obj['des_path']),
                                                                          field_name="sg_uploaded_movie", **kwargs)
                                        # if obj['task_type'].lower() in ['asset']:
                                        #
                                        #     sg_version.update_version_version(sg_login, version_dict['id'],
                                        #                                       upload_movie=self._set_sgpath(obj['des_path']),
                                        #                                       field_name="sg_uploaded_movie_mp4")
                                        # else:
                                        #     sg_version.update_version_version(sg_login, version_dict['id'],
                                        #                                       upload_movie=self._set_sgpath(obj['des_path']),
                                        #                                       field_name="sg_uploaded_movie")
                                    # if version_dict and obj['task_type'] in ['Asset']:
                                    #     sg_version.emove_version_thubnail(sg_login,version_dict['id'])

                                except Exception as e:
                                    self.errorInfo.append(e)
                                    result_list.append(False)

                    if second_k == 'publish':
                        if second_v:
                            for obj in second_v:

                                try:
                                    publish_dict = self._dbfile_create(db_type='publish',
                                                                       db_file=self._set_sgpath(obj['des_path']),
                                                                       project_name=obj['project_name'],
                                                                       task_type=obj['task_type'],
                                                                       entity_name=obj['entity_name'],
                                                                       task_name=obj['task_name'],
                                                                       link_type=obj['file_link_type'],
                                                                       sequence_name=obj['sequence_name'],
                                                                       episode_name=obj['episode_name'],
                                                                       description=obj['description'],
                                                                       tags=[
                                                                           sg_tag.get_tag_tagID(sg_login, obj['tags'])],
                                                                       sg_src_path=obj['des_path'],
                                                                       sg_status_list=obj['status'],
                                                                       down_path=obj['down_path'],
                                                                       up_path=obj['up_path'],

                                                                       publish_file_type=obj['publish_file_type'],
                                                                       work_file=self._set_sgpath(obj['work_file']),
                                                                       ref_info=obj['ref_info']

                                                                       )
                                    if obj['work_file']:
                                        _work_data['work_file'] = self._set_sgpath(obj['work_file'])

                                    if obj['send_jenkins']:
                                        _send_jenkins = obj['send_jenkins']

                                    if 'wbx' in obj and obj['wbx']:
                                        _wbx = obj['wbx']
                                    if obj['ref_info']:
                                        _work_data['ref_info'] = eval(obj['ref_info'])

                                    publish_updown_dict[publish_dict['id']] = {'down': obj['down_path'],
                                                                               'up': obj['up_path']}
                                    if obj['thumbnail']:
                                        _thumbnail_dict[publish_dict['id']] = obj['thumbnail']
                                        __thumbnail = obj['thumbnail']

                                    _update_publish_dict[publish_dict['id']] = [obj['publish_file_type'],
                                                                                self._set_sgpath(obj['des_path'])]

                                    publish_list.append({obj['relationship']: publish_dict['id']})
                                    _publish_files.append(self._set_sgpath(obj['des_path']))

                                    self.delarray.append({'Publishedfile': publish_dict['id']})
                                    _task_name = obj['task_name']
                                    _entity_name = obj['entity_name']
                                    _project_name = obj['project_name']
                                    _status = obj['status']
                                    _description = obj['description']
                                    _entity_type = obj['task_type']
                                    __parent_asset = obj.get('parent_asset', '')
                                except Exception as e:
                                    self.errorInfo.append(e)
                                    result_list.append(False)

        # publish 更新上下游上传文件
        if publish_updown_dict:
            self.publish_uddata(publish_updown_dict)
        # 更新缩略图
        with open(self._dict_log, 'a') as f:
            f.write(str(_thumbnail_dict))

        if _thumbnail_dict:
            for _id, _thumbnail in _thumbnail_dict.items():
                self.updat_publish_thumbnail(_id, _thumbnail=_thumbnail)

        # rig 和mod
        if _task_name in ["fight_mdl", "drama_mdl", "drama_rig", "rbf", "ue_mdl", "ue_rig", "ue_final", "whitebox",
                          "out_mdl", "out_rig"]:
            _data = {"sg_status_list": "rev"}
            self.task_updata(_project_name, _task_name, _entity_name, _data)

        # 记录上传状态tag

        if _status == 'pub':
            _tags = [{'type': 'Tag', 'id': 662, 'name': 'pub'}]
        else:
            _tags = [{'type': 'Tag', 'id': 663, 'name': 'ip'}]
        _data = {"tags": _tags}
        self.task_updata(_project_name, _task_name, _entity_name, _data)

        # item wbx drma_mdl

        # if _task_name in ["drama_rig", "rbf", "lan_rig"] and _status == 'pub' and _publish_files:
        #     data_dic = {}
        #     _publish_files = list(set(_publish_files))
        #     _publish_files = [u'{}'.format(_publish_file) for _publish_file in _publish_files if
        #                       (_publish_file.endswith('.fbx') or _publish_file.endswith('.json'))]
        #     data_dic['files'] = _publish_files
        #     data_dic['person'] = u'{}'.format(self.user)
        #     data_dic['description'] = u'{}'.format(_description)
        #     data_dic['asset_name'] = u'{}'.format(_entity_name)
        #     data_dic['task_name'] = u'{}'.format(_task_name)
        #     _entity_id = self._get_entityid(_project_name, _entity_type, _entity_name)
        #     if _entity_id:
        #         _entity_R = self._get_entity_R(_entity_type, _entity_id)
        #         data_dic['entity_R'] = u'{}'.format(_entity_R)
        #
        #     event_publish_send_jenkins(data_dic)
        _entity_id = self._get_entityid(_project_name, _entity_type, _entity_name)
        asset_type = self._get_assettype(_entity_id)
        _send_jenkins = self._judge_senter(_publish_files)

        # if asset_type and asset_type in ['item']:
        #     self.__updata_entity_thumbnail(_entity_id,_entity_type,__thumbnail)

        if (_task_name in ["drama_rig",
                           "lan_rig"] and _status == 'pub' and asset_type not in [
                'item']) or (_task_name in ['rbf'] and _status == 'pub' and _publish_files) or (
                asset_type in ['item'] and _status == 'pub' and _publish_files and _task_name in ["drama_rig",
                                                                                                  "lan_rig"]):
            data_dic = {}
            _publish_files = list(set(_publish_files))
            _publish_files = self.__get_send_jenkins_publish_files(_publish_files)
            if _publish_files:
                data_dic['files'] = _publish_files
                data_dic['person'] = u'{}'.format(self.user)
                data_dic['description'] = u'{}'.format(_description)
                data_dic['asset_name'] = u'{}'.format(_entity_name)
                data_dic['task_name'] = u'{}'.format(_task_name)
                if asset_type.lower() in ['item']:
                    __asset_level = self.__get_asset_level(_entity_id)
                    if __asset_level and int(__asset_level) == 5:
                        __asset_level = 5
                    else:
                        __asset_level = 0
                    data_dic['asset_level'] = __asset_level
                _drama_mdl_user_data = self._get_drama_mdl_user(_entity_id, task_name='drama_mdl')
                if _drama_mdl_user_data:
                    __drama_mdl_user_id = _drama_mdl_user_data['id']
                    __drama_mdl_user_email_data = sg_user.select_user_user(sg_login, __drama_mdl_user_id,
                                                                           user_fields=['email'])
                    data_dic['upstream_created_by'] = __drama_mdl_user_email_data[
                        'email'] if __drama_mdl_user_email_data and 'email' in __drama_mdl_user_email_data else ''
                _entity_id = self._get_entityid(_project_name, _entity_type, _entity_name)
                try:
                    data_dic['entity_R'] = u'{}'.format(self._get_entity_R(_entity_type, _entity_id))
                except:
                    data_dic['entity_R'] = 'main'

                if _wbx:
                    data_dic['upstream_step'] = 'wbx'
                else:
                    data_dic['upstream_step'] = 'mod'
                if __parent_asset:
                    data_dic['parent_asset'] = __parent_asset
                send_jenkins_ok = False
                count = 0
                while count <= 100:
                    send_jenkins_ok, result = event_publish_send_jenkins(data_dic)
                    if send_jenkins_ok:
                        break
                    else:
                        time.sleep(3)
                        count = count + 1
                if not send_jenkins_ok:
                    print(u'自动化失败,文件暂停上传,请联系@林欢')

                    raise Exception(u'自动化失败,文件暂停上传,请联系@林欢')

                _send_data = u'{}'.format(data_dic)
                try:
                    _send_data = _send_data.encode('utf-8').decode('gbk')
                except:
                    pass
                if _send_data:
                    _up_data = {"sg_send_jenkins": u'{}'.format(_send_data)}
                    self.task_updata(_project_name, _task_name, _entity_name, _up_data)

        # 模型文件上传,将rig状态改为fix
        # if _task_name in ["drama_mdl", "fight_mdl"] and _status == 'pub':
        # 根据 2023 0131 木易意见更新
        if _task_name in ["fight_mdl", "drama_mdl"] and _status == 'pub':
            _datan = {"sg_status_list": "fix"}
            _rbf_task = "rbf"
            _rig_task = "drama_rig"
            _rbf_status = self._get_task_status(_project_name, _rbf_task, _entity_name)
            if _rbf_status and _rbf_status not in ['omt', 'wtg', 'hld']:
                self.task_updata(_project_name, _rbf_task, _entity_name, _datan)
            else:
                self.task_updata(_project_name, _rig_task, _entity_name, _datan)
        if _task_name in ['out_mdl'] and _status == 'pub':
            _datan = {"sg_status_list": "fix"}
            _out_rig_task = "out_rig"
            self.task_updata(_project_name, _out_rig_task, _entity_name, _datan)
        if _task_name in ["ue_mdl", "ue_final", "ue_low"] and _status == 'pub':
            _datan = {"sg_status_list": "fix"}
            _ue_rig_task = 'ue_rig'
            self.task_updata(_project_name, _ue_rig_task, _entity_name, _datan)

        if _task_name in ["drama_rig", "rbf"] and _status == 'pub':
            _datan = {"sg_status_list": "unity"}
            _u3d_task = 'u3d_check'
            self.task_updata(_project_name, _u3d_task, _entity_name, _datan)
        _asset_type = self._get_assettype(_entity_id)
        _task_status = self._get_task_status(_project_name, _task_name, _entity_name)
        # item wbx  drma_mdl
        if _asset_type and _asset_type in ['item'] and _task_name in [
            "whitebox"] and _status == 'pub' and _task_status not in ['omt']:
            _datan = {"sg_status_list": "fix"}
            _rig_task = "drama_rig"
            self.task_updata(_project_name, _rig_task, _entity_name, _datan)

        if _asset_type and _asset_type in ['item'] and _task_name in ["drama_mdl"]:
            _wbx_task = "whitebox"
            _wbx_status = self._get_task_status(_project_name, _wbx_task, _entity_name)
            _datan = {"sg_status_list": "omt"}
            if _wbx_status and _wbx_status not in ['omt']:
                self.task_updata(_project_name, _wbx_task, _entity_name, _datan)

        if _work_data:
            _datan = {"sg_work": str(_work_data)}
            self.task_updata(_project_name, _task_name, _entity_name, _datan)

        # rig文件,上传附件(pub状态下才会上传附件)
        # if _task_name in ["drama_rig", "rbf"] and _update_publish_dict and _status == 'pub':
        #     for k, v in _update_publish_dict.items():
        #         if v and len(v) > 1:
        #             if v[0] in ['Maya FBX']:
        #                 sg_publish.update_publish_attachments(sg_login, k, upload_path=v[-1])

        # for  _rig_task in _rig_tasks:
        #     # _result=self.judge_publish(_entity_type,_entity_id,_rig_task)
        #     _datan = {"sg_status_list": "fix"}
        #     self.task_updata(_project_name, _rig_task, _entity_name, _datan)

        # version和publish链接关系
        if version_list and publish_list:
            for version in version_list:
                for publish in publish_list:
                    if list(publish.keys())[0] == list(version.keys())[0]:
                        try:
                            result = sg_publish.update_publish_publish(sg_login,
                                                                       publish_id=publish[list(publish.keys())[0]],
                                                                       version={'type': 'Version',
                                                                                'id': version[list(version.keys())[0]]})

                            result_list.append(result)
                        except Exception as e:
                            self.errorInfo.append(e)
                            result_list.append(False)

        elif version_list and not publish_list:
            result_list.append(True)
        elif publish_list and not version_list:
            result_list.append(True)
        else:
            result_list.append(False)

        return False if False in result_list else True

    def __write_json(self, data, json_file):
        import json

    def __get_asset_level(self, asset_id):
        try:
            return sg_asset.select_asset_entity(sg_login, asset_id, ['sg_asset_level'])['sg_asset_level']
        except:
            return

    def __get_send_jenkins_publish_files(self, publish_files):
        _publish_files = []
        for publish_file in publish_files:
            publish_file = publish_file.replace("\\", "/")
            if (publish_file.endswith('.fbx') and not publish_file.endswith(
                    '_MB.fbx') and not '/mobu/' in publish_file and not publish_file.endswith(
                '_asis.fbx')) or publish_file.endswith('.json'):
                _publish_files.append(publish_file)
        return _publish_files

    def __updata_entity_thumbnail(self, entity_id, entity_type, thumbnail):
        return sg_login.upload_thumbnail(entity_type, entity_id, thumbnail)

    def __updata_version_thumbnail(self, version_id, thumbnail):
        return sg_version.update_version_version(sg_login, version_id, thumbnail=thumbnail)

    def _judge_senter(self, publish_files):
        result = False
        if publish_files:
            for publish_file in publish_files:
                if publish_file.endswith('.ma'):
                    result = True
                    break
        return result

    def _get_entity_R(self, entity_type, entity_id):
        _entity_R = ''
        if entity_type == 'Asset':
            _entity_R = self._get_entity_id_field(entity_type, entity_id, ['sg_text_4'])['sg_text_4']
        elif entity_type == 'Shot':
            _entity_R = self._get_entity_id_field(entity_type, entity_id, ['sg_text_1'])['sg_text_1']
        try:
            return _entity_R

        except:
            return ('{}'.format(_entity_R)).decode('utf-8').encode('gbk')

    def _get_entity_id_field(self, entity_type, entity_id, fields):

        return sg_base.select_entity(sg_login, entity_type, entity_id, fields=fields)

    def _get_task_status(self, project_name, task_name, entity_name):
        u"""
        获取任务状态
        """
        _task_id = self._get_task_id(project_name, task_name, entity_name)
        if _task_id:
            _status_data = self._select_taskid_field(_task_id)
            try:
                return _status_data['sg_status_list']
            except:
                return

    def _updata_subasset_task(self, project_name, task_name, task_type, entity_name, sequence_name, episode_name):
        u"""
        刷新上传参考 的 SubAssets 文件
        :param project_name:项目名
        :param task_name:任务名
        :param entity_name:资产名
        :return:
        """
        _entity_data = self._get_entity_data(project_name, task_type, entity_name, sequence_name, episode_name)
        if _entity_data and 'id' in _entity_data:
            _entity_id = _entity_data['id']
            _entity_type = _entity_data['type']
            assetype = self._get_assettype(_entity_id)
            if _entity_type == 'Asset' and assetype and assetype in ['role', 'cartoon_role'] and task_name in [
                'drama_rig', 'rbf']:
                _subassets = self._get_subassets(_entity_id, _entity_type)
                if _subassets and 'assets' in _subassets and _subassets['assets']:
                    _asset_datas = _subassets['assets']

    def _get_subassets(self, entity_id, entity_type):
        u"""

        :param entity_id:
        :param entity_type:
        :return:
        """
        return sg_base.select_entity(sg_login, entity_type, entity_id, fields=['assets'])

    def _get_task_id(self, project_name, task_name, entity_name):
        u"""
        获得任务id
        """
        _task_data = sg_task.get_task_taskID(sg_login, project_name, task_name, entity_name)[0] if \
            sg_task.get_task_taskID(sg_login, project_name, task_name, entity_name) else None
        try:
            return _task_data['id']
        except:
            return

    def _select_taskid_field(self, task_id, fields=['sg_status_list']):
        u"""
        获取任务字段信息
        """

        return sg_base.select_entity(sg_login, 'Task', task_id, fields=fields)

    def _get_entityid(self, _project_name, _entity_type, _entity_name):
        u"""
        获取id
        """
        try:
            return sg_base.select_entity_id(sg_login, _project_name, _entity_type, _entity_name)[0]['id']
        except:
            return

    def _get_assettype(self, entity_id):
        try:
            return sg_asset.select_asset_entity(sg_login, entity_id)['sg_asset_type']
        except:
            return

    def judge_publish(self, entity_type, entity_id, task_name):
        u"""
        判断任务是否上传过
        :param _task_id:
        :return:
        """
        _pub = sg_base.select_entity_publish(sg_login, entity_type, entity_id, task_name)
        if _pub:
            return True
        else:
            return False

    def task_updata(self, project_name, task_name, entity_name, _data):
        u"""
        根据
        :param project_name:
        :param task_name:
        :param entity_name:
        :return:
        """

        _task_data = sg_task.get_task_taskID(sg_login, project_name, task_name, entity_name)[0] if \
            sg_task.get_task_taskID(sg_login, project_name, task_name, entity_name) else None
        if _task_data and 'id' in _task_data:
            _task_id = _task_data['id']
            return sg_task.upadata_task(sg_login, _task_id, data=_data)

    def publish_uddata(self, _publish_updown_dict):
        u"""
        更新publish文件
        Args:
            _publish_updown_dict

        Returns:

        """
        _dict = {}
        _uplist = []
        _downlist = []
        _prolist = []
        if _publish_updown_dict:
            for k, v in _publish_updown_dict.items():
                if v['down'] == True and k not in _downlist:
                    _downlist.append(k)
                if v['up'] == True and k not in _uplist:
                    _uplist.append(k)
            #
            if _uplist:
                for pubid in list(_publish_updown_dict.keys()):
                    if pubid not in _uplist and pubid not in _prolist:
                        self.updata_publish_downstream(pubid, _uplist, 'upstream_published_files')
                        _prolist.append(pubid)
                        _prolist.extend(_uplist)
            if _downlist:
                for pubid in list(_publish_updown_dict.keys()):
                    if pubid not in _downlist and pubid not in _prolist:
                        self.updata_publish_downstream(pubid, _downlist, 'downstream_published_files')
                        _prolist.append(pubid)
                        _prolist.extend(_downlist)

    def updata_publish_downstream(self, id, _list=[], field='downstream_published_files', entity_type='PublishedFile'):
        u"""
        更新
        Args:
            id: publish 文件id
            _list: id 列表
            fields: 更新字段

        Returns:

        """
        _data_dict = {}

        _datas = []
        if _list:
            for i in range(len(_list)):
                data = sg_base.select_entity(sg_login, entity_type, _list[i], ['code'])
                if data and 'code' in data:
                    _datas.append(self.fix_updown_data(data))
        if _datas:
            _data_dict[field] = _datas
            sg_login.update(entity_type, id, _data_dict)

    def updat_publish_thumbnail(self, entity_id, _thumbnail='', entity_type='PublishedFile'):
        u"""
        更新缩略图
        :param id: id
        :param _thumbnail: 缩略图路径
        :param field:
        :param entity_type: publish类型
        :return:
        """
        import database.shotgun.core.sg_image as sg_image
        return sg_image.updata_entity_thumbnaildata(sg_login, entity_type, entity_id, _thumbnail)

    def fix_updown_data(self, _data):
        u"""
        更新_data信息
        Args:
            _data:

        Returns:

        """
        if not _data:
            return
        return eval(str(_data).replace('code', 'name'))

    def add_sginfo(self):
        if self.errorInfo:
            with open(self.log, 'a') as f:
                for error in self.errorInfo:
                    f.write(str(error) + '\n')
                f.write('"+++++++++++++++++++++*Upload All Infos to shotgun is faild*+++++++++++++++++++++"')
        else:
            with open(self.log, 'a') as f:
                f.write(
                    '"-----------------------------------*Upload All infos to shotgun has succeeded*-----------------------------------" ')

    # def _add_info(self,info):
    #     with open(self.log, 'a') as f:
    #         f.write(info + '\n')

    def dbinfo_delete(self):
        """
        回溯，删除数据库上已创建的实体
        :return:
        """
        if self.delarray:
            for obj in self.delarray:
                for k, v in obj.items():
                    try:
                        sg_base.delete_entity(sg_login, k, v)
                    except:
                        traceback.print_exc()

    def _set_sgpath(self, path):
        """
        把M盘路径转为同sg存储路径一致
        :param path: M盘路径
        :return: 转换好的路径地址
        """
        if path:
            driver = os.path.splitdrive(path)[0][0]
            if driver not in self._localDriver:
                if 'm:' in path:
                    path = path.replace('m:', 'M:')
                elif 'M:' in path:
                    path = path.replace('M:', 'M:')
                path = path.replace("/", "\\")
            path = path.replace("\\\\10.10.201.151\\share\\product\\", "M:\\")
        return path


def init_process(data_dic, username, timepath):
    """
    主程序入口
    :param data_dic: 字典
    :param username: 用户名
    :param timepath: time path
    :return: 元组 (True, false) 元组的第一个元素代表文件上传文件服务器结果(True代表上传服务器成功，false失败)，第二个元素代表创建数据库结果（True代表创建数据库信息，false代表创建失败或者不创建）
    """
    server_sg = ServerSG(data_dic, username, timepath)

    bat_result = server_sg.bat_run()
    # print('bat_result={}'.format(bat_result))

    db_result = True
    if bat_result:
        db_result = server_sg.dbinfo_upload()
        server_sg.add_sginfo()
    if not db_result:
        server_sg.dbinfo_delete()
    return bat_result, db_result


def event_publish_send_jenkins(data_dic):
    """
    发送事件到jenkins
    :return:
    """
    import method.lark.send_xmla_jenkins as send_xmla_jenkins
    reload(send_xmla_jenkins)

    return send_xmla_jenkins.ReadShotEvent(str(data_dic))

# if __name__ == '__main__':
#     data_dic={'files': ['M:/projects/X3/publish/assets/role/XL011C/rbf/maya/data/bs/XL011C_HD_asis_Rig.json'], 'description': u'\u7ed1\u5b9a\u66f4\u65b0\u4e0a\u4f20 @Danny @\u5c0f\u6ee1 @\u5c0f\u675c @\u535a\u5ca9', 'upstream_step': 'mod', 'asset_name': u'XL011C', 'person': u'v-xuqing', 'entity_R': u'\u56e4\u8d27', 'task_name': u'rbf'}
#     print(event_publish_send_jenkins(data_dic))


# if bat_result:
#     try:
#         return bat_result, server_sg.dbinfo_upload()
#     except:
#         traceback.print_exc()
#         server_sg.dbinfo_delete()
#         return bat_result, false
# else:
#     return bat_result, false


# import python2.code_lib.user as user
# print type(user.get_user())
# if __name__ == '__main__':
# import lib.common.timedate as timedate
# _dict = {'collecter': {
#     'back': [{'des_path': 'Y:/projects/X3/publish/assets/body/ST_BODY/mod/maya/back/ST_BODY.drama_mdl.v003.ma',
#               'src_path': 'Y:/projects/X3/work/assets/body/ST_BODY/mod/maya/ST_BODY.drama_mdl.v003.ma',
#               'upload_type': 'back'}],
#     'pub_description': [{
#                             'des_path': 'Y:/projects/X3/publish/assets/body/ST_BODY/mod/maya/data/description/ST_BODY.drama_mdl.description.v005.json',
#                             'src_path': 'Y:/projects/X3/work/assets/body/ST_BODY/mod/maya/data/description/ST_BODY.drama_mdl.description.v005.json',
#                             'upload_type': 'pub_description'}],
#     'thumbnail': [
#         {'des_path': u'Y:/projects/X3/publish/assets/body/ST_BODY/mod/thumbnail/ST_BODY.drama_mdl.v005.jpg',
#          'src_path': 'D:/temp_info/X3/assets/body/ST_BODY/mod/drama_mdl/maya/work/thumbnail/ST_BODY.drama_mdl.v005.jpg',
#          'upload_type': 'thumbnail'}]},
#          'shotgun': {'publish': [{'dcc': 'maya',
#                                   'des_path': u'Y:/projects/X3/publish/assets/body/ST_BODY/mod/maya/ST_BODY.drama_mdl.ma',
#                                   'description': u'test',
#                                   'down_path': False,
#                                   'entity_name': u'ST_BODY',
#                                   'episode_name': None,
#                                   'file_link_type': 'local',
#                                   'project_name': 'X3',
#                                   'publish_file_type': 'Maya Scene',
#                                   'relationship': 0,
#                                   'sequence_name': None,
#                                   'src_path': 'Y:/projects/X3/work/assets/body/ST_BODY/mod/maya/ST_BODY.drama_mdl.ma',
#                                   'status': u'ip',
#                                   'tags': 'publish',
#                                   'task_name': u'drama_mdl',
#                                   'task_thumbnail': None,
#                                   'task_type': 'Asset',
#                                   'up_path': True,
#                                   'upload_type': 'publish'}],
#                      'version': [{'dcc': None,
#                                   'des_path': u'Y:/projects/X3/publish/assets/body/ST_BODY/mod/maya/ST_BODY.drama_mdl.v005.png',
#                                   'description': u'test',
#                                   'down_path': None,
#                                   'entity_name': u'ST_BODY',
#                                   'episode_name': None,
#                                   'file_link_type': 'upload',
#                                   'project_name': 'X3',
#                                   'relationship': 0,
#                                   'sequence_name': None,
#                                   'src_path': u'Y:/projects/x3/publish/assets/body/ST_BODY/mod/maya/ST_BODY.drama_mdl.v002(2).png',
#                                   'status': u'ip',
#                                   'tags': 'version',
#                                   'task_name': u'drama_mdl',
#                                   'task_thumbnail': None,
#                                   'task_type': 'Asset',
#                                   'up_path': None,
#                                   'upload_type': 'version'}]}}
# _user='linhuan'
# _time = timedate.get_currenttime()
# init_process(_dict, _user, _time)
# server_sg = ServerSG(_dict, _user, _time)
# project_name = 'X3'
# task_name = 'drama_mdl'
# entity_name = 'ST_BODY'
# _task_data = sg_task.get_task_taskID(sg_login, project_name, task_name, entity_name)[0] if \
#     sg_task.get_task_taskID(sg_login, project_name, task_name, entity_name) else None
# print(_task_data)
