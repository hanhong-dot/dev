# coding:utf-8


import pymel.core as pm

try:
    from PySide.QtGui import *
    from PySide.QtCore import *
except ImportError:
    from PySide2.QtGui import *
    from PySide2.QtCore import *
    from PySide2.QtWidgets import *

import os
import faceMorphExport
import faceRigExport
import lipsyncExport
reload(faceRigExport)


class Path(QLineEdit):
    def __init__(self, label, ext):
        QLineEdit.__init__(self)
        self.label = label
        self.ext = ext

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            return event.accept()
        event.ignore()

    def dragMoveEvent(self, event):
        pass

    def dropEvent(self, event):
        path = event.mimeData().urls()[0].path()[1:]
        _, ext = os.path.splitext(path)
        if ext != self.ext:
            return
        self.setText(path)

    def mouseDoubleClickEvent(self, event):
        QLineEdit.mouseDoubleClickEvent(self, event)
        url = QFileDialog.getSaveFileName(parent=self, filter="{self.label}(*{self.ext})".format(self=self))[0]
        self.setText(url)

    def resizeEvent(self, event):
        QLineEdit.resizeEvent(self, event)
        self.setTextMargins(0, 0, 0, 0)


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


class PrefixWeight(QHBoxLayout):

    def __init__(self, label, weight):
        QHBoxLayout.__init__(self)
        prefix = QLabel(label)
        prefix.setFixedWidth(70)
        prefix.setAlignment(Qt.AlignRight)
        self.addWidget(prefix)
        if isinstance(weight, QWidget):
            self.addWidget(weight)
        else:
            self.addLayout(weight)


class MayaObeLayout(QHBoxLayout):

    def __init__(self, label):
        QHBoxLayout.__init__(self)
        prefix = QLabel(label)
        prefix.setFixedWidth(70)
        prefix.setAlignment(Qt.AlignRight)
        self.addWidget(prefix)
        self.line = QLineEdit()
        self.line.setReadOnly(True)
        self.addWidget(self.line)
        self.button = QPushButton("<<")
        self.addWidget(self.button)
        self.button.setFixedSize(40, 18)
        self.obj = None
        self.button.clicked.connect(self.load_selected)
        self.setContentsMargins(0, 0, 0, 0)
        self.line.setContentsMargins(0, 0, 0, 0)

    def set_obj(self, obj):
        if obj is None:
            return
        self.obj = obj
        self.line.setText(obj.name())

    def load_selected(self):
        selected = pm.selected(o=1)
        if len(selected) == 1:
            self.set_obj(selected[0])

    def clear(self):
        self.obj = None
        self.line.clear()


class JointsLayout(MayaObeLayout):

    def set_obj(self, obj):
        if obj is None:
            return
        self.obj = obj
        self.line.setText(",".join([joint.name() for joint in obj]))

    def load_selected(self):
        selected = pm.selected(o=1, type="joint")
        self.set_obj(selected)


class BlendShapeLayout(MayaObeLayout):

    def load_selected(self):
        selected = pm.selected(o=1, type="blendShape")
        if len(selected) != 1:
            return

        self.set_obj(selected[0])


class FaceMorphPublish(QDialog):

    def __init__(self):
        QDialog.__init__(self)
        self.setMinimumWidth(360)
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.face_joints = JointsLayout(u"脸部骨骼：")
        self.bs_node = BlendShapeLayout(u"融合变形：")
        self.path = Path(u"JSON", ".json")
        layout.addLayout(self.face_joints)
        layout.addLayout(self.bs_node)
        layout.addLayout(PrefixWeight(u"导出路径：", self.path))
        button = QPushButton(u"导出捏脸数据")
        layout.addWidget(button)
        button.clicked.connect(self.apply)

    def apply(self):
        path = self.path.text()
        joints = [joint for joint in self.face_joints.line.text().split(",") if joint]
        bs_name = self.bs_node.line.text()
        faceMorphExport.export_face_morph_export(joints, bs_name, path)
        QMessageBox.about(self, u"提示！", u"导出完毕！")


class LipSync(QDialog):

    def __init__(self):
        QDialog.__init__(self)
        self.setMinimumWidth(360)
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.face_joints = JointsLayout(u"脸部骨骼：")
        self.tongue_joints = JointsLayout(u"舌头骨骼：")
        self.path = Path(u"JSON", ".json")
        layout.addLayout(self.face_joints)
        layout.addLayout(self.tongue_joints)
        self.typ = QComboBox()
        self.typ.addItems([u"AU", u"FACS"])
        layout.addLayout(PrefixWeight(u"类型：", self.typ))
        layout.addLayout(PrefixWeight(u"导出路径：", self.path))

        button = QPushButton(u"导出口型数据")
        layout.addWidget(button)
        button.clicked.connect(self.apply)

    def apply(self):
        path = self.path.text() # json 路径
        joints = [joint for joint in self.face_joints.line.text().split(",") if joint]  # 骨骼名称列表字符串
        tonguejoints = [joint for joint in self.tongue_joints.line.text().split(",") if joint] # 舌头名称列表
        typ = self.typ.currentIndex()
        lipsyncExport.lip_export(path, joints, tonguejoints, typ)
        QMessageBox.about(self, u"提示！", u"导出完毕！")


