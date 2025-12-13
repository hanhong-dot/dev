# coding=utf-8
import os.path

from PySide2.QtWidgets import *
from PySide2.QtCore import *
from .tools import *
from . import reCurveTool


def q_prefix(text, width):
    prefix = QLabel(text)
    prefix.setFixedWidth(width)
    prefix.setAlignment(Qt.AlignRight)
    return prefix


def q_add(layout, *elements):
    for elem in elements:
        if isinstance(elem, QLayout):
            layout.addLayout(elem)
        elif isinstance(elem, QWidget):
            layout.addWidget(elem)
    return layout


def q_button(text, action):
    but = QPushButton(text)
    but.clicked.connect(action)
    return but


qss = """
QWidget{
    font-size: 16px;
    font-family: 楷体;
}
"""


def get_open_path(default_path, ext):
    path, _ = QFileDialog.getOpenFileName(get_app(), "Load", default_path, "{0} (*.{0})".format(ext))
    return path

def get_save_path(default_path, ext):
    path, _ = QFileDialog.getSaveFileName(get_app(), "Save", default_path, "{0} (*.{0})".format(ext))
    return path


class Tool(QDialog):

    def __init__(self, parent):
        QDialog.__init__(self, parent)
        self.setWindowTitle("AIMetaTool")
        self.setStyleSheet(qss)
        self.ctrl_set = QLineEdit(self)
        self.ani_ns = QLineEdit(self)
        self.nn_path = QLineEdit()
        self.typ = QComboBox()
        self.typ.addItems(sorted(action_config.keys()))
        self.ip = QLineEdit()
        urls = [
            '10.10.133.157:8081',
        ]
        comp = QCompleter(urls)
        comp.setCompletionMode(comp.UnfilteredPopupCompletion)
        self.st_frame = QSpinBox(self)
        self.st_frame.setRange(-1e8, 1e8)
        self.ip.setCompleter(comp)
        self.ip.setText(urls[0])

        self.export_st_frame = QSpinBox(self)
        self.export_st_frame.setRange(-1e8, 1e8)
        self.export_et_frame = QSpinBox(self)
        self.export_et_frame.setRange(-1e8, 1e8)

        self.setLayout(q_add(
            QVBoxLayout(),
            # q_add(QHBoxLayout(), q_prefix(u"服务地址:", 90), self.ip),
            # q_add(QHBoxLayout(), q_prefix(u"模型权重:", 90), self.nn_path, q_button(u"<<<", self.load_nn)),
            q_add(QHBoxLayout(), q_prefix(u"控制器集合:", 90), self.ctrl_set, q_button(u"<<<", self.load_ctrl_set)),
            q_add(QHBoxLayout(), q_prefix(u"动画空间名:", 90), self.ani_ns, q_button(u"<<<", self.load_ani_ns)),
            q_add(QHBoxLayout(), q_prefix(u"项目类型:", 90), self.typ),

            q_button(u"批量计算BS曲线", self.solve_anim_all),
            q_button(u"姿势转驱动", self.pose_driver),
            q_add(
                QHBoxLayout(),
                q_button(u"导入控制器动画", self.load_driver_anim),
                q_button(u"批量导入保存", self.load_driver_anim_all),
            ),
            q_add(
                QHBoxLayout(),
                q_button(u"导入口型动画", self.load_ai_speak),
                q_button(u"批量口型转BS曲线", self.convert_ai_speak_to_bs),
            ),
            # q_button(u"导出修复动画数据", self.export_anim),
            # q_button(u"上传训练", self.server_tran),
            # q_button(u"从模型导入动画", self.load_nn_anim),
            q_add(
                QHBoxLayout(),
                q_button(u"转为纯融合变形", self.convert_blend_shape),
                q_button("平滑曲线", reCurveTool.tool.tool_auto_smooth),

            ),
            q_add(
                QHBoxLayout(),
                q_prefix("开始帧:", 60),
                self.st_frame,
                q_button(u"导入实时", self.load_runtime_data),
                q_button(u"帧偏移", self.compute_frame_offset),
            ),
            q_add(
                QHBoxLayout(),
                q_prefix("帧范围:", 60),
                self.export_st_frame,
                self.export_et_frame,
                q_button(u"<<<", self.load_frame_range),
            ),
            q_button(u"导出动画", self.export_anim_data),
            q_button(u"视频转图片", self.mov_to_jpg),
        ))

    def load_frame_range(self):
        from maya import cmds
        st = int(round(cmds.playbackOptions(q=1, min=1)))
        et = int(round(cmds.playbackOptions(q=1, max=1)))
        self.export_st_frame.setValue(st)
        self.export_et_frame.setValue(et)

    def export_anim_data(self):
        from .export_unity_anim import export_unity_anim
        path = get_save_path("", "json")
        st = self.export_st_frame.value()
        et = self.export_et_frame.value()
        export_unity_anim(path, st, et)


    def convert_blend_shape(self):
        action_config[self.typ.currentText()]["convert_bs"]()

    def load_runtime_data(self):
        path = get_open_path("", "json")
        if not path:
            return
        st = self.st_frame.value()
        action_config[self.typ.currentText()]["load_runtime"](path, st)

    def load_ctrl_set(self):
        self.ctrl_set.setText(anim_driver.get_selected_ctrl_set())

    def load_ani_ns(self):
        self.ani_ns.setText(anim_driver.get_name_space())

    @staticmethod
    def load_bs_anim():
        path = get_open_path("", "json")
        if path:
            anim_driver.load_bs_anim(path)

    def solve_anim(self):
        path, _ = QFileDialog.getSaveFileName(get_app(), "Load", "", "{0} (*.{0})".format("json"))
        if not path:
            return
        action_config[self.typ.currentText()]["solve_anim"](path)

    def solve_anim_all(self):
        path = QFileDialog.getExistingDirectory(self)
        if not path:
            return
        solve_fun = action_config[self.typ.currentText()]["solve_anim"]
        solve_all_bs_anim(path, solve_fun)

    def pose_driver(self):
        action_config[self.typ.currentText()]["pose_driver"](self.ani_ns.text(), self.ctrl_set.text())

    def load_driver_anim(self):
        path = get_open_path("", "json")
        if not path:
            return
        action_config[self.typ.currentText()]["load_anim"](path)

    def load_driver_anim_all(self):
        path = QFileDialog.getExistingDirectory(self)
        if not path:
            return
        load_fun = action_config[self.typ.currentText()]["load_anim"]
        load_all_bs_anim(path, load_fun)

    def export_anim(self):
        path, _ = QFileDialog.getSaveFileName(get_app(), "Load", "", "{0} (*.{0})".format("npz"))
        if not path:
            return
        ns = anim_driver.get_name_space()
        action_config[self.typ.currentText()]["export_anim"](ns, self.ctrl_set.text(), path)

    def server_tran(self):
        path = QFileDialog.getExistingDirectory(self)
        if not path:
            return
        try:
            seed_to_server_tran(path, url=self.ip.text())
            QMessageBox.about(self, u"提示", u"训练完成!")
        except Exception:
            QMessageBox.about(self, u"提示", u"运行失败!")
            raise

    def load_nn(self):
        path, _ = QFileDialog.getOpenFileName(get_app(), "Load", "", "{0} (*.{0})".format("npz"))
        if not path:
            return
        self.nn_path.setText(path)

    def load_nn_anim(self):
        nn_path = self.nn_path.text()
        if not os.path.isfile(nn_path):
            return
        path = get_open_path("", "json")
        if not path:
            return
        ns = anim_driver.get_name_space()
        face_anim_retarget.load_anim_data(nn_path, path, ns)

    @staticmethod
    def load_ai_speak():
        path = get_open_path("", "json")
        if not path:
            return
        load_ai_speak_ue_ctrl_anim(path)

    def convert_ai_speak_to_bs(self):
        path = QFileDialog.getExistingDirectory(self)
        if not path:
            return
        solve_fun = action_config[self.typ.currentText()]["solve_anim"]
        batch_convert_speak(path, solve_fun)

    def mov_to_jpg(self):
        path = QFileDialog.getExistingDirectory(self)
        if not path:
            return
        from .convert_video import convert
        convert.convert_all_videos_in_folder(path)

    def compute_frame_offset(self):
        take_path, _ = QFileDialog.getOpenFileName(get_app(), "Load Take", "", "take (take.json)")
        if not take_path:
            return
        anim_path, _ = QFileDialog.getOpenFileName(get_app(), "Load Anim", "", "anim (*.json)")
        if not anim_path:
            return
        from . import frame_offset
        frame_offset = frame_offset.get_frame_offset(take_path, anim_path)
        QMessageBox.about(self, u"提示", u"偏移{frame_offset}帧!".format(frame_offset=frame_offset))
        st = self.st_frame.value() + frame_offset
        action_config[self.typ.currentText()]["load_runtime"](anim_path, st)


window = None


def get_app():
    top = QApplication.activeWindow()
    if top is None:
        return
    while True:
        parent = top.parent()
        if parent is None:
            return top
        top = parent


def show():
    global window
    if window is None:
        window = Tool(parent=get_app())
    window.showNormal()


def doit():
    show()
