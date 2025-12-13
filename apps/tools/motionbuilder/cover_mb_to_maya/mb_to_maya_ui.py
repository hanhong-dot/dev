# -*- coding: utf-8 -*-
# author: linhuan
# file: mb_to_maya_ui.py
# time: 2025/11/27 10:58
# description:
import os

from PySide2.QtWidgets import *
from PySide2.QtCore import *

from lib.common.log import Logger
from apps.publish.ui.message.messagebox import msgview
import json

from apps.tools.motionbuilder.cover_mb_to_maya import sg_fun as mb_sg_fun

reload(mb_sg_fun)

from apps.tools.motionbuilder.cover_mb_to_maya import mb_process_fun

reload(mb_process_fun)


class CoverMBToMayaUI(QDialog):
    def __init__(self, parent=None):
        super(CoverMBToMayaUI, self).__init__(parent)
        self.__mb_window_name = "CoverMBToMayaUI"
        self.__mb_window_title = "MB至Maya批量转换工具"
        self.__mb_window_size = (600, 200)
        self.__current_time = self.__get_current_time()
        self.__local_dir = self.__get_local_dir()
        self._log_file = '{}/cover_mb_to_maya_{}.log'.format(
            self.__get_local_dir('Info_Temp/mobu/cover_mb_to_maya/log'), self.__current_time)
        self.__init_ui()
        self.__logger = Logger(self._log_file)
        self.__connect_signals()

    def __init_ui(self):
        self.setWindowTitle(self.__mb_window_title)
        self.resize(self.__mb_window_size[0], self.__mb_window_size[1])
        self.__main_layout = QVBoxLayout(self)

        self.__prp_group_box = QGroupBox(u"转换设置")
        self.__main_layout.addWidget(self.__prp_group_box)
        self.__prp_group_box.setLayout(QVBoxLayout())
        self.__proper_a_layout = QVBoxLayout()
        self.__prp_group_box.layout().addLayout(self.__proper_a_layout)

        self.__proper_layout = QHBoxLayout()
        self.__modle_layout = QHBoxLayout()
        self.__model_label = QLabel(u"转换模式:")
        self.__current_radio = QRadioButton(u"当前文件")
        self.__current_radio.setChecked(True)
        self.__batch_radio = QRadioButton(u"批量文件")
        self.__batch_radio.setChecked(False)
        self.__mode_group = QButtonGroup(self)
        self.__mode_group.setExclusive(True)
        self.__mode_group.addButton(self.__current_radio)
        self.__mode_group.addButton(self.__batch_radio)
        self.__modle_layout.addWidget(self.__model_label)
        self.__modle_layout.addWidget(self.__current_radio)
        self.__modle_layout.addWidget(self.__batch_radio)
        self.__modle_layout.addStretch()
        # 添加空格

        # 烘焙单选（使用 QButtonGroup 保证互斥，与模式无关）
        self.__bake_layout = QHBoxLayout()
        self.__bake_label = QLabel(u"是否烘焙动画:")
        self.__bake_yes_radio = QRadioButton(u"是")
        self.__bake_yes_radio.setChecked(False)
        self.__bake_no_radio = QRadioButton(u"否")
        self.__bake_no_radio.setChecked(True)
        self.__bake_group = QButtonGroup(self)
        self.__bake_group.setExclusive(True)
        self.__bake_group.addButton(self.__bake_yes_radio)
        self.__bake_group.addButton(self.__bake_no_radio)
        self.__bake_layout.addWidget(self.__bake_label)
        self.__bake_layout.addWidget(self.__bake_yes_radio)
        self.__bake_layout.addWidget(self.__bake_no_radio)
        self.__bake_layout.addWidget(self.__bake_label)
        self.__bake_layout.addWidget(self.__bake_yes_radio)
        self.__bake_layout.addWidget(self.__bake_no_radio)
        self.__bake_layout.addStretch()

        self.__proper_layout.addLayout(self.__modle_layout)
        self.__proper_layout.addLayout(self.__bake_layout)
        self.__proper_a_layout.addLayout(self.__proper_layout)
        self.__proper_layout.addStretch()
        self.__proper_layout.addSpacing(40)

        self.__batch_file_widget = QWidget()
        self.__batch_file_layout = QHBoxLayout(self.__batch_file_widget)
        self.__batch_file_label = QLabel(u"批量文件路径:")
        self.__batch_file_input = QLineEdit()
        self.__batch_file_browse = QPushButton(u"浏览")
        self.__batch_file_layout.addWidget(self.__batch_file_label)
        self.__batch_file_layout.addWidget(self.__batch_file_input)
        self.__batch_file_layout.addWidget(self.__batch_file_browse)
        self.__batch_file_layout.addSpacing(40)

        self.__batch_file_widget.setVisible(False)

        self.__proper_a_layout.addWidget(self.__batch_file_widget)
        self.__proper_a_layout.addLayout(self.__batch_file_layout)

        self.__mapping_layout = QVBoxLayout()
        self.__mapping_label = QLabel(u"映射关系(格式:MB Rig名称:Maya资产名称):")
        self.__mapping_rig_layout = QGridLayout()
        self.__mapping_layout.addWidget(self.__mapping_label)
        self.__mapping_layout.addLayout(self.__mapping_rig_layout)

        self.__proper_a_layout.addLayout(self.__mapping_layout)

        self.__pl_layout = QHBoxLayout()
        self.__pl_label = QLabel("PL_Rig")
        self.__pl_input = QLineEdit("PL_Body")
        self.__pl_layout.addWidget(self.__pl_label)
        self.__pl_layout.addWidget(self.__pl_input)
        self.__mapping_rig_layout.addLayout(self.__pl_layout, 0, 0)

        self.__st_layout = QHBoxLayout()
        self.__st_label = QLabel("ST_Rig")
        self.__st_input = QLineEdit("ST_Body")
        self.__st_layout.addWidget(self.__st_label)
        self.__st_layout.addWidget(self.__st_input)
        self.__mapping_rig_layout.addLayout(self.__st_layout, 0, 1)

        self.__fy_layout = QHBoxLayout()
        self.__fy_label = QLabel("FY_Rig")
        self.__fy_input = QLineEdit("FY_Body_New")
        self.__fy_layout.addWidget(self.__fy_label)
        self.__fy_layout.addWidget(self.__fy_input)
        self.__mapping_rig_layout.addLayout(self.__fy_layout, 0, 2)

        self.__ry_layout = QHBoxLayout()
        self.__ry_label = QLabel("RY_Rig")
        self.__ry_input = QLineEdit("RY_Body")
        self.__ry_layout.addWidget(self.__ry_label)
        self.__ry_layout.addWidget(self.__ry_input)
        self.__mapping_rig_layout.addLayout(self.__ry_layout, 1, 0)

        self.__yg_layout = QHBoxLayout()
        self.__yg_label = QLabel("YG_Rig")
        self.__yg_input = QLineEdit("YG_Body")
        self.__yg_layout.addWidget(self.__yg_label)
        self.__yg_layout.addWidget(self.__yg_input)
        self.__mapping_rig_layout.addLayout(self.__yg_layout, 1, 1)

        self.__ys_layout = QHBoxLayout()
        self.__ys_label = QLabel("YS_Rig")
        self.__ys_input = QLineEdit("YS_Body")
        self.__ys_layout.addWidget(self.__ys_label)
        self.__ys_layout.addWidget(self.__ys_input)
        self.__mapping_rig_layout.addLayout(self.__ys_layout, 1, 2)

        self.__xl_layout = QHBoxLayout()
        self.__xl_label = QLabel("XL_Rig")
        self.__xl_input = QLineEdit("XL_Body")
        self.__xl_layout.addWidget(self.__xl_label)
        self.__xl_layout.addWidget(self.__xl_input)
        self.__mapping_rig_layout.addLayout(self.__xl_layout, 2, 0)
        self.__mapping_rig_layout.setColumnStretch(3, 1)
        self.__mapping_layout.addStretch()

        self.__btn_layout = QVBoxLayout()
        self.__btn_confirm = QPushButton(u"确认转换")
        # 点击时颜色为 rgb(50, 150, 145)
        self.__btn_confirm.setStyleSheet("""
        QPushButton{
            background-color: rgb(30, 90, 87);
            color: white;
            border: 0;
            border-radius: 4px;
        }
        QPushButton:hover{
            background-color: rgb(50, 150, 145);
        }
        QPushButton:pressed{
            background-color: rgb(50, 150, 145);
        }
        QPushButton:disabled{
            background-color: #505050;
            color: #9a9a9a;
        }
        """)
        self.__btn_log = QPushButton(u"打开日志")
        self.__btn_file = QPushButton(u"打开输出文件夹(maya)")
        self.__btn_layout.addWidget(self.__btn_confirm)
        self.__btn_layout.addWidget(self.__btn_log)
        self.__btn_layout.addWidget(self.__btn_file)
        self.__btn_confirm.setFixedHeight(25)
        # self.__btn_log.setFixedHeight(30)
        # self.__btn_file.setFixedHeight(30)
        self.__btn_layout.addStretch()
        self.__main_layout.addLayout(self.__btn_layout)

    def __connect_signals(self):

        self.__current_radio.toggled.connect(self.__on_mode_changed)
        self.__btn_confirm.clicked.connect(self.__on_confirm_clicked)
        self.__batch_file_browse.clicked.connect(self.__on_batch_file_browse)
        self.__btn_log.clicked.connect(self.__on_open_log_clicked)
        self.__btn_file.clicked.connect(self.__on_open_output_dir_clicked)

    def __on_open_log_clicked(self):
        if os.path.exists(self._log_file):
            os.startfile(self._log_file)
        else:
            msgview(u"日志文件不存在！", 0, 0)

    def __on_open_output_dir_clicked(self):
        out_dir = '{}/output/maya'.format(self.__local_dir)
        if os.path.exists(out_dir):
            os.startfile(out_dir)
        else:
            msgview(u"输出文件夹不存在！", 0, 0)

    def __on_mode_changed(self):
        visible = not self.__current_radio.isChecked()
        self.__batch_file_widget.setVisible(visible)

    def __on_batch_file_browse(self):
        dir_path = QFileDialog.getExistingDirectory(self, u"选择批量文件夹路径", "")
        if dir_path:
            self.__batch_file_input.setText(dir_path)

    def __get_local_dir(self, sub_dir='Info_Temp/mobu/cover_mb_to_maya'):
        local_temp_path = set_localtemppath(sub_dir)
        if not os.path.exists(local_temp_path):
            os.makedirs(local_temp_path)
        return local_temp_path

    def __get_current_time(self):
        return QDateTime.currentDateTime().toString("yyyy-MM-dd-hh-mm-ss")

    def __on_confirm_clicked(self):
        from lib.mobu.mb_fun import get_all_characters, mb_get_current_file
        ok = msgview(u"请确认是否开始转换", 1, 1)
        if not ok:
            return
        mode = 'current' if self.__current_radio.isChecked() else 'batch'

        bake = True if self.__bake_yes_radio.isChecked() else False
        if mode == 'batch':
            batch_path = self.__batch_file_input.text().strip()
            if not os.path.exists(batch_path):
                msgview(u"批量文件路径不存在，请检查！", 0, 0)
                return

        mapping = {
            'PL_Rig': self.__pl_input.text().strip(),
            'ST_Rig': self.__st_input.text().strip(),
            'FY_Rig': self.__fy_input.text().strip(),
            'RY_Rig': self.__ry_input.text().strip(),
            'YG_Rig': self.__yg_input.text().strip(),
            'YS_Rig': self.__ys_input.text().strip(),
            'XL_Rig': self.__xl_input.text().strip(),
        }
        # 检测maping资产
        ok, result = mb_sg_fun.check_maping(mapping)
        if not ok:
            # self.__logger.error(result)
            msgview(result, 0, 0)
            return

        if mode == 'current':
            characters = get_all_characters()
            if not characters:
                msgview(u"当前文件没有角色，请检查！", 0, 0)
                return
            current_file_name = mb_get_current_file()
            if not current_file_name:
                msgview(u"当前文件名为空,请打开或保存文件！", 0, 0)
                return
            out_dir = '{}/output'.format(self.__local_dir)
            if not os.path.exists(out_dir):
                os.makedirs(out_dir)
            ok, result = mb_process_fun.process_current_mobu_file(current_file_name, mapping, out_dir, bake=bake,
                                                                  log_handle=self.__logger)
            if not ok:
                msgview(result, 0, 0)
                return
            else:
                msgview(u"mobu文件转maya文件成功,请检查ma文件:\n{}".format(result), 2)
        elif mode == 'batch':
            batch_path = self.__batch_file_input.text().strip()
            if not batch_path:
                msgview(u"批量文件路径不能为空，请输入！", 0, 0)
                return
            if not os.path.exists(batch_path):
                msgview(u"批量文件路径不存在，请检查！", 0, 0)
                return
            out_dir = '{}/output'.format(self.__local_dir)
            if not os.path.exists(out_dir):
                os.makedirs(out_dir)

            ok, result = mb_process_fun.batch_process_mobu_files(batch_path, mapping, out_dir, bake=bake,
                                                                 log_handle=self.__logger)

            if not ok:
                msgview(result, 0, 0)
                return
            success_files = result.get('success_files', [])
            failed_files = result.get('failed_files', [])
            if not success_files:
                msgview(u"批量转换失败，请检查日志！", 0, 0)
                return
            if failed_files:
                msg = u"批量转换完成！\n成功转换文件数:{}\n失败文件数:{}\n请检查日志了解详情！".format(len(success_files),
                                                                                                     len(failed_files))
                msgview(msg, 1, 0)
            else:
                msg = u"批量转换完成！\n成功转换文件数:{}\n所有文件转换成功！".format(len(success_files))
                msgview(msg, 2, 0)


def set_localtemppath(sub_dir='Info_Temp/'):
    _root = ''
    if os.path.exists('D:/'):
        _root = 'D:/'
    elif os.path.exists('E:/'):
        _root = 'E:/'
    elif os.path.exists('F:/'):
        _root = 'F:/'
    elif os.path.exists('C:/'):
        _root = 'C:/'
    if not _root:
        return False
    _tempPath = _root + sub_dir
    if not os.path.exists(_tempPath):
        try:
            os.makedirs(_tempPath)
        except:
            return False
    return _tempPath


def json_read(path, rtype="r", hook=None):
    if not os.path.exists(path):
        return None
    with open(path, rtype) as f:
        _data = json.load(f, object_pairs_hook=hook)
        f.close()
    return _data


def json_write(info, path, wtype="w"):
    _path = os.path.dirname(path)
    if not os.path.exists(_path):
        os.makedirs(_path)
    with open(path, wtype) as f:
        json.dump(info, f, indent=4, separators=(',', ':'))
        f.close()
    return True


if __name__ == '__main__':
    app = QApplication([])
    window = CoverMBToMayaUI()
    window.show()
    app.exec_()
