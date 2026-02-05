# -*- coding: utf-8 -*-
import maya.cmds as cmds
from PySide2 import QtWidgets, QtCore


def get_maya_main_window():
    for obj in QtWidgets.QApplication.topLevelWidgets():
        if obj.objectName() == 'MayaWindow':
            return obj
    return None


class JointMigrationProV4(QtWidgets.QDialog):
    def __init__(self, parent=get_maya_main_window()):
        super(JointMigrationProV4, self).__init__(parent)

        self.setWindowTitle(u"引擎骨骼导入（记得保存文件）")
        self.setFixedWidth(420)
        self.setWindowFlags(QtCore.Qt.Window)

        self.recorded_names = []

        layout = QtWidgets.QVBoxLayout(self)
        layout.setSpacing(12)

        group1 = QtWidgets.QGroupBox(u"选择骨骼，记得保存文件")
        layout1 = QtWidgets.QVBoxLayout(group1)
        self.btn_clean = QtWidgets.QPushButton(u"选择骨骼前置（记录+导入+改名")
        self.btn_clean.setFixedHeight(40)
        self.btn_clean.setStyleSheet("background-color: #D35400; color: white; font-weight: bold;")
        self.btn_clean.clicked.connect(self.process_old_hierarchy)
        layout1.addWidget(self.btn_clean)
        layout.addWidget(group1)

        group2 = QtWidgets.QGroupBox(u"约束")
        layout2 = QtWidgets.QVBoxLayout(group2)
        self.btn_constrain = QtWidgets.QPushButton(u"选择引擎骨骼+old骨骼")
        self.btn_constrain.setFixedHeight(45)
        self.btn_constrain.setStyleSheet("background-color: #27AE60; color: white; font-weight: bold;")
        self.btn_constrain.clicked.connect(self.constrain_old_to_new)
        layout2.addWidget(self.btn_constrain)
        layout.addWidget(group2)

        self.status = QtWidgets.QLabel(u"状态: 就绪")
        layout.addWidget(self.status)

    def process_old_hierarchy(self):

        sel = cmds.ls(sl=True, long=True)
        if not sel:
            cmds.warning(u"请先选择【旧骨骼】根部")
            return

        for item in sel:
            if cmds.objExists(item) and cmds.referenceQuery(item, isNodeReferenced=True):
                ref_node = cmds.referenceQuery(item, referenceNode=True)
                ref_file = cmds.referenceQuery(ref_node, filename=True)
                cmds.file(ref_file, importReference=True)

        cmds.refresh()

        root_short_names = [s.split('|')[-1].split(':')[-1] for s in sel]
        re_sel = []
        for sn in root_short_names:
            found = cmds.ls("*" + sn, type='joint', long=True) or []
            re_sel.extend(found)

        if not re_sel:
            self.status.setText(u"错误: 导入后找不到根骨骼")
            return

        all_joints = cmds.listRelatives(re_sel, ad=True, fullPath=True, type='joint') or []
        all_joints.extend(re_sel)
        all_joints = list(set(all_joints))
        all_joints.sort(key=len, reverse=True)

        self.recorded_names = []
        count = 0

        for jnt in all_joints:
            if not cmds.objExists(jnt): continue

            cons = cmds.listConnections(jnt, type='constraint') or []
            if cons: cmds.delete(cons)

            plugs = cmds.listConnections(jnt, d=False, s=True, p=True) or []
            for p in plugs:
                d_plugs = cmds.listConnections(p, d=True, s=False, p=True) or []
                for dp in d_plugs:
                    if jnt in dp and not any(x in dp for x in ['worldMatrix', 'message']):
                        try:
                            cmds.disconnectAttr(p, dp)
                        except:
                            pass

            raw_name = jnt.split('|')[-1].split(':')[-1]
            self.recorded_names.append(raw_name)  # 存入内存

            if not raw_name.startswith('old_'):
                try:
                    cmds.rename(jnt, "old_" + raw_name)
                    count += 1
                except:
                    pass

        self.status.setText(u"已处理 {} 根骨骼，并记录名单。".format(count))

    def constrain_old_to_new(self):

        sel_new_root = cmds.ls(sl=True, long=True)
        if not sel_new_root:
            cmds.warning(u"请选择【新导入】层级的根节点")
            return

        all_new_nodes = cmds.listRelatives(sel_new_root, ad=True, fullPath=True, type='transform') or []
        all_new_nodes.extend(sel_new_root)

        match_count = 0
        for node in all_new_nodes:

            sn = node.split('|')[-1].split(':')[-1]

            if sn in self.recorded_names:
                target_old = "old_" + sn
                if cmds.objExists(target_old):
                    try:

                        cmds.parentConstraint(node, target_old, mo=False)
                        cmds.scaleConstraint(node, target_old, mo=False)
                        match_count += 1
                    except:
                        pass

        self.status.setText(u"对齐完成: {} 个节点受驱动".format(match_count))

def load_mig_pro_v4():
    global mig_pro_v4
    try:
        if 'mig_pro_v4' in globals():
            mig_pro_v4.close()
            mig_pro_v4.deleteLater()
    except:
        pass
    mig_pro_v4 = JointMigrationProV4()
    mig_pro_v4.show()


# if __name__ == "__main__":
#     try:
#         if 'mig_pro_v4' in globals():
#             mig_pro_v4.close()
#             mig_pro_v4.deleteLater()
#     except:
#         pass
#     mig_pro_v4 = JointMigrationProV4()
#     mig_pro_v4.show()