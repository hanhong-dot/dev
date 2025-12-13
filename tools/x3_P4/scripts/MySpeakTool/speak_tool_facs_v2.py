# coding:utf-8

import json
import pymel.core as pm
import os
import stat
from maya import cmds
try:
    from PySide.QtGui import *
    from PySide.QtCore import *
except ImportError:
    from PySide2.QtGui import *
    from PySide2.QtCore import *
    from PySide2.QtWidgets import *


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


def write_json_data(path, data):
    if os.path.isfile(path):
        os.chmod(path, stat.S_IWRITE)
    with open(path, "w") as fp:
        json.dump(data, fp, indent=4)


def read_json_data(path):
    with open(path, "r") as fp:
        return json.load(fp)


def get_time_scale():
    time_scale = 1
    time_unit = pm.currentUnit(q=1, t=1)
    if time_unit == "ntsc":
        time_scale = 0.5
    elif time_unit == "ntscf":
        time_scale = 1
    return time_scale


def get_config():
    config_path = os.path.abspath(__file__+"/../speak_config_facs")
    if os.path.isfile(config_path):
        return read_json_data(config_path)
    else:
        return dict()


def set_config(data):
    config_path = os.path.abspath(__file__ + "/../speak_config_facs")
    write_json_data(config_path, data)


def get_config_key(key, value):
    return get_config().get(key, value)


def set_config_key(key, value):
    data = get_config()
    data[key] = value
    set_config(data)


# au_list = [
#     "Dimpler",
#     "LipCornerDepressor",
#     "LipPuckerDn",
#     "LipPuckerUp",
#     "LipSuckDn",
#     "LipSuckUp",
#     "LipTightener",
#     "LipZipDn",
#     "LipZipUp",
#     "LowerLipDepressor",
#     "MouthStretch",
#     "SharpLipPuller",
#     "UpperLipRaiser"
# ]

au_list = [
    'LipCornerPuller',
    'LipFunneler',
    'LipPressor',
    'LipPucker',
    'LipStercher',
    'LipSuck',
    'LipTightener',
    'LowerLipDepressor',
    'MouthStretch',
    'SharpLipPuller',
    'UpperLipRaiser',
    'ChinRaiser',
    'Dimpler',
    'LipCornerDepressor',
    'JawDrop',
    'MouthCloseDn',
    'MouthCloseUp',
    'LipZipUp',
    'LipZipDn',
]

au_list += ["OOO", "PPP", "III"]
au_list.sort()


def get_speak_data():
    data = {
        "brows": [],
        "blinks": [],
        "motionPoints": [],
        "energy": [],
        "auAnimations": [[] for _ in au_list],
        "length": 0,
        "source": "maya",
        "lipScaleAnimation": [],
        "jawScaleAnimation": []
    }
    ctrl = pm.selected()[0]
    name = ctrl.name().split(":")[-1].split("|")[-1]
    if name != "speakControl":
        return pm.warning("please selected speakControl")
    # bridge = ctrl.getChildren(type="transform")
    # if len(bridge) != 1:
    #     return pm.warning("can not find SpeakBlendShapeBridge")
    # bridge = bridge[0]
    # name = bridge.name().split(":")[-1].split("|")[-1]
    # if name != "SpeakBlendShapeBridge":
    #     return pm.warning("can not find SpeakBlendShapeBridge")
    time_scale = get_time_scale()
    st = int(round(pm.playbackOptions(q=1, min=1)/time_scale))
    et = int(round(pm.playbackOptions(q=1, max=1)/time_scale))
    length = ((et - st) + 1)/60.0
    data["length"] = length
    for t in range(st, et+1, 1):
        unity_time = float(t)/60
        maya_time = t * time_scale
        pm.currentTime(maya_time)
        for keys, attr_name in zip(data["auAnimations"], au_list):
            if not ctrl.hasAttr(attr_name):
                continue
            keys.append([unity_time, ctrl.attr(attr_name).get()])
        lipscale = ctrl.tx.get()
        data["lipScaleAnimation"].append([unity_time, lipscale])
        jawscale = ctrl.ty.get()
        data["jawScaleAnimation"].append([unity_time, jawscale])
    return data


