# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       : center_widget
# Describe   : 中心weight
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2022/10/14__14:33
# -------------------------------------------------------
import time
import threading
import os
import sys
import re
import traceback

try:
    from PySide2.QtGui import *
    from PySide2.QtCore import *
    from PySide2.QtWidgets import *
except:
    from Qt.QtWidgets import *
    from Qt.QtGui import *
    from Qt.QtCore import *

from apps.tools.common.library.component import searchline
from apps.tools.maya.sub_assets_republish.commont import sg_fun
reload(sg_fun)


from apps.tools.maya.sub_assets_republish.commont import base_data
from apps.tools.common.library.component.spliter_widget import SpliterWidgetSimple

from database.shotgun.core import sg_analysis
from database.shotgun.core import sg_asset
from apps.tools.maya.sub_assets_republish.component import asset_flow
reload(asset_flow)


class CenterWidget(QFrame):
    '''
    资源库中心部件，包含资产显示部件，以及翻页，查询，过滤部件.
    '''

    ok_signal = Signal(int)
    error_signal = Signal(str)
    menu_signal = Signal()
    item_pressed_signal = Signal(list)

    asset_add_fin_signal = Signal()
    def __init__(self, sg,asset_data, accept_drop=False):
        super(CenterWidget, self).__init__()
        self.sg = sg
        self.asset_data = asset_data
        self.setLayout(QVBoxLayout())
        self.layout().setContentsMargins(1, 1, 1, 1)
        self.init_flow_widget()
        if accept_drop:
            self.setAcceptDrops(True)
        else:
            self.setAcceptDrops(False)

        # 数据
        self.old_press_item = None
        self.current_asset_type = None
        self.current_task_template = None
        self.children_id_list = []
        self.box_value = None
        self.current_item_id = None

        self.query_model = 'tree'
        self.filter_list = []
        # 消息框
        self.process = QProgressBar(self)
        self.process.setMaximum(0)
        self.process.setWindowTitle(u'上传进度')
        self.process.setMinimumSize(QSize(150, 30))
        self.process.hide()
        self.message_box = QMessageBox()
        self.message_box.setStandardButtons(QMessageBox.Cancel | QMessageBox.Ok)
        self.message_box.setWindowTitle(u'消息框')
        self.menu = QMenu()

        self.ok_signal.connect(self.process.setValue)
        self.error_signal.connect(self.show_error)
        self.menu_signal.connect(self.show_content_menu)
        self.menu.triggered.connect(self.action_response)

    def init_flow_widget(self,asset_data=None):
        u'''
        初始化时，加载过滤部件，资产部件，分页部件等
        :return: None
        '''
        # model_instace = self.asset_data
        # if model_instace:
        #     self.tooltip = SearchWidget(model_instace[0]['code'])
        # else:
        #     self.tooltip = SearchWidget()
        if asset_data==None:
            asset_data= self.asset_data

        self.asset_flow = asset_flow.AssetTaskFlow(self.sg,asset_data)
        self.asset_flow.setFrameShape(QFrame.Box)
        self.asset_flow.setFrameShadow(QFrame.Raised)
        if self.acceptDrops():
            self.asset_flow.setAcceptDrops(True)
        # 新增分栏部件
        # self.spliter_widget = SpliterWidget()
        # self.spliter_widget = SpliterWidgetSimple()
        # self.spliter_widget.setFixedHeight(50)
        # self.layout().addWidget(self.tooltip)
        self.layout().addWidget(self.asset_flow)


        # self.layout().addWidget(self.spliter_widget)
        # 信号
        # self.spliter_widget.text_changed_signal.connect(self.change_content_by_page)
        # self.spliter_widget.line_edit.textChanged.connect(self.change_content_by_page)
        self.asset_flow.item_pressed.connect(self.send_selected_widget)
        # self.tooltip.zuhe_filter.label_list.state_changed_signal.connect(self.add_label_and_active_view)
        # self.tooltip.search_signal.connect(self.search_asset)
        self.asset_add_fin_signal.connect(self.update_by_thread)

    def send_selected_widget(self, asset_info):
        u'''
        相关资产部件被选中后，发送信号
        :param asset_info:
        :return: None
        '''
        self.item_pressed_signal.emit(asset_info)

        # 鼠标加选 选中的元素
        self.asset_flow.select_item_by_id(asset_info['id'])

    def dragEnterEvent(self, event):
        u'''
        设置是否接受拖入事件
        :param event:
        :return:
        '''
        if self.acceptDrops():
            event.ignore()

    def dropEvent(self, event):
        '''
        处理外界拖入文件夹事件
        当前只有资源库开启拖入事件
        :param event:
        :return: None
        '''
        urls = event.mimeData().hasUrls()
        if not urls:
            return False
        # 开始检测添加文件到库中
        urls_list = event.mimeData().urls()
        self.drop_signal.emit(urls_list)

    def update_by_thread(self):
        '''
        线程通过信号调用此函数
        :return:
        '''
        self.process.hide()
        # 更新视图

        # asset_id_list, asset_type, new_asset_list = self.model_instance.load_asset_dic_for_sucai(template_name=self.current_task_template,
        #                                                                                          project_name=self.model_instance.project)
        # new_asset_type_list = list(set(asset_type))
        # # 调用中心部件
        # self.model_instance.data = asset_id_list
        # self.model_instance.data_list = new_asset_list
        self.spliter_asset()
        # self.tooltip.zuhe_filter.init_check_box(new_asset_type_list)

    def run_in_child_thread(self,urls):
        '''
        获取用户拖入的文件地址，处理并写入到shotgun。
        此函数当前只有资源库会使用。
        :param urls: 文件列表
        :return: True or False
        '''
        threading.Thread(target=self.check_file_format, args=(urls,)).start()
        # self.check_file_format(urls)

    def update_flow_view(self,asset_data):
        '''
        接收树元素，并根据树元素更新相关数据。
        :param tree_item: 左侧树部件元素
        :return: None
        '''
        # self.asset_flow=asset_flow.AssetTaskFlow(self.sg,asset_data)

        #
        # asset_dic = self.model_instance.query_info_by_path(self.children_id_list, 'sg_dir_id')
        # self.model_instance.view_data = asset_dic

        self.asset_flow.flow_layout.remove_all_widget()


        # # 开始视图
        self.asset_flow.add_flow_widget(asset_data)




    def update_flow_by_asset_id(self, asset_id_list):
        '''
        通过传入的资产id，查询shotgun数据库信息更新视图
        :param asset_id_list:
        :return: None
        '''
        pass

    def update_flow_by_task_id(self, task_id_list):
        '''
        通过传入的任务id，查询shotgun数据库信息，更新视图
        :param task_id_list:
        :return: None
        '''
        pass

    def update_flow_by_condition(self,dic):
        ''''
        根据筛选条件更新视图,
        获取筛选属性，以及获得值，从视图数据（.view_data）中查询，
        并更新到视图中。
        :parameter 数据字典
        :return None
        '''
        shotgun_attr_dic = {}
        search_data_dic = {}

        # 所有过滤数据
        attr_list = self.tooltip.filter_box.item_list()
        # 搜索栏中输入的属性值
        attr_value = self.tooltip.search_button.text()

    # def find_all_dir_id(self, parent_id):
    #     '''
    #     递归查找目录树id树
    #     :param parent_id:
    #     :return:
    #     '''
    #     # 递归
    #
    #     self.asset_flow = asset_flow.AssetTaskFlow(self.sg, self.asset_data)
    #     # if parent_id not in self.model_instance.tree_data.keys():
    #     #     return False
    #     # children_list = self.model_instance.tree_data[parent_id][1]
    #     # self.children_id_list += children_list
    #     # for children in children_list:
    #     #     self.find_all_dir_id(children)
    #     self.asset_flow.add_flow_widget()

    def show_error(self, info):
        '''
        显示数据信息
        :param info: 错误信息
        :return:
        '''
        self.message_box.setText(info)
        self.box_value = self.message_box.exec_()

    def mousePressEvent(self, event):
        '''
        处理鼠标点击事件
        :param event:
        :return:
        '''
        if event.button() == Qt.RightButton:
            self.menu_signal.emit()
        event.ignore()
        super(CenterWidget, self).mousePressEvent(event)

    def show_content_menu(self):
        '''
        点击资产部件，触发右键菜单槽
        可重写,考虑配置文件，方便添加
        :return:
        '''
        self.menu.clear()
        self.load_action()
        self.menu.move(self.cursor().pos())
        self.menu.show()

    def action_response(self, action):
        '''
        接收Action按钮，执行相关程序
        可重写
        :param action: QAction
        :return: None
        '''
        task_data_str = ''
        command = action.data()

        for item in self.asset_flow.selected_item:
            task_data_str += str(item.task_data)
            task_data_str += ';'

        task_data_str = task_data_str.rstrip(';')
        new_command = command.replace('{task_data}', '"'+task_data_str+'"')

        try:
            # 返回类型限制,
            # status (arg1, arg2)
            # arg1 : True or False
            # arg2: "错误信息字符串"
            # 如果返回的不是数组，不进行处理
            command_split = new_command.split(";")
            if len(command_split) == 1:
                status = eval(command_split[0])
            else:
                command_length = len(command_split)
                start_command = command_split[0:command_length-1]
                end_command = command_split[-1]
                for temp_command in start_command:
                    exec(temp_command)
                status = eval(end_command)
            if isinstance(status, tuple):
                if status[0] == True:

                    # 内置与UI交互功能
                    if action.text() == u"删除资产":
                        # 内置与UI交互菜单功能单独处置
                        for item in self.asset_flow.selected_item:
                            item.setParent(None)
                            self.asset_flow.layout().removeWidget(item)


                    msgBox = QMessageBox()
                    msgBox.setWindowTitle(u'成功')
                    msgBox.setMinimumSize(QSize(200, 60))
                    msgBox.setText(status[1])
                    msgBox.exec_()

                else:
                    msgBox = QMessageBox()
                    msgBox.setWindowTitle(u'失败')
                    msgBox.setMinimumSize(QSize(200, 60))
                    msgBox.setText(status[1])
                    msgBox.exec_()

            else:
                print "不是元组类型"
                # 不做处理
                pass

        except:
            msgBox = QMessageBox()
            msgBox.setWindowTitle(u'错误提示')
            msgBox.setMinimumSize(QSize(200, 60))
            msgBox.setText(traceback.format_exc())
            msgBox.exec_()

    def load_action(self):
        '''
        从其他配置读取文件,读取相关文件，相关目录默认两层。
        外部资产框架只提供非dcc命令程序执行
        DCC内部资产框架会提供dcc命令程序执行
        可重写
        :return: True or False
        '''
        # 根据传入的项目加载相关的菜单栏
        # 读取项目的配置
        menu_list = base_data.read_center_action_config()
        for menu in menu_list:
            temp_menu = QMenu(menu[0])
            for action in menu[1]:
                temp_action = QAction(temp_menu)
                temp_action.setText(action[0])
                temp_icon = QIcon()
                temp_icon.addPixmap(QPixmap(action[1]), QIcon.Normal, QIcon.Off)
                temp_action.setIcon(temp_icon)
                temp_action.setData(action[2])
                temp_menu.addAction(temp_action)
            self.menu.addMenu(temp_menu)

    def main_widget_move(self):
        '''
        更新部件的位置
        :return:
        '''
        self.tooltip.relocal_no_layout_widget()

    def find_all_attr_name(self):
        pass

    def spliter_asset(self):
        '''
        展示视图之前，先进行分页，优化运行速度,默认每行100条
        :return:
        '''
        self.query_model = 'tree'
        # self.spliter_widget.set_text('1')

    def search_asset(self, filter_list=[]):
        '''
        查询视图方式
        :return:
        '''
        self.filter_list = filter_list
        self.query_model = 'search'
        self.spliter_widget.set_text('1')


    def change_content_by_page(self):
        '''
        '''
        time1 = time.time()
        if self.query_model == 'tree':
            print 'self.current_item_id', self.current_item_id

            asset_data=sg_fun.get_asset_from_asset_id(self.sg, self.current_item_id)
            self.asset_flow = asset_flow.AssetTaskFlow(self.sg, [asset_data])
            if asset_data:
                self.spliter_widget.flags = True
                self.asset_flow.flow_layout.remove_all_widget()
                self.asset_flow.add_flow_widget()
            else:
                self.spliter_widget.flags = False
                self.asset_flow.flow_layout.remove_all_widget()








if __name__ == '__main__':

    import database.shotgun.core.sg_analysis as sg_analysis


    sg = sg_analysis.Config().login()
    asset_data=[{'type': 'Asset', 'id': 13809, 'code': 'FY_BODY','sg_asset_type': 'body'}]
    try:
        app = QApplication(sys.argv)
    except:
        app = QApplication.instance()

    # asset_data={'code': 'FY_BODY', 'type': 'Asset', 'id': 13809, 'sg_asset_type': 'body'}

    center_widget = CenterWidget(sg,asset_data)


    # center_widget.set_info(u"删除完成")
    center_widget.show()
    # center_widget.update_flow_view()
    asset_data = [{'code': 'FY001C', 'type': 'Asset', 'id': 12858, 'sg_asset_type': 'role'}]
    # center_widget = CenterWidget(sg, asset_data)
    #
    # center_widget = CenterWidget(sg, asset_data)
    center_widget.update_flow_view(asset_data)
    # center_widget.show()

    sys.exit(app.exec_())
