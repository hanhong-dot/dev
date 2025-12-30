# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       : process_batch_file
# Describe   : fbx前处理文件(BakeToControl)
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2022/7/12__19:42
# -------------------------------------------------------
import maya.cmds as cmds

import maya.mel as mel
import maya.OpenMaya as om

from . import bk, reference
class ProcessFile(object):
    def __init__(self, startframe, endframe, name_space='', _bake=True):
        self._bake = _bake
        self._ns = name_space

        self._startframe = startframe
        self._endframe = endframe

    def process_file(self):
        u"""
        文件处理
        :return:
        """
        # bake to control
        if self._bake == True:
            self._bake_to_control(self._ns)
        self._delete_ST()

    def _delete_ST(self):
        u"""
        删除fbx物体
        :return:
        """
        _root_grps = self._get_root_grp()
        _delet_objs = []
        _objlist = ['*_Rig', '*:Reference']
        for _ob in _objlist:
            _objs = cmds.ls(_ob, l=1)
            for i in range(len(_objs)):
                if _objs[i] in _root_grps and _objs[i] not in _delet_objs:
                    _delet_objs.append(_objs[i])

        if _delet_objs:
            self._delete(_delet_objs)

    def _delete(self, objs):
        u"""
        删除物体
        :param objs: 需要删除的物体列表
        :return:
        """
        if objs:
            for ob in objs:
                if ob and cmds.ls(ob):
                    try:
                        cmds.delete(ob)
                    except:
                        cmds.lockNode(ob, l=0)
                        cmds.delete(ob)

    def _get_root_grp(self):
        u"""
        获得最外层大组
        :return:
        """
        EXCLUDE = ['|persp', '|top', '|front', '|side']
        objlist = []
        trs = cmds.ls(tr=1, l=1)
        for tr in trs:
            _split = tr.split('|')
            if len(_split) <= 2 and tr not in EXCLUDE and tr not in objlist:
                objlist.extend(cmds.ls(tr, l=1))
        return objlist

    def _get_reference_ns(self):
        u"""
        获得参考 namespace
        :return:
        """

        _ref_dict = reference.reference_info_dict()
        if _ref_dict:
            return _ref_dict.keys()

    def _bake_to_control(self, _ns=''):
        u"""
        bake 到control(修改自 MaxToMaya_kami (T:/X3_RawData/X3_MayaTools/python/MaxToMaya_kami))
        :param _ns:  namespacew
        :return:
        """
        if not _ns:
            return
        # 设置当前帧为起始帧
        cmds.currentTime(self._startframe)
        #
        _ctrls = bk.bk_ctrl()

        FKcon = [_ns + ':' + ii for ii in _ctrls["fkcon"]]
        fk_js = [_ns + ':' + ii for ii in _ctrls["fk_js"]]
        ik_cons = [_ns + ':' + ii for ii in _ctrls["ik_cons"]]
        ik_vector = [_ns + ':' + ii for ii in _ctrls["ik_vector"]]

        constrains = []
        locs = []
        for item in FKcon:
            if 'FK' in item:
                extra = item.replace('FK', 'FKExtra')
            elif 'RootX' in item:
                extra = item.replace('Root', 'RootExtra')
            if cmds.objExists(extra):
                parent = cmds.listRelatives(extra, p=True)[0]
                loc = cmds.spaceLocator(n=item + '_fixOrder_locs')[0]
                cmds.parent(loc, parent)
                mel.eval('ResetTransformations("{0}")'.format(loc))
                cmds.setAttr(loc + '.rotateOrder', cmds.getAttr(item + '.rotateOrder'))
                cons = cmds.parentConstraint(extra, loc)[0]
                constrains.append(cons)
                locs.append(loc)

        if locs:
            cmds.bakeResults(locs, sm=True, t=(self._startframe, self._endframe), sb=1)
            cmds.delete(constrains)
            for ll in locs:
                mainFK = ll.split('_fixOrder_locs')[0]
                cmds.connectAttr(ll + '.translateX', mainFK + '.translateX')
                cmds.connectAttr(ll + '.translateY', mainFK + '.translateY')
                cmds.connectAttr(ll + '.translateZ', mainFK + '.translateZ')

                cmds.connectAttr(ll + '.rotateX', mainFK + '.rotateX')
                cmds.connectAttr(ll + '.rotateY', mainFK + '.rotateY')
                cmds.connectAttr(ll + '.rotateZ', mainFK + '.rotateZ')

            FKCon_ex = []
            for dd in FKcon:
                if cmds.objExists(dd):
                    FKCon_ex.append(dd)
                else:
                    cmds.warning('{} Non-Ex !! please check your scenes'.format(dd))

            cmds.bakeResults(FKCon_ex, sm=True, t=(self._startframe, self._endframe), sb=1)
            cmds.delete(locs)
            self.cleanMocapjoint(_ns)
            # bake
            print(fk_js, ik_cons, ik_vector, self._startframe, self._endframe)
            self.BakeIKcontroler(fk_js, ik_cons, ik_vector, self._startframe, self._endframe)

    def BakeIKcontroler(self, fk_js, ik_cons, ik_vector, timemin, timemax):
        sp_locs = []
        constrains = []

        objtest = fk_js[0] + '_FKIK_switch'
        if cmds.objExists(objtest):
            for ii in fk_js:
                sploc = cmds.spaceLocator(n=ii + '_joint_loc')[0]
                cons = cmds.parentConstraint(ii + '_FKIK_switch', sploc, mo=False)[0]
                sp_locs.append(sploc)
                constrains.append(cons)

            vec_locs = []
            for ii in range(4):
                cmds.setAttr(ik_vector[ii] + '.follow', 0)
                sploc = cmds.spaceLocator(n=fk_js[ii] + '_vector_sp_loc')[0]
                cons = cmds.parentConstraint(fk_js[ii] + '_FKIK_switch_pole', sploc, mo=False)[0]

                constrains.append(cons)
                vec_locs.append(sploc)

            cmds.bakeResults(sp_locs + vec_locs, sm=True, t=(timemin, timemax), sb=1)
            cmds.delete(constrains)

            constrains = []
            for ii in range(4):
                pp = cmds.parentConstraint(sp_locs[ii], ik_cons[ii], mo=False)[0]
                po = cmds.pointConstraint(vec_locs[ii], ik_vector[ii], mo=False)[0]
                constrains.append(pp)
                constrains.append(po)

            cmds.bakeResults(ik_vector + ik_cons, sm=True, t=(timemin, timemax), sb=1)
            cmds.delete(constrains, vec_locs, sp_locs)
            om.MGlobal.displayInfo('Bake HIK to maya already over!!!')
        else:
            om.MGlobal.displayError('ik bake failure, maybe the rigging not completely, please call kami!')

    def cleanMocapjoint(self, _ns):

        root = [_ns + ':' + 'Root_MoCap_M', _ns + ':' + 'Mocap_Root_M']

        for uu in root:
            if cmds.objExists(uu):
                joint = [uu]
                sel = cmds.listRelatives(uu, ad=True)
                for ii in sel:
                    if cmds.objectType(ii) == 'joint':
                        joint.append(ii)
                for ii in joint:
                    self.disConnnectAttr(ii + '.tx')
                    self.disConnnectAttr(ii + '.ty')
                    self.disConnnectAttr(ii + '.tz')
                    self.disConnnectAttr(ii + '.rx')
                    self.disConnnectAttr(ii + '.ry')
                    self.disConnnectAttr(ii + '.rz')
                cmds.joint(uu, e=True, apa=True, ch=True)
                cmds.setAttr(uu + '.translateX', 0)
                cmds.setAttr(uu + '.translateY', 0)
                cmds.setAttr(uu + '.translateZ', 0)
            else:
                cmds.warning('{0} Non-Ex , check it!!'.format(uu))

    def disConnnectAttr(self, attr):
        u"""
        断开连接
        :param attr:
        :return:
        """
        source = cmds.listConnections(attr, p=True, s=True, d=False)
        if source:
            cmds.disconnectAttr(source[0], attr)


