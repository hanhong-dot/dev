import maya.api.OpenMaya as OM
import math
import maya.cmds as cmds
import math
import maya.api.OpenMayaRender as OMR
import maya.api.OpenMayaAnim as OMA
import maya.mel as mel
import sys
import json
import re

class DualQuaternion:
    def __init__(self, real=OM.MQuaternion(0, 0, 0, 1), dual=OM.MQuaternion(0, 0, 0, 0)):
        self.real = real
        self.dual = dual

    def __add__(self, q):
        return DualQuaternion(self.real + q.real, self.dual + q.dual)

    def __mul__(self, q):
        if isinstance(q, float) or isinstance(q, int):
            return DualQuaternion(q * self.real, q * self.dual)
        elif isinstance(q, DualQuaternion):
            return DualQuaternion(self.real * q.real, self.dual * q.real + self.real * q.dual)

    def dot(self, q):
        return self.real.x * q.real.x + self.real.y * q.real.y + self.real.z * q.real.z + self.real.w * q.real.w;

    @staticmethod
    def dotQuat(a, b):
        return a.x * b.x + a.y * b.y + a.z * b.z + a.w * b.w

    def normalize(self):
        rr = DualQuaternion.dotQuat(self.real, self.real)
        rd = DualQuaternion.dotQuat(self.real, self.dual)
        invrr = 1 / rr
        invsq = 1 / math.sqrt(rr)
        alpha = rd * invrr * invsq
        self.real = invsq * self.real
        q1 = invsq * self.dual
        q2 = alpha * self.real
        self.dual.x = q1.x - q2.x
        self.dual.y = q1.y - q2.y
        self.dual.z = q1.z - q2.z
        self.dual.w = q1.w - q2.w

    def display(self):
        pass

    def conjugate(self):
        return DualQuaternion(self.real.conjugate(), self.dual.conjugate())

    def conjugateIt(self):
        self.real.conjugateIt()
        self.dual.conjugateIt()

    def getTranslation(self):
        t = self.real.conjugate() * (2 * self.dual)
        return [t.x, t.y, t.z]

    def transPoint(self, p):
        q = 0.5 * OM.MQuaternion(p[0], p[1], p[2], 0)
        qut = DualQuaternion(self.real, q * self.real + self.dual)
        return qut.getTranslation()

    @staticmethod
    def makeDQfromRT(r, tx, ty, tz):
        return DualQuaternion(r, 0.5 * (r * OM.MQuaternion(tx, ty, tz, 0)))

    @staticmethod
    def makeDQfromMat(mat):
        r = OM.MTransformationMatrix(mat).rotation(asQuaternion=True)
        return DualQuaternion.makeDQfromRT(r, mat[12], mat[13], mat[14])
