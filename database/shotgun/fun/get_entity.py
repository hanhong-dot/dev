# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       : get_entity
# Describe   : 获得实体信息
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2022/7/19__17:28
# -------------------------------------------------------
import database.shotgun.core.sg_base as sg_base
import database.shotgun.core.sg_image as sg_image


import database.shotgun.fun.analysis_taskdata as analysis_taskdata

import method.shotgun.task_path as task_path
import database.shotgun.core.sg_task as sg_task





class BaseGetSgInfo(object):
    def __init__(self, sg, entity_id, entity_type):
        u"""
        获得shotgun信息
        :param sg: sg实体
        :param entity_id: 实体id
        :param entity_type:实体类型
        """
        self.sg = sg
        self.entity_id = entity_id
        self.entity_type = entity_type

    def get_name(self):
        u"""
        根据id获取name名
        :return:
        """
        try:
            return sg_base.select_entity(self.sg, self.entity_type, self.entity_id, ["code"])["code"]
        except:
            return

    def get_subject(self):
        u"""
        根据id获取subject名
        """
        return sg_base.select_entity(self.sg, self.entity_type, self.entity_id, ["subject"])["subject"]

    def get_status(self):
        u"""
        根据id获得状态
        :return:
        """
        return sg_base.select_entity(self.sg, self.entity_type, self.entity_id, fields=['sg_status_list'])[
            'sg_status_list']

    def get_asset_level(self):
        u"""
        获得资产级别
        @return:
        """
        _level_data = sg_base.select_entity(self.sg, self.entity_type, self.entity_id, fields=['sg_asset_level'])
        if _level_data and 'sg_asset_level' in _level_data:
            return _level_data['sg_asset_level']

    def get_creatby(self):
        u"""
        获取创建时
        :return:
        """
        return sg_base.select_entity(self.sg, self.entity_type, self.entity_id, fields=['created_by'])['created_by']

    def get_text(self):
        u"""
        获取制作内容
        Returns:

        """
        try:
            return sg_base.select_entity(self.sg, self.entity_type, self.entity_id, fields=['sg_text'])['sg_text']
        except:
            pass

    def get_cc(self):
        u"""
        获得cc 抄送人员
        """
        return sg_base.select_entity(self.sg, self.entity_type, self.entity_id, fields=['addressings_cc'])[
            'addressings_cc']

    def get_to(self):
        u"""
        获得review人员
        :return:
        """
        return sg_base.select_entity(self.sg, self.entity_type, self.entity_id, fields=['addressings_to'])[
            'addressings_to']

    def get_creat_at(self):
        u"""
        获得创建时间
        :return:
        """
        return sg_base.select_entity(self.sg, self.entity_type, self.entity_id, fields=['created_at'])[
            'created_at']

    def get_body(self):
        u"""
        获得内容
        :return:
        """
        return sg_base.select_entity(self.sg, self.entity_type, self.entity_id, fields=['content'])[
            'content']

    def get_notetype(self):
        u"""
        获得notetype
        :return:
        """
        return sg_base.select_entity(self.sg, self.entity_type, self.entity_id, fields=['sg_note_type'])[
            'sg_note_type']

    def get_start_date(self):
        u"""
        获得start_date
        :return:
        """
        return sg_base.select_entity(self.sg, self.entity_type, self.entity_id, fields=['start_date'])[
            'start_date']

    def get_due_date(self):
        u"""
        获得due_date
        :return:
        """
        return sg_base.select_entity(self.sg, self.entity_type, self.entity_id, fields=['due_date'])[
            'due_date']

    def get_description(self):
        u"""
        获得description 中文备注
        :return:
        """
        return sg_base.select_entity(self.sg, self.entity_type, self.entity_id, fields=['description'])[
            'description']

    def get_duration(self):
        u"""
        获得duration
        :return:
        """
        _time = sg_base.select_entity(self.sg, self.entity_type, self.entity_id, fields=['duration'])[
            'duration']
        if _time:
            return u"{} days".format(_time / (8 * 60))

    def get_path(self):
        u"""
        获得due_date
        :return:
        """
        return sg_base.select_entity(self.sg, self.entity_type, self.entity_id, fields=['path'])[
            'path']

    def get_task_step(self, _task_id):
        u"""
        获取task 的step
        Args:
            _task_id:

        Returns:

        """
        return sg_base.select_entity(self.sg, 'Task', _task_id, fields=['step'])['step']['name']

    def get_x3_tag(self):
        u"""
        获得x3_tag
        """
        try:
            return sg_base.select_entity(self.sg, self.entity_type, self.entity_id, ["sg_x3_tag"])["sg_x3_tag"]
        except:
            pass

    def get_path_to_frame(self):

        try:
            return sg_base.select_entity(self.sg, self.entity_type, self.entity_id, ["sg_path_to_frames"])["sg_path_to_frames"]
        except:
            pass
    def judige_x3tag(self, limit):
        u"""
        判断x3_tag 字段是否符合限制条件
        """
        return self.judge_limit(self.get_x3_tag(), limit)

    def judge_limit(self, data, limit):
        u"""
        判断数据中是否包含limit条件
        """
        if data:
            for i in range(len(data)):
                if data[i] and 'name' in data[i] and data[i]['name'] in limit:
                    return True
                    break
        return False

    def get_tasks(self, task_fields=[]):
        u"""
        获得实体关联的所有task
        """
        try:
            return sg_base.select_entity_task(self.sg, self.entity_type, self.entity_id, task_fields=task_fields)
        except:
            pass

    def get_thumbnail(self):
        u"""
        获得缩略图
        @return:
        """
        return sg_image.select_entity_thumbnaildata(self.sg, self.entity_type, self.entity_id)



    def select_shot_assets(self):
        u"""
        获得镜头关联胡资产
        """
        if self.entity_type == 'Shot':
            try:
                import database.shotgun.core.sg_shot as sg_shot
                return sg_shot.select_shot_asset(self.sg, self.entity_id)
            except:
                return

    def select_entity_filters_tasks(self, filter=[['content', 'is', 'u3d_check'], ["sg_status_list", "is_not", 'fin']]):
        u"""
        获得符合条件的关联task
        """
        fields = ['content']
        filters = [
            ['entity.' + self.entity_type + '.id', 'is', self.entity_id]
        ]
        if filter:
            filters.extend(filter)
        return self.sg.find("Task", filters, fields)

    def download_entity_thumbnail(self, imagepath):
        u"""
        下载缩略图
        @param imagepath: 需要下载到的路径
        @return:
        """
        import os
        _dir = os.path.dirname(imagepath)
        if not os.path.exists(_dir):
            os.makedirs(_dir)
        return sg_image.download_entity_thumbnail(self.sg, self.entity_type, self.entity_id, cover_M(imagepath))


