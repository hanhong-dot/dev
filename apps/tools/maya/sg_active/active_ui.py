# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       : test
# Describe   : 说明描述
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2022/9/13__16:13
# -------------------------------------------------------
try:
    from PySide2.QtWidgets import *
    from PySide2.QtGui import *
    from PySide2.QtCore import *
except:
    from Qt.QtWidgets import *
    from Qt.QtGui import *
    from Qt.QtCore import *

# import apps.publish.ui.basewindow.basewiondow as basewindow

import method.common.dir as _dir

import apps.tools.maya.sg_active.do_active as _active
reload(_active)

import lib.common.jsonio as _jsonio
import os

# try:
#     reload(_active)
# except:
#     pass

TASKLIST_mdl= ['fight_mdl','drama_mdl','ue_mdl','ue_final','whitebox','out_mdl']
TASKLIST_rig=['drama_rig','rbf','ue_rig','out_rig']


class ActiveUI(QFrame):
    def __init__(self, project='X3', suffix='.ma', dcc='maya', ui=None, parent=None):
        """
        实例初始化
        """
        # 即使直接派生自object，最好也调用一下super().__init__，
        # 不然可能造成多重继承时派生层次中某些类的__init__被跳过。NPC_F01
        super(ActiveUI, self).__init__(parent)
        self.window = QMainWindow()
        self.window.resize(500, 400)
        self.project_name = project
        self.suffix = suffix
        self.dcc = dcc
        self.ui = ui
        self._json_file = '{}/shotgrid_active.json'.format(_dir.set_localtemppath('temp_info'))

        self._build()

    def _build(self):

        self._label_entity = QLabel(self.window)
        self._label_entity.setMinimumHeight(2)
        self._label_entity.setText(u"请填写资产名|镜头号")

        self._textedit_entity = QTextEdit()
        self._textedit_entity.setText(self._select_entity_name)
        self._textedit_entity.setFixedHeight(30)


        self._label_task = QLabel(self.window)
        self._label_task.setMinimumHeight(2)
        self._label_task.setText(u"请选择任务名")

        self.task_box = QComboBox(self.window)
        self.task_box.setMinimumHeight(2)
        self.task_box.addItems(TASKLIST_mdl)
        self.task_box.insertSeparator(6)
        self.task_box.addItems(TASKLIST_rig)
        self.task_box.setCurrentText(self._select_task_name)
        self.task_box.setView(QListView())




        # self._textedit_task = QTextEdit()
        # self._textedit_task.setText(self._select_task_name)
        # self._textedit_task.setFixedHeight(30)

        self._save_checkbox = QCheckBox()

        self._save_checkbox.setFixedSize(75, 30)

        self._save_checkbox.setText(u"重命名保存")
        self._save_checkbox.setChecked(0)

        self._active_button = QPushButton()
        self._active_button.setFixedHeight(30)
        self._active_button.setText(u"Active ShotGrid")
        self._active_button.clicked.connect(self.do_active)

        self.layout_active = QVBoxLayout(self)
        self.layout_active.addWidget(self._label_entity)
        self.layout_active.addWidget(self._textedit_entity)

        self.layout_active.addWidget(self._label_task)
        self.layout_active.addWidget(self.task_box)
        # self.layout_active.addWidget(self._textedit_task)

        self.layout_active.addWidget(self._save_checkbox)
        self.layout_active.addStretch()
        self.layout_active.setSpacing(15)

        self.layout_active.addWidget(self._active_button)
        self.layout_active.addStretch()

    def draw_status_comb(self):
        '''
        for text in text_list:
            p_item = QListWidgetItem(self.list_widget)
            self.list_widget.addItem(p_item)
            p_item.setData(Qt.UserRole, text)
            p_check_box = QCheckBox(self)
            p_check_box.setText(text)
            p_check_box.setChecked(True)
            self.list_widget.setItemWidget(p_item, p_check_box)
            p_check_box.stateChanged.connect(self.state_changed)
        '''
        self.setModel(self.list_widget.model())
        self.setView(self.list_widget)
        self.setLineEdit(self.task_select)
        self.task_select.setText(u'请选择任务')
        self.task_select.setReadOnly(True)





    @property
    def _get_entity_info(self):
        if self._json_file and os.path.exists(self._json_file):
            return _jsonio.read(self._json_file)

    @property
    def _select_entity_name(self):
        u"""

        """
        try:

            if self._get_entity_info['entity_name']:
                return self._get_entity_info['entity_name']
            else:
                return "TDTEST_ROLE"
        except:
            return "TDTEST_ROLE"

    @property
    def _select_task_name(self):
        u"""

        """
        try:
            if self._get_entity_info['task_name']:
                return self._get_entity_info['task_name']
            else:
                return 'drama_mdl'
        except:
            return 'drama_mdl'

    @property
    def _get_entity(self):
        '''返回实体名
        '''
        return self._textedit_entity.toPlainText()

    @property
    def _get_task(self):
        return self.task_box.currentText()

    @property
    def _get_save(self):
        return self._save_checkbox.isChecked()

    def _write_info(self):
        u"""
        写入输入的实体任务信息
        """
        _dict = {}
        _dict['entity_name'] = self._get_entity
        _dict['task_name'] = self._get_task
        _jsonio.write(_dict, self._json_file)

    def do_active(self):
        u"""
        執行
        @return:
        """
        self._write_info()
        _active_handle = _active.DoActive(self.project_name, self._get_entity, self._get_task, self.dcc, self.suffix,
                                          self._get_save)
        _result = _active_handle.active_shotgrid()

        if _result == True:
            self._delect_ui()

    def _delect_ui(self):
        u"""
        删除maya UI
        """
        self.ui.close()
        self.ui.deleteLater()

if __name__ == '__main__':
    try:
        import sys
        app = QApplication(sys.argv)
    except:
        app = QApplication.instance()

    window = ActiveUI()
    window.show()

    app.exec_()