# st
# faceShortJoints = [u'Head_rivet_R_117', u'Head_rivet_R_116', u'Head_rivet_L_117', u'Head_rivet_L_116', u'Head_rivet_R_115', u'Head_rivet_R_114', u'Head_rivet_R_113', u'Head_rivet_L_115', u'Head_rivet_L_114', u'Head_rivet_L_113', u'Head_rivet_M_21', u'Head_rivet_R_111', u'Head_rivet_R_112', u'Head_rivet_R_1_lod', u'Head_rivet_R_10', u'Head_rivet_R_11_lod', u'Head_rivet_R_12', u'Head_rivet_R_16_lod', u'Head_rivet_R_17', u'Head_rivet_R_18_lod', u'Head_rivet_R_19', u'Head_rivet_R_2', u'Head_rivet_R_20', u'Head_rivet_R_21', u'Head_rivet_R_22', u'Head_rivet_R_23_lod', u'Head_rivet_R_24', u'Head_rivet_R_25_lod', u'Head_rivet_R_26', u'Head_rivet_R_27', u'Head_rivet_R_28', u'Head_rivet_R_29_lod', u'Head_rivet_R_3_lod', u'Head_rivet_R_30', u'Head_rivet_R_31_lod', u'Head_rivet_R_32', u'Head_rivet_R_33_lod', u'Head_rivet_R_34_lod', u'Head_rivet_R_35', u'Head_rivet_R_36', u'Head_rivet_R_37', u'Head_rivet_R_38', u'Head_rivet_R_4', u'Head_rivet_R_40', u'Head_rivet_R_41', u'Head_rivet_R_42', u'Head_rivet_R_45', u'Head_rivet_R_5_lod', u'Head_rivet_R_50', u'Head_rivet_R_51_lod', u'Head_rivet_R_52_lod', u'Head_rivet_R_53', u'Head_rivet_R_54_lod', u'Head_rivet_R_55', u'Head_rivet_R_56_lod', u'Head_rivet_R_57_lod', u'Head_rivet_R_59_lod', u'Head_rivet_R_6', u'Head_rivet_R_60_lod', u'Head_rivet_R_61', u'Head_rivet_R_62_lod', u'Head_rivet_R_63_lod', u'Head_rivet_R_64', u'Head_rivet_R_65', u'Head_rivet_R_66', u'Head_rivet_R_67', u'Head_rivet_R_68', u'Head_rivet_R_69', u'Head_rivet_R_7_lod', u'Head_rivet_R_70', u'Head_rivet_R_71', u'Head_rivet_R_72', u'Head_rivet_R_73_lod', u'Head_rivet_R_74_lod', u'Head_rivet_R_79_lod', u'Head_rivet_R_8', u'Head_rivet_R_80', u'Head_rivet_R_81_lod', u'Head_rivet_R_82', u'Head_rivet_R_83_lod', u'Head_rivet_R_84_lod', u'Head_rivet_R_85_lod', u'Head_rivet_R_86', u'Head_rivet_R_87', u'Head_rivet_R_88', u'Head_rivet_R_89', u'Head_rivet_R_9_lod', u'Head_rivet_R_90', u'Head_rivet_R_91_lod', u'Head_rivet_R_92', u'Head_rivet_R_93_lod', u'Head_rivet_R_94_lod', u'Head_rivet_R_95', u'Head_rivet_R_96', u'Head_rivet_R_97', u'Head_rivet_R_98_lod', u'Head_rivet_R_99_lod', u'Head_rivet_R_100_lod', u'Head_rivet_R_101_lod', u'Head_rivet_R_102', u'Head_rivet_R_103', u'Head_rivet_R_104_lod', u'Head_rivet_R_105_lod', u'Head_rivet_R_106_lod', u'Head_rivet_R_107_lod', u'Head_rivet_R_108_lod', u'Head_rivet_R_109_lod', u'Head_rivet_R_110_lod', u'Head_rivet_L_112', u'Head_rivet_L_111', u'Head_rivet_L_110_lod', u'Head_rivet_L_109_lod', u'Head_rivet_L_108_lod', u'Head_rivet_L_107_lod', u'Head_rivet_L_106_lod', u'Head_rivet_L_105_lod', u'Head_rivet_L_104_lod', u'Head_rivet_L_103', u'Head_rivet_L_102', u'Head_rivet_L_101_lod', u'Head_rivet_L_100_lod', u'Head_rivet_L_99_lod', u'Head_rivet_L_98_lod', u'Head_rivet_L_97', u'Head_rivet_L_96', u'Head_rivet_L_95', u'Head_rivet_L_94_lod', u'Head_rivet_L_93_lod', u'Head_rivet_L_92', u'Head_rivet_L_91_lod', u'Head_rivet_L_90', u'Head_rivet_L_9_lod', u'Head_rivet_L_89', u'Head_rivet_L_88', u'Head_rivet_L_87', u'Head_rivet_L_86', u'Head_rivet_L_85_lod', u'Head_rivet_L_84_lod', u'Head_rivet_L_83_lod', u'Head_rivet_L_82', u'Head_rivet_L_81_lod', u'Head_rivet_L_80', u'Head_rivet_L_8', u'Head_rivet_L_79_lod', u'Head_rivet_L_74_lod', u'Head_rivet_L_73_lod', u'Head_rivet_L_72', u'Head_rivet_L_71', u'Head_rivet_L_70', u'Head_rivet_L_7_lod', u'Head_rivet_L_69', u'Head_rivet_L_68', u'Head_rivet_L_67', u'Head_rivet_L_66', u'Head_rivet_L_65', u'Head_rivet_L_64', u'Head_rivet_L_63_lod', u'Head_rivet_L_62_lod', u'Head_rivet_L_61', u'Head_rivet_L_60_lod', u'Head_rivet_L_6', u'Head_rivet_L_59_lod', u'Head_rivet_L_57_lod', u'Head_rivet_L_56_lod', u'Head_rivet_L_55', u'Head_rivet_L_54_lod', u'Head_rivet_L_53', u'Head_rivet_L_52_lod', u'Head_rivet_L_51_lod', u'Head_rivet_L_50', u'Head_rivet_L_5_lod', u'Head_rivet_L_45', u'Head_rivet_L_42', u'Head_rivet_L_41', u'Head_rivet_L_40', u'Head_rivet_L_4', u'Head_rivet_L_38', u'Head_rivet_L_37', u'Head_rivet_L_36', u'Head_rivet_L_35', u'Head_rivet_L_34_lod', u'Head_rivet_L_33_lod', u'Head_rivet_L_32', u'Head_rivet_L_31_lod', u'Head_rivet_L_30', u'Head_rivet_L_3_lod', u'Head_rivet_L_29_lod', u'Head_rivet_L_28', u'Head_rivet_L_27', u'Head_rivet_L_26', u'Head_rivet_L_25_lod', u'Head_rivet_L_24', u'Head_rivet_L_23_lod', u'Head_rivet_L_22', u'Head_rivet_L_21', u'Head_rivet_L_20', u'Head_rivet_L_2', u'Head_rivet_L_19', u'Head_rivet_L_18_lod', u'Head_rivet_L_17', u'Head_rivet_L_16_lod', u'Head_rivet_L_12', u'Head_rivet_L_11_lod', u'Head_rivet_L_10', u'Head_rivet_L_1_lod', u'Head_rivet_M_20', u'Head_rivet_M_19_lod', u'Head_rivet_M_18', u'Head_rivet_M_17', u'Head_rivet_M_16', u'Head_rivet_M_9_lod', u'Head_rivet_M_8_lod', u'Head_rivet_M_7_lod', u'Head_rivet_M_4_lod', u'Head_rivet_M_3_lod', u'Head_rivet_M_15_lod', u'Head_rivet_M_11_lod', u'Head_rivet_M_10_lod', u'Head_rivet_M_1_lod', u'Head_rivet_M_0_lod', u'Eye_L', u'Eye_R', u'Tongue3_M', u'Tongue2_M', u'Tongue1_M', u'Tongue0_M', u'TeethLower_M', u'TeethUpper_M']
# NaiNai
# faceShortJoints = [u'NoseLfUpJoint', u'NoseRtUpJoint', u'faceLfEye05Joint', u'faceRtEye08Joint', u'faceRtEye05Joint', u'faceRtEye06Joint', u'faceRtEye07Joint', u'faceRtEye01Joint', u'faceLfEye06Joint', u'faceRtEye03Joint', u'faceRtEye02Joint', u'faceRtEye04Joint', u'faceLfEye01Joint', u'faceLfEye07Joint', u'faceLfEye08Joint', u'faceLfEye02Joint', u'faceLfEye03Joint', u'faceLfEye04Joint', u'faceMdLipUpJoint', u'faceMdJaw02Joint', u'faceMdJaw03Joint', u'faceMdJaw01Joint', u'faceRtWrinkleDnJoint', u'faceLfWrinkleMdJoint', u'faceRtWrinkleUpJoint', u'faceLfWrinkleDnJoint', u'faceLfWrinkleUpJoint', u'faceRtWrinkleMdJoint', u'faceLfCheekOt01Joint', u'faceLfCheekOt02Joint', u'faceLfCheekOt03Joint', u'faceRtCheekOt01Joint', u'faceRtCheekOt02Joint', u'faceRtCheekOt03Joint', u'faceRtCheek04Joint', u'faceLfCheek04Joint', u'NoseMd02Joint', u'NoseMd01Joint', u'faceRtCheek03Joint', u'faceLfCheek03Joint', u'faceLfCheek02Joint', u'faceRtCheek02Joint', u'faceRtCheek01Joint', u'faceLfCheek01Joint', u'faceRtDimpleDnJoint', u'faceLfDimpleDnJoint', u'faceLfDimpleMdJoint', u'faceRtDimpleMdJoint', u'faceLfDimpleUpJoint', u'faceRtDimpleUpJoint', u'faceMdToothUpJoint', u'faceMdToothDnJoint', u'fk04Joint', u'fk03Joint', u'fk02Joint', u'fk01Joint', u'faceRtCheekOtJoint', u'faceLfCheekOtJoint', u'jawJoint', u'lip18Joint', u'lip17Joint', u'lip16Joint', u'lip15Joint', u'lip14Joint', u'lip13Joint', u'lip12Joint', u'lip11Joint', u'lip10Joint', u'lip09Joint', u'lip08Joint', u'lip07Joint', u'lip06Joint', u'lip05Joint', u'lip04Joint', u'lip03Joint', u'lip02Joint', u'lip01Joint', u'noseDnJoint', u'NoseLfJoint', u'NoseRtJoint', u'NoseMdJoint', u'eyeLf08Joint', u'eyeLf07Joint', u'eyeLf06Joint', u'eyeLf05Joint', u'eyeLf04Joint', u'eyeLf03Joint', u'eyeLf02Joint', u'eyeLf01Joint', u'eyeLfJoint', u'eyeRt08Joint', u'eyeRt07Joint', u'eyeRt06Joint', u'eyeRt05Joint', u'eyeRt04Joint', u'eyeRt03Joint', u'eyeRt02Joint', u'eyeRt01Joint', u'eyeRtJoint', u'browMd01Joint', u'browLf05Joint', u'browLf04Joint', u'browLf03Joint', u'browLf02Joint', u'browLf01Joint', u'browRt05Joint', u'browRt04Joint', u'browRt03Joint', u'browRt02Joint', u'browRt01Joint', u'HeadEnd_M'] #
# shuzhang
# faceShortJoints = [u'eyeRtJoint', u'eyeRt01Joint', u'eyeRt02Joint', u'eyeRt03Joint', u'eyeRt04Joint', u'eyeRt05Joint', u'eyeRt06Joint', u'eyeRt07Joint', u'eyeRt08Joint', u'eyeLf01Joint', u'eyeLf02Joint', u'eyeLf03Joint', u'eyeLf04Joint', u'eyeLf05Joint', u'eyeLf06Joint', u'eyeLf07Joint', u'eyeLf08Joint', u'browRt01Joint', u'browRt02Joint', u'browRt03Joint', u'browRt04Joint', u'browRt05Joint', u'browLf01Joint', u'browLf02Joint', u'browLf03Joint', u'browLf04Joint', u'browLf05Joint', u'browMd01Joint', u'NoseUpRtJoint', u'NoseMd02Joint', u'NoseMd03Joint', u'NoseMd01Joint', u'noseDnJoint', u'NoseUpLfJoint', u'NoseRtJoint', u'noseUpJoint', u'NoseLfJoint', u'lip01Joint', u'lip02Joint', u'lip03Joint', u'lip04Joint', u'lip05Joint', u'lip06Joint', u'lip07Joint', u'lip08Joint', u'lip09Joint', u'lip10Joint', u'lip11Joint', u'lip12Joint', u'lip13Joint', u'lip14Joint', u'lip15Joint', u'lip16Joint', u'lip17Joint', u'lip18Joint', u'jawJoint', u'faceRtCheek04Joint', u'faceMdLipUpJoint', u'faceLfCheek04Joint', u'faceLfWrinkle01Joint', u'faceLfWrinkle02Joint', u'faceLfWrinkle03Joint', u'faceRtWrinkle01Joint', u'faceRtWrinkle02Joint', u'faceRtWrinkle03Joint', u'faceMdWrinkleJoint', u'faceMdDimpleJoint', u'faceMdJawJoint', u'faceRtDimple01Joint', u'faceRtDimple02Joint', u'faceRtDimple03Joint', u'faceLfDimple01Joint', u'faceLfDimple02Joint', u'faceLfDimple03Joint', u'faceRtCheek01Joint', u'faceRtCheek02Joint', u'faceRtCheek03Joint', u'faceLfCheek01Joint', u'faceLfCheek02Joint', u'faceLfCheek03Joint', u'faceLfCheekDn01Joint', u'faceLfCheekDn02Joint', u'faceLfCheekDn03Joint', u'faceRtCheekDn03Joint', u'faceRtCheekDn01Joint', u'faceRtCheekDn02Joint', u'faceLfCheekOtJoint', u'faceRtCheekOtJoint', u'fk01Joint', u'fk02Joint', u'fk03Joint', u'fk04Joint', u'fk05Joint', u'faceMdToothDnJoint', u'faceMdToothUpJoint', u'faceLfEye08Joint', u'faceLfEye07Joint', u'faceLfEye06Joint', u'faceLfEye05Joint', u'faceLfEye04Joint', u'faceLfEye03Joint', u'faceLfEye02Joint', u'faceLfEye01Joint', u'faceRtEye03Joint', u'faceRtEye02Joint', u'faceRtEye01Joint', u'faceRtEye07Joint', u'faceRtEye06Joint', u'faceRtEye05Joint', u'faceRtEye04Joint', u'faceRtEye08Joint', u'eyeLfJoint'] #


