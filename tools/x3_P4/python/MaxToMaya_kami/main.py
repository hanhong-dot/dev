from maya import cmds
from .main_kami import mainWindow as kami_mainWindow
from PySide2.QtWidgets import *

class mainWindow(kami_mainWindow):


    def __init__(self):
        kami_mainWindow.__init__(self)
        self.ui.setObjectName("LushMaxToMaya")
        self.global_bake_but = QPushButton("BakeGlobalControl")
        self.ui.layout().addWidget(self.global_bake_but)
        self.global_bake_but.clicked.connect(self.bake_global)

    def bake_global(self):
        mainWindow.BakeImplement(self)
        timemin = float(self.ui.time_min.text())
        timemax = float(self.ui.time_max.text())
        st = int(round(timemin))
        et = int(round(timemax))
        NameSpace = str(self.ui.namespace_combo.currentText())
        nametext = NameSpace.split(':')[0]+":"
        FKcon = ["FKShoulder_L", "FKShoulder_R", "FKHead_M"]
        FKcon = [nametext + ':' + ii for ii in FKcon]
        cmds.select(FKcon)
        for i in range(st, et+1):
            cmds.currentTime(i)
            for fk in FKcon:
                if not cmds.objExists(fk):
                    continue
                if not cmds.objExists(fk+".Global"):
                    continue
                cmds.setAttr(fk+".Global", 0)
                m = cmds.xform(fk, ws=1, q=1, m=1)
                cmds.setAttr(fk+".Global", 10)
                cmds.xform(fk, ws=1, m=m)
                cmds.setKeyframe(fk)


maxtomaya = None


def load_ui():
    global maxtomaya
    for i in range(100):
        if cmds.window("LushMaxToMaya", q=1, ex=1):
            cmds.deleteUI("LushMaxToMaya")
    maxtomaya = mainWindow()
    maxtomaya.showUI()


def doit():
    global maxtomaya
    load_ui()
    maxtomaya.ui.namespace_combo.setCurrentIndex(7)
    maxtomaya.ui.bake_change_btn.setCurrentIndex(1)
    maxtomaya.ui.time_min.setText(str(1536))
    maxtomaya.ui.time_max.setText(str(1537))
    maxtomaya.bake_global()
    ""
