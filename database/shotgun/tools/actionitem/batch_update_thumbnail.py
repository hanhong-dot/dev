# -*- coding: utf-8 -*-
# -----------------------------------
# @File    : batch_update_thumbnail.py
# @Author  : linhuan
# @Time    : 2025/8/23 19:41
# @Description : 
# -----------------------------------
import sys
import os

sys.path.append('Z:/dev')

import database.shotgun.tools.actionitem.action_item_server as action_item_server

try:
    from PySide2.QtWidgets import *
    from PySide2.QtGui import *
    from PySide2.QtCore import *
except:
    from PyQt5.QtWidgets import *
    from PyQt5.QtGui import *
    from PyQt5.QtCore import *


class BatchUpdateThumbnail(QWidget):
    def __init__(self, parent=None):
        super(BatchUpdateThumbnail, self).__init__(parent)
        self.project = sys.argv[1]
        self.select_ids = sys.argv[2].split(',')
        self.entity_type = sys.argv[3]
        self.sg = action_item_server.action_login()
        if not self.select_ids:
            return
        self.__init_ui()
        self.__connect_signal()

    def __init_ui(self):
        self.setWindowFlags(Qt.WindowCloseButtonHint | Qt.WindowStaysOnTopHint)
        self.setWindowTitle(u'批量更新缩略图')
        self.__layout = QVBoxLayout(self)

        self.__select_layout = QHBoxLayout()
        # self.__select_label = QLabel(u'请选择缩略图')
        self.__choose_thumbnail = QLineEdit()
        self.__choose_thumbnail.setPlaceholderText(u"请输入或选择缩略图路径(支持png,jpg格式)")
        self.__choose_thumbnail.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.__choose_thumbnail.setFixedHeight(30)
        self.__choose_button = QPushButton(u"选择文件")
        self.__choose_button.setFixedHeight(30)
        self.__choose_button.setAutoDefault(True)
        # self.__select_layout.addWidget(self.__select_label)
        self.__select_layout.addWidget(self.__choose_thumbnail)
        self.__select_layout.addWidget(self.__choose_button)
        self.__layout.addLayout(self.__select_layout)

        self.__confirm_layout = QHBoxLayout()

        self.__confirm_button = QPushButton(u"确认")
        self.__confirm_button.setStyleSheet("background-color: rgb(30, 90, 87); color: white;")

        self.__cancel_button = QPushButton(u"取消")
        self.__confirm_layout.addStretch()
        self.__confirm_layout.addWidget(self.__confirm_button)
        self.__confirm_layout.addWidget(self.__cancel_button)
        self.__layout.addLayout(self.__confirm_layout)

    def __connect_signal(self):
        self.__choose_button.clicked.connect(self.__on_choose_thumbnail)
        self.__confirm_button.clicked.connect(self.__on_confirm)
        self.__cancel_button.clicked.connect(self.__close)

    def __on_choose_thumbnail(self):
        __thumbnail_file_path = self.__choose_thumbnail.text().strip() if self.__choose_thumbnail.text().strip() else ''

        self.__thumbnail_file_path = QFileDialog.getOpenFileName(self, u"选择缩略图文件", __thumbnail_file_path,
                                                                 u"Image Files (*.png *.jpg);;All Files (*)")
        if self.__thumbnail_file_path:
            self.__choose_thumbnail.setText(self.__thumbnail_file_path[0])

    def __on_confirm(self):
        thumbnail_path = self.__choose_thumbnail.text().strip()
        if not thumbnail_path or not os.path.isfile(thumbnail_path):
            QMessageBox.warning(self, u"警告", u"请选择有效的缩略图文件路径！", QMessageBox.Ok)
            return
        if not thumbnail_path.lower().endswith(('.png', '.jpg', '.jpeg')):
            QMessageBox.warning(self, u"警告", u"请选择png或jpg格式的图片文件！", QMessageBox.Ok)
            return

        success, reslult = self.batch_update_thumbnails(thumbnail_path)
        if success:
            QMessageBox.information(self, u"成功", u"缩略图已成功更新！", QMessageBox.Ok)
            self.close()
        else:
            QMessageBox.critical(self, u"错误", u"更新缩略图时出错，请重试！", QMessageBox.Ok)

    def batch_update_thumbnails(self, thumbnail_path):
        pass

        if not self.select_ids:
            return False, u'未选择资产,请选择'
        for entity_id in self.select_ids:
            entity_id = int(entity_id)
            try:
                self.sg.upload_thumbnail(self.entity_type, entity_id, thumbnail_path)
            except Exception as e:
                print("Error,No updating  Asset {} thumbnail : {}".format(entity_id, e))
                return False, "Error,No updating  Asset {} thumbnail : {}".format(entity_id, e)
        return True, "Success"

    def __close(self):
        self.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = BatchUpdateThumbnail()
    window.resize(600, 120)
    window.show()
    sys.exit(app.exec_())
