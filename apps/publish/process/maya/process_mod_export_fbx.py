# -*- coding: utf-8 -*-#
# Python     : 
# -------------------------------------------------------
# NAME       : process_mod_export_fbx
# Describe   : mod export fbx
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2025/3/25__17:16
# -------------------------------------------------------
import time

import apps.publish.process.maya.process_export_fbx as process_export_fbx

from apps.publish.process.maya.process_export_fbx import Porcess_Export

import lib.maya.process.export_fbx as _fbx_common

import lib.maya.plugin as maya_plugin

import lib.maya.process.exoprt_ani_fbx as _fbx_ani_common
import lib.maya.analysis.analyze_fbx as analyze_fbx
import method.maya.common.file as filecommon
import maya.cmds as cmds
import os
import lib.maya.process.bs_break as bs_break

reload(_fbx_ani_common)
reload(process_export_fbx)
reload(_fbx_common)
reload(bs_break)
EYELASHES = ['*_Eyelashes', '*_Eyelash']
import shutil

import method.common.fbx_import as common_fbx_import

reload(common_fbx_import)
from apps.publish.process.maya.process_rig_export_fbx import Porcess_RigFbx_Export


class ProcessModFbxExport(Porcess_RigFbx_Export):
    def __init__(self, TaskData, down=True, up=False):
        Porcess_RigFbx_Export.__init__(self, TaskData, down=down, up=up)
        self.taskdata = TaskData
        self._work_data_dir = TaskData.work_data_dir
        self._publish_data_dir = TaskData.publish_data_dir
        self._entity_name = TaskData.entity_name
        self._file = cmds.file(q=1, exn=1)

        self._work_fbx_dir = '{}/fbx'.format(self._work_data_dir)
        if not os.path.exists(self._work_fbx_dir):
            os.makedirs(self._work_fbx_dir)
        self._publish_fbx_dir = '{}/fbx'.format(self._publish_data_dir)
        self._asset_type = TaskData.asset_type

        self._task_name = TaskData.task_name
        self._entity_id = TaskData.entity_id
        self._down = down
        self._up = up

    def export_mob_fbx(self):
        u"""
        导出rig fbx
        @return:
        """
        try:
            maya_plugin.plugin_load(['fbxmaya'])
        except:
            pass
        __result = True
        if __result:
            _fbx_dict = self._get_fbx_info()

            # 导出fbx
            _fbxfiles = self._export_mod_final_fbx(_fbx_dict)
            # 导出fbx
            _mbfbxfiles = []
            _up_data = {}
            _fbx_dict = self.package_work_publish(_fbxfiles, _key='fbx')
            if _fbx_dict:
                _up_data.update(_fbx_dict)
            return _up_data
        else:
            return

    def _export_mod_final_fbx(self, _dict):
        u"""
        导出fbx
        :param _dict: 例{file01:[objs01,fbx01]}
        :return:
        """
        _list = []
        if _dict:
            for k, v in _dict.items():
                if v:
                    # 打开rig 文件,减少问题
                    self._open_file(self._file)
                    # 输出fbx
                    for _fbx_file, _result in v.items():
                        _objs, _triangulate = _result
                        try:
                            _result = self._export_mdl_fbx(_objs, _fbx_file, _dismesh=k, _triangulate=_triangulate)

                            if _result and _result == True:
                                if "_Render" in _fbx_file:
                                    if _fbx_file and os.path.exists(_fbx_file):
                                        _list.extend([_fbx_file])
                                else:
                                    _list.extend([_fbx_file])
                            if "_Render" in _fbx_file:
                                self._open_file(self._file)

                        except:
                            pass
        return _list

    def _export_mdl_fbx(self, _exportobjs, _exportfile, _dismesh=True, _triangulate=0):
        u"""
        导出fbx
        @param _exportobjs: 需要导出fbx的物体列表
        @param _exportfile: 导出的fbx文件
        @param _dismesh: 为True时，断开_exportobjs组下所有模型连接
        @return:
        """
        result = False
        # 显示组及组以下模型组
        self.__dispaly_grps_objs(_exportobjs)

        # body 添加去睫毛版本fbx
        if '_Render' in _exportfile:
            _exportobjs = [_exportobj.split('_{Eyelashes}')[0] for _exportobj in _exportobjs if _exportobj]
            # 删除睫毛
            if _exportobjs:
                self._delete_eyelashes()
            else:
                _exportobjs = []

        if _dismesh == True:
            if self._task_name in ['drama_mdl', 'fight_mdl'] and \
                    os.path.splitext(os.path.basename(_exportfile))[0].split('_')[-1] not in [
                'asis'] and self._asset_type.lower() not in ['item']:
                _sg = self._create_shader(name='lambert_combine', type='lambert')
                _meshs = self._sect_grps_mes_trs(_exportobjs)
                self._assign_shader(_sg, _meshs)

        if _dismesh == True and self._asset_type.lower() not in ['npc', 'enemy']:
            _meshs = self._sect_grps_mes_trs(_exportobjs)
            if _meshs:
                _exportobjs = _meshs
            else:
                _exportobjs = []

        if "_GuaranteedAnim" in _exportfile:
            # 保存下文件
            _file = _exportfile.replace(".fbx", ".ma")
            filecommon.BaseFile().save_file(_file)

            _joins = self._get_joins("Root_M")

            _exportfile = _exportfile.replace('\\', '/')
            _clip = os.path.basename(_exportfile).split('_')[-1].split('.')[0]
            self._bake_joins(_joins, 0, 30)
            _file_fbx = self._export_animation_fbx(objlist=_joins, export_path=_exportfile, dis=1, usescenename=1)
            filecommon.BaseFile().new_file()
            if os.path.exists(_file):
                os.remove(_file)
            if _file_fbx and _file_fbx != False:
                result = True

        else:
            if _exportobjs and self._asset_type.lower() not in ['npc', 'enemy'] and self._task_name not in ['rbf_m',
                                                                                                            'out_rig_rm']:
                result = self._export_fbx_base(_exportobjs, _exportfile, _triangulate=_triangulate, _dismesh=_dismesh)
            elif _exportobjs and self._asset_type.lower() not in ['npc', 'enemy'] and self._task_name in ['rbf_m',
                                                                                                          'out_rig_rm']:
                result = self._export_fbx_base(_exportobjs, _exportfile, _triangulate=_triangulate, _dismesh=_dismesh,
                                               _constrains=1)
            if _exportobjs and self._asset_type.lower() in ['npc', 'enemy']:
                result = self._export_fbx_base(_exportobjs, _exportfile, _triangulate=_triangulate, _dismesh=False)
        if result and result != False:
            return True

    def _delete_eyelashes(self):
        u"""
        删除睫毛
        :return:
        """
        try:
            _eyelashes = self._delete_objs(cmds.ls(EYELASHES))
        except:
            pass

    def __dispaly_grps_objs(self, grps):
        if not grps:
            return
        for grp in grps:
            self.__display_grp_objs(grp)

    def __display_grp_objs(self, grp):
        objs = []
        if not grp:
            return
        if not cmds.ls(grp):
            return
        objs.append(grp)
        _children = cmds.listRelatives(grp, ad=1, type='transform')
        if _children:
            objs.extend(_children)
        for obj in objs:
            self.__display_obj(obj)

    def __display_obj(self, obj):
        attr = '{}.visibility'.format(obj)
        if not obj:
            return
        if not cmds.ls(obj):
            return
        if not cmds.ls(attr):
            return
        vis = cmds.getAttr(attr)
        if vis != True:
            self.__unlock_obj(obj)
            self.__unlocek_attr(attr)
            self.__dis_connected_attr(attr)
            self.__set_attr(attr, 1)

    def __process_q_body_lod_fbx(self, fbx_file):
        __fbx_handle = common_fbx_import.FbxImport(fbx_file)
        __all_nodes = __fbx_handle.get_all_nodes()
        _p_name = ''
        for node in __all_nodes:
            node_name = node.GetName()
            if node_name.endswith('_Rig'):
                _p_name = node_name.split('_Rig')[0]
                break
        if not _p_name:
            return
        __node_name = '{}_Head_lod'.format(_p_name)
        __node_new_name = '{}_Head'.format(_p_name)
        __node = __fbx_handle.get_node_by_name(__node_name)
        if not __node:
            return
        __bs_nodes = __fbx_handle.get_bs_nodes_from_node(__node)
        __bs_node = None
        __bs_node_new = None
        for bs_node in __bs_nodes:
            if bs_node.GetName().endswith('_lod_bs'):
                __bs_node = bs_node
                break
        if __bs_node != None:
            __bs_node_new = '{}_Head_bs'.format(_p_name)
        if __node:
            __fbx_handle.rename_node(__node, __node_new_name)
        if __bs_node and __bs_node_new:
            __fbx_handle.rename_node(__bs_node, __bs_node_new)
        __fbx_handle.save_fbx(fbx_file)
        return True

    def __set_attr(self, attr, key=True):
        try:
            cmds.setAttr(attr, key)
        except:
            pass

    def __unlock_obj(self, obj):
        try:
            cmds.lockNode(obj, l=0)
        except:
            pass

    def __unlocek_attr(self, attr):
        try:
            cmds.setAttr(attr, l=0)
        except:
            pass

    def __dis_connected_attr(self, attr):
        con = cmds.listConnections(attr, s=1, d=1, p=1)
        if not con:
            return
        cons = cmds.listConnections(attr, s=1, d=1, p=1, c=1)
        for i in range(len(cons)):
            try:
                cmds.disconnectAttr(cons[i + 1], cons[i])
            except:
                pass

    def _open_file(self, _file):
        u"""
        打开maya文件
        :param _file:
        :return:
        """
        return filecommon.BaseFile().open_file(_file)

    def _get_fbx_info(self):
        u"""
        获取需要导出fbx的信息
        :return:
        """
        _dict = {}
        _objs_fbx_dict = self._get_objs_fbxfile()
        _work_dir = self._get_local_dir()
        for k, v in _objs_fbx_dict.items():
            if k and v:
                if k == 'joins':
                    #
                    _key = False
                else:
                    _key = True
                _dict[_key] = v
        return _dict

    def _get_objs_fbxfile(self):
        u"""
        根据配置文件获得需要导出fbx的物体和fbx文件
        @return:
        """
        _dict = {}
        _mod_dict = {}
        _joins_dict = {}
        _root_grp = self._get_body_root()
        _gprs = self._select_grp_grps(_root_grp)
        _grp_shorts = self._short_list
        # 配置文件信息
        _fbx_info = analyze_fbx.AnalyFbx(self.taskdata).get_fbx()
        # {ad}变量
        _ad = self._get_mod_ad()
        # 转换{ad}变量
        _fbx_cv = self._cover_variable_info('{ad}', _ad, _fbx_info)
        if _fbx_cv:
            for i in range(len(_fbx_cv)):
                _objs = []
                if _fbx_cv[i] and 'fbx_objs' in _fbx_cv[i] and 'fbx_file' in _fbx_cv[i]:
                    _fbx_objs = _fbx_cv[i]['fbx_objs']
                    _fbx_file = _fbx_cv[i]['fbx_file']
                    if "triangulate" in _fbx_cv[i]:
                        _triangulate = _fbx_cv[i]["triangulate"]
                    else:
                        _triangulate = 0
                    if '_FX_' in _fbx_file:
                        _fx_dict = self._cover_FX_fbx(_fbx_file)
                        if _fx_dict:
                            for k, v in _fx_dict.items():
                                _fbx_work_fx = '{}/{}.fbx'.format(self._work_fbx_dir, v)
                                if _fbx_work_fx not in _mod_dict:
                                    _mod_dict[_fbx_work_fx] = [[k], _triangulate]

                    else:
                        _fbx_work = '{}/{}.fbx'.format(self._work_fbx_dir, _fbx_file)
                        if _fbx_objs:
                            if 'Roots' in _fbx_objs or "Root_M" in _fbx_objs:
                                _joins_dict[_fbx_work] = [_fbx_objs, _triangulate]
                            else:
                                _mod_dict[_fbx_work] = [_fbx_objs, _triangulate]
        if _mod_dict:
            _dict['mods'] = _mod_dict
        if _joins_dict:
            _dict['joins'] = _joins_dict
        return _dict

    def _get_mod_ad(self):
        u"""
        获取mod ad
        :return:
        """
        _ad = ''
        _roots = self.root_group
        for grp in _roots:
            if '_HD' in grp or '_LD' in grp and '00' in grp:
                _ad = grp.split('00')[0]
                _ad = _ad.split('|')[-1]
                break
        return _ad

    def _get_local_dir(self):
        u"""
        获得本地工作目录
        :return:
        """
        import method.common.dir as _dir
        return _dir.set_localtemppath(sub_dir='temp_info/fbx_export/mod')


if __name__ == '__main__':
    import method.shotgun.get_task as get_task

    _filename = 'YS_BODY.drama_mdl.v017.ma'
    taskdata = get_task.TaskInfo(_filename, 'X3', 'maya', 'version')
    _handle = ProcessModFbxExport(taskdata)
    print(_handle.export_mob_fbx())
