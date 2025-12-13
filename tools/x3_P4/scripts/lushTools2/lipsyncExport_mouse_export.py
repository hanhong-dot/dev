# coding:utf-8

import maya.cmds as cmds
import maya.api.OpenMaya as om
import json

# 获取当前选中的 Set 的名称
# selected_set = cmds.ls("lipzip_set", type='objectSet')[0]

# 获取选中 Set 中包含的所有物体的路径
# set_members = cmds.sets(selected_set, query=True)
set_members = [
    u'Head_rivet_L_99_lod',
    u'Head_rivet_L_101_lod',
    u'Head_rivet_L_100_lod',
    u'Head_rivet_L_98_lod',
    u'Head_rivet_L_109_lod',
    u'Head_rivet_L_104_lod',
    u'Head_rivet_L_106_lod',
    u'Head_rivet_L_107_lod',
    u'Head_rivet_L_108_lod',
    u'Head_rivet_L_105_lod',
    u'Head_rivet_L_111',
    u'Head_rivet_L_112',
    u'Head_rivet_R_108_lod',
    u'Head_rivet_R_109_lod',
    u'Head_rivet_R_106_lod',
    u'Head_rivet_R_104_lod',
    u'Head_rivet_R_107_lod',
    u'Head_rivet_R_105_lod',
    u'Head_rivet_M_10_lod',
    u'Head_rivet_M_15_lod',
    u'Head_rivet_L_37',
    u'Head_rivet_L_36',
    u'Head_rivet_L_52_lod',
    u'Head_rivet_L_38',
    u'Head_rivet_L_51_lod',
    u'Head_rivet_L_56_lod',
    u'Head_rivet_L_60_lod',
    u'Head_rivet_L_62_lod',
    u'Head_rivet_L_54_lod',
    u'Head_rivet_L_57_lod',
    u'Head_rivet_L_55',
    u'Head_rivet_L_53',
    u'Head_rivet_L_59_lod',
    u'Head_rivet_L_61',
    u'Head_rivet_L_63_lod',
    u'Head_rivet_L_64',
    u'Head_rivet_M_8_lod',
    u'Head_rivet_M_9_lod',
    u'Head_rivet_M_7_lod',
    u'Head_rivet_L_65',
    u'Head_rivet_L_67',
    u'Head_rivet_L_66',
    u'Head_rivet_L_68',
    u'Head_rivet_L_82',
    u'Head_rivet_R_99_lod',
    u'Head_rivet_R_98_lod',
    u'Head_rivet_R_100_lod',
    u'Head_rivet_R_101_lod',
    u'Head_rivet_R_82',
    u'Head_rivet_R_64',
    u'Head_rivet_R_65',
    u'Head_rivet_R_68',
    u'Head_rivet_R_67',
    u'Head_rivet_R_66',
    u'Head_rivet_R_57_lod',
    u'Head_rivet_R_60_lod',
    u'Head_rivet_R_54_lod',
    u'Head_rivet_R_61',
    u'Head_rivet_R_62_lod',
    u'Head_rivet_R_63_lod',
    u'Head_rivet_R_59_lod',
    u'Head_rivet_R_56_lod',
    u'Head_rivet_R_55',
    u'Head_rivet_R_52_lod',
    u'Head_rivet_R_51_lod',
    u'Head_rivet_R_53',
    u'Head_rivet_R_38',
    u'Head_rivet_R_36',
    u'Head_rivet_R_37',
    u'Head_rivet_R_111',
    u'Head_rivet_L_114',
    u'Head_rivet_M_21',
    u'Head_rivet_R_112',
    u'Head_rivet_L_113',
    u'Head_rivet_R_114',
    u'Head_rivet_L_116',
    u'Head_rivet_R_116',
    u'Head_rivet_L_115',
    u'Head_rivet_R_113',
    u'Head_rivet_R_115',
    u'Head_rivet_L_117',
    u'Head_rivet_R_117']
set_upMembers = []
set_downMembers = []

leftLipPath = "Head_rivet_L_54_lod"
rightLipPath = "Head_rivet_R_54_lod"
upLipPath = "Head_rivet_M_15_lod"
downLipPath = "Head_rivet_M_8_lod"

# 用于判断骨骼点属于上半部分还是下半部分
midLipTargetPath = "Head_rivet_R_54_lod"


# 用于获取骨骼TR信息，返回[trans,rot_quat]
def get_transAndRot(joint_name):
    sel = om.MSelectionList()
    sel.add(joint_name)
    dagPath = sel.getDagPath(0)
    matrix = dagPath.inclusiveMatrix()
    local_matrix = matrix * dagPath.exclusiveMatrixInverse()
    local_matrix[1] *= -1
    local_matrix[2] *= -1
    local_matrix[4] *= -1
    local_matrix[8] *= -1
    local_matrix[12] *= -0.01
    local_matrix[13] *= 0.01
    local_matrix[14] *= 0.01
    # 获取局部变换的旋转和位移
    trans_matrix = om.MTransformationMatrix(local_matrix)
    trans = trans_matrix.translation(om.MSpace.kTransform)
    rotation_quat = trans_matrix.rotation(asQuaternion=True)
    return [trans, rotation_quat]


# 自动区分上下唇骨骼点
def detect_up_down():
    del set_upMembers[:]
    del set_downMembers[:]

    fk_jaw = cmds.ls("FKJaw_M")[0]

    cmds.setAttr(fk_jaw + ".ZipLip_L", 0)
    cmds.setAttr(fk_jaw + ".ZipLip_R", 0)
    cmds.setAttr(fk_jaw + ".translateY", -2)

    targetTrans = get_transAndRot(midLipTargetPath)[0]

    for m in set_members:
        translation = get_transAndRot(m)[0]
        if translation.y > targetTrans.y:
            set_upMembers.append(m)
        else:
            set_downMembers.append(m)

    cmds.setAttr(fk_jaw + ".ZipLip_L", 0)
    cmds.setAttr(fk_jaw + ".ZipLip_R", 0)
    cmds.setAttr(fk_jaw + ".translateY", 0)


