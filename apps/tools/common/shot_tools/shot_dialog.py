# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       : shot_dialog
# Describe   : 说明描述
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2023/3/13__17:29
# -------------------------------------------------------
try:
    from PySide2 import QtCore
    from PySide2.QtWidgets import *
    from PySide2.QtGui import *
    from PySide2.QtCore import *
except:
    from Qt.QtWidgets import *
    from Qt.QtGui import *
    from Qt.QtCore import *

from lib.common import fileio
import sys


from apps.tools.common.shot_tools.base_dialog import ShotAssetInfoDialog

from apps.tools.common.shot_tools.resources import resources


class ShotInfoDialog(ShotAssetInfoDialog):
    __TITLE__ = u"动画组装工具"

    def __init__(self, entity_list=[], dcc='motionbuilder'):
        super(ShotInfoDialog, self).__init__(entity_list, dcc)
        self.pushButtonReference.clicked.connect(self.ref_files)
        res_stylesheet = resources.get("qss", "shot_asset_info.qss")
        style = fileio.read(res_stylesheet)
        self.dcc = dcc
        self.setStyleSheet(style)

    def ref_files(self):
        '''
        参考选中的资产文件
        :return:
        '''

        _assets = self.get_checked_asset_info()

        if self.dcc in ['motionbuilder']:
            import apps.tools.common.shot_tools.action.action_motionbuilder as refaction
            refaction.action(_assets)

        # if not _assets:
        #     tools.show_messagebox("W", u"你似乎什么都没有选")
        #     return
        # print _assets
        # # ret_value = process_animation_reference.ProcessAnimationReference(_assets).reference_file_animation()
        # print ret_value

    def get_checked_asset_info(self):
        '''
        拼装面板中选中项的资产信息
        :return:
        '''
        _rows = self.tableWidgetAssetInfoList.rowCount()

        info = []
        for i in range(_rows):
            # print(self.tableWidgetAssetInfoList.cellWidget(i, 0).isChecked())
            # print(self.tableWidgetAssetInfoList.item(i, 2).text())
            # print(self.tableWidgetAssetInfoList.item(i, 4).text())
            # print(self.tableWidgetAssetInfoList.item(i, 8).text())
            #
            # print(self.tableWidgetAssetInfoList.cellWidget(i, 6).currentText())
            # print(self.tableWidgetAssetInfoList.item(i, 7).text())
            if self.tableWidgetAssetInfoList.cellWidget(i, 0).isChecked():
                ele_dict = dict()
                ele_dict["name"] = self.tableWidgetAssetInfoList.item(i, 2).text()
                ele_dict["asset_type"] = self.tableWidgetAssetInfoList.item(i, 4).text()
                ele_dict["path"] = self.tableWidgetAssetInfoList.item(i, 8).text()
                ele_dict["task_name"] = self.tableWidgetAssetInfoList.cellWidget(i, 6).currentText()
                ele_dict["asset_state"] = self.tableWidgetAssetInfoList.item(i, 7).text()
                ele_dict["project_name"] = self.project_name
                ele_dict["entity"] = self.entity['entity']
                info.append(ele_dict)
        return info


# if __name__ == '__main__':
#     entity_list = [{
#         'due_date': None,
#         'sg_custom_totalrealwork': None,
#         'project': {'type': 'Project', 'id': 114, 'name': 'X3'},
#         'entity.Asset.sg_asset_type': None,
#         'entity.Shot.sg_sequence.Sequence.code': 'CutScene_ML_C10S1',
#         'entity': {'type': 'Shot', 'id': 2910, 'name': 'CutScene_ML_C10S1_S01_P01'},
#         'content': 'cts_rough',
#         'start_date': None,
#         'sg_status_list': 'rev',
#         'est_in_mins': None,
#         'step': {'type': 'Step', 'id': 273, 'name': 'cts'},
#         'task_assignees': [],
#         'type': 'Task',
#         'id': 168479
#     }]
#
#     app = QApplication(sys.argv)
#     win = ShotInfoDialog(entity_list, dcc='motionbuilder')  # create an window
#
#     win.show()  # show window
#     sys.exit(app.exec_())