def save_phn(path):
    if path is None:
        return
    write_json_data(path, get_speak_data())


def key_abc(ctrl, name, data, ani_st, ani_et, offset):
    _st = pm.playbackOptions(q=1, min=1)
    time_scale = get_time_scale()

    for unit_time, weight in data:
        maya_time = _st + (unit_time * 60.0 * time_scale)
        st = maya_time + (ani_st * time_scale) + (offset * time_scale)
        et = maya_time + (ani_et * time_scale) + (offset * time_scale)
        st = int(round(st))
        et = int(round(et))
        pm.setKeyframe(ctrl, attribute=name + "Time", v=ani_st, t=st)
        pm.setKeyframe(ctrl, attribute=name + "Time", v=ani_et, t=et)
        pm.keyTangent(ctrl, edit=True, time=(st, st), attribute=name + "Time", ott="linear")
        pm.keyTangent(ctrl, edit=True, time=(et, et), attribute=name + "Time", itt="linear", ott="step")
        pm.setKeyframe(ctrl, attribute=name + "Weight", v=weight, t=st)
        pm.setKeyframe(ctrl, attribute=name + "Weight", v=weight, t=et)
        pm.keyTangent(ctrl, edit=True, time=(st, st), attribute=name + "Weight", ott="linear")
        pm.keyTangent(ctrl, edit=True, time=(et, et), attribute=name + "Weight", itt="linear", ott="step")


def set_speak_data(data):
    st = pm.playbackOptions(q=1, min=1)
    ctrl = pm.selected()[0]
    pm.cutKey(ctrl, time=":", clear=1, hierarchy="none", shape=1, controlPoints=0)
    time_scale = get_time_scale()
    maya_time = st
    end_num = len(au_list)
    for keys, attr_name in zip(data["auAnimations"][0:end_num], au_list):    #delete last two[:-2]
        for unit_time, value in keys:
            maya_frame = round(unit_time*60.0)
            maya_time = st + maya_frame * time_scale
            pm.setKeyframe(ctrl, attribute=attr_name, v=value, t=maya_time-0*time_scale)
    pm.playbackOptions(e=1, min=st, max=maya_time)
    # key_abc(ctrl, "eyebrows", data["motionPoints"],  0, 124, -56)
    # key_abc(ctrl, "head", data["motionPoints"],  0, 74, -10)
    # key_abc(ctrl, "fastblink", data["blinks"],  0, 32, 0)


#喉结动画
def set_adam_data(data):
    print len(data["auAnimations"]), len(au_list)
    if len(data["auAnimations"]) == (len(au_list) + 2):
        st = pm.playbackOptions(q=1, min=1)
        ctrl = pm.selected()[0]
        time_scale = get_time_scale()
        maya_time = st
        adam_anima  = data["auAnimations"][-2:]   #last two 
        AdamDn_keys = adam_anima[0]
        AdamUp_keys = adam_anima[1]
        for down_data, up_data in zip(AdamDn_keys, AdamUp_keys):
            unit_time, down_value = down_data
            unit_time2, up_value = up_data
            value = down_value*(-1) + up_value
            maya_frame = round(unit_time*60.0)
            maya_time = st + maya_frame * time_scale
            pm.setKeyframe(ctrl, attribute="AdamSlider", v=value, t=maya_time-0*time_scale)
    else:
        ctrl = pm.selected()[0]
        try:
            cmds.setAttr("{}.AdamSlider".format(ctrl), 0)
        except RuntimeError:
            pass



def get_name_space():
    speak_namespace =  cmds.ls(sl=1)[0].split(":")[0] + ":" 
    if speak_namespace == "speakControl:":
        return ""
    else:
        return speak_namespace


