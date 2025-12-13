# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       : batch_publish_item
# Describe   : 说明描述
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2024/1/2__15:05
# -------------------------------------------------------
PUBLISH_ASSET_TYPES = ['item']
PUBLISH_TASK_NAME = ['drama_mdl']

import database.shotgun.core.sg_analysis as sg_analysis

from apps.publish.batch_publish import batch_check

reload(batch_check)
import os
import shutil

import re


import method.maya.common.file as file_common


# import lib.common.jsonio as jsonio

from  apps.publish.batch_publish import batch_publish
reload(batch_publish)

import method.common.dir as dircommon
reload(dircommon)
import method.common.file as common_file
import method.shotgun.get_task as get_task
from lib.common import log

ASSET_TYPES=['item']
TASK_NAME=['drama_mdl']
class MayaBatchCheckPublish(object):
    def __init__(self, file_name, log_file,project_name='X3', dcc='maya', tag='publish', description=u'批量工具，批量上传'):
        self._file_name = file_name
        self._project_name = project_name
        self._dcc = dcc
        self._tag = tag
        self.log_handle= log.Logger(log_file)

        self._des = description
        self._sg = sg_analysis.Config().login()
        ok, result = self._get_task_data()
        self._task_data = None
        if ok == True:
            self._task_data = result


    def batch_process(self):
        # task_data = get_task_data.TaskData(self._task_data.task_id)
        self.log_handle.info(u'开始处理文件:\n{}'.format(self._file_name))
        if self._task_data==None:
            self.log_handle.error(u'没有找到任务信息,请检查文件命名')
            raise Exception(u'没有找到任务信息,请检查文件命名')
        file_common.BaseFile().open_file(self._file_name)

        ok, result = self.check_published()
        if ok == False:
            if isinstance(result, list):
                for error in result:
                    self.log_handle.error(error)
            if isinstance(result, str) or isinstance(result, unicode):
                self.log_handle.error(result)
            return False, result
        version_file = result

        work_file = self._task_data.work_path
        asset_type= self._task_data.asset_type
        task_name = self._task_data.task_name
        if asset_type in ASSET_TYPES and task_name in TASK_NAME:
            work_dir,work_file_name=os.path.split(work_file)
            basename, suffix = os.path.splitext(work_file_name)
            laster_work_file=dircommon.get_laster_file(work_dir, suffix)
            next_work_file=self._get_next_version_file(laster_work_file)

            check_ok, check_result = self.batch_check()
            if check_ok == False:
                for error in check_result:
                    self.log_handle.error(error)
                return False, check_result

            return self.batch_publish_file(next_work_file, version_file)
        else:
            self.log_handle.error(u'这个任务不是角色道具模型,无法进行批量上传')
            return False, u'这个任务不是角色道具模型,无法进行批量上传'
            # raise Exception(u'这个任务不是角色道具模型,无法进行批量上传')

    def _get_next_version_file(self,file_name):

        _get_vernum = common_file.get_vernum(file_name)
        _next_version = common_file.get_next_ver_fil(file_name)

        return file_name.replace('.v{}.'.format(_get_vernum), '.v{}.'.format(_next_version))

    def batch_publish_file(self, work_file, version_file):
        copy_result = self._copy_to_work_file(work_file)
        if copy_result == False:
            return False, u'复制文件失败,请检查'

        if os.path.exists(work_file):


            self.sg_publish_file(work_file, version_file)


    def sg_publish_file(self, work_file, versino_file):

        file_common.BaseFile().open_file(work_file)

        batch_publish.BatchPublish(self._task_data, versino_file, self._des).do_batch_publish()



    def _copy_to_work_file(self, work_file):
        try:
            shutil.copy(self._file_name, work_file)
            return True
        except:
            return False

    def check_published(self):

        publish_file = self._task_data.des_path
        if not publish_file:
            return False, u"这个任务没有发布信息,无法进行批量上传,请先前台发布"
        publish_file = self._remove_version(publish_file)

        if not publish_file or not os.path.exists(publish_file):
            return False, u'这个文件任务没有发布过，无法进行批量上传，请先前台发布'

        version_file = self.get_laster_vesion_file()
        if not version_file or not os.path.exists(version_file):
            return False, u'没有找到最新版本文件'
        return True, version_file

    def _remove_version(self, str=''):
        '''
        移除版本号
        :param str: 字符串中带'.v005'版本字样的字符串
        :return: 移除版本号的字符串
        '''
        _versionsign = re.findall('.v\w+', str)
        return str.replace(_versionsign[-1], '') if _versionsign else str

    def get_version_file_from_version_id(self, version_id):
        version = self._sg.find_one('Version', [['id', 'is', version_id]], ['sg_path_to_frames'])
        return version['sg_path_to_frames']

    def get_laster_vesion_file(self):
        version_id = self._task_data.last_version_id
        if not version_id:
            return False, u'没有找到最新版本'
        return self.get_version_file_from_version_id(version_id)

    def batch_check(self):
        ok, result = batch_check.batch_check_info(task_data=self._task_data)
        if ok == False:
            for error in result:
                print(error)
            return False, result
        if ok == True:
            if result:
                for info in result:
                    print(info)
        return True, result

    def _get_task_data(self):

        try:
            task_data = get_task.TaskInfo(self._file_name, self._project_name, self._dcc, self._tag,is_lastversion=True,ui=False)
            return True, task_data
        except:
            return False, u'获取任务信息失败'
# if __name__ == '__main__':
#     import method.shotgun.get_task as get_task
#     file_path = r'E:\p\card_cream_fx_003.drama_mdl.v002.ma'
#     handle= MayaBatchCheckPublish(file_path)
#     handle.batch_process()

#     print ok
#     print result
