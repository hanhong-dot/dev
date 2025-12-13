# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       : asset_flow
# Describe   : 以类似网格布局，可以自适应长宽的情况，显示子部件
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2022/10/14__11:05
# -------------------------------------------------------
import os
import sys

try:
    from PySide2.QtGui import *
    from PySide2.QtCore import *
    from PySide2.QtWidgets import *
    from PySide2.QtMultimediaWidgets import QVideoWidget
    from PySide2.QtMultimedia import QMediaPlayer
    from PySide2.QtMultimedia import QMediaPlaylist
except:
    from Qt.QtWidgets import *
    from Qt.QtGui import *
    from Qt.QtCore import *
    from PyQt5.QtMultimediaWidgets import QVideoWidget
    from PyQt5.QtMultimedia import QMediaPlayer
    from PyQt5.QtMultimedia import QMediaPlaylist

from apps.tools.common.library.component.image_label_simple import AssetLabelSimple

from apps.tools.maya.sub_assets_republish import config

from lib.common import yamlio
from apps.tools.maya.sub_assets_republish.commont import sg_fun

reload(sg_fun)
from apps.tools.maya.sub_assets_republish.component import image_label

reload(image_label)

from apps.tools.maya.sub_assets_republish.component.image_label import TaskLabel


class AssetTaskFlow(QFrame):
    '''
    负责以流式布局将资产的缩略图合理排放显示，方便用户查看，
    同时对某一个资产的相关操作包含与此。
    '''

    # 发送选中部件的数据信息。
    # 点击其中某缩略图资产，即会触发该信号。
    item_pressed = Signal(list)

    def __init__(self, sg, asset_data):
        '''
        从传入的数据model中拿去相关数据
        :param data_list:
        '''

        super(AssetTaskFlow, self).__init__()
        self.setLayout(QHBoxLayout())

        self.asset_data = asset_data

        self.sg = sg

        self.box = QWidget()
        self.frame = QFrame()
        # self.scroll_bar = QScrollBar()
        self.scroll_bar = CustomScrollBar()
        self.scroll_bar.setMinimum(0)
        self.setFocusPolicy(Qt.ClickFocus)

        self.box.setLayout(QHBoxLayout())
        self.flow_layout = FlowLayout(None, 1, 10, 1)
        self.frame.setLayout(self.flow_layout)
        self.flow_layout.do_finish_signal.connect(self.get_layout_heght)
        self.box.layout().addWidget(self.frame)
        self.box.layout().addWidget(self.scroll_bar)

        self.layout().addWidget(self.box)

        self.add_flow_widget()

        self.scroll_bar.valueChanged.connect(self.set_value)

        # 数据
        self.old_slider_number = 0
        self.flow_layout_height = 0
        self.resize_event = 0
        self.selected_item = []
        self.selected_id_list = []
        self.shift_press = False

    def add_widget_by_task_id_list(self, task_id_list=[]):
        '''
        通过外界传入task_id_list构建任务列表
        :param task_id_list: shotgun 任务id列表
        :return: None
        '''
        pass

    def add_flow_widget(self, view_data=None):
        '''
        将资产以缩略图的形式加载到视图中去。
        :return: None
        '''
        if view_data == None:
            view_data = self.asset_data

        asset_data = view_data
        data = []

        if asset_data:
            for _asset_data in asset_data:
                _data = self.get_asset_task_data(_asset_data['id'], _asset_data['sg_asset_type'])

                # _data=sg_fun.get_task_info_from_task_name(self.sg, _asset_data['id'], _asset_data['sg_asset_type'])
                if _data:
                    data.extend(_data)

        if data:
            for _task_data in data:
                temp_asset_data = TaskLabel(_task_data)
                temp_asset_data.setFixedSize(200, 160)
                temp_asset_data.pressed_signal.connect(self.item_pressed_emit)
                temp_asset_data.selected_signal.connect(self.add_flow_item)
                self.flow_layout.addWidget(temp_asset_data)
        self.tasks_data = data

        self.scroll_bar.setValue(0)
        self.scroll_bar.setSliderPosition(0)

    def get_asset_task_data(self, asset_id, asset_type):
        '''
        通过资产id获取资产任务数据
        :param asset_id: 资产id
        :return: 资产任务数据
        '''
        data_list = []
        self.config = yamlio.read(config.get("config/common", 'asset_sub_info.yml'))
        asset_config = self.config['asset']
        if asset_type and asset_type in asset_config.keys():
            task_names = asset_config[asset_type]
            if task_names:
                for task_name in task_names:
                    _task_dict = sg_fun.get_task_info_from_task_name(self.sg, task_name, asset_id)
                    if _task_dict:
                        data_list.append(_task_dict)
        return data_list

    def get_layout_heght(self, number):
        '''
        获取放置这些资产需要的高度信息
        :param number:
        :return: None
        '''
        need_heigth = self.flow_layout.do_layout_test()
        self.resize_event = 1
        self.scroll_bar.setValue(0)
        self.old_slider_number = 0
        self.flow_layout_height = need_heigth
        frame_size = self.frame.visibleRegion().boundingRect()
        x = frame_size.width()
        frame_height = frame_size.height()
        out_line = self.flow_layout_height - frame_height
        if out_line < 0:
            self.scroll_bar.setMaximum(0)
        else:
            self.frame.resize(QSize(x, need_heigth))
            self.scroll_bar.show()
            self.scroll_bar.setMinimum(0)
            self.scroll_bar.setSingleStep(1)
            self.scroll_bar.setMaximum(out_line)

    def set_value(self, number):
        '''
        设置使用滑块栏滑动资产时，设置滑块的值。
        :param number: 滑块此时的值。
        :return: None
        '''
        if self.resize_event:
            self.resize_event = 0
            return True
        value = number - self.old_slider_number
        if number > self.old_slider_number:
            self.frame.move(self.frame.pos().x(), self.frame.pos().y() - value)
        elif number < self.old_slider_number:
            if self.frame.pos().y() - value > 0:
                self.frame.move(self.frame.pos().x(), 0)
            else:
                self.frame.move(self.frame.pos().x(), self.frame.pos().y() - value)
        self.old_slider_number = number

    def item_pressed_emit(self, list):
        '''
        点击的元素信息列表，并将其发射出去。
        :param list: 元素信息列表。例如[{'code': 'asset', 'id': 99, ....}]
        :return: None
        '''
        self.item_pressed.emit(list)

    def wheelEvent(self, event):
        '''
        重写滑轮事件
        :param event:
        :return:
        '''
        max_distance = self.scroll_bar.maximum()
        super(AssetTaskFlow, self).wheelEvent(event)
        # rotate_degree 值 120 或 -120
        rotate_degree = event.delta()
        move_distance = rotate_degree / 2
        distance = self.old_slider_number - move_distance
        if 0 < distance <= max_distance:
            self.scroll_bar.setSliderPosition(distance)
            self.old_slider_number = distance
        elif distance > max_distance:
            self.scroll_bar.setSliderPosition(max_distance)
            self.old_slider_number = max_distance
        elif distance <= 0:
            self.scroll_bar.setSliderPosition(0)
            self.old_slider_number = 0

        event.accept()

    def resizeEvent(self, event):
        self.scroll_bar.setValue(0)

    def asset_item_clicked(self, item):
        pass

    def keyPressEvent(self, event):
        '''
        检测是否触发shift按键
        :param event: 键盘事件
        :return:
        '''
        if event.key() == 16777248:
            self.set_shift_selected(True)

    def keyReleaseEvent(self, event):
        '''
        检测shift键是否已被用户释放
        :param event:键盘释放事件
        :return:
        '''
        if event.key() == 16777248:
            self.set_shift_selected(False)

    def set_shift_selected(self, value):
        '''
        当用户点击shift键是记录相关值
        :param value: 释放的按键值
        :return: None
        '''
        self.shift_press = value

    def add_flow_item(self, item):
        '''
        存在多选时，激活选中部件的样式，并将选中的信息记录在实例数据中。
        :param item: 缩略图部件元素
        :return: None
        '''
        if self.shift_press:
            # 添加进列表
            # item : QMedia_Label
            self.selected_item.append(item)
            # self.selected_item.append(item.ass)
        else:
            for temp_item in self.selected_item:
                # 清空之前元素的状态，将当前元素添加进去
                temp_item.setFrameShadow(QFrame.Plain)
                temp_item.setFrameShape(QFrame.NoFrame)
                temp_item.setStyleSheet('border:0px solid red;')
            # 将当前元素添加到空列表
            self.selected_item = [item]
        item.setFrameShape(QFrame.Panel)
        item.setFrameShadow(QFrame.Sunken)
        item.setStyleSheet('border:2px solid #66CCFF;border-radius:1px')


