# -*- coding: utf-8 -*-#
# Python       : python 2.7.16
# -------------------------------------------------------------------------------
# NAME         : basewiondow
# Describe     : 基础面板
# Version      : v0.01
# Author       : linhuan
# Email        : hanhong@papegames.net
# DateTime     : 2022/5/20__10:30
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
	from PyQt5.QtWidgets import *
	from PyQt5.QtGui import *
	from PyQt5.QtCore import *

import webbrowser
import winreg

import os

import apps.publish.ui.basewindow.resources as resources

import lib.common.fileio as fileio

__all__ = ["BaseWindow", "BaseTitle", "BaseWidget", "BaseTail", "BaseButton", "BaseFrame"]


class BorderFrame(QFrame):
	'''边框类
	'''
	__ALLTYPE__ = ["top", "left", "right", "bottom", "top_left", "top_right", "bottom_left", "bottom_right"]
	__HTYPE__ = ["left", "right"]
	__VTYPE__ = ["top", "bottom"]
	__FTYPE__ = ["top_left", "bottom_right"]
	__BTYPE__ = ["top_right", "bottom_left"]
	
	def __init__(self, parent=None, area=None):
		super(BorderFrame, self).__init__(parent)
		self.setMouseTracking(True)
		self._is_pressed = False
		self._initial_position = QPoint(0, 0)
		self._area = area
		if parent:
			self._parent = self.parent()
	
	def enterEvent(self, event):
		if not self._is_pressed:
			if self._area in self.__HTYPE__:
				self.setCursor(QCursor(Qt.SizeHorCursor))
			if self._area in self.__VTYPE__:
				self.setCursor(QCursor(Qt.SizeVerCursor))
			if self._area in self.__FTYPE__:
				self.setCursor(QCursor(Qt.SizeFDiagCursor))
			if self._area in self.__BTYPE__:
				self.setCursor(QCursor(Qt.SizeBDiagCursor))
	
	def mousePressEvent(self, event):
		self._is_pressed = True
		if event.button() == Qt.LeftButton:
			self._drag_position = event.globalPos() - self.pos()
	
	def mouseReleaseEvent(self, event):
		self._is_pressed = False
	
	def mouseMoveEvent(self, event):
		_parent_rect = self._parent.rect()
		if self._is_pressed:
			if event.buttons() == Qt.LeftButton:
				_distance = event.globalPos() - self._drag_position
				if self._area == "left":
					_rect = QRect(self._parent_tlp.x() + _distance.x(),
					              self._parent_tlp.y(),
					              -(self._parent_tlp.x() + _distance.x() - self._parent_brp.x()),
					              _parent_rect.height())
				
				elif self._area == "top":
					_rect = QRect(self._parent_tlp.x(),
					              self._parent_tlp.y() + _distance.y(),
					              _parent_rect.width(),
					              -(self._parent_tlp.y() + _distance.y() - self._parent_brp.y()))
				if self._area == "right":
					_rect = QRect(self._parent_tlp.x(),
					              self._parent_tlp.y(),
					              _distance.x() + self.width(),
					              _parent_rect.height())
				
				elif self._area == "bottom":
					_rect = QRect(self._parent_tlp.x(),
					              self._parent_tlp.y(),
					              _parent_rect.width(),
					              _distance.y() + self.height())
				
				elif self._area == "top_left":
					_rect = QRect(self._parent_tlp.x() + _distance.x(),
					              self._parent_tlp.y() + _distance.y(),
					              -(self._parent_tlp.x() + _distance.x() - self._parent_brp.x()),
					              -(self._parent_tlp.y() + _distance.y() - self._parent_brp.y()))
				elif self._area == "top_right":
					_rect = QRect(self._parent_tlp.x(),
					              self._parent_tlp.y() + _distance.y(),
					              _distance.x() + self.width(),
					              -(self._parent_tlp.y() + _distance.y() - self._parent_brp.y()))
				elif self._area == "bottom_left":
					_rect = QRect(self._parent_blp.x() + _distance.x(),
					              self._parent_tlp.y(),
					              -(self._parent_blp.x() + _distance.x() - self._parent_brp.x()),
					              _distance.y() + self.height())
				elif self._area == "bottom_right":
					_rect = QRect(self._parent_tlp.x(),
					              self._parent_tlp.y(),
					              _distance.x() + self.width(),
					              _distance.y() + self.height())
				self._parent.setGeometry(_rect)
		else:
			self._parent_tlp = self._parent.mapToParent(_parent_rect.topLeft())
			self._parent_trp = self._parent.mapToParent(_parent_rect.topRight())
			self._parent_blp = self._parent.mapToParent(_parent_rect.bottomLeft())
			self._parent_brp = self._parent.mapToParent(_parent_rect.bottomRight())


