# -*- coding: utf-8 -*-#
# -------------------------------------------------------
# NAME       : pose_syn_ui
# Describe   : 说明描述
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2025/6/27__上午10:44
# -------------------------------------------------------
try:
    from PySide2.QtWidgets import *
    from PySide2.QtGui import *
    from PySide2.QtCore import *
except:
    from PyQt5.QtWidgets import *
    from PyQt5.QtGui import *
    from PyQt5.QtCore import *
from apps.tools.maya.pose_syn_tool import pose_syn_fun

reload(pose_syn_fun)


class PoseSynUI(QDialog):
    CloseSignal = Signal()

    def __init__(self, parent=None):
        super(PoseSynUI, self).__init__(parent)
        self.setWindowTitle(u"A Pose 模型同步工具")
        self.setGeometry(100, 100, 400, 300)
        self.__init_ui()
        self.__connect_signals()

    def __init_ui(self):
        self.__layout = QVBoxLayout(self)

        self.__label = QLabel(u"请选择要同步的模型:")
        self.__layout.addWidget(self.__label)

        self.__list_layout = QHBoxLayout()

        self.__model_list = QListWidget()

        self.__select_layout = QVBoxLayout()

        self.__add_button = QPushButton(u"添加模型")
        self.__remove_button = QPushButton(u"移除模型")
        self.__clear_button = QPushButton(u"清空模型列表")

        self.__select_layout.addWidget(self.__add_button)
        self.__select_layout.addWidget(self.__remove_button)
        self.__select_layout.addWidget(self.__clear_button)

        self.__select_layout.addStretch()

        self.__list_layout.addWidget(self.__model_list)
        self.__list_layout.addLayout(self.__select_layout)
        self.__layout.addLayout(self.__list_layout)

        self.__sync_button = QPushButton(u"生成A Pose 模型")
        self.__clear_sync_button = QPushButton(u"清除所有A Pose 模型")
        # self.__clear_target_button = QPushButton(u"清除所有Target")
        self.__layout.addWidget(self.__sync_button)
        self.__layout.addWidget(self.__clear_sync_button)

    def __connect_signals(self):
        self.__add_button.clicked.connect(self.__add_model_clicked)
        self.__remove_button.clicked.connect(self.__remove_model_clicked)
        self.__clear_button.clicked.connect(self.__clear_models_clicked)
        self.__sync_button.clicked.connect(self.__sync_models_clicked)
        self.__clear_sync_button.clicked.connect(self.__clear_sync_models_clicked)
        self.__model_list.itemSelectionChanged.connect(self.__selection_changed)

    def __selection_changed(self):
        import maya.cmds as cmds
        selected_items = self.__model_list.selectedItems()
        selected_meshes = []
        if selected_items:
            for item in selected_items:
                mesh_name = item.text()
                if cmds.objExists(mesh_name):
                    selected_meshes.append(mesh_name)
        if selected_meshes:
            cmds.select(selected_meshes)
        else:
            cmds.select(clear=True)

    def __add_model_clicked(self):
        import maya.cmds as cmds

        listwidget_items = [self.__model_list.item(i).text() for i in range(self.__model_list.count())]
        meshs = cmds.ls(selection=True, long=True)
        if not meshs:
            QMessageBox.warning(self, u"警告", u"请先选择要添加的模型")
        for mesh in meshs:
            _judge=self._judge_mesh(mesh)
            if mesh and cmds.ls(mesh) and mesh not in listwidget_items and _judge==True:
                self.__model_list.addItem(mesh)

    def _judge_mesh(self, poly):
        import maya.cmds as cmds
        if not poly or not cmds.objExists(poly):
            return False
        shape = cmds.listRelatives(poly, s=1, type='mesh', f=1)
        if shape:
            return True
        return False

    def __clear_target_button(self):
        import maya.cmds as cmds
        meshs = [self.__model_list.item(i).text() for i in range(self.__model_list.count())]
        if not meshs:
            QMessageBox.warning(self, u"警告", u"模型列表为空，请添加模型后再清除")
            return
        for mesh in meshs:
            bs = pose_syn_fun.get_mesh_bs(mesh)
            target_name = '{}_A_Pose'.format(mesh.split('|')[-1])
            pose_syn_fun.delete_target(bs, target_name)
        QMessageBox.information(self, u"信息", u"所有Target已清除")

    def __remove_model_clicked(self):
        selected_items = self.__model_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, u"警告", u"请先选择要移除的模型")
            return
        for item in selected_items:
            self.__model_list.takeItem(self.__model_list.row(item))

    def __clear_models_clicked(self):

        self.__model_list.clear()

    def __sync_models_clicked(self):
        import maya.cmds as cmds
        if self.__model_list.count() == 0:
            QMessageBox.warning(self, u"警告", u"模型列表为空，请添加模型后再同步")
            return

        __meshs = [self.__model_list.item(i).text() for i in range(self.__model_list.count())]
        if not __meshs:
            QMessageBox.warning(self, u"警告", u"请先选择要同步的模型")
            return
        if not cmds.ls('A_Pose_Grp'):
            grp = pose_syn_fun.creat_target_group(grp_name='A_Pose_Grp')
        else:
            grp = cmds.ls('A_Pose_Grp')[0]

        __targets = []

        for __mesh in __meshs:
            try:
                self._delete_a_pose_mesh_from_grp(grp, __mesh)
            except:
                pass
            __target_name = '{}_A_Pose'.format(__mesh.split('|')[-1])
            if cmds.objExists(__target_name):
                cmds.delete(__target_name)
            __bs = pose_syn_fun.get_mesh_bs(__mesh)
            if not __bs:
                QMessageBox.warning(self, u"警告", u"模型 {} 没有绑定骨骼".format(__mesh))
                continue
            __target = pose_syn_fun.create_target(__bs, __target_name)
            __target_mesh = pose_syn_fun.rebuild_target(__bs, __target)
            pose_syn_fun.delete_target(__bs, __target_name)
            if not __target_mesh:
                QMessageBox.warning(self, u"警告", u"模型 {} 同步失败".format(__mesh))
                continue
            if cmds.ls(__target_mesh):
                __targets.append(cmds.ls(__target_mesh, long=True)[0])
        if not __targets:
            QMessageBox.warning(self, u"警告", u"没有成功同步的模型")
            return
        for __target in __targets:
            cmds.parent(__target, grp)

            __target = cmds.ls(__target.split('|')[-1], long=True)[0]

            __mesh_name = __target.split('|')[-1].split('_A_Pose')[0]
            target = cmds.rename(__target, __mesh_name)

        QMessageBox.information(self, u"信息", u"A Pose 模型同步成功")

    def _delete_a_pose_mesh_from_grp(self, grp, mesh):
        import maya.cmds as cmds
        __meshs = cmds.listRelatives(grp, children=True, fullPath=True) or []
        if not __meshs:
            return
        for __mesh in __meshs:
            if cmds.objExists(__mesh) and __mesh.split('|')[-1] == mesh.split('|')[-1]:
                cmds.delete(__mesh)
                return

    def __clear_sync_models_clicked(self):
        import maya.cmds as cmds
        reply = QMessageBox.question(self, u"确认", u"确定要清除所有A Pose 模型吗?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            grp = 'A_Pose_Grp'
            if cmds.ls(grp):
                cmds.delete(grp)

            QMessageBox.information(self, u"信息", u"所有A Pose 模型已清除")


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    window = PoseSynUI()
    window.show()
    sys.exit(app.exec_())
