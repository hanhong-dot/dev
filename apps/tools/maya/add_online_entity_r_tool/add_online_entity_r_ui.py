# -*- coding: utf-8 -*-
# author: linhuan
# file: add_online_entity_r_ui.py
# time: 2026/2/2 15:48
# description:
try:
    from PySide2.QtWidgets import *
    from PySide2.QtGui import *
    from PySide2.QtCore import *
except:
    from PyQt5.QtWidgets import *
    from PyQt5.QtGui import *
    from PyQt5.QtCore import *
import lib.common.config as config
import lib.common.jsonio as jsonio
from apps.publish.ui.message.messagebox import msgview
from apps.tools.maya.add_online_entity_r_tool import entity_r_fun
reload(entity_r_fun)

class AddOnlineEntityRUI(QWidget):
    def __init__(self, parent=None):
        super(AddOnlineEntityRUI, self).__init__(parent)
        self.setWindowTitle(u"更新在线版本工具")
        self.resize(400, 200)
        self.__setup_ui()
        self.__connect_signals()

    def __setup_ui(self):
        layout = QVBoxLayout()

        self.label = QLabel(u"")
        layout.addWidget(self.label)

        __current_online_entity_r = self.__get_online_entity_r()
        self.label.setText(
            u"当前在线版本R: {}".format(__current_online_entity_r[0] if __current_online_entity_r else "None"))

        self.input_field = QLineEdit(__current_online_entity_r[0])
        self.input_field.setPlaceholderText(u"请添加在线版本")
        layout.addWidget(self.input_field)

        self.add_button = QPushButton("Apply")

        layout.addWidget(self.add_button)

        self.setLayout(layout)

    def __connect_signals(self):
        self.add_button.clicked.connect(self.__on_add_button_clicked)

    def __on_add_button_clicked(self):
        new_r = self.input_field.text().strip()
        if not new_r:
            msgview(u'请输入在线版本号', 0)
            return
        current_entity_r = self.__get_online_entity_r()
        if current_entity_r and new_r == current_entity_r[0]:
            msgview(u'输入的版本号与当前在线版本号相同,不需要更新', 1)
            return
        ok, result = entity_r_fun.judge_entity_r_in_online(new_r)
        if not ok:
            msgview(result, 0)
            return
        self.__replace_online_entity_r(new_r)
        msgview(u'在线版本更新成功:{}'.format(new_r), 2)
        self.label.setText(u"当前在线版本R: {}".format(new_r))

    def __replace_online_entity_r(self, new_r):
        try:
            _configpath = config.GetConfig(dcc='shotgun', configfile="oline_entity_version.json").get_config()
            jsonio.write([new_r], _configpath, wtype="w")
            return True
        except Exception as e:
            msgview(u'更新在线版本失败:{}'.format(e), 1)
            return False

    def __get_online_entity_r(self):
        _configpath = config.GetConfig(dcc='shotgun', configfile="oline_entity_version.json").get_config()
        return jsonio.read(_configpath)


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    window = AddOnlineEntityRUI()
    window.show()
    sys.exit(app.exec_())