def file_save_as(_add=None):
    u"""

    :param _add: 当前路径添加文件夹 ，例如原 D:\test  ,另存后就为 d:\test\save
    :return:
    """
    import os
    _filename = cmds.file(q=1, exn=1)
    if _filename:
        _path, _file = os.path.split(_filename)
        if not _add:
            _dir = _path
        else:
            _dir = '{}/{}'.format(_path, _add)

        _file_new = '{}/{}'.format(_dir, _file)
        # 创建文件夹
        _makedirs(_dir)
        # 保存文件
        save_file(_file_new)


def save_file(filename):
    u"""
    保存文件
    :param filename: 文件夹+文件名
    :return: 保存成功,返回filename;保存失败,返回False
    """
    import os
    _format = get_format(filename)

    if _format and _format != False:
        try:
            # 添加创建文件路径 xcz 2021.8.6
            _path = os.path.dirname(filename)
            if not os.path.exists(_path):
                os.makedirs(_path)
            cmds.file(rename=filename)
            cmds.file(save=True, type=_format, f=True, options="v=0;")
        except:
            raise Exception(u'文件未保存成功'.encode('gbk'))


def save_current_file():
    _filename = cmds.file(q=1, exn=1)
    if _filename:
        save_file(_filename)
        return


def get_format(_file):
    u"""
    获取文件格式
    """
    import os
    _sub = os.path.splitext(_file)[-1]
    _format = ''
    if _sub == '.mb':
        _format = 'mayaBinary'
    else:
        _format = 'mayaAscii'
    return _format


def _makedirs(_dir=''):
    import os
    if _dir and not os.path.exists(_dir):
        try:
            os.makedirs(_dir)
        except:
            pass


if __name__ == '__main__':
    _char = "ST001C_HD_Rig"
    _startframe = 0
    _endframe = 131
    _process_handle = ProcessFile(_startframe, _endframe)
    # _process_handle.process_fil()

    file_save_as('save')
