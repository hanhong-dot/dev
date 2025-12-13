# coding:utf-8

import pymel.core as pm
import os
from maya.OpenMaya import *
from maya.OpenMayaAnim import *

try:
    from PySide.QtGui import *
    from PySide.QtCore import *
except ImportError:
    from PySide2.QtGui import *
    from PySide2.QtCore import *
    from PySide2.QtWidgets import *


def dup_fbx(objects=None):
    if objects is None:
        objects = pm.selected()
    pm.select(objects)
    for node in pm.listRelatives(objects[0].getParent(), ad=1):
        pm.delete(pm.ls(node.name().split(":")[-1]))
    path = pm.sceneName() + ".temp.fbx"
    pm.mel.FBXResetExport()
    pm.mel.eval("FBXProperty Export|IncludeGrp|Animation -v false")
    pm.mel.eval("FBXProperty Export|IncludeGrp|Animation|BakeComplexAnimation -v false")
    pm.mel.eval("FBXExportInputConnections -v false")
    pm.mel.eval("FBXProperty  Export|IncludeGrp|Geometry|SmoothingGroups -v true")
    pm.mel.eval("FBXProperty  Export|IncludeGrp|Geometry|SmoothMesh -v true")
    pm.mel.eval("FBXProperty  Export|IncludeGrp|Geometry|Triangulate -v true")
    pm.select(objects)
    pm.exportSelected(path, type="FBX export", f=1)
    if pm.namespace(exists=":lush_dup_fbx_temp"):
        pm.namespace(rm=":lush_dup_fbx_temp", mnp=1)
    pm.createReference(path, type="FBX", namespace="lush_dup_fbx_temp", f=1)
    pm.mel.file(path, ir=1)
    ns = ":lush_dup_fbx_temp:" + objects[0].name().split(":")[0]
    if pm.namespace(exists=ns):
        pm.namespace(rm=ns, mnp=1)
    for node in pm.ls("|lush_dup_fbx_temp:*", type="transform"):
        if not node.name().endswith("_Rig"):
            pm.delete(node)
    group = pm.ls("|lush_dup_fbx_temp:*", type="transform")[0]
    nodes = pm.ls("|lush_dup_fbx_temp:*")
    if pm.namespace(exists=":lush_dup_fbx_temp"):
        pm.namespace(rm=":lush_dup_fbx_temp", mnp=1)
    ns = objects[0].name().split(":")[0] + ":"
    for joint in pm.listRelatives(group, type="joint", ad=1):
        re_node = pm.ls(ns+joint.name().split("|")[-1])[0]
        for trs in "trs":
            for xyz in "xyz":
                dst_attr = joint.attr(trs+xyz)
                if dst_attr.isLocked():
                    continue
                re_node.attr(trs+xyz).connect(joint.attr(trs+xyz))
        for attr in joint.listAttr(ud=1):
            pm.deleteAttr(attr)
    for mesh in pm.listRelatives(group, type="mesh", ad=1):
        if mesh.io.get():
            continue
        polygon = mesh.getParent()
        if not pm.listHistory(polygon, type="blendShape"):
            continue
        bs = pm.listHistory(polygon, type="blendShape")[0]
        re_polygon = pm.ls(ns+polygon.name().split("|")[-1])[0]
        re_bs = pm.listHistory(re_polygon, type="blendShape")[0]
        for attr in bs.weight.elements():
            if not re_bs.hasAttr(attr):
                continue
            if not bs.hasAttr(attr):
                continue
            re_bs.attr(attr).connect(bs.attr(attr), f=1)
    os.remove(path)
    return group, nodes


