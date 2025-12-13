# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       : batch_process
# Describe   : 说明描述
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2023/12/30__16:56
# -------------------------------------------------------

import method.shotgun.get_task as get_task

import os
import sys

sys.path.append(r'Z:\dev\database\shotgun\toolkit\x3')
sys.path.append(r'Z:\dev\Ide\Python\2.7.11\Lib\site-packages')
from lib.common import log


class BatchProcessPublish(object):
    def __init__(self, entity_list=[]):
        self.entity = None
        self.log_file = None

        if entity_list:
            self.entity = entity_list[0]
            self.log_file = self.entity['log_file'] if 'log_file' in self.entity else None

    def batch_proeces(self, model='item_mdl_batch_publish'):
        # do something
        return self.batch_publish(model)
    def batch_publish(self, model='item_mdl_batch_publish'):
        file_path = self.entity['FilePath']
        try:
            file_path = file_path.decode('utf-8')
        except:
            file_path = file_path.decode('gbk').encode('utf-8')
        file_name = self.entity['FileName']
        project_name = self.entity['Project']['name']
        if model == 'item_mdl_batch_publish':
            from apps.batch.process.batch_item_mdl_publish import item_mdl_batch_publish

            return item_mdl_batch_publish(file_path, self.log_file)
        if model == 'item_fbx_cover_wbx_publish':
            from apps.batch.process.maya_batch_process import batch_item_fbx_cover_wbx_publish
            return batch_item_fbx_cover_wbx_publish(file_path, self.log_file)

        # from apps.publish.batch_publish.item_batch_publish import MayaBatchCheckPublish
        # print self.entity['FilePath']
        # print type(self.entity['FilePath'])
        # return MayaBatchCheckPublish(self.entity['FilePath']).batch_process()

    def check_task_data(self):
        if not self.entity:
            return False, u"没有选中文件，请选中文件后再执行"
        project_name = ''
        file_path = ''
        file_name = ''

        try:
            project_name = self.entity['Project']['name']
            file_path = self.entity['FilePath']
            file_name = self.entity['FileName']

        except:
            pass

        if not project_name:
            return False, u"没有项目信息,请发消息给TD"
        if not file_path:
            return False, u"没有文件路径信息,请发消息给TD"

        if not file_name:
            return False, u"没有文件名信息,请发消息给TD"

        suffix = os.path.splitext(file_name)[-1]
        if suffix not in ['.ma']:
            return False, u"选择的文件不是ma文件,请检查"

        self.task_data = get_task.TaskInfo(file_path, project_name, 'maya', 'publish')
        if not self.task_data:
            return False, u"选择的文件，没有找到对应的任务信息,请检查文件命名是否正确"
        return True, self.task_data

    def get_value(self, model='item_mdl_batch_publish'):
        log_handle = log.Logger(self.log_file)
        log_handle.info(u'start batch publish')
        if model in ['item_mdl_batch_publish']:
            ok, result = self.check_task_data()
            if ok == False:
                log_handle.error(result)
                return False, result
        batch_ok, batch_result = self.batch_proeces(model)

        # log_handle.info(u"batch_result:{}".format(batch_result))
        # log_handle.info(u"batch_ok:{}".format(batch_ok))

        if batch_ok == False:
            log_handle.error(u"批处理执行错误,请检查")
            # if isinstance(batch_result, list):
            #     for item in batch_result:
            #         log_handle.error(item)
            # if isinstance(batch_result, str):
            #     log_handle.error(batch_result)
            # if isinstance(batch_result, unicode):
            #     log_handle.error(batch_result.encode('utf-8'))
            # if isinstance(batch_result, Exception):
            #     log_handle.error(batch_result.message)

            return False, u"批处理执行错误,请检查"
        errors = log_handle.get_errors()
        if errors:
            log_handle.error(u"批处理执行错误,请检查log信息")

            return False, u"批处理执行错误,请检查log信息"
        else:
            log_handle.info(u"批处理执行成功")
            return True, u"执行成功"
