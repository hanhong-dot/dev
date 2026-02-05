# -*- coding: utf-8 -*-
import maya.cmds as cmds
from PySide2 import QtWidgets, QtCore, QtGui
import re


class AssetRenamer18(QtWidgets.QDialog):
    def __init__(self):
        super(AssetRenamer18, self).__init__()

        self.setWindowTitle(u"x3DB/REG骨骼重命名工具")
        self.setFixedWidth(400)
        self.setWindowFlags(QtCore.Qt.Window | QtCore.Qt.WindowStaysOnTopHint)

        self.target_data = self.auto_find_data()

        layout = QtWidgets.QVBoxLayout(self)

        info_box = QtWidgets.QGroupBox(u"自动识别数据")
        info_layout = QtWidgets.QHBoxLayout(info_box)
        self.data_label = QtWidgets.QLabel(u"检测到核心标识: " + (self.target_data if self.target_data else u"未找到"))
        self.data_label.setStyleSheet("color: #5DADE2; font-weight: bold;")
        info_layout.addWidget(self.data_label)
        btn_refresh = QtWidgets.QPushButton(u"重新扫描")
        btn_refresh.clicked.connect(self.refresh_data)
        info_layout.addWidget(btn_refresh)
        layout.addWidget(info_box)

        setup_box = QtWidgets.QGroupBox(u"命名设置")
        grid = QtWidgets.QGridLayout(setup_box)

        grid.addWidget(QtWidgets.QLabel(u"前缀:"), 0, 0)
        self.prefix_combo = QtWidgets.QComboBox()
        self.prefix_combo.addItems(["DB_", "REG_"])
        grid.addWidget(self.prefix_combo, 0, 1)

        grid.addWidget(QtWidgets.QLabel(u"中间描述:"), 1, 0)
        self.mid_name = QtWidgets.QLineEdit()
        self.mid_name.setPlaceholderText(u"例如: Arm / Leg")
        grid.addWidget(self.mid_name, 1, 1)

        grid.addWidget(QtWidgets.QLabel(u"起始编号 (01-99):"), 2, 0)
        self.start_num = QtWidgets.QSpinBox()
        self.start_num.setRange(1, 99)
        self.start_num.setValue(1)
        grid.addWidget(self.start_num, 2, 1)

        layout.addWidget(setup_box)

        self.btn_run = QtWidgets.QPushButton(u"骨骼重命名")
        self.btn_run.setMinimumHeight(50)
        self.btn_run.setStyleSheet("background-color: #2E86C1; color: white; font-weight: bold;")
        self.btn_run.clicked.connect(self.process_rename)
        layout.addWidget(self.btn_run)

        layout.addWidget(QtWidgets.QLabel(u"<small>注：选骨骼父级，检查识别的模型数据</small>"))

    def auto_find_data(self):
        keywords = ["FY", "RY", "PL", "YG", "ST", "YS"]
        all_nodes = cmds.ls(dag=True)
        for node in all_nodes:
            short_name = node.split('|')[-1]
            if any(key in short_name for key in keywords):
                match = re.match(r'^([a-zA-Z]+\d+[a-zA-Z]+)', short_name)
                if match:
                    core = match.group(1)
                    if "001" not in core:
                        return core
        return None

    def refresh_data(self):
        self.target_data = self.auto_find_data()
        self.data_label.setText(u"检测到核心模型命名: " + (self.target_data if self.target_data else u"未找到"))

    def process_rename(self):
        if not self.target_data:
            cmds.confirmDialog(title=u"错误", message=u"未能在场景中识别到有效的核心数据。")
            return

        roots = cmds.ls(sl=True, type='joint', long=True)
        if not roots:
            cmds.confirmDialog(title=u"提示", message=u"请选择至少一个父级骨骼。")
            return

        prefix = self.prefix_combo.currentText()
        mid = self.mid_name.text()
        global_start_val = self.start_num.value()

        new_names_dict = {}
        all_new_names_list = []
        all_affected_joints = []

        for idx, root in enumerate(roots):
            current_root_start_num = global_start_val + idx

            if current_root_start_num > 99: current_root_start_num = 99

            children = cmds.listRelatives(root, ad=True, type='joint', fullPath=True) or []

            current_hierarchy = sorted([root] + children, key=len)

            counter = 1
            for jnt in current_hierarchy:
                fmt_name = u"{}{}_{}_{:02d}_{:02d}".format(
                    prefix, self.target_data, mid, current_root_start_num, counter
                )
                new_names_dict[jnt] = fmt_name
                all_new_names_list.append(fmt_name)
                all_affected_joints.append(jnt)
                counter += 1

        duplicates = [n for n in set(all_new_names_list) if all_new_names_list.count(n) > 1]
        if duplicates:
            cmds.confirmDialog(title=u"查重警告", message=u"生成的命名中存在重复: \n" + str(duplicates))
            return

        cmds.undoInfo(openChunk=True)
        try:

            rename_order = sorted(all_affected_joints, key=len, reverse=True)
            for old_path in rename_order:
                cmds.rename(old_path, new_names_dict[old_path])

            print(u"--- 重命名完成 ---")
            cmds.inViewMessage(amg=u"重命名完成！", pos='midCenter', fade=True)

        except Exception as e:
            cmds.warning(str(e))
        finally:
            cmds.undoInfo(closeChunk=True)


def main():
    global asset_rename_win
    try:
        asset_rename_win.close()
        asset_rename_win.deleteLater()
    except:
        pass
    asset_rename_win = AssetRenamer18()
    asset_rename_win.show()


# if __name__ == "__main__":
#     main()