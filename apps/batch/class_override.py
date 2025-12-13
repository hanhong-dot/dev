# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       : class_override
# Describe   : 说明描述
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2022/12/30__14:13
# -------------------------------------------------------
from PySide2 import QtCore
from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class MyQListWidget(QListWidget):
    dropped = QtCore.Signal(list)

    def __init__(self, parent=None):
        super(MyQListWidget, self).__init__(parent)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls:
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls:
            event.setDropAction(QtCore.Qt.CopyAction)
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasUrls:
            links = []
            for url in event.mimeData().urls():
                file_path = str(url.toLocalFile().encode('utf-8'))
                # file_path = file_path.replace('/', '\\')
                links.append(file_path)
            self.dropped.emit(links)
        else:
            event.ignore()


class MyQTableView(QTableView):
    dropped = QtCore.Signal(list)

    def __init__(self, parent=None):
        super(MyQTableView, self).__init__(parent)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls:
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls:
            event.setDropAction(QtCore.Qt.CopyAction)
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasUrls:
            links = []
            for url in event.mimeData().urls():
                file_path = str(url.toLocalFile().encode('utf-8'))
                # file_path = file_path.replace('/', '\\')
                links.append(file_path)
            self.dropped.emit(links)
        else:
            event.ignore()


class AutoCompleter(QCompleter):
    def __init__(self, parent=None):
        super(AutoCompleter, self).__init__(parent)
        self.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.setCompletionMode(QCompleter.PopupCompletion)
        self.setWrapAround(False)

    def pathFromIndex(self, index):
        path = QCompleter.pathFromIndex(self, index).encode('utf-8')
        text = str(self.widget().text().encode('utf-8'))

        lst = text.split(',')
        if len(lst) > 1:
            path = '%s, %s' % (','.join(lst[:-1]), path)
        return path

    def splitPath(self, path):
        text = str(path.split(',')[-1].encode('utf-8'))
        path = str(text).lstrip(' ')
        return [path]


class MyQLabelWidget(QWidget):
    doubleClicked = Signal(dict)

    def __init__(self, parent=None):
        super(MyQLabelWidget, self).__init__(parent)
        self.data = dict()

        self.textQVBoxLayout = QVBoxLayout()

        self.textContentQLabel = QLabel()
        self.thumbnailQLabel = QLabel()

        self.textContentQLabel.setObjectName("Content")
        self.thumbnailQLabel.setObjectName("thumbnail")

        self.thumbnailQLabel.setFixedSize(80, 80)

        self.textQVBoxLayout.addWidget(self.thumbnailQLabel)
        self.textQVBoxLayout.addWidget(self.textContentQLabel)
        self.textQVBoxLayout.setAlignment(self.thumbnailQLabel, Qt.AlignHCenter)
        self.textQVBoxLayout.setAlignment(self.textContentQLabel, Qt.AlignHCenter)

        self.setLayout(self.textQVBoxLayout)

    def setTextContent(self, text):
        self.textContentQLabel.setText(text)

    def setThumbnail(self, thumbnail_path):
        pix = QPixmap(thumbnail_path)
        self.thumbnailQLabel.setPixmap(pix.scaled(self.thumbnailQLabel.size(), QtCore.Qt.KeepAspectRatio))

    def getTextContent(self):
        return self.textContentQLabel.text()

    def setData(self, data):
        self.data = data

    def mouseDoubleClickEvent(self, *args, **kwargs):
        self.doubleClicked.emit(self.data)


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    dialog = MyQLabelWidget()
    dialog.setThumbnail(r'D:/RY_SSR0007.png')
    dialog.setTextContent('Label')
    dialog.show()
    sys.exit(app.exec_())