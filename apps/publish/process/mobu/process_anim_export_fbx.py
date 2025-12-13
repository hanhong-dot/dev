# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       : process_anim_export_fbx
# Describe   : cts_rough 动画输出fbx数据
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2023/5/6__15:56
# -------------------------------------------------------
import os
import sys
import tools.x3_P4.motionbuilder.x3_animation_exporter.functions as functions
import method.shotgun.get_task_data as get_task_data
#
import database.shotgun.core.sg_asset as sg_asset
import apps.publish.process.process_package as process_package

ITEMTYPE = ['item']
import pyfbsdk as fb

class MbExport(object):

    def __init__(self, TaskData, down=True, up=False):
        """
        实例初始化
        """
        super(MbExport, self).__init__()
        self.TaskData = TaskData
        self._task_id = self.TaskData.task_id
        self._entity_name = self.TaskData.entity_name
        self._task_data = get_task_data.TaskData(self._task_id, _dcc='mobu')
        self._publish_dir = self._task_data.publish_dir
        self._work_fbx_dir = '{}/fbx'.format(self._task_data.work_data_dir)
        self._publish_fbx_dir = '{}/fbx'.format(self._task_data.publish_data_dir)
        self._sg = self._task_data.sg
        self._project_name = self._task_data.project_name
        self._down = down
        self._up = up

    def export_ani_fbx(self):
        u"""
        输出动画fbx
        :return:
        """
        _fbx_list = []
        _chr_fbx = self.export_chr_fbx()
        _cam_fbx = self.export_cama_fbx()
        # _item_fbx = self.export_item_fbx()
        if _chr_fbx:
            _fbx_list.extend(_chr_fbx)
        if _cam_fbx:
            _fbx_list.append(_cam_fbx)
        # if _item_fbx:
        #     _fbx_list.append(_item_fbx)
        if _fbx_list:
            return self.package_work_publish(_fbx_list, _key='fbx')

    def export_chr_fbx(self):
        u"""
        输出角色fbx
        :return:
        """
        _chr_list = self._get_chr_asstes_rig()
        _fbx_list = []
        for _chr in _chr_list:
            _asset_name = self.select_mod_assetname(_chr)
            _asset_type = self.get_asset_type(_asset_name)
            _work_path = ''
            if _asset_type and _asset_type not in ITEMTYPE:
                if _asset_type.lower() == 'body':

                    _work_path = '{}\\{}_{}.fbx'.format(self._work_fbx_dir, _asset_name.split('_')[0],
                                                        self._entity_name)
                else:
                    _work_path = '{}\\{}_{}.fbx'.format(self._work_fbx_dir, _asset_name, self._entity_name)

                functions.export([_chr], _work_path, mask_types=self._get_dy, start_frame=self._get_start_frame,
                                 end_frame=self._get_end_frame,export_camera=False)
                _fbx_list.append(_work_path)
        if _fbx_list:
            return list(set(_fbx_list))

    def select_mod_assetname(self, mod):
        return mod.split('::')[-1].split(':')[0].split('__')[0]

    def get_asset_type(self, assetname):
        u"""

        :param assetname:
        :return:
        """
        return sg_asset.select_asset_entity_by_name(self._sg, self._project_name, assetname)['sg_asset_type']


    def export_cama_fbx(self):
        u"""
        输出相机fbx
        :return:
        """
        _work_path = '{}\\Cam_{}.fbx'.format(self._work_fbx_dir,self._entity_name)
        return functions.export_camera(_work_path, self._get_start_frame, self._get_end_frame)

    # def export_item_fbx(self):
    #     u"""
    #     输出道具fbx
    #     :return:
    #     """
    #     _work_path = ''
    #     ok, reason = functions.export_item(_work_path, item_root_m, binding_character_name, binding_hpoint,
    #                                        self._get_start_frame, self._get_end_frame)
    #     if ok:
    #         return work_path

    @property
    def _get_dy(self):
        return ['correct', 'cloth', 'DynamicBone', 'face', 'AP']

    @property
    def _get_start_frame(self):
        u"""
        获取起始帧
        :return:
        """
        return fb.FBPlayerControl().ZoomWindowStart.GetFrame()

    @property
    def _get_end_frame(self):
        u"""
        获取结束帧
        :return:
        """
        return fb.FBPlayerControl().ZoomWindowStop.GetFrame()

    def _get_asset_id(self, asset_name):
        u"""
        获取资产id
        :return:
        """
        try:
            return sg_asset.select_asset_assetID(self._sg, self._project_name, asset_name)[0]['id']
        except Exception as e:
            print e
            return None

    def package_work_publish(self, workfiles, _key='fbx'):
        u"""
        打包上传字典
        Args:
            workfiles: 需要上传的本地文件列表

        Returns:

        """
        _dict = {}
        _fbx_dict = {}
        _json_dict = {}
        _updata_dict = {}
        if workfiles:
            print(workfiles)
            for fil in workfiles:
                if fil:
                    _publish_file = '{}/{}'.format(self._publish_fbx_dir, os.path.basename(fil))
                    _dict[fil] = _publish_file
        if _dict:
            _package_dict = process_package.datapack_dict(_dict, down=self._down, up=self._up)
            _fbx_dict = {_key: _package_dict}

        # 打包上传字典
        if _json_dict:
            _updata_dict.update(_json_dict)
        if _fbx_dict:
            _updata_dict.update(_fbx_dict)
        return _updata_dict

    def _get_asset_type(self, asset_name):
        u"""
        获取资产类型
        :return:
        """
        _asst_id = self._get_asset_id(asset_name)
        if _asst_id:
            try:
                return sg_asset.select_asset_entity(self._sg, _asst_id, asset_fields=['sg_asset_type'])['sg_asset_type']
            except Exception as e:
                print e
                return None

    def _get_asstes_rig(self):
        try:
            return functions.get_scene_character_full_names()
        except Exception as e:
            print e
            return None

    def _get_chr_asstes_rig(self):
        _assetlist = []
        _asset_rigs = self._get_asstes_rig()
        if _asset_rigs:
            for _asset in _asset_rigs:
                _asset_name = _asset.split('::')[1].split(':')[0].split('__')[0]
                _asset_type = self._get_asset_type(_asset_name)
                if _asset_type and _asset_type not in ITEMTYPE:
                    _assetlist.append(_asset)
        return _assetlist



import database.shotgun.core.sg_analysis as sg_analysis
import method.shotgun.get_task as get_task

sg = sg_analysis.Config().login()
_project_name = 'X3'
scene = fb.FBApplication().FBXFileName
_taskdata=get_task.TaskInfo(scene, _project_name, 'motionbuilder', 'version', is_lastversion=False)
_handle=MbExport(_taskdata)

print(MbExport(_taskdata).export_ani_fbx())


    # _asset_name='YG001S'
    # _project_name='X3'
    # _id=sg_asset.select_asset_assetID(sg, _project_name,_asset_name)[0]['id']
    #
    # print(_id)
    # _asset_id = 11116
    # print(sg_asset.select_asset_entity(sg, _asset_id, asset_fields=['sg_asset_type'])['sg_asset_type'])
    # _list = ['Model::YG001S:YG_Rig', 'Model::PL023C:PL_Rig', 'Model::YG001S__01:YG_Rig']
