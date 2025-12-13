from PySide2 import QtGui
from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtUiTools
import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMayaUI as omui
import maya.OpenMaya as om
import shiboken2

qtVersion = cmds.about(qtVersion=True)

import refreshSkin_kami as ref_k

uifile_path = ref_k.__path__[0].replace('\\', '/') + '/ui/window.ui'
om.MGlobal.displayInfo('this plugin path are {}'.format(ref_k.__path__[0].replace('\\', '/')))


def loadui(uifile_path):
    uifile = QtCore.QFile(uifile_path)
    uifile.open(QtCore.QFile.ReadOnly)
    uiWindow = QtUiTools.QUiLoader().load(uifile, parentWidget=maya_main_window())
    uifile.close()
    return uiWindow


def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return shiboken2.wrapInstance(long(main_window_ptr), QtWidgets.QWidget)

class mainWindows():
    def __init__(self):
        self.ui = loadui(uifile_path)
        self.ui.setWindowFlags(QtCore.Qt.Dialog)
        Currentpoint = QtGui.QCursor.pos()

        self.ui.move(Currentpoint.x(), Currentpoint.y())
        self.ui.ghost_btm.clicked.connect(self.CopySkinJointFunction_kami)
        self.ui.ref_btn.clicked.connect(self.refreshSkinCluster_kami)
        self.ui.getnum_btn.clicked.connect(self.jointNumTotal)
        self.ui.mocap_ct_btn.clicked.connect(self.CreateMocapFunction_kami)
        self.ui.mocap_dl_btn.clicked.connect(self.deleteMocapfunc)

    def showUI(self):
        self.ui.show()

    def closeUI(self):
        self.ui.close()
        self.ui.deleteLater()

    def refreshSkinCluster_kami(self, RootName='Roots'):
        sel = cmds.ls(sl=True)
        if sel:
            RootName = self.ui.tex_root.text()
            if RootName:
                for ii in sel:
                    copy = cmds.duplicate(ii)[0]
                    tempsel = cmds.select(RootName, r=True, hi=True)
                    joints = cmds.ls(sl=True)
                    cmds.skinCluster(joints, copy, dr=4, mi=16)
                    cmds.copySkinWeights(ii, copy, sa='closestPoint', ia='closestJoint', nm=True)
                    cmds.select(copy, r=True)
                    mel.eval('removeUnusedInfluences')
                    if self.ui.checkBox1.isChecked():
                        cmds.delete(ii)
                        cmds.rename(copy, ii)
                    cmds.select(cl=True)

    def renameMultiJoint_kami(self, sel):
        tex = self.ui.ghostPreLine.text()
        if tex:
            sel.reverse()
            for ii in sel:
                if cmds.objectType(ii) == 'joint':
                    if '|' in ii:
                        newName = tex + ii.split('|')[-1]
                        cmds.rename(ii, newName)
                    else:
                        newName = tex + ii
                        RootName = cmds.rename(ii, newName)
                        if '1' in RootName:
                            NewRootName = RootName.replace('1', '')
                            FinalName = cmds.rename(RootName, NewRootName)
                            return FinalName
                else:
                    cmds.delete(ii)
        else:
            cmds.warning('prefix text empty!')

    def connectOldtoSkinJoint_kami(self, oldname):
        newTex = self.ui.ghostPreLine.text()
        matrixName = self.ui.Matrix_root_ipt.text()
        for ii in oldname:
            if cmds.objExists(newTex + ii):
                newname = newTex + ii
                if ii == matrixName:
                    deMatrix = cmds.createNode('decomposeMatrix', n='Root_decomposeMatrix_kami')
                    muiltyMatrix = cmds.createNode('multMatrix', n='Root_muiltycomposeMatrix_kami')
                    zerotest = cmds.createNode('multiplyDivide', n='Root_zeroLock_kami')
                    cmds.connectAttr(ii + '.worldMatrix[0]', muiltyMatrix + '.matrixIn[0]')
                    cmds.connectAttr(newname + '.parentInverseMatrix', muiltyMatrix + '.matrixIn[1]')
                    cmds.connectAttr(muiltyMatrix + '.matrixSum', deMatrix + '.inputMatrix')
                    cmds.connectAttr(deMatrix + '.outputTranslateX', newname + '.translateX')
                    cmds.connectAttr(deMatrix + '.outputTranslateY', newname + '.translateY')
                    cmds.connectAttr(deMatrix + '.outputTranslateZ', newname + '.translateZ')
                    cmds.connectAttr(deMatrix + '.outputRotateX', newname + '.rotateX')
                    cmds.connectAttr(deMatrix + '.outputRotateY', newname + '.rotateY')
                    cmds.connectAttr(deMatrix + '.outputRotateZ', newname + '.rotateZ')
                    cmds.connectAttr(deMatrix + '.outputScaleX', newname + '.scaleX')
                    cmds.connectAttr(deMatrix + '.outputScaleY', newname + '.scaleY')
                    cmds.connectAttr(deMatrix + '.outputScaleZ', newname + '.scaleZ')
                    cmds.connectAttr(zerotest + '.output', newname + '.jointOrient')
                    om.MGlobal.displayInfo('special Matrix Root constructing over!!')
                else:
                    try:
                        cmds.connectAttr(ii + '.translateX', newname + '.translateX')
                        cmds.connectAttr(ii + '.translateY', newname + '.translateY')
                        cmds.connectAttr(ii + '.translateZ', newname + '.translateZ')

                        cmds.connectAttr(ii + '.rotateX', newname + '.rotateX')
                        cmds.connectAttr(ii + '.rotateY', newname + '.rotateY')
                        cmds.connectAttr(ii + '.rotateZ', newname + '.rotateZ')

                        cmds.connectAttr(ii + '.scaleX', newname + '.scaleX')
                        cmds.connectAttr(ii + '.scaleY', newname + '.scaleY')
                        cmds.connectAttr(ii + '.scaleZ', newname + '.scaleZ')

                        cmds.connectAttr(ii + '.jointOrient', newname + '.jointOrient')

                    except:
                        cmds.warning('{0} has something problem!!!'.format(str(ii)))

    def CopySkinJointFunction_kami(self):
        sel = cmds.ls(sl=True)
        if sel:
            if cmds.objectType(sel[0]) == 'joint':
                newSel = cmds.duplicate(sel[0], rr=True)[0]
                newSel = self.listLongName(newSel)
                finalname = self.renameMultiJoint_kami(newSel)
                cmds.select(finalname, r=True, hi=True)
                finalnames = cmds.ls(sl=True)
                for ii in finalnames:
                    self.disconnectSet(ii)
                inverscales = cmds.listConnections(finalname, d=True, s=False, p=True)
                for ii in inverscales:
                    cmds.disconnectAttr(finalname + '.scale', ii)
                cmds.select(sel[0], r=True, hi=True)
                oldSel = cmds.ls(sl=True)
                self.connectOldtoSkinJoint_kami(oldSel)
                cmds.select(cl=True)

    def CreateMocapFunction_kami(self):
        config = ['muscleDriver', 'corrective', 'rivet', 'Tongue', 'Eye', 'Teeth', 'Jaw']
        oldTest = cmds.ls('*_offset_paper_grp')
        if len(oldTest) == 0:
            if cmds.objExists('Root_M') and cmds.objectType('Root_M') == 'joint':
                newSel = cmds.duplicate('Root_M', rr=True)[0]
                newSel = self.listLongName(newSel)
                final = self.renameMultiJoint_kami(newSel)
                tex = self.ui.ghostPreLine.text()
                offsetgrp = cmds.group(n=tex + 'Zero_offset_paper_grp', em=True)
                centergrp = cmds.group(n=tex + 'center_offset_paper_grp', em=True)
                cmds.matchTransform(centergrp, final, pos=True)
                cmds.parent(final, centergrp)
                cmds.parent(centergrp, offsetgrp)
                cmds.select(final, r=True, hi=True)
                mocap_bone = cmds.ls(sl=True)
                dodelete = [cc for ii in config for cc in mocap_bone if ii in cc]
                simple_bs = list(set(mocap_bone) - set(dodelete))
                cmds.delete(dodelete)
                self.connectFKcontrol(tex, simple_bs)
                om.MGlobal.displayInfo('Mocap Created!')
        else:
            cmds.warning('please delete old mocap system!')

    def deleteMocapfunc(self):
        sel = cmds.ls('*_Zero_offset_paper_grp')
        if sel:
            cmds.delete(sel)
            om.MGlobal.displayInfo('deleted mocap')

    def disconnectSet(self, bone):
        sel = cmds.listConnections(bone + '.instObjGroups[0]', d=True, s=False, p=True)
        if sel:
            for ii in sel:
                cmds.disconnectAttr(bone + '.instObjGroups[0]', ii)

    def disconnectNewVertion(self, attrFullname):
        connect = cmds.listConnections(attrFullname, d=False, s=True, p=True)
        if connect:
            cmds.disconnectAttr(connect[0], attrFullname)

    def connectFKcontrol(self, pre, bone):
        if bone:
            for ii in bone:
                self.disconnectSet(ii)
                name = ii.split(pre)[1]
                if 'Part' not in name:
                    if name != 'Root_M':
                        if cmds.objExists('FKExtra' + name):
                            loc = self.createOffsetLocator(ii)
                            self.disconnectNewVertion('FKExtra' + name + '.tx')
                            self.disconnectNewVertion('FKExtra' + name + '.ty')
                            self.disconnectNewVertion('FKExtra' + name + '.tz')
                            self.disconnectNewVertion('FKExtra' + name + '.rx')
                            self.disconnectNewVertion('FKExtra' + name + '.ry')
                            self.disconnectNewVertion('FKExtra' + name + '.rz')

                            cmds.connectAttr(loc + '.tx', 'FKExtra' + name + '.tx')
                            cmds.connectAttr(loc + '.ty', 'FKExtra' + name + '.ty')
                            cmds.connectAttr(loc + '.tz', 'FKExtra' + name + '.tz')
                            cmds.connectAttr(ii + '.rx', 'FKExtra' + name + '.rx')
                            cmds.connectAttr(ii + '.ry', 'FKExtra' + name + '.ry')
                            cmds.connectAttr(ii + '.rz', 'FKExtra' + name + '.rz')
                    else:
                        loc = self.createOffsetLocator_root(ii)
                        self.disconnectNewVertion('RootExtraX_M.tx')
                        self.disconnectNewVertion('RootExtraX_M.ty')
                        self.disconnectNewVertion('RootExtraX_M.tz')
                        self.disconnectNewVertion('FKExtraRoot_M.rx')
                        self.disconnectNewVertion('FKExtraRoot_M.ry')
                        self.disconnectNewVertion('FKExtraRoot_M.rz')

                        cmds.connectAttr(loc + '.tx', 'RootExtraX_M.tx')
                        cmds.connectAttr(loc + '.ty', 'RootExtraX_M.ty')
                        cmds.connectAttr(loc + '.tz', 'RootExtraX_M.tz')
                        cmds.connectAttr(loc + '.rx', 'RootExtraX_M.rx')
                        cmds.connectAttr(loc + '.ry', 'RootExtraX_M.ry')
                        cmds.connectAttr(loc + '.rz', 'RootExtraX_M.rz')

    def createOffsetLocator(self, bone):
        loc = cmds.spaceLocator(n=bone + '_offset_loc')[0]
        cmds.setAttr(loc + '.localScaleX', 0.1)
        cmds.setAttr(loc + '.localScaleY', 0.1)
        cmds.setAttr(loc + '.localScaleZ', 0.1)
        grp = cmds.group(n=bone + '_offset_grp', em=True)
        cmds.parent(loc, grp)
        cmds.matchTransform(grp, bone)
        parent = cmds.listRelatives(bone, p=True)
        cmds.parent(grp, parent)
        cmds.pointConstraint(bone, loc, mo=True)
        return loc

    def createOffsetLocator_root(self, bone):
        loc = cmds.spaceLocator(n=bone + '_offset_loc')[0]
        cmds.setAttr(loc + '.localScaleX', 0.1)
        cmds.setAttr(loc + '.localScaleY', 0.1)
        cmds.setAttr(loc + '.localScaleZ', 0.1)
        grp = cmds.group(n=bone + '_offset_grp', em=True)
        cmds.parent(loc, grp)
        cmds.matchTransform(grp, 'RootExtraX_M')
        parent = cmds.listRelatives(bone, p=True)
        cmds.parent(grp, parent)
        cmds.parentConstraint(bone, loc, mo=True)
        return loc

    def listLongName(self, root):
        cmds.select(root, r=True, hi=True)
        child = cmds.ls(sl=True, fl=True)
        return child

    def jointNumTotal(self):
        sel = cmds.ls(sl=True)
        joint = []
        if sel:
            for ii in sel:
                if cmds.objectType(ii) == 'joint':
                    joint.append(ii)
            self.ui.jointNumTex.setText(str(len(joint)))

def refreshSkin_kami_ui():
    global refreshSkin
    try:
        refreshSkin.close()
    except:
        pass
    refreshSkin = mainWindows()
    refreshSkin.showUI()