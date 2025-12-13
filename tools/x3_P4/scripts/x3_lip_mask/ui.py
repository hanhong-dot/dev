# coding:utf-8
try:
    from PySide.QtGui import *
    from PySide.QtCore import *
except ImportError:
    from PySide2.QtGui import *
    from PySide2.QtCore import *
    from PySide2.QtWidgets import *
from functools import partial
import os
import sys


class PathArray(QListWidget):

    def __init__(self, *extensions):
        QListWidget.__init__(self)
        self.extensions = extensions
        self.setAcceptDrops(True)
        self.paths = []
        self.menu = QMenu(self)
        action = self.menu.addAction("clear")
        action.triggered.connect(self.clear)

    def contextMenuEvent(self, event):
        self.menu.exec_(event.globalPos())

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        pass

    def dropEvent(self, event):
        try:
            self.update_paths([url.path().replace("\\", "/")[1:] for url in event.mimeData().urls()])
        except:
            self.update_paths([url.url().replace("\\", "/")[8:] for url in event.mimeData().urls()])

    def clear(self):
        self.paths = []
        QListWidget.clear(self)

    def update_paths(self, value):
        for path in value:
            is_file = self.extensions and (os.path.splitext(path)[-1] in self.extensions)
            is_dir = not self.extensions and (not os.path.splitext(path)[-1])
            if path not in self.paths and (is_file or is_dir):
                self.paths.append(path)
                self.addItem(path)


def get_host_app():
    try:
        main_window = QApplication.activeWindow()
        while True:
            last_win = main_window.parent()
            if last_win:
                main_window = last_win
            else:
                break
        return main_window
    except:
        pass


def q_prefix(label, width):
    prefix = QLabel(label)
    prefix.setFixedWidth(width)
    prefix.setAlignment(Qt.AlignRight)
    return prefix


def q_add(lay, *args):
    for arg in args:
        if isinstance(arg, QWidget):
            lay.addWidget(arg)
        else:
            lay.addLayout(arg)
    return lay


def q_button(label, action):
    but = QPushButton(label)
    but.clicked.connect(action)
    return but


class Path(QLineEdit):

    def __init__(self, get_path):
        QLineEdit.__init__(self)
        self._get_path = get_path

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            return event.accept()
        event.ignore()

    def dragMoveEvent(self, event):
        pass

    def dropEvent(self, event):
        path = event.mimeData().urls()[0].path()[1:]
        self.setText(path)

    def mouseDoubleClickEvent(self, event):
        QLineEdit.mouseDoubleClickEvent(self, event)
        path = self._get_path()
        if not path:
            return
        self.setText(path)

    @staticmethod
    def get_open_path(default_path, ext):
        path, _ = QFileDialog.getOpenFileName(get_host_app(), "Load", default_path(), "(*.{0})".format(ext))
        return path

    @staticmethod
    def get_save_path(default_path, ext):
        path, _ = QFileDialog.getSaveFileName(get_host_app(), "Export", default_path(), "(*.{0})".format(ext))
        return path

    @staticmethod
    def get_existing_dir(default_path):
        path = QFileDialog.getExistingDirectory(get_host_app(), default_path(), default_path())
        return path


class LipMaskTool(QDialog):

    def __init__(self):
        QDialog.__init__(self, get_host_app())
        self.setWindowTitle("HatHairCollisionTool")
        self.setLayout(QVBoxLayout())
        self.anim_paths = PathArray(".fbx", ".FBX", ".Fbx")
        # self.hair_paths = PathArray(".fbx", ".FBX", ".Fbx")
        # self.parent_name = QLineEdit()
        # self.parent_name.setText("head_neck_upper")
        self.bind_pose_path = Path(partial(Path.get_open_path, str, ".fbx"))
        q_add(
            self.layout(),
            QLabel(u"动画路径列表:"),
            self.anim_paths,
            q_add(QHBoxLayout(), q_prefix(u"初始姿势路径：", 90), self.bind_pose_path),
            q_button(u"批处理全部", self.run_all),
        )

    def run_all(self):
        import lip_mask
        reload(lip_mask)
        lip_mask.remove_all_lip_amin(self.anim_paths.paths, self.bind_pose_path.text())


window = None


def show():
    global window
    if window is None:
        window = LipMaskTool()
    window.show()


if __name__ == '__main__':
    app = QApplication([])
    # window = QJointButton(None, None, None, None)
    window = LipMaskTool()
    window.show()
    app.exec_()
