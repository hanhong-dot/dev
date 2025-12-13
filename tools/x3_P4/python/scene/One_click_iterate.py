from PySide2.QtWidgets import *
from PySide2.QtGui import *
import maya.OpenMayaUI as omui
import maya.OpenMaya as om
import json
import maya.cmds as cmds
import maya.mel as mel
import shiboken2
import os

def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return shiboken2.wrapInstance(long(main_window_ptr), QWidget)


class One_Click_Rigging_code():

    def listOutLine(self):
        orig = ['persp', 'perspShape', 'top', 'topShape', 'front', 'frontShape', 'side', 'sideShape']
        new = cmds.ls(dag=True)
        final = [ii for ii in list(set(new) - set(orig)) if cmds.objectType(ii) == 'transform']
        return final
        
    def listTopParent(self, name):
        if cmds.listRelatives(name, p=True):
            return self.listTopParent(cmds.listRelatives(name, p=True,pa=1)[0])
        else:
            return name
            
    def checkSkinAndCopy(self):
        # get mesh target 
        shape = cmds.ls(typ='mesh')
        meshs = []
        if shape:
            for ii in shape:
                parent = cmds.listRelatives(ii,p=1,pa=1)[0]
                meshs.append(parent)
        skin_mesh = []
        non_skin_mesh = []
        if meshs:
            for ii in meshs:
                skincluster = mel.eval('findRelatedSkinCluster {0};'.format(ii))
                if skincluster:
                    skin_mesh.append(ii)
                else:
                    non_skin_mesh.append(ii)
        skin_mesh = list(set(skin_mesh))
        non_skin_mesh = list(set(non_skin_mesh))
        influence = []
        for ii in skin_mesh:
            inf = cmds.skinCluster(ii,q=1,inf=1)
            for hh in inf:
                influence.append(hh)
        influence = list(set(influence))

        # copy skin
        if skin_mesh and non_skin_mesh:
            for ii in non_skin_mesh:
                cmds.skinCluster(influence,ii,tsb=True,mi=20)[0]
                cmds.select(skin_mesh,r=1)
                cmds.select(ii,add=1)
                cmds.copySkinWeights(nm=True,sa='closestPoint')
                
        # reparent files
        old_grp = cmds.listRelatives(skin_mesh[0],p=1,pa=1)[0]
        top_grp = self.listTopParent(old_grp)
        cmds.delete(skin_mesh)
        for ii in non_skin_mesh:
            cmds.parent(ii,old_grp)
        cmds.select(top_grp,r=1)

class One_Click_Item_Tool(QDialog):

    def __init__(self, parent=maya_main_window()):
        super(One_Click_Item_Tool, self).__init__(parent)

        # common setting
        self.setWindowTitle('One Click Item Tool')
        self.resize(280, 250)

        # layout style
        self.mainLayout = QVBoxLayout()
        self.topLayout = QVBoxLayout()
        self.centerLayout = QVBoxLayout()
        self.underLayout = QHBoxLayout()

        # group box
        self.groupBox_a = QGroupBox()
        self.groupBox_a.setTitle('Load Region')
        self.groupBox_a.setLayout(self.topLayout)

        self.groupBox_b = QGroupBox()
        self.groupBox_b.setTitle('Output Region')
        self.groupBox_b.setLayout(self.centerLayout)

        self.groupBox_c = QGroupBox()
        self.groupBox_c.setTitle('Generate Rigging')
        self.groupBox_c.setLayout(self.underLayout)

        # button
        self.button_load_path = QPushButton('Select Old Rigging fbx')
        self.button_load_model = QPushButton('Select New Model fbx')
        self.button_fbx_load = QPushButton('Select New output Fbx path')
        self.button_Apply = QPushButton('iteration Apply')



        # Space Spring
        self.spacerA = QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Layout Control
        self.setLayout(self.mainLayout)
        
        self.topLayout.addWidget(self.button_load_path)
        self.topLayout.addWidget(self.button_load_model)
        self.centerLayout.addWidget(self.button_fbx_load)
        self.underLayout.addWidget(self.button_Apply)
        self.mainLayout.addWidget(self.groupBox_a)
        self.mainLayout.addWidget(self.groupBox_b)
        self.mainLayout.addWidget(self.groupBox_c)
        self.mainLayout.addSpacerItem(self.spacerA)

        # Slot and signal
        self.button_load_path.clicked.connect(self.loadOldRiggingFunc)
        self.button_load_model.clicked.connect(self.loadModelFunc)
        self.button_fbx_load.clicked.connect(self.setOutputFbxPath)
        self.button_Apply.clicked.connect(self.ApplyFbxRigging)


    def showUI(self):
        self.show()

    def closeUI(self):
        self.close()

    def loadOldRiggingFunc(self):
        pathName = cmds.fileDialog2(fileFilter='*.fbx',dialogStyle=2,fm=1)
        if pathName:
            self.button_load_path.setText(pathName[0])
            
    def loadModelFunc(self):
        pathName = cmds.fileDialog2(fileFilter='*.fbx',dialogStyle=2,fm=1)
        if pathName:
            self.button_load_model.setText(pathName[0])

    def setOutputFbxPath(self):
        pathName = cmds.fileDialog2(fileFilter='selectdir', dialogStyle=2, fm=2, cap='SetFbxOutput', okc='selectDir')
        if pathName:
            self.button_fbx_load.setText(pathName[0])

    def ApplyFbxRigging(self):
        old_f = self.button_load_path.text()
        new_m = self.button_load_model.text()
        fbx_out_path = self.button_fbx_load.text() + '/'
        
        
        if 'Select' not in old_f and 'Select' not in new_m and 'Select' not in fbx_out_path:
            cmds.file(f=True, new=True)
            
            cmds.file(old_f, i=True, iv=True, op='fbx')
            cmds.file(new_m, i=True, iv=True, op='fbx',mergeNamespacesOnClash=False,ns='new_')
            
            fileName = old_f.split('/')[-1]
            
            click_func = One_Click_Rigging_code()
            click_func.checkSkinAndCopy()
            cmds.namespace(removeNamespace=":new_", mergeNamespaceWithRoot = True)
            cmds.file(fbx_out_path + fileName, f=True, es=True, op='fbx', type='FBX export', pr=True)
            
            cmds.file(f=True, new=True)
            cmds.headsUpMessage('generate over!',t=2)
        else:
            cmds.warning('please Select two fbx!')


if __name__ == "__main__":
    try:
        One_Click_item_UI.deleteLater()
        One_Click_item_UI = One_Click_Item_Tool()
        One_Click_item_UI.showUI()
    except:
        One_Click_item_UI = One_Click_Item_Tool()
        One_Click_item_UI.show()
