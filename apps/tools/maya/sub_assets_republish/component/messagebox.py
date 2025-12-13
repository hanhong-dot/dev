# coding:utf-8
# author:binglu.wang


try:
    from PySide2.QtWidgets import *
    from PySide2.QtGui import *
    from PySide2.QtCore import *
except:
    from Qt.QtWidgets import *
    from Qt.QtGui import *
    from Qt.QtCore import *

import lib.common.fileio as fileio
from apps.tools.maya.sub_assets_republish.component import resources

__all__ = ["msgview"]


def msgview(*args):
    '''
    消息提示框
    :param args:
    :return: 返回点击的按钮值，单按钮模式返回值恒为ture
    '''
    _msgview = MessageBox(*args)
    return _msgview.exec_()


class MessageBox(QMessageBox):
    LEVEl_TYPE = [
        "QMessageBox.Critical",
        "QMessageBox.Warning",
        "QMessageBox.Information"
    ]

    def __init__(self, text, level=2, buttonmode=0, parent=None):
        '''
        消息提示框
        :param text:显示信息
        :param level:信息级别，0是错误，1是警告，2以上是普通，默认2
        :param buttonmode:按钮状态，0是单按钮，1是双按钮，默认0
        :param parent:父窗口
        '''
        super(MessageBox, self).__init__(parent)
        # self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)
        self._text = text
        self._level = self._get_level(level)
        self._title = self._get_level_code(self._level)
        self._msg = QMessageBox
        self._buttonmode = buttonmode if buttonmode else self.singlebutton()
        self._build()
        # self.exec_()

    def _get_level_code(self, level_type):
        return level_type.split(".")[-1]

    def _get_level(self, level):
        return self.LEVEl_TYPE[level] if level <= len(self.LEVEl_TYPE) else self.LEVEl_TYPE[-1]

    def singlebutton(self):
        return 0

    def _build(self):
        self.setWindowFlags(Qt.Drawer)
        self.setMinimumWidth(450)
        self.setWindowTitle(self._title)
        self.setText(self._text)
        if self._buttonmode:
            self.cancelButton = self.addButton("cancel", self._msg.RejectRole)
            self.okButton = self.addButton("ok", self._msg.AcceptRole)
        else:
            self.okButton = self.addButton("确认", self._msg.AcceptRole)
        self.setIcon(eval(self._level))
        self._qss = fileio.read(resources.get(r"qss", "messagebox.qss"))
        if self._qss:
            self.setStyleSheet(self._qss)

    def resizeEvent(self, event):
        super(MessageBox, self).resizeEvent(event)
        # self.setFixedSize(450,30)

    def exec_(self):
        super(MessageBox, self).exec_()
        if self.clickedButton() == self.okButton:
            return True
        else:
            return False


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    print (msgview(u"红红火火恍恍惚惚哈哈哈", 0))
    sys.exit(app.exec_())
