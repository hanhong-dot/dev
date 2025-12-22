# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       : batch_publish
# Describe   : 说明描述
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2023/12/30__16:53
# -------------------------------------------------------
import apps.publish.util.media as _media
import apps.publish.util.analyze_xml as _get_data
import method.maya.common.project_info as projectinfo
import os
import lib.common.mediainfo as mediainfo
import method.shotgun.task_path as task_path
import method.shotgun.datapack as _datapack
import re
import threading
import method.shotgun.serversg2 as serversg2
import lib.common.jsonio as jsonio
import method.common.dir as _dir
import lib.common.timedate as timedate
import time
import pprint


class BatchPublish(object):
    def __init__(self, task_data, version_src, description, statu='pub', mb_export=True):
        self._task_data = task_data
        self._version_src = version_src
        self._description = description
        self._statu = statu
        self._project_name = self._task_data.project_name
        self._task_name = self._task_data.task_name
        self._task_id = self._task_data.task_id
        self._task_launch_soft = self._task_data.task_launch_soft
        self._entity_name = self._task_data.entity_name
        self._entity_type = self._task_data.entity_type
        self._mb_export = mb_export
        self._time = timedate.get_currenttime()
        self._analyse_data = _get_data.GetXLMData(self._task_data)
        self._info_data = []

    def do_batch_publish_dict(self, process_dict, user=None, send_jenkins=False, cover_thumbnail=True):
        infolist = []
        info1 = {}
        if self._version_src:
            info1 = self.package_thumbnail(self._version_src, cover_thumbnail)
            if info1:
                infolist.append(info1)
            infolist.append(_datapack.Pack.set_info(
                src_path=self._version_src,
                des_path=os.path.splitext(self._task_data.des_path)[0] + os.path.splitext(self._version_src)[-1],
                description=self._description,
                status=self._statu,
                task_type=self._task_data.entity_type,
                task_name=self._task_data.task_name,
                entity_name=self._task_data.entity_name,
                sequence_name=self._task_data.sequence_name,
                project_name=self._task_data.project_name,
                file_link_type='upload',
                tags='version',
                relationship=0,
            ))

        if process_dict:
            if isinstance(process_dict, dict):
                for key, value in process_dict.items():
                    if key == 'version':
                        for obj_dic in value:
                            infolist.append(_datapack.Pack.set_info(
                                src_path=obj_dic['src_path'] if 'src_path' in obj_dic.keys() else self._version_src,
                                des_path=obj_dic['des_path'] if 'des_path' in obj_dic.keys() else obj_dic[
                                                                                                      'des_dir'] + '/' + os.path.basename(
                                    self._version_src),
                                description=obj_dic[
                                    'description'] if 'description' in obj_dic.keys() else self._description,
                                status=obj_dic['status'] if 'status' in obj_dic.keys() else self._statu,
                                task_type=obj_dic['task_type'],
                                task_name=obj_dic['task_name'],
                                entity_name=obj_dic['entity_name'],
                                sequence_name=obj_dic['sequence_name'] if 'sequence_name' in obj_dic.keys()
                                else '',
                                project_name=obj_dic['project_name'] if 'project_name' in obj_dic.keys() else
                                self._task_data.project_name,
                                file_link_type='upload',
                                tags='version',
                                relationship=obj_dic['relationship']

                            ))

                    elif key in ['publish', 'fbx', 'mbfbx', 'mbexfbx', 'mocap', 'ue', 'unityfbx', 'unityxml']:
                        for obj_dic in value:
                            infolist.append(_datapack.Pack.set_info(
                                src_path=obj_dic['src_path'],
                                des_path=obj_dic['des_path'],
                                description=obj_dic[
                                    'description'] if 'description' in obj_dic.keys() else self._description,

                                down_path=obj_dic['down_path'] if 'down_path' in obj_dic else '',
                                up_path=obj_dic['up_path'] if 'up_path' in obj_dic else '',

                                status=obj_dic['status'] if 'status' in obj_dic.keys() else self._statu,
                                task_type=obj_dic[
                                    'task_type'] if 'task_type' in obj_dic.keys() else self._task_data.entity_type,
                                task_name=obj_dic['task_name'] if 'task_name' in obj_dic.keys() else
                                self._task_data.task_name,
                                entity_name=obj_dic['entity_name'] if 'entity_name' in obj_dic.keys() else
                                self._task_data.entity_name,
                                sequence_name=obj_dic['sequence_name'] if 'sequence_name' in obj_dic.keys() else
                                self._task_data.sequence_name,
                                project_name=obj_dic['project_name'] if 'project_name' in obj_dic.keys() else
                                self._task_data.project_name,
                                tags=key,
                                relationship=obj_dic['relationship'] if 'relationship' in obj_dic.keys() else 0,
                                dcc=self._task_launch_soft,
                                thumbnail=info1['des_path'] if (
                                            info1 and 'thumbnail' in info1 and 'des_path' in info1) else '',
                                work_file=obj_dic['work_file'] if 'work_file' in obj_dic.keys() else '',
                                ref_info=obj_dic['ref_info'] if 'ref_info' in obj_dic.keys() else '',
                                send_jenkins=send_jenkins

                            ))

                    elif key == 'publish_thumbnail':
                        for obj_dic in value:
                            infolist.append(_datapack.Pack.set_info(
                                src_path=obj_dic['src_path'] if 'src_path' in obj_dic.keys() else info1[
                                    'src_path'],
                                des_path=obj_dic['des_path'],
                                tags='thumbnail'))

                    else:
                        for obj_dic in value:
                            infolist.append(_datapack.Pack.set_info(
                                src_path=obj_dic['src_path'],
                                des_path=obj_dic['des_path'],
                                tags=key))

        # 运行
        # pprint.pprint(infolist)

        if _datapack.Pack.combine(infolist):
            bat_result, db_result = self.main_pub(_datapack.Pack.combine(infolist), user)

            if bat_result == True and db_result == True:
                return True, True
        return False, False

    def do_batch_publish(self, user=None, send_jenkins=False, cover_thumbnail=True,source_asset=''):
        infolist = []

        # 处理缩略图字典
        _mediaprocess = _media.MediaProcess(task_data=self._task_data)
        # 检测视频
        info1 = None
        if self._version_src:
            check_result = _mediaprocess.check_media(self._version_src)
            if isinstance(check_result, dict):
                if not check_result['status']:
                    raise Exception(check_result['error_msg'])

            # 处理视频
            _mediaprocess.process_media(self._version_src)
            # 处理缩略图

            info1 = self.package_thumbnail(self._version_src, cover_thumbnail)
            if info1:
                infolist.append(info1)

            # 处理version原图字典
            infolist.append(_datapack.Pack.set_info(
                # src_path = self._get_mediaInfo()[0]
                # des_path=self._get_mediaInfo()[1],
                src_path=self._version_src,
                des_path=os.path.splitext(self._task_data.des_path)[0] + os.path.splitext(self._version_src)[-1],
                description=self._description,
                status=self._statu,
                task_type=self._task_data.entity_type,
                task_name=self._task_data.task_name,
                entity_name=self._task_data.entity_name,
                sequence_name=self._task_data.sequence_name,
                project_name=self._task_data.project_name,
                file_link_type='upload',
                tags='version',
                relationship=0,
                source_asset=source_asset
            ))

        # 获取process的字典
        for script_obj in self._analyse_data.get_processcmds():
            _process_dict = self._do_processcmd(script_obj)

            if _process_dict:
                if isinstance(_process_dict, dict):
                    for key, value in _process_dict.items():
                        if key == 'version':
                            for obj_dic in value:
                                infolist.append(_datapack.Pack.set_info(
                                    src_path=obj_dic['src_path'] if 'src_path' in obj_dic.keys() else self._version_src,
                                    des_path=obj_dic['des_path'] if 'des_path' in obj_dic.keys() else obj_dic[
                                                                                                          'des_dir'] + '/' + os.path.basename(
                                        self._version_src),
                                    description=obj_dic[
                                        'description'] if 'description' in obj_dic.keys() else self._description,
                                    status=obj_dic['status'] if 'status' in obj_dic.keys() else self._statu,
                                    task_type=obj_dic['task_type'],
                                    task_name=obj_dic['task_name'],
                                    entity_name=obj_dic['entity_name'],
                                    sequence_name=obj_dic['sequence_name'] if 'sequence_name' in obj_dic.keys()
                                    else '',
                                    project_name=obj_dic['project_name'] if 'project_name' in obj_dic.keys() else
                                    self._task_data.project_name,
                                    file_link_type='upload',
                                    tags='version',
                                    relationship=obj_dic['relationship']

                                ))

                        elif key in ['publish', 'fbx', 'mbfbx', 'mbexfbx', 'mocap', 'ue', 'unityfbx', 'unityxml']:
                            for obj_dic in value:
                                infolist.append(_datapack.Pack.set_info(
                                    src_path=obj_dic['src_path'],
                                    des_path=obj_dic['des_path'],
                                    description=obj_dic[
                                        'description'] if 'description' in obj_dic.keys() else self._description,

                                    down_path=obj_dic['down_path'] if 'down_path' in obj_dic else '',
                                    up_path=obj_dic['up_path'] if 'up_path' in obj_dic else '',

                                    status=obj_dic['status'] if 'status' in obj_dic.keys() else self._statu,
                                    task_type=obj_dic[
                                        'task_type'] if 'task_type' in obj_dic.keys() else self._task_data.entity_type,
                                    task_name=obj_dic['task_name'] if 'task_name' in obj_dic.keys() else
                                    self._task_data.task_name,
                                    entity_name=obj_dic['entity_name'] if 'entity_name' in obj_dic.keys() else
                                    self._task_data.entity_name,
                                    sequence_name=obj_dic['sequence_name'] if 'sequence_name' in obj_dic.keys() else
                                    self._task_data.sequence_name,
                                    project_name=obj_dic['project_name'] if 'project_name' in obj_dic.keys() else
                                    self._task_data.project_name,
                                    tags=key,
                                    relationship=obj_dic['relationship'] if 'relationship' in obj_dic.keys() else 0,
                                    dcc=self._task_launch_soft,
                                    thumbnail=info1['des_path'] if (
                                            info1 and 'thumbnail' in info1 and 'des_path' in info1) else '',
                                    work_file=obj_dic['work_file'] if 'work_file' in obj_dic.keys() else '',
                                    ref_info=obj_dic['ref_info'] if 'ref_info' in obj_dic.keys() else '',
                                    send_jenkins=send_jenkins,
                                    source_asset=source_asset

                                ))

                        elif key == 'publish_thumbnail':
                            for obj_dic in value:
                                infolist.append(_datapack.Pack.set_info(
                                    src_path=obj_dic['src_path'] if 'src_path' in obj_dic.keys() else info1[
                                        'src_path'],
                                    des_path=obj_dic['des_path'],
                                    tags='thumbnail'))

                        else:
                            for obj_dic in value:
                                infolist.append(_datapack.Pack.set_info(
                                    src_path=obj_dic['src_path'],
                                    des_path=obj_dic['des_path'],
                                    tags=key))

        # 运行

        if _datapack.Pack.combine(infolist):
            bat_result, db_result = self.main_pub(_datapack.Pack.combine(infolist), user)
            if bat_result == True and db_result == True:
                return True, True

    def package_thumbnail(self, path, cover_thumbnail=True):
        '''
        '''
        _name = u'{}.jpg'.format(self._entity_name)
        _thumbnall_local = self.get_loacalfile(self._task_data, _name, '/thumbnail')
        _thumbnail_src = ''
        if cover_thumbnail == True:
            try:
                import lib.common.image as _image
                _thumbnail_src = _image.resize_proportion(path, [0.5, 0.5], _thumbnall_local)
            except:
                try:
                    _thumbnail_src = mediainfo.MediaCollect().get_image_from_mov(
                        seconds="1", frames="1", filepath=path,
                        output_name=(os.path.splitext(_thumbnall_local)[0] + '.jpg'))
                except:
                    try:
                        import lib.maya.process.image_process as image_process
                        image_process.image_resize(path, None, dst=_thumbnall_local, imgform='jpg')
                        _thumbnail_src = _thumbnall_local
                    except:
                        print(u'无法生成缩量图'.encode('gbk'))
        else:
            _thumbnail_src = path

        if _thumbnail_src:
            _thumbnail_publish_dir = task_path.SgTaskPath(self._task_data).get_publish_thumbnail()
            return (_datapack.Pack.set_info(
                src_path=_thumbnail_src,
                des_path=_thumbnail_publish_dir + '/' + os.path.basename(_thumbnail_src),
                tags='thumbnail'))
        else:
            return (None, None)

    def main_pub(self, _dict, _user=None):
        return self._onProgress_pub(_dict, _user)

    def _onProgress_pub(self, _dict, _user=None):
        if not _user:
            _user = self._task_data.current_user_name

        return serversg2.init_process(_dict, _user, self._time)

    def _do_processcmd(self, cmd):
        if cmd and isinstance(cmd, str):
            _command = cmd.split(';')[-1]
            _getInfo = re.findall(r'[(](.*?)[)]', _command)[0]
            _command_new = _command.replace('TaskData_Class', 'self._task_data').replace('mb_export',
                                                                                         'self._mb_export').replace(
                'version_file', 'self._version_src').replace('export_fbx_grp_list', 'all')
            exec (cmd[0:len(cmd) - len(_command)])
            return eval(_command_new)

    def get_loacalfile(self, task_data, filename, addpath=''):
        '''
        获取存储到本地temp下的文件路径
        :param TaskData:
        :param filename: 文件名
        :param addpath: 补充路径 如 '/data/fbx'
        :return:返回本地的路径
        '''
        _tempdir = ''

        _project = task_data.project_name
        _dcc = task_data.task_launch_soft
        _task_type = task_data.entity_type
        _entity_name = task_data.entity_name
        _task_name = task_data.task_name
        _asset_type = task_data.asset_type
        _task_step = task_data.step_name
        _shot_name = task_data.shot_name
        _sequence_name = task_data.sequence_name
        _entity_type = task_data.entity_type
        # 本地基础路径
        if _entity_type.lower() == 'asset':
            _tempdir = '{}/assets/{}/{}/{}/{}/{}/work{}/'.format(projectinfo.ProjectInfo(_project).workpath(),
                                                                 _asset_type,
                                                                 _entity_name, _task_step, _task_name, _dcc, addpath)
        if _entity_type.lower() == 'shot':
            _tempdir = '{}/shots/{}/{}/{}/{}/{}/work{}/'.format(projectinfo.ProjectInfo(_project).workpath(),
                                                                _sequence_name, _entity_name,
                                                                _task_step,
                                                                _task_name, _dcc, addpath)

        _tempfile = r"{}{}".format(_tempdir, filename)
        if not os.path.exists(_tempdir):
            os.makedirs(_tempdir)
        return _tempfile

# if __name__ == '__main__':
#     import method.shotgun.get_task as get_task
#
#     file_name = 'card_cream_fx_003.drama_mdl.v002.ma'
#     task_data = get_task.TaskInfo(file_name, 'X3', 'maya', 'publish')
#     version_src = r'M:\projects\x3\publish\assets\item\card_cream_fx_003\mod\maya\card_cream_fx_003.drama_mdl.v004.png'
#     _description = u'测试上传'
#     BatchPublish(task_data,version_src,_description).do_batch_publish()
