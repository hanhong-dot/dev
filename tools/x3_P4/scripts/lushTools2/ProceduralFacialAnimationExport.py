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
        print self.real
        print self.dual

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


def ProceduralFacialAnimationExport(path, faceShortJoints, pupilShortJoint, bsNode, Eye_L, Eye_R, _DrivenBsNode):
    eyeDriversBones = {'EyeAim_L_cod_loc':Eye_L,'EyeAim_R_cod_loc': Eye_R}

    faceJoints = cmds.ls(faceShortJoints, l=True)
    pupilJoint = cmds.ls(pupilShortJoint,l=True)[0]

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
    FaceParameter['pupilJoint'] =getNewJointPath(pupilJoint,rootIndex)
    jointsInfo = FaceParameter['jointsInfo']

    cmds.currentTime(0)

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
                print j
                jointsScaleIndex.append(j)
                jointScale.append({'x': s[0], 'y': s[1], 'z': s[2]})

    def appendPhoneme(parameter,attributes,controller):
        for attr in attributes:
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



    transfromAttr = ['translateX','translateY','translateZ']

    FaceParameter['eyeElements'] = []
    FaceParameter['eyeDriverParas'] = []
    controllerAttrDic = {}
    bsindexes = cmds.getAttr(bsNode + '.weight', mi=True)
    for bsid in bsindexes:
        conNodes = cmds.listConnections(bsNode + '.weight[{0}]'.format(bsid), s=True, d=False)
        if conNodes and cmds.nodeType(conNodes[0]) == 'animCurveUU' and cmds.nodeType(cmds.listConnections(conNodes[0], s=True, d=False)) == 'transform':
            controllerName, attribute = cmds.listConnections(conNodes[0], s=True, d=False, p=True)[0].split('.')
            # weightControlList.append((controllerName, attribute))
            if controllerName in eyeDriversBones:
                controlPar = cmds.listRelatives(controllerName,p=True)[0]
                controllerAttribute = controllerName + attribute
                if not controllerAttrDic.has_key(controllerAttribute):
                    controllerAttrDic[controllerAttribute] = [len(controllerAttrDic), controllerName, attribute]
                fc = cmds.keyframe(conNodes[0], q=True, fc=True)
                if attribute == 'translateX':
                    fc[0] *= -1
                    fc[1] *= -1
                vc = cmds.keyframe(conNodes[0], q=True, vc=True)
                a = (vc[1] - vc[0]) / (fc[1] - fc[0])
                b = vc[0] - fc[0] * a
                print(controllerAttrDic[controllerAttribute],a,b)
                FaceParameter['eyeDriverParas'].append({'attributeId':controllerAttrDic[controllerAttribute][0],'a':a,'b':b})
                cmds.setAttr(bsNode + '.weight[{0}]'.format(bsid), 1)
                cmds.refresh()
                calculateElement(FaceParameter['eyeElements'],cmds.attributeName(bsNode + '.weight[{0}]'.format(bsid)))
                cmds.setAttr(bsNode + '.weight[{0}]'.format(bsid), 0)


    FaceParameter['eyes'] = []
    for driven,bone in eyeDriversBones.iteritems():
        controlPar = cmds.listRelatives(driven, p=True)[0]
        lookAtLocalPosition = cmds.xform(controlPar, q=True, t=True, os=True)
        lookAtLocalPosition[0] *= -0.01
        lookAtLocalPosition[1] *= 0.01
        lookAtLocalPosition[2] *= 0.01
        FaceParameter['eyes'].append({'basePose': {'x': lookAtLocalPosition[0],
                                                   'y': lookAtLocalPosition[1],
                                                   'z': lookAtLocalPosition[2]},
                                      'id': faceShortJoints.index(bone)})

    FaceParameter['eyeAttributes'] = []
    FaceParameter['eyeAttributes'] = [{}]*len(controllerAttrDic)
    for id,controllerName,attribute in controllerAttrDic.itervalues():
        FaceParameter['eyeAttributes'][id] = {'driverId':eyeDriversBones.keys().index(controllerName),
                                              'attributeId':transfromAttr.index(attribute)}


    cmds.currentTime(0)
    FaceParameter["drivenBlendShapes"] = [
        {
            "target": _DrivenBsNode+".Eye_close_R",
            "weight": 1
        },
        {
            "target": _DrivenBsNode+".Eye_close_L",
            "weight": 1
        },
    ]
    with open(path, "wb") as f:
        json.dump(FaceParameter, f, indent=4)







