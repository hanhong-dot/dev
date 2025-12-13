# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       : collect_ui
# Describe   : 说明描述
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2024/2/18__11:12
# -------------------------------------------------------
import os

try:
    from PySide2.QtWidgets import *
    from PySide2.QtGui import *
    from PySide2.QtCore import *
except:
    from PyQt5.QtWidgets import *
    from PyQt5.QtGui import *
    from PyQt5.QtCore import *

import apps.tools.collect.collect_fun as collect_fun

import method.common.dir as _dir

import lib.common.jsonio as _jsonio

from apps.publish.ui.message import messagebox

PRP_ASSET_TYPES = ['item', 'plant', 'environment', 'envmodel', 'scn']
ASSET_TYPES = [u'body', u'role', u'weapon', u'rolaccesory', u'npc', u'hair', u'fx', u'enemy', u'cartoon_body',
               u'cartoon_role', u'cartoon_rolaccesory', u'cartoon_fx', u'item', u'plant', u'environment', u'envmodel',
               u'scn']


class CollectUI(QWidget):
    def __init__(self, parent=None):
        super(CollectUI, self).__init__(parent)
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle(u'收集工具')
        self.resize(500, 400)
        self._json_file = '{}/shotgrid_collect.json'.format(_dir.set_localtemppath('temp_info'))

        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        self.build_ui()

        self.collect_btn = QPushButton(u'收集')
        self.main_layout.addWidget(self.collect_btn)

        self.collect_btn.clicked.connect(self.collect_work)
        self.file_type.currentIndexChanged.connect(self.update_check_local_map_state)

    def update_check_local_map_state(self):
        __file_type = self.file_type.currentText()
        if __file_type in [u'ma(publish)', u'ma(work)', u'all']:
            self.check_local_map.setEnabled(True)
        else:
            self.check_local_map.setChecked(False)
            self.check_local_map.setEnabled(False)


    def build_ui(self):
        self.property_layout = QFormLayout()
        self.asset_type = QComboBox()
        self.asset_type.addItems(ASSET_TYPES)
        self.property_layout.addRow(u'资产类型:', self.asset_type)

        self.asset_name = QTextEdit()
        # asset_type = self.asset_type.currentText()
        # self.assets=self.find_assets(asset_type)
        # if self.assets:
        #     self.asset_name.addItems([asset['code'] for asset in self.assets if asset['code']])
        self.property_layout.addRow(u'资产名称:', self.asset_name)

        self.main_layout.addLayout(self.property_layout)

        self.task_name = QComboBox()
        self.task_name.addItems([u'whitebox', u'fight_mdl', u'drama_mdl', u'drama_rig', u'rbf'])
        self.property_layout.addRow(u'任务名称:', self.task_name)

        self.file_type = QComboBox()
        self.file_type.addItems([u'ma(publish)', u'fbx', u'ma(work)', u'all'])
        self.property_layout.addRow(u'文件类型:', self.file_type)

        self.check_local_map = QCheckBox(u'贴图收集到本机(仅ma格式文件有效)')
        self.check_local_map.setStyleSheet("""
            QCheckBox::indicator:checked {
                border: 1px solid green;
                image: url(Z:/dev/ico/small/check.png);
                color:green;
                
                
            }
            QCheckBox::indicator:unchecked {
                border: 1px solid none;
            }
        """)
        __file_type = self.file_type.currentText()
        if __file_type not in [u'ma(publish)', u'ma(work)', u'all']:
            self.check_local_map.setChecked(False)
            self.check_local_map.setEnabled(False)
        else:
            self.check_local_map.setEnabled(True)

        self.property_layout.addRow(u'贴图收集:', self.check_local_map)
        self.read_property()

    def find_assets(self, asset_type):
        pass
        # return collect_fun.get_assets(asset_type=asset_type)

    def save_property(self):
        _dict = {}
        _dict['asset_type'] = self.asset_type.currentText()
        _dict['asset_name'] = self.asset_name.toPlainText()
        _dict['task_name'] = self.task_name.currentText()
        _dict['file_type'] = self.file_type.currentText()
        _dict['check_local_map'] = self.check_local_map.isChecked()
        _jsonio.write(_dict, self._json_file)
        return _dict



    def read_property(self):
        if self._json_file and os.path.exists(self._json_file):
            property = _jsonio.read(self._json_file)
            self.asset_type.setCurrentText(property['asset_type'] if 'asset_type' in property else u'item')
            self.asset_name.setText(property['asset_name'] if 'asset_name' in property else '')
            self.task_name.setCurrentText(property['task_name'] if 'task_name' in property else u'drama_rig')
            self.file_type.setCurrentText(property['file_type'] if 'file_type' in property else u'fbx')
            self.check_local_map.setChecked(property['check_local_map'] if 'check_local_map' in property else False)
        else:
            self.asset_type.setCurrentText(u'item')
            self.asset_name.setText('')
            self.task_name.setCurrentText(u'drama_rig')
            self.file_type.setCurrentText(u'fbx')
            self.check_local_map.setChecked(False)

    def collect_work(self):
        _dict = self.save_property()

        ok, result = collect_fun.copy_publish_files(_dict)
        if ok == False:
            messagebox.QMessageBox.warning(self, u'错误提示', result)
            return
        copy_files = result

        self.__collect_map_files(copy_files)

        if ok == True:
            dirs = self.__get_dir(result)
            if dirs:
                for _dir in dirs:
                    if os.path.exists(_dir):
                        cmd = 'cmd.exe /C start "Folder" "%s"' % _dir
                        os.system(cmd)

            text = u'文件收集完成,共收集到{}个文件:\n'.format(len(result))
            for i in range(len(result)):
                text = text + result[i] + '\n'
            messagebox.QMessageBox.information(self, u'完成提示', text)

        else:
            messagebox.QMessageBox.warning(self, u'错误提示', result)

    def __collect_map_files(self, files):
        if not files:
            return
        ok_list = []
        error_list = []
        for file in files:
            result = self.__batch_collect_map_file(file)
            if result:
                ok_list.append(file)
            else:
                error_list.append(file)
        return ok_list, error_list

    def __batch_collect_map_file(self, path):
        import apps.tools.collect.batch_collect as batch_collect
        reload(batch_collect)

        try:
            batch_collect.run_maya_batch(path)
            return True
        except:
            return False

    def __get_dir(self, files):
        dirs = []
        if not files:
            return dirs
        for file in files:
            file = file.replace('\\', '/')
            _dir = os.path.dirname(file)
            if _dir not in dirs:
                dirs.append(_dir)
        return dirs

    def __set_check_local_map_clicked(self):
        __file_type = self.file_type.currentText()
        if __file_type in [u'ma(publish)', u'ma(work)', u'all']:
            self.check_local_map.setEnabled(True)
        else:
            self.check_local_map.isChecked(False)
            self.check_local_map.setEnabled(False)


if __name__ == '__main__':
    app = QApplication([])
    win = CollectUI()
    win.show()
    app.exec_()
