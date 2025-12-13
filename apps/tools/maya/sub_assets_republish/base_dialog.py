# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       : base_dialog
# Describe   : 说明描述
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2023/12/6__22:23
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

import sys
import uuid

from database.shotgun.fun import get_entity

from apps.tools.maya.sub_assets_republish.component import treegroups

reload(treegroups)

from apps.tools.maya.sub_assets_republish.commont import sg_fun
from apps.tools.maya.sub_assets_republish.component import center_widget

reload(center_widget)

from apps.tools.maya.sub_assets_republish.component import messagebox
reload(messagebox)


class SubAssetsInfoDialog(QDialog):
    UpdateAssetInfoSignal = QtCore.Signal(list)
    __TITLE__ = u"子资产【Republish】工具"

    def __init__(self, sg, task_id, project_name='X3'):
        super(SubAssetsInfoDialog, self).__init__()
        self.__sg = sg
        self.__task_id = task_id
        self.__entity = get_entity.TaskGetSgInfo(sg, self.__task_id).get_entity()
        self.__entity_id = self.__entity['id']
        self.__entity_name = self.__entity['name']
        self.__sub_assets_info = self. __get_asset_sub_assets_info()
        if not self.__sub_assets_info:
            messagebox.msgview(u"【{}】 shotgun缺少子资产信息,请检查".format(self.__entity_name), 1)
            raise Exception(u'【{}】shotgun缺少子资产信息,请检查'.format(self.__entity_name))
        self.__project_name = project_name
        self.__asset_data = sg_fun.get_asset_from_asset_name(self.__sg, self.__entity['name'], self.__project_name)
        # print 'self.__asset_data',self.__asset_data

        self.__builder()


    def __get_asset_sub_assets_info(self):
        try:
            return sg_fun.get_asset_sub_sub_assets_info(self.__sg, self.__entity_id)[self.__entity['name']]
        except:
            return {}

    def __builder(self):
        self.setWindowTitle(self.__TITLE__)

        self.setWindowFlags(Qt.Window)
        self.setModal(True)
        self.setWindowModality(Qt.WindowModal)

        self.layout = QHBoxLayout(self)
        self._setup()

        self.layout.addWidget(self.left_widget)
        self.layout.addWidget(self.center_widget)
        # self.layout.addLayout(self.right_layout)

        # self._setup()
        # self.layout_active = QVBoxLayout(self)
        # self.layout_active.addLayout(self.list_layout)
        # self.layout_active.addLayout(self.radio_layout)
        # self.layout_active.addWidget(self.link_pushButton)
        #
        # # self.layout_active.addWidget(self.Export_pushButton)
        # self.layout_active.addWidget(self.reload_pushButton)
        # self.layout_active.addWidget(self.clear_link_pushButton)

    def _setup(self):
        '''
        初始化各个组件
        :return:
        '''
        # self.left_layout= QVBoxLayout()
        self.left_widget = treegroups.TreeGroups(self.__sub_assets_info)
        # self.left_widget.setFixedWidth(300)
        # self.left_widget.setAcceptDrops(False)
        # self.left_layout.addWidget(self.left_widget)
        #
        # center_widget = CenterWidget(sg, asset_data)

        # self.center_layout = QVBoxLayout()
        #
        self.center_widget = center_widget.CenterWidget(self.__sg, [])

        # self.center_layout.addWidget(self.center_widget)

        # self.right_layout = QVBoxLayout()
        # self.right_widget = QFrame()
        # self.right_widget.setFixedWidth(250)
        # self.right_widget.setLayout(QVBoxLayout())
        # self.right_widget.layout().setAlignment(Qt.AlignTop)

        # # 设置信号方式,点击左侧图标，击发相关信息。
        self.left_widget.itemPressed.connect(self.get_tree_signal)
        # self.center_widget.item_pressed_signal.connect(self.set_info_to_rightwidget)

    def get_tree_signal(self):
        '''
        点击树目录之后，运行此函数
        槽函数
        :return: None
        '''
        tree_widget_item = self.left_widget.presse_widget_item
        data = tree_widget_item.data(0, Qt.UserRole)

        text = tree_widget_item.text(0)

        asset_data = sg_fun.get_asset_from_asset_name(self.__sg, text, self.__project_name)

        # self.center_widget = center_widget.CenterWidget(self.__sg, [asset_data])

        self.center_widget.update_flow_view([asset_data])

        self.center_widget.current_item_id = asset_data['id']

        self.center_widget.spliter_asset()

    def cover_info(self, info):
        '''
        覆盖信息
        :param info:
        :return:
        '''
        if not info:
            return
        id_dict = {}
        sub_info = {}
        __dict = {}
        for k, v in info.items():
            if v and isinstance(v, list):
                for asset in v:
                    if isinstance(asset, str):
                        hex = uuid.uuid1().get_hex()


# if __name__ == '__main__':
#     import database.shotgun.core.sg_analysis as sg_analysis
#
#     sg = sg_analysis.Config().login()
#     try:
#         app = QApplication(sys.argv)
#     except:
#         app = QApplication.instance()
#     window = SubAssetsInfoDialog(sg, 92636)
#     window.show()
#     sys.exit(app.exec_())
