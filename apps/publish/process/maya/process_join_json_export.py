# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       : process_join_json_export
# Describe   : 说明描述
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2023/4/21__16:48
# -------------------------------------------------------
import lib.maya.analysis.analyze_config as analyze_config

import lushTools2.lipsyncExport as lipsyncExport
import lushTools2.faceRigExport as facerigExport

import lushTools2.qst_face_rig_export as qst_face_rig_export

import apps.publish.process.process_package as process_package
import method.maya.common.file as filecommon
import os

EXJOIT = 'SpeakBlendShapeBridge'

reload(facerigExport)
reload(lipsyncExport)

import maya.cmds as cmds


class ProcessJsonExport(object):
    """
    """

    def __init__(self, TaskData, down=True, up=False):
        """
        实例初始化
        """
        super(ProcessJsonExport, self).__init__()

        self.entity_name = TaskData.entity_name
        self.assettype = TaskData.asset_type
        self.task_name = TaskData.task_name
        self.step_name = TaskData.step_name
        self._work_data_dir = TaskData.work_data_dir
        self._publish_data_dir = TaskData.publish_data_dir
        self._work_bs_dir = '{}/bs'.format(self._work_data_dir)
        if not os.path.exists(self._work_bs_dir):
            os.makedirs(self._work_bs_dir)
        self._publish_bs_dir = '{}/bs'.format(self._publish_data_dir)
        self._file = cmds.file(q=1, exn=1)

        self._data = self._get_data
        self._down = down
        self._up = up

    def export_faceMorph_json(self):
        if self.assettype in ['body'] and self.entity_name.endswith('_Attach'):
            return
        _jsonfiles = self.export_face_json()
        print(_jsonfiles)
        if _jsonfiles:
            return self._package_work_publish(_jsonfiles)

    def export_face_json(self):
        """
        导出脸部json
        :return:
        """
        if self.assettype in ['cartoon_body']:
            _facerig_json=self.export_qst_facerig_json()
            if _facerig_json and os.path.exists(_facerig_json):
                return [_facerig_json]
        else:
            _jslist = []
            _lipsync_json = self.export_lipsync_json()
            self._open_file(self._file)
            _facerig_json = self.export_facerig_json()
            if _lipsync_json and os.path.exists(_lipsync_json):
                _jslist.append(_lipsync_json)
            if _facerig_json and os.path.exists(_facerig_json):
                _jslist.append(_facerig_json)
            return _jslist

    def _open_file(self, _file):
        u"""
        打开maya文件
        :param _file:
        :return:
        """
        return filecommon.BaseFile().open_file(_file)

    def _package_work_publish(self, workfiles):
        u"""
        打包上传字典
        Args:
            workfiles: 需要上传的本地文件列表

        Returns:

        """
        _dict = {}
        if workfiles:
            for fil in workfiles:
                _publish_file = '{}/{}'.format(self._publish_bs_dir, os.path.basename(fil))
                _dict[fil] = _publish_file
        if _dict:
            _package_dict = process_package.datapack_dict(_dict, down=self._down, up=self._up)
            return {'fbx': _package_dict}

    def export_lipsync_json(self):
        """
        导出嘴部json
        :return:
        """
        import maya.cmds as cmds
        _face_joins = self._get_face_joins
        _tongue_joins = self._get_tongue_joins
        _json_name = self._get_lipsync_json
        _json_work = '{}/{}'.format(self._work_bs_dir, _json_name)
        AU, FACS = range(2)
        if self.assettype in ['body','cartoon_body'] and self.task_name in ['drama_rig',
                                                           'lan_rig'] and "PL_Body" not in self.entity_name:
            lipsyncExport.lip_export(_json_work, _face_joins, _tongue_joins, FACS)
            return _json_work
        if self.assettype == 'npc' and self.task_name in ['rbf', 'lan_rbf'] and cmds.ls(EXJOIT):
            lipsyncExport.lip_export(_json_work, _face_joins, _tongue_joins, AU)
            return _json_work

    def export_facerig_json(self):
        u"""

        :return:
        """
        import maya.cmds as cmds
        _face_joins = self._get_face_joins
        _bs_name = self._get_head_bs
        _json_name = self._get_facerig_json
        _json_work = '{}/{}'.format(self._work_bs_dir, _json_name)
        NPC, CORE = range(2)
        if self.assettype in ['body']  and self.task_name == 'drama_rig' and "PL_Body" not in self.entity_name:
            facerigExport.face_rig_export(_json_work, CORE, _face_joins, _bs_name)
            return _json_work
        if self.assettype == 'npc' and self.task_name == 'rbf' and cmds.ls(EXJOIT):
            facerigExport.face_rig_export(_json_work, NPC, _face_joins, _bs_name)
            return _json_work

    def export_qst_facerig_json(self):
        import maya.cmds as cmds
        _head_mesh=self._get_cartoon_body_head_mesh
        _json_name = self._get_facerig_json
        _json_work = '{}/{}'.format(self._work_bs_dir, _json_name)
        if _head_mesh and cmds.ls(_head_mesh):
            cmds.select(_head_mesh)
            try:
                qst_face_rig_export.export_q_face_rig(_json_work)
                return _json_work
            except:
                return None


    def _get_bs_node(self, _bsdict):
        u"""
        获取bs节点
        :param _bsdict:
        :return:
        """
        _bs_node = []
        if _bsdict:
            for k, v in _bsdict.items():
                _bs_node.append(v)

    def _cover_body_new(self, jsonfile):
        if jsonfile and self.assettype in ['body','cartoon_body'] and self.entity_name.endswith('_New'):
            return jsonfile.replace('_FaceData.json', '_New_FaceData.json').replace('_FACS', '_New_FACS').replace('_AU',
                                                                                                                  '_New_AU')
        else:
            return jsonfile

    @property
    def _get_lipsync_json(self):
        u"""

        :return:
        """
        try:
            jsonfile = self._data[self.assettype]["lipsync_json"]
            return self._cover_body_new(jsonfile)
        except:
            return ""

    @property
    def _get_facerig_json(self):
        u"""

        :return:
        """
        try:

            jsonfile = self._data[self.assettype]["facerig_json"]
            return self._cover_body_new(jsonfile)
        except:
            return ""

    @property
    def _get_face_joins(self):
        """
        获取面部骨骼
        :return:
        """
        try:
            return self._data[self.assettype]["face_joins"]
        except:
            return []

    @property
    def _get_tongue_joins(self):
        """
        获取舌头骨骼
        :return:
        """
        try:
            return self._data[self.assettype]["tongue_joins"]
        except:
            return []

    @property
    def _get_cartoon_body_head_mesh(self):

        try:
            return self._data[self.assettype]["cartoon_head_bs"]["mesh"]
        except:
            return ""

    @property
    def _get_head_bs(self):
        u"""
        获取头部bs
        :return:
        """
        try:
            return self._data[self.assettype]["entity_bs"][self.entity_name]["bs"]
        except:
            return ""

    @property
    def _get_data(self):
        """
        获取数据
        :return:
        """
        return self._cover_data(analyze_config.AnalyConfigBase(configfile="head_joins.json", dcc="maya").data)

    def _cover_data(self, data):
        """
        转换数据s
        :param data:
        :return:
        """
        return eval(
            str(data).replace("{entity_name}", self.entity_name).replace("{ad}", self.entity_name.split('_')[0]))

if __name__ == '__main__':
    import method.shotgun.get_task as get_task

    _file = cmds.file(q=1,exn=1)

    taskdata = get_task.TaskInfo(_file, 'X3', 'maya', 'version')
    _handle = ProcessJsonExport(taskdata)

    # print(_handle._data['body'].keys())
    # print(_handle.export_faceMorph_json())
