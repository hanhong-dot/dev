# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       : batch_cover_fbx_to_publish
# Describe   : 说明描述
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2024/3/6_11:52
# -------------------------------------------------------
import database.shotgun.core.sg_analysis as sg_analysis
import database.shotgun.core.sg_asset as sg_asset
from lib.common import log
import maya.cmds as cmds
import method.maya.common.file as maya_common_file
import method.common.file as common_file
import os
import time
import method.shotgun.get_task as get_task
from apps.publish.batch_publish import batch_publish

reload(batch_publish)
import method.common.dir as dircommon

reload(dircommon)

from lib.maya.plugin import plugin_load
from apps.publish.batch_publish import batch_check

reload(batch_check)

SUFFIXList = ['.fbx']


class BatchCoverFbxToPublish(object):
    def __init__(self, fbx_file, log_file, version_file=None, task_name='whitebox', project_name='X3', dcc='maya',
                 tag='publish', description=u'批量转fbx工具，批量上传'):
        super(BatchCoverFbxToPublish, self).__init__()
        self._fbx_file = fbx_file
        self._log_file = log_file
        self._sg = sg_analysis.Config().login()
        self._project_name = project_name
        self._task_name = task_name
        self._dcc = dcc
        self._tag = tag
        self._des = description
        self._version_file = version_file
        if not self._fbx_file:
            return
        self._log_handle = log.Logger(log_file)
        self._log_handle.info(u'开始处理文件:\n{}'.format(self._fbx_file))
        self._asset_name, self._suffix = os.path.splitext(os.path.basename(self._fbx_file))
        if self._suffix not in SUFFIXList:
            self._log_handle.error(u'当前文件不是fbx文件,请检查')
            return

        self._maya_file = '{}.{}.v001.ma'.format(self._asset_name, self._task_name)
        ok, result = self._get_task_data()
        if ok == False:
            self._log_handle.error(result)
            return
        self._task_data = result

    def batch_process(self):
        ok, result = self._check_asset_name()
        if ok == False:
            self._log_handle.error(result)
            return False, result
        work_file = self._cover_fbx_to_ma()
        if not work_file:
            return False, u'检测未通过,请检查日志'
        self._log_handle.info(u'生成的maya文件为:\n{}'.format(work_file))
        time.sleep(1)
        if os.path.exists(work_file):
            try:
                self.sg_publish_file()
                self._log_handle.info(u'上传成功')
                return True, u'publish sucess'
            except:
                self._log_handle.error(u'未上传成功,请检查')
                return False, u'未上传成功,请检查'

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

    def sg_publish_file(self):
        batch_publish.BatchPublish(self._task_data, self._version_file, self._des).do_batch_publish()

    def _cover_fbx_to_ma(self):
        work_file = self._task_data.work_path
        work_dir = os.path.dirname(work_file)
        if not os.path.exists(work_dir):
            os.makedirs(work_dir)
        work_file_new = self._get_next_work_file(work_file)

        self._open_fbx_file(self._fbx_file)
        ok, reslut = self.batch_check()
        if not ok:
            for error in reslut:
                self._log_handle.error(error)
            return None
        maya_common_file.BaseFile().save_file(work_file_new)
        return work_file_new

    def _open_fbx_file(self, fbx_file):
        self._log_handle.info(u'打开文件{}'.format(fbx_file))
        plugin_load(['fbxmaya'])
        cmds.file(fbx_file, options='v=0', f=1, o=1, ignoreVersion=1, pmt=0, rer=0)

    def _check_asset_name(self):
        asset = sg_asset.select_asset_assetID(self._sg, self._project_name, self._asset_name)
        if not asset:
            return False, u'没有找到资产信息'
        return True, asset

    def _get_task_data(self):

        try:
            task_data = get_task.TaskInfo(self._maya_file, self._project_name, self._dcc, self._tag,
                                          is_lastversion=True, ui=False)
            return True, task_data
        except:
            return False, u'获取任务信息失败'

    def _get_next_work_file(self, work_file):
        work_dir, work_file_name = os.path.split(work_file)
        basename, suffix = os.path.splitext(work_file_name)
        laster_work_file = dircommon.get_laster_file(work_dir, suffix)
        if not laster_work_file:
            laster_work_file = work_file
        return self._get_next_version_file(laster_work_file)

    def _get_next_version_file(self, file_name):

        _get_vernum = common_file.get_vernum(file_name)
        _next_version = common_file.get_next_ver_fil(file_name)

        return file_name.replace('.v{}.'.format(_get_vernum), '.v{}.'.format(_next_version))

# if __name__ == '__main__':
#     fbx_file = r'E:\p\re\f\test\common_baseball_001.fbx'
#     log_file = r'E:\p\re\f\test\common_baseball_001.log'
#     handle = BatchCoverFbxToPublish(fbx_file, log_file)
#     handle.batch_process()
