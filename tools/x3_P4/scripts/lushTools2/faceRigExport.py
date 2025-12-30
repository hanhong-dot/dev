import os.path
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

mergedControllers = []
faceConstraintCtrs = []
transfromAttr = {'translateX': 0, 'translateY': 1, 'translateZ': 2,
                 'rotateX': 3, 'rotateY': 4, 'rotateZ': 5,
                 'scaleX': 6, 'scaleY': 7, 'scaleZ': 8}


def find_index(ctrls, name):
    for i, ctrl in enumerate(ctrls):
        if ctrl["name"] == name:
            return i


def check_same_ctrl(data):
    bs_names = set([ctrl["name"] for ctrl in data["blendControllers"]])
    se_names = set([ctrl["name"] for ctrl in data["secondaryControllers"]])
    same_ctrls = bs_names.intersection(se_names)
    for name in same_ctrls:
        i = find_index(data["blendControllers"], name)
        ctrl = data["blendControllers"][i]
        ctrl["controllerInfo"]["shape"] = [{k: v*0.8 for k, v in p.items()} for p in ctrl["controllerInfo"]["shape"]]
        ctrl["position"]["y"] += 0.001

def get_bs_info(bs_node_name=""):
    bsInfo = []
    if not cmds.objExists(bs_node_name):
        return []
    for target_name in cmds.listAttr(bs_node_name+".weight", m=1):
        target = bs_node_name+"."+target_name
        weight = cmds.getAttr(bs_node_name+"."+target_name)
        if weight > 0.01:
            bsInfo.append(dict(target=target, weight=weight))
    return bsInfo


def find_pose_id(data, ctrl_name, attr_name, plug_min):
    attr_names = ['translateX', 'translateY', 'translateZ',
                  'rotateX', 'rotateY', 'rotateZ',
                  'scaleX', 'scaleY', 'scaleZ']
    for i, vwm in enumerate(data["valueWeightMap"]):
        current_plug_min = vwm["a"] > 0.0
        if current_plug_min != plug_min:
            continue
        node_attr_id = vwm["id"]
        ctrl_i = data["weightControllerMap"][node_attr_id]["controlId"]
        current_ctrl_name = data["blendControllers"][ctrl_i]["name"]

        if current_ctrl_name != ctrl_name:
            continue
        attr_i = data["weightControllerMap"][node_attr_id]["attributeId"]
        if attr_i < 9:
            current_attr_name = attr_names[attr_i]
        else:
            current_attr_name = data["blendControllers"][ctrl_i]["customAttrs"][attr_i-9]["attrName"]
        if attr_name != current_attr_name:
            continue
        return i
    return -1


def add_switch_map(data):
    driven_id = find_pose_id(data, "FKJaw_M", "translateY", True)
    switch_id = find_pose_id(data, "FKJaw_M", "Chin_Upstair_follow", True)
    if driven_id and switch_id:
        data["drivenSwitchMap"] = [dict(drivenId=driven_id, switchId=switch_id)]
    else:
        pass


def close_chin_follow():
    if cmds.objExists("FKJaw_M"):
        if cmds.listAttr("FKJaw_M", ud=1) is None:
            return
        if "Chin_Upstair_follow" in cmds.listAttr("FKJaw_M", ud=1):
            cmds.setAttr("FKJaw_M.Chin_Upstair_follow", 0)


def add_default(data):
    for ctrl_data in data["blendControllers"]:
        for attr_data in ctrl_data["customAttrs"]:
            if attr_data["attrName"] == "Chin_Upstair_follow":
                attr_data["defaultValue"] = 1.0
            else:
                attr_data["defaultValue"] = 0.0


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

