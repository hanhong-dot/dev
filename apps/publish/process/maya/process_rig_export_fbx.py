# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       : process_rig_export_fbx
# Describe   : 说明描述
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2022/10/8__18:29
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

CLEARJIONS = ['DB_*', 'AP_*']
# 2023.3.1 四个角色的ue_rig 任务多出一个不带睫毛的fbx文件 (_Render后缀)
# BODYS = ['RY_BODY', 'ST_BODY', 'YG_BODY', 'YS_BODY']
# 2023.3.15根据要求，BODY角色全部出
TASKS = ['ue_rig', 'ue_rig_low']
EYELASHES = ['*_Eyelashes', '*_Eyelash']
COMSHADER = 'lambert'
import shutil

import method.common.fbx_import as common_fbx_import

reload(common_fbx_import)
import database.shotgun.fun.get_entity as get_entity

reload(get_entity)
import database.shotgun.core.sg_analysis as sg_analysis
import method.common.judge_online_version_entity as judge_online_version_entity

reload(judge_online_version_entity)

EXASSETS = ['M3011_Puppet01', 'M3111_Obsidian01', 'M3013_Puppet05', 'M3017_Puppet09', 'M3011_Puppet01_test',
            'M3011_Puppet01_Card', 'M3451_STCardSkeleton01', 'M3451_STCardSkeleton01_Card', 'M3121_DirewolfCard01',
            'M3121_DirewolfCard02', 'NPC_Ecat01', 'NPC_Ecat02', 'NPC_Ecat02']