class NoteGetSgInfo(BaseGetSgInfo):
    def __init__(self, sg, entity_id, entity_type="Note"):
        u"""
        Note类型实例获取sg信息
        :param sg:sg实体
        :param entity_id:note id
        :param entity_type:类型(默认为Note类型)
        """
        self.sg = sg
        self.entity_id = entity_id
        self.entity_type = entity_type
        BaseGetSgInfo.__init__(self, self.sg, self.entity_id, self.entity_type)

    def get_note_notelink(self):
        _dict = {}
        _linkinfo = self.get_notelink()
        if _linkinfo:
            for i in range(len(_linkinfo)):
                if _linkinfo[i] and 'type' in _linkinfo[i] and 'name' in _linkinfo[i]:
                    _dict[_linkinfo[i]['id']] = [_linkinfo[i]['name'], _linkinfo[i]['type']]
        return _dict

    def get_notelink(self):
        u"""
        :return:
        """
        return sg_base.select_entity(self.sg, self.entity_type, self.entity_id, ["note_links"])["note_links"]

    def get_tasks(self):
        u"""
        获取关联的任务
        Returns:

        """
        return sg_base.select_entity(self.sg, self.entity_type, self.entity_id, ["tasks"])["tasks"]

    def get_attachments(self):
        u"""
        获取note attachments图片
        @return:
        """
        return sg_base.select_entity(self.sg, self.entity_type, self.entity_id, ["attachments"])["attachments"]

    def download_attachement(self,_img_dir):
        u"""
        下载返修图片
        @return:
        """
        import os
        _attachments = self.get_attachments()

        if _attachments:
            _data = _attachments[0]
            if not os.path.exists(_img_dir):
                os.makedirs(_img_dir)
            imagepath = '{}/{}'.format(_img_dir, _data['name'])
            return sg_image.download_attachment(self.sg, _data, cover_M(imagepath))