def clean_keys(speak_namespace):
    find_ctrl_list = cmds.ls(u'{}FKTongue0_M'.format(speak_namespace))
    if not find_ctrl_list:
        return
    else:
        pm.cutKey([u'{}FKTongue0_M'.format(speak_namespace)], hierarchy='both', clear=1, controlPoints=0, shape=1, time=":")
        ctrl_list = [u'FKTongue0_M', u'FKTongue1_M', u'FKTongue2_M', u'FKTongue3_M']
        for ctrl in ctrl_list:
            cmds.setAttr("{}{}.translateX".format(speak_namespace,ctrl), 0)
            cmds.setAttr("{}{}.translateY".format(speak_namespace,ctrl), 0)
            cmds.setAttr("{}{}.translateZ".format(speak_namespace,ctrl), 0)
            cmds.setAttr("{}{}.rotateX".format(speak_namespace,ctrl), 0)
            cmds.setAttr("{}{}.rotateY".format(speak_namespace,ctrl), 0)
            cmds.setAttr("{}{}.rotateZ".format(speak_namespace,ctrl), 0)


def get_inverse_data():
    ns = get_name_space()
    clean_keys(ns)
    inverse_list = []
    ctrl_list = [u'FKTongue0_M', u'FKTongue1_M', u'FKTongue2_M', u'FKTongue3_M']
    for ctrl in ctrl_list:
        ctrl_name = "{}{}".format(ns, ctrl)
        ctrl = pm.PyNode(ctrl_name)
        inverse_matrix = ctrl.getParent().getMatrix().inverse() 
        inverse_list.append(inverse_matrix)
    inverse_list[0] = pm.PyNode("{}Tongue0_M".format(ns)).getMatrix().inverse()
    return inverse_list


def set_tongue_data(data):
    ns = get_name_space()
    if "tongueAnimations" in data:
        if data["tongueAnimations"] == []:
            clean_keys(ns)
        else:
            inverse_matrix_list = get_inverse_data()
            inverse_num = 0
            ctrl_list = [u'FKTongue0_M', u'FKTongue1_M', u'FKTongue2_M', u'FKTongue3_M']
            for ctrl , speak_bone_frames in zip(ctrl_list, data['tongueAnimations']):
                speak_bone_name = "{}{}".format(ns, ctrl)
                for frame in speak_bone_frames:
                    unit_time, transx, rotatez = frame
                    time_scale = get_time_scale()
                    st = pm.playbackOptions(q=1, min=1)
                    maya_time = st
                    maya_frame = round(unit_time*60.0)
                    maya_time = st + maya_frame * time_scale
                    translate_vector  = pm.datatypes.Vector(transx*(-100), 0, 0) * inverse_matrix_list[inverse_num] 
                    pm.setKeyframe(speak_bone_name, attribute="translateX", v=translate_vector[0], t=maya_time-0*time_scale)
                    pm.setKeyframe(speak_bone_name, attribute="translateY", v=translate_vector[1], t=maya_time-0*time_scale)
                    pm.setKeyframe(speak_bone_name, attribute="rotateZ", v=rotatez*(-1), t=maya_time-0*time_scale)
                inverse_num = inverse_num + 1
    else:
        clean_keys(ns)


def load_phn(path=r"D:\work\liuruomei\v6\SpecialDate_ST_02_Excel_359.phn"):
    if path is None:
        return
    set_speak_data(read_json_data(path))
    set_adam_data(read_json_data(path))
    set_tongue_data(read_json_data(path))


def load_sound(path=r"T:/WwiseProject/Project_IMIL/Originals/Voices/zh-CN/MainLine/Chapter01/Stage01-01/MainStory_Ch1_10101_Excel_10.wav"):
    st = pm.playbackOptions(q=1, min=1)
    pm.delete(pm.ls(type="audio"))
    pm.importFile(path, typ="audio", options="o=%i" % st)


class PrefixWeight(QHBoxLayout):
    def __init__(self, label, weight, width=60):
        QHBoxLayout.__init__(self)
        prefix = QLabel(label)
        prefix.setFixedWidth(width)
        prefix.setAlignment(Qt.AlignRight)
        self.addWidget(prefix)
        self.addWidget(weight)