class FlowLayout(QLayout):
    do_finish_signal = Signal(int)
    '''
    自定义布局，负责布局子部件
    '''

    def __init__(self, parent, margin, hSpacing, vSpacing):
        '''
        传入布局需要的参数，例如子部件之间的垂直和水平距离。
        :param parent: 父类
        :param margin: 与其余部件之间的间隔
        :param hSpacing: 子部件的水平距离
        :param vSpacing: 子部件的垂直距离
        '''
        super(FlowLayout, self).__init__(parent)
        self._item_list = []
        self.setContentsMargins(margin, margin, margin, margin)

        self.m_hSpace = hSpacing
        self.m_vSpace = vSpacing

    def addItem(self, item):
        '''
        添加Item元素。类型QLayoutItem或者QWidgetItem
        :param item:
        :return: None
        '''
        self._item_list.append(item)

    def itemAt(self, index_number):
        '''
        索引位置
        :param index_number:
        :return: item(QLayoutItem)
        '''
        index = self.count() - 1
        if index_number <= index:
            return self._item_list[index_number]
        else:
            return None

    def takeAt(self, index_number):
        u'''
        根据索引位置，删除相关元素
        :param index_number: 元素位置索引
        :return: None
        '''
        if index_number >= 0 and index_number < self.count():
            return self._item_list.pop(index_number)

    def count(self):
        u'''
        返回元素数量
        :return: 子部件的个数
        '''
        item_count = len(self._item_list)
        return item_count

    def indexOf(self, qwidget):
        u'''
        查询部件，并返回位置
        :param qwidget:
        :return: 返回子元素所在的索引位置
        '''
        if qwidget in self._item_list:
            return self._item_list.index(qwidget)
        else:
            return -1
        pass

    def sizeHint(self):
        u'''
        QLayoutItem
        :return: QSize(600, 600)
        '''
        return QSize(600, 600)

    def minimumSize(self):
        u'''
        # 计算出所有item元素最大尺寸
        :return:  QSize
        '''
        size = QSize()
        for item in self._item_list:
            size = size.expandedTo(item.minimumSize())
        size = size + QSize(2 * self.margin(), 2 * self.margin())
        return size

    def expandingDirections(self):
        '''
        QLayout自带方法
        :return: 0
        '''
        return 0

    def horizontalSpacing(self):
        '''
        返回元素的水平距离
        :return: int
        '''
        if self.m_hSpace >= 0:
            return self.m_hSpace
        else:
            return self.smartSpacing(QStyle.PM_LayoutHorizontalSpacing)

    def verticalSpacing(self):
        '''
        返回元素之间的垂直距离
        :return: int
        '''
        if self.m_vSpace >= 0:
            return self.m_vSpace
        else:
            return self.smartSpacing(QStyle.PM_LayoutVerticalSpacing)

    def expandingDirections(self):
        return 0

    def hasHeightForWidth(self):
        '''
        是否保持长宽比，需重写
        :return: False
        '''
        return False

    def heightForWidth(self, width):
        u'''
        保持长宽比，需重写
        :return:
        '''
        height = self.do_layout(QRect(0, 0, width, 0), True)
        return height

    def getHeight(self):
        '''
        获取布局的高度
        :return: int
        '''
        height = self.do_layout(QRect(0, 0, 0, 0), True)
        return height

    def do_layout_test(self):
        '''
        对布局进行测试，返回竖直高度
        :return: int
        '''
        parent_width = self.parent().width()
        rect = QRect(0, 0, parent_width, 0)
        v_height = 0
        left, top, right, bottom = self.getContentsMargins()
        effectiveRect = rect.adjusted(left, top, -right, -bottom)
        x = effectiveRect.x()
        y = effectiveRect.y()
        lineHeight = 0
        count = 0
        nextX = 0
        for item in self._item_list:
            item_height = item.widget().height()
            spaceX = self.horizontalSpacing()
            if spaceX == -1:
                spaceX = 1
            spaceY = self.verticalSpacing()
            if spaceY == -1:
                spaceY = -1
            if count == 0:
                v_height = item_height + lineHeight + 15
            count += 1

            # nextX = x + item.sizeHint().width() + spaceX
            nextX = x + item.widget().width() + spaceX
            if nextX - spaceX > effectiveRect.right():
                v_height = v_height + item_height + lineHeight + 15
                x = effectiveRect.x()
                y = y + lineHeight + spaceY
                nextX = x + item.widget().width() + spaceX
                lineHeight = 0

            x = nextX
        return v_height

    def setGeometry(self, rect):
        '''
        开始布局
        :param rect: 布局的相关尺寸
        :return: None
        '''
        super(FlowLayout, self).setGeometry(rect)
        self.do_layout(rect, False)

    def smartSpacing(self, qstyle):
        '''
        计算部件之间的间距
        :param qstyle: qt样式
        :return: int (部件距离)
        '''
        parent = self.parent()

        if not parent:
            return -1
        elif parent.isWidgetType():
            return parent.style().pixelMetric(qstyle, 0, parent)
        else:
            return parent.spacing()

    def do_layout(self, rect, test_only):
        '''
        rect为布局所使用的矩形实体。QRec
        :param rect: 定义布局矩形的位置和大小
        :param test_only: 测试
        :return: None
        '''
        v_height = 0
        left, top, right, bottom = self.getContentsMargins()
        effectiveRect = rect.adjusted(left, top, -right, -bottom)
        x = effectiveRect.x()
        y = effectiveRect.y()
        lineHeight = 0
        count = 0
        for item in self._item_list:
            item_height = item.widget().height()
            spaceX = self.horizontalSpacing()
            if spaceX == -1:
                spaceX = 1
            spaceY = self.verticalSpacing()
            if spaceY == -1:
                spaceY = -1
            nextX = x + item.widget().width() + spaceX
            if nextX - spaceX > effectiveRect.right() and lineHeight > 0:
                v_height = v_height + item_height + lineHeight + 15
                x = effectiveRect.x()
                y = y + lineHeight + spaceY
                nextX = x + item.widget().width() + spaceX
                lineHeight = 0

            if not test_only:
                item.setGeometry(QRect(QPoint(x, y), item.widget().size()))

            x = nextX
            lineHeight = max(lineHeight, item.widget().height())
        self.do_finish_signal.emit(v_height)

    def printItem(self):
        '''
        测试
        :return:
        '''
        for i in self._item_list:
            pass

    def addLayout(self, args):
        u'''
        需重写，可添加子布局
        :param args: 布局部件
        :return: None
        '''
        pass

    def widgetEvent(self, event):
        super(FlowLayout, self).widgetEvent(event)

    def remove_all_widget(self):
        '''
        移除该布局中的所有资产
        :return: None
        '''
        widget_list = self.get_all_widget()
        for widget in widget_list:
            widget.setParent(None)
            self.removeWidget(widget)
        # self.v_height = 0

    def get_all_widget(self):
        '''
        获取布局中的所有部件
        :return: 部件列表
        '''
        widget_list = []
        count = self.count()
        for i in range(count):
            temp_widget = self.itemAt(i).widget()
            if temp_widget:
                widget_list.append(temp_widget)
        return widget_list