class VersionGetSgInfo(BaseGetSgInfo):
    def __init__(self, sg, entity_id, entity_type="Version"):
        u"""
        Note类型实例获取sg信息
        :param sg:sg实体
        :param entity_id:note id
        :param entity_type:类型(默认为Note类型)
        """
        self.sg = sg
        self.entity_id = entity_id
        self.entity_type = entity_type
        BaseGetSgInfo.__init__(self, self.sg, self.entity_id, self.entity_type)

    def get_versionlink(self):
        u"""
        :return:
        """
        return sg_base.select_entity(self.sg, self.entity_type, self.entity_id, ["entity"])["entity"]

    def get_publishs(self):
        u"""
        获得publish
        Returns:

        """
        return sg_base.select_entity(self.sg, self.entity_type, self.entity_id, ["published_files"])["published_files"]

    def get_task(self):
        u"""
        获得关联的task
        Returns:

        """
        try:
            return sg_base.select_entity(self.sg, self.entity_type, self.entity_id, ['sg_task'])['sg_task']
        except:
            return

    @property
    def get_taskdata(self):
        u"""

        @return:
        """
        try:
            _entity_name = self.get_versionlink()['name']
            _task_name = self.get_task()['name']
            return analysis_taskdata.AnalysisTaskData(entity_name=_entity_name, task_name=_task_name).TaskData
        except:
            return

    @property
    def get_thumbnail_filepath(self):
        u"""
        获取缩略图模板路径
        @return:
        """
        if self.get_taskdata:
            return task_path.SgTaskPath(self.get_taskdata).get_publish_thumbnail()

    def download_thumbnail(self):
        u"""
        下载缩略图
        @return:
        """

        imagepath = self.get_thumbnail_filepath
        if imagepath:
            return self.download_entity_thumbnail(imagepath)


class PublishGetSgInfo(BaseGetSgInfo):
    def __init__(self, sg, entity_id, entity_type="PublishedFile"):
        u"""
        Note类型实例获取sg信息
        :param sg:sg实体
        :param entity_id:note id
        :param entity_type:类型(默认为PublishedFile类型)
        """
        self.sg = sg
        self.entity_id = entity_id
        self.entity_type = entity_type
        BaseGetSgInfo.__init__(self, self.sg, self.entity_id, self.entity_type)

    def get_publish_link(self):
        u"""
        获取publish 链接
        Returns:

        """
        return sg_base.select_entity(self.sg, self.entity_type, self.entity_id, ["entity"])["entity"]

    def get_task(self):
        u"""
        获得publish 文件链接的task
        Returns:

        """
        return sg_base.select_entity(self.sg, self.entity_type, self.entity_id, ['task'])['task']

    def get_publish_path(self):
        u"""
        获取上传文件路径
        @return:
        """
        return sg_base.select_entity(self.sg, self.entity_type, self.entity_id, ['path'])['path']

    @property
    def get_attachments(self):
        u"""
        获取上传附件路径
        @return:
        """
        return sg_base.select_entity(self.sg, self.entity_type, self.entity_id, ['sg_attachments'])['sg_attachments']

    def get_local_path(self):
        u"""
        获取上传文件路径
        @return:
        """
        _local_path = ''
        _name = ''
        _path_data = self.get_publish_path()
        if _path_data and 'url' in _path_data and 'name' in _path_data:
            _local_path = _path_data['url']
            if _local_path:
                _local_path = cover_M(_local_path)
            _name = _path_data['name']
        return {'name': _name, 'path': _local_path}

    def get_local_dir(self):
        u"""
        获取上传文件路径
        @return:
        """
        _local_path = ''
        _name = ''
        _path_data = self.get_publish_path()

        if _path_data and 'local_path' in _path_data:
            return _path_data['local_path']

    @property
    def get_taskdata(self):
        u"""

        @return:
        """
        try:
            _entity_name = self.get_publish_link()['name']
            _task_name = self.get_task()['name']
            return analysis_taskdata.AnalysisTaskData(entity_name=_entity_name, task_name=_task_name).TaskData
        except:
            return

    @property
    def get_thumbnail_filepath(self):
        u"""
        获取缩略图模板路径
        @return:
        """
        if self.get_taskdata:
            try:
                return task_path.SgTaskPath(self.get_taskdata).get_publish_thumbnail()
            except:
                return

    def download_thumbnail(self):
        u"""
        下载缩略图
        @return:
        """

        imagepath = self.get_thumbnail_filepath
        if imagepath:
            return self.download_entity_thumbnail(cover_M(imagepath))


def cover_M(_path):
    if 'M:' in _path:
        _path = _path.replace('M:', '//10.10.201.151/share/product')
    if 'm:' in _path:
        _path = _path.replace('m:', '//10.10.201.151/share/product')
    return _path.replace('\\', '/')
    # return _path