def export_fbx(path, st, et, cam=False):
    dir_path = os.path.dirname(path)
    if not os.path.isdir(dir_path):
        os.makedirs(dir_path)
    pm.mel.FBXResetExport()
    pm.mel.eval("FBXProperty Export|IncludeGrp|Animation|BakeComplexAnimation -v true")
    pm.mel.eval("FBXProperty Export|IncludeGrp|Animation|BakeComplexAnimation|BakeFrameStart -v %s" % st)
    pm.mel.eval("FBXProperty Export|IncludeGrp|Animation|BakeComplexAnimation|BakeFrameEnd -v %s" % et)
    pm.mel.eval("FBXProperty Export|IncludeGrp|Animation|BakeComplexAnimation|BakeFrameStep -v 1")
    pm.mel.eval("FBXProperty Export|IncludeGrp|Animation|BakeComplexAnimation|ResampleAnimationCurves -v true")
    pm.mel.eval("FBXExportInputConnections -v false")
    if not cam:
        pm.mel.eval("FBXProperty  Export|IncludeGrp|Geometry|SmoothingGroups -v true")
        pm.mel.eval("FBXProperty  Export|IncludeGrp|Geometry|SmoothMesh -v true")
        pm.mel.eval("FBXProperty  Export|IncludeGrp|Geometry|Triangulate -v true")
    pm.exportSelected(path, type="FBX export", f=1)


def abc_export(path=None, st=None, et=None):
    if st is not None:
        pm.playbackOptions(e=1, min=st)
    if et is not None:
        pm.playbackOptions(e=1, max=et)
    root = u" -root ".join([u""]+[sel.fullPath() for sel in pm.selected()])
    j = u"-frameRange {st} {et} -stripNamespaces -uvWrite -writeFaceSets -worldSpace -writeUVSets -dataFormat ogawa{root} -file {path}, -root"
    pm.AbcExport(j=j.format(**locals()))


def is_char_rig_path(path):
    if "/Role/" in path:
        return True
    for typ in ["body", "npc", "role", "enemy", "weapon", "hair", "rolaccesory"]:
        if  "/%s/" % typ in path:
            return True
    return False


def find_char_roots():
    roots = []
    for joint in pm.ls("*:Roots", type="joint"):
        if not joint.isReferenced():
            continue
        path = joint.referenceFile().path.replace("\\", "/")
        print "is_char_rig_path", is_char_rig_path(path)
        if not is_char_rig_path(path):
            continue
        roots.append(joint)
    return roots


# def get_geo_group_list(root, body, cloth):
#     group = root.getParent()
#     geo_group_list = []
#
#     for geo_group in pm.listRelatives(group, type="transform"):
#         if geo_group.endswith("_lod"):
#             continue
#         if geo_group.endswith("_ld"):
#             continue
#         if not geo_group.v.get():
#             continue
#         if geo_group.type() != "transform":
#             continue
#         if any([body, cloth]):
#             if "BaseHead" in geo_group.name():
#                 geo_group_list.append(geo_group)
#             elif geo_group.name().endswith("F_UE"):
#                 geo_group_list.append(geo_group)
#         if body:
#             if "BaseBody" in geo_group.name():
#                 geo_group_list.append(geo_group)
#             if geo_group.name().endswith("B_UE"):
#                 geo_group_list.append(geo_group)
#         if cloth:
#             if "Hair" in geo_group.name():
#                 continue
#             if geo_group.name().endswith("_HD"):
#                 geo_group_list.append(geo_group)
#                 continue
#             geo_group_list.append(geo_group)
#     return geo_group_list


def get_export_group_list(group, typ):
    # char_joint, body_abc, body_fbx, cloth_abc, cloth_fbx = range(5)
    char_joint, cloth_fbx = range(2)
    joint = [grp for grp in group.getChildren() if grp.type() == "joint"]
    face = [grp for grp in group.getChildren() if grp.name().endswith("Head")]
    hair = [grp for grp in group.getChildren() if grp.name().endswith("Hair")]
    body = [grp for grp in group.getChildren() if grp.name().endswith("Body")]
    # suits = [grp for grp in group.getChildren() if grp.name().endswith("") and grp not in face+hair+body]
    suits = [grp for grp in group.getChildren() if grp not in face + hair + body]
    exports = []
    # if typ == body_fbx:
    #     exports = joint+face+body
    # elif typ == body_abc:
    #     exports = face+body
    # elif typ == char_joint:
    if typ == char_joint:
        exports = joint
    elif typ == cloth_fbx:
        exports = joint + face + suits
    # elif typ == cloth_abc:
    #     exports = face + suits
    return exports