#taotao
# faceShortJoints = [u'eyeRtJoint', u'eyeRt01Joint', u'eyeRt02Joint', u'eyeRt03Joint', u'eyeRt04Joint', u'eyeRt05Joint', u'eyeRt06Joint', u'eyeRt07Joint', u'eyeRt08Joint', u'eyeLfJoint', u'eyeLf01Joint', u'eyeLf02Joint', u'eyeLf03Joint', u'eyeLf04Joint', u'eyeLf05Joint', u'eyeLf06Joint', u'eyeLf07Joint', u'eyeLf08Joint', u'browRt01Joint', u'browRt02Joint', u'browRt03Joint', u'browRt04Joint', u'browRt05Joint', u'browLf01Joint', u'browLf02Joint', u'browLf03Joint', u'browLf04Joint', u'browLf05Joint', u'browMd01Joint', u'faceLfCheek03Joint', u'faceRtCheek02Joint', u'faceRtEye04Joint', u'faceLfEye03Joint', u'faceMdLipUpJoint', u'faceRtCheekOt03Joint', u'faceRtCheekOt02Joint', u'faceRtCheekOt01Joint', u'faceLfEye02Joint', u'faceRtCheek04Joint', u'faceRtCheek01Joint', u'faceLfDimpleDnJoint', u'faceRtCheek03Joint', u'faceMdToothUpJoint', u'faceLfEye08Joint', u'faceLfEye07Joint', u'faceLfCheek01Joint', u'faceLfCheek02Joint', u'faceLfEye04Joint', u'faceLfCheek04Joint', u'faceMdToothDnJoint', u'faceLfEye01Joint', u'faceMdJaw01Joint', u'faceMdJaw03Joint', u'faceRtDimpleUpJoint', u'faceLfDimpleMdJoint', u'faceLfWrinkleUpJoint', u'faceLfDimpleUpJoint', u'faceLfCheekOt03Joint', u'faceLfCheekOt02Joint', u'faceLfWrinkleDnJoint', u'faceRtWrinkleUpJoint', u'faceRtCheekOtJoint', u'faceRtDimpleDnJoint', u'faceRtDimpleMdJoint', u'faceMdJaw02Joint', u'faceLfCheekOtJoint', u'faceLfCheekOt01Joint', u'faceRtEye03Joint', u'faceRtEye02Joint', u'faceRtEye01Joint', u'faceRtEye07Joint', u'faceRtEye06Joint', u'faceRtEye05Joint', u'faceLfEye06Joint', u'faceRtEye08Joint', u'faceLfEye05Joint', u'faceRtWrinkleDnJoint', u'lip01Joint', u'lip02Joint', u'lip03Joint', u'lip04Joint', u'lip05Joint', u'lip06Joint', u'lip07Joint', u'lip08Joint', u'lip09Joint', u'lip10Joint', u'lip11Joint', u'lip12Joint', u'lip13Joint', u'lip14Joint', u'lip15Joint', u'lip16Joint', u'lip17Joint', u'lip18Joint', u'jawJoint', u'NoseMd02Joint', u'NoseMd01Joint', u'NoseRtUpJoint', u'noseDnJoint', u'NoseRtJoint', u'NoseLfUpJoint', u'NoseMdJoint', u'noseUpJoint', u'NoseLfJoint', u'fk01Joint', u'fk02Joint', u'fk03Joint', u'fk04Joint', u'faceRtWrinkleMdJoint', u'faceLfWrinkleMdJoint'] #
#FY

