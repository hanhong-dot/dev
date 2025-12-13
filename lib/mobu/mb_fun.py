# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       : mb_fun
# Describe   : 说明描述
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2023/5/19__10:31
# -------------------------------------------------------
from pyfbsdk import *
import os


def find_model(_name):
    u"""
    通过名字查找节点
    :param _name:
    :return:
    """
    _model = FBFindModelByLabelName(_name)
    if _model and _model.FullName:
        return _model


def find_by_shotname(shotname):
    u"""
    通过短名查找节点
    :param _name:
    :return:
    """
    objs = FBComponentList()
    FBFindObjectsByName(shotname, objs, True, False)
    if objs:
        return objs


def get_all_characters():
    u"""
    获取场景中所有的角色
    :return:
    """
    return FBSystem().Scene.Characters


def get_all_namespaces():
    u"""
    获取场景中所有的命名空间
    :return:
    """
    namespaces = []
    models = get_all_nodes_in_scene()
    for model in models:
        if model.LongName and ':' in model.LongName:
            namespaces.append(model.LongName.split(':')[0])
    if namespaces:
        return list(set(namespaces))
    return []


def get_character_by_namespace(name_space):
    all_characters = get_all_characters()
    for character in all_characters:
        if character.LongName and character.LongName.startswith(name_space + ':'):
            return character
    return None


def get_charcter_hip_node(character):
    return character.GetModel(FBBodyNodeId.kFBHipsNodeId)


def get_root_node_by_node(node):
    parent = node.Parent
    if not parent:
        return node
    while parent:
        node = parent
        parent = node.Parent
    return node


def mb_get_current_file():
    # type: () -> str
    u"""
    当前文件名(文件路径+文件名)
    :return:
    """
    return FBApplication().FBXFileName


def get_character_rig_node(character):
    hip_node = get_charcter_hip_node(character)
    return get_root_node_by_node(hip_node)


def get_all_nodes_in_scene():
    # type: () -> List[FBModel]
    ret = []
    get_children(ret, FBSystem().Scene.RootModel)
    return ret


def get_current_character():
    return FBApplication().CurrentCharacter


def get_children(childrenList, Root=FBSystem().Scene.RootModel, condition_callback=None):
    for childModel in Root.Children:
        if condition_callback is not None:
            if not condition_callback(childModel):
                continue
        childrenList.append(childModel)
        get_children(childrenList, childModel, condition_callback)


def bake_to_control_rig(ikfk=True, character=None):
    plotoptions = FBPlotOptions()
    plotoptions.ConstantKeyReducerKeepOneKey = False
    plotoptions.PlotAllTakes = False
    plotoptions.PlotOnFrame = True
    plotoptions.PlotPeriod = FBTime(0, 0, 0, 1)
    plotoptions.PlotTranslationOnRootOnly = False
    plotoptions.PreciseTimeDiscontinuities = False
    plotoptions.RotationFilterToApply = FBRotationFilter.kFBRotationFilterNone
    plotoptions.UseConstantKeyReducer = False
    if character is None:
        character = get_current_character()
    control_rig = character.GetCurrentControlSet()
    if not control_rig:
        character.CreateControlRig(ikfk)
    if character.ActiveInput != True:
        character.PlotAnimation(FBCharacterPlotWhere.kFBCharacterPlotOnControlRig, plotoptions)


def set_current_character(character):
    FBApplication().CurrentCharacter = character
    FBSystem().Scene.Evaluate()


def get_handle_constraints_target_list(character):
    left_hand_point_name = 'HPoint_hand_L'
    right_handle_point_name = 'HPoint_hand_R'
    __point_nodes = []
    __data = []
    if not character:
        return __data
    root = character.GetModel(FBBodyNodeId.kFBHipsNodeId)
    child_nodes = get_all_children(root)
    if not child_nodes:
        return __data
    for node in child_nodes:
        if node.Name == left_hand_point_name or node.Name == right_handle_point_name:
            __point_nodes.append(node)
    if not __point_nodes:
        return __data
    for point_node in __point_nodes:
        targe_list = get_node_constraints_targe_list(point_node)
        if targe_list:
            __data.extend(targe_list)
    if __data:
        __data = list(set(__data))

    return __data


