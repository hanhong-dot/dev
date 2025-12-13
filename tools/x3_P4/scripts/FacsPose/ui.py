# -*- coding: UTF-8 -*-
import FacsPose.poses
import pymel.core as pm
import os
try:
    from PySide.QtGui import *
    from PySide.QtCore import *
except ImportError:
    pass
try:
    from PySide2.QtWidgets import *
    from PySide2.QtCore import *
    from PySide2.QtGui import *
except ImportError:
    pass
from functools import partial
import bs
import poses


def save_temp_icons():
    _bs = pm.PyNode("blendShape1")
    # geo = pm.PyNode("NPC_Tao:NPC_Tao_BaseHead")
    # i = 0
    # for target_name in _bs.weight.elements():
    #     i += 1
    #     pm.currentTime(i)
    #     dup = pm.duplicate(geo)[0]
    #     dup.rename(target_name)

    path = os.path.abspath(__file__+"/../icons/X3NpcRom/").replace("\\", "/")+"/"
    target_name = "base"
    wh = (1094, 830)
    pm.playblast(frame=[0], format="image", viewer=0, filename=path + target_name, compression="jpg", quality=100,
                 percent=100, fp=4, clearCache=1, orn=0, wh=wh)
    for target_name in _bs.weight.elements():
        _bs.attr(target_name).set(1)
        pm.playblast(frame=[0], format="image", viewer=0, filename=path+target_name, compression="jpg", quality=100,
                     percent=100, fp=4, clearCache=1, orn=0, wh=wh)
        _bs.attr(target_name).set(0)


def get_app():
    parent = QApplication.activeWindow()
    for i in range(100):
        try:
            new_parent = parent.parent()
        except:
            return parent
        if new_parent is None:
            return parent
        parent = new_parent


class PoseList(QListWidget):
    def __init__(self):
        QListWidget.__init__(self)
        self.setViewMode(QListView.IconMode)
        self.setFixedSize(677, 724)
        icon_size = [1094, 830.0]
        icon_scale = 0.2
        self.setIconSize(QSize(icon_size[0]*icon_scale, icon_size[1]*icon_scale))
        self.setResizeMode(QListView.Adjust)
        self.setContextMenuPolicy(Qt.CustomContextMenu)

    def update_items(self, icon_typ):
        icon_path = os.path.abspath(__file__ + "/../icons/"+icon_typ)
        if not os.path.isdir(icon_path):
            return
        self.clear()
        for name in os.listdir(icon_path):
            base_name = os.path.splitext(os.path.splitext(name)[0])[0]
            icon_file_path = "{icon_path}/{base_name}.0000.jpg".format(**locals()).replace("\\", "/")
            if not os.path.isfile(icon_file_path):
                continue
            item_default = QListWidgetItem(self)
            item_default.setIcon(QIcon(icon_file_path))
            item_default.setText(base_name)
            self.addItem(item_default)

    def resizeEvent(self, event):
        QListWidget.resizeEvent(self, event)
        # print self.size()
    

class FacePoseTool(QDialog):

    def __init__(self):
        QDialog.__init__(self, get_app())
        layout = QVBoxLayout()
        self.setLayout(layout)

        config_layout = QHBoxLayout()
        layout.addLayout(config_layout)

        self.char_comb = QComboBox()
        self.update_chars()
        config_layout.addWidget(self.char_comb)

        add_button = QPushButton(u"添加角色")
        add_button.clicked.connect(self.add_char)
        config_layout.addWidget(add_button)

        del_button = QPushButton(u"删除角色")
        del_button.clicked.connect(self.del_char)
        config_layout.addWidget(del_button)

        self.icon_comb = QComboBox()
        self.update_icons()
        config_layout.addWidget(self.icon_comb)
        
        self.pose_list = PoseList()
        layout.addWidget(self.pose_list)
        self.pose_list.customContextMenuRequested.connect(self.show_menu)
        self.icon_comb.currentIndexChanged.connect(self.update_items)
        self.icon_comb.setCurrentIndex(1)
        self.pose_list.itemDoubleClicked.connect(self.to_pose)

        tool_layout = QHBoxLayout()
        layout.addLayout(tool_layout)

        convert_button = QPushButton(u"全部转成BS")
        convert_button.clicked.connect(self.convert_bs_all)
        tool_layout.addWidget(convert_button)

        joint_drive_button = QPushButton(u"全部转为骨骼驱动")
        joint_drive_button.clicked.connect(self.convert_joint_drive_all)
        tool_layout.addWidget(joint_drive_button)

        load_button = QPushButton(u"导入动画")
        load_button.clicked.connect(self.load_anim)
        tool_layout.addWidget(load_button)

    def update_items(self):
        self.pose_list.update_items(self.icon_comb.currentText())

    def convert_bs_all(self):
        char = self.char_comb.currentText()
        typ = self.icon_comb.currentText()
        poses.tool_convert_bs_all(char, typ)

    def convert_joint_drive_all(self):
        char = self.char_comb.currentText()
        typ = self.icon_comb.currentText()
        poses.tool_convert_joint_drive_all(char, typ)

    def update_chars(self):
        self.char_comb.clear()
        names = []
        path = poses.get_char_root()
        if not os.path.isdir(path):
            return
        for name in os.listdir(path):
            if os.path.isdir(os.path.join(path, name)):
                names.append(name)
        self.char_comb.addItems(names)
    
    def update_icons(self):
        self.icon_comb.clear()
        names = []
        path = os.path.abspath(__file__+"/../icons")
        if not os.path.isdir(path):
            return
        for name in os.listdir(path):
            if os.path.isdir(os.path.join(path, name)):
                names.append(name)
        self.icon_comb.addItems(names)
        
    def del_char(self):
        char = self.char_comb.currentText()
        poses.tool_del_char(char)
        self.update_chars()

    def add_char(self):
        char = raw_input(u"输入角色名称：")
        if not char:
            return
        poses.tool_add_char(char)
        self.update_chars()

    def show_menu(self):
        menu = QMenu(self.pose_list)
        char = self.char_comb.currentText()
        typ = self.icon_comb.currentText()
        pose_name = str(self.pose_list.itemAt(self.pose_list.mapFromGlobal(QCursor.pos())).text())

        if self.pose_list.itemAt(self.pose_list.mapFromGlobal(QCursor.pos())):
            menu.addAction(u'保存', partial(poses.tool_save_pose, char, typ, pose_name))
            menu.addAction(u'加载', partial(poses.tool_load_pose, char, typ, pose_name))
            menu.addAction(u'转为BS', partial(bs.tool_cache_static_target, pose_name))
            menu.addAction(u'转为骨骼驱动', partial(poses.tool_convert_joint_drive, pose_name))
        menu.exec_(QCursor.pos())

    def to_pose(self):
        char = self.char_comb.currentText()
        typ = self.icon_comb.currentText()
        pose_name = self.pose_list.currentItem().text()
        poses.tool_load_pose(char, typ, pose_name)

    @staticmethod
    def load_anim():
        path, _ = QFileDialog.getOpenFileName(get_app(), "Load", "", "(*.json)")
        poses.tool_load_x3_face_rom_anim(path)


window = None


def show():
    global window
    if window is None:
        window = FacePoseTool()
    window.show()


if __name__ == '__main__':
    app = QApplication([])
    show()
    app.exec_()