class DirLine(QLineEdit):
    def __init__(self):
        QLineEdit.__init__(self)
        self.setReadOnly(True)
        self.default_root = get_config_key("phn_path", "T:/Tools/LipSyncWizard/output/zh-CN")
        self.setText(self.default_root)

    def mouseDoubleClickEvent(self, event):
        QLineEdit.mouseDoubleClickEvent(self, event)
        path = QFileDialog.getExistingDirectory(get_host_app(), "T:/Tools/LipSyncWizard/output/zh-CN")
        if not path:
            return
        self.setText(path.replace("\\", "/"))

    def setText(self, text):
        QLineEdit.setText(self, text)
        set_config_key("phn_path", text.replace("\\", "/"))


class SavePhnPath(DirLine):

    def __init__(self):
        QLineEdit.__init__(self)
        self.setReadOnly(True)
        self.default_root = get_config_key("save_path", "T:/Tools/LipSyncWizard/output/zh-CN/MayaEdit")
        self.setText(self.default_root)

    def setText(self, text):
        QLineEdit.setText(self, text)
        set_config_key("save_path", text.replace("\\", "/"))


class Sound(DirLine):

    def __init__(self):
        QLineEdit.__init__(self)
        self.setReadOnly(True)
        self.default_root = get_config_key("sound_path", "Z:/Project_IMIL/Originals/Voices/zh-CN")
        self.data = None
        self.setText(self.default_root)

    def setText(self, text):
        QLineEdit.setText(self, text)
        set_config_key("sound_path", text.replace("\\", "/"))
        self.data = dict()
        for root, dir_names, file_names in os.walk(text):
            for file_name in file_names:
                path = os.path.join(root, file_name).replace("\\", "/")
                base, ext = os.path.splitext(file_name)
                if ext == ".wav":
                    self.data[base] = path

    def load_phn(self, path):
        base, _ = os.path.splitext(os.path.basename(path))
        sound_path = self.data.get(base)
        if sound_path is None:
            raise IOError, "can not find sound file"
        load_sound(sound_path)


class Files(QListWidget):
    loadPHN = Signal(unicode)

    def __init__(self):
        QListWidget.__init__(self)
        self.root = ""
        self.query = ""
        self.save_path = ""
        self.menu = QMenu(self)
        self.menu.addAction(u"加载", self.load_phn)
        self.menu.addAction(u"上传", self.save_phn)

    def current_path(self):
        if len(self.selectedItems()) != 1:
            return
        path = os.path.join(self.root, self.selectedItems()[0].text()).replace("\\", "/")
        return path

    def current_save_path(self):
        if len(self.selectedItems()) != 1:
            return
        path = os.path.join(self.save_path, self.selectedItems()[0].text()).replace("\\", "/")
        return path

    def load_phn(self):
        load_phn(self.current_path())
        self.loadPHN.emit(self.current_path())

    def save_phn(self):
        save_phn(self.current_save_path())

    def update_root(self, path):
        if not os.path.isdir(path):
            return
        self.root = path
        self.clear()
        names = []
        for name in os.listdir(self.root):
            _, ext = os.path.splitext(name)
            if ext != ".phn":
                continue
            names.append(name)
        self.addItems(names)
        self.update_query(self.query)

    def update_save_path(self, save_path):
        if not os.path.isdir(save_path):
            return
        self.save_path = save_path

    def update_query(self, query):
        self.query = query
        if self.query:
            for i in range(self.count()):
                item = self.item(i)
                if all([field in item.text() for field in self.query.split(",")]):
                    self.setItemHidden(item, False)
                else:
                    self.setItemHidden(item, True)
        else:
            for i in range(self.count()):
                item = self.item(i)
                self.setItemHidden(item, False)

    def contextMenuEvent(self, event):
        self.menu.exec_(event.globalPos())


