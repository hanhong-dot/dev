import MaxToMaya_kami as mmk
import maya.cmds as cmds
import maya.OpenMayaUI as omui
import maya.OpenMaya as om
import maya.mel as mel

from PySide2 import QtGui
from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtUiTools
import shiboken2

uifile_path = mmk.__path__[0].replace('\\', '/') + '/ui/window.ui'


def get_host_app():
    try:
        main_window = QtWidgets.QApplication.allWidgets()[0]
        while True:
            last_win = main_window.parent()
            if last_win:
                main_window = last_win
            else:
                break
        return main_window
    except Exception as e:
        print (e)

def loadui(uifile_path):
    uifile = QtCore.QFile(uifile_path)
    uifile.open(QtCore.QFile.ReadOnly)
    uiWindow = QtUiTools.QUiLoader().load(uifile, parentWidget = QtWidgets.QMainWindow(get_host_app()))
    uifile.close()
    return uiWindow


class mainWindow():
    def __init__(self):
        self.ui = loadui(uifile_path)
        self.ui.setWindowFlags(QtCore.Qt.Dialog)

        int_Validator = QtGui.QIntValidator()
        self.ui.time_min.setValidator(int_Validator)
        self.ui.time_max.setValidator(int_Validator)

        self.ui.bakeControl_btn.clicked.connect(self.BakeImplement)
        self.ui.bakeJoint_btn.clicked.connect(self.bakeToJoint)
        self.ui.Resetoft_btn.clicked.connect(self.ResetToOffset)
        self.ui.getRange_btn.clicked.connect(self.getKeyRange)

        self.listNamespaceAdd()

    def showUI(self):
        self.ui.show()

    def closeUI(self):
        self.ui.close()
        self.ui.deleteLater()

    def modifySPtext(self):
        sels = cmds.ls('*FBXASC032*')
        if sels:
            for ii in sels:
                if cmds.objectType(ii) == 'joint':
                    newName = ii.replace('FBXASC032', '_')
                    cmds.rename(ii, newName)

    def MirrorConstrainFunctions(self, offset):
        cmds.orientConstraint('Bip001_' + offset + '_Thigh', 'FKHip_' + offset, mo=True, n='Hip_' + offset + '_max3d')
        cmds.orientConstraint('Bip001_' + offset + '_Calf', 'FKKnee_' + offset, mo=True, n='Knee_' + offset + '_max3d')
        cmds.orientConstraint('Bip001_' + offset + '_Foot', 'FKAnkle_' + offset, mo=True, n='Foot_' + offset + '_max3d')
        cmds.orientConstraint('Bip001_' + offset + '_Toe0', 'FKToes_' + offset, mo=True, n='Toe_' + offset + '_max3d')

        cmds.orientConstraint('Bip001_' + offset + '_Clavicle', 'FKScapula_' + offset, mo=True,
                              n='Scapula_' + offset + '_max3d')
        cmds.orientConstraint('Bip001_' + offset + '_UpperArm', 'FKShoulder_' + offset, mo=True,
                              n='Shoulder_' + offset + '_max3d')
        cmds.orientConstraint('Bip001_' + offset + '_Forearm', 'FKElbow_' + offset, mo=True,
                              n='Elbow_' + offset + '_max3d')
        cmds.orientConstraint('Bip001_' + offset + '_Hand', 'FKWrist_' + offset, mo=True,
                              n='Wrist_' + offset + '_max3d')

        cmds.orientConstraint('Bip001_' + offset + '_Finger0', 'FKThumbFinger1_' + offset, mo=True,
                              n='Thumb1_' + offset + '_max3d')
        cmds.orientConstraint('Bip001_' + offset + '_Finger01', 'FKThumbFinger2_' + offset, mo=True,
                              n='Thumb2_' + offset + '_max3d')
        cmds.orientConstraint('Bip001_' + offset + '_Finger02', 'FKThumbFinger3_' + offset, mo=True,
                              n='Thumb3_' + offset + '_max3d')

        cmds.orientConstraint('Bip001_' + offset + '_Finger1', 'FKIndexFinger1_' + offset, mo=True,
                              n='Index1_' + offset + '_max3d')
        cmds.orientConstraint('Bip001_' + offset + '_Finger11', 'FKIndexFinger2_' + offset, mo=True,
                              n='Index2_' + offset + '_max3d')
        cmds.orientConstraint('Bip001_' + offset + '_Finger12', 'FKIndexFinger3_' + offset, mo=True,
                              n='Index3_' + offset + '_max3d')

        cmds.orientConstraint('Bip001_' + offset + '_Finger2', 'FKMiddleFinger1_' + offset, mo=True,
                              n='Middle1_' + offset + '_max3d')
        cmds.orientConstraint('Bip001_' + offset + '_Finger21', 'FKMiddleFinger2_' + offset, mo=True,
                              n='Middle2_' + offset + '_max3d')
        cmds.orientConstraint('Bip001_' + offset + '_Finger22', 'FKMiddleFinger3_' + offset, mo=True,
                              n='Middle3_' + offset + '_max3d')

        cmds.orientConstraint('Bip001_' + offset + '_Finger3', 'FKRingFinger1_' + offset, mo=True,
                              n='Ring1_' + offset + '_max3d')
        cmds.orientConstraint('Bip001_' + offset + '_Finger31', 'FKRingFinger2_' + offset, mo=True,
                              n='Ring2_' + offset + '_max3d')
        cmds.orientConstraint('Bip001_' + offset + '_Finger32', 'FKRingFinger3_' + offset, mo=True,
                              n='Ring3_' + offset + '_max3d')

        cmds.orientConstraint('Bip001_' + offset + '_Finger4', 'FKPinkyFinger1_' + offset, mo=True,
                              n='Pinky1_' + offset + '_max3d')
        cmds.orientConstraint('Bip001_' + offset + '_Finger41', 'FKPinkyFinger2_' + offset, mo=True,
                              n='Pinky2_' + offset + '_max3d')
        cmds.orientConstraint('Bip001_' + offset + '_Finger42', 'FKPinkyFinger3_' + offset, mo=True,
                              n='Pinky3_' + offset + '_max3d')

    def centerConstrainFunctions(self):
        root = cmds.xform('Bip001', q=True, ws=True, t=True)
        if cmds.objExists('world_max3d_locator'):
            pass
        else:
            loc = cmds.spaceLocator(n='world_max3d_locator')[0]
            cmds.xform(loc, ws=True, t=(root[0], root[1], root[2]))
        axia = []
        if self.ui.center_x.isChecked() == False:
            axia.append('x')
        if self.ui.center_y.isChecked() == False:
            axia.append('y')
        if self.ui.center_z.isChecked() == False:
            axia.append('z')

        if len(axia) == 1:
            cmds.pointConstraint('Bip001', loc, mo=True, n='center_max3d_test', skip=axia[0])
        elif len(axia) == 2:
            cmds.pointConstraint('Bip001', loc, mo=True, n='center_max3d_test', skip=(axia[0], axia[1]))
        elif len(axia) == 3:
            cmds.pointConstraint('Bip001', loc, mo=True, n='center_max3d_test', skip=(axia[0], axia[1], axia[2]))
        else:
            # spare im
            cmds.pointConstraint('Bip001', loc, mo=True, n='center_max3d_test')

        cmds.pointConstraint(loc, 'RootX_M', mo=True, n='root_point_max3d')
        cmds.orientConstraint('Bip001', 'RootX_M', mo=True, n='root_max3d')
        cmds.orientConstraint('Bip001_Spine', 'FKSpine1_M', mo=True, n='Spine_max3d')
        cmds.orientConstraint('Bip001_Spine1', 'FKSpine2_M', mo=True, n='Spine1_max3d')
        cmds.orientConstraint('Bip001_Spine2', 'FKSpine3_M', mo=True, n='Spine2_max3d')
        cmds.orientConstraint('Bip001_Spine3', 'FKChest_M', mo=True, n='Spine3_max3d')
        cmds.orientConstraint('Bip001_Neck', 'FKNeck_M', mo=True, n='neck_max3d')
        cmds.orientConstraint('Bip001_Head', 'FKHead_M', mo=True, n='head_max3d')

    def deleteConstrain(self):
        sels = cmds.ls('*max3d*', 'hikTransferTemp*')
        if sels:
            cmds.delete(sels)

    def bakeToConstrain(self):
        self.modifySPtext()
        timemin = float(self.ui.time_min.text())
        timemax = float(self.ui.time_max.text())
        cmds.currentTime(timemin)
        if cmds.objExists('Bip001'):
            self.centerConstrainFunctions()
            self.MirrorConstrainFunctions('L')
            self.MirrorConstrainFunctions('R')
            fkcon = []
            sels = cmds.sets('ControlSet', q=True)
            if sels:
                for ii in sels:
                    shape = cmds.pickWalk(ii, d='down')
                    if cmds.objectType(shape) == 'nurbsCurve' and 'FK' in ii and 'IK' not in ii:
                        fkcon.append(ii)
                fkcon.append('RootX_M')
                try:
                    fkcon.remove('FKRoot_M')
                except:
                    pass
                cmds.bakeResults(fkcon, sm=True, t=(timemin, timemax), sb=1)
                self.deleteConstrain()
        else:
            cmds.warning('Bip001 Non-existent!!!')

    def bakeToJoint(self):
        self.modifySPtext()
        timemin = float(self.ui.time_min.text())
        timemax = float(self.ui.time_max.text())
        cmds.currentTime(timemin)
        self.centerConstrainFunctions()
        self.MirrorConstrainFunctions('L')
        self.MirrorConstrainFunctions('R')
        joint = []
        sl = cmds.select('Root_M', hi=True, r=True)
        sels = cmds.ls(sl=True)
        if sels:
            for ii in sels:
                if cmds.objectType(
                        ii) == 'joint' and 'Head_rivet' not in ii and 'Eye' not in ii and 'Teeth' not in ii and 'Tongue' not in ii:
                    joint.append(ii)
            # print joint
            cmds.bakeResults(joint, sm=True, t=(timemin, timemax), sb=1)
            self.deleteConstrain()
            
    def getKeyRange(self):
        # st = int(round(cmds.playbackOptions(q=1, ast=1)))
        # et = int(round(cmds.playbackOptions(q=1, aet=1)))
        st = int(round(cmds.playbackOptions(q=1, min=1)))
        et = int(round(cmds.playbackOptions(q=1, max=1)))
        self.ui.time_min.setText(str(st))
        self.ui.time_max.setText(str(et))
        # keyframe = cmds.ls(typ='animCurveTL') + cmds.ls(typ='animCurveTU') + cmds.ls(typ='animCurveTA')
        # range_list = [cmds.keyframe(ii,q=True) for ii in keyframe if keyframe]
        # if range_list:
        #     result = sorted(list(set(sum(range_list,[]))))
        #     self.ui.time_min.setText(str(result[0]))
        #     self.ui.time_max.setText(str(result[-1]))

    def ResetToOffset(self):
        timemin = float(self.ui.time_min.text())
        timemax = float(self.ui.time_max.text())
        cmds.currentTime(timemin)
        root = cmds.xform('RootX_M', q=True, ws=True, t=True)
        # print 'root'
        # print root
        loc = cmds.spaceLocator(n='reset_max3d_locator')[0]
        cmds.xform(loc, ws=True, t=(root[0], root[1], root[2]))
        axia = []
        if self.ui.center_x.isChecked() == False:
            axia.append('x')
        if self.ui.center_y.isChecked() == False:
            axia.append('y')
        if self.ui.center_z.isChecked() == False:
            axia.append('z')

        if len(axia) == 1:
            pointC = cmds.pointConstraint('RootX_M', loc, mo=True, n='reset_max3d_test', skip=axia[0])
        elif len(axia) == 2:
            pointC = cmds.pointConstraint('RootX_M', loc, mo=True, n='reset_max3d_test', skip=(axia[0], axia[1]))
        elif len(axia) == 3:
            pointC = cmds.pointConstraint('RootX_M', loc, mo=True, n='reset_max3d_test',
                                          skip=(axia[0], axia[1], axia[2]))
        else:
            # spare im
            pointC = cmds.pointConstraint('RootX_M', loc, mo=True, n='reset_max3d_test')

        cmds.bakeResults(loc, sm=True, t=(timemin, timemax), sb=1)
        cmds.delete(pointC)
        cmds.currentTime(timemin)
        self.DeleteInput('RootX_M.translateX')
        self.DeleteInput('RootX_M.translateY')
        self.DeleteInput('RootX_M.translateZ')
        pointC = cmds.pointConstraint(loc, 'RootX_M', mo=True, n='resetSecond_max3d_test')
        cmds.bakeResults('RootX_M', sm=True, t=(timemin, timemax), sb=1)
        cmds.delete(pointC)
        cmds.delete(loc)

    def DeleteInput(self, attr):
        sel = cmds.listConnections(attr, p=True)[0]
        cmds.disconnectAttr(sel, attr)

    def exchangeHIKtoFk(self):
        timemin = float(self.ui.time_min.text())
        timemax = float(self.ui.time_max.text())
        cmds.currentTime(timemin)
        FKcon = [u'FKHip_L',
                 u'FKToes_R',
                 u'FKAnkle_R',
                 u'FKKnee_R',
                 u'FKHip_R',
                 u'FKMiddleFinger1_R',
                 u'FKToes_L',
                 u'FKAnkle_L',
                 u'FKKnee_L',
                 u'FKIndexFinger3_L',
                 u'FKIndexFinger2_L',
                 u'FKIndexFinger1_L',
                 u'FKThumbFinger3_L',
                 u'FKPinkyFinger3_L',
                 u'FKPinkyFinger2_L',
                 u'FKPinkyFinger1_L',
                 u'FKCup_L',
                 u'FKRingFinger1_R',
                 u'FKPinkyFinger3_R',
                 u'FKPinkyFinger2_R',
                 u'FKPinkyFinger1_R',
                 u'FKElbow_R',
                 u'FKShoulder_R',
                 u'FKRingFinger3_R',
                 u'FKRingFinger2_R',
                 u'FKThumbFinger3_R',
                 u'FKThumbFinger2_R',
                 u'FKThumbFinger1_R',
                 u'FKMiddleFinger3_R',
                 u'FKMiddleFinger2_R',
                 u'FKCup_R',
                 u'FKIndexFinger3_R',
                 u'FKIndexFinger2_R',
                 u'FKIndexFinger1_R',
                 u'FKRingFinger3_L',
                 u'FKRingFinger2_L',
                 u'FKRingFinger1_L',
                 u'FKWrist_L',
                 u'FKElbow_L',
                 u'FKShoulder_L',
                 u'FKScapula_R',
                 u'FKWrist_R',
                 u'FKSpine1_M',
                 u'FKRoot_M',
                 u'FKScapula_L',
                 u'FKNeck_M',
                 u'FKNeckPart1_M',
                 u'FKHead_M',
                 u'FKChest_M',
                 u'FKSpine3_M',
                 u'FKSpine2_M',
                 u'FKThumbFinger2_L',
                 u'FKThumbFinger1_L',
                 u'FKMiddleFinger3_L',
                 u'FKMiddleFinger2_L',
                 u'FKMiddleFinger1_L',
                 u'RootX_M',
                 u'FKPinkyFinger0_L',
                 u'FKRingFinger0_L',
                 u'FKMiddleFinger0_L',
                 u'FKIndexFinger0_L',
                 u'FKPinkyFinger0_R',
                 u'FKRingFinger0_R',
                 u'FKMiddleFinger0_R',
                 u'FKIndexFinger0_R',
                 u'FKToe_a_0_R',
                 u'FKToe_a_1_R',
                 u'FKToe_b_0_R',
                 u'FKToe_b_1_R',
                 u'FKToe_b_2_R',
                 u'FKToe_c_0_R',
                 u'FKToe_c_1_R',
                 u'FKToe_c_2_R',
                 u'FKToe_d_0_R',
                 u'FKToe_d_1_R',
                 u'FKToe_d_2_R',
                 u'FKToe_e_0_R',
                 u'FKToe_e_1_R',
                 u'FKToe_e_2_R',
                 u'FKToe_a_0_L',
                 u'FKToe_a_1_L',
                 u'FKToe_b_0_L',
                 u'FKToe_b_1_L',
                 u'FKToe_b_2_L',
                 u'FKToe_c_0_L',
                 u'FKToe_c_1_L',
                 u'FKToe_c_2_L',
                 u'FKToe_d_0_L',
                 u'FKToe_d_1_L',
                 u'FKToe_d_2_L',
                 u'FKToe_e_0_L',
                 u'FKToe_e_1_L',
                 u'FKToe_e_2_L'
                 ]

        fk_js = [u'FKAnkle_L', u'FKAnkle_R', u'FKWrist_L', u'FKWrist_R']
        ik_cons = [u'IKLeg_L', u'IKLeg_R', u'IKArm_L', u'IKArm_R']
        ik_vector = [u'PoleLeg_L', u'PoleLeg_R', u'PoleArm_L', u'PoleArm_R']

        NameSpace = str(self.ui.namespace_combo.currentText())

        if ':' in NameSpace:
            nametext = NameSpace.split(':')[0]
            FKcon = [nametext + ':' + ii for ii in FKcon]
            fk_js = [nametext + ':' + ii for ii in fk_js]
            ik_cons = [nametext + ':' + ii for ii in ik_cons]
            ik_vector = [nametext + ':' + ii for ii in ik_vector]
            
        # print FKcon

        constrains = []
        locs = []
        for item in FKcon:
            if 'FK' in item:
                extra = item.replace('FK', 'FKExtra')
            elif 'RootX' in item:
                extra = item.replace('Root', 'RootExtra')
            if cmds.objExists(extra):
                parent = cmds.listRelatives(extra, p=True)[0]
                loc = cmds.spaceLocator(n=item + '_fixOrder_locs')[0]
                cmds.parent(loc, parent)
                mel.eval('ResetTransformations("{0}")'.format(loc))
                cmds.setAttr(loc + '.rotateOrder', cmds.getAttr(item + '.rotateOrder'))
                cons = cmds.parentConstraint(extra, loc)[0]
                constrains.append(cons)
                locs.append(loc)

        if locs:
            # 2023-12-19
            # add function  setAttr "FKNeck_M.bend_atte" 1 at bake pre
            
            # 2024-08-07
            # add function  setAttr "FKHead_M.autoTwist" 0 at bake pre
            for gg in FKcon:
                if 'FKNeck_M' in gg:
                    neck_sub = gg
                if 'FKHead_M' in gg:
                    head_auto_twist = gg

            if neck_sub:
                if cmds.objExists(neck_sub + '.bend_atte'):
                    cmds.setAttr(neck_sub + '.bend_atte',1)
            if head_auto_twist:
                if cmds.objExists(head_auto_twist + '.autoTwist'):
                    cmds.setAttr(head_auto_twist + '.autoTwist',0)

            cmds.bakeResults(locs, sm=True, t=(timemin, timemax), sb=1)
            cmds.delete(constrains)
            for ll in locs:
                mainFK = ll.split('_fixOrder_locs')[0]
                cmds.connectAttr(ll + '.translateX', mainFK + '.translateX')
                cmds.connectAttr(ll + '.translateY', mainFK + '.translateY')
                cmds.connectAttr(ll + '.translateZ', mainFK + '.translateZ')

                cmds.connectAttr(ll + '.rotateX', mainFK + '.rotateX')
                cmds.connectAttr(ll + '.rotateY', mainFK + '.rotateY')
                cmds.connectAttr(ll + '.rotateZ', mainFK + '.rotateZ')

            FKCon_ex = []
            for dd in FKcon:
                if cmds.objExists(dd):
                    FKCon_ex.append(dd)
                else:
                    cmds.warning('{} Non-Ex !! please check your scenes'.format(dd))

            cmds.bakeResults(FKCon_ex, sm=True, t=(timemin, timemax), sb=1)
            cmds.delete(locs)
            self.cleanMocapjoint()

            if self.ui.ik_check_box.isChecked():
                self.BakeIKcontroler(fk_js, ik_cons, ik_vector, timemin, timemax)
            else:
                om.MGlobal.displayInfo('Bake HIK to maya already over!!!')
        else:
            cmds.warning('Target Non-excited, please check you bake running mode')

    def cleanMocapjoint(self):
        NameSpace = str(self.ui.namespace_combo.currentText())
        if ':' in NameSpace:
            nametext = NameSpace.split(':')[0]
            root = [nametext + ':' + 'Root_MoCap_M', nametext + ':' + 'Mocap_Root_M']
        else:
            root = ['Root_MoCap_M', 'Mocap_Root_M']
        for uu in root:
            if cmds.objExists(uu):
                joint = [uu]
                sel = cmds.listRelatives(uu,ad=True)
                for ii in sel:
                    if cmds.objectType(ii) == 'joint':
                        joint.append(ii)
                for ii in joint:
                    self.disConnnectAttr(ii + '.tx')
                    self.disConnnectAttr(ii + '.ty')
                    self.disConnnectAttr(ii + '.tz')
                    self.disConnnectAttr(ii + '.rx')
                    self.disConnnectAttr(ii + '.ry')
                    self.disConnnectAttr(ii + '.rz')
                cmds.joint(uu, e=True, apa=True, ch=True)
                cmds.setAttr(uu + '.translateX', 0)
                cmds.setAttr(uu + '.translateY', 0)
                cmds.setAttr(uu + '.translateZ', 0)
            else:
                cmds.warning('{0} Non-Ex , check it!!'.format(uu))

    def bakeToConstrain_Hik(self):
        timemin = float(self.ui.time_min.text())
        timemax = float(self.ui.time_max.text())
        cmds.currentTime(timemin)

    def BakeImplement(self):
        num = self.ui.bake_change_btn.currentIndex()
        if num == 0:
            self.bakeToConstrain()
        elif num == 1:
            self.exchangeHIKtoFk()

    def disConnnectAttr(self, attr):
        source = cmds.listConnections(attr, p=True,s=True,d=False)
        if source:
            cmds.disconnectAttr(source[0], attr)
                    
    def nameSpaceFind(self):
        current = set(cmds.namespaceInfo(lon=True))
        defult = set(['UI','shared'])
        if len(list(current - defult)) != 0:
            return list(current - defult)
        else:
            return None

    def listNamespaceAdd(self):
        namespace = self.nameSpaceFind()
        nameMain = []
        self.ui.namespace_combo.clear()
        self.ui.namespace_combo.addItem('No Namespace')
        if namespace:
            for ii in namespace:
                self.ui.namespace_combo.addItem(ii+':')

    def BakeIKcontroler(self, fk_js, ik_cons, ik_vector, timemin, timemax):
        sp_locs = []
        constrains = []

        objtest = fk_js[0] + '_FKIK_switch'
        if cmds.objExists(objtest):
            # print '============'
            # print objtest
            # print '============'
            for ii in fk_js:
                sploc = cmds.spaceLocator(n=ii + '_joint_loc')[0]
                cons = cmds.parentConstraint(ii + '_FKIK_switch', sploc, mo=False)[0]
                sp_locs.append(sploc)
                constrains.append(cons)

            vec_locs = []
            for ii in range(4):
                cmds.setAttr(ik_vector[ii] + '.follow', 0)
                sploc = cmds.spaceLocator(n=fk_js[ii] + '_vector_sp_loc')[0]
                cons = cmds.parentConstraint(fk_js[ii] + '_FKIK_switch_pole', sploc, mo=False)[0]

                constrains.append(cons)
                vec_locs.append(sploc)

            cmds.bakeResults(sp_locs + vec_locs, sm=True, t=(timemin, timemax), sb=1)
            cmds.delete(constrains)

            constrains = []
            for ii in range(4):
                pp = cmds.parentConstraint(sp_locs[ii], ik_cons[ii], mo=False)[0]
                po = cmds.pointConstraint(vec_locs[ii], ik_vector[ii], mo=False)[0]
                constrains.append(pp)
                constrains.append(po)

            cmds.bakeResults(ik_vector + ik_cons, sm=True, t=(timemin, timemax), sb=1)
            cmds.delete(constrains, vec_locs, sp_locs)
            om.MGlobal.displayInfo('Bake HIK to maya already over!!!')
        else:
            om.MGlobal.displayError('ik bake failure, maybe the rigging not completely, please call kami!')


def load_ui():
    try:
        mainWindow().closeUI()
    except:
        pass
    maxtomaya = mainWindow()
    maxtomaya.showUI()


if __name__ == '__main__':
    try:
        mainWindow().closeUI()
    except:
        pass
    maxtomaya = mainWindow()
    maxtomaya.showUI()