# log_file=r'Z:\TD\0812\test.log'
# from lib.common.log import Logger
# log_handle=Logger(log_file)
class Porcess_RigFbx_Export(Porcess_Export):
    def __init__(self, TaskData, down=True, up=False):
        Porcess_Export.__init__(self, TaskData, down=down, up=up)
        self.taskdata = TaskData
        self._work_data_dir = TaskData.work_data_dir
        self._publish_data_dir = TaskData.publish_data_dir
        self._entity_name = TaskData.entity_name
        self.entity_id = TaskData.entity_id
        self.entity_type = TaskData.entity_type
        self._file = cmds.file(q=1, exn=1)

        self._work_fbx_dir = '{}/fbx'.format(self._work_data_dir)
        if not os.path.exists(self._work_fbx_dir):
            os.makedirs(self._work_fbx_dir)
        self._publish_fbx_dir = '{}/fbx'.format(self._publish_data_dir)
        self._asset_type = TaskData.asset_type
        self.sg = sg_analysis.Config().login()

        self._asset_level = get_entity.BaseGetSgInfo(self.sg, self.entity_id, self.entity_type).get_asset_level()

        self._task_name = TaskData.task_name
        self._task_id = TaskData.task_id
        self._down = down
        self._up = up

    def export_rig_fbx(self):
        u"""
        导出rig fbx
        @return:
        """
        if self._asset_type in ['body', 'cartoon_body'] and self._entity_name.endswith('_Attach'):
            return
        try:
            maya_plugin.plugin_load(['fbxmaya'])
        except:
            pass
        __result = True
        if self._entity_name in EXASSETS:
            __result = False

        if __result:
            _fbx_dict = self._get_fbx_info()

            # 导出fbx
            _fbxfiles = self._export_final_fbx(_fbx_dict)
            # 导出fbx
            _mbfbxfiles = []

            # 导出mb fbx(非hik)
            _parrnt_assets = self._get_parent_assets()
            if self._asset_type.lower() in ['rolaccesory']:
                _mbfbxfiles = self._copy_mb_fbxs(_fbxfiles)
            _up_data = {}
            if _fbxfiles:
                if self._asset_type and self._asset_type.lower() in ['item', 'enemy', 'weapon']:
                    _fbx_dict = self.package_work_publish(_fbxfiles, _key='mbfbx')
                    if _fbx_dict:
                        _up_data.update(_fbx_dict)
                else:
                    _fbx_dict = self.package_work_publish(_fbxfiles, _key='fbx')
                    if _fbx_dict:
                        _up_data.update(_fbx_dict)
            if _mbfbxfiles and self._asset_type.lower() in ['rolaccesory', 'hair']:
                _mb_fbx_dict = self.package_work_publish(_mbfbxfiles, _key='mbfbx', add_path='mobu')
                if _mb_fbx_dict:
                    _up_data.update(_mb_fbx_dict)
            if _fbxfiles and self._asset_type and self._asset_type.lower() in ['npc']:
                _fbx_dict = self.package_work_publish(_fbxfiles, _key='mbfbx')
                if _fbx_dict:
                    _up_data.update(_fbx_dict)

            return _up_data
        else:
            return

    def export_rig_fbx_by_grp_list(self, grp_list=all):
        if grp_list in [all, 'all']:
            return self.export_rig_fbx()
        else:
            return self._export_rig_fbx_by_grp_list(grp_list)

    def _export_rig_fbx_by_grp_list(self, grp_list):
        u"""
        导出rig fbx
        @return:
        """
        # log_handle.info('grp_list:{}'.format(grp_list))
        if self._asset_type in ['body', 'cartoon_body'] and self._entity_name.endswith('_Attach'):
            return
        try:
            maya_plugin.plugin_load(['fbxmaya'])
        except:
            pass
        __result = True
        if self._entity_name in EXASSETS:
            __result = False

        if __result:
            _fbx_dict = self._get_fbx_info_by_grp_list(grp_list)
            # log_handle.info('_fbx_dict:{}'.format(_fbx_dict))
            if not _fbx_dict:
                return

            _fbxfiles = self._export_final_fbx(_fbx_dict)
            # 导出fbx
            _mbfbxfiles = []

            _parrnt_assets = self._get_parent_assets()
            if self._asset_type.lower() in ['rolaccesory', 'hair']:
                _mbfbxfiles = self._copy_mb_fbxs(_fbxfiles)
            _up_data = {}
            if _fbxfiles:
                if self._asset_type and self._asset_type.lower() in ['item', 'enemy', 'weapon']:
                    _fbx_dict = self.package_work_publish(_fbxfiles, _key='mbfbx')
                    if _fbx_dict:
                        _up_data.update(_fbx_dict)
                else:
                    _fbx_dict = self.package_work_publish(_fbxfiles, _key='fbx')
                    if _fbx_dict:
                        _up_data.update(_fbx_dict)
            if _mbfbxfiles and self._asset_type.lower() in ['rolaccesory', 'hair']:
                _mb_fbx_dict = self.package_work_publish(_mbfbxfiles, _key='mbfbx', add_path='mobu')
                if _mb_fbx_dict:
                    _up_data.update(_mb_fbx_dict)
            if _fbxfiles and self._asset_type and self._asset_type.lower() in ['npc']:
                _fbx_dict = self.package_work_publish(_fbxfiles, _key='mbfbx')
                if _fbx_dict:
                    _up_data.update(_fbx_dict)

            return _up_data
        else:
            return

    def _get_fbx_info_by_grp_list(self, grp_list):
        # log_handle.info('_get_fbx_info_by_grp_list:{}'.format(grp_list))
        grp_list = self._cover_grp_list(grp_list)
        # log_handle.info('cover_grp_list:{}'.format(grp_list))
        _dict = {}
        _objs_fbx_dict = self._get_objs_fbxfile()
        # log_handle.info('_objs_fbx_dict:{}'.format(_objs_fbx_dict))
        _work_dir = self._get_local_dir()
        _objs_fbx_dict_new = {}
        for k, v in _objs_fbx_dict.items():
            if k == 'mods':
                if not grp_list:
                    _objs_fbx_dict_new['mods'] = {}
                if v and grp_list:
                    __mod_info_new = {}

                    for work_file, grp_infos in v.items():
                        if not work_file:
                            continue
                        _obj_list = []
                        if not grp_infos:
                            continue
                        _objs, _triangulate = grp_infos
                        _obj_news = []
                        if not _objs:
                            continue
                        for _obj in _objs:
                            _obj_new = cmds.ls(_obj, l=1)[0].split('|')[-1] if cmds.ls(_obj, l=1) else None
                            if _obj_new:
                                _obj_news.append(_obj_new)

                        _objs = [obj for obj in _obj_news if obj in grp_list]
                        if _objs:
                            _obj_list.extend([_objs, _triangulate])
                        if _obj_list:
                            __mod_info_new[work_file] = _obj_list
                    if __mod_info_new:
                        _objs_fbx_dict_new['mods'] = __mod_info_new
                else:
                    _objs_fbx_dict_new['mods'] = {}
            else:
                _objs_fbx_dict_new[k] = v
        for k, v in _objs_fbx_dict_new.items():
            if k and v:
                if k == 'joins':
                    #
                    _key = False
                else:
                    _key = True
                _dict[_key] = v
        return _dict

    def _cover_grp_list(self, grp_list):
        __gpr_list = []
        if not grp_list:
            return __gpr_list
        for __grp in grp_list:
            if __grp and cmds.ls(__grp, type='transform'):
                __grp = cmds.ls(__grp, type='transform')[0]
                __gpr_list.append(__grp)
        return __gpr_list

    def _get_parent_assets(self):
        import database.shotgun.core.sg_analysis as sg_analysis
        sg = sg_analysis.Config().login()
        parent_assets = sg.find_one('Asset', [['id', 'is', self.entity_id]], ['parents'])
        if parent_assets and 'parents' in parent_assets:
            return parent_assets['parents']

    def _copy_mb_fbxs(self, _fbxfiles):
        mb_fbx_files = []
        for _fbxfile in _fbxfiles:
            if _fbxfile and os.path.exists(_fbxfile):
                _dir, _base_name = os.path.split(_fbxfile)
                _fbx_dir = '{}/mobu'.format(_dir)
                if not os.path.exists(_fbx_dir):
                    os.makedirs(_fbx_dir)
                _mb_fbx = '{}/{}'.format(_fbx_dir, _base_name)
                if os.path.exists(_mb_fbx):
                    os.remove(_mb_fbx)
                try:
                    shutil.copy(_fbxfile, _mb_fbx)
                    mb_fbx_files.append(_mb_fbx)
                except:
                    pass
        return mb_fbx_files

    def _assign_shader(self, _sg, _meshs):
        u"""
        文件中所有mesh 物体赋lambert 材质球
        :return:
        """
        if _meshs and _sg:
            try:
                cmds.sets(_meshs, e=1, forceElement=_sg)
            except:
                for _mesh in _meshs:
                    try:
                        cmds.sets(_mesh, e=1, forceElement=_sg)
                    except:
                        pass

    def _get_all_meshs(self):
        u"""
        获得文件中所有polygon物体
        :return:
        """
        _trs = []
        _meshs = cmds.ls(type='mesh', l=1)
        if _meshs:
            for _mesh in _meshs:
                tr = cmds.listRelatives(_mesh, typ='transform', p=1)
                _trs.extend(tr)
        return _trs

    def _disconnet_joins(self, objs=['Roots']):
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

    def _create_shader(self, name='lambert_combine', type='lambert'):
        u"""
        创建材质球
        :param type:
        :return:
        """
        try:
            sg = '{}SG'.format(name)
            if cmds.ls(name, type='lambert'):
                cmds.delete(name)
            if cmds.ls(sg, type='shadingEngine'):
                cmds.delete(sg)

            shader = cmds.shadingNode(type, asShader=True, n=name)

            # sg =cmds.createNode('shadingEngine', name=sg)

            sg = cmds.sets(renderable=1, noSurfaceShader=1, em=1, n=sg)

            cmds.connectAttr(('%s.outColor' % shader), ('%s.surfaceShader' % sg))
            return sg
        except:
            return

    def get_fbx_objs(self):
        _dict = self._get_fbx_info()
        _list = []
        if _dict:
            for k, v in _dict.items():
                if k != True:
                    continue
                if k and v:
                    for _fbx_file, _result in v.items():
                        _objs, _triangulate = _result
                        _list.extend(_objs)
        return _list

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

    def get_export_mod_objs_info(self):
        _mod_objs = []
        __dict = self._get_objs_fbxfile()
        mod_dict = __dict['mods'] if __dict and 'mods' in __dict else None
        if not mod_dict:
            return

        mods = mod_dict.values()
        if not mods:
            return
        for mod in mods:
            _objs, _triangulate = mod
            _mod_objs.extend(_objs)
        return _mod_objs

    def clear_body_joins(self):
        u"""
        删除 AP
        Returns:

        """
        _clear_joins = cmds.ls(CLEARJIONS, type='joint')
        if _clear_joins:
            self._delete_objs(_clear_joins)

    def _get_local_dir(self):
        u"""
        获得本地工作目录
        :return:
        """
        import method.common.dir as _dir
        return _dir.set_localtemppath(sub_dir='temp_info/fbx_export')

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
        _ad = self._get_rig_ad()
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

    def _cover_FX_fbx(self, _fbx_file):
        _dict = {}
        if '_FX_' in _fbx_file:
            grps = self._get_groups_by_key('*_FX_*')
            if grps:
                for grp in grps:
                    grp_short = grp.split('|')[-1]
                    _fbx_fil_new = '{}'.format(grp_short)
                    _dict[grp_short] = _fbx_fil_new
        return _dict

    def _get_groups_by_key(self, key='*_FX_*'):
        grps = []

        objs = cmds.ls(key, l=1, type='transform')
        if objs:
            for obj in objs:
                if not cmds.listRelatives(obj, s=1):
                    grps.append(obj)
        if grps:
            grps = list(set(grps))
        return grps

    def _get_joins(self, join):
        u"""
        获取join 下所有骨骼
        :param join:
        :return:
        """
        _joins = [join]
        if join and cmds.ls(join):
            _children = cmds.listRelatives(join, ad=1, type='joint')
            if _children:
                _joins = _joins + _children
        return _joins

    def _bake_joins(self, _objs, startframe, endframe):
        u"""

        :param _objs:
        :return:
        """
        import lib.maya.process.maya_bake as maya_bake
        reload(maya_bake)
        return maya_bake.bake(_objs, startframe=startframe, endframe=endframe, shape=0)

    def _export_animation_fbx(self, objlist, export_path, dis, usescenename):
        return _fbx_ani_common.export_animation_fbx(objlist, export_path, dis=dis, hi=0, startframe=0, endframe=30,
                                                    bake=1,
                                                    bakestart=0, bakeend=30,
                                                    animationonly=0, UpAxis='y', warning=0, instances=0, log=0,
                                                    constrains=0, shape=0, usescenename=usescenename)

    def _export_rig_fbx(self, _exportobjs, _exportfile, _dismesh=True, _triangulate=0):
        u"""
        导出fbx
        @param _exportobjs: 需要导出fbx的物体列表
        @param _exportfile: 导出的fbx文件
        @param _dismesh: 为True时，断开_exportobjs组下所有模型连接
        @return:
        """
        result = False
        # 显示组及组以下模型组
        if '_Render' not in _exportfile:
            self.__dispaly_grps_objs(_exportobjs)

        # 清理Group 组
        if self._asset_type not in ['item']:
            self._disconnet_joins(objs=['Roots'])
        else:
            self._disconnet_joins(objs=['Root_M'])
        # body joins 删除 CB AP 前缀骨骼

        if self._asset_type and self._asset_type.lower() in ['body', 'cartoon_body'] and _dismesh == False:
            self.clear_body_joins()

        # body 添加去睫毛版本fbx
        if '_Render' in _exportfile:
            if self._task_name in TASKS:
                _exportobjs = [_exportobj.split('_{Eyelashes}')[0] for _exportobj in _exportobjs if _exportobj]
                # 删除睫毛
                if _exportobjs:
                    self._delete_eyelashes()
            else:
                _exportobjs = []

        # 断开组下所有模型连接
        if _dismesh == True:
            self._disconnet_mesh_grps(_exportobjs)

        if _dismesh == True:
            if self._task_name in ['drama_rig', 'rbf'] and \
                    os.path.splitext(os.path.basename(_exportfile))[0].split('_')[-1] not in [
                'asis'] and self._asset_type.lower() not in ['item']:
                _sg = self._create_shader(name='lambert_combine', type='lambert')
                _meshs = self._sect_grps_mes_trs(_exportobjs)
                self._assign_shader(_sg, _meshs)

        # bake保底动画
        # if "_GuaranteedAnim" in _exportfile:
        #     _joins = self._get_joins("Root_M")
        #     self._bake_joins(_joins, 0, 30)

        # 清理grp组
        # self.clear_group(['Group'])
        # 添加模型

        if _dismesh == True and self._asset_type.lower() not in ['npc', 'enemy']:

            _meshs = self._sect_grps_mes_trs(_exportobjs)
            if _meshs:
                _exportobjs = _meshs
            else:
                _exportobjs = []

            # # 处理后再打开文件保证安全
            # self._open_file(self._file)

        # 导出fbx
        if self._asset_type.lower() in ['npc'] and self._asset_level == 3:

            rig_grp = cmds.ls('*_Rig', type='transform', l=1)
            if rig_grp:
                rig_grp = rig_grp[0].split('|')[-1]
                if rig_grp != '{}_Rig'.format(self._entity_name):
                    cmds.rename(rig_grp, '{}_Rig'.format(self._entity_name))
            _exportobjs = cmds.ls('Roots', type='joint')
            for _grp in ['BaseHead', 'BaseBody', 'BaseHair']:
                __obj = cmds.ls('{}_{}'.format(self._entity_name, _grp), l=1)
                if __obj:
                    _exportobjs.append(__obj[0])

        if "_GuaranteedAnim" in _exportfile:
            # 保存下文件
            _file = _exportfile.replace(".fbx", ".ma")
            filecommon.BaseFile().save_file(_file)

            _joins = self._get_joins("Root_M")
            # self._disconnet_joins(objs=_joins)
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
            if _exportobjs and self._asset_type.lower() not in ['npc', 'enemy']:
                result = self._export_fbx_base(_exportobjs, _exportfile, _triangulate=_triangulate, _dismesh=_dismesh)
            if _exportobjs and self._asset_type.lower() in ['npc', 'enemy']:
                result = self._export_fbx_base(_exportobjs, _exportfile, _triangulate=_triangulate, _dismesh=False)
        base_file = os.path.basename(_exportfile)
        if self._asset_type.lower() in ['cartoon_body'] and self._entity_name.lower().startswith(
                'q') and base_file.endswith('F_LD.fbx'):
            time.sleep(5)
            if result and result != False and os.path.exists(_exportfile):
                print(u'start process {}'.format(_exportfile))
                self.__process_q_body_lod_fbx(_exportfile)
            time.sleep(3)
        if self._asset_type.lower() in ['role', 'hair'] and "_GuaranteedAnim" not in _exportfile and \
                os.path.splitext(os.path.basename(_exportfile))[0].split('_')[-1] not in ['asis']:
            judge_is_online = judge_online_version_entity.judge_is_online_entity(self.sg, self._task_id)
            if not judge_is_online:
                time.sleep(5)
                result = self._process_tangent_fbx(_exportfile)
        if result and result != False:
            return True

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

    def _delete_eyelashes(self):
        u"""
        删除睫毛
        :return:
        """
        try:
            _eyelashes = self._delete_objs(cmds.ls(EYELASHES))
        except:
            pass

    def _export_fbx_base(self, _exportobjs, _exportfile, _triangulate, _dismesh=True):
        u"""

        :param _exportobjs:
        :param _exportfile:
        :param _dismesh:
        :return:
        """
        if _exportobjs and _exportfile:
            try:
                if _dismesh == True:
                    _fbx_common.export_fbx(_exportobjs, _exportfile, hi=1, triangulate=_triangulate, warning=0)
                else:
                    _fbx_common.export_fbx(_exportobjs, _exportfile, hi=0, triangulate=_triangulate, warning=0)
                return {_exportfile: _exportobjs}
            except:
                return

    def _select_grps_meshs(self, _grps):
        u"""
        从gprs 列表，获得所有mesh tr 节点
        @param _grps:
        @return:
        """
        _meshs = []
        if _grps:
            for _grp in _grps:
                _mshs = self.select_grp_meshs(_grp)
                if _mshs:
                    _meshs.extend(_mshs)
        return _meshs

    def _sect_grps_mes_trs(self, _grps):
        u"""
        从大组列表获得mesh tr 列表
        :param _grps:
        :return:
        """
        trs = []
        _meshs = self._select_grps_meshs(_grps)
        if _meshs:
            for _mesh in _meshs:
                tr = cmds.listRelatives(_mesh, p=1, type='transform', f=1)
                if tr:
                    trs.extend(tr)
        if trs:
            return list(set(trs))

    def _disconnet_mesh_grps(self, _grps):
        u"""
        断开组下所有模型连接
        """
        _meshs = self._sect_grps_mes_trs(_grps)
        cmds.select(_meshs)
        try:
            bs_break.mainFunc()
        except:
            pass

    def check_export_fbx(self):
        if self._asset_type in ['body', 'cartoon_body'] and self._entity_name.endswith('_Attach'):
            return
        try:
            maya_plugin.plugin_load(['fbxmaya'])
        except:
            pass

        # 导出maya 文件
        # _file_dict = self._export_files()
        _fbx_dict = self._get_fbx_info()
        if not _fbx_dict:
            return
        # 导出fbx
        _fbxfiles = self.__check_export_fbx(_fbx_dict)
        if not _fbxfiles:
            return
        return _fbxfiles

    def __check_export_fbx(self, _dict):
        _list = []
        if _dict:
            for k, v in _dict.items():
                if v:
                    for _fbx_file, _result in v.items():
                        _objs, _triangulate = _result
                        if os.path.splitext(os.path.basename(_fbx_file))[0].split('_')[-1] not in [
                            'asis'] and "_Render" not in _fbx_file:
                            try:
                                _result = self._export_rig_fbx(_objs, _fbx_file, _dismesh=k, _triangulate=_triangulate)

                                if _result and _result == True:
                                    _list.extend([_fbx_file])

                            except:
                                pass
        return _list

    def _export_final_fbx(self, _dict):
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
                            if os.path.splitext(os.path.basename(_fbx_file))[0].split('_')[-1] in ['asis']:
                                self._open_file(self._file)
                            _result = self._export_rig_fbx(_objs, _fbx_file, _dismesh=k, _triangulate=_triangulate)

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

        # if _dict:
        #     for k, v in _dict.items():
        #         try:
        #             self._open_file(k)
        #             if v[-1] == [u'Roots']:
        #                 _fbx_common.export_fbx(v[0], v[1], hi=0, warning=0)
        #             else:
        #                 _fbx_common.export_fbx(v[0], v[1], hi=0, warning=0)
        #             _list.extend([v[-1]])
        #         except:
        #             pass
        # return _list

    def _open_file(self, _file):
        u"""
        打开maya文件
        :param _file:
        :return:
        """
        return filecommon.BaseFile().open_file(_file)

    def _fix_rig_fbx(self, _dict):
        u"""
        修复rig
        :param _dict: 例{fbx_file01:objs01,fbx_file02:objs02……}
        :return:
        """
        if _dict:
            for k, v in _dict.items():
                try:
                    self._open_fbx(k)
                    _fbx_common.export_fbx(v, k, hi=1, warning=0)
                except:
                    pass

    def _process_tangent_fbx(self, fbx_file):
        u"""
        处理tangent
        :param fbx_file:
        :return:
        """
        from method.common.process_fbx_tangent_gen import run_fbx_tangent_gen

        ok, result = run_fbx_tangent_gen(fbx_file, fbx_file)
        if not ok:
            raise RuntimeError('Process fbx tangent failed: {}'.format(result))
        return True


