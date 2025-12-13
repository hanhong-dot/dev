# -*- coding: utf-8 -*-#

# -------------------------------------------------------
# NAME       : batch_ui
# Describe   : 说明描述
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2023/12/30__14:54
# -------------------------------------------------------

import sys
sys.path.append('Z:/dev')
sys.path.append(r'Z:\dev\database\shotgun\toolkit\x3\install\core\python')
sys.path.append(r'Z:\dev\Ide\python310\site-packages')



import os
import time
import threading


import thread
import json
import PySide2


try:

    from PySide2.QtCore import *
    from PySide2.QtGui import *
    from PySide2.QtWidgets import *

except:
    from PyQt5.QtWidgets import *
    from PyQt5.QtGui import *
    from PyQt5.QtCore import *


from lib.common import fileio

# from apps.batch import resources

from apps.batch import analyze_xml
from apps.batch import tools
from apps.batch.class_override import MyQTableView
from lib.common import log
import lib.common.timedate as timedate
import method.common.dir as common_dir
import uuid

import  apps.batch.ui.listwidget as _listwidget
import re
from lib.common.log import Logger,read_info



class Append_Signal(QObject):
    Str_Signal = Signal(str)

class Batch(QWidget):
    addItemSignal = Signal(dict)
    updateUISignal = Signal(tuple)

    def __init__(self, project_list):
        super(Batch, self).__init__()
        self.project = eval(project_list)[0]
        self.is_interrupt_execution = False
        self.appendSignal = Append_Signal()

        self.setup()
        self.init_data()
        self.setObjectName(self.__class__.__name__)
        self.resize(1000, 600)
        res_stylesheet = 'Z:/dev/apps/batch/batch.qss'
        style = fileio.read(res_stylesheet)
        self.setStyleSheet(style)
        self.main_info()

    def init_data(self):
        self.setWindowTitle(u'批处理工具')
        label_project_html = (u'<b style="color:#00FA9A;font-size:30px">{}批量处理工具(请拖入需要处理的文件)</b>').format(
            self.project['name'])
        self.labelProjectName.setText(label_project_html)
        self.tableview_model = QStandardItemModel(self.tableView)
        self.tableView.setModel(self.tableview_model)
        self.header_labels = [u'状态', u'文件名', u'开始时间', u'结束时间', u'批处理命令']
        self.tableview_model.setHorizontalHeaderLabels(self.header_labels)
        self.tableView.dropped.connect(self.add_file_path)
        self.addItemSignal.connect(self.add_item)
        self.updateUISignal.connect(self.update_ui)
        self.tableView.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.tableView.horizontalHeader().setMinimumSectionSize(100)
        self.tableView.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.tableView.horizontalHeader().setStretchLastSection(True)
        self.tableView.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.tableView.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.tableView.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tableView.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tableView.horizontalHeader().setSortIndicatorShown(True)
        self.tableView.setSortingEnabled(True)
        self.tableView.setContextMenuPolicy(Qt.CustomContextMenu)
        if self.right_context_menu:
            self.tableView.customContextMenuRequested[QPoint].connect(self.right_context_menu)

        self.pushButtonChosenAll.clicked.connect(self.chosen_all)
        self.pushButtonResetReady.clicked.connect(self.reset_ready)
        self.pushButtonDelete.clicked.connect(self.delete)
        self.pushButtonDeleteAll.clicked.connect(self.delete_all)
        self.pushButtonCancel.clicked.connect(self.cancel)
        self.pushButtonProcess.clicked.connect(self.process)
        self.tableView.doubleClicked.connect(self.open_log)



    def chosen_all(self):
        self.tableView.selectAll()

    def reset_ready(self):
        rowCount = self.tableview_model.rowCount()
        for row in range(rowCount):
            item = self.tableview_model.item(row, 0)
            item.setText('Ready')
            item.setBackground(Qt.darkGray)

    def main_info(self):
        self._clearInfo()
        threading.Thread(target=self._set_back_weight).start()
        self.appendSignal.Str_Signal.connect(self._set_back_weight)
    def _clearInfo(self):
        self._listwidget._clear_info()


    def _set_back_weight(self):
        rowCount = self.tableview_model.rowCount()
        if not rowCount:
            return
        for row in range(rowCount):
            item=self.tableview_model.item(row, 0)
            text=item.text()
            if text and text in ['Complete','Error']:
                _data=item.data()
                if _data and 'log_file' in _data:
                    log_file=_data['log_file']
                    info_=self._read_info(log_file)
                    if not info_:
                        continue
                    for info in info_:
                        print('info:',info)
                        self._ProcessInfo(info)




    def _read_info(self,logfile):

        return read_info(logfile)


    def _ProcessInfo(self, addInfo):
        self.__listwidget = self._listwidget._listwidget
        item = QListWidgetItem()
        item.setText(u'{}'.format(addInfo))
        if 'ERROR' in addInfo:
            item.setTextColor(QColor('red'))
            # self.back_weight._listwidge.addItem(item)
        # elif 'files to fileSystem is started' in addInfo:
        #     item.setTextColor(QColor('yellow'))
        #     self.back_weight._listwidge.addItem(item)
        # elif addInfo.startswith('Result :') and re.findall(r"ErrFiles : (.+?) /", addInfo) != ['0']:
        #     item.setTextColor(QColor('red'))
        #     self.back_weight._listwidge.addItem(item)
        # elif addInfo.startswith('Result :') and re.findall(r"ErrDirs : (.+?)", addInfo) != ['0']:
        #     item.setTextColor(QColor('red'))
        #     self.back_weight._listwidge.addItem(item)
        # else:
        self.__listwidget.addItem(item)
        self.__listwidget.setCurrentRow(self.__listwidget.count() - 1)

    def delete(self):
        index_list = []
        for model_index in self.tableView.selectionModel().selectedRows():
            index = QPersistentModelIndex(model_index)
            index_list.append(index)

        for index in index_list:
            self.tableview_model.removeRow(index.row())

    def delete_all(self):
        self.tableview_model.removeRows(0, self.tableview_model.rowCount())

    def cancel(self):
        self.is_interrupt_execution = True

    def open_log(self):
        indexes = self.tableView.selectionModel().selectedRows()
        current_item = self.tableview_model.item(indexes[0].row())
        process_data = current_item.data()
        if 'log_file' in process_data:
            log_file = process_data['log_file']
            if os.path.exists(log_file):
                os.startfile(log_file)

    def process(self):
        self.is_interrupt_execution = False
        thread.start_new_thread(self.process_thread, ())

    def process_thread(self):
        for row in range(self.tableview_model.rowCount()):
            if self.is_interrupt_execution:
                break
            current_item = self.tableview_model.item(row)
            start_time_item = self.tableview_model.item(row, 2)
            end_time_item = self.tableview_model.item(row, 3)
            process_cmd_item = self.tableview_model.item(row, self.tableview_model.columnCount() - 1)

            process_cmd = process_cmd_item.data()
            if process_cmd:
                self.updateUISignal.emit((current_item, 'Process...', None, Qt.darkYellow))
                nowtime = time.strftime('%Y-%m-%d %H:%M:%S')
                self.updateUISignal.emit((start_time_item, nowtime, nowtime, None))
                process_data = current_item.data()
                commands = process_cmd['process_command']
                log_file = process_data['log_file']



                is_ok, err_msg = self.process_action(commands, [process_data])

                if is_ok == True:
                    self.updateUISignal.emit((current_item, 'Complete', 'Complete', Qt.darkGreen))
                else:
                    self.updateUISignal.emit((current_item, 'Error', err_msg, Qt.darkRed))

                log_info=self._read_info(log_file)
                if log_info:
                    for info in log_info:
                        self._ProcessInfo(info)


            nowtime = time.strftime('%Y-%m-%d %H:%M:%S')
            self.updateUISignal.emit((end_time_item, nowtime, nowtime, None))

        return

    def process_action(self, commands, entity_list):



        can_do = False
        result_tuple = tuple()
        import_path = str()
        import_path_list = commands.split(';')[:-1]
        for import_path_temp in import_path_list:
            import_path += import_path_temp
            import_path += ';'

        command = commands.split(';')[-1]
        if 'entity_list' in command and entity_list:
            exec_order = command.replace('entity_list', json.dumps(entity_list, default=tools.json_datetime_converter,
                                                                   ensure_ascii=False))
            can_do = True
        if can_do:
            exec(import_path)
            result_tuple = eval(exec_order)
        return result_tuple


    def get_log_file(self):

        log_path = common_dir.get_localtemppath('batch_publish')
        if not os.path.exists(log_path):
            os.makedirs(log_path)
        log_name = '{}.log'.format(uuid.uuid4().get_hex())
        log_file = os.path.join(log_path, log_name).replace('\\', '/')
        return log_file



    def add_item(self, data):
        file_name = data['FileName']
        find_result_list = self.tableview_model.findItems(file_name, Qt.MatchWrap, 1)
        if find_result_list:
            return
        items = list()
        items.append(QStandardItem('Ready'))
        items.append(QStandardItem(data['FileName']))
        items.append(QStandardItem())
        items.append(QStandardItem())
        items.append(QStandardItem())
        if items:
            items[0].setData(data)
            items[0].setBackground(Qt.darkGray)
            items[0].setToolTip('Ready')
            items[1].setToolTip(data['FileName'])
        self.tableview_model.appendRow(items)

    @Slot(list)
    def add_file_path(self, urls):
        paths = tools.get_file_path_list(urls)
        try:
            thread.start_new_thread(self.file_process, (paths,))
        except:
            print('Error: unable to start thread')

    def file_process(self, file_paths):
        if file_paths:
            for file_path in file_paths:
                log_file = self.get_log_file()
                data = dict()
                file_dir, file_name = os.path.split(file_path)
                data['FileName'] = file_name
                data['FilePath'] = file_path
                data['Project'] = self.project
                data['log_file'] = log_file
                self.addItemSignal.emit(data)

    def right_context_menu(self, pos):
        pop_menu = QMenu(self)
        pop_menu.triggered.connect(self.right_menu_action_clicked_process)
        index = self.tableView.indexAt(pos)
        if index.isValid():
            self.create_menu(pop_menu, self.project)
            pop_menu.exec_(QCursor.pos())

    def right_menu_action_clicked_process(self, action):
        action_data = action.data()
        item_name = action_data['item_name']
        indexes = self.tableView.selectionModel().selectedRows()
        for index in indexes:
            process_cmd_item = self.tableview_model.item(index.row(), self.tableview_model.columnCount() - 1)
            process_cmd_item.setText(item_name)
            process_cmd_item.setData(action_data)

    def create_menu(self, pop_menu, project_entity):
        project_name = project_entity['name']
        project_type = project_entity['sg_type']
        entity_data = analyze_xml.EntityData()
        entity_data.project_name = project_name
        entity_data.project_type = project_type
        xml_name = 'right_menu_config.xml'
        action_list = analyze_xml.GetXMLData(entity_data).get_batch_process_data(xml_name)
        if action_list:
            self.add_menu_action(pop_menu, action_list)

    def add_menu_action(self, menu, action_list):
        tab_set = set()
        for temp in action_list:
            tab_set.add(temp['tab_name'])

        tab_list = list(tab_set)
        for tab_name in tab_list:
            second_menu = QMenu(self)
            second_menu.setTitle(tab_name)
            for action_info in action_list:
                text = action_info['item_name']
                tool_tip = action_info['toolTip']
                if tab_name == action_info['tab_name']:
                    action = QAction(second_menu)
                    action.setText(text)
                    action.setData(action_info)
                    action.setToolTip(tool_tip)
                    second_menu.addAction(action)

            menu.addMenu(second_menu)

    def update_ui(self, tuple_data):
        item, text, tooltip, background = tuple_data
        item.setText(text)
        if background:
            item.setBackground(background)
        if tooltip:
            item.setToolTip(tooltip)

    def setup(self):
        self._listwidget=_listwidget.ListWidget()
        self.widget = QWidget()
        self.widget.setGeometry(QRect(61, 31, 300, 200))
        self.widget.setObjectName('widget')
        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName('gridLayout')
        self.setLayout(self.gridLayout)
        self.verticalLayoutMain = QVBoxLayout()
        self.widgetProjectName = QWidget()
        self.horizontalLayout_2 = QHBoxLayout(self.widgetProjectName)
        self.horizontalLayoutProject = QHBoxLayout()
        self.horizontalSpacerLeft = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.horizontalLayoutProject.addItem(self.horizontalSpacerLeft)
        self.labelProjectName = QLabel(self.widgetProjectName)
        self.horizontalLayoutProject.addWidget(self.labelProjectName)
        self.horizontalSpacerRight = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.horizontalLayoutProject.addItem(self.horizontalSpacerRight)
        self.horizontalLayout_2.addLayout(self.horizontalLayoutProject)
        self.verticalLayoutMain.addWidget(self.widgetProjectName)
        self.tableView = MyQTableView()
        self.tableView.setLayoutDirection(Qt.LeftToRight)
        self.tableView.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.verticalLayoutMain.addWidget(self.tableView)
        self.horizontalLayout = QHBoxLayout()
        self.pushButtonProcess = QPushButton()
        self.pushButtonProcess.setObjectName('pushButtonProcess')
        self.horizontalLayout.addWidget(self.pushButtonProcess)
        self.pushButtonCancel = QPushButton()
        self.pushButtonCancel.setObjectName('pushButtonCancel')
        self.horizontalLayout.addWidget(self.pushButtonCancel)
        self.pushButtonChosenAll = QPushButton()
        self.pushButtonChosenAll.setObjectName('pushButtonChosenAll')
        self.horizontalLayout.addWidget(self.pushButtonChosenAll)
        self.pushButtonDeleteAll = QPushButton()
        self.pushButtonDeleteAll.setObjectName('pushButtonDeleteAll')
        self.horizontalLayout.addWidget(self.pushButtonDeleteAll)
        self.pushButtonDelete = QPushButton()
        self.pushButtonDelete.setObjectName('pushButtonDelete')
        self.horizontalLayout.addWidget(self.pushButtonDelete)
        self.pushButtonResetReady = QPushButton()
        self.pushButtonResetReady.setObjectName('pushButtonResetReady')
        self.horizontalLayout.addWidget(self.pushButtonResetReady)
        self.verticalLayoutMain.addLayout(self.horizontalLayout)
        self.groupBoxNote = QGroupBox()
        self.groupBoxNote.setObjectName('groupBoxNote')
        self.groupBoxNote.setMinimumSize(QSize(0, 100))
        self.verticalLayout = QVBoxLayout(self.groupBoxNote)
        self.verticalLayout.setObjectName('verticalLayout')
        self.textNotes = QTextBrowser(self.groupBoxNote)
        self.textNotes.setObjectName('textNotes')
        self.verticalLayout.addWidget(self.textNotes)
        self.gridLayout.addLayout(self.verticalLayoutMain, 0, 0, 1, 1)
        self.gridLayout.addWidget(self._listwidget, 0, 1, 1, 1)
        self.labelProjectName.setText('项目名称')
        self.pushButtonProcess.setText('执行')
        self.pushButtonCancel.setText('取消')
        self.pushButtonChosenAll.setText('选择所有')
        self.pushButtonDelete.setText('删除选中')
        self.pushButtonDeleteAll.setText('删除全部')
        self.pushButtonResetReady.setText('重置')
        self.groupBoxNote.setTitle('插件介绍')
        self.textNotes.setHtml('请将需要处理的文件或者文件夹拖到上方的表格上，即可完成放置文件操作。在工具界面鼠标右键即可看到不同项目插件，点击运行即可')


# if __name__ == '__main__':
#     # import glob
#     # print(glob)
#     import sys
#
#     project_list = "[{'id': 114, 'name': 'X3', 'type': 'Project', 'sg_type': 'Game'}]"
#     app = QApplication(sys.argv)
#     dialog = Batch(project_list)
#     log_file = r'D:\temp_info\batch_publish\40bb0b9ced324e9cb26d23aadee6f016.log'
#     log_info =dialog._read_info(log_file)
#     # print(log_info)
#     for info in log_info:
#         print('info:',info)
#         dialog._ProcessInfo(info)
#
#     dialog.show()
#     sys.exit(app.exec_())
