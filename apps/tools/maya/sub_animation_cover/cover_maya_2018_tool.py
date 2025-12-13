# -*- coding: utf-8 -*-#
# Python     :
# -------------------------------------------------------
# NAME       :submission_mark_clean_up_tool.py
# Describe   :
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2025/03/03 16:51
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

from apps.tools.maya.sub_animation_cover.sub_cover_ui import SubmissionMayaCoverUI


def load_cover_submission_ui():
    app = QApplication.instance()
    global collect
    try:
        collect.close()
        collect.deleteLater()
    except:
        pass

    if not app:
        app = QApplication(sys.argv)
    Cover_Submission = basewindow.BaseWindow(title="Submission Cover to Maya2018 Tool")
    Cover_Submission.set_central_widget(SubmissionMayaCoverUI())
    # collect.set_help(url=r"https://papergames.feishu.cn/wiki/SavswLVLLinFsAkRuzncIVVenCR?from=from_copylink")
    Cover_Submission.setMinimumSize(450, 200)
    Cover_Submission.show()
    app.exec_()


load_cover_submission_ui()
