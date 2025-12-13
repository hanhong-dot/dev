# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       : process_bs_export
# Describe   : 导出rig bs 描述json (引自萌牙sdr_export_bs，提供给引擎)
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2022/10/13__14:18
# -------------------------------------------------------
import lib.maya.analysis.analyze_fbx as analyze_fbx
import lib.common.jsonio as _jsonio
import re
from method.maya.adPose2.ADPose import ADPoses
from method.maya.adPose2 import sdr
from method.maya.adPose2 import twist
import lib.maya.node.bs as get_bs_info

reload(get_bs_info)
from method.maya import fk_data

reload(fk_data)
import pymel.core as pm
# from method.maya.adPose2 import bs
import apps.publish.process.process_package as process_package
import lib.maya.node.grop as group_common
import adPose2_FKSdk

reload(adPose2_FKSdk)

import adPose2_FKSdk.sdr_export_bs as sdr_export_bs

import os

ASSETYPES = ['cartoon_role']


class BaseTools(object):
    def __init__(self):
        super(BaseTools, self).__init__()

    def _get_twist_targets(object):
        u"""

        :return:
        """
        twist_targets = []
        axis = "X"
        for joint in pm.ls(type="joint"):
            if not joint.hasAttr("twist" + axis):
                continue
            joint_name = joint.name().split("|")[-1].split(":")[-1]
            target_re = r"^{joint_name}_twist{axis}_(plus|minus)[0-9]+$".format(**locals())
            twistPoses = []
            driverNode = joint
            for attr in joint.listAttr():
                target_name = attr.name().split(".")[-1]
                if re.match(target_re, target_name):
                    twist_targets.append(target_name)
        return twist_targets

    def twist_to_unity_data(self, bs_nodes):
        twistElements = []
        axis = "X"
        for joint in pm.ls(type="joint"):
            if not joint.hasAttr("twist" + axis):
                continue
            joint_name = joint.name().split("|")[-1].split(":")[-1]
            target_re = r"^{joint_name}_twist{axis}_(plus|minus)[0-9]+$".format(**locals())
            twistPoses = []
            driverNode = joint
            for attr in joint.listAttr():
                target_name = attr.name().split(".")[-1]
                if not re.match(target_re, target_name):
                    continue
                driverPose = twist.Twist(joint=joint).get_value_by_target(target_name)
                drivenPoses = []
                bsinfo = get_bs_info.search_bsinfo(target_name, bs_nodes)
                twistPoses.append(dict(
                    driverPose=driverPose,
                    drivenPoses=drivenPoses,
                    bsInfo=bsinfo,
                ))
            if len(twistPoses) == 0:
                continue
            bindPose = dict(bsInfo=u'bindPose', drivenPoses=[], driverPose=0.0)
            twistPoses.insert(0, bindPose)
            driverNode = self._node_name(joint)
            driverBasePose = self._matrix_to_unity_rotation(joint.getMatrix())
            twistElements.append(dict(
                driverNode=driverNode,
                driverBasePose=driverBasePose,
                axis=dict(x=1, y=0, z=0),
                twistPoses=twistPoses,
                drivenNodes=[],
            ))

        return twistElements

    def _node_name(self, joint):
        names = joint.fullPath().split("|")
        if names[0] == u"":
            names.pop(0)
        if names[0] != "Roots":
            names.pop(0)
        return "/".join(names)

    def _matrix_to_unity_rotation(self, matrix):
        matrix = self._maya_matrix_to_unity_matrix(matrix)
        trans = pm.datatypes.TransformationMatrix(matrix)
        rotate = trans.getRotation().asQuaternion()
        return dict(x=rotate.x, y=rotate.y, z=rotate.z, w=rotate.w)

    def _maya_matrix_to_unity_matrix(self, matrix):
        matrix.a01 *= -1
        matrix.a02 *= -1
        matrix.a10 *= -1
        matrix.a20 *= -1
        matrix.a30 *= -0.01
        matrix.a31 *= 0.01
        matrix.a32 *= 0.01
        return matrix


