# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       : image_label
# Describe   : 用来显示资产的缩略图，鼠标放上去可以查看大图
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2023/12/7__16：51
# -------------------------------------------------------
import numpy
import sys
import os

try:
    from PySide2.QtGui import *
    from PySide2.QtCore import *
    from PySide2.QtWidgets import *
except:
    from Qt.QtWidgets import *
    from Qt.QtGui import *
    from Qt.QtCore import *

from lib.common import apps_path,ico_path


class TaskLabel(QFrame):
    pressed_signal = Signal(list)
    selected_signal = Signal(object)

    def __init__(self,task_data):
        '''
        根据资产数据创建图片以及相关信息数据
        :param asset_data:
        '''
        super(TaskLabel, self).__init__()
        self.setLayout(QVBoxLayout())
        self.layout().setContentsMargins(1, 1, 1, 1)
        # 数据，资产ID
        self.task_data = task_data
        # self.model_instance = model_instance
        self.tag = False
        self.resource_path = '{}/tools/maya/sub_assets_republish/resources'.format(apps_path())
        # self.asset_library_path = RounterInfo.get_m_path()

        self.add_media()
        self.add_file_name()
        # self.add_file_size()
        self.setAcceptDrops(True)
    def add_media(self):
        '''
        :return:
        '''


        full_path = self.task_data['version_file']

        full_path = full_path.replace('\\', '/')

        self.media_widget = MediaWidget(media_path=full_path, size=(120, 80))
        self.media_widget.setStyleSheet('border:0px solid red')
        self.media_widget.load_info()
        self.layout().addWidget(self.media_widget)

    def add_file_name(self):
        '''
        加载文件名称标签
        :return: None
        '''
        base_name = self.task_data['task_name']
        file_name = QLabel(base_name)
        file_name.setMaximumHeight(20)
        file_name.setStyleSheet("border:0px solid red")
        self.layout().addWidget(file_name)
        file_name.setAlignment(Qt.AlignCenter)

    def add_file_size(self):
        '''
        加载显示文件尺寸标签
        :return:
        '''
        size = 80
        media_size = QLabel(size)
        media_size.setMaximumHeight(20)
        media_size.setStyleSheet("border:0px solid red")
        self.layout().addWidget(media_size)
        media_size.setAlignment(Qt.AlignCenter)

    def mousePressEvent(self, event):
        '''
        鼠标点击时，处理鼠标点击事件
        :param event: 事件实例
        :return: None
        '''
        if event.button() == Qt.LeftButton:
            # self.setFrameShape(QFrame.Panel)
            # self.setFrameShadow(QFrame.Sunken)
            self.drag_start_position = event.pos()
            # print self.pos()
            # 发送按压信号
            asset_data = self.task_data
            # model_instance = self.model_instance
            # self.pressed_signal.emit([asset_data, model_instance])
            self.selected_signal.emit(self)

        super(TaskLabel, self).mousePressEvent(event)
        #

    def leaveEvent(self, event):
        '''
        鼠标离开部件时，触发该事件。
        :param event: 事件类
        :return: None
        '''
        self.media_widget.search_button.hide()
        super(TaskLabel, self).leaveEvent(event)

    def enterEvent(self, event):
        '''
        进入事件，鼠标进入时，触发该事件
        :param event: 事件
        :return: None
        '''
        self.media_widget.search_button.show()
        super(TaskLabel, self).enterEvent(event)

    def mouseMoveEvent(self, event):
        '''
        鼠标移动时，触发该事件
        :param event: 事件
        :return: None
        '''
        if not (event.buttons() and Qt.LeftButton):
            return
        point = event.pos() - self.drag_start_position
        if self.mandistance(point) < QApplication.startDragDistance():
            return False

    def mandistance(self, point):
        '''
        计算中心点位置
        :param point: QPoint
        :return: 长度
        '''
        x = point.x()
        y = point.y()
        d1 = numpy.sum(numpy.abs(x - y))
        return d1


class MediaWidget(QLabel):
    '''
    显示图片或者部件并为将来的拓展留空间
    '''

    def __init__(self, media_path='', size=''):
        super(MediaWidget, self).__init__()
        # self.setAttribute(Qt.WA_StyledBackground)
        # self.setStyleSheet('border-radius: 20px;')
        self.media_path = media_path
        # self.media_path = self.media_path.decode("utf8")
        self.tag = False
        '''
        with open(media_path, 'rb') as filet:
            file_data = filet.read()
        qt_byte = QByteArray()
        qt_byte.append(file_data)
        picture = QPixmap()
        picture.loadFromData(qt_byte)
        picture = QPixmap(media_path)
        self.setPixmap(picture)
        self.setScaledContents(True)
        #self.setStyleSheet('border-radius: 20px;')
        '''
        self.search_button = SearchButton(self, media_path=self.media_path)
        self.search_button.hide()

    def load_info(self):
        load_status = True
        if not self.tag:
            self.tag = True
        else:
            return True
        try:
            with open(self.media_path, 'rb') as filet:
                file_data = filet.read()
        except Exception, e:
            load_status = False
        if load_status == False:
            return False
        qt_byte = QByteArray()
        qt_byte.append(file_data)
        picture = QPixmap()
        picture.loadFromData(qt_byte)
        picture = QPixmap(self.media_path)
        self.setPixmap(picture)
        self.setScaledContents(True)


