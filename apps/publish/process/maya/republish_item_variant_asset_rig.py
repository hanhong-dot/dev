# -*- coding: utf-8 -*-
# author: linhuan
# file: republish_item_variant_asset_rig.py
# time: 2025/10/27 10:58
# description:
import os
import sys

from method.shotgun import sg_asset_fun

reload(sg_asset_fun)

TASKS = ['drama_rig']
ASSET_TYPES = ['item']
import database.shotgun.core.sg_analysis as sg_analysis
from method.shotgun import get_task_data

from database.shotgun.core import sg_task
from database.shotgun.core import sg_version
from apps.publish.batch_publish.batch_publish import BatchPublish
from method.maya.common.file import BaseFile
import apps.publish.process.filehandle as filehandle
import method.common.dir as common_dir
import method.shotgun.get_task as get_task

FASTCOPY_CMD = '\\\\10.10.201.151\\share\\development\\dev\\tools\\fastcopy\\fastCopy.exe'
RUNAS_CMD = r'Z:/dev/tools/runas/runas_n.exe'
DES = 'republish item variant asset rig'
import shutil
import apps.publish.process.maya.process_sgfile as process_sgfile

TASK_NAME = 'drama_rig'

reload(process_sgfile)


class RepublishItemVariantAssetRig(object):
    def __init__(self, asset_id):
        super(RepublishItemVariantAssetRig, self).__init__()
        self._sg = sg_analysis.Config().login()
        if asset_id is None:
            return
        self._asset_id = int(asset_id)

    def run(self):
        ok, reslut = self._process_variant_asset_rig()
        if ok:
            print(reslut)
        else:
            raise Exception(reslut)

    def _process_variant_asset_rig(self):
        __judge = self._judge_variant_asset(self._asset_id)
        if not __judge:
            return False
        parent_ok, parent_asset_id = self._get_parent_item_asset(self._asset_id)
        if not parent_ok:
            return False, u'not parent asset'



        ok, result = self._get_asset_rig_task_id(parent_asset_id)
        if not ok:
            return False, u'not parent rig task'
        task_id = result

        __parent_ok, __parent_work_file = self._get_parent_work_file(task_id)

        if not __parent_ok:
            return False, __parent_work_file

        ok, version_file = self._get_latest_version_by_task_id(task_id)
        if not ok:
            version_file = ''

        ok, rig_task_data = self._get_rig_task_data_by_asset(self._asset_id)
        if not ok:
            return False, rig_task_data
        work_file = rig_task_data.work_path

        copy_ok, copy_result = self._copy_file(__parent_work_file, work_file)
        if work_file and os.path.exists(work_file):
            BaseFile().open_file(work_file)
            result01, result02 = BatchPublish(rig_task_data, version_file, DES, statu='ip').do_batch_publish()
            if result01 and result02:
                return True, u'publish successful'
        return False, u'publish failed'

    def _copy_file(self, src, dst):
        if not os.path.exists(src):
            return False, u'not src file'
        dst_dir = os.path.dirname(dst)
        if not os.path.exists(dst_dir):
            os.makedirs(dst_dir)
        try:
            shutil.copy2(src, dst)
        except Exception, e:
            return False, u'copy file error: {}'.format(e)
        return True, dst

    def _get_parent_work_file(self, task_id):

        ok, work_file = self._get_work_file_by_task_id(task_id)
        if not ok:
            return False, u'not parent work file'
        return True, work_file

    def _get_asset_rig_task_id(self, asset_id):
        filter = [['entity', 'is', {'type': 'Asset', 'id': asset_id}], ['content', 'is', 'drama_rig']]
        fields = ['id']
        task_data = self._sg.find_one('Task', filter, fields)
        if not task_data:
            return False, u'not rig task'
        return True, task_data['id']

    def _get_latest_version_by_task_id(self, task_id):
        filters = [
            ['sg_task.Task.id', 'is', task_id]
        ]
        version_fields = ['sg_path_to_frames']
        additional_filter_presets = [
            {
                "preset_name": "LATEST",
                "latest_by": "ENTITIES_CREATED_AT"
            }
        ]
        laster_version = self._sg.find("Version", filters, version_fields,
                                       additional_filter_presets=additional_filter_presets)
        if not laster_version:
            return False, u'not version'
        return True, laster_version[0]['sg_path_to_frames']

    def _get_work_file_by_task_id(self, task_id):
        filter = [['id', 'is', task_id]]
        fields = ['sg_work']
        task_data = self._sg.find_one('Task', filter, fields)
        if not task_data:
            return False, u'not task'
        work_data = task_data.get('sg_work', None)
        if not work_data:
            return False, u'not work data'
        work_data = eval(work_data)
        return True, work_data.get('work_file', None)

    def judge_item_asset(self, asset_id):
        filter = [['id', 'is', asset_id], ['sg_asset_type', 'is', 'item']]
        fields = ['id']
        asset_data = self._sg.find_one('Asset', filter, fields)
        if not asset_data:
            return False
        return True

    def _get_parent_item_asset(self, asset_id):
        fields = ['parents']
        filters = [
            ['id', 'is', asset_id]
        ]
        asset = self._sg.find_one('Asset', filters, fields)
        if not asset or 'parents' not in asset or not asset['parents']:
            return False, u'not parent asset'
        parent_assets = asset['parents']
        item_parent_id = []
        for parent in parent_assets:
            parent_id = parent['id']
            __judge = self.judge_item_asset(parent_id)
            if __judge:
                item_parent_id.append(parent_id)
        if not item_parent_id:
            return False, u'not item parent asset'
        if len(item_parent_id) > 1:
            return False, u'more than one item parent asset'
        return True, item_parent_id[0]





    def _get_rig_task_data_by_asset(self, asset_id):
        asset_ok, asset_name = self._get_asset_name_from_id(asset_id)
        if not asset_ok:
            return False, u'not asset'
        __work_file = '{}.{}.v001.ma'.format(asset_name, TASK_NAME)
        __task_data = get_task.TaskInfo(__work_file, 'X3', 'maya', 'publish', is_lastversion=True)
        if not __task_data:
            return False, u'not rig task'
        return True, __task_data

    def _judge_variant_asset(self, asset_id):
        filter = [['id', 'is', asset_id], ['sg_asset_type', 'is', 'item'], ['parents', 'is_not', None]]
        fields = ['id']
        asset_data = self._sg.find_one('Asset', filter, fields)
        if not asset_data:
            return False
        return True

    def _get_asset_name_from_id(self, asset_id):
        fields = ['code']
        filters = [
            ['id', 'is', asset_id]
        ]
        asset = self._sg.find_one('Asset', filters, fields)
        if asset and 'code' in asset:
            return True, asset['code']
        else:
            return False, u'not asset'


if __name__ == '__main__':
    asset_id = 20658
    handle=RepublishItemVariantAssetRig(asset_id)
    handle.run()

