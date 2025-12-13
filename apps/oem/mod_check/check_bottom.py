# -*- coding: utf-8 -*-#
# Python       : python 2.7.16
# -------------------------------------------------------------------------------
# NAME         : check_bottom
# Describe     : 框架底部显示
# Version      : v0.01
# Author       : linhuan
# Email        : hanhong@papegames.net
# DateTime     : 2022/5/23__11:19
# -------------------------------------------------------------------------------
# -------------------------------------------------------------------------------
# example:
# 
# -------------------------------------------------------------------------------



try:
    from PySide2.QtWidgets import *
    from PySide2.QtGui import *
    from PySide2.QtCore import *
except:
    from Qt.QtWidgets import *
    from Qt.QtGui import *
    from Qt.QtCore import *


class CheckBottomWidget(object):
    def checkbottom_setup(self):
        # self._check_bottomframe = QFrame(self)
        
        self._check_bottomframe = QFrame()
        self._check_displayallbox = QCheckBox()
        self._check_displayallbox.setText(u"显示全部检查项")

        self._checkfixbox = QCheckBox()
        self._checkfixbox.setMinimumSize(75, 30)
        self._checkfixbox.setText(u"自动修复")

        self.check_allpushbutton = QPushButton()
        self.check_allpushbutton.setMinimumSize(75, 30)
        self.check_allpushbutton.setText(u"检查全部")

        self._checkalllayout = QHBoxLayout()
        self._checkalllayout.setSpacing(2)
        self._checkalllayout.setContentsMargins(0, 0, 0, 0)
        self._checkalllayout.addStretch()
        self._checkalllayout.addWidget(self._check_displayallbox)
        self._checkalllayout.addWidget(self._checkfixbox)
        self._checkalllayout.addWidget(self.check_allpushbutton)

        self._check_bottomframe.setLayout(self._checkalllayout)

        self.check_allpushbutton.clicked.connect(self.check_all)
        self._check_displayallbox.stateChanged.connect(self._change_show)
        


    def check_all(self):
        pass

    def _change_show(self):
        '''设置显示模式
        '''
        pass


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    win = CheckBottomWidget()
    win.show()
    sys.exit(app.exec_())