# coding:utf-8
try:
    from PySide.QtGui import *
    from PySide.QtCore import *
    from PySide import QtUiTools
except:
    from PySide2.QtCore import *
    from PySide2.QtWidgets import *
    from PySide2.QtGui import *
    from PySide2 import QtUiTools
import os
import re
from functools import partial
import QFn


def callback(src, dst, match):
    path = match.group()[1:-1]
    dir_path, basename = os.path.split(path)
    _, ext = os.path.splitext(basename)
    if ext not in [".ma", ".mb"]:
        return match.group()
    if path != src:
        return match.group()
    new_path = dst
    return '"%s"' % new_path


def replace_paths(paths=("D:/ani", ), src="D:/old_rig.ma", dst="D:/new_rig.ma"):
    u"""
    :param paths: 动画路径
    :param src: 旧绑定
    :param dst: 新绑定
    :return:
    """
    paths = [str(path) for path in paths]
    src = str(src)
    dst = str(dst)
    print paths
    for path in paths:
        print path
        for name in os.listdir(path):
            ma_path = os.path.join(path, name).replace("\\", "/")
            new_ma_path = os.path.join(path, "new", name).replace("\\", "/")
            _dir = os.path.dirname(new_ma_path)
            if not os.path.isdir(_dir):
                os.makedirs(_dir)
            _, ext = os.path.splitext(name)
            if ext not in [".ma"]:
                continue
            with open(ma_path, "r") as read:
                text = read.read().replace(src, dst)  # re.sub(ur"\"[A-Z]:[.\\/\w]+\"", partial(callback, src, dst), read.read())
            with open(new_ma_path, "w") as write:
                write.write(text)


window = None


def output_map(win):
    for cls in [QPushButton, QLabel]:
        for obj in win.findChildren(cls):
            print 'u"{0}": u"",'.format(cls.text(obj))


def replace_text(win, text_map):
    for cls in [QPushButton, QLabel]:
        for obj in win.findChildren(cls):
            text = cls.text(obj)
            if text not in text_map:
                continue

            cls.setText(obj, text_map[text])


win_text_map = {
    u"apply and close": u"替换引用并关闭",
    u"apply": u"替换引用",
    u"close": u"关闭",
    u"open": u"打开",
    u"Paths : ": u"动画文件夹",
    u"Src : ": u"旧路径",
    u"Dst : ": u"新路径",
}


def show():
    global window
    if window is None:
        window = QFn.Window(replace_paths)
    replace_text(window.window, win_text_map)
    window.show()


if __name__ == '__main__':
    replace_paths("D:/work/ani_convert/anis/YS", "T:/X3_RawData/Role/YS/Body/Rig/YS_body_Rig.ma",
                  "T:/X3_RawData/Role/YS/YS001S/Rig/YS001S_HD_Rig.ma")