def getControllerInfo(controllerName,headInverseMat,isLookAt = False,lookAtLocalPosition = [0,0,0],isFaceConstraint = False,limit = None):
    if controllerName==None:
        return {"name": ""}
    if not cmds.objExists(controllerName):
        return {"name": ""}
    isMerged = controllerName in mergedControllers
    controlMat = OM.MMatrix(cmds.xform(controllerName, q=True, m=True, ws=True))
    controlMat[1] *= -1
    controlMat[2] *= -1
    controlMat[4] *= -1
    controlMat[8] *= -1
    worldPivot = cmds.xform(controllerName, q=True, rp=True, ws=True)
    controlMat[12] = worldPivot[0] * -0.01
    controlMat[13] = worldPivot[1] * 0.01
    controlMat[14] = worldPivot[2] * 0.01
    controlMat = controlMat * headInverseMat
    transMat = OM.MTransformationMatrix(controlMat)
    r = transMat.rotation(asQuaternion=True)
    scalse = transMat.scale(OM.MSpace.kWorld)

    limitX = [-1e+7, 1e+7]
    limitY = [-1e+7, 1e+7]
    limitZ = [-1e+7, 1e+7]

    if limit:
        limitX = [0,0]
        limitY = [0,0]
        limitZ = [0,0]
        for i in range(len(limit)):
            attr = limit[i][0]
            v = limit[i][1]

            if attr in transfromAttr:
                id = transfromAttr[attr]
                if id<3:
                    if id ==0:
                        v *= -0.01
                    else:
                        v*=0.01
                    if v>0:
                        [limitX,limitY,limitZ][id][1] = v
                    else:
                        [limitX, limitY, limitZ][id][0] = v

    else :
        for attr, limit in [['tx', limitX], ['ty', limitY], ['tz', limitZ]]:
            if cmds.getAttr(controllerName + '.' + attr, lock=True):
                limit[0] = 0
                limit[1] = 0
            else:
                limitMin, limitMax = eval('cmds.transformLimits(controllerName, q=True, {0}=True)'.format(attr))
                # enableMin,enableMax = cmds.transformLimits(controllerName, q=True, etx=True)
                enableMin, enableMax = eval('cmds.transformLimits(controllerName, q=True, e{0}=True)'.format(attr))
                if attr == 'tx':
                    if enableMin:
                        limit[0] = limitMax * -0.01
                    if enableMax:
                        limit[1] = limitMin * -0.01
                else:
                    if enableMin:
                        limit[0] = limitMin * 0.01
                    if enableMax:
                        limit[1] = limitMax * 0.01
    localPivot = cmds.xform(controllerName, q=True, rp=True, os=True)
    curveShape = []

    if cmds.listRelatives(controllerName, s=True, f=True) == None:
        print controllerName + "  has not shape"
    for shape in cmds.listRelatives(controllerName, s=True, f=True):
        if not cmds.getAttr(shape + '.io'):
            for i in cmds.getAttr(shape + '.controlPoints', mi=True):
                controlPoint = cmds.getAttr(shape + '.controlPoints[{0}]'.format(i))[0]
                curveShape.append(
                    {'x': (controlPoint[0] - localPivot[0]) * -0.01*scalse[0], 'y': (controlPoint[1] - localPivot[1]) * 0.01*scalse[1],
                     'z': (controlPoint[2] - localPivot[2]) * 0.01*scalse[2]})

    slls = OM.MSelectionList()
    for shape in cmds.listRelatives(controllerName, s=True, f=True):
        if not cmds.getAttr(shape + '.io'):
            slls.add(shape)
    color = OMR.MGeometryUtilities.wireframeColor(slls.getDagPath(0))
    if not isFaceConstraint:
        isFaceConstraint =True if cmds.listRelatives(controllerName,p=True)[0].find('Subtract')>=0 else False
    if not isFaceConstraint:
        isFaceConstraint = controllerName in faceConstraintCtrs
    return {"name": controllerName, 'customAttrs': [],'isFaceConstraint':isFaceConstraint,'isLookAt':isLookAt,
                        'isMerged':isMerged,
                        'position': {'x': controlMat[12], 'y': controlMat[13], 'z': controlMat[14]},
                        'rotation': {'x': r.x, 'y': r.y, 'z': r.z, 'w': r.w, },
                        'scale': {'x': scalse[0], 'y': scalse[1], 'z': scalse[2]},
                        'lookAtLocalPosition': {'x': lookAtLocalPosition[0], 'y': lookAtLocalPosition[1], 'z': lookAtLocalPosition[2]},
                        'controllerInfo': {'limitMinX': limitX[0],
                                           'limitMaxX': limitX[1],
                                           'limitMinY': limitY[0],
                                           'limitMaxY': limitY[1],
                                           'limitMinZ': limitZ[0],
                                           'limitMaxZ': limitZ[1],
                                           'shape': curveShape,
                                           'color': {'r': color.r, 'g': color.g, 'b': color.b, 'a': color.a}},
                        'mirrorId':-1
                        }
def addMirrorInfo(controllers,str1,str2):
    controllerDic = {}
    for i,v in enumerate(controllers):
        controllerDic[v['name']] = i
    for v in controllers:
        name = v['name']
        v['mirrorId'] = -1
        if re.search(str1,name):
            mirrorName = re.sub(str1,str2,name)
            if controllerDic.has_key(mirrorName):
                v['mirrorId'] = controllerDic[mirrorName]
        elif re.search(str2,name):
            mirrorName = re.sub(str2,str1,name)
            if controllerDic.has_key(mirrorName):
                v['mirrorId'] = controllerDic[mirrorName]


NPC, CORE = range(2)