class CustomScrollBar(QScrollBar):
    '''
    自定义滑轮部件，重写鼠标滑轮事件
    '''

    def __init__(self):
        super(CustomScrollBar, self).__init__()


class AssetFlowSimple(QFrame):
    '''
    负责以流式布局将资产的缩略图合理排放显示，方便用户查看，
    此部件主要显示资产，不再与shotgun交互，主要数据都从外部传入
    '''
    # 发送选中部件的数据信息
    # 点击其中某缩略图资产，即会触发该信号
    item_pressed = Signal(list)

    def __init__(self):
        '''
        初始化相关部件
        '''
        super(AssetFlowSimple, self).__init__()
        self.setLayout(QHBoxLayout())
        self.box = QWidget()
        self.frame = QFrame()
        self.scroll_bar = CustomScrollBar()
        self.scroll_bar.setMinimum(0)
        self.setFocusPolicy(Qt.ClickFocus)

        self.box.setLayout(QHBoxLayout())
        self.flow_layout = FlowLayout(None, 1, 10, 1)
        self.frame.setLayout(self.flow_layout)
        self.flow_layout.do_finish_signal.connect(self.get_layout_height)
        self.box.layout().addWidget(self.frame)
        self.box.layout().addWidget(self.scroll_bar)

        self.layout().addWidget(self.box)
        self.scroll_bar.valueChanged.connect(self.set_value)
        # 数据
        self.old_slider_number = 0
        self.flow_layout_height = 0
        self.resize_event = 0
        self.selected_item = []
        self.selected_id_list = []
        self.shift_press = False

    def get_layout_height(self, number):
        '''
        获取放置资产需要的高度信息
        :param number: 高度
        :return: NOne
        '''
        need_height = self.flow_layout.do_layout_test()
        self.resize_event = 1
        self.scroll_bar.setValue(0)
        self.old_slider_number = 0
        self.flow_layout_height = need_height
        frame_size = self.frame.visibleRegion().boundingRect()
        x = frame_size.width()
        frame_height = frame_size.height()
        out_line = self.flow_layout_height - frame_height
        if out_line < 0:
            self.scroll_bar.setMaximum(0)
        else:
            self.frame.resize(QSize(x, need_height))
            self.scroll_bar.show()
            self.scroll_bar.setMinimum(0)
            self.scroll_bar.setSingleStep(1)
            self.scroll_bar.setMaximum(out_line)

    def set_value(self, number):
        '''
        设置使用滑块栏滑动资产时，设置滑块的值。
        :param number:
        :return: None
        '''
        if self.resize_event:
            self.resize_event = 0
            return True
        value = number - self.old_slider_number
        if number > self.old_slider_number:
            self.frame.move(self.frame.pos().x(),
                            self.frame.pos().y() - value)
        elif number < self.old_slider_number:
            if self.frame.pos().y() - value > 0:
                self.frame.move(self.frame.pos().x(), 0)

            else:
                self.frame.move(self.frame.pos().x(),
                                self.frame.pos().y() - value)

        self.old_slider_number = number

    def item_pressed_emit(self, asset_list):
        '''
        点击的元素信息列表，并将其发射出去
        :param asset_list: 元素信息列表。例如[{'code': 'asset', 'id': 99,...}]
        :return: None
        '''
        self.item_pressed.emit(asset_list)

    def wheelEvent(self, event):
        '''
        重写滑轮事件
        :param event:
        :return:
        '''
        max_distance = self.scroll_bar.maximum()
        super(AssetFlowSimple, self).wheelEvent(event)
        # rotate_degree 值 120 或 -120
        rotate_degree = event.delta()
        move_distance = rotate_degree / 2
        distance = self.old_slider_number - move_distance
        if 0 < distance <= max_distance:
            self.scroll_bar.setSliderPosition(distance)
            self.old_slider_number = distance
        elif distance > max_distance:
            self.scroll_bar.setSliderPosition(max_distance)
            self.old_slider_number = max_distance
        elif distance <= 0:
            self.scroll_bar.setSliderPosition(0)
            self.old_slider_number = 0

        event.accept()

    def keyPressEvent(self, event):
        '''
        检测是否触发shift按键
        :param event:  键盘事件
        :return:
        '''
        if event.key() == 16777248:
            self.set_shift_selected(False)

    def resizeEvent(self, event):
        self.scroll_bar.setValue(0)

    def set_shift_selected(self, value):
        '''
        当用户点击shift键时记录相关值
        :param value: 释放的按键值
        :return: None
        '''
        self.shift_press = value

    def add_flow_item(self, item):
        '''
        存在多选时，激活选中部件的样式，并将选中的信息记录在实例数据中
        :param item: 缩略图部件元素
        :return: None
        '''
        if self.shift_press:
            # 添加列表
            self.selected_item.append(item)
        else:
            for temp_item in self.selected_item:
                # 清空之前元素的状态，将当前元素添加进去
                temp_item.setFrameShadow(QFrame.Plain)
                temp_item.setFrameShape(QFrame.NoFrame)
                temp_item.setStyleSheet('border:0px solid red;')
            # 将当前元素添加到空列表
            self.selected_item = [item]

        item.setFrameShape(QFrame.Panel)
        item.setFrameShadow(QFrame.Sunken)
        item.setStyleSheet('border:2px solid #66CCFF; border-radius:1px')

    def add_flow_widget(self, asset_list=[]):
        '''
        将资产以缩略图形式加载到视图中去
        :param asset_list: 资产信息资产列表
        :return: None
        '''
        data = asset_list
        for asset in data:
            # temp_format = os.path.splitext(asset["sg_file_path"])[1]
            # if temp_format in base_data.PIC_FORMAT:
            temp_asset_data = AssetLabelSimple(asset)
            temp_asset_data.setFixedSize(160, 100)
            temp_asset_data.pressed_signal.connect(self.item_pressed_emit)
            self.flow_layout.addWidget(temp_asset_data)

        self.scroll_bar.setValue(0)
        self.scroll_bar.setSliderPosition(0)