def export_char(root, base_path, st, et, check_list):
    # cam, prop, char_joint, body_abc, body_fbx, cloth_abc, cloth_fbx = check_list
    # if not any([char_joint, body_abc, body_fbx, cloth_abc, cloth_fbx]):
    cam, prop, char_joint, cloth_fbx = check_list
    if not any([char_joint, cloth_fbx]):
        return
    export_groups = []
    group = root.getParent()
    # for typ, is_export in enumerate([char_joint, body_abc, body_fbx, cloth_abc, cloth_fbx]):
    for typ, is_export in enumerate([char_joint, cloth_fbx]):
        if not is_export:
            continue
        for export_group in get_export_group_list(group, typ):
            if export_group  in export_groups:
                continue
            export_groups.append(export_group)
    group, temp_nodes = dup_fbx(export_groups)
    base_name = os.path.basename(base_path)
    char_name = group.name().split("_")[0]
    if char_name in base_name:
        suffix = "_" + char_name
    else:
        suffix = "_" + char_name
    if char_joint:
        pm.select(get_export_group_list(group, 0))
        export_fbx(base_path + suffix + ".fbx", st, et)
    # if body_abc:
    #     pm.select(get_export_group_list(group, 1))
    #     abc_export(base_path + suffix + ".abc", st, et)
    # if body_fbx:
    #     pm.select(get_export_group_list(group, 2))
    #     export_fbx(base_path + suffix + "_All.fbx", st, et)
    # if cloth_abc:
    #     pm.select(get_export_group_list(group, 3))
    #     abc_export(base_path + suffix + "_All_Cloth.abc", st, et)
    if cloth_fbx:
        # pm.select(get_export_group_list(group, 4))
        pm.select(get_export_group_list(group, 1))
        pm.select([grp for grp in group.getChildren() if grp.type() == "joint"], add=1)
        export_fbx(base_path + suffix + "_All_Cloth.fbx", st, et)
    pm.delete(temp_nodes)


def export_all_char(base_path, st, et, check_list, roots):
    for root in find_char_roots():
        if root.name() not in roots:
            continue
        export_char(root, base_path, st, et, check_list)


def export_prop(root, base_path, st, et):
    objects = root.getParent().getChildren()
    group, temp_nodes = dup_fbx(objects)
    suffix = "_" + root.name().split(":")[0]
    pm.select(group)
    export_fbx(base_path + suffix + ".fbx", st, et)
    pm.delete(temp_nodes)


def find_prop_roots():
    roots = []
    for joint in pm.ls("*:Root_M"):
        if joint.isReferenced():
            path = joint.referenceFile().path.replace("\\", "/")
            if "/Role/" in path:
                continue
        roots.append(joint)
    return roots


def export_all_prop(base_path, st, et, roots):
    for root in find_prop_roots():
        export_prop(root, base_path, st, et)


def export_cam(cam_name, base_path, st, et):
    path = base_path+"_Cam.fbx"
    name = os.path.splitext(os.path.basename(path))[0]
    node = pm.ls(cam_name, type="transform")[0]
    cam = node.duplicate()[0]
    for child in cam.getChildren():
        if child.type() == "camera":
            continue
        pm.delete(child)
    pm.parent(cam, w=1)
    cam.rename(name)
    for trs in "trs":
        for xyz in "xyz":
            cam.attr(trs + xyz).setLocked(False)
            cam.attr(trs + xyz).setKeyable(True)
    cam.attr("r").setLocked(False)
    cam.attr("r").setKeyable(True)
    parent_constraint = pm.parentConstraint(node, cam)
    pm.parent(parent_constraint, w=1)
    src = node.getShape()
    dst = cam.getShape()
    for attr in src.listAttr():
        try:
            if not attr.inputs():
                continue
        except:
            continue
        attr.connect(dst.attr(attr.name(includeNode=False)))
    pm.select(cam)
    export_fbx(path, st, et, cam=True)
    pm.delete(cam, parent_constraint)


def card_export_all(base_path, cam_name, st, et, check_list, roots):
    # cam, prop, char_joint, body_abc, body_fbx, cloth_abc, cloth_fbx = check_list
    cam, prop, char_joint, cloth_fbx = check_list
    if prop:
        export_all_prop(base_path, st, et, roots)
    if cam:
        export_cam(cam_name, base_path, st, et)
    export_all_char(base_path, st, et, check_list, roots)


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


