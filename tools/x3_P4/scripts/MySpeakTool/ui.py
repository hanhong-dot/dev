# coding:utf-8
import export_objs

try:
    from PySide.QtGui import *
    from PySide.QtCore import *
except ImportError:
    from PySide2.QtGui import *
    from PySide2.QtCore import *
    from PySide2.QtWidgets import *
try:
    import pymel.core as pm
except ImportError:
    pm = None

import speak_tool
import speak_tool_facs
import export_objs
from . import speak_tool_facs_v2


def get_host_app():
    try:
        main_window = QApplication.activeWindow()
        while True:
            last_win = main_window.parent()
            if last_win:
                main_window = last_win
            else:
                break
        return main_window
    except:
        pass

class allSpeakTool(QDialog):

    def __init__(self):
        QDialog.__init__(self, get_host_app())
        self.setWindowTitle(u"口型工具")
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 2, 0, 0)
        try:
            layout.setMargin(5)
        except AttributeError:
            pass
        self.setLayout(layout)
        menu_bar = QMenuBar()
        layout.setMenuBar(menu_bar)

        self.window_1 = speak_tool.SpeakTool()
        self.window_2 = speak_tool_facs.SpeakTool()
        self.window_3 = speak_tool_facs_v2.SpeakTool()
        self.tab = QTabWidget(self)
        layout.addWidget(self.tab)
        self.tab.addTab(self.window_1, u"NPC版")
        self.tab.addTab(self.window_2, u"FACS版")
        self.tab.addTab(self.window_3, u"FACS2.0版")

        self.tab.setCurrentIndex(2)

        self.window_1.showNormal()
        self.window_2.showNormal()
        self.window_3.showNormal()
        self.tab.currentChanged.connect(self.window_1.showNormal)
        self.tab.currentChanged.connect(self.window_2.showNormal)

        self.create_export_box()
        layout.addWidget(self.export_box)
        layout.setStretch(0, 1)
        layout.setStretch(1, 0)
        layout.setStretch(2, 0)
        self.resize(380, 380 / 0.618)

    def create_export_box(self):
        self.export_box = QGroupBox()
        layout = QHBoxLayout()
        self.export_box.setLayout(layout)
        self.export_box.setTitle(u'导出动画obj序列')

        self.lineEdit = QLineEdit()
        self.lineEdit.setText('ST')
        layout.addLayout(speak_tool_facs.PrefixWeight(u"角色名：", self.lineEdit))
        layout.addWidget(self.lineEdit)

        button = QPushButton(u'本场景内')
        layout.addWidget(button)
        QObject.connect(button, SIGNAL('clicked()'), self.export_objs_in_scene)
        button = QPushButton(u'根目录内')
        layout.addWidget(button)
        QObject.connect(button, SIGNAL('clicked()'), self.export_objs_in_list)

    def export_objs_in_scene(self):
        i = self.tab.currentIndex()
        save_path = [self.window_1.save.text(), self.window_2.save.text()][i]
        phn_path = [self.window_1.root.text(), self.window_2.root.text()][i]
        export_objs.main(False, self.lineEdit.text(), save_path, phn_path)
        print u'已保存至：%s' % save_path

    def export_objs_in_list(self):
        i = self.tab.currentIndex()
        save_path = [self.window_1.save.text(), self.window_2.save.text()][i]
        phn_path = [self.window_1.root.text(), self.window_2.root.text()][i]
        export_objs.main(True, self.lineEdit.text(), save_path, phn_path)
        print u'已保存至：%s' % save_path

window = None


def show():
    global window
    if window is None:
        window = allSpeakTool()
    window.show()