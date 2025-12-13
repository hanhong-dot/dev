# -*- coding: UTF-8 -*-

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
import os
import main
reload(main)
import split_combined_bs
reload(split_combined_bs)
from functools import partial
import pymel.core as pm

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

# class SliderDemo(QWidget):
#     def __init__(self, parent=None, attr=None):
#         super(SliderDemo, self).__init__(parent)
#         self.attr = attr
#         layout = QVBoxLayout()
#         self.setLayout(layout)
#
#         self.label = QLabel(str(self.attr))
#         self.label.setAlignment(Qt.AlignCenter)
#         layout.addWidget(self.label)
#
#         self.spinBox = QDoubleSpinBox()
#         self.spinBox.setValue(0.00)
#         self.spinBox.setRange(0.00, 1.00)
#         self.spinBox.setSingleStep(0.1)
#         layout.addWidget(self.spinBox)
#
#         # 水平方向
#         self.sl = QSlider(Qt.Horizontal)
#         # 设置最小值
#         self.sl.setMinimum(0)
#         # 设置最大值
#         self.sl.setMaximum(100)
#         # 步长
#         self.sl.setSingleStep(1)
#         # 设置当前值
#         self.sl.setValue(0)
#         # 刻度位置，刻度在下方
#         self.sl.setTickPosition(QSlider.TicksBelow)
#         # 设置刻度间隔
#         self.sl.setTickInterval(1)
#         layout.addWidget(self.sl)
#         # 连接信号槽
#         self.sl.valueChanged.connect(self.setSpinValue)
#         self.spinBox.valueChanged.connect(self.setSliderValue)
#         self.spinBox.valueChanged.connect(partial(main.set_tongueBS, attr=self.attr))
#
#         button = QPushButton(u'修改/添加舌型')
#         QObject.connect(button, SIGNAL('clicked()'), partial(main.edit_BS, attr=self.attr))
#         layout.addWidget(button)
#
#     def setSpinValue(self):
#         self.spinBox.setValue(float(self.sl.value()) / 100)
#
#     def setSliderValue(self):
#         self.sl.setValue(float(self.spinBox.value()) * 100)
#
# class BS_SliderDemo(QWidget):
#     def __init__(self, parent=None):
#         super(BS_SliderDemo, self).__init__(parent)
#         layout = QVBoxLayout()
#         self.setLayout(layout)
#
#         self.label = QLabel(u'口型总开关')
#         self.label.setAlignment(Qt.AlignCenter)
#         layout.addWidget(self.label)
#
#         self.spinBox = QDoubleSpinBox()
#         self.spinBox.setValue(1.00)
#         self.spinBox.setRange(0.00, 1.00)
#         self.spinBox.setSingleStep(0.1)
#         layout.addWidget(self.spinBox)
#
#         # 水平方向
#         self.sl = QSlider(Qt.Horizontal)
#         # 设置最小值
#         self.sl.setMinimum(0)
#         # 设置最大值
#         self.sl.setMaximum(100)
#         # 步长
#         self.sl.setSingleStep(1)
#         # 设置当前值
#         self.sl.setValue(100)
#         # 刻度位置，刻度在下方
#         self.sl.setTickPosition(QSlider.TicksBelow)
#         # 设置刻度间隔
#         self.sl.setTickInterval(1)
#         layout.addWidget(self.sl)
#         # 连接信号槽
#         self.sl.valueChanged.connect(self.setSpinValue)
#         self.spinBox.valueChanged.connect(self.setSliderValue)
#         QObject.connect(self.spinBox, SIGNAL('valueChanged (double)'), main.set_speakBS_value)
#
#     def setSpinValue(self):
#         self.spinBox.setValue(float(self.sl.value()) / 100)
#
#     def setSliderValue(self):
#         self.sl.setValue(float(self.spinBox.value()) * 100)