class SearchButton(QLabel):
    def __init__(self, parent, media_path=''):
        super(SearchButton, self).__init__(parent)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.init()
        self.setFixedSize(QSize(24, 24))
        self.media_path = media_path

    def init(self):
        icon_path = ico_path()
        with open(icon_path + '/sq32/library/cam.png', 'rb') as filet:
            file_data = filet.read()
        qt_byte = QByteArray()
        qt_byte.append(file_data)
        picture = QPixmap()
        picture.loadFromData(qt_byte)
        self.setPixmap(picture)
        self.setScaledContents(True)

    def mousePressEvent(self, event):
        '''
        点击后，显示图片原图
        :param event:
        :return: None
        '''
        rect = QApplication.desktop().availableGeometry(self)
        width = rect.width()
        height = rect.height()
        # 查找原图路径
        big_size_file = ''
        base_dir = os.path.dirname(self.media_path)

        for file in os.listdir(base_dir):
            if os.path.isfile(os.path.join(base_dir, file)):
                if '_mini' not in file and '.db' not in file:
                    big_size_file = os.path.join(base_dir, file)
        self.display_image = DisplayImage(big_size_file)
        self.display_image.init()
        posg = self.mapToGlobal(self.pos())
        size = self.display_image.size()
        desktop = QApplication.desktop().screenGeometry()
        screen_height = desktop.height()
        screen_width = desktop.width()
        # 获取分辨率,重新上传
        if posg.x() < 0:
            self.display_image.move(screen_width / 4 - screen_width, screen_height / 4)
        else:
            self.display_image.move(screen_width / 4, screen_height / 4)
        self.display_image.show()
        super(SearchButton, self).mousePressEvent(event)

    def leaveEvent(self, event):
        super(SearchButton, self).leaveEvent(event)


class DisplayImage(QLabel):
    def __init__(self, media_path):
        # self.setWindowFlags(Qt.Window)
        super(DisplayImage, self).__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.media_path = media_path

    def init(self):
        with open(self.media_path, 'rb') as filet:
            file_data = filet.read()
        qt_byte = QByteArray()
        qt_byte.append(file_data)
        picture = QPixmap()
        picture.loadFromData(qt_byte)
        self.setPixmap(picture)
        self.setScaledContents(True)

    def leaveEvent(self, event):
        # self.close()
        # self.destroy()
        super(DisplayImage, self).leaveEvent(event)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()
            self.destroy()
        super(DisplayImage, self).keyPressEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.m_pressed = True
            self.m_point = event.pos()
        super(DisplayImage, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.m_pressed:
            self.move(event.pos() - self.m_point + self.pos())
        super(DisplayImage, self).mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self.m_pressed = False
        super(DisplayImage, self).mouseReleaseEvent(event)


# if __name__ == '__main__':
#     task_data = [{'work_file': 'M:\\projects\\x3\\work\\assets\\role\\FY001C\\rbf\\maya\\FY001C.rbf.v007.ma', 'publish_file': 'M:\\projects\\x3\\publish\\assets\\role\\FY001C\\rbf\\maya\\FY001C.rbf.ma', 'vesion_file': 'M:\\projects\\X3\\publish\\assets\\role\\FY001C\\rbf\\maya\\FY001C.rbf.v002.png', 'task_id': 82711, 'task_name': 'rbf'}, {'work_file': 'M:\\projects\\x3\\work\\assets\\role\\FY001C\\rig\\maya\\FY001C.drama_rig.v008.ma', 'publish_file': 'M:\\projects\\x3\\publish\\assets\\role\\FY001C\\rig\\maya\\FY001C.drama_rig.ma', 'vesion_file': 'M:\\projects\\X3\\publish\\assets\\role\\FY001C\\rig\\maya\\FY001C.drama_rig.v004.png', 'task_id': 82712, 'task_name': 'drama_rig'}]
#     task_data=task_data[0]
#     app = QApplication(sys.argv)
#     asset_label = TaskLabel(task_data)
#     asset_label.setFixedSize(600, 600)
#     asset_label.show()
#     sys.exit(app.exec_())