class SpeakTool(QDialog):

    def __init__(self):
        QDialog.__init__(self, get_host_app())
        self.setWindowTitle(u"口型工具")
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.root = DirLine()
        self.sound = Sound()
        self.save = SavePhnPath()
        layout.addLayout(PrefixWeight(u"根目录：", self.root))
        layout.addLayout(PrefixWeight(u"音频目录：", self.sound))
        layout.addLayout(PrefixWeight(u"保存目录：", self.save))
        self.query = QLineEdit()
        layout.addLayout(PrefixWeight(u"搜索：", self.query))
        self.files = Files()
        layout.addWidget(self.files)
        self.root.textChanged.connect(self.files.update_root)
        self.query.textChanged.connect(self.files.update_query)
        self.resize(380, 380/0.618)
        self.files.loadPHN.connect(self.sound.load_phn)
        self.save.textChanged.connect(self.files.update_save_path)

    def showNormal(self):
        # QDialog.showNormal(self)
        self.files.update_root(self.root.text())
        self.files.update_save_path(self.save.text())

window = None


def show():
    global window
    if window is None:
        window = SpeakTool()
    window.showNormal()


def load_npy(name):
    path = "D:/to_wuwu/mengya/regression1/sequence_res/debug/%s.npy" % name
    cof = "D:/to_wuwu/mengya/regression1/Config/blendshape_config.json"
    import json
    with open(cof, "r") as fp:
        bs_data = json.load(fp)
    import numpy
    ani_data = numpy.load(path)
    bs = pm.PyNode("speakControl")
    start = pm.playbackOptions(q=1, min=1)
    for i in range(ani_data.shape[0]):
        for name, index in bs_data["lip_sync"].items():
            name, _ = os.path.splitext(name)
            if not bs.hasAttr(name):
                continue
            value = ani_data[i][index]
            print name, value
            pm.setKeyframe(bs, attribute=name, v=value, t=start + i)


from maya.api.OpenMaya import *
def get_err():

    import numpy as np
    base = "base_mod"
    origin = "phone_word_test_FLAME_sample"
    sel = MSelectionList()
    sel.add(base)
    sel.add(origin)

    with open(r"D:\to_wuwu\mengya\regression1\mouth_index\mask.json", "r") as f:
        donghao_mask = json.load(f)
    base_points = np.array(MFnMesh(sel.getDagPath(0)).getPoints())[:3931, :3]
    origin_points = np.array(MFnMesh(sel.getDagPath(1)).getPoints())[:3931, :3]
    err = np.sum(np.linalg.norm((origin_points - base_points) * np.expand_dims(np.array(donghao_mask), axis=-1), axis=1))
    return err
    # donghao_mask = np.load(r"D:\work\liuruomei\mengya\regression1\mouth_index\liuruomei_bigmouth_mouth_index.npy")
    # base_points = np.array(MFnMesh(sel.getDagPath(0)).getPoints())[donghao_mask, :3]
    # origin_points = np.array(MFnMesh(sel.getDagPath(1)).getPoints())[donghao_mask, :3]
    # print np.sum(np.linalg.norm(origin_points - base_points, axis=1))


def get_errs():
    name = "blendShape1.Dimpler2"
    for i in range(101):
        pm.setAttr(name, i*0.01)
        print i*0.01, get_err()


def export_selected_obj():
    polygon = pm.selected()[0]
    bs = pm.listHistory(polygon, type="blendShape")[0]
    for name in bs.weight.elements():
        if bs.attr(name).inputs():
            continue
        if bs.attr(name).isLocked():
            continue
        bs.attr(name).set(0)
    pm.exportSelected("D:/work/liuruomei/v6/obj/%s.obj" % "base")
    for name in bs.weight.elements():
        if bs.attr(name).isLocked():
            continue
        if bs.attr(name).inputs():
            continue
        bs.attr(name).set(1)
        pm.exportSelected("D:/work/liuruomei/v6/obj/%s.obj" % name)
        bs.attr(name).set(0)


