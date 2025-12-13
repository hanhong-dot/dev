# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       : check_exist_binpose
# Describe   :
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2024/10/08
# -------------------------------------------------------
import lib.common.loginfo as info
import maya.cmds as cmds
from apps.publish.process.maya import process_rig_export_fbx
reload(process_rig_export_fbx)
from method.maya.common.file import BaseFile
import method.maya.common.reference as refcommon
import os

LIMI = 100


class Check(object):

    def __init__(self, TaskData):
        super(Check, self).__init__()
        self._taskdata = TaskData
        self.tooltip = u'开始检测fbx大小'
        self._error = u'以下fbx大小超过100M,请优化文件'

        self.end = u"已检测fbx大小"

    def checkinfo(self):
        _error = self.run()

        _error_list = []
        if _error:
            _error_list.append(self._error)
            _error_list.extend(_error)

            return False, info.displayErrorInfo(title=self.tooltip, objList=_error_list)
        else:
            return True, info.displayInfo(title=self.tooltip, objList=[self.end])

    def run(self):
        _errors = []
        __current_file = cmds.file(q=1, exn=1)
        BaseFile().save_file(__current_file)
        refcommon.import_all_reference()
        __exp_handle = process_rig_export_fbx.Porcess_RigFbx_Export(self._taskdata)
        _fbx_files = __exp_handle.check_export_fbx()
        if not _fbx_files:
            return
        for _fbx_file in _fbx_files:
            if _fbx_file and os.path.exists(_fbx_file):

                file_size = os.path.getsize(_fbx_file) / (1024 * 1024)
                if file_size >= LIMI:
                    _errors.append(os.path.basename(_fbx_file))
        if _errors:
            _errors = list(set(_errors))

        BaseFile().open_file(__current_file)

        return _errors
