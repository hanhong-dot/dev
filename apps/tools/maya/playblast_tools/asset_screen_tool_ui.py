# -*- coding: utf-8 -*-
# author: linhuan
# file: asset_screen_tool_ui.py
# time: 2025/11/5 15:21
# description:
import os.path

try:
    from PySide2.QtWidgets import *
    from PySide2.QtGui import *
    from PySide2.QtCore import *
except:
    from Qt.QtWidgets import *
    from Qt.QtGui import *
    from Qt.QtCore import *
import apps.tools.maya.playblast_tools.playblast_fun as playblast_fun

reload(playblast_fun)


class AssetScreenToolUI(QWidget):
    def __init__(self, parent=None):
        super(AssetScreenToolUI, self).__init__(parent)
        self.setWindowTitle(u'资产截屏工具')
        self.resize(300, 250)
        self._main_layout = QVBoxLayout()
        self.setLayout(self._main_layout)
        self.__init_ui()
        self.__connect_signals()

    def __init_ui(self):
        self.__size_layout = QVBoxLayout()
        self.__size_label = QLabel()
        self.__size_label.setText(u"截屏尺寸:")
        self.__width_label = QLabel()
        self.__width_label.setText(u"宽度")
        self.__size_label.setFont(QFont("Arial", 15, QFont.Bold))
        # self.__size_label.setStyleSheet("Arial;margin-top:15px;Bold;")

        # 滑条

        # self.__width_textbox.setText("4000")
        self.__width_lineedit = QSpinBox()
        self.__width_lineedit.setRange(100, 10000)
        self.__width_lineedit.setValue(4000)
        self.__height_label = QLabel()
        self.__height_label.setText(u"高度")
        self.__hight_lineedit = QSpinBox()
        self.__hight_lineedit.setRange(100, 10000)
        self.__hight_lineedit.setValue(4000)

        self.__size_layout.addWidget(self.__size_label)
        self.__size_layout.addWidget(self.__width_label)
        self.__size_layout.addWidget(self.__width_lineedit)
        self.__size_layout.addWidget(self.__height_label)
        self.__size_layout.addWidget(self.__hight_lineedit)
        self.__size_layout.addStretch()

        self.__output_layout = QVBoxLayout()
        self.__output_label = QLabel()
        self.__output_label.setText(u"输出路径:")
        self.__output_label.setFont(QFont("Arial", 15, QFont.Bold))
        # self.__output_label.setStyleSheet("Arial; margin-top:15px;Bold;")
        self.__out_layout = QHBoxLayout()
        self.__output_lineedit = QLineEdit()
        self.__output_browse_button = QPushButton(u"浏览")
        self.__out_layout.addWidget(self.__output_lineedit)
        self.__out_layout.addWidget(self.__output_browse_button)

        self.__output_layout.addWidget(self.__output_label)
        self.__output_layout.addLayout(self.__out_layout)

        # 添加间隔线
        self.__output_layout.addWidget(self._create_separator())
        self.__output_layout.addStretch()

        self._main_layout.addLayout(self.__size_layout)
        self._main_layout.addLayout(self.__output_layout)

        self._button_layout = QHBoxLayout()
        self._screenshot_button = QPushButton(u"执行截屏")
        # self._screenshot_button.setFixedHeight(30)
        self._screenshot_button.setStyleSheet("background-color: rgb(30, 90, 87); color: white;Height:30px;")

        self._button_layout.addWidget(self._screenshot_button)

        self._main_layout.addLayout(self._button_layout)

    def __connect_signals(self):
        self.__output_browse_button.clicked.connect(self.__browse_output_path_clicked)
        self._screenshot_button.clicked.connect(self.__screenshot_clicked)

    def __browse_output_path_clicked(self):
        _dir = QFileDialog.getExistingDirectory(self, u"选择输出路径", "./")
        if _dir:
            self.__output_lineedit.setText(_dir)

    def __screenshot_clicked(self):
        width = self.__width_lineedit.value()
        height = self.__hight_lineedit.value()
        #判断奇偶数
        if int(width) % 2 != 0:
            return QMessageBox.warning(self, u"警告", u"宽度需要为偶数，请检查")
        if int(height) % 2 != 0:
            return QMessageBox.warning(self, u"警告", u"高度需要为偶数，请检查")
        output_dir = self.__output_lineedit.text().strip()
        output_dir = u'{}'.format(output_dir.replace('\\', '/'))
        if not output_dir:

            QMessageBox.warning(self, u"警告", u"请设置输出路径")
            return

        if not os.path.isdir(output_dir):
            QMessageBox.critical(self, u"错误", u"需要输入有效的文件夹,请检查")
            return
        if not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir)
            except Exception as e:
                QMessageBox.critical(self, u"错误", u"输出路径创建失败，错误信息：{}".format(e))
                return
        success, msg = playblast_fun.asset_screen(width=width, height=height, output_dir=output_dir)
        if success:
            QMessageBox.information(self, u"成功", u"截屏成功，文件保存于：{}".format(msg))
        else:
            QMessageBox.critical(self, u"失败", u"截屏失败，错误信息：{}".format(msg))

    def _create_separator(self):
        # 线再靠下
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setLineWidth(1)
        return line


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    window = AssetScreenToolUI()
    window.show()
    sys.exit(app.exec_())
