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

import split_combined_bs

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

class Dialog(QDialog):

    def __init__(self):
        super(Dialog, self).__init__(parent=get_app())

        self.create_split_box()

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.split_box)
        mainLayout.setStretch(0, 1)
        self.setLayout(mainLayout)
        self.resize(290, 144)
        self.setWindowTitle(u"口型修改工具_base版")
        import os
        qss_path = os.path.abspath(__file__ + "/../data/qss.css")
        with open(qss_path, "r") as fp:
            qss = fp.read()
        # self.setStyleSheet(qss)

    def create_split_box(self):

        self.split_box = QGroupBox(u"请选择你的组合口型模型：")
        layout = QVBoxLayout()
        self.split_box.setLayout(layout)

        button = QPushButton(u'分离MouthCloseDn和MouthCloseUp')
        layout.addWidget(button)
        QObject.connect(button, SIGNAL('clicked()'), split_combined_bs.split_MouthClose)
        layout.addStretch(1)

        button = QPushButton(u'分离LipZipDn和LipZipUp')
        layout.addWidget(button)
        QObject.connect(button, SIGNAL('clicked()'), split_combined_bs.split_LipZip)
        layout.addStretch(1)

        button = QPushButton(u'重建所有并导出obj')
        layout.addWidget(button)
        QObject.connect(button, SIGNAL('clicked()'), split_combined_bs.export_all_bs)
        layout.addStretch(1)


    # def resizeEvent(self, event):
    #    QDialog.resizeEvent(self, event)
    #    print self.size()


if __name__ == '__main__':

    import sys

    app = QApplication(sys.argv)
    dialog = Dialog()
    sys.exit(dialog.exec_())
