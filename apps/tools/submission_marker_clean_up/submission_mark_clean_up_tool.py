# -*- coding: utf-8 -*-#
# Python     : 
# -------------------------------------------------------
# NAME       :submission_mark_clean_up_tool.py
# Describe   :
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2024/11/25 19:08
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

from apps.tools.submission_marker_clean_up.submission_ui import SubmissionMarkerCleanUpUI


def load_submission_ui():
    app = QApplication.instance()
    global collect
    try:
        collect.close()
        collect.deleteLater()
    except:
        pass

    if not app:
        app = QApplication(sys.argv)
    Submission = basewindow.BaseWindow(title="Submission Marker Clean Up Tool")
    Submission.set_central_widget(SubmissionMarkerCleanUpUI())
    # collect.set_help(url=r"https://papergames.feishu.cn/wiki/SavswLVLLinFsAkRuzncIVVenCR?from=from_copylink")
    Submission.setMinimumSize(400, 300)
    Submission.show()
    app.exec_()

load_submission_ui()
