# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       : com_ui
# Describe   : motionbuilder 中添加布局
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2023/5/12__17:11
# -------------------------------------------------------
import apps.tools.motionbuilder.item_chr_link.ui as item_link_ui
import sys
try:
    from PySide2 import QtCore
    from PySide2.QtWidgets import *
    from PySide2.QtGui import *
    from PySide2.QtCore import *
except:
    from Qt.QtWidgets import *
    from Qt.QtGui import *
    from Qt.QtCore import *

from pyfbsdk import FBApplication
from pyfbsdk import FBMessageBox
from pyfbsdk_additions import *
import apps.publish.ui.basewindow.basewiondow as basewindow
def get_mainwindows():
    return qApp.topLevelWidgets()[0]
def show():
    FBApplication().FBCreate()
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)

    mobu_link_tools = basewindow.BaseWindow(get_mainwindows(), title=u"Item Link Tool")

    mobu_link_tools.set_central_widget(item_link_ui.ItemLinkUI())
    mobu_link_tools.set_modal()
    mobu_link_tools.setMinimumSize(500, 600)
    mobu_link_tools.show()
    app.exec_()
