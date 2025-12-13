# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       : copy_publish_file
# Describe   : 说明描述
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2022/12/5__15:03
# -------------------------------------------------------
import sys

sys.path.append('Z:/dev')
import database.shotgun.core.sg_base as sg_base


import database.shotgun.tools.actionitem.action_item_server as action_item_server
import shutil
import os
import time

BASEDIR = 'E:/work/Testbed-Main'

# try:
#     from Pyside2 import QtWidgets
# except:
#     from PyQt5 import QtWidgets


sys.path.append(r'Z:\dev\Ide\Python\2.7.18-x64\Lib\site-packages')

try:

    from PySide2.QtWidgets import QApplication, QWidget, QFileDialog
except:
    from PyQt5.QtWidgets import QApplication, QWidget, QFileDialog


class CopyPublishFile(object):

    def __init__(self):

        self.project = sys.argv[1]
        self.select_ids = sys.argv[2].split(',')
        self.entity_type = sys.argv[3]
        self.sg = action_item_server.action_login()

    def copy_pulish_files(self):
        u"""
        复制
        """
        _list = []
        _publish_files = self._get_publishs
        _dec = self._local_dir
        print(_dec)
        if _publish_files:
            for _scr in _publish_files:
                if _scr and os.path.exists(_scr):
                    _result = self._copyfile(_scr, _dec)
                    _dec_file = '{}/{}'.format(_dec, os.path.basename(_scr))
                    time.sleep(1)
                    if _result and _result == True and os.path.exists(_dec_file):
                        _list.append(_dec_file)
        print(_list)
        if _list:
            _list = list(set(_list))
            print('Please check that the following files have been updated')
            for _file in _list:
                print(_file)

    def judge_publish_copy(self, _publish_id, _publishtype=['Motion Builder FBX'],
                           asset_typs=['item', 'enemy', 'weapon']):
        u"""
        :param asset_typs: 资产类型列表
        :return:
        """
        _result = True
        _entity_id = self._get_entitys(_publish_id)
        if _entity_id and self._get_asset_type(_entity_id['id']) not in asset_typs:
            _publish_type = sg_base.select_entity(self.sg, "PublishedFile", int(_publish_id), ['published_file_type'])[
                'published_file_type']
            if _publish_type and _publish_type['name'] in _publishtype:
                _result = False
        return _result

    def _get_entitys(self, _publish_id):
        u"""
        获得实体
        """
        try:
            return sg_base.select_entity(self.sg, self.entity_type, int(_publish_id), ["entity"])['entity']
        except:
            return None

    def _get_asset_type(self, _entity_id):
        u"""

        :param asset_typs:
        :return:
        """
        try:
            return sg_base.select_entity(self.sg, 'Asset', _entity_id, ['sg_asset_type'])['sg_asset_type']
        except:
            return None

    def _copyfile(self, scr, dec):
        u"""
        复制文件
        """
        try:
            shutil.copy2(scr, dec)
            return True
        except:
            return False

    @property
    def _local_dir(self):
        # _dir = BASEDIR
        _dir = DirectorySelector().open_dialog()
        if not os.path.exists(_dir):
            os.makedirs(_dir)
        return _dir

    @property
    def _get_publishs(self):
        u"""
        获得publish 文件列表
        """
        if self.select_ids:
            # for id in self.select_ids:
            #     print(self._get_publish_file(int(id), self.entity_type) )
            return [self._get_publish_file(int(entity_id), self.entity_type) for entity_id in self.select_ids if
                    (entity_id and self.judge_publish_copy(entity_id) == True)]

    def _get_publish_file(self, entity_id, entity_type):
        u"""
        获取publish 文件
        """
        try:
            return sg_base.select_entity(self.sg, entity_type, entity_id, ['path'])['path']['local_path']
        except:
            return


class DirectorySelector(QWidget):
    def __init__(self):
        super(DirectorySelector, self).__init__()

    def open_dialog(self):
        options = QFileDialog.Options()
        directory = QFileDialog.getExistingDirectory(self, "Select Directory", BASEDIR, options=options)
        if directory:
            return directory


if __name__ == '__main__':

    app = QApplication(sys.argv)
    selector = DirectorySelector()

    CopyPublishFile().copy_pulish_files()
    sys.exit(app.exec_())
    # dir=QtWidgets.QFileDialog.getExistingDirectory(self,u'选择文件夹', 'E:/work/Testbed-Main')
    # print(dir)

    # sg = sg_analysis.Config().login()
    # print(sg_base.select_entity(sg, 'Asset', 19620, ['sg_asset_type'])['sg_asset_type'])
#
# _enity_id = ['94414']
# _enity_type = "PublishedFile"
# sys.argv = ['copy_publish_file.py', 'Testbed-Main', ','.join([str(_id) for _id in _enity_id]), _enity_type]
# _handle = CopyPublishFile()
# print(_handle.judge_publish_copy(122151))
# sg=sg_analysis.Config().login()
# _publish_id = 94414

# filters=[['id', 'is', _publish_id]]
# version_fields=['published_file_type']
# print(sg.find("PublishedFile", filters, version_fields))

#     print(_handle._get_publishs)

#     print(_handle._get_entitys())
#     print(_handle._judge_asset_type(14289))