if __name__ == '__main__':
    import sys

    sys.path.append('Z:/dev/Ide/Python/2.7.11/Lib/site-packages')
    import method.shotgun.get_task as get_task

    _filename = cmds.file(q=1, exn=1)

    taskdata = get_task.TaskInfo(_filename, 'X3', 'maya', 'version')
    # _fbx_info = analyze_fbx.AnalyFbx(taskdata).get_fbx()
    # print _fbx_info
    _handle = Porcess_RigFbx_Export(taskdata)
    _handle.export_rig_fbx()

    # _dict = _handle._get_fbx_info()
    # # _handle.export_rig_fbx()
    # print _handle.get_export_objs_info()
    #
    # _exportobjs = [u'PL082C_Card_EA_HD']
    # _handle._disconnet_mesh_grps(_exportobjs)
    #
    # _meshs = _handle._sect_grps_mes_trs(_exportobjs)
    #
    # objlist = ['PL082C_Card_HD']
    # _triangulate = 1
    # _dismesh = True
    # _exportfile = 'M:/projects/X3/work/assets/role/PL082C_Card/rbf/maya/data/fbx/PL082C_Card_HD.fbx'
    #
    # _handle._export_rig_fbx(objlist, _exportfile, _dismesh, _triangulate)
    #
    # objlist=[u'YS004S_Card_HD']
    # _triangulate = 1
    # _dismesh = True
    # _exportfile = 'M:/projects/X3/work/assets/role/YS004S_Card/rbf/maya/data/fbx/YS004S_Card_HD.fbx'
    #
    # _data=_handle._export_rig_fbx(objlist, _exportfile, _dismesh, _triangulate)
#     objlist= _handle._get_objs_fbxfile()
#     _joins = _handle._get_joins("Root_M")
#     export_path='E:/gitlab/NPC_M02_GuaranteedAnim_test.fbx'
#     _handle._export_animation_fbx(objlist, export_path)
#     cmds.select(_handle._get_joins("Root_M"))
# print(_handle.export_rig_fbx())

# _objs_fbx_dict = _handle._get_objs_fbxfile()
# print(_objs_fbx_dict)
#     # _handle._get_objs_fbxfile()
#     # _ad = _handle._get_rig_ad()
#     # # 转换{ad}变量
#     # _fbx_info = _handle._cover_variable_info('{ad}', _ad, _fbx_info)
#     # print(_fbx_info)
#     # _dict = _handle.export_rig_fbx()
#     # print(_handle._get_fbx_info())
#     _joins = _handle._get_joins("Root_M")
#     _handle._bake_joins(_joins, 0, 30)