class BaseButton(QPushButton):
	def __init__(self, parent=None, normal_icon=None, hover_icon=None, pressed_icon=None):
		super(BaseButton, self).__init__(parent)
		
		self._normal_icon, self._hover_icon, self._pressed_icon = None, None, None
		if normal_icon:
			self._normal_icon = QIcon(normal_icon)
		if hover_icon:
			self._hover_icon = QIcon(hover_icon)
		if pressed_icon:
			self._pressed_icon = QIcon(pressed_icon)
		
		self.setMouseTracking(True)
		self.setIcon(self._normal_icon)
	
	def enterEvent(self, event):
		super(BaseButton, self).enterEvent(event)
		if self._hover_icon:
			self.setIcon(self._hover_icon)
	
	def leaveEvent(self, event):
		super(BaseButton, self).leaveEvent(event)
		if self._normal_icon:
			self.setIcon(self._normal_icon)
	
	def mousePressEvent(self, event):
		super(BaseButton, self).mousePressEvent(event)
		if self._pressed_icon:
			self.setIcon(self._pressed_icon)
	
	def mouseReleaseEvent(self, event):
		super(BaseButton, self).mouseReleaseEvent(event)
		if self._normal_icon:
			self.setIcon(self._normal_icon)


class BaseWidget(QWidget):
	__moving = False
	
	def __init__(self, parent=None):
		super(BaseWidget, self).__init__(parent)
	
	def mousePressEvent(self, event):
		super(BaseWidget, self).mousePressEvent(event)
		if event.button() & Qt.LeftButton:
			self.__moving = True
			self._start_pos = event.globalPos()
			self._win_pos = self.frameGeometry().topLeft()
	
	def mouseMoveEvent(self, event):
		super(BaseWidget, self).mouseMoveEvent(event)
		if self.__moving:
			_pos = event.globalPos() - self._start_pos
			self.move(self._win_pos + _pos)
	
	def mouseReleaseEvent(self, event):
		super(BaseWidget, self).mouseReleaseEvent(event)
		self.__moving = False


class BaseFrame(QFrame, BaseWidget):
	def __init__(self, parent=None):
		super(BaseFrame, self).__init__(parent)


class BaseTail(QFrame):
	'''窗口底栏
	计划内容：
	信息显示槽
	进度条
	状态显示按钮（不可操作）
	'''
	
	def __init__(self, parent=None):
		super(BaseTail, self).__init__(parent)
		self._build()
	
	def _build(self):
		self._basetail_label = QLabel()
		self._basetail_label.setText("pipeline_version_v1.0 by linhuan")
		self._basetail_label.setAlignment(Qt.AlignHCenter | Qt.AlignBottom)
		self._basetail_layout = QHBoxLayout(self)
		self._basetail_layout.setSpacing(0)
		self._basetail_layout.setContentsMargins(0, 0, 0, 0)
		self._basetail_layout.addWidget(self._basetail_label)
	
	def set_info(self, desc):
		self._basetail_label.setText(desc)


