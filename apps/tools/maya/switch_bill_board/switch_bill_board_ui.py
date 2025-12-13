# -*- coding: utf-8 -*-#
# -------------------------------------------------------
# NAME       : __init__.py
# Describe   : 说明描述
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2025/6/30__16:18
# -------------------------------------------------------


try:
    from PySide2.QtWidgets import *
    from PySide2.QtGui import *
    from PySide2.QtCore import *
except:
    from PyQt5.QtWidgets import *
    from PyQt5.QtGui import *
    from PyQt5.QtCore import *

from apps.tools.maya.switch_bill_board import switch_bill_board_fun
#
reload(switch_bill_board_fun)

from apps.publish.ui.message.messagebox import msgview


class SwitchBillBoardUI(QWidget):
    def __init__(self, parent=None):
        super(SwitchBillBoardUI, self).__init__(parent)
        self.setWindowTitle("BillBoard转换工具")
        self.setGeometry(100, 100, 300, 150)
        self.__init_ui()
        self.__connect_signals()

    def __init_ui(self):
        layout = QVBoxLayout(self)

        layout.setAlignment(Qt.AlignTop)

        self.__model_layout = QHBoxLayout()

        self.__model_group= QGroupBox(u"模型转换模式")

        self.__model_group.setLayout(self.__model_layout)
        self.__model_group.setStyleSheet(
            "QGroupBox { border: 1px solid #555555; border-radius: 5px; padding: 10px; }")

        layout.addWidget(self.__model_group)

        self.__point_model_radio = QRadioButton(u"点")


        self.__face_model_radio = QRadioButton(u"面")

        self.__face_model_radio.setChecked(True)

        self.__sphere_model_radio = QRadioButton(u"球")

        self.__model_layout.addWidget(self.__point_model_radio)
        self.__model_layout.addWidget(self.__face_model_radio)
        self.__model_layout.addWidget(self.__sphere_model_radio)

        self.__switch_button= QPushButton(u"转换模型")
        # self.__switch_button.setStyleSheet("background-color: rgb(30, 90, 87); color: white;")
        self.__switch_button.setFixedHeight(25)
        layout.addWidget(self.__switch_button)


        # self.__switch_sphere_to_face_button=QPushButton(u"选择球转换为BillBoard模型", self)
        # self.__switch_sphere_to_face_button.setFixedHeight(30)
        #
        #
        # self.__switch_to_point_button = QPushButton(u"BillBoard转换为点", self)
        # self.__switch_to_point_button.setFixedHeight(30)
        #
        # self.__switch_to_point_button.setToolTip(u"将BillBoard切换为点")
        #
        # self.__switch_to_face_button = QPushButton(u"BillBoard切换为面", self)
        # self.__switch_to_face_button.setToolTip(u"将BillBoard转换为面")
        # self.__switch_to_face_button.setFixedHeight(30)
        #
        # self.__switch_to_face_dis_sphere_button = QPushButton(u"BillBoard面生成显示球", self)
        # self.__switch_to_face_button.setFixedHeight(30)
        #
        # self.__clear_display_sphere_button = QPushButton(u"清除显示球", self)
        # self.__clear_display_sphere_button.setToolTip(u"清除所有显示球")
        # self.__clear_display_sphere_button.setFixedHeight(30)
        # self.__clear_display_sphere_button.setStyleSheet("background-color: rgb(30, 90, 87); color: white;")
        #
        # layout.addWidget(self.__switch_sphere_to_face_button)
        # layout.addWidget(self.__switch_to_point_button)
        # layout.addWidget(self.__switch_to_face_button)
        # layout.addWidget(self.__switch_to_face_dis_sphere_button)
        # layout.addWidget(self.__clear_display_sphere_button)
        # self.setLayout(layout)

    def __connect_signals(self):
        self.__switch_button.clicked.connect(self.__switch_button_clicked)
        # self.__switch_sphere_to_face_button.clicked.connect(self.__switch_sphere_to_face_button_clicked)
        # self.__switch_to_point_button.clicked.connect(self.__switch_bill_board_to_point_clicked)
        # self.__switch_to_face_button.clicked.connect(self.__switch_bill_board_to_face_clicked)
        # self.__switch_to_face_dis_sphere_button.clicked.connect(self.__switch_to_face_dis_psphere_button_clicked)
        # self.__clear_display_sphere_button.clicked.connect(self.__clear_display_sphere_button_clicked)


    def __switch_button_clicked(self):
        if self.__point_model_radio.isChecked():
            ok,result=switch_bill_board_fun.switch_bill_board_meshs_to_point()
            if not ok:
                msgview(result, 1)
                return
            msgview(u"已将BillBoard模型转换为点", 2)
        elif self.__face_model_radio.isChecked():
            ok,result=switch_bill_board_fun.switch_bill_board_meshs_to_face()
            if not ok:
                msgview(result, 1)
                return
            msgview(u"已将BillBoard模型转换为面", 2)
        elif self.__sphere_model_radio.isChecked():
            ok,result=switch_bill_board_fun.switch_bill_board_meshs_to_sphere()
            if not ok:
                msgview(result, 1)
                return
            msgview(u"已将BillBoard模型转换为球", 2)




    # def __switch_button_clicked(self):
    #     meshs=cmds.ls



    # def __switch_sphere_to_face_button_clicked(self):
    #     ok,result=switch_bill_board_fun.switch_spheres_to_faces()
    #     if ok:
    #         msgview(result, 1)
    #     msgview('选择的球模型已经转换为Billboard面片,请检查', 0)
    #
    #
    # def __switch_bill_board_to_point_clicked(self):
    #
    #     bill_board_meshs = switch_bill_board_fun.get_bill_board_meshs()
    #     if not bill_board_meshs:
    #         msgview(u"当前场景没有BillBoard模型节点,请检查", 1)
    #         return
    #     bill_board_meshs = list(set(bill_board_meshs))
    #     for mesh in bill_board_meshs:
    #         ok, result = switch_bill_board_fun.switch_bill_board_face_to_point(mesh)
    #         if not ok:
    #             msgview(result, 1)
    #             return
    #     msgview(u"BillBoard已切换为bake点,请检查", 2)
    #
    # def __switch_bill_board_to_face_clicked(self):
    #     bill_board_meshs = switch_bill_board_fun.get_bill_board_meshs()
    #     if not bill_board_meshs:
    #         msgview(u"当前场景没有BillBoard模型节点,请检查", 1)
    #         return
    #     bill_board_meshs = list(set(bill_board_meshs))
    #     for mesh in bill_board_meshs:
    #         ok, result = switch_bill_board_fun.switch_bill_board_point_to_face(mesh)
    #         if not ok:
    #             msgview(result, 1)
    #             return
    #     msgview(u"BillBoard已转换为面,请检查", 2)
    #
    # def __switch_to_face_dis_psphere_button_clicked(self):
    #     bill_board_meshs = switch_bill_board_fun.get_bill_board_meshs()
    #     if not bill_board_meshs:
    #         msgview(u"当前场景没有BillBoard模型节点,请检查", 1)
    #         return
    #     ok, result = switch_bill_board_fun.switch_bill_board_face_to_sphere(bill_board_meshs)
    #     if not ok:
    #         msgview(result, 1)
    #         return
    #     msgview(u"BillBoard面已生成显示球,请检查", 2)
    #
    # def __clear_display_sphere_button_clicked(self):
    #     ok, result = switch_bill_board_fun.clear_bill_board_sphere()
    #     if not ok:
    #         msgview(result, 1)
    #         return
    #     msgview(u"已清除所有BillBoard显示球", 2)

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    window = SwitchBillBoardUI()
    window.show()
    sys.exit(app.exec_())
