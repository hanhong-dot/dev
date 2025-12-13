# -*- coding: utf-8 -*-
# -----------------------------------
# @File    : load_ai_video_match_ui.py
# @Author  : linhuan
# @Time    : 2025/7/10 17:59
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
sys.path.append('z:/dev')

sys.path.append(r'Z:\dev\Ide\Python\2.7.11\Lib\site-packages')
from apps.tools.common.ai_video_match_tool import ai_video_match_ui
import apps.publish.ui.basewindow.basewiondow as basewindow


def load_ai_video_match_ui():
    """
    加载AI视频对比匹配工具UI
    :return: bool, QWidget
    """
    app = QApplication.instance()
    global ai_video_match_win
    try:
        ai_video_match_win.close()
        ai_video_match_win.deleteLater()
    except:
        pass

    if not app:
        app = QApplication(sys.argv)

    ai_video_match_win = basewindow.BaseWindow(title=u'AI视频对比工具')

    ai_video_match_win.set_central_widget(ai_video_match_ui.AIVideoMatchUI())
    ai_video_match_win.set_help(url=r"https://papergames.feishu.cn/wiki/VjIVwJqIMibBI1kyCBOc6vqPnqb?from=from_copylink")
    ai_video_match_win.setMinimumSize(1200, 600)
    # ai_video_match_win.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.WindowCloseButtonHint | Qt.WindowMinimizeButtonHint)
    # ai_video_match_win.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint)
    # ai_video_match_win.setWindowFlags(Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint)
    #
    # ai_video_match_win.set_modal()
    # ai_video_match_win.minimum_view()
    # ai_video_match_win.maximum_view()

    # ai_video_match_win.resizeEvent = handle.resizeEvent

    ai_video_match_win.show()
    app.exec_()


if __name__ == '__main__':
    load_ai_video_match_ui()
