# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       : hik_fun
# Describe   : hik 相关代码
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2022/7/13__19:30
# -------------------------------------------------------

import maya.mel as mel
import maya.cmds as cmds

CHLIST=['_mb_to_maya','mb2maya','mb_maya']
SCLIST=['ST_VR_MB_maya_to_mb','_maya_to_mb','maya_to_mb']
class HikSet(object):
    def __init__(self, character, source):
        u"""
        hik 重定位
        :param character: character
        :param source: source
        """
        self._character = character
        self._source = source

    def set_hik(self):
        u"""
        重定向
        :return:
        """
        # 更新cha
        try:
            self.updata_character()
        except:
            pass
        # 创建

        self.creat_ctrol()
        # 重定向设置
        self.set_charter()

    def set_charter(self):
        u"""
        设置重定向
        :return:
        """
        try:
            _cmd = 'hikSetCharacterInput( "{}", "{}" );'.format(self._character, self._source)
            mel.eval(_cmd)
        except:
            pass

    def creat_ctrol(self):
        u"""
        创建ctrl
        :return:
        """
        try:
            mel.eval("hikCreateControlRig();")
        except:
            pass

    def updata_character(self):
        u"""
        更新Character
        :return:
        """
        try:
            cmd = 'global string $gHIKCurrentCharacter;\n$gHIKCurrentCharacter = "{}";\nhikUpdateCharacterList();\nhikSetCurrentSourceFromCharacter($gHIKCurrentCharacter);\nhikUpdateSourceList();'.format(
                self._character)
            mel.eval(cmd)
        except:
            pass


def set_mb_to_maya():
    u"""
    设置mb 至maya
    :return:
    """

    from . import reference
    _ns = reference.reference_info_dict().keys()[0]
    _hik_nodes = get_hiknodes()
    _cha = _get_cha(_hik_nodes,_ns)
    _scr = _get_scr(_hik_nodes)
    if _cha and _scr:
        HikSet(_cha, _scr).set_hik()
        delete_reference(_cha)

def _get_cha(_hiknodes,_ns):
    u"""
    获得cha 键
    :param _hiknodes:
    :param _ns:
    :return:
    """

    _cha=''
    if _hiknodes :
        for i in range(len(_hiknodes)):
            for j in range(len(CHLIST)):
                if _ns in _hiknodes[i] and CHLIST[j] in _hiknodes[i]:
                    _cha=_hiknodes[i]
                    break
    return _cha

def _get_scr(_hiknodes):
    u"""
    获得scr键
    :param _hiknodes:
    :return:
    """
    _scr=''
    if _hiknodes :
        for i in range(len(_hiknodes)):
            for j in range(len(SCLIST)):
                if ":" not in _hiknodes[i] and SCLIST[j] in _hiknodes[i]:
                    _scr=_hiknodes[i]
                    break
    return _scr

def delete_reference(_cha):
    u"""
    删除参考
    :return:
    """
    ref = cmds.ls('{}_Ctrl_Reference'.format(_cha))
    if ref:
        try:
            cmds.delete(ref)
        except:
            pass


def get_hik_nodes():
    u"""
    获取文件中HIKCharacterNode节点
    :return:
    """
    return cmds.ls(type="HIKCharacterNode")


if __name__ == '__main__':
    _character = "ST001C_HD_Rig:ST_mb_to_maya"
    # _source = "ST_maya_to_mb"
    # _handle = HikSet(_character, _source)
    # _handle.set_hik()
    # set_mb_to_maya()
    # delete_reference(_character)