AU, FACS = range(2)


def lip_export(path, faceShortJoints, tongueJoints, typ):
    # faceShortJoints = [u'TeethUpper_M', u'TeethLower_M', u'Tongue0_M', u'Head_rivet_L_10', u'Head_rivet_L_100_lod', u'Head_rivet_L_101_lod', u'Head_rivet_L_102', u'Head_rivet_L_103', u'Head_rivet_L_104_lod', u'Head_rivet_L_105_lod', u'Head_rivet_L_106_lod', u'Head_rivet_L_107_lod', u'Head_rivet_L_108_lod', u'Head_rivet_L_109_lod', u'Head_rivet_L_110_lod', u'Head_rivet_L_111', u'Head_rivet_L_112', u'Head_rivet_L_113', u'Head_rivet_L_114', u'Head_rivet_L_115', u'Head_rivet_L_116', u'Head_rivet_L_117', u'Head_rivet_L_118_lod', u'Head_rivet_L_11_lod', u'Head_rivet_L_12', u'Head_rivet_L_120_lod', u'Head_rivet_L_121_lod', u'Head_rivet_L_16_lod', u'Head_rivet_L_17', u'Head_rivet_L_18_lod', u'Head_rivet_L_19', u'Head_rivet_L_1_lod', u'Head_rivet_L_2', u'Head_rivet_L_20', u'Head_rivet_L_21', u'Head_rivet_L_22', u'Head_rivet_L_23_lod', u'Head_rivet_L_24', u'Head_rivet_L_25_lod', u'Head_rivet_L_26', u'Head_rivet_L_27', u'Head_rivet_L_28', u'Head_rivet_L_29_lod', u'Head_rivet_L_30', u'Head_rivet_L_31_lod', u'Head_rivet_L_32', u'Head_rivet_L_33_lod', u'Head_rivet_L_34_lod', u'Head_rivet_L_35', u'Head_rivet_L_36', u'Head_rivet_L_37', u'Head_rivet_L_38', u'Head_rivet_L_3_lod', u'Head_rivet_L_4', u'Head_rivet_L_40', u'Head_rivet_L_41', u'Head_rivet_L_42', u'Head_rivet_L_45', u'Head_rivet_L_50', u'Head_rivet_L_51_lod', u'Head_rivet_L_52_lod', u'Head_rivet_L_53', u'Head_rivet_L_54_lod', u'Head_rivet_L_55', u'Head_rivet_L_56_lod', u'Head_rivet_L_57_lod', u'Head_rivet_L_59_lod', u'Head_rivet_L_5_lod', u'Head_rivet_L_6', u'Head_rivet_L_60_lod', u'Head_rivet_L_61', u'Head_rivet_L_62_lod', u'Head_rivet_L_63_lod', u'Head_rivet_L_64', u'Head_rivet_L_65', u'Head_rivet_L_66', u'Head_rivet_L_67', u'Head_rivet_L_68', u'Head_rivet_L_69', u'Head_rivet_L_70', u'Head_rivet_L_71', u'Head_rivet_L_72', u'Head_rivet_L_73_lod', u'Head_rivet_L_74_lod', u'Head_rivet_L_79_lod', u'Head_rivet_L_7_lod', u'Head_rivet_L_8', u'Head_rivet_L_80', u'Head_rivet_L_81_lod', u'Head_rivet_L_82', u'Head_rivet_L_83_lod', u'Head_rivet_L_84_lod', u'Head_rivet_L_85_lod', u'Head_rivet_L_86', u'Head_rivet_L_87', u'Head_rivet_L_88', u'Head_rivet_L_89', u'Head_rivet_L_90', u'Head_rivet_L_91_lod', u'Head_rivet_L_92', u'Head_rivet_L_93_lod', u'Head_rivet_L_94_lod', u'Head_rivet_L_95', u'Head_rivet_L_96', u'Head_rivet_L_97', u'Head_rivet_L_98_lod', u'Head_rivet_L_99_lod', u'Head_rivet_L_9_lod', u'Head_rivet_M_0_lod', u'Head_rivet_M_10_lod', u'Head_rivet_M_11_lod', u'Head_rivet_M_15_lod', u'Head_rivet_M_16', u'Head_rivet_M_17', u'Head_rivet_M_18', u'Head_rivet_M_19_lod', u'Head_rivet_M_1_lod', u'Head_rivet_M_20', u'Head_rivet_M_21', u'Head_rivet_M_22', u'Head_rivet_M_23_lod', u'Head_rivet_M_3_lod', u'Head_rivet_M_4_lod', u'Head_rivet_M_7_lod', u'Head_rivet_M_8_lod', u'Head_rivet_M_9_lod', u'Head_rivet_R_10', u'Head_rivet_R_100_lod', u'Head_rivet_R_101_lod', u'Head_rivet_R_102', u'Head_rivet_R_103', u'Head_rivet_R_104_lod', u'Head_rivet_R_105_lod', u'Head_rivet_R_106_lod', u'Head_rivet_R_107_lod', u'Head_rivet_R_108_lod', u'Head_rivet_R_109_lod', u'Head_rivet_R_110_lod', u'Head_rivet_R_111', u'Head_rivet_R_112', u'Head_rivet_R_113', u'Head_rivet_R_114', u'Head_rivet_R_115', u'Head_rivet_R_116', u'Head_rivet_R_117', u'Head_rivet_R_118_lod', u'Head_rivet_R_11_lod', u'Head_rivet_R_12', u'Head_rivet_R_120_lod', u'Head_rivet_R_121_lod', u'Head_rivet_R_16_lod', u'Head_rivet_R_17', u'Head_rivet_R_18_lod', u'Head_rivet_R_19', u'Head_rivet_R_1_lod', u'Head_rivet_R_2', u'Head_rivet_R_20', u'Head_rivet_R_21', u'Head_rivet_R_22', u'Head_rivet_R_23_lod', u'Head_rivet_R_24', u'Head_rivet_R_25_lod', u'Head_rivet_R_26', u'Head_rivet_R_27', u'Head_rivet_R_28', u'Head_rivet_R_29_lod', u'Head_rivet_R_30', u'Head_rivet_R_31_lod', u'Head_rivet_R_32', u'Head_rivet_R_33_lod', u'Head_rivet_R_34_lod', u'Head_rivet_R_35', u'Head_rivet_R_36', u'Head_rivet_R_37', u'Head_rivet_R_38', u'Head_rivet_R_3_lod', u'Head_rivet_R_4', u'Head_rivet_R_40', u'Head_rivet_R_41', u'Head_rivet_R_42', u'Head_rivet_R_45', u'Head_rivet_R_50', u'Head_rivet_R_51_lod', u'Head_rivet_R_52_lod', u'Head_rivet_R_53', u'Head_rivet_R_54_lod', u'Head_rivet_R_55', u'Head_rivet_R_56_lod', u'Head_rivet_R_57_lod', u'Head_rivet_R_59_lod', u'Head_rivet_R_5_lod', u'Head_rivet_R_6', u'Head_rivet_R_60_lod', u'Head_rivet_R_61', u'Head_rivet_R_62_lod', u'Head_rivet_R_63_lod', u'Head_rivet_R_64', u'Head_rivet_R_65', u'Head_rivet_R_66', u'Head_rivet_R_67', u'Head_rivet_R_68', u'Head_rivet_R_69', u'Head_rivet_R_70', u'Head_rivet_R_71', u'Head_rivet_R_72', u'Head_rivet_R_73_lod', u'Head_rivet_R_74_lod', u'Head_rivet_R_79_lod', u'Head_rivet_R_7_lod', u'Head_rivet_R_8', u'Head_rivet_R_80', u'Head_rivet_R_81_lod', u'Head_rivet_R_82', u'Head_rivet_R_83_lod', u'Head_rivet_R_84_lod', u'Head_rivet_R_85_lod', u'Head_rivet_R_86', u'Head_rivet_R_87', u'Head_rivet_R_88', u'Head_rivet_R_89', u'Head_rivet_R_90', u'Head_rivet_R_91_lod', u'Head_rivet_R_92', u'Head_rivet_R_93_lod', u'Head_rivet_R_94_lod', u'Head_rivet_R_95', u'Head_rivet_R_96', u'Head_rivet_R_97', u'Head_rivet_R_98_lod', u'Head_rivet_R_99_lod', u'Head_rivet_R_9_lod', u'Head_rivet_L_122_lod', u'Head_rivet_R_122_lod', u'Head_rivet_L_123_lod', u'Head_rivet_R_123_lod', u'Tongue1_M', u'Tongue2_M', u'Tongue3_M'] #
    for tongue_joint in tongueJoints:
        if tongue_joint in faceShortJoints:
            pass
        else:
            faceShortJoints.append(tongue_joint)

    if typ != AU:
        phonemeAttributes = [
            "ChinRaiser",
            "Dimpler",
            "JawDrop",
            "LipCornerDepressor",
            "LipCornerPuller",
            "LipFunneler",
            "LipPressor",
            "LipPucker",
            "LipStercher",
            "LipSuck",
            "LipTightener",
            "LipZipDn",
            "LipZipUp",
            "LowerLipDepressor",
            "MouthCloseDn",
            "MouthCloseUp",
            "MouthStretch",
            "SharpLipPuller",
            "UpperLipRaiser",
            ]
    else:
        phonemeAttributes = ["Dimpler",
                             "LipCornerDepressor",
                             "LipPuckerDn",
                             "LipPuckerUp",
                             "LipSuckDn",
                             "LipSuckUp",
                             "LipTightener",
                             "LipZipDn",
                             "LipZipUp",
                             "LowerLipDepressor",
                             "MouthStretch",
                             "SharpLipPuller",
                             "UpperLipRaiser"
                             ]
    import pymel.core as pm
    bridge = pm.PyNode("SpeakBlendShapeBridge")
    cache = []
    for attr in pm.listAttr(bridge, ud=1):
        dst_attr = bridge.attr(attr)
        for src_attr in dst_attr.inputs(p=1):
            src_attr.disconnect(dst_attr)
            cache.append([src_attr, dst_attr])


    mouthJointsData = []
    mouthJointsData2 = []
    mouthDownWeight = 0.7
    mouthScale = 2.350
    maxClose = 0.2
    # bsNode = 'low_model_bs'
    # bsNode = 'blendShape8'
    # eyeDriversBones = {'Eye_angle_to_offset_L':'Eye_L','Eye_angle_to_offset_R':'Eye_R'}
    eyeDriversBones = {'EyeAim_L_cod_loc':'Eye_L','EyeAim_R_cod_loc':'Eye_R'}
    phonemeController = "SpeakBlendShapeBridge"

    combId0 = phonemeAttributes.index("MouthStretch")
    combId1 = phonemeAttributes.index("LowerLipDepressor")
    combPhonemeAttributes = ["LowerLipDepressorClose"]

    browFrameMap = [['browUp',51],['browDown',53]]
    blinkFrameMap = [['blink',55]]

    browAnimationMap = [0,0,0]
    headAnimationMap = [0,0,0]







    faceJoints = cmds.ls(faceShortJoints, l=True)
    cmds.select([])
    cmds.refresh()
    hierarchy = faceJoints[0].split('|')
    rootIndex = 0
    for i, p in enumerate(hierarchy):
        if cmds.ls(p, type='joint'):
            rootIndex = i
            break

    def getNewJointPath(joint,rootIndex):
        jointHierarchy = joint.split('|')
        newBoneName = ''
        for i in range(rootIndex, len(jointHierarchy)):
            newBoneName += '|' + jointHierarchy[i]

        nodeStr = newBoneName.replace('|', '/')
        if nodeStr[0] == '/':
            nodeStr = nodeStr[1:len(nodeStr)]
        return nodeStr

    jointStr = []
    for join in faceJoints:
        jointStr.append(getNewJointPath(join,rootIndex))

    pars = {}
    for j in faceJoints:
        ps = cmds.listRelatives(j,p=True)
        if ps:
            if pars.has_key(ps[0]):
                pars[ps[0]] += 1
            else:
                pars[ps[0]] = 0


    FaceParameter = {}
    FaceParameter['jointsInfo'] = []
    jointsInfo = FaceParameter['jointsInfo']
    FaceParameter["mouthJointsId"] = []
    FaceParameter["mouthJointsId1"] = []
    mouthJointsId = FaceParameter["mouthJointsId"]
    mouthJointsId1 = FaceParameter["mouthJointsId1"]
    FaceParameter["mouthDownWeight"] = mouthDownWeight


    cmds.currentTime(0)
    for id,groupPair in enumerate(mouthJointsData):
        down = groupPair[0]
        up = groupPair[1]

        downJoint = cmds.ls(down[0],l=True)[0]
        upJoint = cmds.ls(up[0],l=True)[0]
        followingDownJoint = cmds.ls(down[1],l=True)[0]
        followingUpJoint = cmds.ls(up[1],l=True)[0]

        jointMatDown = OM.MMatrix(cmds.xform(downJoint, q=True, m=True, os=True))
        jointMatDown[1] *= -1
        jointMatDown[2] *= -1
        jointMatDown[4] *= -1
        jointMatDown[8] *= -1
        jointMatDown[12] *= -0.01
        jointMatDown[13] *= 0.01
        jointMatDown[14] *= 0.01

        jointMatUp = OM.MMatrix(cmds.xform(upJoint, q=True, m=True, os=True))
        jointMatUp[1] *= -1
        jointMatUp[2] *= -1
        jointMatUp[4] *= -1
        jointMatUp[8] *= -1
        jointMatUp[12] *= -0.01
        jointMatUp[13] *= 0.01
        jointMatUp[14] *= 0.01

        downPoint =  OM.MVector(jointMatDown[12],jointMatDown[13],jointMatDown[14])
        upPoint = OM.MVector(jointMatUp[12],jointMatUp[13],jointMatUp[14])

        centerPoint = (upPoint-downPoint)*mouthDownWeight + downPoint
        offsetDown = downPoint - centerPoint
        offsetUp = upPoint - centerPoint
        downIndex = faceJoints.index(downJoint)
        upIndex = faceJoints.index(upJoint)
        followingDownIndex = faceJoints.index(followingDownJoint)
        followingUpIndex = faceJoints.index(followingUpJoint)

        mouthJointsId.append({"down": downIndex,
                              "up": upIndex,
                              "followingDown": followingDownIndex,
                              "followingUp": followingUpIndex,
                           "offsetDown":{'x':offsetDown.x,'y':offsetDown.y,'z':offsetDown.z},
                           "offsetUp":{'x':offsetUp.x,'y':offsetUp.y,'z':offsetUp.z}})


    for joint,weight in mouthJointsData2:
        jointstr = cmds.ls(joint, l=True)[0]
        mouthJointsId1.append({'id':faceJoints.index(jointstr),'weight':weight})



    baseQuat = []

    for i,joint in enumerate(faceJoints):
        jointMat = OM.MMatrix(cmds.xform(joint, q=True, m=True, os=True))
        jointMat[1] *= -1
        jointMat[2] *= -1
        jointMat[4] *= -1
        jointMat[8] *= -1
        jointMat[12] *= -0.01
        jointMat[13] *= 0.01
        jointMat[14] *= 0.01
        r = OM.MTransformationMatrix(jointMat).rotation(asQuaternion=True)

        jointsInfo.append({'jointName':jointStr[i],
                           'blendMode':0,
                           'baseTransform':{'position': {'x': jointMat[12], 'y': jointMat[13], 'z': jointMat[14]},
                                            'rotation': {'x': r.x, 'y': r.y, 'z': r.z, 'w': r.w, }}})
        baseQuat.append(r)



    def calculateElement(parameter,name):
        threshold = 0.0001
        parameter.append({})
        parameterElements = parameter[-1]
        parameterElements['jointsOffset'] = []
        parameterElements['jointsIndex'] = []
        parameterElements['jointScale'] = []
        parameterElements['jointsScaleIndex'] = []
        parameterElements['name'] = name
        jointsOffset = parameterElements['jointsOffset']
        jointsIndex = parameterElements['jointsIndex']
        jointScale = parameterElements['jointScale']
        jointsScaleIndex= parameterElements['jointsScaleIndex']
        for j, joint in enumerate(faceJoints):
            jointMat = OM.MMatrix(cmds.xform(joint, q=True, m=True, os=True))
            jointMat[1] *= -1
            jointMat[2] *= -1
            jointMat[4] *= -1
            jointMat[8] *= -1
            jointMat[12] *= -0.01
            jointMat[13] *= 0.01
            jointMat[14] *= 0.01
            r = OM.MTransformationMatrix(jointMat).rotation(asQuaternion=True)
            distance = 0
            distance += abs(jointsInfo[j]['baseTransform']['position']['x'] - jointMat[12])
            distance += abs(jointsInfo[j]['baseTransform']['position']['y'] - jointMat[13])
            distance += abs(jointsInfo[j]['baseTransform']['position']['z'] - jointMat[14])

            dotQ = r.x * jointsInfo[j]['baseTransform']['rotation']['x'] + \
                   r.y * jointsInfo[j]['baseTransform']['rotation']['y'] + \
                   r.z * jointsInfo[j]['baseTransform']['rotation']['z'] + \
                   r.w * jointsInfo[j]['baseTransform']['rotation']['w']
            distance += 1 - abs(dotQ)

            if distance > threshold:
                offQu = baseQuat[j].conjugate() * r
                jointsIndex.append(j)
                jointsOffset.append({'position': {'x': jointMat[12] - jointsInfo[j]['baseTransform']['position']['x'],
                                                  'y': jointMat[13] - jointsInfo[j]['baseTransform']['position']['y'],
                                                  'z': jointMat[14] - jointsInfo[j]['baseTransform']['position']['z']},
                                     'rotation': {'x': offQu.x, 'y': offQu.y, 'z': offQu.z, 'w': offQu.w, }})
            s = OM.MTransformationMatrix(jointMat).scale(OM.MSpace.kObject)
            if abs(s[0]-1)+abs(s[1]-1)+abs(s[2]-1)>0.001:
                jointsScaleIndex.append(j)
                jointScale.append({'x': s[0], 'y': s[1], 'z': s[2]})

    def appendPhoneme(parameter,attributes,controller):
        for attr in attributes:
            print controller +"."+ attr
            cmds.setAttr(controller +"."+attr,1)
            cmds.refresh()
            calculateElement(parameter, attr)
            cmds.setAttr(controller + "." + attr, 0)
    def appendShape(parameter,map):
        for i, [name, frame] in enumerate(map):
            cmds.currentTime(frame)
            cmds.refresh()
            calculateElement(parameter,name)

    def appendAnimation(parameter,map,fps = 30.0):
        parameters = []
        for i, frame in enumerate(map):
            cmds.currentTime(frame)
            cmds.refresh()
            calculateElement(parameters,str(i))


        fullJointsIndex = []
        for para in parameters:
            for i in para['jointsIndex']:
                if i not in fullJointsIndex:
                    fullJointsIndex.append(i)
        fullJointsIndex.sort()
        keys = []
        startFrame = map[0]
        for i, frame in enumerate(map):
            t = (float)(frame - startFrame) / float(fps)
            para = parameters[i]
            jointOffset = para['jointsOffset']
            jointsIndex = para['jointsIndex']
            newJointOffset = []
            for i in fullJointsIndex:
                if i in jointsIndex:
                    newJointOffset.append(jointOffset[jointsIndex.index(i)])
                else:
                    newJointOffset.append({'position': {'x': 0,'y': 0,'z': 0},
                                         'rotation': {'x': 0, 'y': 0, 'z': .0, 'w': 1}})
            keys.append({"t": t, "jointsOffset": newJointOffset})
        parameter["jointsIndex"] = fullJointsIndex
        parameter["keys"] = keys

    FaceParameter['visemePoses'] = []

    appendPhoneme(FaceParameter['visemePoses'],phonemeAttributes,phonemeController)

    FaceParameter['combvisemePoses'] = []

    appendPhoneme(FaceParameter['combvisemePoses'],combPhonemeAttributes,phonemeController)

    FaceParameter['browElements'] = []
    appendShape(FaceParameter['browElements'],browFrameMap)

    FaceParameter['blinkElements'] = []
    appendShape(FaceParameter['blinkElements'],blinkFrameMap)

    FaceParameter['browAnimation'] = {}
    appendAnimation(FaceParameter['browAnimation'],browAnimationMap,24)

    FaceParameter['headAnimation'] = {}
    appendAnimation(FaceParameter['headAnimation'],headAnimationMap,24)

    FaceParameter['mouthScale'] = mouthScale
    FaceParameter['maxClose'] = maxClose
    FaceParameter['combId0'] = combId0
    FaceParameter['combId1'] = combId1

    #add tongue index
    FaceParameter["tongueJointsIndex"] = []
    jointsInfo_list = FaceParameter["jointsInfo"]
    for tongue_joint in tongueJoints:
        tongue_joint_name = cmds.ls(tongue_joint, l=True)[0]
        tongue_path = getNewJointPath(tongue_joint_name,rootIndex)
        for num, joint_info  in enumerate(jointsInfo_list):
            if joint_info["jointName"] == tongue_path:
                FaceParameter["tongueJointsIndex"].append(num)


    # add adam group
    def generate_empty_element(parameter,name):
        parameter.append({})
        parameterElements = parameter[-1]
        parameterElements['jointsOffset'] = []
        parameterElements['jointsIndex'] = []
        parameterElements['jointScale'] = []
        parameterElements['jointsScaleIndex'] = []
        parameterElements['name'] = name

    if typ != AU:
        temp_list1 = {}
        temp_list1['Adam_downward'] = []
        generate_empty_element(temp_list1['Adam_downward'],"Adam_downward")
        temp_list2 = {}
        temp_list2['Adam_upward'] = []
        generate_empty_element(temp_list2['Adam_upward'],"Adam_upward")
        FaceParameter['visemePoses'].append(temp_list1['Adam_downward'][-1])
        FaceParameter['visemePoses'].append(temp_list2['Adam_upward'][-1])
    else:
        pass
    if typ == FACS:
        import lipsyncExport_mouse_export
        reload(lipsyncExport_mouse_export)
        FaceParameter["lipzip"] = lipsyncExport_mouse_export.get_lip_sync_zip_data()
    cmds.currentTime(0)

    with open(path, "wb") as f:
        json.dump(FaceParameter, f, indent=4)

    for src_attr, dst_attr in cache:
        src_attr.connect(dst_attr)





