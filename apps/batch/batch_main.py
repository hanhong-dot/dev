# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       : batch_main
# Describe   : 说明描述
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2024/1/10__17:56
# -------------------------------------------------------
import sys
sys.path.append('z:/dev')
sys.path.append(r'Z:\dev\Ide\Python\2.7.11\Lib\site-packages')
# sys.path.append(r'Z:\dev\Ide\python310\Lib\site-packages')

# sys.path.append(r'')

from apps.batch.ui.batch_ui import Batch
try:
    from PySide2.QtCore import *
    from PySide2.QtGui import *
    from PySide2.QtWidgets import *

except:
    from PyQt5.QtWidgets import *
    from PyQt5.QtGui import *
    from PyQt5.QtCore import *


def batch_main():
    project_list = "[{'id': 114, 'name': 'X3', 'type': 'Project', 'sg_type': 'Game'}]"
    app = QApplication(sys.argv)
    dialog = Batch(project_list)
    dialog.show()
    sys.exit(app.exec_())

batch_main()

