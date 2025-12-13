# coding:utf-8
from .adPose2.general_ui import *
import json
import os


def find_all_bs_info(data, bs_info_list=None):
    if bs_info_list is None:
        bs_info_list = []
    if isinstance(data, dict):
        if "bsInfo" in data and isinstance(data["bsInfo"], list):
            bs_info_list += data["bsInfo"]
        for elem in data.values():
            find_all_bs_info(elem, bs_info_list)
    elif isinstance(data, list):
        for elem in data:
            find_all_bs_info(elem, bs_info_list)
    return bs_info_list


def check_fbx_json(json_path, fbx_path):
    pm.openFile(fbx_path, type="FBX", f=1, ignoreVersion=1)
    with open(json_path, "r") as fp:
        data = json.load(fp)
    assert isinstance(data, dict), "json data type error"
    assert "bsMeshs" in data, "can not find bs mesh"
    mesh_name_list = data["bsMeshs"]
    assert isinstance(mesh_name_list, list), "bs mesh type error"
    mesh_list = []
    bs_list = []
    for name in mesh_name_list:
        assert isinstance(name, (str, unicode)), "bs mesh elem type error"
        name = name.split("/")[-1]
        mesh_nodes = pm.ls(name, type="transform")
        assert len(mesh_nodes) == 1, "can not find  " + name
        mesh_list.append(mesh_nodes[0])
        bs_nodes = pm.listHistory(mesh_nodes[0], type="blendShape")
        if len(bs_nodes):
            bs_list.append(bs_nodes[0])
        else:
            bs_list.append(None)
    bs_info_list = find_all_bs_info(data)
    for bs_info in bs_info_list:
        assert isinstance(bs_info, dict), "bsInfo Type Error"
        assert "target" in bs_info, "bsInfo can not find target"
        assert "meshID" in bs_info, "bsInfo can not find meshID"
        target = bs_info["target"]
        mesh_id = bs_info["meshID"]
        assert isinstance(target, (str, unicode)), "target type error"
        assert isinstance(mesh_id, int), "mesh_id type error"
        assert mesh_id < len(bs_list), "mesh id index out of range "
        bs_node = bs_list[mesh_id]
        bs_name, target_name = target.split(".")
        assert bs_node is not None, "can not find " + bs_name
        assert bs_name == bs_node.name(), "can not find " + bs_name
        assert bs_node.hasAttr(target_name), "can not find " + target
    assert "allDrivenNodes" in data, "can not find allDrivenNodes"
    all_driven_nodes = data["allDrivenNodes"]
    assert isinstance(all_driven_nodes, list), "allDrivenNodes type error"
    for name in all_driven_nodes:
        assert isinstance(name, (str, unicode)), "joint name type error"
        name = name.split("/")[-1]
        joint_nodes = pm.ls(name, type="joint")
        assert len(joint_nodes) == 1, "can not find "
    return True


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
        url = QFileDialog.getOpenFileName(parent=self, filter="{self.label}(*{self.ext})".format(self=self))[0]
        self.setText(url)

    def resizeEvent(self, event):
        QLineEdit.resizeEvent(self, event)
        self.setTextMargins(0, 0, 0, 0)


class FbxJsonCheck(Tool):
    title = u"fbx json 检查"
    button_text = u"检查"

    def __init__(self, parent):
        Tool.__init__(self, parent)
        self.fbx = Path("fbx", ".fbx")
        self.json = Path("json", ".json")
        self.kwargs_layout.addLayout(PrefixWeight(u"FBX：", self.fbx, 50))
        self.kwargs_layout.addLayout(PrefixWeight(u"Json：", self.json, 50))
        self.resize(300, 10)

    def apply(self):
        fbx_path = self.fbx.text()
        json_path = self.json.text()
        try:
            check_fbx_json(json_path, fbx_path)
            QMessageBox.about(get_host_app(), u"提示", u"检查通过！")
        except AssertionError as err:
            QMessageBox.warning(get_host_app(), u"错误", err.message)


window = None


def show():
    global window
    if window is None:
        window = FbxJsonCheck(get_host_app())
    window.showNormal()


def main():
    # json_path = "D:/work/ADPose/fbx_cehck/ST001C_HD.json"
    # fbx_path = "D:/work/ADPose/fbx_cehck/ST001C_HD.fbx"
    # check_fbx_json(json_path, fbx_path)
    # json_path = "D:/work/ADPose/fbx_cehck/base_body_test.json"
    # fbx_path = "D:/work/ADPose/fbx_cehck/ST001C_HD.fbx"
    # check_fbx_json(json_path, fbx_path)
    # global window
    # window = FbxJsonCheck(get_host_app())
    # window.showNormal()
    show()