class PorcessBsExport(BaseTools):
    def __init__(self, TaskData, down=True, up=False):
        super(BaseTools, self).__init__()
        self.taskdata = TaskData
        self._work_data_dir = TaskData.work_data_dir
        self._publish_data_dir = TaskData.publish_data_dir
        self._entity_name = TaskData.entity_name

        self._work_bs_dir = '{}/bs'.format(self._work_data_dir)
        if not os.path.exists(self._work_bs_dir):
            os.makedirs(self._work_bs_dir)
        self._publish_bs_dir = '{}/bs'.format(self._publish_data_dir)
        self._asset_type = TaskData.asset_type
        self._down = down
        self._up = up

    def export_bs_json(self):
        u"""
        导出bs json
        :return:
        """
        if self._asset_type in ['body', 'cartoon_body'] and self._entity_name.endswith('_Attach'):
            return
        # 导出bs json 文件
        _work_files = self._export_bs_work()
        if not _work_files:
            print('no export bs json file')

        # 打包上传字典
        return self._package_work_publish(_work_files)

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

    def _export_bs_work(self):
        u"""
        导出bs json文件
        :return:
        """
        import maya.cmds as cmds
        _work_files = []
        _objs_file_dict = self._get_objs_file_dict()
        print(_objs_file_dict)
        if _objs_file_dict:
            for k, v in _objs_file_dict.items():
                if '_Render' not in k:
                    _meshs, _bs_objs = self._selet_objs_bs(v)

                    _work_file = '{}/{}_Rig.json'.format(self._work_bs_dir, k)
                    data = {}
                    if _bs_objs:

                        cmds.select(cl=1)
                        cmds.select(_meshs)
                        print('meshs:', _meshs)

                        if self._asset_type and self._asset_type in ['npc', 'cartoon_npc']:
                            _data, _ok, _info = sdr_export_bs.to_unity_bs_data_and_successful_info(True)
                            if _info:
                                print(_info)
                            if _ok == True:
                                data = _data
                        else:
                            _data, _ok, _info = sdr_export_bs.to_unity_bs_data_and_successful_info(False)
                            if _info:
                                print(_info)
                            if _ok == True:
                                data = _data
                        try:
                            if data:
                                _jsonio.write(data, path=_work_file)
                                print('write json success:{}'.format(_work_file))
                                _work_files.append(_work_file)
                        except:
                            pass

        return _work_files

    def __judge_data_not_enmity(self, data):
        if not data or not isinstance(data, dict):
            return False
        _data = []
        for k, v in data.items():
            if v and isinstance(v, list):
                _data.append(v)
        if _data:
            return True
        else:
            return False

    @property
    def _fbx_info(self):
        return analyze_fbx.AnalyFbx(self.taskdata).get_fbx()

    @property
    def root_group(self):
        u"""
        获取最外层大组
        Returns:

        """

        return group_common.BaseGroup().get_root_groups()

    def _get_objs_file_dict(self):
        u"""
        获得物体及对应json
        :return:
        """
        _dict = {}
        _fbx_info = self._fbx_info
        _ad = self._get_rig_ad()
        _fbx_info_n = self._cover_variable_info('{ad}', _ad, _fbx_info)

        if _fbx_info_n:
            for i in range(len(_fbx_info_n)):
                if _fbx_info_n[i] and 'fbx_objs' in _fbx_info_n[i] and 'fbx_file' in _fbx_info_n[i]:

                    _objs = _fbx_info_n[i]['fbx_objs']
                    _file = _fbx_info_n[i]['fbx_file']

                    if '_FX_' in _file:
                        _fx_dict = self._cover_FX_fbx(_file)
                        if _fx_dict:
                            for k, v in _fx_dict.items():
                                if v not in _dict:
                                    _dict[v] = [k]
                    else:
                        _dict[_file] = _objs
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
        import maya.cmds as cmds

        grps = []

        objs = cmds.ls(key, l=1, type='transform')
        if objs:
            for obj in objs:
                if not cmds.listRelatives(obj, s=1):
                    grps.append(obj)
        if grps:
            grps = list(set(grps))
        return grps

    def _get_rig_ad(self):
        u"""
        获取rig ad
        """
        _rig_grp = self._get_body_root()
        if _rig_grp:
            return _rig_grp.split('|')[-1].split('_Rig')[0]

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

    def _get_targets(self):
        u"""
        获得bs targets物体
        :return:
        """
        return (ADPoses.get_targets() + self._get_twist_targets())

    def _selet_objs_meshs(self, _objs):
        u"""
        判读物体，或组下物体是否有信息
        :param _objs: 物体(组)列表
        :return:
        """
        import maya.cmds as cmds
        _bs_meshs = []
        if _objs:
            _meshs = self._select_objs_meshs(_objs)
            cmds.select(_meshs)
            # return get_bs_info.get_selected_bsMeshes()
            return _meshs

    def _selet_objs_bs(self, _objs):
        u"""
        判读物体，或组下物体是否有信息
        :param _objs: 物体(组)列表
        :return:
        """
        import maya.cmds as cmds
        _bs_meshs = []
        _meshs = []
        if _objs:
            _meshs = self._select_objs_meshs(_objs)
            cmds.select(_meshs)
            _bs_meshs = get_bs_info.get_selected_bsMeshes()
        return _meshs, _bs_meshs

    def _select_objs_meshs(self, _objs):
        u"""
        获得mesh物体(tr节点)
        :param _objs:
        :return:
        """
        import maya.cmds as cmds
        _meshs = []
        if _objs:
            for _obj in _objs:
                if _obj and cmds.ls(_obj):
                    if cmds.listRelatives(_obj, s=1, type='mesh'):
                        _meshs.append(_obj)
                    elif not cmds.listRelatives(_obj, s=1):
                        _mesh = self._select_grp_meshs(_obj)
                        if _mesh:
                            trs = self._select_meshs_tr(_mesh)
                            if trs:
                                _meshs.extend(trs)
        return _meshs

    def _select_meshs_tr(self, _meshs):
        u"""
        从shape 获得tr节点列表
        :param _meshs:
        :return:
        """
        import maya.cmds as cmds
        _trs = []
        if _meshs:
            for _mesh in _meshs:
                if _mesh and cmds.ls(_mesh) and cmds.listRelatives(_mesh, p=1, type='transform'):
                    _trs.extend(cmds.listRelatives(_mesh, p=1, type='transform', f=1))
        if _trs:
            _trs = list(set(_trs))
        return _trs

    def _select_grp_meshs(self, grp=''):
        u"""
        获得组下所有模型tr节点
        :param grp: 组
        :return:
        """
        import maya.cmds as cmds
        try:
            return cmds.listRelatives(grp, type='mesh', ad=1, f=1)
        except:
            return

    def _to_unity_bs_data(self, ifFullPath):
        all_targets = self._get_targets()
        bsMeshs_path_list, bs_nodes = get_bs_info.get_bsMeshs_list(all_targets, ifFullPath)

        targets = []
        for target in all_targets:
            for bs_node in bs_nodes:
                if bs_node.hasAttr(target):
                    targets.append(target)
        real_targets = list(set(targets))
        real_targets.sort()

        target_name_comb_id = dict()
        comb_joint_id = 0

        # get pose to unity data
        joint_elements = []
        ad_poses = ADPoses.targets_to_ad_poses(real_targets)
        for ad, poses in ad_poses:
            target_names = [ad.target_name(pose) for pose in poses]
            driver_node = sdr.node_name(ad.joint)
            axis = 0
            driver_pose_data, up = sdr.driven_poses(ad.joint, poses)
            target_names.insert(0, "bindPose")
            bsinfo_list = [get_bs_info.search_bsinfo(target, bs_nodes) for target in target_names]
            rbf_poses = [dict(driverPose=driver, bsInfo=bsinfo)
                         for driver, bsinfo in zip(driver_pose_data, bsinfo_list)]
            part_sorted = sorted(rbf_poses[1:])
            rbf_poses[1:] = part_sorted
            joint_elements.append(dict(
                driverNode=driver_node,
                rbfPoses=rbf_poses,
                axis=axis,
                driverUpPose=up,
                k=2,
                isADsolveMode=True,
                is2DsolveMode=False
            ))

            for comb_target_id, target_name in enumerate(target_names):
                target_name_comb_id[target_name] = [comb_joint_id, comb_target_id]
            comb_joint_id += 1
        # comb data
        all_driven_nodes = []
        fk_sdk_set = fk_data.find_node_by_name("FkSdkJointSet")
        fk_sdk_joints = []
        joint_bind_pose = {}
        if fk_sdk_set is not None:
            fk_sdk_joints = pm.ls(fk_sdk_set.elements(), type="joint")
            for joint in fk_sdk_joints:
                name = fk_data.node_name(joint)
                joint_bind_pose[name] = joint.getMatrix()

        comb_elements = []
        comb_targets = [target_name for target_name in all_targets if "_COMB_" in target_name]
        for comb_target in comb_targets:
            for target_name in comb_target.split("_COMB_"):
                if target_name not in target_name_comb_id:
                    message = u"导出模型缺失目标体：" + target_name
                    pm.warning(message)
                    return message
            ids = [target_name_comb_id[target_name] for target_name in comb_target.split("_COMB_")]
            ids = {"driverId%i" % i: {"elementId": element_id, "poseId": pose_id}
                   for i, (element_id, pose_id) in enumerate(ids)}
            bs_info = get_bs_info.search_bsinfo(comb_target, bs_nodes)
            row = dict(
                drivenNodes=[],
                drivenPose=[],
                bsInfo=bs_info,
            )
            row.update(ids)
            comb_elements.append(row)
            # comb joint data
            target_name = comb_target
            if len(fk_sdk_joints) == 0:
                continue
            ADPoses.set_pose_by_targets([target_name])
            matrix_list = []
            name_list = []
            for joint in fk_sdk_joints:
                name = fk_data.node_name(joint)
                bind_pose_matrix = joint_bind_pose[name]
                current_matrix = joint.getMatrix()
                if fk_data.matrix_eq(bind_pose_matrix, current_matrix):
                    continue
                matrix_list.append(current_matrix * bind_pose_matrix.inverse())
                name_list.append(name)
                if name not in all_driven_nodes:
                    all_driven_nodes.append(name)
            driven_pose = [fk_data.matrix_to_unity_position_rotation(matrix) for matrix in matrix_list]
            driven_nodes = [all_driven_nodes.index(name) for name in name_list]
            row["drivenNodes"] = driven_nodes
            row["drivenPose"] = driven_pose
            ADPoses.set_pose_by_targets([])

        data = dict(
            rbfElements=joint_elements,
            allDrivenNodes=[],
            bsMeshs=bsMeshs_path_list,
            twistElements=self.twist_to_unity_data(bs_nodes),
            combElements=comb_elements,
        )

        fk_data.update_fk_data(data)
        return data
