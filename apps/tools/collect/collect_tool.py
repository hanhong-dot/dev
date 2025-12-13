# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       : collect_tool
# Describe   : 说明描述
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2024/2/18__18:00
# -------------------------------------------------------
import sys
sys.path.append('Z:/dev')

try:
    from PySide2.QtWidgets import *
    from PySide2.QtGui import *
    from PySide2.QtCore import *
except:
    from PyQt5.QtWidgets import *
    from PyQt5.QtGui import *
    from PyQt5.QtCore import *

import apps.publish.ui.basewindow.basewiondow as basewindow

from apps.tools.collect.collect_ui import CollectUI


def load_collect_ui():
    app = QApplication.instance()
    global collect
    try:
        collect.close()
        collect.deleteLater()
    except:
        pass

    if not app:
        app = QApplication(sys.argv)
    collect = basewindow.BaseWindow(title="Collect")
    collect.set_central_widget(CollectUI())
    collect.set_help(url=r"https://papergames.feishu.cn/wiki/SavswLVLLinFsAkRuzncIVVenCR?from=from_copylink")
    collect.setMinimumSize(300, 400)
    collect.show()
    app.exec_()


load_collect_ui()

# if __name__ == '__main__':
#     load_collect_ui()
#     # pass
