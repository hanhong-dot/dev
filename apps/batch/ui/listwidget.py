# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------------
# NAME         : check_listwidget
# Describe     : 信息面板，支持彩色输出
# Version      : v0.02
# Author       : linhuan
# Email        : hanhong@papegames.net
# DateTime     : 2022/5/1__14:43
# -------------------------------------------------------------------------------

__AUTHORZH__ = u"韩虹"
__AUTHOR__ = "linhuan"
__EMAIL__ = "hanhong@papegames.net"

try:
    from PySide2.QtWidgets import *
    from PySide2.QtGui import *
    from PySide2.QtCore import *
except:
    from Qt.QtWidgets import *
    from Qt.QtGui import *
    from Qt.QtCore import *


class ListWidget(QFrame):
    def __init__(self, parent=None):
        super(ListWidget, self).__init__(parent)
        self.list_setup()

    def list_setup(self):
        self._grpboxwidget = QGroupBox(u'反馈信息')
        self._listwidget = QListWidget()
        self._listwidget.setSelectionMode(QAbstractItemView.ContiguousSelection)
        self._listwidget.setMinimumHeight(200)
        self._listwidget.setVerticalScrollMode(QAbstractItemView.ScrollPerItem)

        self._listlayout = QVBoxLayout()
        self._listlayout.addWidget(self._listwidget)
        self._grpboxwidget.setLayout(self._listlayout)

        self._grplayout = QHBoxLayout()
        self._grplayout.addWidget(self._grpboxwidget)
        self.setLayout(self._grplayout)

    def _clear_info(self):
        """清空列表"""
        self._listwidget.clear()

    def add_info(self, text, level="info"):
        """
        添加带颜色的提示信息
        level 可选：
            "info"    —— 默认灰黑色
            "success" —— 绿色
            "warning" —— 橙色
            "error"   —— 红色
            "debug"   —— 蓝色
        """
        item = QListWidgetItem(text)
        font = QFont("Consolas", 10)
        item.setFont(font)

        color_map = {
            "info": QColor(50, 50, 50),
            "success": QColor(0, 160, 0),
            "warning": QColor(200, 120, 0),
            "error": QColor(200, 0, 0),
            "debug": QColor(30, 80, 180),
        }

        color = color_map.get(level.lower(), QColor(50, 50, 50))
        item.setForeground(QBrush(color))
        self._listwidget.addItem(item)

        # 自动滚动到底部
        self._listwidget.scrollToBottom()


if __name__ == '__main__':
    import sys
    log_file=r'D:\temp_info\batch_publish\40bb0b9ced324e9cb26d23aadee6f016.log'


    app = QApplication(sys.argv)
    win = ListWidget()
    win.resize(400, 300)
    win.show()

    # 测试输出
    # win.add_info("初始化完成", "info")
    # win.add_info("文件加载成功", "success")
    # win.add_info("检测到未配置项", "warning")
    # win.add_info("无法连接服务器", "error")
    # win.add_info("调试模式已开启", "debug")

    sys.exit(app.exec_())

