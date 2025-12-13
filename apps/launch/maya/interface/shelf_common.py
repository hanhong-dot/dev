# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       : shelf_common.py
# Describe   : 说明描述
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2022/5/9__13:50
# -------------------------------------------------------
import os
import sys

import maya.mel as mel
import maya.cmds as cmds

BASH_DIR = os.path.dirname(os.path.abspath(__file__)).split('launch')[0]
sys.path.append(BASH_DIR)

import lib.common.jsonio as jsonio


# __all__ = ["set_shelf2", "restore_shelf2", "remove_shelf2"]

# 暂时关闭删除shelf
__all__ = ["set_shelf2", "restore_shelf2", "remove_shelf2"]

_NODELETE_SHELF=['UnityMeshSync','X3_Animation','X3_modelling','X3_Pipe','X3_rigging','Custom']
def set_shelf2(config, project):
    '''设置pipeline工具架
    '''

    _shelfhandle = Shelf(config, project)
    if not _shelfhandle.exists():
        _shelfhandle.set_shelf()
        _shelfhandle.build_shelfitem(_shelfhandle.data())


def restore_shelf2(config, project):
    remove_shelf2(config, project)
    set_shelf2(config, project)


def remove_shelf2(config, project):
    _shelfhandle = Shelf(config, project)
    _shelfhandle.remove_shelf()


