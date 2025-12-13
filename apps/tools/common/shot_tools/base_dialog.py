# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       : base_dialog
# Describe   : 基础面板
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2023/3/13__17:33
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

import os
import sys

from functools import partial
import threading
import tempfile
import urllib
import getpass
from lib.common import yamlio

import method.shotgun.shotgunfuns as shotgunfuns

reload(shotgunfuns)
from method.shotgun.shotgunfuns import ShotgunClass

import apps.tools.common.shot_tools.config as config

import method.common.dir as _dir

PUBLISHTYPE = {'motionbuilder': ['Motion Builder FBX'], 'maya': ['Maya Scene']}

CMAERANAME='camera_drama'
class ShotAssetInfoDialog(QDialog):
    UpdateAssetInfoSignal = QtCore.Signal(list)
    __TITLE__ = "组装工具"

    def __init__(self, entity_list=[], dcc='motionbuilder'):
        super(ShotAssetInfoDialog, self).__init__()

        self.entity = entity_list[0]
        self.setup()
        self.init_data()

        self.asset_task_dict = dict()

        self.project_name = self.entity['project']['name']
        # "Asset"|"Shot"
        self.entity_type = self.entity['entity']['type']
        self.entity_name = self.entity['entity']['name']
        self.task_name = self.entity['content']
        self.user_name = getpass.getuser()
        self.task_shotgun = ShotgunClass()
        self.dcc = dcc
        self._type = PUBLISHTYPE[self.dcc.lower()]
        # read config file
        config_path = config.get("config/projects", self.project_name, 'shot_asset_info.yml')
        # 如果文件不存在，则读取common下的配置
        if not os.path.exists(config_path):
            config_path = config.get("config/common", 'shot_asset_info.yml')

        self.config = yamlio.read2(config_path)

        # init tableWidget ui data
        self.set_shot_info()
        self.update_shot_asset_info()

        self.resize(1000, 650)

        self.setWindowTitle("项目名称：[{}] 镜头名称：[{}] 任务名称：[{}]".format(self.project_name, self.entity_name, self.task_name))

    def init_data(self):
        self.pushButtonReload.clicked.connect(self.update)
        self.UpdateAssetInfoSignal.connect(self.update_asset_info)
        self.pushButtonSelectAll.clicked.connect(self.select_all)
        self.pushButtonSelectNone.clicked.connect(self.select_none)
        self.tableWidgetAssetInfoList.cellDoubleClicked.connect(self.image_clicked_process)

        self.tableWidgetAssetInfoList.setColumnCount(9)
        self.tableWidgetAssetInfoList.setRowCount(0)

        self.tableWidgetAssetInfoList.setHorizontalHeaderItem(0, QTableWidgetItem("选择"))
        self.tableWidgetAssetInfoList.setHorizontalHeaderItem(1, QTableWidgetItem("缩略图"))
        self.tableWidgetAssetInfoList.setHorizontalHeaderItem(2, QTableWidgetItem("资产名称"))
        self.tableWidgetAssetInfoList.setHorizontalHeaderItem(3, QTableWidgetItem("资产备注"))
        self.tableWidgetAssetInfoList.setHorizontalHeaderItem(4, QTableWidgetItem("类型"))
        self.tableWidgetAssetInfoList.setHorizontalHeaderItem(6, QTableWidgetItem("任务选择"))
        self.tableWidgetAssetInfoList.setHorizontalHeaderItem(7, QTableWidgetItem("任务状态"))
        self.tableWidgetAssetInfoList.setHorizontalHeaderItem(8, QTableWidgetItem("上传文件源路径"))

        self.tableWidgetAssetInfoList.setIconSize(QSize(75, 75))
        self.tableWidgetAssetInfoList.setColumnWidth(0, 35)
        self.tableWidgetAssetInfoList.setColumnWidth(1, 75)
        self.tableWidgetAssetInfoList.setColumnWidth(2, 100)
        self.tableWidgetAssetInfoList.setColumnWidth(3, 150)
        self.tableWidgetAssetInfoList.setColumnWidth(5, 30)

        self.tableWidgetAssetInfoList.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tableWidgetAssetInfoList.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tableWidgetAssetInfoList.setCornerButtonEnabled(True)
        self.tableWidgetAssetInfoList.horizontalHeader().setSectionsClickable(False)
        self.tableWidgetAssetInfoList.verticalHeader().setVisible(False)
        self.tableWidgetAssetInfoList.horizontalHeader().setVisible(True)
        self.tableWidgetAssetInfoList.setFrameShape(QFrame.StyledPanel)
        self.tableWidgetAssetInfoList.horizontalHeader().setStretchLastSection(True)
        self.tableWidgetAssetInfoList.setEditTriggers(QAbstractItemView.NoEditTriggers)

        # hide the source path column
        self.tableWidgetAssetInfoList.setColumnHidden(5, True)
        # self.tableWidgetAssetInfoList.setColumnHidden(8, True)

        # self.tableWidgetAssetInfoList.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        # self.tableWidgetAssetInfoList.customContextMenuRequested[QtCore.QPoint].connect(self.right_context_menu)

    def set_shot_info(self):
        cut_in_text = u"<span style='font-size:28pt'>%s</span>" % " 迭代R:".decode("utf8")
        cut_duration_text = u"<span style='font-size:28pt'>%s</span>" % "   镜头备注:".decode("utf8")
        cut_in = ""
        cut_duration = ""
        if self.entity_type == "Shot":
            # 设置镜头名称，Cut in Cut Duration等等
            entity = self.task_shotgun.get_shot_frame(self.project_name, self.entity_name)
            if entity:
                cut_in_data = entity['sg_text_1']
                cut_duration_data = entity['description'].decode("utf8")
            else:
                cut_in_data = ''
                cut_duration_data = ''

            cut_in = u"<span style='font-size:30pt'><font color = green>%s</font></span>" % cut_in_data
            cut_duration = (u"<span style='font-size:30pt'><font color = red>%s</font></span>" % cut_duration_data)

        # shot_info = cut_in_text + cut_in + cut_duration_text + cut_duration
        shot_info = cut_in_text + cut_in + cut_duration_text + cut_duration

        self.labelShotInfo.setText(shot_info)

    def update_shot_asset_info(self):
        project_name, entity_name, task_name = self.project_name, self.entity_name, self.task_name

        self.asset_task_dict.clear()
        asset_list = []
        _asset_type = None
        if self.entity_type == "Asset":
            _assets_list = self.task_shotgun.get_asset_subassets_list(project_name, entity_name)
            asset_list = _assets_list['assets']
            _asset_type = _assets_list['sg_asset_type']
        elif self.entity_type == "Shot":
            asset_list = self.task_shotgun.get_shot_assets_list(project_name, entity_name)


            # 读取配置文件中的relation_asset_type，并追加入asset_list
            relation_asset_type_list = self.read_shot_asset_relation_asset_type('shot', task_name)
            if relation_asset_type_list:
                for _asset_type_temp in relation_asset_type_list:
                    asset_by_type_list = self.task_shotgun.get_assets_list_form_type(project_name, _asset_type_temp)

                    asset_by_type_list_new = list()

                    for asset_by_type in asset_by_type_list:
                        asset_by_type_new = dict()

                        for key, value in asset_by_type.items():
                            key_new = 'asset.Asset.{}'.format(key)
                            asset_by_type_new[key_new] = asset_by_type[key]
                        if asset_by_type_new:
                            asset_by_type_list_new.append(asset_by_type_new)
                    if asset_by_type_list_new:
                        asset_list += asset_by_type_list_new
        #camera
        _camerlist=self.task_shotgun.get_camera_assets_list(self.project_name,CMAERANAME)
        if _camerlist:
            asset_list.extend(_camerlist)
        if asset_list:

            asset_info_list = []
            for asset in asset_list:

                asset_publish_file_path = ''
                asset_task_status = ''
                latest_version_thumbnail_image = ''
                latest_version_image_path = ''

                if self.entity_type == "Asset":
                    asset_entity = self.task_shotgun.get_asset_entity(self.project_name, asset['name'])
                    asset_name = asset_entity['code']
                    # asset_id = asset_entity['id']
                    asset_type = asset_entity['sg_asset_type']
                    asset_published_file_entity_list = asset_entity['sg_published_files']
                    asset_task_entity_list = asset_entity['tasks']
                    asset_task_name_dict = self.read_shot_asset_task_name("asset", task_name, asset_type,
                                                                          target="asset_link_up")

                    if not asset_task_name_dict or asset_type not in asset_task_name_dict.keys():
                        continue

                    asset_task_name_list = asset_task_name_dict[asset_type]
                    if not asset_task_name_list:
                        continue

                else:
                    try:
                        asset_name = asset['asset.Asset.code']
                        asset_id = asset['asset.Asset.id']
                        asset_chinesename = asset['asset.Asset.description']
                        asset_type = asset['asset.Asset.sg_asset_type']
                        asset_published_file_entity_list = asset['asset.Asset.sg_published_files']
                        asset_task_entity_list = asset['asset.Asset.tasks']

                        asset_task_name_list = self.read_shot_asset_task_name("shot", task_name, asset_type,
                                                                              target="asset_up")
                    except:

                        asset_name = asset['code']
                        asset_id = asset['id']
                        asset_chinesename = asset['description']
                        asset_type = asset['sg_asset_type']
                        asset_published_file_entity_list = asset['sg_published_files']
                        asset_task_entity_list = asset['tasks']

                        asset_task_name_list = self.read_shot_asset_task_name("shot", task_name, asset_type,
                                                                              target="asset_up")


                    if not asset_task_name_list:
                        continue


                # # 检测任务是否在列表中，只保留存在的任务
                # if asset_task_entity_list:
                #     asset_task_name_list_temp = []
                #     for asset_task_entity in asset_task_entity_list:
                #         if asset_task_name_list:
                #             asset_task_name_temp = asset_task_entity['name']
                #             if asset_task_name_temp in asset_task_name_list:
                #                 asset_task_name_list_temp.append(asset_task_name_temp)
                #
                # asset_task_name_list = asset_task_name_list_temp

                if asset_task_entity_list:

                    for asset_task_entity in asset_task_entity_list:
                        asset_task_dict_key = asset_name + "." + asset_task_entity['name']
                        self.asset_task_dict[asset_task_dict_key] = asset_task_entity['id']

                        if asset_task_name_list and (asset_task_entity['name'] == asset_task_name_list[0] or asset_task_entity['name'] in ['cam_drama']):
                            asset_task_id = asset_task_entity['id']
                            latest_version_thumbnail_image, asset_task_status = self.get_latest_version_image_path(
                                self.project_name, asset_name, asset_task_id)

                            asset_published_file = self.task_shotgun.get_published_file_src_path2(asset_task_id)
                            if asset_published_file:
                                # print(asset_published_file)

                                asset_publish_file_path = self.select_publishdata_path(asset_published_file,type=self._type)

                asset_info = [latest_version_thumbnail_image,
                              asset_name,
                              asset_chinesename,
                              asset_type,
                              asset_publish_file_path,
                              asset_task_name_list,
                              asset_task_status,
                              asset_publish_file_path]
                asset_info_list.append(asset_info)

            self.tableWidgetAssetInfoList.setRowCount(len(asset_info_list))
            self.UpdateAssetInfoSignal.emit(asset_info_list)

    def read_shot_asset_relation_asset_type(self, type='shot', current_task='', key='relation_asset_type'):
        if type == "shot":
            dict_shot = self.config[type]
            if current_task in dict_shot.keys():
                dict_shot_asset = dict_shot[current_task]

                if key in dict_shot_asset.keys():
                    dict_shot_relation_asset_type = dict_shot_asset[key]
                    return dict_shot_relation_asset_type
        return []

    def read_shot_asset_task_name(self, type, current_task, asset_type=None, target=None):
        if type == "asset":
            dict_asset = self.config[type]
            dict_asset_task = dict_asset[asset_type]
            if current_task in dict_asset_task.keys():
                dict_asset_asset = dict_asset_task[current_task]
                if target in dict_asset_asset.keys():
                    asset_asset_task_list = dict_asset_asset[target]
                    if asset_asset_task_list:
                        return asset_asset_task_list
        elif type == "shot":
            dict_shot = self.config[type]
            if current_task in dict_shot.keys():
                dict_shot_asset = dict_shot[current_task]

                if asset_type:
                    # 如果是读取Asset字段，需要asset type
                    if asset_type in dict_shot_asset.keys():
                        dict_shot_asset_type = dict_shot_asset[asset_type]
                        if target in dict_shot_asset_type.keys():
                            shot_asset_task_list = dict_shot_asset_type[target]
                            if shot_asset_task_list:
                                return shot_asset_task_list
                else:
                    # 否则读取Shot字段
                    if target in dict_shot_asset.keys():
                        shot_asset_task_list = dict_shot_asset[target]
                        if shot_asset_task_list:
                            return shot_asset_task_list
        return []

    def update_table_item(self, asset_info_list):
        row = -1
        for asset_info in asset_info_list:
            row += 1
            column = 0
            check_box = QCheckBox()
            check_box.setCheckState(QtCore.Qt.Unchecked)
            self.tableWidgetAssetInfoList.setCellWidget(row, column, check_box)
            self.tableWidgetAssetInfoList.setRowHeight(row, 75)

            for item_name in asset_info:
                column += 1
                if column == 1:


                    assert_image = QTableWidgetItem()
                    assert_image_icon = QIcon(item_name)
                    assert_image_icon.addFile(item_name, size=QSize(75, 75))
                    assert_image.setIcon(assert_image_icon)
                    self.tableWidgetAssetInfoList.setItem(row, column,assert_image)
                elif column == 6:
                    combobox = QComboBox()
                    combobox.addItems(item_name)
                    combobox.setProperty("row", row)
                    combobox.setProperty("col", column)
                    self.tableWidgetAssetInfoList.setCellWidget(row, column, combobox)
                    combobox.currentIndexChanged.connect(partial(self.combobox_changer, combobox))

                elif column == 8:

                    latest_version_image_path_item = QTableWidgetItem(item_name)
                    self.tableWidgetAssetInfoList.setItem(row, column, latest_version_image_path_item)
                else:
                    item = QTableWidgetItem(item_name)

                    self.tableWidgetAssetInfoList.setItem(row, column, item)

    @QtCore.Slot(int, int)
    def image_clicked_process(self, row, col):
        if col == 1:
            image_path = self.tableWidgetAssetInfoList.item(row, 1).text()
            if image_path:
                os.startfile(image_path)

    @QtCore.Slot(int)
    def combobox_changer(self, combobox, index):
        current_row = combobox.property("row")
        asset_name = self.tableWidgetAssetInfoList.item(current_row, 2).text()
        asset_task_name = self.tableWidgetAssetInfoList.cellWidget(current_row, 6).currentText()
        asset_task_dict_key = asset_name + "." + asset_task_name
        if asset_task_dict_key in self.asset_task_dict:
            asset_publish_file_path = ''
            asset_task_id = self.asset_task_dict[asset_task_dict_key]
            thumbnail_image, asset_task_status = self.get_latest_version_image_path(
                self.project_name, asset_name, asset_task_id)

            asset_published_file = self.task_shotgun.get_published_file_src_path2(asset_task_id)

            if asset_published_file:
                asset_publish_file_path = self.select_publishdata_path(asset_published_file, type=self._type)
            assert_image = QTableWidgetItem()
            assert_image_icon = QIcon(thumbnail_image)
            assert_image_icon.addFile(thumbnail_image, size=QSize(75, 75))
            assert_image.setIcon(assert_image_icon)





            self.tableWidgetAssetInfoList.setItem(current_row, 1, assert_image)
            self.tableWidgetAssetInfoList.item(current_row, 5).setText(asset_publish_file_path)
            self.tableWidgetAssetInfoList.item(current_row, 7).setText(asset_task_status)
            self.tableWidgetAssetInfoList.item(current_row, 8).setText(asset_publish_file_path)
        else:
            assert_image = QTableWidgetItem()
            assert_image_icon = QIcon("")
            assert_image_icon.addFile("", size=QSize(75, 75))
            assert_image.setIcon(assert_image_icon)
            self.tableWidgetAssetInfoList.setItem(current_row, 1, assert_image)
            self.tableWidgetAssetInfoList.item(current_row, 5).setText("")
            self.tableWidgetAssetInfoList.item(current_row, 7).setText("")
            self.tableWidgetAssetInfoList.item(current_row, 8).setText("")

    @QtCore.Slot()
    def select_all(self):
        self.table_widget_checkbox_state(True)

    @QtCore.Slot()
    def select_none(self):
        self.table_widget_checkbox_state(False)

    @QtCore.Slot(list)
    def update_asset_info(self, asset_info_list):
        self.update_table_item(asset_info_list)

    @QtCore.Slot()
    def update(self, *args, **kwargs):
        t = threading.Thread(target=self.update_shot_asset_info)
        t.setDaemon(True)
        t.start()

    def table_widget_checkbox_state(self, is_checked):
        rows = self.tableWidgetAssetInfoList.rowCount()
        for row in range(rows):
            table_widget_item = self.tableWidgetAssetInfoList.cellWidget(row, 0)
            if is_checked:
                table_widget_item.setCheckState(QtCore.Qt.Checked)
            else:
                table_widget_item.setCheckState(QtCore.Qt.Unchecked)

    @QtCore.Slot(QPoint)
    def right_context_menu(self, pos):
        '''
        this is the right context menu for tablewidget item which you selected
        it will call the function below
        '''
        pop_menu = QMenu()
        if self.tableWidgetAssetInfoList.itemAt(pos):
            self.show_right_context_menu(pop_menu)
        pop_menu.exec_(QCursor.pos())

    def show_right_context_menu(self, pop_menu):
        pop_menu.addAction(QAction(u'导入|参考资产', self, triggered=self.right_menu_process))

    def right_menu_process(self):
        dict_data = self.get_tablewidget_item_data()
        # pprint(dict_data)

    def get_tablewidget_selected_item_data(self):
        rows = self.tableWidgetAssetInfoList.rowCount()
        for current_row in range(rows):
            is_checked = self.tableWidgetAssetInfoList.cellWidget(current_row, 0).isChecked()
            if is_checked:
                check_status = self.tableWidgetAssetInfoList.cellWidget(current_row, 0).isChecked()
                asset_name = self.tableWidgetAssetInfoList.item(current_row, 2).text()
                asset_type = self.tableWidgetAssetInfoList.item(current_row, 4).text()
                asset_src_path = self.tableWidgetAssetInfoList.item(current_row, 5).text()
                asset_task_name = self.tableWidgetAssetInfoList.cellWidget(current_row, 6).currentText()
                asset_task_status = self.tableWidgetAssetInfoList.item(current_row, 7).text()

                path_temps = asset_src_path.split('|')
                path = []
                for path_temp in path_temps:
                    if asset_task_name in path_temp:
                        path.append(path_temp)
                result_dict = {
                    "check_status": check_status,
                    "asset_name": asset_name,
                    "asset_type": asset_type,
                    "asset_src_path": path,
                    "asset_task_name": asset_task_name,
                    "asset_task_status": asset_task_status
                }

    def get_tablewidget_item_data(self):
        current_row = self.tableWidgetAssetInfoList.currentRow()

        check_status = self.tableWidgetAssetInfoList.cellWidget(current_row, 0).isChecked()
        asset_name = self.tableWidgetAssetInfoList.item(current_row, 2).text()
        asset_type = self.tableWidgetAssetInfoList.item(current_row, 4).text()
        asset_src_path = self.tableWidgetAssetInfoList.item(current_row, 8).text()
        asset_task_name = self.tableWidgetAssetInfoList.cellWidget(current_row, 6).currentText()
        asset_task_status = self.tableWidgetAssetInfoList.item(current_row, 7).text()

        path_temps = asset_src_path.split('|')
        path = []
        for path_temp in path_temps:
            if asset_task_name in path_temp:
                path.append(path_temp)
        result_dict = {
            "check_status": check_status,
            "asset_name": asset_name,
            "asset_type": asset_type,
            "asset_src_path": path,
            "asset_task_name": asset_task_name,
            "asset_task_status": asset_task_status
        }
        return result_dict

    def select_publishdata_path(self, publishdata, type=['Motion Builder FBX']):
        _path = []
        _cover_path = ''
        if publishdata:
            for i in range(len(publishdata)):
                publishtype = publishdata[i]['published_file_type']['name']
                if publishtype in type:
                    _locafile = publishdata[i]['path']['local_path_windows']
                    _path.extend([_locafile])
        if _path:
            _path = list(set(_path))

        return self.cover_list_str_path(_path)

    def cover_list_str_path(self, pathlist):
        _path = ''
        if pathlist:
            for i in range(len(pathlist)):
                if i == 0:
                    _path = pathlist[i]
                else:
                    _path = '{}\n{}'.format(_path, pathlist[i])
        return _path

    def get_image_path(self, image_name, url):
        if url:
            temp_image_file = tempfile.gettempdir() + "\\" + image_name + ".jpg"
            urllib.urlretrieve(url, temp_image_file)
            return temp_image_file
        else:
            return ""

    def get_latest_version_image_path(self, project_name, asset_name, task_id):
        filters = [
            ['project.Project.name', 'is', project_name],
            ['code', 'is', asset_name]
        ]

        field = ['id']

        _entity = self.task_shotgun.sg_login.find_one("Asset", filters, fields=field)
        if not _entity:
            return '', '', ''
        # src_image_path = convert_drive.ip2drive(version_entity['sg_src_path'], "\\\\10.10.201.151\\share\product")

        asset_id = _entity['id']
        asset_task_status = self.task_shotgun.select_entity_fields('Task', task_id, ['sg_status_list'])[
            'sg_status_list']
        _path = _dir.get_localtemppath('thumbnail')
        if not os.path.exists(_path):
            os.makedirs(_path)

        thumbnail_path = '{}/{}.jpg'.format(_path, asset_name)
        if not os.path.exists(thumbnail_path):
            thumbnail_path = self.task_shotgun.down_entity_thumbnail('Asset', asset_id, thumbnail_path)
        return thumbnail_path, asset_task_status

    def read_asset_task_name(self, shot_step, asset_type):
        asset_task_name_list = []
        asset_task_name = self.config[shot_step][asset_type]
        if type(asset_task_name).__name__ == 'list':
            for task_name in asset_task_name:
                asset_task_name_list.append(task_name.keys()[0])
        else:
            asset_task_name_list.append(asset_task_name)
        return asset_task_name_list

    def read_asset_path_return_type(self, shot_step, asset_type, asset_task_name):
        task_name = self.config[shot_step][asset_type]
        return_type = []
        if type(task_name).__name__ == 'dict':
            return_type = task_name[asset_task_name]
        else:
            return_type.append(task_name)
        return return_type

    def setup(self):
        self.widget = QWidget()
        self.widget.setGeometry(QRect(61, 31, 300, 200))
        self.widget.setObjectName("widget")

        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.setLayout(self.gridLayout)

        self.tabWidget = QTabWidget()
        self.tabWidget.setObjectName("tabWidget")

        self.tabInfo = QWidget()
        self.tabInfo.setObjectName("tabInfo")
        self.gridLayout_2 = QGridLayout(self.tabInfo)
        self.gridLayout_2.setObjectName("gridLayout_2")

        self.pushButtonSelectAll = QPushButton("全部选中")
        self.pushButtonSelectAll.setObjectName("pushButtonSelectAll")
        self.gridLayout_2.addWidget(self.pushButtonSelectAll, 2, 0, 1, 1)

        self.pushButtonSelectNone = QPushButton("全部取消")
        self.pushButtonSelectNone.setObjectName("pushButtonSelectNone")
        self.gridLayout_2.addWidget(self.pushButtonSelectNone, 2, 1, 1, 1)

        self.tableWidgetAssetInfoList = QTableWidget(self.tabInfo)
        self.tableWidgetAssetInfoList.setObjectName("tableWidgetAssetInfoList")
        self.gridLayout_2.addWidget(self.tableWidgetAssetInfoList, 0, 0, 1, 4)

        self.pushButtonReload = QPushButton("Reload")
        self.pushButtonReload.setObjectName("pushButtonReload")
        self.gridLayout_2.addWidget(self.pushButtonReload, 2, 2, 1, 1)

        self.pushButtonReference = QPushButton("导入|参考资产")
        self.gridLayout_2.addWidget(self.pushButtonReference, 2, 3, 1, 1)

        self.tabWidget.addTab(self.tabInfo, "资产列表")
        self.gridLayout.addWidget(self.tabWidget, 1, 0, 1, 4)

        self.labelShotInfo = QLabel("镜头信息:")
        self.labelShotInfo.setObjectName("labelShotInfo")
        self.gridLayout.addWidget(self.labelShotInfo, 0, 0, 1, 1)