class BaseTitle(QFrame):
	'''窗口标题栏
	'''
	__maxview__ = False
	__minview__ = False
	
	def __init__(self, parent=None):
		super(BaseTitle, self).__init__(parent)
		self._build()
		self._basetitle_max_button.clicked.connect(self._changemaxedicon)
	
	def _build(self):
		self.setMinimumHeight(22)
		self.setMaximumHeight(22)
		
		self._basetitle_icon_button = QPushButton()
		self._basetitle_icon_button.setObjectName("basetitle_icon_button")
		self._basetitle_icon_button.setFlat(True)
		self._basetitle_icon_button.setIcon(QIcon(resources.get("icon", "large", "logo2.png")))
		
		self._basetitle_label_button = QPushButton()
		self._basetitle_label_button.setObjectName("basetitle_label_button")
		self._basetitle_label_button.setFlat(True)
		
		self._basetitle_help_button = QPushButton()
		self._basetitle_help_button.setObjectName("basetitle_help_button")
		self._basetitle_help_button.setMinimumSize(22, 22)
		self._basetitle_help_button.setMaximumSize(22, 22)
		self._basetitle_help_button.setIcon(QIcon(resources.get("icon", "large", "help_hover.png")))
		
		self._basetitle_min_button = QPushButton()
		self._basetitle_min_button.setObjectName("basetitle_min_button")
		self._basetitle_min_button.setMinimumSize(22, 22)
		self._basetitle_min_button.setMaximumSize(22, 22)
		self._basetitle_min_button.setIcon(QIcon(resources.get("icon", "large", "minimum.png")))
		
		self._basetitle_max_button = QPushButton()
		self._basetitle_max_button.setObjectName("basetitle_max_button")
		self._basetitle_max_button.setMinimumSize(22, 22)
		self._basetitle_max_button.setMaximumSize(22, 22)
		self._basetitle_max_button.setIcon(QIcon(resources.get("icon", "large", "maximum.png")))
		
		self._basetitle_close_button = QPushButton()
		self._basetitle_close_button.setObjectName("basetitle_close_button")
		self._basetitle_close_button.setMinimumSize(22, 22)
		self._basetitle_close_button.setMaximumSize(22, 22)
		self._basetitle_close_button.setIcon(QIcon(resources.get("icon", "large", "close.png")))
		
		self._basetitle_layout = QHBoxLayout(self)
		self._basetitle_layout.setSpacing(0)
		self._basetitle_layout.setContentsMargins(0, 0, 0, 0)
		self._basetitle_layout.addWidget(self._basetitle_icon_button)
		self._basetitle_layout.addWidget(self._basetitle_label_button)
		self._basetitle_layout.addStretch()
		self._basetitle_layout.addWidget(self._basetitle_help_button)
		self._basetitle_layout.addWidget(self._basetitle_min_button)
		self._basetitle_layout.addWidget(self._basetitle_max_button)
		self._basetitle_layout.addWidget(self._basetitle_close_button)
	
	def _changemaxedicon(self):
		_value = self.__maxview__
		if _value:
			self._basetitle_max_button.setIcon(QIcon(resources.get("icon", "large", "maximum.png")))
		else:
			self._basetitle_max_button.setIcon(QIcon(resources.get("icon", "large", "maximumed.png")))
		self.__maxview__ = not _value