class FaceRigPublish(QDialog):

    def __init__(self):
        QDialog.__init__(self)
        self.setMinimumWidth(360)
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.face_joints = JointsLayout(u"脸部骨骼：")
        self.bs_node = BlendShapeLayout(u"融合变形：")
        self.path = Path(u"JSON", ".json")
        self.typ = QComboBox()
        self.typ.addItems([u"NPC", u"主角"])
        layout.addLayout(self.face_joints)
        layout.addLayout(self.bs_node)
        layout.addLayout(PrefixWeight(u"类型：", self.typ))
        layout.addLayout(PrefixWeight(u"导出路径：", self.path))

        button = QPushButton(u"导出面部绑定")
        layout.addWidget(button)
        button.clicked.connect(self.apply)

    def apply(self):
        path = self.path.text()
        joints = [joint for joint in self.face_joints.line.text().split(",") if joint]
        typ = self.typ.currentIndex()
        bs_node_name = self.bs_node.line.text()
        faceRigExport.face_rig_export(path, typ, joints, bs_node_name)
        QMessageBox.about(self, u"提示！", u"导出完毕！")


class ProceduralPublish(QDialog):

    def __init__(self):
        QDialog.__init__(self)
        self.setMinimumWidth(360)
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.face_joints = JointsLayout(u"脸部骨骼：")
        layout.addLayout(self.face_joints)

        self.pupil = MayaObeLayout(u"瞳孔：")
        self.pupil.line.setText("Pupil_L")
        layout.addLayout(self.pupil)

        self.bs = BlendShapeLayout(u"融合变形：")
        layout.addLayout(self.bs)
        # self.bs.line.setText("blendShape8")
        self.Eye_L = MayaObeLayout(u"Eye_L：")
        layout.addLayout(self.Eye_L)
        self.Eye_R = MayaObeLayout(u"Eye_R：")
        layout.addLayout(self.Eye_R)
        self.Eye_L.line.setText("Eye_L")
        self.Eye_R.line.setText("Eye_R")

        self.path = Path(u"JSON", ".json")
        layout.addLayout(PrefixWeight(u"导出路径：", self.path))

        # path, faceShortJoints, pupilShortJoint, bsNode, Eye_L, Eye_R

        button = QPushButton(u"导出面部绑定")
        layout.addWidget(button)
        button.clicked.connect(self.apply)

    def apply(self):
        path = self.path.text()
        faceShortJoints = [joint for joint in self.face_joints.line.text().split(",") if joint]
        pupilShortJoint = self.pupil.line.text()
        bsNode = "blendShape8"
        Eye_L = self.Eye_L.line.text()
        Eye_R = self.Eye_R.line.text()
        import ProceduralFacialAnimationExport
        reload(ProceduralFacialAnimationExport)
        _DrivenBsNode = self.bs.line.text()
        ProceduralFacialAnimationExport.ProceduralFacialAnimationExport(
            path, faceShortJoints, pupilShortJoint, bsNode, Eye_L, Eye_R, _DrivenBsNode)
        QMessageBox.about(self, u"提示！", u"导出完毕！")


class RigPublish(QDialog):

    def __init__(self):
        QDialog.__init__(self, get_host_app())
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.setWindowTitle(u"绑定导出")
        self.tab = QTabWidget()
        self.face_morph = FaceMorphPublish()
        self.tab.addTab(self.face_morph, "FaceMorph")
        self.face_rig = FaceRigPublish()
        self.tab.addTab(self.face_rig, "FaceRIg")
        self.lip_sync = LipSync()
        self.tab.addTab(self.lip_sync, "LipSync")

        self.procedural = ProceduralPublish()
        self.tab.addTab(self.procedural, "Procedural")

        layout.addWidget(self.tab)

    def showNormal(self):
        QDialog.showNormal(self)
        path, _ = os.path.splitext(pm.sceneName())
        self.face_morph.path.setText(path+"_"+"face_morph.json")
        self.face_rig.path.setText(path+"_"+"face_rig.json")
        self.lip_sync.path.setText(path+"_"+"lip_sync.json")
        self.procedural.path.setText(path+"_"+"procedural.json")

window = None


def show():
    global window
    if window is None:
        window = RigPublish()
    window.showNormal()
