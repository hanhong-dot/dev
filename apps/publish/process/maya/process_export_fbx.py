# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       : process_export_fbx
# Describe   : 导出fbx处理
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2022/6/16__16:28
# -------------------------------------------------------
import os
import lib.maya.process.export_fbx as _fbx_common

reload(_fbx_common)

import lib.maya.node.object as _object

import apps.publish.process.process_package as process_package

reload(process_package)
import maya.cmds as cmds
import lib.maya.node.nodes as nodes_commond

import maya.mel as mel

import lib.maya.node.join as joincommon

import lib.maya.node.grop as group_common

import method.maya.common.file as filecommon

import method.maya.common.reference as refcommon

BODYGRPS = ['BaseHead', 'BaseBody', 'BaseHair']

CLEARJIONS = ['DB_*', 'AP_*']

import apps.publish.process.filehandle as filehandle
import lib.maya.analysis.analyze_fbx as analyze_fbx

reload(analyze_fbx)
import lib.common.jsonio as jsonio


class Porcess_Export(object):
    u"""
    导出相关内容处理
    """

    def __init__(self, TaskData, down=True, up=False):
        self.taskdata = TaskData
        self._work_data_dir = TaskData.work_data_dir
        self._publish_data_dir = TaskData.publish_data_dir
        self._entity_name = TaskData.entity_name
        self._des_name = filehandle.remove_version(TaskData.des_name)
        self._task_name = TaskData.task_name
        self._step = TaskData.step_name
        self.suffix = os.path.splitext(self._des_name)[-1]
        self._fbx_file = self._des_name.replace(self.suffix, '.fbx')
        self._work_fbx_dir = '{}/fbx'.format(self._work_data_dir)
        self._publish_fbx_dir = '{}/fbx'.format(self._publish_data_dir)
        self._asset_type = TaskData.asset_type
        self._down = down
        self._up = up
        self._fbx_json = '{}.{}.json'.format(self._entity_name, self._task_name)

    @property
    def root_group(self):
        u"""
        获取最外层大组
        Returns:

        """

        return group_common.BaseGroup().get_root_groups()

    def export_fbx(self):
        u"""
        导出fbx并打包
        """
        _work_fbx_file = self._fbx_export()
        if _work_fbx_file and _work_fbx_file != False and os.path.exists(_work_fbx_file):
            _dict = process_package.datapack_dict({_work_fbx_file:
                                                       '{}/{}'.format(self._publish_fbx_dir, self._fbx_file)},
                                                  down=self._down, up=self._up)
            if _dict:
                return {'fbx': _dict}

    # def export_rig_fbx(self):
    #     u"""
    #     绑定文件导出fbx
    #     Returns:
    #
    #     """
    #     if self._asset_type == 'body':
    #         return self.export_rig_body_fbx()
    #     elif self._asset_type == 'role':
    #         return self.export_role_rig_fbx()
    #     elif self._asset_type == 'npc':
    #         return self.export_rig_npc_fbx()
    #     else:
    #         return self.export_rig_fbx_other()

    def export_rig_fbx_other(self):
        u"""
        绑定文件导出fbx(item,rolaccesory,weapon,enemy,hair)
        """
        _fbx_info = analyze_fbx.AnalyFbx(self.taskdata).get_fbx()
        if _fbx_info:
            return self.export_rig_fbx_byinfo(_fbx_info)

    def export_rig_fbx_byinfo(self, _fbxinfo):
        u"""
        根据fbx info 导出fbx
        """
        _fbx_objs_files = {}
        if _fbxinfo:
            for i in range(len(_fbxinfo)):
                _fbx_file = _fbxinfo[i]['fbx_file']
                _fbx_objs = _fbxinfo[i]["fbx_objs"]
                _work_fbx_file = self.export_rig_fbx_objs(_fbx_file, _fbx_objs)
            if _work_fbx_file and _work_fbx_file not in _fbx_objs_files:
                _fbx_objs_files[_work_fbx_file] = _fbx_objs
        # 修复fbx
        if _fbx_objs_files:
            for k, v in _fbx_objs_files.items():
                self.fix_fbxfile(objlist=v, fbxfile=k)
                # 打包上传字典
        if _fbx_objs_files and _fbx_objs_files.keys():
            return self.package_work_publish(_fbx_objs_files.keys())

    def export_rig_fbx_objs(self, fbxfile, fbxobjs):
        u"""
        导出rig fbx
        """
        if not fbxfile or fbxobjs:
            return
        _export_objs = self._get_export_objs(fbxobjs)
        _fbxfile = '{}.fbx'.format(fbxfile)
        if _export_objs:
            _work_fbxfile = '{}/{}'.format(self._work_fbx_dir, _fbxfile)
            _fbx_work_file = _fbx_common.export_fbx(_export_objs, _work_fbxfile, hi=1)
            return _fbx_work_file

    def _get_export_objs(self, objs):
        u"""
        导出胡objs
        """
        _exoprt_objs = []
        for i in range(len(objs)):
            objs = cmds.ls(objs[i])
            if objs:
                _exoprt_objs.extend(objs)
        return _exoprt_objs

    def export_mod_fbx(self):
        u"""
        导出模型fbx并打包
        Returns:

        """
        # body 分别输出三个组的fbx(_BaseHead,_BaseHair,_BaseBody)

        # 其他类型均选择最外层大组输出
        _fbx_info = analyze_fbx.AnalyFbx(self.taskdata).get_fbx()
        _fbx_dict = self.get_export_mod_file(_fbx_info)
        # 导出fbx
        _work_fbx_files = self.export_work_fbx(_fbx_dict)
        # 打包上传字典
        if self._asset_type and self._asset_type not in ['item']:
            return self.package_work_publish(_work_fbx_files)
        # item fbx 为MBFBX
        else:
            return self.package_work_publish(_work_fbx_files, _key='mbfbx')

    def package_work_publish(self, workfiles, _jsonfile=None, _key='fbx',add_path=''):
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
        if _jsonfile == None:
            _json_file = self._fbx_json
        else:
            _json_file = _jsonfile
        if workfiles:
            for fil in workfiles:
                if add_path:
                    _publish_file = '{}/{}/{}'.format(self._publish_fbx_dir, add_path,os.path.basename(fil))

                else:
                    _publish_file = '{}/{}'.format(self._publish_fbx_dir, os.path.basename(fil))
                if fil and os.path.exists(fil):
                    _dict[fil] = _publish_file
        if _dict:
            _package_dict = process_package.datapack_dict(_dict, down=self._down, up=self._up)
            _fbx_dict = {_key: _package_dict}
            # 写入json
            _json_dict = self._jsonfile_write({'export_json': _dict}, _json_file)

        # 打包上传字典
        if _json_dict:
            _updata_dict.update(_json_dict)
        if _fbx_dict:
            _updata_dict.update(_fbx_dict)
        return _updata_dict

    def _jsonfile_write(self, _info, _jsonfile):
        u"""
        写入json文件,并返回json打包字典
        :param _info:
        :return:
        """
        _json_dict = {}
        _json_file = u'{}/{}'.format(self._work_fbx_dir, _jsonfile)
        _publish_json = u'{}/{}'.format(self._publish_fbx_dir, _jsonfile)
        try:
            jsonio.write(_info, _json_file)
            _json_dict = {_json_file: _publish_json}
        except:
            pass
        if _json_dict:
            _package_dict = process_package.datapack_dict(_json_dict, down=self._down, up=self._up)
            return {'export_fbx_json': _package_dict}

    def export_work_fbx(self, _dict, hi=0):
        u"""
        导出fbx在work路径
        Args:
            _dict: {fbx01:objs01,fbx02:objs02…………}

        Returns:

        """
        _workfiles = []
        if _dict:
            for k, v in _dict.items():
                _fbx_work_file = '{}/{}'.format(self._work_fbx_dir, k)
                _fbxfile = _fbx_common.export_fbx(v, _fbx_work_file, hi=hi)
                _workfiles.append(_fbxfile)
        return _workfiles

    def get_export_mod_file(self, _fbx_info):
        u"""
        获取物体与输出fbx文件名对应
        Args:
            _fbx_info:

        Returns:

        """
        _dict = {}

        if self._asset_type:
            if self._asset_type not in ['npc']:
                _objs = self.select_info_root(_fbx_info)
                for _obj in _objs:
                    _dict['{}.fbx'.format(_obj.split('|')[-1])] = [_obj]
            else:
                _objs = self.root_group
                _fbx = '{}.fbx'.format(_fbx_info[0])
                _dict[_fbx] = _objs
        return _dict

    def select_info_root(self, info):
        u"""
        获取 最外层大组
        Args:
            info:信息

        Returns:

        """
        _grps = []
        _root = self.root_group
        for i in range(len(info)):

            grps = cmds.ls(info[i], l=1)
            if grps:
                for grp in grps:
                    if grp and grp in _root and grp not in _grps:
                        _grps.append(grp)
        return _grps

    def export_rig_body_fbx(self):
        u"""
        body的rig导出fbx
        Returns:

        """
        _dict = {}
        # 导出模型fbx
        _modfbx_dict = self._export_body_mod_fbx()
        # 导出骨骼 fbx
        _joins_dict = self.export_body_joins_fbx()

        # fbx 修正
        self.fix_body_fbx()

        # 打包上传字典
        if _modfbx_dict:
            _dict.update(_modfbx_dict)
        if _joins_dict:
            _dict.update(_joins_dict)

        _dict_package = process_package.datapack_dict(_dict, down=self._down, up=self._up)
        if _dict_package:
            return {'fbx': _dict_package}

    def export_rig_npc_fbx(self):
        u"""
        npc rig 导出fbx
        Returns:

        """
        #
        _fbx_info = analyze_fbx.AnalyFbx(self.taskdata).get_fbx()

        _rig_grp = self.get_rig_Grp
        if not _rig_grp:
            return
        # rig 组下所有mesh打断bs
        _meshs = self.select_grp_meshs(_rig_grp)
        # 断开模型连接
        self._disconnect_mesh(_meshs)
        # 导出fbx
        _fbx_file = '{}.fbx'.format(_fbx_info[0]['fbx_file'])
        _export_fbx_work = '{}/{}'.format(self._work_fbx_dir, _fbx_file)
        _fbx_common.export_fbx(_rig_grp, _export_fbx_work, hi=1)
        # 修正fbx
        self.fix_fbxfile(_rig_grp, _export_fbx_work)
        # 打包上传字典
        _publish_fbx = '{}/{}'.format(self._publish_fbx_dir, self._fbx_file)

        _dict_package = process_package.datapack_dict({_export_fbx_work: _publish_fbx}, down=self._down, up=self._up)

        #
        if _dict_package:
            return {'fbx': _dict_package}

    @property
    def get_rig_Grp(self):
        u"""
        获得rig 大组
        Returns:

        """
        _root_grp = self.root_group
        rig_grps = cmds.ls('*Rig*', l=1) + cmds.ls('*rig*', l=1)
        for rig_grp in rig_grps:
            if rig_grp in _root_grp:
                return rig_grp

    def fix_body_fbx(self):
        u"""
        修正mod  fbx
        Returns:

        """
        _fix_dict = {}
        _mod_dict = self._get_body_grps()
        _joint_dict = {'joins': self._get_joins_root()}

        if _mod_dict:
            _fix_dict.update(_mod_dict)
        if _joint_dict:
            _fix_dict.update(_joint_dict)
        # 修正
        self.fix_fbx(_fix_dict)

    def export_body_joins_fbx(self):
        u"""
        导出骨骼
        Returns:

        """
        # 清理 DB_ ,AP_ 前缀骨骼
        self.clear_body_joins()
        # 删除除Rig 大组以外大组
        # self.delet_body_othergrps()

        # 导出的骨骼最外大组
        _export_objs = self._get_joins_root()
        # 导出的fbx文件名
        _fbx_file = self._fix_insert_file('joins')
        #
        _export_fbx_work = '{}/{}'.format(self._work_fbx_dir, _fbx_file)
        # 导出fbx
        _fbx_common.export_fbx(_export_objs, _export_fbx_work, hi=1)
        #
        # 上传基础字典
        if _export_fbx_work and os.path.exists(_export_fbx_work):
            return {_export_fbx_work: '{}/{}'.format(self._publish_fbx_dir, _fbx_file)}

    def _selet_body_grps(self, grps):
        u"""
        除grps 其他最外层大组
        Args:
        grp:

        Returns:

        """
        _root_grps = self.root_group
        try:
            return list(set(_root_grps) - set(grps))
        except:
            return

    def delet_body_othergrps(self):
        u"""

        Returns:

        """
        _rig_grp = self._get_body_root()
        if _rig_grp:
            _otergrps = self._selet_body_grps([_rig_grp])
        if _otergrps:
            self._delete_objs(_otergrps)

    def _get_joins_root(self):
        u"""
        获得骨骼Roots
        Returns:

        """
        _root = cmds.ls('Roots')
        if _root:
            for i in range(len(_root)):
                if cmds.nodeType(_root[i]) == 'joint':
                    return _root[i]

    def export_role_rig_fbx(self):
        u"""
        导出rig fbx
        Returns:

        """
        # 导入参考
        refcommon.import_all_reference()

        _dict = {}
        # 删除非rig 组
        # self._delete_groups()
        # 导出HD FBX
        _hd_dict = self._export_hd_fbx('HD')
        # 导出LD FBX
        _ld_dict = self._export_hd_fbx('LD')
        # 修正fbx
        self._fix_fbx('HD')
        self._fix_fbx('LD')

        if _hd_dict and _hd_dict != False:
            _dict.update(_hd_dict)
        if _ld_dict and _ld_dict != False:
            _dict.update(_ld_dict)
        if _dict:
            _dict_package = process_package.datapack_dict(_dict, down=self._down, up=self._up)
            if _dict_package:
                return {'fbx': _dict_package}

    def _fbx_export(self):
        u"""
        导出fbx
        """

        _fbx_file = self._des_name.replace(self.suffix, '.fbx')
        _root_objs = _object.root_objs()
        _export_fbx_work = '{}/{}'.format(self._work_fbx_dir, self._fbx_file)
        if _root_objs:
            return _fbx_common.export_fbx(_root_objs, _export_fbx_work)

    def _export_body_mod_fbx(self):
        u"""
        body 导出
        Returns:

        """
        _grp_dict = self._get_body_grps()
        if _grp_dict:
            try:
                return self._export_mod_fbx(_grp_dict)
            except:
                return

    def _export_rig_mod_fbx(self, objs, fbxfile):
        u"""
        导出fbx 模型fbx
        """

    def _rig_fbx_export(self):
        u"""
        获得裸模需要导出的模型fbx(head,body,hair)
        Returns:

        """
        _mod_dict = {}
        _joins_dict = {}
        _grps = []
        _root_grp = self._get_body_root()
        _gprs = self._select_grp_grps(_root_grp)
        _grp_shorts = self._short_list
        _fbx_info = analyze_fbx.AnalyFbx(self.taskdata).get_fbx()
        _ad = self._get_rig_ad()
        _fbx_info = self._cover_variable_info('ad', _ad, _fbx_info)
        # if _fbx_info:
        #     for i in range(len(_fbx_info)):
        #         _objs=[]
        #         if _fbx_info[i]:
        #             _fbx_objs=_fbx_info[i]['fbx_objs']
        #             _fbx_file=_fbx_info[i]['fbx_file']
        #             if 'Roots' not in _fbx_objs:

        # rig 组下胡组

        # for _grp in _gprs:
        #     _short = _grp.split('|')[-1].split('_')[-1]
        #     for _gr in BODYGRPS:
        #         if _gr == _short:
        #             _dict[_gr.lower()] = _grp
        # return _dict

    def _get_body_grps(self):
        u"""
        获得裸模需要导出的模型fbx(head,body,hair)
        Returns:

        """
        _dict = {}
        _grps = []
        _root_grp = self.root_group
        _dict[_root_grp] = self._entity_name

        return _dict

    def _cover_variable_info(self, _var, _ad, _info):
        u"""
        转换info 中的{ad}变量
        """
        if _info:
            if isinstance(_info, str) or isinstance(_info, unicode):
                try:
                    return _info.replace(_var, _ad)
                except:
                    return _info
            else:
                try:
                    return eval(str(_info).replace(_var, _ad))
                except:
                    return _info

    def _select_grp_grps(self, grp):
        u"""
        获得组下所有组的列表(不遍历)
        Args:
            grp: 组

        Returns:组列表

        """
        _grps = []
        if grp and cmds.ls(grp):
            objs = cmds.listRelatives(grp, c=1, f=1)
            if objs:
                for obj in objs:
                    _shape = cmds.listRelatives(obj, s=1, f=1)
                    if not _shape and obj not in _grps:
                        _grps.extend([obj])
        return _grps

    def _short_list(self, _grps):
        u"""

        """
        _list = []
        if _grps:
            for i in range(len(_grps)):
                _short = _grps[i].split('|')[-1]
                if _short and _short not in _list:
                    _list.append(_short)
        return _list

    def clear_body_joins(self):
        u"""
        删除 AP
        Returns:

        """
        _clear_joins = cmds.ls(CLEARJIONS, type='joint')
        if _clear_joins:
            self._delete_objs(_clear_joins)

    def _get_rig_ad(self):
        u"""
        获取rig ad
        """
        _rig_grp = self._get_body_root()
        if _rig_grp:
            return _rig_grp.split('|')[-1].split('_Rig')[0]

    def _get_body_root(self):
        u"""
        获得裸模最外层大组(rig)
        Returns:

        """
        _roots = self.root_group
        if _roots:
            for grp in _roots:
                if '_Rig' in grp.split('|')[-1]:
                    return grp

    def _export_mod_fbx(self, grps={}):
        u"""
        导出模型组fbx
        Args:
            grps: {basename01:grp01,basename02:grp02……}

        Returns: {workfbx01:publishfbx01,workfbx02:publishfbx02……}

        """

        _updict = {}
        if not grps:
            return
        for k, v in grps.items():
            _meshs = self.select_grp_meshs(v)
            if _meshs:
                # 断开模型连接
                self._disconnect_mesh(_meshs)
                # 导出fbx路径及命名
                _fbx_file = self._fix_insert_file(k)
                _export_fbx_work = '{}/{}'.format(self._work_fbx_dir, _fbx_file)
                # 导出fbx
                _fbx_common.export_fbx(v, _export_fbx_work, hi=1)
                #
                # 上传基础字典
                if _export_fbx_work and os.path.exists(_export_fbx_work):
                    _updict[_export_fbx_work] = '{}/{}'.format(self._publish_fbx_dir, _fbx_file)
        return _updict

    def _select_grps_meshs(self, grps=[]):
        u"""
        获取组下所有模型g
        Args:
            grps:组

        Returns:{grp01:meshs01,grp02:meshs02……}f

        """
        try:
            return {grp: self.select_grp_meshs(grp) for grp in grps if (grp and cmds.ls(grp))}
        except:
            return

    def select_grp_meshs(self, grp=''):
        u"""
        获得组下所有模型mesh节点
        :param grp: 组
        :return:
        """
        try:
            return cmds.listRelatives(grp, type='mesh', ad=1, f=1)
        except:
            return

    def _export_hd_fbx(self, _k='HD'):
        u"""
        导出rig fbx
        Returns:

        """
        grp = ''
        if _k in ['HD', 'LD']:
            grp = '{}_{}'.format(self._entity_name, _k)
        if _k in ['Rig']:
            grp = cmds.ls('*_Rig')[0]
        # 组下所有模型
        if grp and cmds.ls(grp):
            meshs = cmds.listRelatives(grp, type='mesh', ad=1)
            # 断开模型连接
            self._disconnect_mesh(meshs)
            # 连接的骨骼
            _joins = joincommon.select_meshs_joins(meshs)

            # 需要导出的物体
            _export_objs = self._export_rig_objs(_k)
            _fbx_file = '{}_{}.fbx'.format(self._entity_nam, _k)
            _export_fbx_work = '{}/{}'.format(self._work_fbx_dir, _fbx_file)
            # 导出fbx
            _fbx_common.export_fbx(_export_objs, _export_fbx_work, hi=1)
            # 上传基础字典
            if _export_fbx_work and os.path.exists(_export_fbx_work):
                return {_export_fbx_work: '{}/{}'.format(self._publish_fbx_dir, _fbx_file)}

    def _export_rig_objs(self, _k='HD'):
        u"""
        需要导出的物体
        Args:
            _k:

        Returns:

        """

        if _k not in ['Rig']:
            grp = '{}_{}'.format(self._entity_name, _k)
        else:
            grp = cmds.ls('*_Rig')[0]
        return self._get_meshs([grp])

    def _get_meshs(self, _grps=[]):
        u"""
        组下mesh物体(tr节点)
        Args:
            _grps: 组列表

        Returns:

        """
        _objs = []
        if _grps:
            for _grp in _grps:
                if _grp and cmds.ls(_grp):
                    meshs = cmds.listRelatives(_grp, type='mesh', ad=1)
                    if meshs:
                        for _mesh in meshs:
                            tr = cmds.listRelatives(_mesh, typ='transform', p=1)
                            _objs.extend(tr)

        return list(set(_objs))

    def fix_fbxfile(self, objlist=[], fbxfile=''):
        u"""
        修正fbx文件
            fbxfile:

        Returns:

        """
        try:
            self._open_fbx(fbxfile)
            _fbx_common.export_fbx(objlist, fbxfile, hi=1)
        except:
            pass

    def fix_fbx(self, _dict={}):
        u"""
        修正fbx文件
        Args:
            _dict: {base01:exportobjs01,base02:exportobjs02……}

        Returns:

        """
        if _dict:
            for k, v in _dict.items():
                _fbx_file = self._fix_insert_file(k)
                _fbx_work = '{}/{}'.format(self._work_fbx_dir, _fbx_file)

                # 修正fbx
                self.fix_fbxfile(k, _fbx_work)

    def _fix_fbx(self, _k='HD'):
        u"""
        修正fbx
        Args:
            _k:

        Returns:

        """
        _fbx_file = '{}_{}.fbx'.format(self._entity, _k)
        _export_fbx_work = '{}/{}'.format(self._work_fbx_dir, _fbx_file)
        # 打开fbx
        if _export_fbx_work and os.path.exists(_export_fbx_work):
            self._open_fbx(_export_fbx_work)
            # 处理
            # self._process_fbx()
            # 导出
            _export_objs = self._export_rig_objs(_k)
            _fbx_common.export_fbx(_export_objs, _export_fbx_work, hi=1)

    def _open_fbx(self, fbxfile):
        u"""
        打开fbx文件
        Args:
            fbxfile:

        Returns:

        """
        try:
            mel.eval('FBXProperty Import|AdvOptGrp|UI|ShowWarningsManager -v 0')
            mel.eval('FBXProperty Import|AdvOptGrp|UI|GenerateLogData -v 0')
        except:
            pass
        try:
            cmds.file(fbxfile, o=1, f=1, options='fbx', ignoreVersion=1, type='FBX')
        except:
            pass

    def _process_fbx(self):
        u"""
        处理fbx
        Returns:

        """
        # 清理无用Skin
        mel.eval('removeAllUnusedSkinInfs()')

    def _delete_groups(self):
        u"""
        rig 文件,删除rig 以外的大组
        Returns:

        """
        _root_grps = self.root_group
        _rig_grp = cmds.ls('*_Rig', l=1)
        if not _root_grps or not _rig_grp:
            return
        _gropus = list(set(_root_grps) - set(_rig_grp))
        self._delete_objs(_gropus)

    def _delete_joins(self):
        u"""
        删除
        Returns:

        """

    def _delete_objs(self, objs):
        u"""
        删除节点
        Args:
            objs: 需要删除的节点列表

        Returns:

        """
        if not objs:
            return
        try:
            cmds.delete(objs)
        except:
            for _obj in objs:
                try:
                    cmds.lockNode(_obj, l=0)
                    cmds.delete(_obj)
                except:
                    pass

    def _fix_insert_file(self, _insert='HD'):
        U"""
        插入特色字符转换
        Args:
            _insert: 'HD','LD'

        Returns:

        """
        if _insert not in ['Rig']:
            return self._fbx_file.replace(self._task_name, '{}.{}'.format(self._task_name, _insert))
        else:
            return self._fbx_file

    def _disconnect_mesh(self, _meshs):
        u"""
        断开与模型bs的模型连接
        Args:
            _meshs:mesh 列表

        Returns:

        """
        if not _meshs:
            return
        _meshlist = self._get_bs_connect(_meshs)
        if _meshlist:
            # 断开所有连接
            self._disconnect_sources(_meshlist)

    def _disconnect_sources(self, meshs):
        u"""
        断开节点所有上游连接
        Args:
            meshs:

        Returns:

        """
        if not meshs:
            return
        for i in range(len(meshs)):
            self._disconnect_sorce_listconnect(meshs[i])
            if cmds.nodeType(meshs[i]) != 'transform':
                trs = cmds.listRelatives(meshs[i], p=1, type='transform')
                if trs:
                    self._disconnect_sorce_listconnect(trs[0])

    def _get_bs_connect(self, meshs):
        u"""
        获得meshs bs 连接的模型
        Args:
            meshs:模型列表

        Returns:bs 模型列表

        """
        _con_list = []
        if meshs:
            for _mesh in meshs:
                if _mesh and cmds.ls(_mesh):
                    _bss = cmds.listConnections(_mesh, s=1, type='blendShape')
                    if _bss:
                        for _bs in _bss:
                            _meshs = cmds.listConnections(_bs, s=1, type='mesh', sh=1)
                            for i in range(len(_meshs)):
                                if _meshs[i] != _mesh and _meshs[i] not in _con_list:
                                    _con_list.append(_meshs[i])
        return _con_list

    def _disconnect_sorce_listconnect(self, node, _ex=['initialShadingGroup'], _extype=['blendShape']):
        u"""
        断开连接
        Args:
            node:节点
            _ex:需要排除的节点
            _extype：需要排除
        Returns:上游节点列表

        """
        if node and cmds.ls(node):
            cons = cmds.listConnections(node, c=1, p=1, s=1)
            if cons:
                for i in range(0, len(cons), 2):
                    _targ_node = cons[i + 1].split('.')[0]
                    if _targ_node not in _ex and cmds.nodeType(_targ_node) not in _extype:
                        self._disconnect(cons[i + 1], cons[i])

    def _disconnect(self, _sr_node, _tar_nod):
        u"""
        断开连接
        Args:
            _sr_node: 源节点
            _tar_nod: 目标节点

        Returns:

        """
        try:
            cmds.disconnectAttr(_sr_node, _tar_nod)
            return True
        except:
            try:
                nodes_commond.BaseNodeProcess().unlock_node(_sr_node)
                nodes_commond.BaseNodeProcess().unlock_node(_tar_nod)
                cmds.disconnectAttr(_sr_node, _tar_nod)
                return True

            except:
                return False


if __name__ == '__main__':
    import method.shotgun.get_task as get_task

    # _filename = cmds.file(q=1, exn=1)
    _filename = 'ST_BODY.drama_rig.v003.ma'
    taskdata = get_task.TaskInfo(_filename, 'X3', 'maya', 'version')

    _handle = Porcess_Export(taskdata)

    _fbx_info = analyze_fbx.AnalyFbx(taskdata).get_fbx()
    _ad = _handle._get_rig_ad()
    print(_ad)
    print(_fbx_info)
    print(_handle._cover_variable_info('{ad}', _ad, _fbx_info))

    # print(_handle._get_body_grps())

# _meshs = cmds.ls(sl=1)

# _handle._disconnect_sources(_meshs)
# _handle.delet_body_othergrps()
# a=_handle._export_body_mod_fbx()
# _grp_dict = _handle._get_body_grps()


# print(_handle._export_mod_fbx(_grp_dict))
#
# print(a)

# print Porcess_Export(taskdata).export_fbx()
