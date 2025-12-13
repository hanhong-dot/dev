# -*- coding: utf-8 -*-#
# Python       : python 2.7.16
# -------------------------------------------------------------------------------
# NAME         : check_scrollarea
# Describe     : 说明描述
# Version      : v0.01
# Author       : linhuan
# Email        : hanhong@papegames.net
# DateTime     : 2022/5/1__14:43
# -------------------------------------------------------------------------------
# -------------------------------------------------------------------------------
# example:
# 
# -------------------------------------------------------------------------------

__AUTHOR__ = "linhuan"
__EMAIL__ = "hanhong@papegames.net"

import check_item
reload(check_item)

try:
    from PySide2.QtWidgets import *
    from PySide2.QtGui import *
    from PySide2.QtCore import *
except:
    from Qt.QtWidgets import *
    from Qt.QtGui import *
    from Qt.QtCore import *


class CheckScrollareaWidget(QWidget):
    def __init__(self, parent=None):
        super(CheckScrollareaWidget, self).__init__(parent)

        self.widgets = []

        self.setup()

    def setup(self):
        self._frame = QFrame()
        self._scrollarea = QScrollArea()
        self._scrollarea.setWidget(self._frame)
        self._scrollarea.setWidgetResizable(True)
        self._scrollarea.setBackgroundRole(QPalette.NoRole)
        self._scrollarea.setFrameShape(QFrame.NoFrame)

        self._check_scrolllayout = QVBoxLayout()
        self._check_scrolllayout.addWidget(self._scrollarea)
        self.set_checkitemwidgets()
        self.setLayout(self._check_scrolllayout)

    def set_checkitemwidgets(self):
        '''
        设置检查项
        :return:
        '''
        self._scrollayout = QVBoxLayout(self._frame)
        self._scrollayout.setContentsMargins(0, 0, 0, 0)
        _check_reference_weidget = check_item.CheckItemWidget(u"检查参考",
                                                              u"import check.check_exist_reference as check_exist_reference;reload(check_exist_reference);check_exist_reference.Check().checkinfo()",
                                                              u"import check.check_exist_reference as check_exist_reference;reload(check_exist_reference);check_exist_reference.Check().fix()",
                                                              False,u"检查文件中是否存在参考节点")



        self._scrollayout.addWidget(_check_reference_weidget)
        self.widgets.append(_check_reference_weidget)

        self._scrollayout.addStretch()
        self._frame.setLayout(self._scrollayout)

    def get_checkwidgets(self):
        return self.widgets

# def _trans_commond(self, info):
# 	'''
# 	如果"[]"转数组 否则返回字符串
# 	:param info:
# 	:return:
# 	'''
# 	if isinstance(info, str):
# 		if re.findall(r'[[](.*?)[]]', info) and ',' in info:
# 			getInfo = re.findall(r'[[](.*?)[]]', info)[0]
# 			return getInfo.split(',')
# 		else:
# 			return info


if __name__ == '__main__':
    import sys
    import method.shotgun.get_task as get_task

    app = QApplication(sys.argv)
    ui = CheckScrollareaWidget()
    ui.show()
    sys.exit(app.exec_())
