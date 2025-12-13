# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       : republish_role_sub_republish
# Describe   : 说明描述
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2024/04/25__11:59
# -------------------------------------------------------
import os.path

from method.shotgun import sg_asset_fun

reload(sg_asset_fun)

TASKS = ['rbf']
ASSET_TYPES = ['role']
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

import shutil
import apps.publish.process.maya.process_sgfile as process_sgfile

reload(process_sgfile)


class RePubRoleSub(object):
    def __init__(self, TaskData, publish_status='ip'):
        self.__task_data = TaskData
        self.__entity_name = self.__task_data.entity_name
        self.__entity_id = self.__task_data.entity_id
        self.__task_name = self.__task_data.task_name
        self.__task_id = self.__task_data.task_id
        self.__asset_type = self.__task_data.asset_type
        self.__sg = sg_analysis.Config().login()
        self.publish_status = publish_status

    def republish_sub_assets(self, open_file=True, copy_publish_file=True, sub_asset_types=['weapon']):
        file_name = BaseFile().current_file()
        sub_ok, sub_assets = self.__get_sub_republish_assets(sub_asset_types)

        if sub_ok == False:
            return
        if copy_publish_file == True:
            self._copy_publish_file()

        publish_dict = {}

        if sub_ok == True and sub_assets:
            # re_sub_assets = sub_assets[::-1]

            for asset_id in sub_assets:
                asset_ok, asset_name = self._get_asset_name_from_id(asset_id)

                rbf_ok, rbf_result = self._get_publish_task(asset_id, 'rbf')
                if rbf_ok == True:
                    ok, resutl = self._batch_publish(asset_name, 'rbf', rbf_result[1], rbf_result[2])

                    if ok == True:
                        print u'{} {} publish successful, please check'.format(asset_name, 'rbf')
                        print rbf_result[1]
                        publish_dict[asset_id] = resutl

                else:
                    print u'{} {} does not exist or has no pbulish history, please check'.format(asset_name, 'rbf')

                if rbf_ok == False:
                    rig_ok, rig_result = self._get_publish_task(asset_id, 'drama_rig')
                    print('{} drama_rig'.format(asset_name), rig_result)
                    if rig_ok == True:
                        ok, resutl = self._batch_publish(asset_name, 'drama_rig', rig_result[1], rig_result[2])

                        if ok == True:
                            print u'{} {} publish successful, please check'.format(asset_name, 'drama_rig')
                            print rig_result[1]
                            publish_dict[asset_name] = resutl
                    else:
                        print u'{} {} does not exist or has no pbulish history, please check'.format(asset_name,
                                                                                                     'drama_rig')
        if publish_dict:
            for k, v in publish_dict.items():
                print(k)
                print(v)
        if open_file == True:
            BaseFile().open_file(file_name)
        return True

    def _copy_publish_file(self):
        import uuid
        import subprocess
        work_file = BaseFile().current_file()
        des_file = filehandle.remove_version(filehandle.get_publishfilepath(self.__task_data))
        local_dir = common_dir.set_localtemppath('temp_info/republish')
        _uuid = uuid.uuid4().get_hex()
        bat_file = '{}/rep_{}.bat'.format(local_dir, _uuid)

        work_file = work_file.replace('M:', '//10.10.201.151/share/product').replace('/', '\\')
        des_file = des_file.replace('M:', '//10.10.201.151/share/product').replace('/', '\\')

        infos = u'echo f | xcopy "{}" "{}" /h /y '.format(work_file, des_file)

        with open(bat_file, 'w') as f:
            f.write(infos)
        procmd = "{} {}".format(RUNAS_CMD, bat_file)

        p = subprocess.Popen(procmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        _info, _error = p.communicate()

    def _get_asset_name_from_id(self, asset_id):
        fields = ['code']
        filters = [
            ['id', 'is', asset_id]
        ]
        asset = self.__sg.find_one('Asset', filters, fields)
        if asset and 'code' in asset:
            return True, asset['code']
        else:
            return False, u'not asset'

    def __get_sub_republish_assets(self, sub_asset_types):
        if self.judge_sub_republish() != True:
            return False, u'no need to publish sub assets'
        __sub_asset_ids = self.__get_asset_sub_assets_ids(sub_asset_types)
        if not __sub_asset_ids:
            return False, u'no sub assets'

        return True, __sub_asset_ids

    # def get_asse_ids_from_sub_data(self, sub_data):
    #     asset_ids = []
    #     if sub_data:
    #         if isinstance(sub_data, int):
    #             if sub_data != self.__entity_id:
    #                 asset_ids.append(sub_data)
    #         if isinstance(sub_data, dict):
    #             for k, v in sub_data.items():
    #                 if k != self.__entity_id:
    #                     asset_ids.append(k)
    #                 if v and isinstance(v, list):
    #                     for i in range(len(v)):
    #                         ids = self.get_asse_ids_from_sub_data(v[i])
    #                         asset_ids.extend(ids)
    #         if isinstance(sub_data, list):
    #             for i in range(len(sub_data)):
    #                 ids = self.get_asse_ids_from_sub_data(sub_data[i])
    #                 asset_ids.extend(ids)
    #     return asset_ids

    def __get_asset_sub_assets_ids(self, sub_asset_types):
        __sub_asset_ids = []
        for __asset_type in sub_asset_types:
            sub_assets = sg_asset_fun.get_asset_sub_type_assset_ids(self.__sg, self.__entity_id,
                                                                    sub_asset_type=__asset_type)
            if sub_assets:
                for __sub_asset in sub_assets:
                    __sub_asset_id = __sub_asset['id']
                    if __sub_asset_id not in __sub_asset_ids:
                        __sub_asset_ids.append(__sub_asset_id)
        return __sub_asset_ids

    def _batch_publish(self, entity_name, task_name, work_file, version_file):
        from method.maya.common.file import BaseFile
        des = u'{}子资产,自动上传({}任务)'.format(self.__entity_name, self.__task_name)
        try:
            des = des.encode('utf-8').decode('gbk')
        except:
            des = u'{}'.format(des)
        fil_name = '{}.{}.v001.ma'.format(entity_name, task_name)
        work_file = work_file.replace('\\', '/')
        task_data = get_task.TaskInfo(fil_name, 'X3', 'maya', 'publish', is_lastversion=True)
        if task_data:
            BaseFile().open_file(work_file)

            result01, result02 = BatchPublish(task_data, version_file, des, statu='ip').do_batch_publish()
            if result01 and result02:
                return True, u'publish successful'

    def _get_publish_task(self, asset_id, task_name):
        ok, result = self._get_task_id(asset_id, task_name)
        if ok == True:
            task_id = result
            return self._get_publish_task_by_task_id(task_id)
        return False, u'not task'

    def _get_publish_task_by_task_id(self, task_id):
        work_file = ''
        version_file = ''
        ok, result = self._get_work_file(task_id)
        if ok == False:
            return False, u'not work file'

        if ok == True:
            work_file, work_dir = result
            _base_name = os.path.basename(work_file)
            _suffix = os.path.splitext(_base_name)[-1]
            __info = _base_name.split('.')
            __base_name = '{}.{}.v'.format(__info[0], __info[1])
            _laster_version_file = get_laster_file_by_base_name(work_dir, _suffix, __base_name)
            work_file_next = process_sgfile.get_next_version_file(_laster_version_file)
            if os.path.exists(work_file_next):
                work_file = process_sgfile.get_next_version_file(work_file_next)
            shutil.copy(work_file, work_file_next)

        if work_file:
            version_file = self._get_version_file(task_id)
        if work_file_next and version_file:
            return True, (task_id, work_file_next, version_file)
        else:
            return False, u'not work file or version file'

    def _get_task_id(self, asset_id, task_name):
        fields = ['id']
        filters = [
            ['content', 'is', task_name],
            {
                "filter_operator": "any",
                "filters": [
                    ["entity.Asset.id", "is", asset_id]
                ]
            }
        ]
        task = self.__sg.find('Task', filters, fields)
        if task and 'id' in task[0]:
            return True, task[0]['id']
        else:
            return False, u'not task'

    def _get_version_file(self, task_id):
        versions = sg_task.select_task_version(self.__sg, task_id)
        version_file = ''
        if versions:
            for i in range(len(versions) - 1, 0, -1):
                vesion_id = versions[i]['id']
                ok, result = self._get_version_file_from_version_id(vesion_id)
                if ok == True:
                    version_file = result
                    break
        return version_file

    def _get_version_file_from_version_id(self, version_id):
        version = sg_version.select_version_version(self.__sg, version_id, ['sg_path_to_frames'])
        if version and 'sg_path_to_frames' in version and version['sg_path_to_frames']:
            path = version['sg_path_to_frames']
            if path:
                return True, path
            else:
                return False, u'no version file'
        return False, u'no version file'

    def _get_work_file(self, task_id):

        filters = [
            ['id', 'is', task_id],

        ]
        work_file = ''
        work_dir = ''
        fields = ['sg_work']
        task = self.__sg.find_one('Task', filters, fields)

        if task and 'sg_work' in task and task['sg_work']:
            work_info = eval(task['sg_work'])
            if work_info and 'work_file' in work_info:
                work_file = work_info['work_file']

        print('work_file', work_file)
        if work_file and not os.path.exists(work_file):
            work_dir, work_f = os.path.split(work_file)
            work_dir_back = '{}/back'.format(work_dir)
            work_file = '{}/{}'.format(work_dir_back, work_f)
        elif work_file and os.path.exists(work_file):
            work_dir = os.path.dirname(work_file)
        if work_file and os.path.exists(work_file) and work_dir:
            return True, (work_file, work_dir)

        else:

            return False, u'not work file'

    def judge_sub_republish(self):
        result = True
        if self.__asset_type.lower() not in ASSET_TYPES:
            print('asset type error')
            result = False
        if self.__task_name not in TASKS:
            print('task name error')
            result = False

        # name = self.__entity_name.split('_')[0]
        # s_names = self.get_s_name()
        # match_name = ''
        # for s_name in s_names:
        #     if name.endswith(s_name):
        #         match_name = s_name
        #         break
        # if not match_name:
        #     result = False
        return result


def kill_command(p, timeout):
    import time
    time.sleep(timeout)
    p.kill


def get_laster_file_by_base_name(_dir, _suffixs, _basename):
    if _dir and os.path.exists(_dir):
        _filelist = [_i for _i in os.listdir(_dir) if
                     (os.path.splitext(_i)[-1] and os.path.splitext(_i)[-1] in _suffixs) and _basename in _i]
        if _filelist:
            _lastfile = sorted(_filelist)[-1]
            if _lastfile:
                return '{}/{}'.format(_dir, _lastfile)

# if __name__ == '__main__':
#     import method.shotgun.get_task as get_task
#     import maya.cmds as cmds
#
#     #
#     filename = cmds.file(q=1, exn=1)
#     #     filename='ST001S_Dirt.rbf.v001.png'
#     project = 'X3'
#     dcc = 'maya'
#     tag = 'publish'
#     #     task_id = 81627
#     task_data = get_task.TaskInfo(filename, project, dcc, tag, is_lastversion=False)
#     handle = RePubRoleSub(task_data)
#     handle.republish_sub_assets(open_file=False, copy_publish_file=True)
#
#     handle = RePubliSub(task_data)
#     # {20319: [{30841: [{'type': 'Asset', 'id': 21002, 'name': 'FY006W'}]}]}
#     # {20319: [{'type': 'Asset', 'id': 30841, 'name': 'FY004S_Ng'}]}
#     # print(handle._get_version_file(task_id))
#     print(handle._get_sub_republish_assets())
#     # print(handle._get_asset_sub_assets_info())
