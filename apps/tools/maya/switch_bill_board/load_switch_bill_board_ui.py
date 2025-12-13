# -*- coding: utf-8 -*-
# -----------------------------------
# @File    : load_switch_bill_board_ui.py
# @Author  : linhuan
# @Time    : 2025/7/3 18:55
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
import sys
import apps.publish.ui.basewindow.basewiondow as basewindow
import apps.launch.maya.interface.mayaview as _mayaview

from apps.tools.maya.switch_bill_board import switch_bill_board_ui
reload(switch_bill_board_ui)
def load_switch_bill_board_ui():
    app = QApplication.instance()
    global switch_bill_boar_window
    try:
        switch_bill_boar_window.close()
        switch_bill_boar_window.deleteLater()
    except:
        pass

    if not app:
        app = QApplication(sys.argv)

    win_handle = switch_bill_board_ui.SwitchBillBoardUI()

    switch_bill_boar_window = basewindow.BaseWindow(_mayaview.get_maya_window(), "Switch BillBoard Tool", "BillBoard转换工具")

    switch_bill_boar_window.set_central_widget(win_handle)

    switch_bill_boar_window.setMinimumSize(400,260)
    switch_bill_boar_window.show()
    # win_handle.CloseSignal.connect(load_switch_bill_board_ui)
    app.exec_()