def get_node_constraints_targe_list(node):
    __data = {}
    if not node:
        return __data
    targe_list = []
    for c in FBSystem().Scene.Constraints:
        if not c:
            continue
        source = c.ReferenceGet(1)
        if not source:
            continue
        if source == node:
            targe = c.ReferenceGet(0)
            if targe:
                targe_list.append(targe)
    return targe_list


def get_all_children(root):
    children = []
    for child in root.Children:
        children.append(child)
        children.extend(get_all_children(child))
    return children


def export_character_fbx(character, fbx_file_path):
    lOptions = FBFbxOptions(False)
    lOptions.SaveCharacter = True
    lOptions.SaveControlSet = True
    lOptions.SaveCharacterExtension = True
    lApp = FBApplication()
    lApp.SaveCharacterRigAndAnimation(fbx_file_path, character, lOptions)


def export_selected_models_fbx(fbx_file_path):
    lOptions = FBFbxOptions(False)

    lOptions.SaveSelectedModelsOnly = True
    lOptions.UseASCIIFormat = True

    lOptions.BaseCameras = False
    lOptions.CameraSwitcherSettings = False
    lOptions.CurrentCameraSettings = False
    lOptions.GlobalLightingSettings = False
    lOptions.TransportSettings = False

    lApp = FBApplication()
    return lApp.FileSave(fbx_file_path, lOptions)


def cancel_selected():
    for m in FBSystem().Scene.Components:
        if hasattr(m, "Selected"):
            m.Selected = False


def GetParentRecursive(pChild, pModelList):
    pModelList.append(pChild)
    lParent = pChild.Parent
    if lParent:
        GetParentRecursive(lParent, pModelList)


def GetChildsRecursive(pParent, pModelList):
    pModelList.append(pParent)
    for lChild in pParent.Children:
        GetChildsRecursive(lChild, pModelList)


def bake_to_skeleton(character=None):
    plotoptions = FBPlotOptions()
    plotoptions.ConstantKeyReducerKeepOneKey = False
    plotoptions.PlotAllTakes = False
    plotoptions.PlotOnFrame = True
    plotoptions.PlotPeriod = FBTime(0, 0, 0, 1)
    plotoptions.PlotTranslationOnRootOnly = False
    plotoptions.PreciseTimeDiscontinuities = False
    plotoptions.RotationFilterToApply = FBRotationFilter.kFBRotationFilterNone
    plotoptions.UseConstantKeyReducer = False
    if character is None:
        character = get_current_character()
    if character.ActiveInput == True:
        character.PlotAnimation(FBCharacterPlotWhere.kFBCharacterPlotOnSkeleton, plotoptions)


def bake_all(all_takes=True):
    bake_targets(get_all_nodes_in_scene(), all_takes)


def find_modelnull_noeds_by_name(name):
    objs = FBComponentList()
    FBFindObjectsByName(name, objs, False, False)
    result = []
    for o in objs:
        if o.__class__ == FBModelNull:
            result.append(o)
    return result


def bake_targets(targets, all_takes=True):
    for e in targets:
        e.Translation.SetAnimated(True)
        e.Rotation.SetAnimated(True)
        e.Scaling.SetAnimated(True)

    lOptions = FBPlotOptions()
    lOptions.PlotAllTakes = all_takes
    lOptions.PlotOnFrame = True
    lOptions.PlotPeriod = FBTime(0, 0, 0, 1)  # 表示首帧
    lOptions.PlotLockedProperties = True
    lOptions.UseConstantKeyReducer = False
    lOptions.ConstantKeyReducerKeepOneKey = True
    lOptions.RotationFilterToApply = FBRotationFilter.kFBRotationFilterUnroll

    # FBSystem().CurrentTake.PlotTakeOnSelected(lOptions)
    FBSystem().CurrentTake.PlotTakeOnObjects(lOptions, targets)


def open_mb_file(fbxfile):
    # type: (str) -> bool
    u"""
    打开mb文件
    :param file_path:
    :return:
    """
    if isinstance(fbxfile, unicode):
        fbxfile = fbxfile.encode('utf8')
    if not os.path.exists(fbxfile):
        return False, u'文件不存在: {}'.format(fbxfile)
    app = FBApplication()
    app.FileOpen(fbxfile)
    return True


def get_current_take():
    # type: () -> FBTake
    return FBSystem().CurrentTake


def mb_file_new():
    app = FBApplication()
    app.FileNew()
    return True, u'新建文件成功'