class BaseWindow(QMainWindow, BaseWidget):
	__initgeometry__ = None
	__bordersize__ = 5
	
	def __init__(self, parent=None, title="", icon=None):
		super(BaseWindow, self).__init__(parent)
		self._help_url = ""
		self.setWindowTitle(title)
		self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)
		self.setAttribute(Qt.WA_TranslucentBackground, True)
		self.setAttribute(Qt.WA_DeleteOnClose)
		self.__basebuild()
		self.__build_border()
		self.__set_center()
		
		if title:
			self.set_title_name(title)
		if icon:
			self.set_title_icon(QIcon(icon))
		self.__top_frame._basetitle_help_button.clicked.connect(self._showhelp)
		self.__top_frame._basetitle_min_button.clicked.connect(self.minimum_view)
		self.__top_frame._basetitle_max_button.clicked.connect(self.maximum_view)
		self.__top_frame._basetitle_close_button.clicked.connect(self.close)
	
	def __basebuild(self):
		# self.resize(960,540)
		
		self.__top_frame = BaseTitle()
		self.__top_frame.setObjectName("top_frame")
		self.__central_frame = QFrame()
		self.__central_frame.setObjectName("central_frame")
		self.__down_frame = BaseTail()
		self.__down_frame.setObjectName("down_frame")
		self.__down_frame.setMaximumHeight(30)
		
		self.__central_layout = QVBoxLayout(self.__central_frame)
		self.__central_layout.setSpacing(0)
		self.__central_layout.setContentsMargins(0, 0, 0, 0)
		
		self.__baseframe = QFrame()
		self.__baseframe.setMouseTracking(True)
		self.__baseframe.installEventFilter(self)
		self.__baseframe.setObjectName("baseframe")
		self.__baselayout = QVBoxLayout(self.__baseframe)
		self.__baselayout.setSpacing(2)
		self.__baselayout.setContentsMargins(self.__bordersize__, self.__bordersize__, self.__bordersize__,
		                                     self.__bordersize__)
		self.__baselayout.addWidget(self.__top_frame)
		self.__baselayout.addWidget(self.__central_frame)
		self.__baselayout.addWidget(self.__down_frame)
		self.setCentralWidget(self.__baseframe)
		self.__baseqss = fileio.read(resources.get(r"qss\basewindow", "basewindow.qss"))
		if self.__baseqss:
			self.setStyleSheet(self.__baseqss)
	
	def __build_border(self):
		self.__border_t = BorderFrame(self, "top")
		self.__border_l = BorderFrame(self, "left")
		self.__border_r = BorderFrame(self, "right")
		self.__border_b = BorderFrame(self, "bottom")
		
		self.__border_tl = BorderFrame(self, "top_left")
		self.__border_tr = BorderFrame(self, "top_right")
		self.__border_bl = BorderFrame(self, "bottom_left")
		self.__border_br = BorderFrame(self, "bottom_right")
		
		_border_qss = "QFrame{background-color: transparent}"
		self.__border_t.setStyleSheet(_border_qss)
		self.__border_l.setStyleSheet(_border_qss)
		self.__border_r.setStyleSheet(_border_qss)
		self.__border_b.setStyleSheet(_border_qss)
		self.__border_tl.setStyleSheet(_border_qss)
		self.__border_tr.setStyleSheet(_border_qss)
		self.__border_bl.setStyleSheet(_border_qss)
		self.__border_br.setStyleSheet(_border_qss)
	
	def __border_place(self):
		_rect = self.rect()
		_rx, _ry, _rh, _rw = _rect.x(), _rect.y(), _rect.height(), _rect.width()
		_h, _w = self.height(), self.width()
		_bps = _ry + self.height() - self.__bordersize__
		_lps = _rx + self.width() - self.__bordersize__
		
		self.__border_t.setGeometry(_rx + self.__bordersize__, _ry,
		                            _rw - self.__bordersize__ * 2, self.__bordersize__)
		self.__border_l.setGeometry(_rx, _ry + self.__bordersize__,
		                            self.__bordersize__, _rh - self.__bordersize__ * 2)
		self.__border_b.setGeometry(_rx + self.__bordersize__, _bps,
		                            _rw - self.__bordersize__ * 2, self.__bordersize__)
		self.__border_r.setGeometry(_lps, _ry + self.__bordersize__,
		                            self.__bordersize__, _rh - self.__bordersize__ * 2)
		
		self.__border_tl.setGeometry(_rx, _ry,
		                             self.__bordersize__, self.__bordersize__)
		self.__border_tr.setGeometry(_lps, _ry,
		                             self.__bordersize__, self.__bordersize__)
		self.__border_bl.setGeometry(_rx, _bps,
		                             self.__bordersize__, self.__bordersize__)
		self.__border_br.setGeometry(_lps, _bps,
		                             self.__bordersize__, self.__bordersize__)
	
	def __set_center(self):
		_parent = self.parent()
		if _parent:
			_mp = _parent.geometry()
			_wp = self.geometry()
			self.move(_mp.x() + (_mp.width() / 1.5 - _wp.width()) / 2,
			          _mp.y() + (_mp.height() / 4 - _wp.height()) / 2)
	
	def set_central_widget(self, widget):
		'''设置中心组件
			只允许单个组件存在
		'''
		for i in range(self.__central_layout.count()):
			_item = self.__central_layout.itemAt(i)
			self.__central_layout.removeItem(_item)
		self.__central_layout.addWidget(widget)
	
	def set_title_name(self, text):
		'''设置窗口标题
		'''
		self.__top_frame._basetitle_label_button.setText(text)
		self.setObjectName(u"pipeline_{}".format(text))
	
	def set_title_icon(self, icon):
		'''设置窗口标题图标
		'''
		self.__top_frame._basetitle_label_button.setIcon(QIcon(icon))
	
	def set_tail_test(self, test):
		self.__down_frame.set_info(test)
	
	def set_help(self, url=None, data=None):
		if url:
			self._help_url = url
	
	def set_modal(self):
		self.setWindowModality(Qt.WindowModal)
	
	def close(self):
		super(BaseWindow, self).close()
		import gc
		gc.collect(0)
	
	def minimum_view(self):
		if self.isMinimized():
			self.showNormal()
		else:
			self.showMinimized()
	
	def maximum_view(self):
		if self.isMaximized():
			self.showNormal()
		else:
			self.showMaximized()
			if self.__top_frame.__minview__:
				self.minimum_view()
	
	def resizeEvent(self, event):
		super(BaseWindow, self).resizeEvent(event)
		self.__border_place()
	
	def test(self):
		print("help")
	
	def _showhelp(self):
		'''
		显示帮助
		这里会优先查询chrome，没有会使用ie
		:return:
		'''
		
		if self._help_url:
			# _chrome = r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe'
			try:
				query_path = "SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe"
				reginfo = winreg.OpenKeyEx(winreg.HKEY_LOCAL_MACHINE, query_path)
				_chromepath, value = winreg.QueryValueEx(reginfo, "")
			except:
				_chromepath = ""
			if os.path.exists(_chromepath):
				webbrowser.register("chrome", None, webbrowser.BackgroundBrowser(_chromepath))
				webbrowser.get("chrome").open(self._help_url)
			else:
				webbrowser.open(self._help_url)


if __name__ == '__main__':
	import sys
	
	app = QApplication(sys.argv)
	win = BaseWindow(title="base")
	win.show()
	sys.exit(app.exec_())