class TaskGetSgInfo(BaseGetSgInfo):
    def __init__(self, sg, entity_id, entity_type="Task"):
        u"""
        Note类型实例获取sg信息
        :param sg:sg实体
        :param entity_id:note id
        :param entity_type:类型(默认为Note类型)
        """
        self.sg = sg
        self.entity_id = entity_id
        self.entity_type = entity_type
        BaseGetSgInfo.__init__(self, self.sg, self.entity_id, self.entity_type)

    def get_entity(self):
        u"""
        :return:
        """
        return sg_base.select_entity(self.sg, self.entity_type, self.entity_id, ["entity"])["entity"]

    def get_assigned_to(self):
        u"""
        :return:
        """
        info = sg_base.select_entity(self.sg, self.entity_type, self.entity_id, ["task_assignees"])["task_assignees"]
        if info:
            return [i['name'] for i in info if (i and 'name' in i)]

    def get_assigned_to_data(self):
        return sg_base.select_entity(self.sg, self.entity_type, self.entity_id, ["task_assignees"])["task_assignees"]

    def get_assigned_to_ids(self):
        u"""
        获取assigned_to 的id列表
        :return:
        """
        info = sg_base.select_entity(self.sg, self.entity_type, self.entity_id, ["task_assignees"])["task_assignees"]
        if info:
            return [i['id'] for i in info if (i and 'id' in i)]

    def get_task_id(self, _task_name, _project_name='X3'):
        u"""
        获得与任务链接资产指定任务的id
        @param task_name:指定任务名
        @return:
        """
        _entity_name = self.get_entity()['name']
        return sg_task.get_task_taskID(self.sg, _project_name, _task_name, _entity_name)

    def updata_taskdata(self,data):
        u"""
        更新任务状态
        @param data:
        @return:
        """
        return sg_base.update_entity(self.sg, 'Task', self.entity_id, data=data)

    def select_task_assigned(self,_task_name,_project_name='X3'):
        U"""
        获得同链接资产指定任务的assigne to 人员email列表
        @param _task_name:任务名
        @param _project_name:项目名
        @return:
        """
        _task_data=self.get_task_id(_task_name,_project_name)
        if _task_data and 'id' in _task_data[0]:
            _task_id=_task_data[0]['id']
            if _task_id:
                return TaskGetSgInfo(self.sg, _task_id).get_assigned_to_emails()

    def get_assigned_to_emails(self):
        u"""
        获取assigned_to 的emails 列表
        @return:
        """
        return self._select_user_emails(self.get_assigned_to_ids())

    def _select_user_emails(self, userids):
        u"""
        从userid 列表，获取相应emails 列表
        Args:
            userids:

        Returns:
        """
        _emails = []
        if userids:
            for i in range(len(userids)):
                _email = UserGetSgInfo(self.sg, userids[i]).select_userid_email()
                if _email and _email not in _emails:
                    if isinstance(_email, list):
                        _emails.extend(_email)
                    if isinstance(_email, str):
                        _emails.extend([_email])
        return _emails

    def get_task_name(self):
        u"""
        获得task name
        :return:
        """
        return sg_base.select_entity(self.sg, self.entity_type, self.entity_id, ["content"])["content"]

    def get_task_step(self):
        u"""
        获得任务的step环节名
        Returns:

        """
        return sg_base.select_entity(self.sg, self.entity_type, self.entity_id, ["step"])["step"]

    def get_downstream(self):
        u"""
        获得任务的 UpstreamDependency
        Returns:

        """
        return sg_base.select_entity(self.sg, self.entity_type, self.entity_id, ["downstream_tasks"])[
            "downstream_tasks"]

    def get_upstream(self):
        u"""
        获得任务的 UpstreamDependency
        Returns:

        """
        return sg_base.select_entity(self.sg, self.entity_type, self.entity_id, ["upstream_tasks"])["upstream_tasks"]

    def get_duration(self):
        u"""
        获得任务的duration
        """
        _time = sg_base.select_entity(self.sg, self.entity_type, self.entity_id, ["duration"])["duration"]
        if _time and self._is_number(_time) == True:
            return _time / (24 * 20)

    def _is_number(self, num):
        '''
        是否是数字
        hong.han
        :param num:
        :return: True 为数字
        '''
        try:
            float(num)
            return True
        except ValueError:
            pass

        try:
            import unicodedata
            unicodedata.numeric(num)
            return True
        except (TypeError, ValueError):
            pass

        return False

    def get_due(self):
        u"""
        获得任务截止日期
        """
        return sg_base.select_entity(self.sg, self.entity_type, self.entity_id, ["due_date"])["due_date"]

    def get_cur_due(self):
        u"""
        获得当前日期与截止日期差值(单位为天)
        """
        import datetime
        _due = self.get_due()
        if not _due:
            return
        _due_date = datetime.datetime.strptime(_due, '%Y-%m-%d')
        _today = datetime.datetime.strptime(self._current_time(), '%Y-%m-%d')
        try:
            return ((_due_date - _today).days)
        except:
            return

    def _current_time(self):
        u"""
        获得当前日期
        """
        import datetime
        return datetime.datetime.today().strftime("%Y-%m-%d")

    @property
    def get_taskdata(self):
        u"""

        @return:
        """
        try:
            _entity_name = self.get_entity()['name']
            _task_name = self.get_task_name()
            return analysis_taskdata.AnalysisTaskData(entity_name=_entity_name, task_name=_task_name).TaskData
        except:
            return

    @property
    def get_thumbnail_filepath(self):
        u"""
        获取缩略图模板路径
        @return:
        """
        if self.get_taskdata:
            try:
                return task_path.SgTaskPath(self.get_taskdata).get_task_thumbnail()
            except:
                return

    def download_thumbnail(self):
        u"""
        下载缩略图
        @return:
        """

        imagepath = self.get_thumbnail_filepath
        if imagepath:
            return self.download_entity_thumbnail(imagepath)


