# -*- coding: utf-8 -*-
# -------------------------------------------------------
# @File    : ai_video_match_ui.py
# @Author  : linhuan
# @Time    : 2025/7/3 11:44
# @Description :
# -------------------------------------------------------
import os.path

try:
    from PySide2.QtWidgets import *
    from PySide2.QtGui import *
    from PySide2.QtCore import *
except:
    from PyQt5.QtWidgets import *
    from PyQt5.QtGui import *
    from PyQt5.QtCore import *
TABHEADERS = [u'CutScene名称', u'场次', u'任务名', u'宣发视频时间范围', u'CutScene帧数范围', u'最低相似度']
WIDTHS = [400, 300, 150, 150, 300, 300, 200]
from apps.publish.ui.message.messagebox import msgview
from apps.tools.common.ai_video_match_tool import ai_video_match_fun
import apps.tools.common.ai_video_match_tool.sg_login as sg_login
from lib.common.log import Logger
from apps.tools.common.ai_video_match_tool import process_media

reload(process_media)

import getpass


class AIVideoMatchUI(QWidget):
    def __init__(self, frame_out=10, fps=30):
        super(AIVideoMatchUI, self).__init__(parent=None)
        self.__setup_ui()
        self.__frame_out = frame_out
        self.__user = getpass.getuser()
        self.__current_data = self.__get_current_time()
        self.__log_handle = Logger(self.__get_log_file())
        self.__fps = fps

    def __setup_ui(self):
        self.setWindowTitle('AI视频对比工具')
        self.setGeometry(100, 100, 600, 600)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.WindowCloseButtonHint)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.__main_layout = QVBoxLayout(self)
        self.__main_layout.setContentsMargins(20, 20, 20, 20)
        self.__main_layout.setSpacing(10)
        self.__init_ui()
        self.__connect_signals()
        self.__sg = sg_login.Config().login()

    def __init_ui(self):

        self._modle_layout = QHBoxLayout()



        self._process_layout = QVBoxLayout()
        self.__select_group = QGroupBox('视频对比匹配')
        self.__select_group.setStyleSheet("QGroupBox { border: 1px solid #555555; border-radius: 5px; padding: 10px; }")
        self.__select_layout = QVBoxLayout()
        self.__select_group.setLayout(self.__select_layout)
        self._process_layout.addWidget(self.__select_group)
        self.__select_layout.setContentsMargins(10, 10, 10, 10)
        self.__select_layout.setSpacing(10)

        self.__long_video_layout = QHBoxLayout()
        self.__long_video_layout.setAlignment(Qt.AlignTop)
        self.__long_video_label = QLabel(u'宣发视频:')
        self.__long_video_input = QLineEdit()
        self.__long_video_input.setPlaceholderText(u'【输入|选择】宣发视频路径')
        self.__long_video_button = QPushButton(u'浏览')
        self.__long_video_button.setToolTip(u'选择宣发视频文件')
        self.__long_video_layout.addWidget(self.__long_video_label)
        self.__long_video_layout.addWidget(self.__long_video_input)
        self.__long_video_layout.addWidget(self.__long_video_button)
        self.__select_layout.addLayout(self.__long_video_layout)

        self.__sequence_layout = QHBoxLayout()
        self.__sequence_layout.setAlignment(Qt.AlignTop)
        self.__sequence_label = QLabel(u'匹配場次:')
        self.__sequence_input = QLineEdit()
        self.__sequence_input.setPlaceholderText(u'【输入】CutScene场次(输入多个场次请用;分隔)')
        self.__sequence_layout.addWidget(self.__sequence_label)
        self.__sequence_layout.addWidget(self.__sequence_input)
        self.__select_layout.addLayout(self.__sequence_layout)

        self.__task_check_layout = QHBoxLayout()
        self.__task_check_label = QLabel(u'包含任务:')
        self.__cts_final_check = QCheckBox(u'cts_final')
        self.__cts_final_check.setChecked(True)
        self.__lgt_final_check = QCheckBox(u'lgt_final')
        self.__lgt_final_check.setChecked(True)
        self.__lut_check = QCheckBox(u'lut')
        self.__lut_check.setChecked(True)
        self.__sfx_final_check = QCheckBox(u'sfx_final')
        self.__sfx_final_check.setChecked(True)
        self.__hair_all_check = QCheckBox(u'hair_all')
        self.__hair_all_check.setChecked(True)
        self.__final_check_check = QCheckBox(u'check')
        self.__final_check_check.setChecked(True)

        self.__task_check_layout.addWidget(self.__task_check_label)
        self.__task_check_layout.addWidget(self.__cts_final_check)
        self.__task_check_layout.addWidget(self.__lgt_final_check)
        self.__task_check_layout.addWidget(self.__lut_check)
        self.__task_check_layout.addWidget(self.__sfx_final_check)
        self.__task_check_layout.addWidget(self.__hair_all_check)
        self.__task_check_layout.addWidget(self.__final_check_check)
        self.__select_layout.addLayout(self.__task_check_layout)

        self.__match_button = QPushButton(u'开始对比视频')
        self.__match_button.setFixedHeight(35)
        self.__select_layout.addWidget(self.__match_button)

        self.__progress_bar = QProgressBar()
        self.__progress_bar.setValue(0)
        self.__progress_bar.setVisible(False)
        self.__progress_label = QLabel(u'')
        self.__progress_label.setAlignment(Qt.AlignCenter)
        self.__select_layout.addWidget(self.__progress_label)
        self.__select_layout.addWidget(self.__progress_bar)
        self.__progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #34495e;
                border-radius: 7px;
                background: #ecf0f1;
                height: 14px;
            }
            QProgressBar::chunk {
                background-color: #3498db;  /* 蓝色 */
                border-radius: 7px;
            }
        """)

        self.__match_result_layout = QVBoxLayout()
        self.__display_group = QGroupBox('对比结果')
        self.__display_group.setStyleSheet(
            "QGroupBox { border: 1px solid #555555; border-radius: 5px; padding: 10px; }")

        self.__display_layout = QVBoxLayout()
        self.__display_group.setLayout(self.__display_layout)
        self.__match_result_layout.addWidget(self.__display_group)
        self.__display_layout.setAlignment(Qt.AlignTop)

        self.__init_display_table()

        self.__main_layout.addLayout(self._process_layout)
        self.__main_layout.addLayout(self.__match_result_layout)

    def __get_log_file(self):
        __dir = r'Z:\Data\ai_video_match\logs'
        if not os.path.exists((__dir)):
            os.makedirs(__dir)
        return '{}/ai_video_match_{}.log'.format(__dir, self.__current_data)

    def __get_json_file(self):
        __dir = r'Z:\Data\ai_video_match\jsons'
        if not os.path.exists((__dir)):
            os.makedirs(__dir)
        return '{}/ai_video_match_{}.json'.format(__dir, self.__current_data)

    def __get_current_time(self):
        import datetime
        return (datetime.datetime.now().strftime('%Y-%m-%d__%H-%M-%S'))

    def __connect_signals(self):
        self.__long_video_button.clicked.connect(self.__select_long_video_clicked)
        self.__match_button.clicked.connect(self.__start_video_match_clicked)

    def __select_long_video_clicked(self):
        video_path, _ = QFileDialog.getOpenFileName(self, '选择宣发视频', '', '视频文件 (*.mp4)')
        if video_path:
            self.__long_video_input.setText(video_path)

    def __start_video_match_clicked(self):

        __start_time = QTime.currentTime()
        self.__log_handle.info(u'开始时间:{}'.format(__start_time.toString('hh:mm:ss.zzz')))

        __long_video_path = self.__long_video_input.text().strip()

        __sequence = self.__sequence_input.text().strip()
        if not __long_video_path:
            msgview(u'请先选择或填入宣发视频文件', 1)
            return
        if not os.path.exists(__long_video_path):
            msgview(u'宣发视频文件不存在，请检查路径', 1)
            return
        if not __long_video_path.endswith('.mp4'):
            msgview(u'宣发视频文件格式不正确，请选择mp4格式的视频文件', 1)
            return
        if not __sequence:
            msgview(u'请先输入CutScene场次', 1)
            return
        __sequence_list = self.__get_sequence_list(__sequence)
        if not __sequence_list:
            msgview(u'CutScene场次不能为空，请输入有效的场次', 1)
            return

        __task_list = self.__get_task_list()
        if not __task_list:
            msgview(u'请至少选择包含一个任务类型', 1)
            return
        ok, result = self.__judge_sequence_list(__sequence_list)
        if not ok:
            msgview(result, 1)
            return
        __sequences = result
        ok, result = ai_video_match_fun.find_sequences_shots_laster_version_data(self.__sg, __sequences, __task_list)
        if not ok:
            msgview(result, 1)
            return
        __sequences_shots_versions_data = result
        if self.__log_handle:
            self.__log_handle.info(u'任务提交用户:{}'.format(self.__user))
            self.__log_handle.info(u'宣发视频：{}'.format(__long_video_path))
            self.__log_handle.info(u'CutScene场次：{}'.format(__sequence_list))
        self.__progress_bar.setVisible(True)
        self.__progress_bar.setValue(0)
        self.worker = Worker(__long_video_path, __sequences_shots_versions_data, self.__log_handle, self.__frame_out,
                             self.__fps)
        self.__sequences_shots_versions_data = __sequences_shots_versions_data
        self.worker.progress_signal.connect(self.__on_progress_update)
        self.worker.result_signal.connect(self.__on_ai_finished)
        self.worker.start()

    def __on_progress_update(self, value, service_name):
        self.__progress_bar.setValue(value)
        self.__progress_label.setText(u"{} ({}%)".format(service_name, value))
        # ai_data = result
        # # self.__log_handle.info('__sequences_shots_versions_data : {}'.format(__sequences_shots_versions_data))
        # display_data = self.get_display_data(ai_data, __sequences_shots_versions_data)
        # if not display_data:
        #     msgview(u'没有找到有效的AI计算相似度数据', 1)
        #     return
        #
        # self.__log_handle.info('display_data: {}'.format(display_data))
        #
        # __stop_time = QTime.currentTime()
        # self.__log_handle.info(u'结束时间:{}'.format(__stop_time.toString('hh:mm:ss.zzz')))
        # json_file = self.__get_json_file()
        # ai_video_match_fun.write_json_to_file(display_data, json_file)
        #
        # # json_file = r'Z:\Data\ai_video_match\jsons\ai_video_match_2025-09-01__18-14-17.json'
        # # display_data = ai_video_match_fun.read_json_file(json_file)
        #
        # self.__create_display_table_by_data(display_data)

    def __setup_header(self, width_list):
        labels = [
            self.__sequence_lable,
            self.__cutscene_lable,
            self.__task_lable,
            self.__long_video_frame_range_lable,
            self.__cutscene_frame_range_lable,
            self.__min_similarity_lable
        ]
        for i, w in enumerate(width_list):
            labels[i].setFixedWidth(w)

    def __init_display_table(self):
        self.__tree_widget = QTreeWidget()
        self.__tree_widget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.__tree_widget.customContextMenuRequested.connect(self.__on_tree_context_menu)
        self.__display_layout.addWidget(QLabel(u'请先点击"开始对比视频"按钮进行视频对比匹配'))
        self.__display_layout.addWidget(self.__tree_widget)

    def __on_tree_context_menu(self, pos):
        menu = QMenu(self)
        process_open_long_video_action = QAction(u'打开宣发视频', self)
        process_open_long_video_action.triggered.connect(self.__process_open_long_video)
        menu.addAction(process_open_long_video_action)
        menu.addSeparator()

        process_opend_cutscene_version_action = QAction(u'打开CutScene视频', self)
        process_opend_cutscene_version_action.triggered.connect(self.__process_open_cutscene)
        menu.addAction(process_opend_cutscene_version_action)
        menu.addSeparator()

        process_opend_compared_video_action = QAction(u'打开对比视频', self)
        process_opend_compared_video_action.triggered.connect(self.__process_open_compared_video_version)
        menu.addAction(process_opend_compared_video_action)
        # menu.addSeparator()

        # # process
        # process_action = QAction(u'处理勾选项', self)
        # process_action.triggered.connect(self.__process_checked_children)
        # menu.addAction(process_action)
        menu.exec_(self.__tree_widget.viewport().mapToGlobal(pos))

    def _get_checked_items(self):
        checked_items = []

        def recurse(parent_item):
            for i in range(parent_item.childCount()):
                child = parent_item.child(i)
                if child.checkState(0):  # 0 表示第一列
                    checked_items.append(child)
                recurse(child)

        for i in range(self.__tree_widget.topLevelItemCount()):
            top_item = self.__tree_widget.topLevelItem(i)
            if top_item.checkState(0):
                checked_items.append(top_item)
            recurse(top_item)

        return checked_items

    def __process_open_compared_video_version(self):
        selected_items = self.__get_selected_items()
        # selected_items = self.__tree_widget.selectedItems()
        if not selected_items:
            msgview(u'请先选择一行数据', 1)
            return
        if len(selected_items) > 1:
            msgview(u'请只选择一行数据', 1)
            return
        item = selected_items[0]
        data = item.data(0, Qt.UserRole)
        com_video = data.get('com_video', '') if 'com_video' in data else None

        if not com_video:
            cutscene_version_path = data.get('cutscene_version_path', '')
            long_video = data.get('long_video', '')
            long_video_start_frame = data.get('long_start_frame', 0)
            long_video_end_frame = data.get('long_end_frame', 0)
            cutscene_start_frame = data.get('cutscene_start_frame', 0)
            cutscene_end_frame = data.get('cutscene_end_frame', 0)
            ok, result = process_media.comb_mov_seq_side(long_video, cutscene_version_path, long_video_start_frame,
                                                         long_video_end_frame, cutscene_start_frame, cutscene_end_frame,
                                                         sc=0.5, fps=30)
            if not ok:
                msgview(result, 1)
                return
            else:
                com_video = result
                data['com_video'] = com_video
                item.setData(0, Qt.UserRole, data)
                os.startfile(com_video)
        else:
            if com_video and os.path.exists(com_video):
                os.startfile(com_video)
            else:
                msgview(u'对比视频文件不存在，请检查', 1)
                return

        # item.setProperty('com_video', com_video)

    def __get_selected_items(self):
        return self._get_checked_items()
        # return self.__tree_widget.selectedItems()
        # __selected_items=[]
        # _items = self.__tree_widget.items()
        # if not _items:
        #     return []
        # for item in _items:
        #     if item.checkState(0) == Qt.Checked:
        #         __selected_items.append(item)
        # return __selected_items

    def __process_open_cutscene(self):
        selected_items = self.__get_selected_items()
        # selected_items = self.__tree_widget.selectedItems()
        if not selected_items:
            msgview(u'请先选择一行数据', 1)
            return
        if len(selected_items) > 1:
            msgview(u'请只选择一行数据', 1)
            return
        item = selected_items[0]
        data = item.data(0, Qt.UserRole)

        cutscene_version_path = data.get('cutscene_version_path', '')

        if cutscene_version_path and os.path.exists(cutscene_version_path):
            os.startfile(cutscene_version_path)

            dir_path = os.path.dirname(cutscene_version_path)

            if os.path.exists(dir_path):
                cmd = 'cmd.exe /C start "Folder" "%s"' % dir_path
                exit_code = os.system(cmd)
                if exit_code != 0:
                    raise Exception(u'打开文件夹失败,请检查路径是否正确')
            else:
                msgview(u'本机CutScene视频文件夹路径不存在，请检查', 1)
        else:
            msgview(u'本机CutScene视频路径不存在，请检查', 1)

    def __process_open_long_video(self):
        selected_items = self.__get_selected_items()
        # selected_items = self.__tree_widget.selectedItems()

        if not selected_items:
            msgview(u'请先选择一行数据', 1)
            return
        if len(selected_items) > 1:
            msgview(u'请只选择一行数据', 1)
            return
        item = selected_items[0]
        data = item.data(0, Qt.UserRole)
        ai_data = data.get('ai_data', [])
        long_video = data.get('long_video', '')
        if long_video and os.path.exists(long_video):
            os.startfile(long_video)
        else:
            msgview(u'宣发视频文件不存在，请检查', 1)

    def __process_open_cutscene_version(self):
        selected_items = self.__get_selected_items()
        # selected_items = self.__tree_widget.selectedItems()
        if not selected_items:
            msgview(u'请先选择一行数据', 1)
            return
        if len(selected_items) > 1:
            msgview(u'请只选择一行数据', 1)
            return
        item = selected_items[0]
        data = item.data(0, Qt.UserRole)
        cutscene_version_path = data.get('cutscene_version_path', '')
        if cutscene_version_path and os.path.exists(cutscene_version_path):
            os.startfile(cutscene_version_path)
        else:
            msgview(u'本机CutScene视频路径不存在，请检查', 1)

    def __process_checked_children(self):
        checked_items = []
        root = self.__tree_widget.invisibleRootItem()
        for i in range(root.childCount()):
            parent = root.child(i)
            for j in range(parent.childCount()):
                child = parent.child(j)
                if child.checkState(0) == Qt.Checked:
                    checked_items.append(child)
        # 对 checked_items 做你需要的处理
        for item in checked_items:
            data = item.data(0, Qt.UserRole)
            cutscene_version_path = data.get('cutscene_version_path', '')

    def __create_display_table_by_data(self, display_data):
        self.__tree_widget.clear()

        self.__tree_widget.setColumnCount(len(TABHEADERS) - 1)
        self.__tree_widget.setHeaderLabels(TABHEADERS)
        self.__display_layout.addWidget(self.__tree_widget)

        self.__tree_widget.setColumnCount(len(TABHEADERS))
        self.__tree_widget.setHeaderLabels(TABHEADERS)
        self.__tree_widget.setRootIsDecorated(False)  # 去掉缩进
        self.__tree_widget.setAlternatingRowColors(False)

        # 设置列头
        header = self.__tree_widget.header()
        for i in range(self.__tree_widget.columnCount()):
            header.setSectionResizeMode(i, QHeaderView.Interactive)
        header.setStretchLastSection(True)
        header.setDefaultAlignment(Qt.AlignCenter)
        header.setFixedHeight(30)
        self.__tree_widget.setColumnWidth(0, 200)  # CutScene 列宽
        self.__tree_widget.setColumnWidth(1, 300)
        self.__tree_widget.setColumnWidth(2, 150)  # 场次列宽
        self.__tree_widget.setColumnWidth(3, 150)  # 任务名列宽
        self.__tree_widget.setColumnWidth(4, 300)
        self.__tree_widget.setColumnWidth(5, 300)  # 宣发视频时间范围列宽

        # 行高统一
        self.__tree_widget.setUniformRowHeights(True)
        self.__tree_widget.setStyleSheet("""
            QTreeWidget {
                background-color: #333333;
                color: #DCDCDC;
                border: 1px solid #555555;
            }
            QTreeWidget::item {
                border-right: 1px solid #555555;  /* 每列右边框 */
                border-bottom: 1px solid #555555; /* 每行底部边框 */
            }
            QHeaderView::section {
                background:#5E5E5E;
                padding:3px;
                margin:0px;
                border:1px solid #555555;          /* 表头分割线 */
                border-left-width:0;
                border-right:0px;
                text-align:center;
                color:#DCDCDC;
            }
        """)

        if not display_data:
            msgview(u'没有有效的显示数据', 1)
            return
        for i in range(len(display_data)):
            squence_name = display_data[i].get('squence_name', '')
            cutscene_name = display_data[i].get('cutscene_name', '')
            task_name = display_data[i].get('task_name', '')
            ai_data = display_data[i].get('ai_data', [])
            if not ai_data:
                continue
            parent = QTreeWidgetItem(self.__tree_widget)
            parent.setText(0, '{}'.format(cutscene_name))
            parent.setSelected(True)
            parent.setData(0, Qt.UserRole, display_data[i])
            # parent.setCheckState(0, Qt.Unchecked)
            # 默认展开
            parent.setExpanded(True)
            for j in range(len(ai_data)):
                ai_item = ai_data[j]
                lv = '{}--{}'.format(self.__cover_two(ai_item.get("long_start_time")),
                                     self.__cover_two(ai_item.get("long_end_time")))
                cf = '{}--{}'.format(ai_item.get("short_start"), ai_item.get("short_end"))
                final_similarity = ai_item.get('final_similarity', [])

                if not final_similarity:
                    continue

                __item_data = {}
                __item_data['long_video'] = display_data[i].get('long_video', '') if 'long_video' in display_data[
                    i] else None
                __item_data['cutscene_version_path'] = display_data[i].get('cutscene_version_path',
                                                                           '') if 'cutscene_version_path' in \
                                                                                  display_data[i] else None
                __item_data['long_start_frame'] = ai_item.get('start', 0) if 'start' in ai_item else None
                __item_data['long_end_frame'] = ai_item.get('end', 0) if 'end' in ai_item else None
                __item_data['cutscene_start_frame'] = ai_item.get('short_start',
                                                                  0) if 'short_start' in ai_item else None
                __item_data['cutscene_end_frame'] = ai_item.get('short_end', 0) if 'short_end' in ai_item else None
                __item_data['similarity_data'] = final_similarity
                # try:
                #     ok, result = process_media.comb_mov_seq_side(__item_data['long_video'],
                #                                                  __item_data['cutscene_version_path'],
                #                                                  __item_data['long_start_frame'],
                #                                                  __item_data['long_end_frame'],
                #                                                  __item_data['cutscene_start_frame'],
                #                                                  __item_data['cutscene_end_frame'], sc=0.5, fps=30)
                #     if not ok:
                #         __item_data['com_video'] = ''
                #     else:
                #         __item_data['com_video'] = result
                # except:
                #     __item_data['com_video'] = ''

                similarity_list = self.__get_similarity_list(final_similarity)
                min_s = min(similarity_list)

                child = QTreeWidgetItem(parent)
                child.setFlags(child.flags() | Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                child.setCheckState(0, Qt.Unchecked)  # 设置为未选中状态
                child.setText(0, cutscene_name)

                child.setData(0, Qt.UserRole, __item_data)
                self.__tree_widget.setStyleSheet("""
                    QTreeWidget::item {
                        border-right: 1px solid #555555;
                        border-bottom: 1px solid #555555;
                        text-align: center;
                    }
                """)
                # child.setTextAlignment(0, Qt.AlignCenter)
                # child.setSizeHint(0, QSize(0, 150))
                child.setText(1, squence_name)
                child.setTextAlignment(1, Qt.AlignCenter)

                child.setText(2, task_name)
                child.setTextAlignment(2, Qt.AlignCenter)

                child.setText(3, lv)
                child.setTextAlignment(3, Qt.AlignCenter)

                child.setText(4, cf)
                child.setTextAlignment(4, Qt.AlignCenter)

                child.setText(5, str(min_s))
                child.setTextAlignment(5, Qt.AlignCenter)

    def __get_similarity_list(self, final_similarity):
        if not final_similarity:
            return []
        similarity_list = []
        for i in range(len(final_similarity)):
            __similarity = final_similarity[i]["similarity"] if final_similarity[i] and "similarity" in \
                                                                final_similarity[i] else None
            if __similarity is None:
                continue
            similarity_list.append(__similarity)
        return similarity_list

    def __cover_two(self, s):
        # 转为小数点后两位
        try:
            return round(float(s), 2)
        except:
            return 0.0

    def __sender_to_ai_requents(self, __long_video_path, __sequences_shots_versions_data, log_handle):
        ok, result = ai_video_match_fun.sender_to_ai_video_npz(__long_video_path, frame_out=self.__frame_out,
                                                               log_handle=self.__log_handle)
        if not ok:
            msgview(u'{}'.format(result), 1)
            return

        long_viedo_data = result

        ok, reslut = ai_video_match_fun.sender_data_to_ai_video_lib(__sequences_shots_versions_data,
                                                                    frame_out=self.__frame_out,
                                                                    log_handle=self.__log_handle)
        if not ok:
            msgview(u'{}'.format(reslut), 1)
            return
        video_lib_versions, errors = reslut
        if errors:
            msgview(u'以下场次视频库版本数据错误: {}'.format(', '.join(errors)), 1)
            return

        ok, result = self.__get_sender_to_ai_get_data(long_viedo_data, video_lib_versions, frame_out=self.__frame_out,
                                                      fps=self.__fps,
                                                      log_handle=self.__log_handle)

        if not ok:
            msgview(u'{}'.format(result), 1)
            return
        print(u'AI计算相似度请求结果:', result)
        return True, result


    def __get_video_list_from_lib_data(self, video_lib_versions):
        __video_list = []
        if not video_lib_versions:
            return __video_list

        for i in range(len(video_lib_versions)):
            __video_file = video_lib_versions[i]['version_file'] if 'version_file' in video_lib_versions[
                i] else None
            if __video_file and os.path.exists(__video_file):
                __video_list.append(__video_file)
        if __video_list:
            __video_list = list(set(__video_list))

        return __video_list

    def __get_task_list(self):
        __task_list = []
        if self.__cts_final_check.isChecked():
            __task_list.append('cts_final')
        if self.__lgt_final_check.isChecked():
            __task_list.append('lgt_final')
        if self.__lut_check.isChecked():
            __task_list.append('lut')
        if self.__sfx_final_check.isChecked():
            __task_list.append('sfx_final')
        if self.__hair_all_check.isChecked():
            __task_list.append('hair_all')
        if self.__final_check_check.isChecked():
            __task_list.append('check')
        return __task_list

    def __judge_sequence_list(self, __sequence_list):
        __sequences = []
        __errors = []
        for __sequence in __sequence_list:
            if not __sequence:
                continue
            ok, result = ai_video_match_fun.find_squence_data_by_squence_name(self.__sg, __sequence)
            if not ok:
                __errors.append(__sequence)
            else:
                __sequences.append(result)
        if __errors:
            return False, u'以下CutScene场次不存在或未找到: {}'.format(', '.join(__errors))
        if not __sequences:
            return False, u'没有找到有效的CutScene场次，请检查输入'
        return True, __sequences

    def __get_sequence_list(self, __sequence):
        return [seq.strip() for seq in __sequence.split(';') if seq.strip()]

    def get_display_data(self, ai_data, sequences_shots_versions_data):

        local_dir = ai_video_match_fun.get_local_video_lib_path()

        if not ai_data:
            msgview(u'没有AI计算相似度数据或场次版本数据', 1)
            return
        if not sequences_shots_versions_data:
            msgview(u'没有场次版本数据', 1)
            return
        __display_data = []

        __long_video = ai_data['long_video'] if 'long_video' in ai_data else None
        long_video = __long_video
        ai_compute_similarity_data = ai_data[
            'ai_compute_similarity_data'] if 'ai_compute_similarity_data' in ai_data else None
        for __sqeuence_data in sequences_shots_versions_data:
            __shot_data = __sqeuence_data["shots_data"] if "shots_data" in __sqeuence_data else None
            __squence_name = __sqeuence_data['squence_code'] if 'squence_code' in __sqeuence_data else None
            if not __shot_data or not __squence_name:
                continue
            if not __shot_data:
                continue
            for i in range(len(__shot_data)):
                __shot_dis_data = {}
                __sht_vesion_data = __shot_data[i]
                if not __sht_vesion_data:
                    continue
                __laster_version = __sht_vesion_data[
                    'laster_version'] if 'laster_version' in __sht_vesion_data else None
                if not __laster_version:
                    continue
                __task_name = __laster_version[
                    "sg_task.Task.content"] if "sg_task.Task.content" in __laster_version else None

                __version_name = __laster_version["code"] if "code" in __laster_version else None
                __shot_name = __sht_vesion_data['shot_name'] if 'shot_name' in __sht_vesion_data else None

                __shot_local_dir = '{}/{}/{}'.format(local_dir, __squence_name, __shot_name)
                if not os.path.exists(__shot_local_dir):
                    os.makedirs(__shot_local_dir)
                __local_shot_path = '{}/{}.mp4'.format(__shot_local_dir, __shot_name)

                __version_path = __laster_version[
                    'sg_path_to_frames'] if 'sg_path_to_frames' in __laster_version else None

                if not __version_path or not os.path.exists(__version_path):
                    self.__log_handle.error(u'场次:{}-镜头:{}-版本:{} 视频路径不存在,请检查'.format(__squence_name, __shot_name,
                                                                                   __version_name))
                    continue

                result = ai_video_match_fun.copy_file(__version_path, __local_shot_path)
                __version = os.path.splitext(__version_name)[0] if __version_name else None
                __shot_dis_data['squence_name'] = __squence_name
                __shot_dis_data['cutscene_name'] = __shot_name
                __shot_dis_data['cutscene_version_path'] = __local_shot_path
                __shot_dis_data['task_name'] = __task_name
                __shot_dis_data['long_video'] = long_video
                __ai_sqenece_data = []
                for j in range(len(ai_compute_similarity_data)):
                    __ai_compute_similarity_data = ai_compute_similarity_data[j]
                    if not __ai_compute_similarity_data:
                        continue
                    short_id = __ai_compute_similarity_data.get('short_id', None)
                    if not short_id:
                        continue
                    if short_id == __version:
                        __ai_sqenece_data.append(__ai_compute_similarity_data)
                if not __ai_sqenece_data:
                    continue
                __shot_dis_data['ai_data'] = __ai_sqenece_data

                __display_data.append(__shot_dis_data)
        if not __display_data:
            msgview(u'没有找到有效的AI计算相似度数据', 1)
            return
        return __display_data

    def __get_video_path(self):
        __long_video_path = self.__long_video_input.text()

        if not __long_video_path:
            msgview(u'请先选择或填入宣发视频文件', 1)
            return None

        if not os.path.exists(__long_video_path):
            msgview(u'宣发视频文件不存在，请检查路径', 1)
            return None

        try:
            long_video_path = __long_video_path.decode('utf-8')
        except:
            long_video_path = __long_video_path.decode('gbk', 'ignore').encode('utf-8)')

        return long_video_path

    def __on_ai_finished(self, ok, result):
        if not ok:
            msgview(result, 1)
            self.__progress_bar.setVisible(False)
            return
        ai_data = result
        if not ai_data:
            msgview(u'AI未计算相似度,请联系@水月@林欢', 1)
            self.__progress_bar.setVisible(False)
            return
        if 'ai_compute_similarity_data' not in ai_data or not ai_data['ai_compute_similarity_data']:
            msgview(u'AI计算相似度数据为空,请联系@水月@林欢', 1)
            self.__progress_bar.setVisible(False)
            return
        if 'Error: unexpected indent' in ai_data['ai_compute_similarity_data']:
            msgview(u'AI计算相似度数据错误,请联系@水月@林欢', 1)
            self.__progress_bar.setVisible(False)
            return
        display_data = self.get_display_data(ai_data, self.__sequences_shots_versions_data)
        if not display_data:
            msgview(u'没有找到有效的AI计算相似度数据', 1)
            self.__progress_bar.setVisible(False)
            return

        __stop_time = QTime.currentTime()
        self.__log_handle.info(u'结束时间:{}'.format(__stop_time.toString('hh:mm:ss.zzz')))
        json_file = self.__get_json_file()
        ai_video_match_fun.write_json_to_file(display_data, json_file)
        self.__create_display_table_by_data(display_data)
        self.__progress_bar.setValue(100)
        self.__log_handle.info(u'AI计算完成')
        self.__progress_bar.setVisible(False)
        self.__progress_label.setVisible(False)


class Worker(QThread):
    progress_signal = Signal(int, str)
    result_signal = Signal(bool, object)

    def __init__(self, long_video_path, sequences_shots_versions_data, log_handle, frame_out, fps):
        super(Worker, self).__init__()
        self.long_video_path = long_video_path
        self.sequences_shots_versions_data = sequences_shots_versions_data
        self.log_handle = log_handle
        self.frame_out = frame_out
        self.fps = fps

    def run(self):
        try:
            self.progress_signal.emit(10, u"宣发视频AI特征提取中")
            ok, result = ai_video_match_fun.sender_to_ai_video_npz(
                self.long_video_path, frame_out=self.frame_out, log_handle=self.log_handle
            )
            if not ok:
                self.result_signal.emit(False, result)
                return
            long_viedo_data = result

            self.progress_signal.emit(30, u"场次视频库版本AI特征提取中")

            ok, reslut = ai_video_match_fun.sender_data_to_ai_video_lib(
                self.sequences_shots_versions_data, frame_out=self.frame_out, log_handle=self.log_handle
            )
            if not ok:
                self.result_signal.emit(False, reslut)
                return
            video_lib_versions, errors = reslut
            if errors:
                self.result_signal.emit(False, u'以下场次视频库版本数据错误: {}'.format(', '.join(errors)))
                return

            self.progress_signal.emit(70, u"AI相似度计算中")
            ok, result = self.__get_sender_to_ai_get_data(
                long_viedo_data, video_lib_versions, self.frame_out, self.fps, log_handle=self.log_handle
            )
            if not ok:
                self.result_signal.emit(False, result)
                return
            self.log_handle.info(u'AI计算相似度请求结果: {}'.format(ok))

            self.progress_signal.emit(90, u'已完成AI计算')
            self.result_signal.emit(True, result)
        except Exception as e:
            self.result_signal.emit(False, str(e))

    def __get_sender_to_ai_get_data(self, long_viedo_data, video_lib_versions, frame_out, fps, log_handle=None):
        if not long_viedo_data or not video_lib_versions:
            msgview(u'长视频数据或场次版本数据不能为空', 1)
            return
        __long_npz_file = long_viedo_data['npz_file'] if 'npz_file' in long_viedo_data else None
        __long_video = long_viedo_data['video_file'] if 'video_file' in long_viedo_data else None
        __shot_npz_list = self.__get_npz_from_lib_data(video_lib_versions)

        if not __long_npz_file or not os.path.exists(__long_npz_file):
            msgview(u'长视频npz文件不存在，请检查', 1)
            return
        if not __long_video or not os.path.exists(__long_video):
            msgview(u'长视频文件不存在，请检查', 1)
            return
        if not __shot_npz_list:
            msgview(u'没有找到有效的场次版本npy文件，请检查', 1)
            return


        ok, result = ai_video_match_fun.get_ai_compute_similarity_request(__long_npz_file ,__shot_npz_list, frame_out,fps,log_handle)

        if not ok:
            msgview(result, 1)
            return

        __data = {}

        ai_compute_similarity_data = result

        if not ai_compute_similarity_data:
            msgview(u'AI计算相似度数据为空，请检查', 1)
            return
        __data['ai_compute_similarity_data'] = ai_compute_similarity_data
        __data['long_video'] = __long_video
        return True, __data

    def __get_npz_from_lib_data(self, video_lib_versions):
        __npy_list = []
        if not video_lib_versions:
            return __npy_list

        for i in range(len(video_lib_versions)):
            __npz_file = video_lib_versions[i]['npz_file'] if 'npz_file' in video_lib_versions[i] else None
            if __npz_file and os.path.exists(__npz_file):
                __npy_list.append(__npz_file)
        if __npy_list:
            __npy_list = list(set(__npy_list))

        return __npy_list

    def __get_video_list_from_lib_data(self, video_lib_versions):
        __video_list = []
        if not video_lib_versions:
            return __video_list

        for i in range(len(video_lib_versions)):
            __video_file = video_lib_versions[i]['version_file'] if 'version_file' in video_lib_versions[
                i] else None
            if __video_file and os.path.exists(__video_file):
                __video_list.append(__video_file)
        if __video_list:
            __video_list = list(set(__video_list))

        return __video_list

# class AIVideoMatch(QWidget):
#     def __init_ui(self):
#         # 在按钮下方增加进度条
#         self.__progress_bar = QProgressBar()
#         self.__progress_bar.setValue(0)
#         self.__progress_bar.setVisible(False)
#         self.__select_layout.addWidget(self.__progress_bar)
#
#     def __start_video_match_clicked(self, long_video_path, sequences_shots_versions_data, log_handle, frame_out, fps):
#         self.__progress_bar.setVisible(True)
#         self.__progress_bar.setValue(0)
#         self.worker = Worker(long_video_path, sequences_shots_versions_data, log_handle, frame_out, fps)
#         self.worker.progress_signal.connect(self.__progress_bar.setValue)
#         self.worker.result_signal.connect(self.__on_ai_finished)
#         self.worker.start()
#
#     def __on_ai_finished(self, ok, result):
#         if not ok:
#             msgview(result, 1)
#             self.__progress_bar.setVisible(False)
#             return
#         ai_data = result
#         display_data = self.get_display_data(ai_data, self.__sequences_shots_versions_data)
#         if not display_data:
#             msgview(u'没有找到有效的AI计算相似度数据', 1)
#             self.__progress_bar.setVisible(False)
#             return
#
#         self.__create_display_table_by_data(display_data)
#         self.__progress_bar.setValue(100)
#         self.__log_handle.info(u'AI计算完成')

if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    window = AIVideoMatchUI()
    window.show()
    sys.exit(app.exec_())
#     _json=r'E:\dev01\apps\tools\common\ai_video_match_tool\squence.json'
#     __sequences_shots_versions_data=ai_video_match_fun.read_json_file(_json)
#     _data_json=r'Z:\Data\ai_video_matc\jsons\match_feb538bdb534718be5ce7bf531de0eb9_1756731000991.json'
#
#     _ai_data=ai_video_match_fun.read_json_file(_data_json)
#     ai_data={}
#     ai_data['ai_compute_similarity_data']=_ai_data
#     ai_data['long_video']=r'Z:\test-AI\YGD0026_PV.mp4'
#     print get_display_data(ai_data,__sequences_shots_versions_data)
