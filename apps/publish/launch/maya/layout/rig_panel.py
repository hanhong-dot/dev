# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       : rig_panel
# Describe   : 说明描述
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2022/10/25__15:35
# -------------------------------------------------------
# -*- coding: utf-8 -*-#
# Python       : python 2.7.16
# -------------------------------------------------------------------------------
# NAME         : Lft_panal
# Describe     : 说明描述
# Version      : v0.01
# Author       : hanhong@papegames.net
# Email        :
# DateTime     : 2022/11/22__17:42
# -------------------------------------------------------------------------------
# -------------------------------------------------------------------------------
# example:
#
# -------------------------------------------------------------------------------

import os

import  apps.publish.process.maya.process_export_fbx as process_export_fbx
import apps.publish.ui.message.messagebox as _messagebox

try:
    from PySide2.QtWidgets import *
    from PySide2.QtGui import *
    from PySide2.QtCore import *
except:
    from Qt.QtWidgets import *
    from Qt.QtGui import *
    from Qt.QtCore import *
import lib.common.md5 as _md5
class RigWidget(QFrame):
    def __init__(self,task_data, *args, **kwargs):
        super(RigWidget, self).__init__()
        self.setAcceptDrops(True)
        self.task_data = task_data
        self._project = self.task_data.project_name
        self._task_name = self.task_data.task_name
        self._entity_name = self.task_data.entity_name

        self._work_data_dir = self.task_data.work_data_dir
        self._publish_data_dir = self.task_data.publish_data_dir
        self._work_fbx_dir = '{}/fbx'.format(self._work_data_dir)
        self._publish_fbx_dir = '{}/fbx'.format(self._publish_data_dir)
        self._mb_fbx_file='{}_MB.fbx'.format(self._entity_name)
        self._work_fbx_file = '{}/{}'.format(self._work_fbx_dir, self._mb_fbx_file)
        self._json_file='{}.{}.MB.json'.format(self._entity_name, self._task_name)


        self._suffixlist = ['.fbx']
        self._data = []
        self._setup()

    def _setup(self):
        self._label = QLabel()
        self._label.setText(u"请拖入mb fbx文件(只支持拖入一个文件)")
        self._label.setAlignment(Qt.AlignCenter)
        self._label.setFixedHeight(25)
        self._label.setStyleSheet("background-color:#345612;font: bold 12px")
        # self._label2 = QLabel()
        # self._label2.setText(u"文件名")
        # self._label2.setFixedSize(50, 22)
        self._label3 = QLabel()
        self._label3.setText(u"")
        self._label3.setAlignment(Qt.AlignTop)
        self._label3.setFixedSize(0, 10)
        #self._label3.setFixedHeight(60)
        self._label4 = QLabel()
        self._label4.setText(u"请拖入rig fbx(to mb)文件.")
        self._label4.setFixedHeight(25)

        self._lineedit = QLineEdit()
        self._lineedit.setFixedHeight(212)

        # self._pushbutton = QPushButton()
        # self._pushbutton.setFixedSize(75, 22)
        # self._pushbutton.setText(u"创建新版本")

        self._pushbutton2 = QPushButton()
        self._pushbutton2.setFixedSize(75, 25)
        self._pushbutton2.setText(u"清除")
        self._pushbutton2.clicked.connect(self._delete_all)
        # 旧文本框
        # self._textedit = QTextEdit()
        # self._textedit.setFixedHeight(180)
        self._listwidget_file = QListWidget()
        self._listwidget_file.setFixedHeight(180)
        self._listwidget_file.setSelectionMode(QAbstractItemView.ContiguousSelection)

        # self._seclayout = QHBoxLayout()
        # self._seclayout.setSpacing(2)
        # self._seclayout.setMargin(0)
        # # self._seclayout.addWidget(self._label2)
        # # self._seclayout.addWidget(self._lineedit)
        # # self._seclayout.addWidget(self._pushbutton)

        self._seclayout2 = QHBoxLayout()
        self._seclayout2.setSpacing(2)
        self._seclayout2.setMargin(0)
        self._seclayout2.addWidget(self._label3)
        # self._seclayout2.addWidget(self._textedit)
        self._seclayout2.addWidget(self._listwidget_file)

        self._seclayout3 = QHBoxLayout()
        self._seclayout3.setSpacing(2)
        self._seclayout3.setMargin(0)
        self._seclayout3.addWidget(self._label4)
        self._seclayout3.addWidget(self._pushbutton2)

        self._layout = QVBoxLayout(self)
        self._layout.setSpacing(2)
        self._layout.setMargin(0)
        self._layout.addWidget(self._label)
        # self._layout.addLayout(self._seclayout)
        self._layout.addLayout(self._seclayout2)
        self._layout.addLayout(self._seclayout3)

    def _additem(self, items):
        '''添加列表项，按需求限定添加一个
        '''
        for _item in items:
            if _item not in self._data:
                self._item = QListWidgetItem(self._listwidget_file)
                _base = os.path.basename(_item)
                self._item.setText(_base)
                self._data.append(_item)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()

    def dropEvent(self, event):
        '''获取文件
        '''
        if event.mimeData().hasUrls():
            _urls = event.mimeData().urls()
            _realurls = self._check_urls([i.toLocalFile() for i in _urls])
            if _realurls :
                self._additem(_realurls)

    def _check_urls(self, urls):
        return [_url for _url in urls if os.path.splitext(_url)[-1] in self._suffixlist]

    def data(self):
        '''
        例子：返回这种类型的字典
        :return:
        '''
        _dict = {}

        _work_file=self._copy_work()
        print(_work_file)

        # 打上传包



        if _work_file:
            _dict = process_export_fbx.Porcess_Export(self.task_data).package_work_publish(_work_file,_jsonfile=self._json_file,_key='mbfbx')
        return _dict

    def _copy_work(self):
        u"""
        将拖入的文件复制到work路径(并自动改名{资产名}_MB.fbx)
        :return:
        """
        if self._data and len(self._data)==1:
            self._copy_file(self._data[0], self._work_fbx_file)
            if self._work_fbx_file and os.path.exists(self._work_fbx_file):
                return [self._work_fbx_file]
        elif self._data and len(self._data)>1:
            _messagebox.msgview(u"拖入的fbx文件超过了一个,请检查", 0)
            raise Exception(u"拖入的fbx文件超过了一个,请检查".encode('gbk'))



    def _copy_file(self, _sourcefile, _targefile):
        u"""
        复制文件
        :param _sourcefile:需要复制的文件
        :param _targefile:复制后的目标文件
        """
        import shutil
        import os
        _targedir = os.path.split(_targefile)[0]
        # 创建路径
        if not os.path.exists(_targedir):
            os.makedirs(_targedir)
        #刪除
        if _targefile and os.path.exists(_targefile):
            try:
                os.remove(_targefile)
            except:
                pass

        #判断是否要复制
        _count=True
        if _targefile and os.path.exists(_targefile):
            _judge=_md5.Md5().contrast_md5(_sourcefile,_targefile)
            if _judge==True:
                _count=False




        # 复制
        if _count==True:
            try:
                shutil.copyfile(_sourcefile, _targefile)
            except:
                _messagebox.msgview(u"{}未成功复制到{},请检查或联系TD".format(_sourcefile,_targefile), 0)
                raise Exception((u"{}未成功复制到{},请检查或联系TD".format(_sourcefile,_targefile)).encode('gbk'))

    def _delete_all(self):
        '''
        清除文件列表
        :return:
        '''

        self._listwidget_file.clear()

    def get_all_files(self):
        '''
        返回文件列表.
        :return:
        '''
        return self._data


def return_widget(task_data,*args, **kwargs):
    bswin = RigWidget(task_data, *args, **kwargs)
    return bswin


if __name__ == '__main__':
    import method.shotgun.get_task as get_task
    import sys
    _taskinfo = get_task.TaskInfo('PL007WST01.out_rig.v001.ma', 'X3', 'maya', 'version')
    try:
        app = QApplication(sys.argv)
    except:
        app=QApplication.instance()
    bswin = RigWidget(_taskinfo)
    bswin.show()
    sys.exit(app.exec_())
