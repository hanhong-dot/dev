# -*- coding: utf-8 -*-
# -----------------------------------
# @File    : add_xgen_group_name_attr_ui.py
# @Author  : linhuan
# @Time    : 2025/7/5 13:30
# @Description : 
# -----------------------------------
try:
    from PySide2.QtWidgets import *
    from PySide2.QtGui import *
    from PySide2.QtCore import *
except:
    from PyQt5.QtWidgets import *
    from PyQt5.QtGui import *
    from PyQt5.QtCore import *

from apps.publish.ui.message.messagebox import msgview
from apps.tools.maya.xgen_tool import xgen_fun

reload(xgen_fun)


class AddXgenGroupNameAttrUI(QWidget):
    def __init__(self, parent=None):
        super(AddXgenGroupNameAttrUI, self).__init__(parent)
        self.setWindowTitle(u"Xgen 描述添加Group Name属性工具")
        self.setGeometry(100, 100, 300, 150)
        self.__init_ui()
        self.__connect_signals()

    def __init_ui(self):
        layout = QVBoxLayout(self)

        layout.setAlignment(Qt.AlignTop)

        self.__add_attr_button = QPushButton(u"添加Xgen描述GroupName属性", self)
        self.__add_attr_button.setFixedHeight(30)
        self.__add_attr_button.setToolTip(u"为选中的Xgen描述添加GroupName属性")

        self.__remove_attr_button = QPushButton(u"移除Xgen描述GroupName属性", self)
        self.__remove_attr_button.setFixedHeight(30)
        self.__remove_attr_button.setToolTip(u"移除选中Xgen描述的GroupName属性")

        layout.addWidget(self.__add_attr_button)
        layout.addWidget(self.__remove_attr_button)

    def __connect_signals(self):
        self.__add_attr_button.clicked.connect(self.__add_attr_button_clicked)
        self.__remove_attr_button.clicked.connect(self.__remove_attr_button_clicked)

    def __add_attr_button_clicked(self):
        xgen_descriptions = xgen_fun.get_selected_xgen_descriptions()
        if not xgen_descriptions:
            msgview(u"未选择xgen描述物体,请选择", 1)
            return
        ok, result = self.__add_group_name_dialog(xgen_descriptions)
        if not ok:
            msgview(u"添加Group Name属性失败: {}".format(result), 1)
        else:
            msgview(u"添加Group Name属性成功: {}".format(result), 2)

    def __remove_attr_button_clicked(self):
        xgen_descriptions = xgen_fun.get_selected_xgen_descriptions()
        if not xgen_descriptions:
            msgview(u"未选择xgen描述物体,请选择", 1)
            return
        for desc in xgen_descriptions:
            xgen_fun.remove_xgen_description_group_name_attr(desc)
            xgen_fun.set_remove_grom_name_attr_outliner_color(desc)
        msgview(u"移除Group Name属性成功", 2)

    def __add_group_name_dialog(self, xgen_descriptions):
        group_name, ok = QInputDialog.getText(self, u"添加Group Name属性", u"请输入Group Name:")
        if ok and group_name:
            for desc in xgen_descriptions:
                ok, reslut = xgen_fun.set_xgen_description_by_group_name(desc, group_name)
                if not ok:
                    return False, u'添加Group Name属性失败: {}'.format(reslut)
        return True, u'添加Group Name属性成功'