if __name__ == '__main__':
    entity_list = [{
        'due_date': None,
        'sg_custom_totalrealwork': None,
        'project': {'type': 'Project', 'id': 114, 'name': 'X3'},
        'entity.Asset.sg_asset_type': None,
        'entity.Shot.sg_sequence.Sequence.code': 'CutScene_ML_C10S1',
        'entity': {'type': 'Shot', 'id': 2910, 'name': 'CutScene_ML_C10S1_S01_P01'},
        'content': 'cts_rough',
        'start_date': None,
        'sg_status_list': 'rev',
        'est_in_mins': None,
        'step': {'type': 'Step', 'id': 273, 'name': 'cts'},
        'task_assignees': [],
        'type': 'Task',
        'id': 168479
    }]

    if QApplication.instance() is None:
        app = QApplication(sys.argv)
    else:
        app = QApplication.instance()
    win = ShotAssetInfoDialog(entity_list,dcc='motionbuilder')  # create an window
    # print(win.self.read_shot_asset_relation_asset_type('shot', task_name))
#     # # print(win.entity)
    win.show()  # show window
    sys.exit(app.exec_())  # quit application，it wil release win instance
#     # project_name='X3'
    # entity_name='YG001S'
    # print(win.task_shotgun.get_shot_assets_list(project_name, entity_name))

    # app =QApplication(sys.argv)
    # 加载icon
