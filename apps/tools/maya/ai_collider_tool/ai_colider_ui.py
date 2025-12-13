# -*- coding: utf-8 -*-#
# -------------------------------------------------------
# NAME       : ai_colider_ui
# Describe   : 说明描述
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2025/6/18__下午2:49
# -------------------------------------------------------
try:
    from PySide2.QtWidgets import *
    from PySide2.QtGui import *
    from PySide2.QtCore import *
except:
    from PyQt5.QtWidgets import *
    from PyQt5.QtGui import *
    from PyQt5.QtCore import *
from apps.tools.maya.ai_collider_tool import mesh_fun
reload(mesh_fun)

from apps.publish.ui.message.messagebox import msgview
from apps.tools.maya.ai_collider_tool import send_data_to_ai
reload(send_data_to_ai)
from apps.tools.maya.ai_collider_tool import create_collision_mesh

reload(create_collision_mesh)

import sys


class AiColiderUI(QWidget):
    CloseSignal = Signal()

    def __init__(self, convex_type, parent=None):
        super(AiColiderUI, self).__init__(parent)
        self.__convex_type = convex_type
        self.__init_ui()
        self.__builder()
        self.__connect()

    def __connect(self):
        self.__add_btn.clicked.connect(self.__add_select_mesh)
        self.__remove_btn.clicked.connect(self.__remove_select_mesh)
        self._clear_btn.clicked.connect(self.__clear_select_mesh)
        self.__apply_btn.clicked.connect(self.__apply_creat_ai_colider)
        self.__close_btn.clicked.connect(self.__close)

    def __init_ui(self):
        self.setWindowTitle(u'Ai Collider Tool')
        self.resize(300, 100)
        self.__main_layout = QVBoxLayout()
        self.setLayout(self.__main_layout)

    def __builder(self):
        self.__add_layout = QHBoxLayout()
        self.__butoon_layout = QVBoxLayout()
        self.__butoon_layout.setAlignment(Qt.AlignTop)
        self.__add_btn = QPushButton(u'添加模型')
        self.__butoon_layout.addStretch()
        self.__butoon_layout.setSpacing(15)
        self.__remove_btn = QPushButton(u'移除模型(选择)')
        self._clear_btn = QPushButton(u'清空')
        self.__listwidget = QListWidget()
        self.__listwidget.setSelectionMode(QAbstractItemView.ContiguousSelection)
        self.__listwidget.setVerticalScrollMode(QAbstractItemView.ScrollPerItem)
        self.__butoon_layout.addWidget(self.__add_btn)
        self.__butoon_layout.addWidget(self.__remove_btn)
        self.__butoon_layout.addWidget(self._clear_btn)
        self.__butoon_layout.setAlignment(Qt.AlignBaseline)
        self.__add_layout.addWidget(self.__listwidget)
        self.__add_layout.addLayout(self.__butoon_layout)

        self.__main_layout.addLayout(self.__add_layout)

        self.__property_layout = QVBoxLayout()
        self.__model_layout = QHBoxLayout()

        self.__model_label = QLabel(u'碰撞体类型:')

        self.__box_model_checkbox = QCheckBox(u'Box')
        self.__box_model_checkbox.setChecked(True)

        self.__capsulee_model_checkbox = QCheckBox(u'胶囊体')
        self.__capsulee_model_checkbox.setChecked(False)

        self.__model_layout.addWidget(self.__model_label)
        self.__model_layout.addWidget(self.__box_model_checkbox)
        self.__model_layout.addWidget(self.__capsulee_model_checkbox)


        self.__max_count_layout = QHBoxLayout()
        self.__max_count_label = QLabel(u'最大碰撞体数量:')
        self.__max_count_spinbox = QSpinBox()
        self.__max_count_spinbox.setRange(1, 1000)
        self.__max_count_spinbox.setValue(20)

        self.__max_count_layout.addWidget(self.__max_count_label)
        self.__max_count_layout.addWidget(self.__max_count_spinbox)







        self.__property_layout.addLayout(self.__model_layout)

        self.__property_layout.addLayout(self.__max_count_layout)

        self.__main_layout.addLayout(self.__property_layout)

        self.__apply_btn = QPushButton(u'创建AiColider碰撞体')
        self.__add_btn.setStyleSheet("background-color: rgb(30, 90, 87); color: white;")
        # self.__apply_btn.setStyleSheet("background-color: rgb(30, 90, 87); color: white;")

        self.__close_btn = QPushButton(u'关闭')

        self.__main_layout.addWidget(self.__apply_btn)
        self.__main_layout.addWidget(self.__close_btn)

    def __add_select_mesh(self):
        select_meshs = mesh_fun.get_select_meshs()
        listwidget_items = [self.__listwidget.item(i).text() for i in range(self.__listwidget.count())]
        if not select_meshs:
            return
        for mesh in select_meshs:
            if mesh in listwidget_items:
                continue
            self.__listwidget.addItem(mesh)

    def __close(self):
        self.CloseSignal.emit()
        self.close()
        try:
            self.deleteLater()
        except:
            pass
        try:
            global ai_colider_ui
            ai_colider_ui = None
        except:
            pass

    def __remove_select_mesh(self):
        select_items = self.__listwidget.selectedItems()
        for item in select_items:
            self.__listwidget.takeItem(self.__listwidget.row(item))

    def __clear_select_mesh(self):
        self.__listwidget.clear()

    def __apply_creat_ai_colider(self, ):
        import maya.cmds as cmds


        result = msgview(u'请确认,是否创建碰撞体', 2, 1)
        if not result:
            return
        select_meshs = [self.__listwidget.item(i).text() for i in range(self.__listwidget.count())]
        if not select_meshs:
            msgview(u"请先选择添加模型", 1)
            return
        self.__convex_type=[]

        __box_model = self.__box_model_checkbox.isChecked()
        __capsule_model= self.__capsulee_model_checkbox.isChecked()
        if __box_model:
            self.__convex_type.append(1)
        if __capsule_model:
            self.__convex_type.append(6)
        if not self.__convex_type:
            msgview(u"请至少选择一个碰撞体类型", 1)
            return



        __max_count = self.__max_count_spinbox.value()
        __max_count=int(__max_count)
        check_result = self.__check_exist_mesh(select_meshs)
        if not check_result:
            return


        if len(select_meshs) > 1:
            __combin_mesh = self._copy_combin_meshs(select_meshs)
            mesh_data = mesh_fun.get_mesh_data(__combin_mesh, self.__convex_type,__max_count)
            cmds.delete(__combin_mesh)
        else:
            mesh_data = mesh_fun.get_mesh_data(select_meshs[0], self.__convex_type,__max_count)
        if not mesh_data:
            msgview(u"没有获取到模型数据,请检查选择模型", 1)
            return
        ai_colider_data = send_data_to_ai.send_data_to_ai(mesh_data)
        if not ai_colider_data:
            msgview(u"没有获取到AI碰撞体数据,请检查是否未连接到AI服务", 1)
            return
        ok, result = create_collision_mesh.create_collision_mesh_by_data(ai_colider_data,
                                                                         select_meshs[0].split('|')[-1])
        if not ok:
            msgview(u"创建碰撞体失败:{}".format(result), 1)
            return

    def __check_exist_mesh(self, meshs):
        import maya.cmds as cmds
        errors = []
        if not meshs:
            return False
        for mesh in meshs:
            if not cmds.objExists(mesh):
                errors.append(mesh)
        if errors:
            msgview(u"以下模型不存在:{}".format(','.join(errors)), 1)
            return False
        return True

    def _copy_combin_meshs(self, meshs):
        import maya.cmds as cmds
        import maya.mel as mel
        if not meshs:
            return None
        if len(meshs) == 1:
            return meshs[0]
        __mesh_list = []
        for mesh in meshs:
            if cmds.objExists(mesh):
                __mesh_copy = cmds.duplicate(mesh, name='copy_{}'.format(mesh.split('|')[-1]), rr=True)
                if __mesh_copy:
                    __mesh_list.append(__mesh_copy[0])
        __mesh = cmds.polyUnite(__mesh_list, name='combin_mesh', ch=False)
        mel.eval('DeleteHistory;')

        return __mesh[0]
