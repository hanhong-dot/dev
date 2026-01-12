# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       : check_exist_mshader
# Describe   : 检测一个模型连接多个材质球
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2022/10/26__11:17
# -------------------------------------------------------
import maya.cmds as cmds
import lib.common.loginfo as info

import lib.maya.node.shadingEngine as shadingEngine

reload(shadingEngine)


class Check(object):
    """
    检查是否存在面赋材质模型
    """

    def __init__(self, grp=None):
        super(Check, self).__init__()

        self.name = u'检查是否存在一个连接多个材质球,一个材质球连接多个模型'
        self.tooltip = u'所有模型不能一个模型连接多个材质。'
        # <editor-fold desc="===先罗列所有异常键值===">
        self._multiple_error_key = u'■以下模型存在一个模型连接多个材质球,请检查:'
        self._multiple_mesh_error_key = u'■以下材质球连接多个模型,请检查:'
        self._zero_error_key = u'■以下模型未连接材质球,请检查:'
        # </editor-fold>
        self._tooltip_true=u'已检测，未发现一个模型连接多个材质球,一个材质球连接多个模型情况'

        self._grp = grp
        self._errorInfoDict = self.run()

    def checkinfo(self):
        """
        显示检测内容
        """
        _error_info = self._errorInfoDict
        _error_lists = []
        if _error_info:
            for k, v in _error_info.items():
                _error_lists.append(k)
                _error_lists.extend(v)
                _error_lists.append("=" * 36)

        if _error_lists:
            return False, info.displayErrorInfo(objList=_error_lists)
        else:
            return True, info.displayInfo(title=self._tooltip_true )

    def run(self):
        '''
        开始检查是否存在面赋材质模型
        :return:
        '''
        # mesh 列表
        __error={}
        _meshlist = self._get_meshs()
        # 获得连接字典
        _dict = self._select_meshs_sgdict(_meshlist)
        # 未连接或连接多个sg节点模型(tr节点)
        shader_error_dict = self._judge_mshader(_dict)
        if shader_error_dict:
            __error.update(shader_error_dict)
        # 一个材质球连接多个模型
        shader_multiple_mesh_dict = self._judge_mshader_multiple_mesh(_dict)
        if shader_multiple_mesh_dict:
            __error.update(shader_multiple_mesh_dict)
        return __error



    def _select_meshs_sgdict(self, _meshs):
        u"""
        由mesh列表获得sg 字典
        :param _meshs:mesh 列表
        :return:
        """
        if _meshs:
            return shadingEngine.BaseShadingEngine().select_nodelish_shadingenginedict(_meshs)

    def _judge_mshader_multiple_mesh(self, _dict):
        u"""
        判断一个材质球连接多个模型
        :param _dict:
        :return:
        """

        _merror = []
        __shader_list = []
        __shader_dict = {}
        if not _dict:
            return {}
        for k, v in _dict.items():
            if v:
                for sg in v:
                    __shader = cmds.listConnections(sg + ".surfaceShader", s=1, d=1, p=0)
                    if not __shader:
                        continue
                    __shader_list.extend(__shader)
        if not __shader_list:
            return {}
        __shader_list = list(set(__shader_list))
        for shader in __shader_list:
            __meshs=[]
            __sgs = cmds.listConnections(shader, s=0, d=1, p=0, type='shadingEngine')
            if not __sgs:
                continue
            for sg in __sgs:
                __sg_meshs = cmds.sets(sg, q=1)
                if __sg_meshs:
                    __meshs.extend(__sg_meshs)
            if not __meshs:
                continue
            __meshs=list(set(__meshs))
            __shader_dict[shader]=__meshs
        if not __shader_dict:
            return {}
        for k, v in __shader_dict.items():
            if v and len(v) > 1:
                _merror.extend(k)
        if _merror:
            return {self._multiple_mesh_error_key: list(set(_merror))}


    def _judge_mshader(self, _dict):
        u"""
        判断一个模型连接不止一个sg节点或未连接sg节点
        :param _dict:
        :return:
        """
        _merror = []
        _nerror = []
        _errdict = {}
        if _dict:
            for k, v in _dict.items():
                if not v:
                    _tr = cmds.listRelatives(k, p=1, type='transform')
                    if _tr:
                        _nerror.extend(_tr)
                if v and len(v) > 1:
                    _tr = cmds.listRelatives(k, p=1, type='transform')
                    if _tr:
                        _merror.extend(_tr)
        if _merror:
            _errdict[self._multiple_error_key] = list(set(_merror))
        if _nerror:
            _errdict[self._zero_error_key] = list(set(_nerror))
        return _errdict

    def _get_meshs(self):
        u"""
        获得mesh 列表
        :return:
        """
        if not self._grp or not cmds.ls(self._grp):
            return cmds.ls(type='mesh')
        else:
            return cmds.listRelatives(self._grp, ad=1, type='mesh')

    def fix(self):
        '''
        修复相关内容
        :return:
        '''
        return True


if __name__ == "__main__":
    # 测试代码

    # Check().checkinfo()
    _dict = {u'FY001C_UE_A_01Shape': [u'blinn9SG'],
             u'FY001C_UE_A_02Shape': [u'blinn11SG'],
             u'FY001C_UE_A_03Shape': [u'blinn14SG'],
             u'FY001C_UE_ArmShape': [u'FY_Arm_matSG'],
             u'FY001C_UE_BodyShape': [u'FY_Body_matSG'],
             u'FY001C_UE_CFX_A_01Shape': [u'blinn18SG'],
             u'FY001C_UE_CFX_C_01Shape': [u'blinn19SG'],
             u'FY001C_UE_CFX_P_01Shape': [u'blinn17SG'],
             u'FY001C_UE_C_01Shape': [u'blinn13SG'],
             u'FY001C_UE_C_02Shape': [u'blinn8SG'],
             u'FY001C_UE_C_03Shape': [u'blinn15SG'],
             u'FY001C_UE_C_04Shape': [u'blinn16SG'],
             u'FY001C_UE_P_01Shape': [u'blinn10SG'],
             u'FY001C_UE_P_02Shape': [u'blinn12SG'],
             u'FY001C_UE_P_03Shape': [u'pasted__pasted__pasted__FY001C_HD_P_01SG'],
             u'FY001C_UE_S_01Shape': [u'pasted__pasted__pasted__pasted__pasted__FY001C_Card_HD_S_01_matSG2']}
