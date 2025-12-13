# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       : process_export_rig_mb_fbx
# Describe   : 导出_MB.fbx文件
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2023/8/8__16:48
# -------------------------------------------------------
import apps.publish.process.maya.process_mobu_fbx as process_mobu_fbx

reload(process_mobu_fbx)

from lib.maya.analysis.analyze_config import AnalyDatas
from apps.publish.process.maya.process_export_fbx import Porcess_Export
import maya.cmds as cmds
import lib.maya.process.bs_break as bs_break

reload(bs_break)
import lib.maya.process.export_fbx as _fbx_common

reload(_fbx_common)
import os
import method.maya.common.hik_fun as hik_fun
import method.maya.common.file as filecommon

CLEARJIONS = ['DB_*', 'AP_*', '*No_Twist*']
from threading import Thread, Lock
import time


class ProcessExportRigMbFbx(Porcess_Export):
    def __init__(self, TaskData, mb_export=True, down=True, up=False, ui=True):
        Porcess_Export.__init__(self, TaskData, down=down, up=up)
        self.taskdata = TaskData
        self._work_data_dir = TaskData.work_data_dir
        self._publish_data_dir = TaskData.publish_data_dir
        self._entity_name = TaskData.entity_name
        self._asset_type = TaskData.asset_type
        self._file = cmds.file(q=1, exn=1)
        self._mb_export = mb_export

        self._work_fbx_dir = '{}/fbx'.format(self._work_data_dir)
        self._publish_fbx_dir = '{}/fbx'.format(self._publish_data_dir)
        self._asset_type = TaskData.asset_type
        if not os.path.exists(self._work_fbx_dir):
            os.makedirs(self._work_fbx_dir)

        self._task_name = TaskData.task_name
        self._down = down
        self._up = up
        self._ui = ui
        self._fbx_data = AnalyDatas(TaskData, 'mb_fbx.json').get_datas()
        if not self._fbx_data:
            return

    def export_mb_fbx(self):
        return self.export_motion_builder_fbx()
        # 2024 07 26 根据需求修改(聪聪)

        # if self._asset_type  in ['cartoon_body','cartoon_role']:
        #     return
        # else:
        #     if self._mb_export == True:
        #         return self.export_motion_builder_fbx()

    def export_motion_builder_fbx(self):
        u"""
        导出_MB.fbx文件
        :return:
        """
        import time
        _fbx_info = self._get_fbx_info()
        if not _fbx_info:
            return {}

        self._open_file(self._file)

        #
        _fbx_file = self._export_mb_fbx(_fbx_info)
        if not _fbx_file:
            return
        _fbx_file = self._waite_file_process(_fbx_file, _wait_time=1800)
        if not _fbx_file:
            return False

        self.process_mb_fbx(_fbx_file)

        time.sleep(1)

        # 打包上传字典

        if _fbx_file and os.path.exists(_fbx_file):
            return self.package_work_publish([_fbx_file], _key='mbfbx')

    def process_mb_fbx(self, _fbx_file):
        lock = Lock()
        global n
        # 加锁
        lock.acquire()
        try:
            result = process_mobu_fbx.process_mobu_fbx(_fbx_file, ui=self._ui)
            if result == True:
                print('process_mobu_fbx success')
        finally:

            lock.release()

    def _open_file(self, _file):
        u"""
        打开maya文件
        :param _file:
        :return:
        """
        return filecommon.BaseFile().open_file(_file)

    def _export_mb_fbx(self, _fbx_info):
        _fbx_file = _fbx_info.get("fbx_file")
        _fbx_model_grps = _fbx_info.get("model_grp")
        if self._entity_name.endswith('_New') and self._asset_type in ['body', 'cartoon_body']:
            _fbx_model_grps_new = []
            for i in range(len(_fbx_model_grps)):
                _fbx_model_grps_new.append(
                    _fbx_model_grps[i].replace('_HD', '_New_HD').replace('_LD', '_New_LD').replace('_UE', '_New_UE'))
            _fbx_model_grps = _fbx_model_grps_new

        _fbx_objs = _fbx_info.get("fbx_objs")
        if self._entity_name.endswith('_New') and self._asset_type in ['body', 'cartoon_body']:
            _fbx_objs_new = []
            for i in range(len(_fbx_objs)):
                _fbx_objs_new.append(
                    _fbx_objs[i].replace('_HD', '_New_HD').replace('_LD', '_New_LD').replace('_UE', '_New_UE'))
            _fbx_objs = _fbx_objs_new
        if not _fbx_file or not _fbx_model_grps or not _fbx_objs:
            return
        return self._export_fbx(_fbx_objs, _fbx_file, _fbx_model_grps)

    def _waite_file_process(self, _file, _wait_time):
        u"""
        等待文件处理完成
        :param _file: (文件)
        :param _wait_time: 等待时间(秒)
        :return:
        """
        import time
        _time = 0
        _file_size = self._get_file_size(_file)
        while _time <= _wait_time:
            _time += 1
            _file_size_new = self._get_file_size(_file)
            if os.path.exists(_file) and _file_size_new == _file_size:
                return _file
            else:
                _file_size = _file_size_new
                time.sleep(1)
                _time += 1
            if _time >= _wait_time:
                return ''

    def _get_file_size(self, _file):
        u"""
        获取文件大小
        :param _file:
        :return:
        """
        if _file and os.path.exists(_file):
            return os.path.getsize(_file)

    def _export_fbx(self, fbx_objs, fbx_file, fbx_model_grps):
        import time

        # 先删除fbx文件
        self._remove_file(fbx_file)

        # if self._asset_type and self._asset_type.lower() in ['body']:
        #     self.clear_body_joins()
        #
        # 清理Group 组
        if self._asset_type not in ['item']:
            self._disconnet_joins(objs=['Roots'])
        else:
            self._disconnet_joins(objs=['Root_M'])

        # 断开组下所有模型连接
        self._disconnet_mesh_grps(fbx_model_grps)
        #
        cmds.cycleCheck(e=False)

        # 切换
        character = self._swithch_character_stance()
        if not character:
            # if self._ui:
            #     cmds.confirmDialog(t=u'报错信息', m=u'角色未角色化成功.请检查Character', b=u'确定')
            #     cmds.error(u'角色未角色化成功.请检查Character')
            return
        _fbx_objs = self._get_objs(fbx_objs)
        time.sleep(2)

        # 导出fbx
        if self._asset_type:
            if self._asset_type.lower() not in ['npc', 'item', 'enemy', 'fx', 'cartoon_fx']:
                _fbx_objs = self._sect_grps_mes_trs(fbx_objs)
                roots = cmds.ls('Roots', type='joint')
                if roots and _fbx_objs:
                    _fbx_objs.extend(roots)
                if (self._asset_type.lower() in ['body'] and self._entity_name.endswith(
                        '_RM')) or self._task_name == 'rbf_rm' or self._task_name == 'out_rig_rm':
                    ik_roots = cmds.ls('ik_*_root', type='joint')
                    self._disconnet_joins_without_constraints(objs=ik_roots)
                    if ik_roots:
                        _fbx_objs.extend(ik_roots)
                        __joins = self.get_ch_joins_from_objs(ik_roots)
                        if __joins:
                            self._disconnet_joins_without_constraints_by_objs(objs=__joins)
                            _fbx_objs.extend(__joins)

                    return self._export_fbx_base(_fbx_objs, fbx_file, _dismesh=False, constrains=1)

                return self._export_fbx_base(_fbx_objs, fbx_file, _dismesh=False, constrains=0)
            else:
                return self._export_fbx_base(_fbx_objs, fbx_file, _dismesh=False, constrains=0)

    def get_ch_joins(self, _joint):
        return cmds.listRelatives(_joint, ad=1, type='joint', f=1)

    def get_ch_joins_from_objs(self, _objs):
        _joints = []
        for _obj in _objs:
            _joints.extend(self.get_ch_joins(_obj))
        return _joints

    def clear_body_joins(self):
        u"""
        删除 AP
        Returns:

        """
        _clear_joins = cmds.ls(CLEARJIONS, type='joint')
        if _clear_joins:
            self._delete_objs(_clear_joins)

    def _disconnet_joins(self, objs):
        u"""
        断开Roots
        :return:
        """
        if objs:
            for obj in objs:
                if obj and cmds.ls(obj):
                    cons = cmds.listConnections(obj, s=1, p=1, c=1)
                    if cons:
                        for i in range(0, (len(cons) - 1), 2):
                            try:
                                cmds.disconnectAttr(cons[i + 1], cons[i])
                            except:
                                pass

    def _disconnet_joins_without_constraints(self, objs):

        if objs:
            for obj in objs:
                if obj and cmds.ls(obj):
                    cons = cmds.listConnections(obj, s=1, p=1, c=1)
                    if cons:
                        for i in range(0, (len(cons) - 1), 2):
                            if cmds.nodeType(cons[i + 1]) not in ['parentConstraint']:
                                try:

                                    cmds.disconnectAttr(cons[i + 1], cons[i])
                                except:
                                    pass

    def _disconnet_joins_without_constraints_by_objs(self, objs):
        # from lib.common.log import Logger
        # __log_handle=Logger('E:\\tessst\\test.log')

        if not objs:
            return
        for obj in objs:
            __cons = cmds.listConnections(obj, s=1, d=0, type='constraint')
            if not __cons:
                continue
            __cons = list(set(__cons))
            __cons = self._get_objs_by_nodes(__cons)
            if not __cons:
                continue
            for __con in __cons:
                _constraint_cons = cmds.listConnections(__con, s=1, d=0, p=1)
                if _constraint_cons:
                    _constraint_cons = list(set(_constraint_cons))
                    _constraint_cons = self._get_objs_by_nodes(_constraint_cons)

                    if not _constraint_cons:
                        continue
                    _constraint_cons = list(set(_constraint_cons))
                    for _constraint_con in _constraint_cons:
                        _constraint_con = cmds.ls(_constraint_con, l=1)[0] if cmds.ls(_constraint_con, l=1) else ''
                        if _constraint_con and cmds.nodeType(_constraint_con) in ['joint']:
                            if 'ik_' in _constraint_con:
                                self._disconnet_joins_without_constraints([_constraint_con])

                            else:
                                self._disconnet_joins([_constraint_con])

    def _get_objs_by_nodes(self, _nodes):
        if not _nodes:
            return
        _objs = []
        for _node in _nodes:
            _obj = _node.split('.')[0]
            if _obj and cmds.ls(_obj) and _obj not in _objs:
                _objs.append(_obj)
        return _objs

    def _swithch_character_stance(self):
        _character = self._get_character(['mb_to_maya', 'mb2maya'])
        if not _character:
            return
        self.updata_character(_character)
        self._set_hik_stance(_character)
        self.updata_character(_character)
        return _character

    def updata_character(self, _character):
        u"""
        更新Character
        :return:
        """
        import maya.mel as mel
        try:
            cmd = 'global string $gHIKCurrentCharacter;\n$gHIKCurrentCharacter = "{}";\nhikUpdateCharacterList();\nhikSetCurrentSourceFromCharacter($gHIKCurrentCharacter);\nhikUpdateSourceList();'.format(
                _character)
            mel.eval(cmd)
        except:
            pass

    def _set_hik_stance(self, _charcter):
        import maya.mel as mel
        try:
            _cmd = 'hikSetStanceInput("{}");'.format(_charcter)
            mel.eval(_cmd)
        except:
            pass

    def _get_source(self):
        return 'Stance'

    def _get_character(self, ends):
        hiknodes = hik_fun.get_hik_nodes()
        if not hiknodes:
            return
        _character = ''
        for hiknode in hiknodes:
            for end in ends:
                if hiknode.endswith(end):
                    _character = hiknode
                    break
        return _character

    def _remove_file(self, _file):
        u"""
        删除文件
        :param _file:
        :return:
        """
        if os.path.exists(_file):
            try:
                os.remove(_file)
            except:
                pass

    def _export_fbx_base(self, _exportobjs, _exportfile, _dismesh=True, constrains=0):
        u"""

        :param _exportobjs:
        :param _exportfile:
        :param _dismesh:
        :return:
        """
        if _exportobjs and _exportfile:
            try:
                if _dismesh == True:
                    _fbx_common.export_fbx(_exportobjs, _exportfile, hi=1, constrains=constrains, warning=0)
                else:
                    _fbx_common.export_fbx(_exportobjs, _exportfile, hi=0, constrains=constrains, warning=0)
                return _exportfile
            except:
                return

    def _disconnet_mesh_grps(self, _grps):
        u"""
        断开组下所有模型连接
        """
        grps = self._get_objs(_grps)

        _meshs = self._sect_grps_mes_trs(grps)
        cmds.select(_meshs)
        try:
            bs_break.mainFunc()
        except:
            pass

    def _get_objs(self, objs):
        _objs = []
        for obj in objs:
            if cmds.ls(objs):
                _objs.extend(cmds.ls(obj, l=1, tr=1))
        if _objs:
            return list(set(_objs))

    def _sect_grps_mes_trs(self, _grps):
        u"""
        从大组列表获得mesh tr 列表
        :param _grps:
        :return:
        """
        trs = []
        _meshs = self._get_meshs_from_grps(_grps)
        if _meshs:
            for _mesh in _meshs:
                tr = cmds.listRelatives(_mesh, p=1, type='transform', f=1)
                if tr:
                    trs.extend(tr)
        if trs:
            return list(set(trs))

    def _get_meshs_from_grps(self, _grps):

        _meshs = []
        if _grps:
            for _grp in _grps:
                _mshs = self.select_grp_meshs(_grp)
                if _mshs:
                    _meshs.extend(_mshs)
        return _meshs

    def _get_fbx_info(self):
        u"""
        获取fbx信息
        :return:
        """
        _dict = {}
        if self._fbx_data:
            for k, v in self._fbx_data.items():
                if k == 'fbx_file':

                    _dict[k] = '{}/{}'.format(self._work_fbx_dir, v)
                else:
                    _dict[k] = v
            return _dict

    def _get_local_dir(self):
        u"""
        获得本地工作目录
        :return:
        """
        import method.common.dir as _dir
        return _dir.set_localtemppath(sub_dir='temp_info/mb_fbx_export')


if __name__ == '__main__':
    import method.shotgun.get_task as get_task

    _filename = cmds.file(q=1, exn=1)
    taskdata = get_task.TaskInfo(_filename, 'X3', 'maya', 'version')

    handle = ProcessExportRigMbFbx(taskdata)
# print handle.export_mb_fbx()
