# coding:utf-8
try:
    from PySide.QtGui import *
    from PySide.QtCore import *
except ImportError:
    from PySide2.QtGui import *
    from PySide2.QtCore import *
    from PySide2.QtWidgets import *
import pymel.core as pm
from functools import partial


def get_name_space():
    selected = pm.selected()
    if not selected:
        return ""
    if ":" in selected[0].name():
        return selected[0].name().split(":")[0]+":"
    else:
        return ""


def find_parts(ns, names):
    for name in names:
        for rl in ["_R", "_L"]:
            for part in ["", "Part1", "Part2"]:
                full_name = ns + name + part + rl
                nodes = pm.ls(full_name)
                if len(nodes) == 1:
                    yield nodes[0]


def set_twist(nodes, value, repair_data):
    for node in nodes:
        if not node.hasAttr("twistAmount"):
            continue
        attr = node.twistAmount
        old_value = attr.get()
        inputs = attr.inputs(p=1)
        if inputs:
            old_value = inputs[0]
            pm.disconnectAttr(old_value, attr)
        attr.set(value)
        repair_data.append([attr, old_value])


REPAIR_DATA = []


def remove_twist():
    global REPAIR_DATA
    REPAIR_DATA = []
    ns = get_name_space()
    set_twist(find_parts(ns, ['Shoulder',  'Hip']), 1, REPAIR_DATA)
    set_twist(find_parts(ns, ['Elbow',  'Knee']), 0, REPAIR_DATA)


def repair_twist():
    global REPAIR_DATA
    for attr, value in REPAIR_DATA:
        if isinstance(value, float):
            attr.set(value)
        else:
            value.connect(attr)


def seed(mel_cmd):
    remove_twist()
    pm.mel.eval(mel_cmd)
    repair_twist()


def bake_all(st, et):
    pm.select(pm.selected(o=1), hi=1)
    joints = pm.selected(type="joint")
    pm.bakeResults(joints, t=[st, et], sampleBy=1, simulation=True, oversamplingRate=True)


def doit():
    pm.select("temp_rig:joint1")
    bake_all()


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


class SeedX3CharToMB(QDialog):

    def __init__(self):
        QDialog.__init__(self, get_host_app())
        self.setWindowTitle("SeedX3CharToMB")
        self.setLayout(QVBoxLayout())
        self.st = QSpinBox()
        self.et = QSpinBox()
        self.st.setRange(-99999999, 99999999)
        self.et.setRange(-99999999, 99999999)

        q_add(
            self.layout(),
            # q_button(u"移除四肢part twist", remove_twist),
            # q_button(u"复原四肢part twist", repair_twist),
            q_add(
                QHBoxLayout(),
                QLabel(u"开始"),
                self.st,
                QLabel(u"结束"),
                self.et,
                q_button(u"<<<", self.load_time_range)
            ),
            q_button(u"Send as New Scene", partial(self.seed, "SendAsNewSceneMotionBuilder")),
            q_button(u"Update Current Scene", partial(self.seed, "UpdateCurrentSceneMotionBuilder")),
            q_button(u"Add to Current Scene", partial(self.seed, "AddToCurrentSceneMotionBuilder")),
            q_button(u"Select Previously Sent Objects", partial(self.seed, "SelectPreviousObjectsMotionBuilder")),

        )

    def load_time_range(self):
        st = pm.playbackOptions(q=1, min=1)
        et = pm.playbackOptions(q=1, max=1)
        self.st.setValue(st)
        self.et.setValue(et)

    def seed(self, mel_cmd):
        st = self.st.value()
        et = self.et.value()
        remove_twist()
        bake_all(st, et)
        pm.mel.eval(mel_cmd)


window = None


def show():
    global window
    if window is None:
        window = SeedX3CharToMB()
    window.load_time_range()
    window.show()