def get_lip_sync_zip_data():
    # 获取根节点的名称
    root = cmds.ls(assemblies=True)[0]
    upJointMaxVec = downJointMaxVec = None
    upJointMinVec = downJointMinVec = None
    leftJointMinVec = None
    rightJointMinVec = None

    upJointTPoseVec = None
    downJointTPoseVec = None

    lipEles = []
    pathes = []
    sites = []  # 0 left,1 right, 2 middle.
    versites = []  # 0 up,1 down.
    spLip = {}
    data = {"spLip": spLip, "lipElements": lipEles}

    # 填充上下唇区域数组
    detect_up_down()
    # print(len(set_upMembers))
    # print(len(set_downMembers))
    # print(len(set_members))

    # 查找名称为 "FKJaw_M" 的物体
    fk_jaw = cmds.ls("FKJaw_M")[0]

    defaultTRS = []
    # cmds.setAttr(fk_jaw + ".Falloff_Radius", 1)
    cmds.setAttr(fk_jaw + ".ZipLip_L", 0)
    cmds.setAttr(fk_jaw + ".ZipLip_R", 0)
    cmds.setAttr(fk_jaw + ".translateY", -2)
    for m in set_members:
        # 获取相对于根节点的路径
        relative_path = cmds.ls(m, long=True)[0] #  .replace("|" + root + "|", "")
        # 转换为 Unity 的路径格式
        unity_path = relative_path.replace("|", "/")
        # 剔除根节点
        unity_path = "/".join(unity_path.split("/")[2:])
        pathes.append(unity_path)
        if "_L_" in m:
            sites.append(0)
        elif "_R_" in m:
            sites.append(1)
        else:
            sites.append(2)

        if m in set_upMembers:
            versites.append(0)
        elif m in set_downMembers:
            versites.append(1)
        else:
            print("Not in up or down sets: " + m)
            versites.append(1)

        [translation, rotation_quat] = get_transAndRot(m)
        defaultTRS.append({"pos": translation,
                           "rot": rotation_quat})
        if upLipPath in relative_path:
            spLip["upLip"] = unity_path
            upJointMaxVec = translation
        if downLipPath in relative_path:
            spLip["downLip"] = unity_path
            downJointMaxVec = translation
        if leftLipPath in relative_path:
            spLip["leftLip"] = unity_path
        if rightLipPath in relative_path:
            spLip["rightLip"] = unity_path

    deformTRS = []
    # cmds.setAttr(fk_jaw + ".Falloff_Radius", 5)
    cmds.setAttr(fk_jaw + ".ZipLip_L", 1)
    cmds.setAttr(fk_jaw + ".ZipLip_R", 1)
    cmds.setAttr(fk_jaw + ".translateY", -2)
    for m in set_members:
        relative_path = cmds.ls(m, long=True)[0].replace("|" + root + "|", "")
        [translation, rotation_quat] = get_transAndRot(m)
        deformTRS.append({"pos": translation,
                          "rot": rotation_quat})
        if upLipPath in relative_path:
            upJointMinVec = translation
        if downLipPath in relative_path:
            downJointMinVec = translation
        if leftLipPath in relative_path:
            leftJointMinVec = translation
        if rightLipPath in relative_path:
            rightJointMinVec = translation

    # Get TPose Up/down
    cmds.setAttr(fk_jaw + ".ZipLip_L", 0)
    cmds.setAttr(fk_jaw + ".ZipLip_R", 0)
    cmds.setAttr(fk_jaw + ".translateY", 0)
    for item in [upLipPath, downLipPath]:
        relative_path = cmds.ls(item, long=True)[0].replace("|" + root + "|", "")
        [translation, rotation_quat] = get_transAndRot(relative_path)
        if upLipPath in relative_path:
            upJointTPoseVec = translation
        if downLipPath in relative_path:
            downJointTPoseVec = translation

    for i in range(len(deformTRS)):
        t = deformTRS[i]["pos"] - defaultTRS[i]["pos"]
        r = deformTRS[i]["rot"] * defaultTRS[i]["rot"].inverse()
        lipEles.append({"path": pathes[i],
                        "site": sites[i],
                        "verSite": versites[i],
                        "pos": {
                            "x": t.x,
                            "y": t.y,
                            "z": t.z
                        },
                        "rot": {
                            "x": r.x,
                            "y": r.y,
                            "z": r.z,
                            "w": r.w
                        }})

    spLip["closeVertMax"] = (upJointMaxVec - downJointMaxVec).length() ** 2
    a = (upJointMinVec - downJointMinVec).length() ** 2
    b = (upJointTPoseVec - downJointTPoseVec).length() ** 2
    spLip["closeVertMin"] = min(a, b)
    spLip["closeHor"] = (rightJointMinVec - leftJointMinVec).length() ** 2
    # cmds.setAttr(fk_jaw + ".Falloff_Radius", 1)
    cmds.setAttr(fk_jaw + ".ZipLip_L", 0)
    cmds.setAttr(fk_jaw + ".ZipLip_R", 0)
    cmds.setAttr(fk_jaw + ".translateY", 0)
    # with open("mouse_data.json", "w") as f:
    #     json.dump(data, f, indent=4)
    return data

# get_lip_sync_zip_data()