def face_rig_export(path, typ, faceJoints, bs_node_name):
    temp_eye_cons = []
    global faceConstraintCtrs
    if typ == NPC:
        exportFileName = "DC"
        skinTransforms = []
        blendShapeNodes = []
        eyeJointCtlMap = {'eyeLfJoint': 'FCtrl_eyeAim_L', 'eyeRtJoint': 'FCtrl_eyeAim_R'}
        lookAtController = None
        customEyefollowOffset = [["tx", 6], ["tx", -6], ["ty", 6], ["ty", -6]]
        customBsController = {
            "FCtrl_jaw_M": [["translateX", 2.5], ["translateX", -2.5], ["translateY", -4], ["translateZ", 2]],
            "FCtrl_brow_R": [["translateX", 0.5], ["translateX", -1], ["translateY", 1], ["translateY", -1],
                             ["translateZ", 0.6], ["translateZ", -0.5]],
            "FCtrl_brow_L": [["translateX", 0.5], ["translateX", -1], ["translateY", 1], ["translateY", -1],
                             ["translateZ", 0.6], ["translateZ", -0.5]],
            "FCtrl_eye_R": [["translateX", 0.3], ["translateX", -0.3], ["translateY", 0.3], ["translateY", -0.3]],
            "FCtrl_eye_L": [["translateX", 0.3], ["translateX", -0.3], ["translateY", 0.3], ["translateY", -0.3]],
            "FCtrl_lip_L": [["translateX", 1.4], ["translateX", -1], ["translateY", 1.5], ["translateY", -1.5],
                            ['rotateX', 30], ['rotateX', -30], ['rotateY', 30], ['rotateY', -30], ['rotateZ', 30],
                            ['rotateZ', -30]],
            "FCtrl_lip_R": [["translateX", 1.4], ["translateX", -1], ["translateY", 1.5], ["translateY", -1.5],
                            ['rotateX', 30], ['rotateX', -30], ['rotateY', 30], ['rotateY', -30], ['rotateZ', 30],
                            ['rotateZ', -30]],
            "FCtrl_eyeD_L": [["translateX", 0.4], ["translateX", -0.4], ["translateY", 1], ["translateY", -0.3],
                             ["translateZ", 0.1], ["translateZ", -0.1]],
            "FCtrl_eyeD_R": [["translateX", 0.4], ["translateX", -0.4], ["translateY", 1], ["translateY", -0.3],
                             ["translateZ", 0.1], ["translateZ", -0.1]],
            "FCtrl_eyeB_L": [["translateX", 0.4], ["translateX", -0.4], ["translateY", 0.4], ["translateY", -1],
                             ["translateZ", 0.1], ["translateZ", -0.1]],
            "FCtrl_eyeB_R": [["translateX", 0.4], ["translateX", -0.4], ["translateY", 0.4], ["translateY", -1],
                             ["translateZ", 0.1], ["translateZ", -0.1]],
            }
        customBsControllerLimitRemove = []
        customSedController = [u'FCtrl_eyeC_R', u'FCtrl_eyeB_R', u'FCtrl_eyeD_R', u'FCtrl_eyeA_R', u'FCtrl_eyeA_L',
                               u'FCtrl_eyeC_L', u'FCtrl_eyeB_L', u'FCtrl_eyeD_L', u'FCtrl_browC_R', u'FCtrl_browB_R',
                               u'FCtrl_browA_R', u'FCtrl_browA_L', u'FCtrl_browB_L', u'FCtrl_browC_L', u'FCtrl_lipUp_R',
                               u'FCtrl_lipDn_R', u'FCtrl_lipUp_M', u'FCtrl_lipDn_M', u'FCtrl_lipUp_L', u'FCtrl_lipDn_L',
                               u'FCtrl_nose_M', u'FCtrl_lip_M']  #
        defaultLookAtLocalPosition = [0, 0, 1]
        faceConstraintCtrs = ['FCtrl_lip_R', 'FCtrl_lip_L']
        eyeMasterControllerStr = "FCtrl_eye_M"
        defaultEyeFollow = 0.2
    else:
        try:
            temp_eye_cons += cmds.pointConstraint("EyeAim_FK_L", "Eye_L")
            temp_eye_cons += cmds.pointConstraint("EyeAim_FK_R", "Eye_R")
        except:
            pass
        skinTransforms = ['ClustersRegion','LipsRegion','mouth_copy_nikki_mesh','brow_chin_Region','ChunZhuRegion','NoseMainRegion','NoseTipsRegion','EyeSideRegion','EyeLid_Main_ssdr_attach_Region']
        blendShapeNodes = ['low_model_bs','blendShape8','blendShape12', "blendShape27"]
        eyeJointCtlMap = {'Eye_L':'AimEye_L','Eye_R':'AimEye_R'}
        lookAtController = {'EyeAim_L_cod_loc':'AimEye_L','EyeAim_R_cod_loc':'AimEye_R'}
        customEyefollowOffset = None
        if cmds.getAttr("EyeAim_FK_R.v"):
            customSedController = ["EyeAim_FK_L", "EyeAim_FK_R"]
        else:
            customSedController = []
        def beginSetUpstair(data):
            cmds.setAttr("FKJaw_M.ty",1)
            if not cmds.objExists("FKJaw_M.Chin_Upstair_follow"):
                return
            cmds.setAttr("FKJaw_M.Chin_Upstair_follow",1)
        def endSetUpstair(data):
            cmds.setAttr("FKJaw_M.ty", 0)
            if not cmds.objExists("FKJaw_M.Chin_Upstair_follow"):
                return
            cmds.setAttr("FKJaw_M.Chin_Upstair_follow", 0)
        customBsController ={"FKJaw_M":[["Chin_Upstair_follow",1,[beginSetUpstair,endSetUpstair,None]]]}
        customBsControllerLimitRemove = ["FKJaw_M"]
        faceConstraintCtrs = []
        eyeMasterControllerStr = "AimEye_M"
        defaultLookAtLocalPosition = [1,0,0]
        defaultEyeFollow = 1
    transformAttrs = ['t','tx','ty','tz','r','rx','ry','rz','s','sx','sy','sz']
    EyeParameterDict = {}
    for v in eyeJointCtlMap.values():
        EyeParameterDict[v] = {"eyeFollowIds":[]}
    eyeCtrJointMap = {}
    for k,v in eyeJointCtlMap.iteritems():
        eyeCtrJointMap[v] = k
    global mergedControllers
    mergedControllers = []
    if customSedController and customBsController:
        for a in customSedController:
            for b in customBsController:
                if a==b:
                    mergedControllers.append(a)
                    continue
    print mergedControllers


    customBsAttrs = ["translateX","translateX","translateY","translateY","translateZ","translateZ"]




    cmds.select(faceJoints)
    joints = cmds.ls(sl=True, l=True)
    cmds.select([])
    cmds.refresh()
    hierarchy = joints[0].split('|')
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
    for join in joints:
        jointStr.append(getNewJointPath(join,rootIndex))

    pars = {}
    for j in joints:
        ps = cmds.listRelatives(j,p=True)
        if ps:
            if pars.has_key(ps[0]):
                pars[ps[0]] += 1
            else:
                pars[ps[0]] = 0
    maxV = 0
    headJoint = ''
    for k,v in pars.iteritems():
        if maxV<v:
            maxV = v
            headJoint = k
    headJoint = cmds.ls(headJoint,l=True)[0]
    print (headJoint)
    headMat = OM.MMatrix(cmds.xform(headJoint, q=True, m=True, ws=True))
    maxAxisId = 0
    maxAxis = 0
    for i,v in enumerate([0,4,8]):
        axis = abs(headMat[v])
        if axis>maxAxis:
            maxAxis = axis
            maxAxisId = i
    headMat[1] *= -1
    headMat[2] *= -1
    headMat[4] *= -1
    headMat[8] *= -1
    headMat[12] *= -0.01
    headMat[13] *= 0.01
    headMat[14] *= 0.01
    headJoint = getNewJointPath(headJoint,rootIndex)
    headinverseMat = headMat.inverse()



    eyeControllerTemp = {}
    for k,v in eyeJointCtlMap.iteritems():
        eyeControllerTemp[cmds.ls(k,l=True)[0]] = v
    eyeJointCtlMap = eyeControllerTemp






    FaceParameter = {}
    FaceParameter['jointsInfo'] = []
    jointsInfo = FaceParameter['jointsInfo']
    FaceParameter["valueWeightMap"] = []
    dataParList = FaceParameter["valueWeightMap"]
    FaceParameter['jointInfluences'] = [{'skinItems':[]} for i in joints]
    jointInfluences = FaceParameter['jointInfluences']
    FaceParameter['defaultEyeFollow'] =defaultEyeFollow


    #editorOnly
    FaceParameter['headJoint'] = headJoint
    FaceParameter['blendControllers'] = []
    controllers = FaceParameter['blendControllers']
    FaceParameter['weightControllerMap'] = []
    weightControlMap = FaceParameter['weightControllerMap']
    FaceParameter['baseSecondaryCtrs'] = []
    baseSecondaryCtrs = FaceParameter['baseSecondaryCtrs']
    FaceParameter['secondaryControllers'] = []
    secondaryControllers = FaceParameter['secondaryControllers']
    FaceParameter['tertiaryControllers'] = []
    tertiaryControllers = FaceParameter['tertiaryControllers']
    FaceParameter['eyeMasterController'] = []
    eyeMasterController = FaceParameter['eyeMasterController']
    FaceParameter['eyesPara'] = []
    eyesPara = FaceParameter['eyesPara']
    FaceParameter["mirrorAxisId"] = maxAxisId

    def checkController(controllers,maxIteration = 5):
        if(maxIteration<0):
            return None
        if len(controllers)==0:
            return None
        for c in controllers:
            if cmds.listRelatives(c, s=True, f=True,typ = "nurbsCurve"):
                return c
        sources = []
        for c in controllers:
            cns = cmds.listConnections(c,s=True,d=False)
            if cns!=None:
                for n in set(cns):
                    if cmds.nodeType(n) in ['parentConstraint','transform','decomposeMatrix','multMatrix']:
                        sources.append(n)
        return checkController(sources,maxIteration-1)

    influenceDic = {}
    influenceList = []
    for skinTrans in skinTransforms:
        skinSlls = OM.MSelectionList()
        meshSlls = OM.MSelectionList()
        if not cmds.objExists(skinTrans):
            continue
        for his in cmds.listHistory(skinTrans,f=False):
            if(cmds.nodeType(his) == 'skinCluster'):
                skinSlls.add(his)
                meshSlls.add(skinTrans)
                break
        dagPath,component = meshSlls.getComponent(0)
        meshFn = OM.MFnMesh(dagPath)
        vertexNum = meshFn.numVertices
        skinFn = OMA.MFnSkinCluster(skinSlls.getDependNode(0))
        influenceObjs = skinFn.influenceObjects()
        infJointNum = len(influenceObjs)
        influenceIds = []
        trueInfluenceIds = []
        for i,infJoint in enumerate(influenceObjs):
            infJointName =  infJoint.partialPathName()
            connectSet = set()
            for attr in transformAttrs:
                connects = cmds.listConnections(infJointName+'.'+attr,s=True,d=False)
                if connects and cmds.ls(connects[0],type='transform'):
                    connectSet.add(connects[0])
            if connectSet:
                influenceIds.append(i)
                trueInfluenceId = 0
                if not influenceDic.has_key(infJointName):
                    trueInfluenceId = len(influenceDic)
                    influenceDic[infJointName] = trueInfluenceId
                    influenceList.append(infJointName)
                    secondaryControllers.append(getControllerInfo(checkController(list(connectSet)),headinverseMat))
                else:
                    trueInfluenceId = influenceDic[infJointName]
                trueInfluenceIds.append(trueInfluenceId)
        meshSlls = OM.MSelectionList()
        meshSlls.add(skinTrans)
        dagPath = meshSlls.getDagPath(0)
        meshFn = OM.MFnMesh(dagPath)
        jointVertexMap = []
        for jId, joint in enumerate(joints):
            jointPoint = OM.MPoint(cmds.xform(joint, q=True, ws=True, t=True))
            p, fId = meshFn.getClosestPoint(jointPoint, OM.MSpace.kWorld)
            if p.distanceTo(jointPoint) < 0.001:
                minDistance = 100
                pId = -1
                for i in meshFn.getPolygonVertices(fId):
                    dis = p.distanceTo(meshFn.getPoint(i, OM.MSpace.kWorld))
                    if dis < minDistance:
                        minDistance = dis
                        pId = i
                jointVertexMap.append(pId)
            else:
                jointVertexMap.append(-1)
        weights = skinFn.getWeights(dagPath, component)[0]
        for jointId in range(len(joints)):
            vertexId = jointVertexMap[jointId]
            if vertexId >= 0:
                jointWeights = weights[vertexId*infJointNum:(vertexId+1)*infJointNum]
                for i in range(len(influenceIds)):
                    if jointWeights[influenceIds[i]]>0.001:

                        jointInfluences[jointId]['skinItems'].append({'id':trueInfluenceIds[i],
                                                                      'weight':jointWeights[influenceIds[i]]})

    for i,inf in enumerate(influenceList):
        jointMat = OM.MMatrix(cmds.xform(inf, q=True, m=True, ws=True))
        jointMat[1] *= -1
        jointMat[2] *= -1
        jointMat[4] *= -1
        jointMat[8] *= -1
        jointMat[12] *= -0.01
        jointMat[13] *= 0.01
        jointMat[14] *= 0.01
        jointMat = jointMat * headMat.inverse()

        controllerName = secondaryControllers[i]['name']

        prs = cmds.listRelatives(controllerName, p=True)
        if prs:
            sc = cmds.getAttr(prs[0] + '.s')
            cmds.setAttr(prs[0] + '.s', 1, 1, 1)

        controllerMat = OM.MMatrix(cmds.xform(controllerName, q=True, m=True, ws=True))
        controllerMat[1] *= -1
        controllerMat[2] *= -1
        controllerMat[4] *= -1
        controllerMat[8] *= -1
        controllerMat[12] *= -0.01
        controllerMat[13] *= 0.01
        controllerMat[14] *= 0.01
        controllerMat = controllerMat * headMat.inverse()
        TftMatrix = OM.MTransformationMatrix(controllerMat)
        r = TftMatrix.rotation(asQuaternion=True)
        baseSecondaryCtrs.append({'position': {'x': jointMat[12],'y': jointMat[13],'z': jointMat[14]},
                                  'rotation': {'x': r.x, 'y': r.y, 'z': r.z, 'w': r.w, }})
        if prs:
            cmds.setAttr(prs[0] + '.s', *(sc[0]))

    if customSedController:
        for ctr in customSedController:
            if not cmds.objExists(ctr):
                continue
            secondaryControllers.append(getControllerInfo(ctr,headinverseMat,isFaceConstraint=True))
            controllerMat = OM.MMatrix(cmds.xform(ctr, q=True, m=True, ws=True))
            controllerMat[1] *= -1
            controllerMat[2] *= -1
            controllerMat[4] *= -1
            controllerMat[8] *= -1
            controllerMat[12] *= -0.01
            controllerMat[13] *= 0.01
            controllerMat[14] *= 0.01
            controllerMat = controllerMat * headMat.inverse()
            TftMatrix = OM.MTransformationMatrix(controllerMat)
            r = TftMatrix.rotation(asQuaternion=True)
            baseSecondaryCtrs.append({'position': {'x': controllerMat[12], 'y': controllerMat[13], 'z': controllerMat[14]},
                                      'rotation': {'x': r.x, 'y': r.y, 'z': r.z, 'w': r.w, }})

        jointBasePosition = []
        for i,joint in enumerate(joints):
            jointMat = cmds.xform(joint, q=True, m=True, ws=True)
            jointBasePosition.append(OM.MVector(jointMat[12],jointMat[13],jointMat[14]))

        testOffsetAttrs = [['tx',1],['tx',-1],['ty',1],['ty',-1],['tz',1],['tz',-1]]

        for j,ctr in enumerate(customSedController):
            if not cmds.objExists(ctr):
                continue
            j = len(secondaryControllers) - len(customSedController) + j
            ctrBaseMat = cmds.xform(ctr, q=True, m=True, ws=True)
            jointW = [0]*len(joints)
            for offsetAttr in testOffsetAttrs:
                cmds.setAttr(ctr+'.'+offsetAttr[0],offsetAttr[1])
                cmds.refresh()
                ctrMat = cmds.xform(ctr, q=True, m=True, ws=True)
                ctrOffsetVec = OM.MVector(ctrMat[12]-ctrBaseMat[12],ctrMat[13]-ctrBaseMat[13],ctrMat[14]-ctrBaseMat[14])
                ctrOffsetVec_length = ctrOffsetVec.length()
                if ctrOffsetVec_length < 0.0001:
                    ctrOffsetVec_length = 1
                jointOffset = []
                for i, joint in enumerate(joints):
                    jointMat = cmds.xform(joint, q=True, m=True, ws=True)
                    jointOffsetVec = OM.MVector(jointMat[12], jointMat[13], jointMat[14])- jointBasePosition[i]
                    if jointOffsetVec.length()>0.001:
                        w = jointOffsetVec * ctrOffsetVec /ctrOffsetVec_length/ctrOffsetVec_length
                        jointW[i] += max(min(w, 1), 0)
                cmds.setAttr(ctr + '.' + offsetAttr[0], 0)
            for i in range(len(jointW)):
                if jointW[i] > 0.01:
                    w = jointW[i]/6
                    newItem = {'id': j,'weight': w}
                    # 0 all 1 only pos 2 only rot
                    if "EyeAim_FK" in ctr:
                        newItem['mode'] = 2
                    else:
                        newItem['mode'] = 0
                    jointInfluences[i]['skinItems'].append(newItem)

    addMirrorInfo(secondaryControllers,'_L','_R')

    baseQuat = []

    for i,joint in enumerate(joints):
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
        if eyeJointCtlMap.has_key(joint):
            tertiaryControllers.append(getControllerInfo(eyeJointCtlMap[joint], headinverseMat,True))
            EyeParameterDict[eyeJointCtlMap[joint]]["jointId"] = i
            ctrro = tertiaryControllers[-1]['rotation']
            EyeParameterDict[eyeJointCtlMap[joint]]['lookAtCtlTranslate'] = ctrro

            controlMat = OM.MMatrix(cmds.xform(eyeJointCtlMap[joint], q=True, m=True, ws=True))
            controlMat[1] *= -1
            controlMat[2] *= -1
            controlMat[4] *= -1
            controlMat[8] *= -1
            worldPivot = cmds.xform(eyeJointCtlMap[joint], q=True, rp=True, ws=True)
            controlMat[12] = worldPivot[0] * -0.01
            controlMat[13] = worldPivot[1] * 0.01
            controlMat[14] = worldPivot[2] * 0.01
            controlHeadMat = controlMat * headinverseMat

            jointWorldMat = OM.MMatrix(cmds.xform(joint, q=True, m=True, ws=True))
            jointWorldMat[1] *= -1
            jointWorldMat[2] *= -1
            jointWorldMat[4] *= -1
            jointWorldMat[8] *= -1
            jointWorldMat[12] *= -0.01
            jointWorldMat[13] *= 0.01
            jointWorldMat[14] *= 0.01
            jointHeadMat = jointWorldMat * headinverseMat

            EyeParameterDict[eyeJointCtlMap[joint]]['lookAtCtlLocalPosition'] = {'x': controlHeadMat[12]-jointHeadMat[12], 
                                                                                 'y': controlHeadMat[13]-jointHeadMat[13], 
                                                                                 'z': controlHeadMat[14]-jointHeadMat[14]}

            if cmds.objExists("|YG_Rig") or cmds.objExists("|FY_Rig") or cmds.objExists("|XL_Rig"):
                print "YG Rig Export debug"
            # find locator offset as the real aim target in engine.
                lookAtOffsetPosition = [0, 0, 0]
                controlLocator = cmds.listRelatives(eyeJointCtlMap[joint], c=True, typ="transform")
                if controlLocator is not None:
                    lookAtOffsetPosition = cmds.xform(controlLocator, q=True, rp=True, ws=True)
                    lookAtOffsetPosition[0] *= -0.01
                    lookAtOffsetPosition[1] *= 0.01
                    lookAtOffsetPosition[2] *= 0.01
                    lookAtOffsetPosition[0] -= controlMat[12]
                    lookAtOffsetPosition[1] -= controlMat[13]
                    lookAtOffsetPosition[2] -= controlMat[14]
                EyeParameterDict[eyeJointCtlMap[joint]]['lookAtOffsetPosition'] = {'x': lookAtOffsetPosition[0],
                                                                                   'y': lookAtOffsetPosition[1],
                                                                                   'z': lookAtOffsetPosition[2]}
        else:
            tertiaryControllers.append(getControllerInfo(checkController([joint]),headinverseMat))


    addMirrorInfo(tertiaryControllers,'_L_','_R_')
    for jointId,jointInfluence in enumerate(jointInfluences):
        for skinItem in jointInfluence['skinItems']:
            bpd = jointsInfo[jointId]['baseTransform']['position']
            bcd = baseSecondaryCtrs[skinItem['id']]['position']
            skinItem['relativePosition'] = {'x': bpd['x']-bcd['x'], 'y': bpd['y']-bcd['y'], 'z': bpd['z']-bcd['z']}
    if eyeMasterControllerStr:
        eyeMasterController.append(getControllerInfo(eyeMasterControllerStr,headinverseMat))


    bsindexes = []
    for n in blendShapeNodes:
        if not cmds.objExists(n):
            continue
        for i in cmds.getAttr(n + '.weight', mi=True):
            bsindexes.append([n,i])


    if customEyefollowOffset != None:
        for c in eyeJointCtlMap.values():
            for [k,v] in customEyefollowOffset:
                bsindexes.append([c, "{0}:{1}".format(k,v)])

    if customBsController != None:
        for k,v in customBsController.iteritems():
            for va in v:
                bsindexes.append([k, va])

    bsExpIndexes = []




    controllerList = {}

    controllerAttrDic = {}
    controllerId = 0
    for bsNode,bsid in bsindexes:
        controllerName = None
        attribute = None
        isLookAt = False
        lookAtLocalPosition = [0, 0, 0]
        fc = None
        vc = None
        if bsNode in eyeCtrJointMap:
            controllerName = bsNode
            isLookAt = True
            lookAtLocalPosition = defaultLookAtLocalPosition[:]
            eyeJointMat0 = OM.MMatrix(cmds.xform(eyeCtrJointMap[bsNode], q=True, m=True, ws=True))
            attrData = bsid.split(":")
            cmds.setAttr(bsNode+"."+attrData[0],float(attrData[1]))
            eyeJointMat1 = OM.MMatrix(cmds.xform(eyeCtrJointMap[bsNode], q=True, m=True, ws=True))
            eyeConvertMat = eyeJointMat1 * eyeJointMat0.inverse()
            newLALP = OM.MVector(lookAtLocalPosition) * eyeConvertMat
            cmds.setAttr(bsNode + "." + attrData[0], 0)

            maxDistanceId = 0
            maxDistance = 0.0
            for i in range(3):
                dis = abs(newLALP[i]-lookAtLocalPosition[i])
                if(dis>maxDistance):
                    maxDistance = dis
                    maxDistanceId = i
            attribute = [k for k,v in transfromAttr.iteritems() if v == maxDistanceId][0]

            fc = [0,0]
            vc = [0,0]
            fc[0] =lookAtLocalPosition[maxDistanceId]
            fc[1] = newLALP[maxDistanceId]
            vc[0] = 0
            vc[1] = 1
            lookAtLocalPosition[0] *= -0.01
            lookAtLocalPosition[1] *= 0.01
            lookAtLocalPosition[2] *= 0.01
        elif bsNode in customBsController:
            if bsid[1]==0:
                continue
            controllerName = bsNode
            attribute = bsid[0]
            fc = [0, 0]
            vc = [0, 0]
            fc[0] = 0
            fc[1] = bsid[1]
            vc[0] = 0
            vc[1] = 1

            sc = cmds.xform(controllerName, q=True, s=True, ws=True)

            if transfromAttr.has_key(attribute):
                if transfromAttr[attribute]<3:
                    bsid[1] *= sc[transfromAttr[attribute]]
                elif transfromAttr[attribute] in [3,4,5]:
                    ids = [0,1,2]
                    ids.remove(transfromAttr[attribute]-3)
                    for i in ids:
                        fc[1] *= sc[i]


        else:
            conNodes = cmds.listConnections(bsNode + '.weight[{0}]'.format(bsid), s=True, d=False)
            if not conNodes or cmds.nodeType(conNodes[0]) != 'animCurveUU'  or cmds.nodeType(cmds.listConnections(conNodes[0], s=True, d=False)) != 'transform':
                continue
            controllerName, attribute = cmds.listConnections(conNodes[0], s=True, d=False, p=True)[0].split('.')

            if(lookAtController.has_key(controllerName)):
                if(customEyefollowOffset != None):
                    continue
                controlPar = cmds.listRelatives(controllerName, p=True)[0]
                lookAtLocalPosition = cmds.xform(controlPar, q=True, t=True, os=True)
                lookAtLocalPosition[0] *= -0.01
                lookAtLocalPosition[1] *= 0.01
                lookAtLocalPosition[2] *= 0.01
                controllerName = lookAtController[controllerName]
                isLookAt = True
            elif not cmds.listRelatives(controllerName, s=True, f=True):
                continue
            fc = cmds.keyframe(conNodes[0], q=True, fc=True)
            vc = cmds.keyframe(conNodes[0], q=True, vc=True)
        bsExpIndexes.append([bsNode,bsid])
        controllerAttribute = controllerName + attribute
        if not controllerAttrDic.has_key(controllerAttribute):
            controllerAttrDic[controllerAttribute] = [len(controllerAttrDic),controllerName, attribute]
            if isLookAt:
                EyeParameterDict[controllerName]["eyeFollowIds"].append(
                    {"bsId": controllerAttrDic[controllerAttribute][0], "attributeId": transfromAttr[attribute]})
        if attribute in ['translateX','rotateY','rotateZ']:
            fc[0] *= -1
            fc[1] *= -1
        a = float((vc[1] - vc[0]))/(fc[1]-fc[0])
        b = vc[0] - fc[0]*a
        dataParList.append({'id':controllerAttrDic[controllerAttribute][0], 'a':a,'b':b})

        if not controllerList.has_key(controllerName):
            if controllerName in customBsController:
                limit = None
                if  controllerName not in customBsControllerLimitRemove:
                    limit = customBsController[controllerName]
                controllers.append(getControllerInfo(controllerName, headinverseMat, isLookAt, lookAtLocalPosition,limit = limit))
            else:
                controllers.append(getControllerInfo(controllerName,headinverseMat,isLookAt,lookAtLocalPosition))
            controllerList[controllerName] = [controllerId,{},controllers[-1]]
            controllerId += 1
            if isLookAt:
                EyeParameterDict[controllerName]["lookAtLocalPosition"] = {'x': lookAtLocalPosition[0], 'y': lookAtLocalPosition[1], 'z': lookAtLocalPosition[2]}

        if not transfromAttr.has_key(attribute):
            if not controllerList[controllerName][1].has_key(attribute):
                controllerList[controllerName][1][attribute] = len(controllerList[controllerName][1])+9
                maxV = -1
                minV = 0
                if cmds.objExists(controllerName+"."+attribute):
                    if cmds.attributeQuery(attribute, node=controllerName, mne=True)\
                        and cmds.attributeQuery(attribute,node =controllerName,mxe=True):
                        minV = cmds.attributeQuery(attribute, node=controllerName, min=True)[0]
                        maxV = cmds.attributeQuery(attribute, node=controllerName, max=True)[0]
                controllerList[controllerName][2]['customAttrs'].append({'attrName': attribute,'min':minV,'max':maxV})





    for v in EyeParameterDict.values():
        eyesPara.append(v)
    addMirrorInfo(controllers,'_L','_R')
    for i in range(len(controllerAttrDic)):
        weightControlMap.append({'controlId':None,'attributeId':None})

    for id,controllerName,attribute in controllerAttrDic.itervalues():
        attributeId = 0
        if transfromAttr.has_key(attribute):
            attributeId = transfromAttr[attribute]
        else:
            attributeId = controllerList[controllerName][1][attribute]
        weightControlMap[id]['controlId'] = controllerList[controllerName][0]
        weightControlMap[id]['attributeId'] = attributeId
        # weightControlMap.append({'controlId':controllerList[controllerName][0],'attributeId':attributeId})

    close_chin_follow()

    threshold = 0.001

    FaceParameter['faceElements'] = []
    for i, [bsNode,bsid] in enumerate(bsExpIndexes):
        if bsNode in eyeCtrJointMap:
            attrData = bsid.split(":")
            cmds.setAttr(bsNode + "." + attrData[0], float(attrData[1]))
        elif bsNode in customBsController:
            if len(bsid)>2:
                callbackBlock = bsid[2]
                callbackBlock[0](callbackBlock[2])
            else:
                cmds.setAttr(bsNode + "."+bsid[0],bsid[1])
        else:
            cmds.setAttr(bsNode + '.weight[{0}]'.format(bsid), 1)
        cmds.refresh()
        FaceParameter['faceElements'].append({})
        faceElements = FaceParameter['faceElements'][-1]
        faceElements['jointsOffset'] = []
        faceElements['jointsIndex'] = []
        faceElements['bsInfo'] = get_bs_info(bs_node_name)
        jointsOffset = faceElements['jointsOffset']
        jointsIndex = faceElements['jointsIndex']

        for j, joint in enumerate(joints):
            if eyeCtrJointMap.has_key(bsNode) and eyeJointCtlMap.has_key(joint):
                continue
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
            distance += abs(jointsInfo[j]['baseTransform']['rotation']['x'] - r.x)
            distance += abs(jointsInfo[j]['baseTransform']['rotation']['y'] - r.y)
            distance += abs(jointsInfo[j]['baseTransform']['rotation']['z'] - r.z)
            distance += abs(jointsInfo[j]['baseTransform']['rotation']['w'] - r.w)

            if distance > threshold:
                offQu = baseQuat[j].conjugate() * r
                jointsIndex.append(j)
                jointsOffset.append({'position': {'x': jointMat[12]- jointsInfo[j]['baseTransform']['position']['x'],
                                                  'y': jointMat[13]- jointsInfo[j]['baseTransform']['position']['y'],
                                                  'z': jointMat[14]- jointsInfo[j]['baseTransform']['position']['z']},
                                     'rotation': {'x': offQu.x, 'y': offQu.y, 'z': offQu.z, 'w': offQu.w, }})
        if bsNode in eyeCtrJointMap:
            attrData = bsid.split(":")
            cmds.setAttr(bsNode + "." + attrData[0], 0)
        elif bsNode in customBsController:
            if len(bsid)>2:
                callbackBlock = bsid[2]
                callbackBlock[1](callbackBlock[2])
            else:
                cmds.setAttr(bsNode + "." + bsid[0], 0)
        else:
            cmds.setAttr(bsNode + '.weight[{0}]'.format(bsid), 0)
    add_default(FaceParameter)
    add_switch_map(FaceParameter)
    dir_path = os.path.dirname(path)
    check_same_ctrl(FaceParameter)
    if not os.path.isdir(dir_path):
        os.makedirs(dir_path)
    with open(path, "wb") as f:
        json.dump(FaceParameter, f, indent=4)
    if temp_eye_cons:
        cmds.delete(temp_eye_cons)


def testRig(fileName = "PL", type=1, bs="blendShape49"):
    head = "Head_M_spare"
    if type == 0:
        head = "Head_M"
        bs = ""

    face_rig_export("E:/projects/TestbedDev/Assets/Build/Art/Character/FaceRigData/"+ fileName +".json",
                     type,
                     cmds.listRelatives(head, ad=1, type="joint"),
                     bs)


def test():
    head = "Head_M_spare"
    bs = "YG_Head_bs"
    path = "D:/work/x3_face_rig_export/YG.json"
    joints = cmds.listRelatives(head, ad=1, type="joint")

    face_rig_export(path, CORE, joints, bs)