class UserGetSgInfo(BaseGetSgInfo):
    def __init__(self, sg, entity_id=None, entity_type="HumanUser"):
        u"""
        Note类型实例获取sg信息
        :param sg:sg实体
        :param entity_id:note id 默认为None
        :param entity_type:类型(默认为HumanUser类型)
        """
        self.sg = sg
        self.entity_id = entity_id
        self.entity_type = entity_type
        BaseGetSgInfo.__init__(self, self.sg, self.entity_id, self.entity_type)

    def select_userid_email(self):
        u"""
        由用户id获取用户邮箱字典
        :return:
        """
        return sg_base.select_entity(self.sg, self.entity_type, self.entity_id, fields=['email'])['email']


def get_attachment_url(attachemen_datas):
    u"""
    获得attachment url 信息
    @param attachemen_data:
    @return:
    """
    _base_url = 'https://shotgun.nikkigames.cn/file_serve/attachment'
    if attachemen_datas:
        for i in range(len(attachemen_datas)):
            if 'id' in attachemen_datas[i] and 'name' in attachemen_datas[i]:
                _url = '{}/{}/{}'.format(_base_url, attachemen_datas[i]['id'], attachemen_datas[i]['name'])
                attachemen_datas[i]['url'] = _url
    return attachemen_datas


if __name__ == '__main__':
    import database.shotgun.core.sg_analysis as sg_analysis

    sg = sg_analysis.Config().login()
    entity_id = 153879
    _handle = TaskGetSgInfo(sg, entity_id)
    print(_handle.get_task_name())
    print(_handle.get_entity()['name'])
    print(_handle.get_assigned_to_emails())
    _task_name = 'ue_final'
    print(_handle.get_task_id(_task_name))
    print(_handle.select_task_assigned(_task_name))

#
#     entity_id = 55986
#     _handle = VersionGetSgInfo(sg, entity_id)
#     print(_handle.get_versionlink())
#     print(_handle.get_task())
#     print(_handle.download_thumbnail())
#     print(_handle.get_task())
#     print(_handle.get_thumbnail_filepath)
#     print(_handle.download_thumbnail())


# entity_id = 33571
# _handle = NoteGetSgInfo(sg, entity_id)
# print(_handle.download_attachement())

# attachemen_datas = [{'type': 'Attachment', 'id': 398254, 'name': 'annot_version_58085.0.png'}]
# print(get_attachment_url(attachemen_datas))

# entity_id=398254
# entity_type='Attachment'
# _handle=BaseGetSgInfo(sg,entity_id,entity_type)
# print(_handle.get_path())

#
# entity_id = 83591
# entity_type='task'
# _handle = PublishGetSgInfo(sg, entity_id)
# print(_handle.get_publish_path())
# print(_handle.get_local_path())
# print(_handle.get_task())
# TaskGetSgInfo(sg, 83595, entity_type="Task").get_task_step()
# print(TaskGetSgInfo(sg, 83595).get_task_step())
# print(sg_base.select_entity(sg, "Task", 83595, ["step"])["step"])

