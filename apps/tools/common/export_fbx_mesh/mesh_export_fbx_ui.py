# -*- coding: utf-8 -*-#
# -------------------------------------------------------
# NAME       : mesh_wxport_fbx_ui
# Describe   : 说明描述
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2025/6/11__下午3:01
# -------------------------------------------------------
try:
    from PySide2.QtWidgets import *
    from PySide2.QtGui import *
    from PySide2.QtCore import *
except:
    from PyQt5.QtWidgets import *
    from PyQt5.QtGui import *
    from PyQt5.QtCore import *
from apps.tools.common.export_fbx_mesh import export_fbx_fun


from apps.publish.ui.message.messagebox import msgview
import os


class MeshExportFbxUI(QWidget):
    def __init__(self, parent=None):
        super(MeshExportFbxUI, self).__init__(parent)
        self.__init_ui()
        self.__connect_signals()

    def __init_ui(self):
        """
        Initialize the UI components.
        """
        self.setWindowTitle(u"拆分导出单个Mesh FBX")
        self.setGeometry(100, 100, 400, 150)

        self.layout = QVBoxLayout(self)

        self.__fbx_layout = QHBoxLayout()

        self.__fbxlabel = QLabel(u"fbx文件夹")
        self.__fbxlabel.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.__fbx_dir = QLineEdit()
        self.__fbx_dir.setMinimumWidth(200)
        self.__fbx_dir.setMaximumHeight(30)

        self.__fbx_dir.setPlaceholderText(u"选择/填入需要拆分的FBX文件夹路径")
        self.__fbx_button = QPushButton('...')
        self.__fbx_button.setMaximumHeight(30)
        self.__fbx_button.setMinimumWidth(60)
        self.__fbx_layout.addWidget(self.__fbxlabel)
        self.__fbx_layout.addWidget(self.__fbx_dir)
        self.__fbx_layout.addWidget(self.__fbx_button)

        self.__output_layout = QHBoxLayout()

        self.__output_label = QLabel(u"输出路径")
        self.__output_label.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.__output_dir = QLineEdit()
        self.__output_dir.setMinimumWidth(200)
        self.__output_dir.setMaximumHeight(30)

        self.__output_dir.setPlaceholderText(u"选择/填入输出文件夹路径")
        self.__output_button = QPushButton("...")
        self.__output_button.setMaximumHeight(30)
        self.__output_button.setMinimumWidth(60)
        self.__output_layout.addWidget(self.__output_label)
        self.__output_layout.addWidget(self.__output_dir)
        self.__output_layout.addWidget(self.__output_button)

        self.layout.addLayout(self.__fbx_layout)
        self.layout.addLayout(self.__output_layout)

        self.__button_layout = QHBoxLayout()
        self._confirm_button = QPushButton(u'确认', self)
        self._cancel_button = QPushButton(u'取消', self)
        self.__button_layout.addWidget(self._confirm_button)
        self.__button_layout.addWidget(self._cancel_button)
        self.layout.addLayout(self.__button_layout)

    def __connect_signals(self):
        """
        Connect signals to their respective slots.
        """
        self.__fbx_button.clicked.connect(self.__select_fbx_directory)
        self.__output_button.clicked.connect(self.__select_output_directory)
        self._confirm_button.clicked.connect(self.__confirm_button_clicked)
        self._cancel_button.clicked.connect(self.__close)

    def __select_fbx_directory(self):
        __input_fbx_dir = self.__get_input_fbx_dir()
        if __input_fbx_dir:
            self.__fbx_dir.setText(__input_fbx_dir)

        __directory = QFileDialog.getExistingDirectory(self, u"选择FBX文件夹", __input_fbx_dir,
                                                       QFileDialog.ShowDirsOnly)

        if __directory:
            self.__fbx_dir.setText(__directory)
            self.__write_input_fbx_dir(__directory)

    def __get_path_info(self):
        return export_fbx_fun.get_path_info_from_json()

    def __get_input_fbx_dir(self):

        __path_info = self.__get_path_info()
        if __path_info and 'input_fbx_dir' in __path_info:
            return u'{}'.format(__path_info['input_fbx_dir'])
        else:
            return u'{}'.format(self.__fbx_dir.text().strip())

    def __write_input_fbx_dir(self, _dir):
        __path_info = self.__get_path_info()
        if __path_info is None:
            __path_info = {}
        __path_info['input_fbx_dir'] = _dir
        export_fbx_fun.save_path_info_to_json(__path_info)

    def __write_output_dir(self, _dir):
        __path_info = self.__get_path_info()
        if __path_info is None:
            __path_info = {}
        __path_info['output_dir'] = _dir
        export_fbx_fun.save_path_info_to_json(__path_info)

    def __get_output_dir(self):
        __path_info = self.__get_path_info()
        if __path_info and 'output_dir' in __path_info:
            return u'{}'.format(__path_info['output_dir'])
        else:
            return u'{}'.format(self.__output_dir.text().strip())

    def __select_output_directory(self):

        __out_put_dir = self.__get_output_dir()
        __out_dir = QFileDialog.getExistingDirectory(self, u"选择输出文件夹", __out_put_dir, QFileDialog.ShowDirsOnly)
        if __out_dir:
            self.__output_dir.setText(__out_dir)
            self.__write_output_dir(__out_dir)

    def __confirm_button_clicked(self):
        __input_fbx_dir = u'{}'.format(self.__fbx_dir.text().strip())
        if not __input_fbx_dir:
            msgview(u'未输入fbx文件夹,请输入', 0)
            return
        if not os.path.exists(__input_fbx_dir):
            msgview(u'fbx文件夹不存在,请检查', 0)
            return
        __output_dir = u'{}'.format(self.__output_dir.text().strip())
        if not __output_dir:
            msgview(u'未输入输出文件夹,请输入', 0)
            return
        if not os.path.exists(__output_dir):
            try:
                os.makedirs(__output_dir)
            except:
                msgview(u'输出文件夹创建失败,请检查权限', 0)
                return
        ok, result = export_fbx_fun.export_single_mesh_from_fbx_dir(__input_fbx_dir, __output_dir)
        if not ok:
            msgview(u'导出失败:\n{}'.format(result), 0)
            return
        export_infos, errors = result
        if errors:
            msgview(u'\n导出完成,但有错误,请检查以下信息:\n{}'.format('\n'.join(errors)), 0)

        if not export_infos:
            out_info = u'\n没有导出任何Mesh Fbx,请检查FBX文件夹是否正确'
            msgview(out_info, 0)
            return
        else:
            out_info = u'\n导出完成,导出{}组fbx\n'.format(len(export_infos))
            for info in export_infos:
                fbx_file, output_files = info
                out_info += u'\n======\n'
                out_info += u'FBX文件: {}\n输出文件:\n'.format(fbx_file)
                if not output_files:
                    continue
                for output_file in output_files:
                    out_info += u'{}\n'.format(output_file)
                out_info += u'======\n'

                msgview(u'导出完成,请检查以下信息\n{}'.format(out_info), 2)

    def __close(self):
        self.close()


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    window = MeshExportFbxUI()
    window.show()
    sys.exit(app.exec_())
