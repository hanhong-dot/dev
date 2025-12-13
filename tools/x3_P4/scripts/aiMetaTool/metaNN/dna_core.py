# coding=utf-8
import json
from maya import cmds
import os
import dna
print(dna)
from dna import BinaryStreamReader, BinaryStreamWriter, DataLayer_All, FileStream, Status


def load_dna(path):
    stream = FileStream(path, FileStream.AccessMode_Read, FileStream.OpenMode_Binary)
    reader = BinaryStreamReader(stream, DataLayer_All)
    reader.read()
    return reader


class Dna(object):

    def __init__(self, dna_path):
        self.dna_path = dna_path
        self.reader = load_dna(self.dna_path)

    def get_raw_controls(self):
        return [self.reader.getRawControlName(index).split(".")[-1]
                for index in range(self.reader.getRawControlCount())]

    def get_psd_data(self):
        psd_indexes = self.reader.getPSDRowIndices()
        raw_indexes = self.reader.getPSDColumnIndices()
        psd_data = dict()
        for psd_index, raw_index in zip(psd_indexes, raw_indexes):
            psd_data.setdefault(psd_index, []).append(raw_index)
        return psd_data

    def get_psd_controls(self):
        raw_controls = self.get_raw_controls()
        psd_data = self.get_psd_data()
        psd_controls = ["_".join(sorted([raw_controls[raw_index] for raw_index in psd_data[psd_index]]))
                        for psd_index in sorted(psd_data.keys())]
        return psd_controls

    def get_controls(self):
        return self.get_raw_controls() + self.get_psd_controls()


def get_dna_node():
    return cmds.ls(["rl4Embedded_*", "*:rl4Embedded_*"], type="embeddedNodeRL4")[0]


def get_dna_path():
    return cmds.getAttr(get_dna_node()+".dnaFilePath")


def save_targets_by_dna(path):
    dna = Dna(path)
    targets = dna.get_controls()
    json_path = path.replace(".dna", "_targets.json")
    with open(json_path, "w") as fp:
        json.dump(targets, fp, indent=4)


def save_json_data(data, name):
    path = os.path.abspath(__file__+"/../data/%s.json" % name).replace("\\", "/")
    dir_path = os.path.dirname(path)
    if not os.path.isdir(dir_path):
        os.makedirs(dir_path)
    with open(path, "w") as fp:
        json.dump(data, fp, indent=4)


def save_targets():
    save_json_data(Dna(get_dna_path()).get_controls(), "targets")


def save_base_targets():
    save_json_data(Dna(get_dna_path()).get_raw_controls(), "base_targets")


def test_gui_names():
    reader = load_dna(r'C:/Users/mengya/Documents/maya/scripts/lushTools/AIMhServer/scenes/NewMetaHumanIdentity_rl.dna')
    ctrl_count = reader.getGUIControlCount()
    names = []
    for i in range(ctrl_count):
        names.append(reader.getGUIControlName(i))
    save_json_data(names, "base_ctrl")


def doit():
    test_gui_names()
    # save_targets()
