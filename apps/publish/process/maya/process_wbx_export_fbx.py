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

from apps.publish.process.maya.process_export_fbx import Porcess_Export

import lib.maya.process.export_fbx as _fbx_common
import lib.maya.analysis.analyze_fbx as analyze_fbx
import maya.cmds as cmds


class Porcess_WBXFbx_Export(Porcess_Export):
    def __init__(self, TaskData, down=True, up=False):
        Porcess_Export.__init__(self, TaskData, down=down, up=up)
        self.taskdata = TaskData
        self._work_data_dir = TaskData.work_data_dir
        self._publish_data_dir = TaskData.publish_data_dir
        self._entity_name = TaskData.entity_name

        self._work_fbx_dir = '{}/fbx'.format(self._work_data_dir)
        self._publish_fbx_dir = '{}/fbx'.format(self._publish_data_dir)
        self._asset_type = TaskData.asset_type
        self._down = down
        self._up = up
        self._mb_fbx_json = '{}.{}.MB.json'.format(self._entity_name, self._task_name)

    def export_wbx_fbx(self):
        u"""
        导出rig fbx
        @return:
        """
        # 导出maya 文件
        # _file_dict = self._export_files()
        if self._asset_type.lower() in ['environment']:
            _fbx_dict = self._get_fbx_info()

            # 导出fbx
            _fbxfiles = self._export_wbx_fbx(_fbx_dict)
            # 导出fbx
            # _fbx_dict = self._export_fbx_up()
            # # 修复fbx
            # self._fix_rig_fbx(_fbx_dict)
            # 打包上传字典
            if _fbxfiles:
                return self.package_work_publish(_fbxfiles, _jsonfile=self._mb_fbx_json, _key='mbfbx')

    def _export_wbx_fbx(self, _dict):
        u"""
        导出fbx
        :param _dict: 例{file01:[objs01,fbx01]}
        :return:
        """
        _list = []
        if _dict:
            for _fbx_file, _objs in _dict.items():
                try:
                    self._export_fbx(_objs, _fbx_file)
                    _list.extend([_fbx_file])
                except:
                    pass
        return _list

    def _get_fbx_info(self):
        u"""
        fbx信息
        :return:
        """
        _fbx_file = '{}/{}.fbx'.format(self._work_fbx_dir, self._entity_name)
        return {_fbx_file: self.get_roots()}

    def get_roots(self):
        import maya.cmds as cmds
        transformlist = cmds.ls(transforms=True, long=True)
        rootlist = []
        if transformlist:
            for tr in transformlist:
                _inf = tr.split('|')
                if _inf and len(_inf) <= 2 and tr not in rootlist:
                    rootlist.append(tr)

        exlist = ['|persp', '|top', '|front', '|side']
        if rootlist:
            return list(set(rootlist) - set(exlist))

    def _export_fbx(self, _exportobjs, _exportfile):
        u"""
        导出fbx
        @param _exportobjs: 需要导出fbx的物体列表
        @param _exportfile: 导出的fbx文件
        @return:
        """

        # 导出fbx

        return _fbx_common.export_fbx(_exportobjs, _exportfile, hi=1, warning=0)


if __name__ == '__main__':
    import sys

    sys.path.append('Z:/dev/Ide/Python/2.7.11/Lib/site-packages')
    import method.shotgun.get_task as get_task

    _filename = cmds.file(q=1, exn=1)
    taskdata = get_task.TaskInfo(_filename, 'X3', 'maya', 'version')
    _handle = Porcess_WBXFbx_Export(taskdata)
    # _ad = _handle._get_rig_ad()
    # # 转换{ad}变量
    # _fbx_info = _handle._cover_variable_info('{ad}', _ad, _fbx_info)
    print(_handle._get_fbx_info())
    _dict = _handle.export_wbx_fbx()