if __name__ == "__main__":
    #
    import database.shotgun.core.sg_analysis as sg_analysis

    sg = sg_analysis.Config().login()
    #     # attr = {
    #     #         '7321': {'code': 'a', 'sg_new_type': u'特效素材', 'sg_picture_size': '102x123'
    #     #             , 'sg_file_path': 'D:/temp/a/602dbc30fe4511ea9282b8ca3a76bcf5/a.tif', 'sg_dir_id': '1,2,3,4', 'id': '7321',
    #     #                  'sg_file_size': 14.8, 'sg_duration_time': 0, 'sg_file_type': '.tif',
    #     #                  'created_at': '2020/09/24 17:07', 'created_at': '2020/09/25 14:10'}}
    #     #
    #     # model_data = base_data.EfxLibrary(data=attr,source_dir='d:/temp/a')
    #     # model_data.view_data = model_data.data
    #     # app = QApplication(sys.argv)
    #     # window = AssetFlow(model_data)
    #     # window.resize(800, 600)
    #     # window.show()
    #     # sys.exit(app.exec_())
    #
    #
    #     #-----------AssetFlowSimple---------------------------
    asset_data = [{'code': 'FY001S', 'type': 'Asset', 'id': 12637, 'sg_asset_type': 'role'}]
    # AssetFlow(asset_data).add_flow_widget()
    # print('a')
    # asset_list = [asset_data]
    try:
        app = QApplication(sys.argv)
    except:
        app = QApplication.instance()
    window = AssetTaskFlow(sg, asset_data)
    window.resize(800, 600)
    # window.add_flow_widget()
    window.show()
    sys.exit(app.exec_())
# QApplication.instance()
# window = AssetFlowSimple()
# window.add_flow_widget(asset_list)
# window.resize(800, 600)
# window.show()
# sys.exit(app.exec_())
# QApplication.instance()
