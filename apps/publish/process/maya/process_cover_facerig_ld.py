# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       : process_cover_facerig_ld
# Describe   : body drama_rig 自动转换生成facerig_ld文件
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2023/12/13__10:47
# -------------------------------------------------------


from database.shotgun.core import sg_task

import database.shotgun.core.sg_analysis as sg_analysis
import lib.maya.node.grop as node_grp
import maya.cmds as cmds
import lib.maya.process.bs_break as bs_break
import method.maya.common.file as file_common
from method.shotgun import get_task_data

FACERIG_LD_TASK_NAME = 'faceld_rig'
MODEL_GRPS = ['*001F_HD', '*001H_HD','*001F_New_HD', '*001H_New_HD']
BREAK_GRPS = ['*001B_HD','*001B_New_HD']
FACE_GRPS = ['face_final_rigging_system']
ROOT_EXR = ['Head_M_spare']
import apps.publish.ui.layout.batch_publish as batch_publish

import method.shotgun.get_task as get_task


class ProcessCoverFaceLd(object):
    def __init__(self, TaskData, version_file, description=u'drama_rig 上传，自动生成'):
        self._task_data = TaskData
        self._version_file = version_file
        self._description = description
        self._task_name = self._task_data.task_name
        self._task_id = self._task_data.task_id
        self._task_step_id = self._task_data.step_id
        self._entity_name = self._task_data.entity_name
        self._entity_id = self._task_data.entity_id
        self._entity_type = self._task_data.entity_type
        self._project_name = self._task_data.project_name
        self._asset_type = self._task_data.asset_type

        self._sg = sg_analysis.Config().login()

    def process_face_ld(self):
        if self._asset_type in ['body'] and self._task_name in ['drama_rig']:
            work_file= self._process_cover_face_ld()
            file_common.BaseFile().open_file(work_file)
            face_ld_task_data = get_task.TaskInfo(work_file, 'X3', 'maya', 'version')
            if self._version_file:
                batch_publish.PPublishWidget(face_ld_task_data).do_publish(self._version_file, self._description)
            else:
                batch_publish.PPublishWidget(face_ld_task_data).do_publish_without_version(self._description)

    def _process_cover_face_ld(self):
        file_name = cmds.file(q=1, exn=1)
        file_common.BaseFile().open_file(file_name)
        #
        task = self.creat_faceld_rig_task()
        #
        face_ld_task_data = get_task_data.TaskData(task[0]['id'])
        work_file = face_ld_task_data.get_work_path(next=True)
        file_common.BaseFile().save_file(work_file)
        # 断开模型组关联
        self.process_break_grps()
        # 删除隐藏组或模型
        self.delete_hide_grps_meshs()

        # 断开root 连接
        self.break_root_cons('Roots')
        # 册除控制器组
        self.delete_ctrl_grp()

        # 导出文件
        select_objs = []
        mdl_grps = self.get_modle_grps()
        root_join = cmds.ls('Roots', l=1)
        face_ctrl=cmds.ls(FACE_GRPS, l=1)
        if root_join:
            select_objs.append(root_join[0])
        if mdl_grps:
            select_objs.extend(mdl_grps)
        if face_ctrl:
            select_objs.extend(face_ctrl)
        cmds.select(select_objs)
        file_common.BaseFile().export_file(select_objs, work_file, format="mayaAscii")
        return work_file

    def get_modle_grps(self):
        return cmds.ls((MODEL_GRPS + BREAK_GRPS), l=1, type='transform')

    def break_root_cons(self, joint_root='Roots'):
        u"""
        断开Roots
        :return:
        """
        break_joints = []
        root_joint_joins = self.get_joins_by_roots(joint_root)
        root_exr_joins = self.get_joins_by_roots(ROOT_EXR)
        if root_joint_joins and root_exr_joins:
            break_joints = list(set(root_joint_joins).difference(set(root_exr_joins)))
        if root_joint_joins and not root_exr_joins:
            break_joints = root_joint_joins
        if break_joints:
            self._disconnet_joins(break_joints)

    def get_joins_by_roots(self, joint_root):
        join_list = []
        if cmds.ls(joint_root):
            joint_root = cmds.ls(joint_root, l=1)[0]
            joins = cmds.listRelatives(joint_root, ad=1, type='joint', f=1)
            if joins:
                join_list.extend(joins)
            join_list.append(joint_root)
        return join_list

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

    def delete_ctrl_grp(self):
        root_grps = node_grp.BaseGroup().get_root_groups()
        rig_grps = self.get_rig_grp()
        ctrl_grps = list(set(root_grps) - set([rig_grps]))

        face_grp = cmds.ls(FACE_GRPS, l=1)

        ctrl_ad_grps = []
        delete_grps = []

        if ctrl_grps:
            for grp in ctrl_grps:
                ad_grps = cmds.listRelatives(grp, c=1, type='transform', f=1)
                if ad_grps:
                    ctrl_ad_grps.extend(ad_grps)

        if ctrl_ad_grps:
            delete_grps = list(set(ctrl_ad_grps) - set(face_grp))

        # print 'delete_grps',delete_grps
        # cmds.select(delete_grps)

        if delete_grps:
            for grp in delete_grps:
                if cmds.ls(grp):
                    cmds.delete(grp)

    def delete_hide_grps_meshs(self):
        mdl_grps = self.get_mdl_grp()
        no_delete_grps =cmds.ls((MODEL_GRPS + BREAK_GRPS),l=1,type='transform')
        delete_grps = list(set(mdl_grps) - set(no_delete_grps))
        delete_objs = []
        if delete_grps:
            for grp in delete_grps:
                if cmds.getAttr(grp + '.visibility') == 0:
                    delete_objs.append(grp)
                else:
                    objs = cmds.listRelatives(grp, ad=1, type='transform', f=1)
                    if objs:
                        for obj in objs:
                            if cmds.getAttr(obj + '.visibility') == 0:
                                delete_objs.append(obj)
        if delete_objs:
            cmds.delete(delete_objs)

    def process_break_grps(self):
        grps = self.get_other_mdl_grps()
        if grps:
            meshs = self._select_grps_meshs(grps)
            if meshs:
                cmds.select(meshs)
                bs_break.mainFunc()

    def _select_grps_meshs(self, _grps):
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

    def select_grp_meshs(self, grp=''):
        try:
            return cmds.listRelatives(grp, type='mesh', ad=1, f=1)
        except:
            return

    def get_break_grps(self):
        return cmds.ls(BREAK_GRPS, type='transform', l=1)

    def get_not_delete_mdl_grps(self):
        return cmds.ls(MODEL_GRPS, type='transform', l=1)

    def get_other_mdl_grps(self):
        mdl_grps = self.get_mdl_grp()
        not_delete_mdl_grps = self.get_not_delete_mdl_grps()
        other_mdl_grps = list(set(mdl_grps) - set(not_delete_mdl_grps))
        return other_mdl_grps

    def get_mdl_grp(self):
        '''
        获取mdl组
        :return:

        '''
        mdl_grp = []
        rig_grp = self.get_rig_grp()
        if rig_grp:
            grps = cmds.listRelatives(rig_grp, c=1, type='transform', f=1)
            for grp in grps:
                if cmds.listRelatives(grp, ad=1, type='mesh'):
                    mdl_grp.append(grp)
        return mdl_grp

    def get_rig_grp(self):
        '''
        获取mdl组
        :return:

        '''
        rig_grp = ''
        root_grps = node_grp.BaseGroup().get_root_groups()
        if root_grps:
            for root_grp in root_grps:
                if '_Rig' in root_grp.split('|')[-1] or '_rig' in root_grp.split('|')[-1]:
                    rig_grp = root_grp
                    break
        return rig_grp

    def creat_faceld_rig_task(self):
        '''
        创建faceld_rig task
        :return:
        '''
        task = sg_task.get_task_taskID(self._sg, self._project_name, FACERIG_LD_TASK_NAME, self._entity_name)
        if task:
            return task
        else:
            return sg_task.creat_task(self._sg, self._project_name, self._task_step_id, self._entity_type,
                                      self._entity_id, FACERIG_LD_TASK_NAME, return_fields=['id'])


if __name__ == '__main__':
    import method.shotgun.get_task as get_task

    reload(get_task)

    _filename = 'RY_Body.drama_mdl.v027.ma'
    taskdata = get_task.TaskInfo(_filename, 'X3', 'maya', 'version')

    version_file = r'M:\projects\x3\publish\assets\body\FY_BODY\mod\maya\RY_Body.drama_mdl.v001.png'
    handle=ProcessCoverFaceLd(taskdata, version_file)

    task=handle.creat_faceld_rig_task()


    print task
#     # handle.process_face_ld()