def add_attribute(ctrl, attr):
    if not ctrl.hasAttr(attr):
        pm.addAttr(ctrl, ln=attr, at='double', min=0, max=1, dv=0)
        pm.setAttr(ctrl + '.' + attr, e=1, keyable=1)
        pm.setAttr(ctrl + '.' + attr, 0)

def add_new_BS_test():
    attr_list = ['LipFunneler', 'LipPressor', 'LipPucker', 'LipSuck', 'ChinRaiser']
    updn_attr_list = []
    for i in attr_list:
        updn_attr_list.append(i + 'Up')
        updn_attr_list.append(i + 'Dn')

    from wuwu.MySpeakEditor_FACS import split_combined_bs as split
    reload(split)
    for attr in updn_attr_list:
        split.add_blank_BS(attr=attr, BS_geo='Scale|base', ifDelete=0)

    from wuwu.MySpeakTool import speak_tool
    reload(speak_tool)
    for attr in updn_attr_list:
        speak_tool.connect_bs(attr)


def connect_bs(attr='LipCornerIn'):
    src = pm.PyNode("SpeakBlendShapeBridge")
    dst = pm.PyNode("blendShape1")
    ctrl = pm.PyNode('speakControl')
    add_attribute(src, attr)
    add_attribute(ctrl, attr)
    # for name in src.weight.elements():
    # for name in src.listAttr(ud=1):
    #     name = name.name().split(".")[-1]
    #     if src.attr(name).isLocked():
    #         continue
    #     if not dst.hasAttr(name):
    #         continue
    #     if dst.attr(name).inputs():
    #         continue
    if not src.attr(attr).isLocked() and dst.hasAttr(attr) and not dst.attr(attr).inputs():
        src.attr(attr).connect(dst.attr(attr))

        if not pm.objExists(attr + 'BW'):
            pm.createNode('blendWeighted', n=attr + 'BW')
        BW = pm.PyNode(attr + 'BW')
        if not BW.input[0].listConnections():
            ctrl.attr(attr).connect(BW.input[0])
        if attr in ['UpperLipRaiser', 'LowerLipDepressor', 'MouthStretch', 'LipZipUp',
                    'LipZipDn', 'JawDrop', 'MouthCloseDn', 'MouthCloseUp']:
            if not BW.weight[0].listConnections():
                ctrl.ty.connect(BW.weight[0])
                print attr, 'ty'
        else:
            if not BW.weight[0].listConnections():
                ctrl.tx.connect(BW.weight[0])
                print attr, 'tx'
        if not BW.output.listConnections():
            BW.output.connect(src.attr(attr))


def save_weights(json_name):
    '''
    记录mask权重，并导出为json
    文件路径为D:\kouxing\new_FACS\model\model_newbase_Mask.ma
    :param json_name: str   json的名称
    '''
    sk = pm.PyNode("skinCluster1")
    joint = pm.PyNode("joint2")
    geo = sk.getGeometry()[0]
    index = sk.influenceObjects().index(joint)
    wts = sk.getWeights(geo, index)
    wts = list(wts)
    pm.select([geo.vtx[i] for i, w in enumerate(wts) if w > 0.1])
    import json
    json_path = r"D:\to_wuwu\mengya\regression1\mouth_index/%s" % json_name
    with open(json_path, "w") as fp:
        json.dump(wts, fp)

def draw_weights(json_name):
    '''
    根据json文件，绘制mask权重
    :param json_name: str   json的名称
    '''
    json_path = r"D:\to_wuwu\mengya\regression1\mouth_index/%s" % json_name
    with open(json_path, "r") as f:
        mesh_mask = json.load(f)
    sk = pm.PyNode("skinCluster1")
    joint = pm.PyNode("joint2")
    geo = sk.getGeometry()[0]

    index = sk.influenceObjects().index(joint)
    sk.setWeights(geometry=geo, influnces=[index], weights=mesh_mask, normalize=True)
    pm.select([geo.vtx[i] for i, w in enumerate(mesh_mask) if w > 0.1])



def close_sdk():
    bs = pm.PyNode("blendShape9")