class Dialog(QDialog):

    def __init__(self):
        super(Dialog, self).__init__(parent=get_app())

        # self.create_connect_box()
        self.create_rename_box()
        self.create_other_box()
        # self.create_tongue_box()

        mainLayout = QVBoxLayout()
        # mainLayout.addWidget(self.connect_box)
        mainLayout.addWidget(self.rename_box)
        mainLayout.addWidget(self.other_box)
        # mainLayout.addWidget(self.tongue_box)

        mainLayout.setStretch(0, 1)
        mainLayout.setStretch(1, 0)

        self.setLayout(mainLayout)
        # self.resize(739, 800)
        self.resize(737, 665)
        self.setWindowTitle(u"口型修改工具-FACS版")
        import os
        qss_path = os.path.abspath(__file__ + "/../data/qss.css")
        with open(qss_path, "r") as fp:
            qss = fp.read()
        self.setStyleSheet(qss)

    # def create_connect_box(self):
    #
    #     self.connect_box = QGroupBox(u"BS节点默认为FaceDriverBS：")
    #     layout = QVBoxLayout()
    #     self.connect_box.setLayout(layout)
    #     button_connect = QPushButton(u'连接所有BS')
    #     layout.addWidget(button_connect)
    #     QObject.connect(button_connect, SIGNAL('clicked()'), main.connect_BS)
    #     layout.addStretch(1)

    def create_rename_box(self):
        self.rename_box = QGroupBox(u"选择一个口型：")
        layout = QVBoxLayout()
        self.rename_box.setLayout(layout)
        # listWidget = MyListWidget()
        listWidget = QListWidget()
        layout.addWidget(listWidget)

        listWidget.setViewMode(QListView.IconMode)
        icon_size = [1310, 856.0]
        icon_scale = 0.2
        listWidget.setIconSize(QSize(icon_size[0]*icon_scale, icon_size[1]*icon_scale))
        listWidget.setResizeMode(QListView.Adjust)

        item_default = QListWidgetItem()
        item_default.setIcon(QIcon(__file__ + "/../data/icon/Default.0000.png"))
        item_default.setText('Default')
        listWidget.addItem(item_default)
        # listWidget.LeftChick.connect(partial(main.select_BS, ifitem=1))
        listWidget.itemClicked.connect(partial(main.select_BS, ifitem=1))
        for i in range(len(main.speakBS_list)):
            if main.speakBS_list[i] in ['LipZipUp', 'MouthCloseUp']:
                continue
            item = QListWidgetItem()
            icon_path = __file__ + "/../data/icon/%s.0000.png" % main.speakBS_list[i]
            if not os.path.isfile(icon_path):
                icon_path = __file__ + "/../data/icon/%s.0000.jpg" % main.speakBS_list[i]
            if not os.path.isfile(icon_path):
                continue
            item.setIcon(QIcon(icon_path))
            if main.speakBS_list[i] in ['LipZipDn', 'MouthCloseDn']:
                item.setText(main.speakBS_list[i] + ' + ' + main.speakBS_list[i].replace('Dn', 'Up'))
            else:
                item.setText(main.speakBS_list[i])
            listWidget.addItem(item)


        def show_menu():
            popMenu = QMenu(self)
            item = str(listWidget.itemAt(listWidget.mapFromGlobal(QCursor.pos())).text())
            if listWidget.itemAt(listWidget.mapFromGlobal(QCursor.pos())):
                if item == 'MouthCloseDn + MouthCloseUp':
                    popMenu.addAction(u'分离base的MouthCloseDn和MouthCloseUp',
                                      partial(split_combined_bs.split_combined_BS, 'base', 'MouthClose'))
                    popMenu.addAction(u'分离ST的MouthCloseDn和MouthCloseUp',
                                      partial(split_combined_bs.split_combined_BS, 'ST', 'MouthClose'))
                elif item == 'LipZipDn + LipZipUp':
                    popMenu.addAction(u'分离base的LipZipDn和LipZipUp',
                                      partial(split_combined_bs.split_combined_BS, 'base', 'LipZip'))
                    popMenu.addAction(u'分离ST的LipZipDn和LipZipUp',
                                      partial(split_combined_bs.split_combined_BS, 'ST', 'LipZip'))
                # if item != 'Default':
                #     popMenu.addAction(u'重命名为'+item, partial(main.rename_func, item))
                #     popMenu.addAction(u'添加/修改口型(面片驱动)', partial(main.edit_BS, item))
                #     popMenu.addAction(u'重建口型(面片驱动)', partial(main.rebuild_BS, item))
                #     popMenu.addAction(u'选择两个模型添加口型矫正', partial(main.speakBS_correction, item))
                # else:
                #     popMenu.addAction(u'重建全部口型(面片驱动)', main.rebuild_all_BS)
            popMenu.exec_(QCursor.pos())

        listWidget.setContextMenuPolicy(Qt.CustomContextMenu)
        listWidget.customContextMenuRequested.connect(show_menu)

    # def create_tongue_box(self):
    #     self.tongue_box = QGroupBox(u"选择一个舌型：")
    #     layout = QHBoxLayout()
    #     self.tongue_box.setLayout(layout)
    #
    #     # for i, attr in enumerate(main.tongue_bs_list):
    #     #     slider = SliderDemo(attr=attr)
    #     #     layout.addWidget(slider)
    #
    #     slider = BS_SliderDemo()
    #     slider.setFixedSize(200, 80)
    #     layout.addWidget(slider)
    #     layout.setAlignment(Qt.AlignLeft)
    def setBrowerPath(self):
        download_path = QFileDialog.getExistingDirectory(self, u"浏览", os.path.abspath(__file__ + "/../data/model"))
        if download_path:
            self.lineEdit.setText(download_path.replace('/', '\\'))

    def create_other_box(self):
        self.other_box = QGroupBox()
        layout = QHBoxLayout()
        self.other_box.setLayout(layout)
        self.lineEdit = QLineEdit()
        self.lineEdit.setReadOnly(True)
        self.lineEdit.setText(os.path.abspath(__file__ + "/../data/model"))
        layout.addWidget(self.lineEdit)

        def export_obj():
            split_combined_bs.export_all_bs(obj_path=os.path.abspath(self.lineEdit.text()).replace('\\', '/'))

        def import_obj():
            split_combined_bs.import_all_bs(obj_path=os.path.abspath(self.lineEdit.text()).replace('\\', '/'))

        button = QPushButton(u'浏览')
        layout.addWidget(button)
        QObject.connect(button, SIGNAL('clicked()'), self.setBrowerPath)
        button = QPushButton(u'导出口型')
        layout.addWidget(button)
        QObject.connect(button, SIGNAL('clicked()'), export_obj)
        button = QPushButton(u'导入口型')
        layout.addWidget(button)
        QObject.connect(button, SIGNAL('clicked()'), import_obj)

    #     button = QPushButton(u'清除所有关键帧并还原')
    #     layout.addWidget(button)
    #     QObject.connect(button, SIGNAL('clicked()'), main.clean_anim)
    #
    #     button_cleanBS = QPushButton(u'删除多余口型模型')
    #     layout.addWidget(button_cleanBS)
    #     QObject.connect(button_cleanBS, SIGNAL('clicked()'), main.clean_rebuild_BS)
    #
    #     button_cleanAudio = QPushButton(u'删除所有音频')
    #     layout.addWidget(button_cleanAudio)
    #     QObject.connect(button_cleanAudio, SIGNAL('clicked()'), main.clean_audio)
    #
    #     button_transfer = QPushButton(u'选择两个模型传递顶点')
    #     layout.addWidget(button_transfer)
    #     QObject.connect(button_transfer, SIGNAL('clicked()'), main.transfer_vertex)
    #     layout.addStretch(1)
    #
    #     button_transfer = QPushButton(u'修复scale连接问题')
    #     layout.addWidget(button_transfer)
    #     QObject.connect(button_transfer, SIGNAL('clicked()'), main.repair_scale_connect)
    #     layout.addStretch(1)

    # def resizeEvent(self, event):
    #    QDialog.resizeEvent(self, event)
    #    print self.size()


if __name__ == '__main__':

    import sys

    app = QApplication(sys.argv)
    dialog = Dialog()
    sys.exit(dialog.exec_())