class Shelf(object):
    '''工具架处理与生成类
    '''

    def __init__(self, config, project=None):
        self._shelftab = mel.eval('global string $gShelfTopLevel;string $a=$gShelfTopLevel;')
        self._data = jsonio.read(config)
        self._project = project
        if not self._data:
            raise Exception(u"读取配置信息有误".encode("gbk"))

    def data(self):
        return self._data

    def _get_key(self, key):
        '''去除键头的数字
            maya默认不支持数字开头所以要手动去除
        '''
        return key[len(key.split("_")[0]):]

    def _get_current_level_keys(self, info, parent=None):
        '''获取当前层级的所有按钮
        '''
        outinfo = []
        for k, v in info.items():
            if isinstance(v, dict):
                _tempinfo = {
                    "index": int(k.split("_")[0]),
                    "key": k,
                    "code": self._get_key(k),
                    "docTag": v["docTag"] if "docTag" in v else "",
                    "label": v["label"],
                    "icon": v["icon"] if "icon" in v else "",
                    "parent": self._project,
                    "ann": v["ann"] if "ann" in v else "",
                    "command": v["command"] if "command" in v else "",
                    "cmdrepeat": v["cmdrepeat"] if "cmdrepeat" in v else 0,
                    "is_sub": False,
                }
                for k2, v2 in v.items():
                    if isinstance(v2, dict):
                        _tempinfo["is_sub"] = True
                        break
                outinfo.append(_tempinfo)
        return sorted(outinfo, key=lambda x: x["index"])

    def build_levelitem(self, info, parent=None):
        '''创建按钮
        '''
        subkey = []
        _current_level_keys = self._get_current_level_keys(info, parent)
        if _current_level_keys:
            for _key in _current_level_keys:
                cmds.shelfButton(_key["code"],
                                 docTag=_key["docTag"],
                                 rpt=_key["cmdrepeat"],
                                 l=_key["label"],
                                 iol=_key["label"],
                                 i1=_key["icon"],
                                 ann=_key["ann"],
                                 c=_key["command"],
                                 p=_key["parent"],
                                 overlayLabelBackColor = (.15, .15, .15, 1)
                                 )
                if _key["docTag"]:
                    cmds.shelfButton(_key["code"], e=1, visible=0)
                if _key["is_sub"]:
                    subkey.append(_key["key"])
        return subkey

    def build_shelfitem(self, levelinfo, parent=None):
        if levelinfo:
            _subkey = self.build_levelitem(levelinfo, parent)
            if _subkey:
                for k, v in levelinfo.items():
                    if k in _subkey:
                        self.build_shelfitem(levelinfo[k], self._get_key(k))

    def remove_button(self, shelf):
        _shelf_fullname = cmds.shelfLayout(shelf, q=1, fpn=1)
        _buttons = cmds.shelfLayout(_shelf_fullname, q=1, ca=1)
        for _button in _buttons:
            _button_fullname = cmds.shelfButton(_button, q=1, fpn=1)
            cmds.deleteUI(_button_fullname)

    def remove_shelf(self):
        '''移除所有项目shelf
            方法改写自mel方法deleteShelfTab
            去除了确认框
        '''
        _shelfname = self._project
        _shelf_info = {i: _shelf for i, _shelf in enumerate(cmds.shelfTabLayout(self._shelftab, q=1, ca=1))
                       if _shelf.split("|")[-1].startswith(_shelfname[:2])}
        _shelfnum = cmds.shelfTabLayout(self._shelftab, q=1, numberOfChildren=1)
        if _shelf_info:
            for _k, _v in _shelf_info.items():
                # print("remove shelf:{}".format(_v))
                _shelf_fullname = cmds.shelfLayout(_v, q=1, fpn=1)
                for _i in range(_shelfnum):
                    _align_c = "left"
                    if cmds.optionVar(ex="shelfAlign{}".format(_i + 1)):
                        _align_c = cmds.optionVar(q="shelfAlign{}".format(_i + 1))
                    _shelfload_c = cmds.optionVar(q="shelfLoad{}".format(_i + 1))
                    _shelfname_c = cmds.optionVar(q="shelfName{}".format(_i + 1))
                    _shelffile_c = cmds.optionVar(q="shelfFile{}".format(_i + 1))
                    cmds.optionVar(
                        iv=("shelfLoad{}".format(_i + 1), _shelfload_c),
                        sv=[("shelfAlign{}".format(_i + 1), _align_c),
                            ("shelfName{}".format(_i + 1), _shelfname_c),
                            ("shelfFile{}".format(_i + 1), _shelffile_c)
                            ])
                cmds.optionVar(remove=["shelfLoad{}".format(_k),
                                       "shelfAlign{}".format(_k),
                                       "shelfName{}".format(_k),
                                       "shelfFile{}".format(_k)])
                cmds.deleteUI(_shelf_fullname, layout=1)
                _shelfdir = cmds.internalVar(ush=1)
                _shelffile = os.path.join(_shelfdir, "shelf_{}.mel".format(_v))
                if os.path.exists(_shelffile) and _v not in _NODELETE_SHELF:
                    os.remove(_shelffile)

    def set_shelf(self):
        mel.eval("addNewShelfTab {}".format(self._project))
        _shelf = cmds.shelfLayout(self._project, q=1, fpn=1)
        if cmds.shelfLayout(_shelf, q=1, ca=1):
            self.remove_button(_shelf)

    def exists(self):
        return self._project in cmds.shelfTabLayout(self._shelftab, q=1, ca=1)


def change_shelf(step=None):
    u"""
    change shelf
    :param step:
    :return:
    """
    _project = 'x3'
    _shelf = cmds.shelfLayout(_project, q=1, fpn=1)
    _child = cmds.shelfLayout(_shelf, q=1, childArray=1)
    if not _child:
        return
    if step:
        for i in range(len(_child)):
            tag = cmds.shelfButton(_child[i], q=1, docTag=1)
            if tag and tag == step:
                cmds.shelfButton(_child[i], e=1, visible=1)
            # cmds.shelfLayout(_shelf,e=1,position=(_child[i], index))#影响按钮排序，不使用
            if tag and tag != step:
                cmds.shelfButton(_child[i], e=1, visible=0)
    if not step:
        for i in range(len(_child)):
            tag = cmds.shelfButton(_child[i], q=1, docTag=1)
            if tag:
                cmds.shelfButton(_child[i], e=1, visible=0)
