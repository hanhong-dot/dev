# coding:utf-8
import os.path
import csv
from maya import cmds
from maya.api.OpenMaya import *
from maya.api.OpenMayaAnim import *
from PySide2.QtWidgets import *


class Shape(object):
    mesh = "mesh"
    nurbsSurface = "nurbsSurface"
    nurbsCurve = "nurbsCurve"


def is_shape(polygon_name, typ="mesh"):
    if not cmds.objExists(polygon_name):
        return False
    if cmds.objectType(polygon_name) != "transform":
        return False
    shapes = cmds.listRelatives(polygon_name, s=1, f=1)
    if not shapes:
        return False
    if cmds.objectType(shapes[0]) != typ:
        return False
    return True


def get_skin_cluster(polygon_name):
    if not is_shape(polygon_name, "mesh"):
        return
    shapes = cmds.listRelatives(polygon_name, s=1, f=1)
    for skin_cluster in cmds.ls(cmds.listHistory(polygon_name), type="skinCluster"):
        for shape in cmds.skinCluster(skin_cluster, q=1, geometry=1):
            for long_shape in cmds.ls(shape, l=1):
                if long_shape in shapes:
                    return skin_cluster


def py_to_m_array(cls, _list):
    result = cls()
    for elem in _list:
        result.append(elem)
    return result


def api_ls(*names):
    selection_list = MSelectionList()
    for name in names:
        selection_list.add(name)
    return selection_list


def swap_skin(polygon_name, src_joint, dst_joint):
    if cmds.referenceQuery(polygon_name, isNodeReferenced=1):
        return
    skin_cluster = get_skin_cluster(polygon_name)
    if not skin_cluster:
        return
    joints = cmds.skinCluster(skin_cluster, q=1, influence=1)
    if src_joint not in joints:
        return
    if dst_joint not in joints:
        cmds.skinCluster(skin_cluster, e=1, lw=True, ai=dst_joint, wt=0)
    joints = cmds.skinCluster(skin_cluster, q=1, influence=1)
    shape, components = api_ls(polygon_name + ".vtx[*]").getComponent(0)
    fn_skin = MFnSkinCluster(api_ls(get_skin_cluster(polygon_name)).getDependNode(0))
    influences = MIntArray([joints.index(src_joint), joints.index(dst_joint)])
    weights = fn_skin.getWeights(shape, components, influences)
    for i in range(0, len(weights), 2):
        weights[i+1] = weights[i] + weights[i+1]
        weights[i] = 0
    fn_skin.setWeights(shape, components, influences, MDoubleArray(weights))


def swap_skin_all(joints):
    for src_joint, dst_joint in joints:
        ls_joints = cmds.ls(src_joint, dst_joint, type="joint")
        if len(ls_joints) != 2:
            continue
        skin_clusters = cmds.listConnections(src_joint, dst_joint, s=0, d=1, type="skinCluster")
        skin_clusters = list(set(skin_clusters))
        for skin_cluster in skin_clusters:
            mesh = cmds.skinCluster(skin_cluster, q=1, geometry=1)[0]
            polygon_name = cmds.listRelatives(mesh, p=1)[0]
            swap_skin(polygon_name, src_joint, dst_joint)


def get_open_path(default_path, ext):
    path, _ = QFileDialog.getOpenFileName(get_app(), "Load", default_path, "{0} (*.{0})".format(ext))
    return path


def get_open_dir(default_path):
    path = QFileDialog.getExistingDirectory(get_app(), "Load", default_path)
    return path


def get_save_path(default_path, ext):
    path, _ = QFileDialog.getSaveFileName(get_app(), "Export", default_path, "{0} (*.{0})".format(ext))
    return path


class Path(QLineEdit):
    ModeOpen, ModeSave, ModeOpenDir = range(3)

    def __init__(self, root, ext, mode):
        QLineEdit.__init__(self)
        self.root = root
        self.ext = ext
        self.mode = mode

    def text(self):
        text = QLineEdit.text(self)
        if u"\\" in text:
            text = text.replace(u"\\", u"/")
        elif u"/" not in text:
            path = os.path.join(self.root, text)
            if not path.endswith(self.ext):
                path = ".".join([path, self.ext])
            if os.path.isfile(path):
                text = path.replace(u"\\", u"/")
        return text

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
        if self.mode == self.ModeOpen:
            path = get_open_path(self.root, self.ext)
        elif self.mode == self.ModeOpenDir:
            path = get_open_dir(self.root)
        else:
            path = get_save_path(self.root, self.ext)
        if not path:
            return
        self.setText(path)


class Tool(QDialog):

    def __init__(self, parent):
        QDialog.__init__(self, parent)
        root = os.path.join(os.path.expanduser("~"), "maya", "x3_swap_skin").replace("\\", "/")
        if not os.path.isdir(root):
            os.makedirs(root)
        self.setWindowTitle(u"替换权重")
        self.path = Path(root, ";*.".join(["csv", "CSV"]), Path.ModeOpen)
        self.path.setText(root+"/joints.csv")
        self.setLayout(q_add(
            QVBoxLayout(),
            self.path,
            q_button(u"替换权重", self.apply)
        ))

    def apply(self):
        swap_scv_skin(self.path.text())


def get_app():
    top = QApplication.activeWindow()
    if top is None:
        return
    while True:
        parent = top.parent()
        if parent is None:
            return top
        top = parent


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


window = None


def show():
    global window
    if window is None:
        window = Tool(parent=get_app())
    window.show()


def swap_scv_skin(path):
    if not os.path.isfile(path):
        return
    with open(path, "r") as fp:
        swap_skin_all(csv.reader(fp))


def doit():
    # swap_skin("pSphere1", "joint1", "joint2")
    # swap_skin_all([["joint1", "joint2"]])
    # show()
    swap_scv_skin("C:/Users/mengya/Documents//maya//x3_swap_skin/joints.csv")