def about(text):
    QMessageBox.about(get_host_app(), u"提示", text)


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
        url, _ = os.path.splitext(url)
        self.setText(url)

    def resizeEvent(self, event):
        QLineEdit.resizeEvent(self, event)
        self.setTextMargins(0, 0, 0, 0)


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


def get_cam():
    for cam in pm.ls(type="camera"):
        if not pm.referenceQuery(cam, isNodeReferenced=True):
            continue
        if "SheXiangJiRig_Shot001" not in cam.name():
            continue
        return cam.getParent()
    for cam in pm.ls(type="camera"):
        if cam.name() in [u'perspShape', u'topShape', u'frontShape', u'sideShape']:
            continue
        return cam.getParent()
    for cam in pm.ls(type="camera"):
        return cam.getParent()


def get_ui_default_kwargs():
    cam_name = get_cam()
    st = int(round(pm.playbackOptions(q=1, min=1)))
    et = int(round(pm.playbackOptions(q=1, max=1)))
    file_path, _ = os.path.splitext(pm.sceneName())
    dir_path, name = os.path.split(file_path)
    return cam_name, st, et, dir_path, name


class PvPublish(QDialog):

    def __init__(self):
        QDialog.__init__(self, get_host_app())
        self.setMinimumWidth(360)
        self.setWindowTitle(u"PV导出")
        layout = QVBoxLayout()
        self.setLayout(layout)

        button = QPushButton(u"拾取关键帧")
        layout.addWidget(button)
        button.clicked.connect(self.update_time_range)

        self.st = QSpinBox()
        self.st.setRange(-1000000, +1000000)
        pre_layout = PrefixWeight(u"开始帧：", self.st)
        pre_layout.addStretch()
        layout.addLayout(pre_layout)

        self.et = QSpinBox()
        self.et.setRange(-1000000, +1000000)
        pre_layout = PrefixWeight(u"结束帧：", self.et)
        pre_layout.addStretch()
        layout.addLayout(pre_layout)

        self.node = MayaObeLayout(u"摄像机：")
        layout.addLayout(self.node)

        self.path = Path(u"FBX", ".fbx")
        layout.addLayout(PrefixWeight(u"文件路径：", self.path))
        self.name = QLineEdit()
        layout.addLayout(PrefixWeight(u"文件名：", self.name))

        self.roots = QListWidget()
        self.roots.setSelectionMode(self.roots.ContiguousSelection)
        layout.addWidget(self.roots)
        button = QPushButton(u"刷新场景角色")
        button.clicked.connect(self.update_char)
        layout.addWidget(button)

        self.check_list = []
        # label_list = [u"摄像机", u"道具", u"角色骨骼", u"裸模abc", u"裸模all", u"套装abc", u"套装all"]
        label_list = [u"摄像机", u"道具", u"角色骨骼", u"套装all"]
        for label in label_list:
            check = QCheckBox()
            check.setChecked(True)
            layout.addLayout(PrefixWeight(label, check))
            self.check_list.append(check)

        button = QPushButton(u"卡牌一键导出")
        layout.addWidget(button)
        button.clicked.connect(self.apply)

    def update_char(self):
        names = [root.name() for root in find_char_roots()]
        self.roots.clear()
        self.roots.addItems(names)

    def showNormal(self):
        QDialog.showNormal(self)
        cam_name, st, et, dir_path, base_name = get_ui_default_kwargs()
        self.node.set_obj(cam_name)
        self.path.setText(dir_path)
        self.name.setText(base_name)
        self.st.setValue(st)
        self.et.setValue(et)
        self.update_char()

    def update_time_range(self):
        cam_name, st, et, dir_path, base_name = get_ui_default_kwargs()
        self.st.setValue(st)
        self.et.setValue(et)

    def apply(self):
        dir_path = self.path.text()
        base_name = self.name.text()
        file_path = os.path.join(dir_path, base_name).replace("\\", "/")
        st = self.st.value()
        et = self.et.value()
        cam_name = self.node.line.text()
        check_list = [check.isChecked() for check in self.check_list]
        roots = [item.text() for item in self.roots.selectedItems()]
        card_export_all(file_path, cam_name, st, et, check_list, roots)


window = None


def show():
    global window
    if window is None:
        window = PvPublish()

    window.showNormal()


if __name__ == '__main__':
    show()