#
#     entity_id=12634
#     entity_type='Asset'
#
#     _handle=BaseGetSgInfo(sg, entity_id, entity_type)
#     print(_handle.get_asset_level())


# entity_id = 92803
# entity_type = 'Task'
#
# print(sg_base.select_entity(sg, entity_type, entity_id, ['upstream_tasks']))['upstream_tasks'
# ]
# entity_id = 39948
# project = 'X3'
# entity_type = 'Version'
# print(VersionGetSgInfo(sg,entity_id,entity_type).get_versionlink())
# print(VersionGetSgInfo(sg,entity_id,entity_type).get_publishs())
#
# entity_id = 61903
# entity_type = 'PublishedFile'
# _handle_base = BaseGetSgInfo(sg, entity_id, entity_type)
# #
# print(_handle_base.get_path())

# entity_id=70687
# _handle=BaseGetSgInfo(sg,entity_id,entity_type)
# print(_handle.get_text())
#
# entity_id = 62341
# entity_type = "PublishedFile"

# entity_id = 42639
# entity_type = 'Version'
# _publish_handle = PublishGetSgInfo(sg, entity_id)
# print(_publish_handle.get_task())
# _id=83591
# _task_handle=TaskGetSgInfo(sg,_id)
# print(_task_handle.get_upstream())
# print(BaseGetSgInfo(sg,_id,'Task').get_to())
# entity_id = 26667
#
# entity_type = 'Note'
# #
# print(sg_base.select_entity(sg, entity_type, entity_id, ["note_links"])["note_links"])
# entity_type='Version'
# entity_id=41227
# print(sg_base.select_entity(sg, entity_type, entity_id, ["sg_task"])["sg_task"])

# entity_type = 'Asset'
# entity_id = 12637
# project_name = 'X3'
# entity_name = 'fy001s'
# # _handle = BaseGetSgInfo(sg, entity_id, entity_type)

# print(sg_base.select_entity_task(sg, entity_type, entity_id))

# entity_id=12910
# project_name='TDTEST_ROLE'
# entity_type='Asset'
# _handle=BaseGetSgInfo(sg, entity_id, entity_type)
# print(_handle.get_tasks())


# entity_id = 12671
# entity_type = 'Asset'
# _base_handle = BaseGetSgInfo(sg, entity_id, entity_type)
# print(_base_handle.select_entity_filters_tasks())
# _base_handle = BaseGetSgInfo(sg, entity_id, entity_type)
#
# print(_base_handle.select_entity_filters_tasks())
#
# entity_id=81275
# entity_type = 'Task'
# _base_handle = BaseGetSgInfo(sg, entity_id, entity_type)
# print(_base_handle.get_cc())

# print(_base_handle.select_shot_assets())
#
#
# entity_id=81622
# entity_type = 'Task'
# print(TaskGetSgInfo(sg, entity_id, entity_type).get_entity())

#
# print(_handle.get)

# print(_handle.get_x3_tag())
# entity_id = 81622
# entity_type = 'Task'
# _task_handle=TaskGetSgInfo(sg, entity_id, entity_type)
# print(_task_handle.get_entity())

# print _handle.get_duration()
# star = sg_base.select_entity(sg, entity_type, entity_id, ["due_date"])["due_date"]
#
# import datetime

# star=sg_base.select_entity(sg, entity_type, entity_id, ["start_date"])["start_date"]
# end=sg_base.select_entity(sg, entity_type, entity_id, ["due_date"])["due_date"]
# print(star)
# star='2022-08-01'
# end='2022-08-31'
# import datetime
# # _end = datetime.datetime.strptime(end, '%Y-%m-%d')
# _star=datetime.datetime.strptime(star, '%Y-%m-%d')
# _star = datetime.datetime.strptime(star, '%Y-%m-%d')
# _end = datetime.datetime.today()
# print(type(_end))
# print(type(_star))
#
# print((_end - _star).days)
# print datetime.timedelta(days=2)

# print(_end-_star)
# now_time = datetime.datetime.now()

# entity_id =62410
# entity_type = 'PublishedFile'
# print(sg_base.select_entity(sg,entity_type, entity_id, ["entity"])["entity"])
# {'type': 'Asset', 'id': 12910, 'name': 'tdtest_role'}
