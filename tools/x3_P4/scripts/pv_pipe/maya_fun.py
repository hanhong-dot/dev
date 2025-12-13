import pymel.core as pm
from maya import mel, cmds
import os
from maya.api.OpenMaya import *


old_config = {}


def bake_root():
    attributes = ['Import|PlugInGrp|PlugInUIWidth', 'Import|PlugInGrp|PlugInUIHeight', 'Import|PlugInGrp|PlugInUIXpos', 'Import|PlugInGrp|PlugInUIYpos', 'Import|PlugInGrp|UILIndex', 'Import|IncludeGrp|MergeMode', 'Import|IncludeGrp|Geometry|UnlockNormals', 'Import|IncludeGrp|Geometry|HardEdges', 'Import|IncludeGrp|Geometry|BlindData', 'Import|IncludeGrp|Animation', 'Import|IncludeGrp|Animation|ExtraGrp|Take', 'Import|IncludeGrp|Animation|ExtraGrp|TimeLine', 'Import|IncludeGrp|Animation|ExtraGrp|BakeAnimationLayers', 'Import|IncludeGrp|Animation|ExtraGrp|Markers', 'Import|IncludeGrp|Animation|ExtraGrp|Quaternion', 'Import|IncludeGrp|Animation|ExtraGrp|ProtectDrivenKeys', 'Import|IncludeGrp|Animation|ExtraGrp|DeformNullsAsJoints', 'Import|IncludeGrp|Animation|ExtraGrp|NullsToPivot', 'Import|IncludeGrp|Animation|ExtraGrp|PointCache', 'Import|IncludeGrp|Animation|Deformation', 'Import|IncludeGrp|Animation|Deformation|Skins', 'Import|IncludeGrp|Animation|Deformation|Shape', 'Import|IncludeGrp|Animation|Deformation|ForceWeightNormalize', 'Import|IncludeGrp|Animation|SamplingPanel|SamplingRateSelector', 'Import|IncludeGrp|Animation|SamplingPanel|CurveFilterSamplingRate', 'Import|IncludeGrp|Animation|CurveFilter', 'Import|IncludeGrp|Animation|ConstraintsGrp|Constraint', 'Import|IncludeGrp|Animation|ConstraintsGrp|CharacterType', 'Import|IncludeGrp|CameraGrp|Camera', 'Import|IncludeGrp|LightGrp|Light', 'Import|IncludeGrp|Audio', 'Import|AdvOptGrp|UnitsGrp|DynamicScaleConversion', 'Import|AdvOptGrp|UnitsGrp|UnitsSelector', 'Import|AdvOptGrp|AxisConvGrp|AxisConversion', 'Import|AdvOptGrp|AxisConvGrp|UpAxis', 'Import|AdvOptGrp|UI|ShowWarningsManager', 'Import|AdvOptGrp|UI|GenerateLogData', 'Import|AdvOptGrp|FileFormat|Obj|ReferenceNode', 'Import|AdvOptGrp|FileFormat|Max', 'ds|ReferenceNode', 'Import|AdvOptGrp|FileFormat|Max', 'ds|Texture', 'Import|AdvOptGrp|FileFormat|Max', 'ds|Material', 'Import|AdvOptGrp|FileFormat|Max', 'ds|Animation', 'Import|AdvOptGrp|FileFormat|Max', 'ds|Mesh', 'Import|AdvOptGrp|FileFormat|Max', 'ds|Light', 'Import|AdvOptGrp|FileFormat|Max', 'ds|Camera', 'Import|AdvOptGrp|FileFormat|Max', 'ds|AmbientLight', 'Import|AdvOptGrp|FileFormat|Max', 'ds|Rescaling', 'Import|AdvOptGrp|FileFormat|Max', 'ds|Filter', 'Import|AdvOptGrp|FileFormat|Max', 'ds|Smoothgroup', 'Import|AdvOptGrp|FileFormat|Motion', '_Base|MotionFrameCount', 'Import|AdvOptGrp|FileFormat|Motion', '_Base|MotionFrameRate', 'Import|AdvOptGrp|FileFormat|Motion', '_Base|MotionActorPrefix', 'Import|AdvOptGrp|FileFormat|Motion', '_Base|MotionRenameDuplicateNames', 'Import|AdvOptGrp|FileFormat|Motion', '_Base|MotionExactZeroAsOccluded', 'Import|AdvOptGrp|FileFormat|Motion', '_Base|MotionSetOccludedToLastValidPos', 'Import|AdvOptGrp|FileFormat|Motion', '_Base|MotionAsOpticalSegments', 'Import|AdvOptGrp|FileFormat|Motion', '_Base|MotionASFSceneOwned', 'Import|AdvOptGrp|FileFormat|Biovision', '_BVH|MotionCreateReferenceNode', 'Import|AdvOptGrp|FileFormat|MotionAnalysis', '_HTR|MotionCreateReferenceNode', 'Import|AdvOptGrp|FileFormat|MotionAnalysis', '_HTR|MotionBaseTInOffset', 'Import|AdvOptGrp|FileFormat|MotionAnalysis', '_HTR|MotionBaseRInPrerotation', 'Import|AdvOptGrp|FileFormat|Acclaim', '_ASF|MotionCreateReferenceNode', 'Import|AdvOptGrp|FileFormat|Acclaim', '_ASF|MotionDummyNodes', 'Import|AdvOptGrp|FileFormat|Acclaim', '_ASF|MotionLimits', 'Import|AdvOptGrp|FileFormat|Acclaim', '_ASF|MotionBaseTInOffset', 'Import|AdvOptGrp|FileFormat|Acclaim', '_ASF|MotionBaseRInPrerotation', 'Import|AdvOptGrp|FileFormat|Acclaim', '_AMC|MotionCreateReferenceNode', 'Import|AdvOptGrp|FileFormat|Acclaim', '_AMC|MotionDummyNodes', 'Import|AdvOptGrp|FileFormat|Acclaim', '_AMC|MotionLimits', 'Import|AdvOptGrp|FileFormat|Acclaim', '_AMC|MotionBaseTInOffset', 'Import|AdvOptGrp|FileFormat|Acclaim', '_AMC|MotionBaseRInPrerotation', 'Import|AdvOptGrp|Dxf|WeldVertices', 'Import|AdvOptGrp|Dxf|ObjectDerivation', 'Import|AdvOptGrp|Dxf|ReferenceNode', 'Import|AdvOptGrp|Performance|RemoveBadPolysFromMesh', 'Export|PlugInGrp|PlugInUIWidth', 'Export|PlugInGrp|PlugInUIHeight', 'Export|PlugInGrp|PlugInUIXpos', 'Export|PlugInGrp|PlugInUIYpos', 'Export|PlugInGrp|UILIndex', 'Export|IncludeGrp|Geometry|SmoothingGroups', 'Export|IncludeGrp|Geometry|expHardEdges', 'Export|IncludeGrp|Geometry|TangentsandBinormals', 'Export|IncludeGrp|Geometry|SmoothMesh', 'Export|IncludeGrp|Geometry|SelectionSet', 'Export|IncludeGrp|Geometry|BlindData', 'Export|IncludeGrp|Geometry|AnimationOnly', 'Export|IncludeGrp|Geometry|Instances', 'Export|IncludeGrp|Geometry|ContainerObjects', 'Export|IncludeGrp|Geometry|Triangulate', 'Export|IncludeGrp|Geometry|GeometryNurbsSurfaceAs', 'Export|IncludeGrp|Animation', 'Export|IncludeGrp|Animation|ExtraGrp|UseSceneName', 'Export|IncludeGrp|Animation|ExtraGrp|RemoveSingleKey', 'Export|IncludeGrp|Animation|ExtraGrp|Quaternion', 'Export|IncludeGrp|Animation|BakeComplexAnimation', 'Export|IncludeGrp|Animation|BakeComplexAnimation|BakeFrameStart', 'Export|IncludeGrp|Animation|BakeComplexAnimation|BakeFrameEnd', 'Export|IncludeGrp|Animation|BakeComplexAnimation|BakeFrameStep', 'Export|IncludeGrp|Animation|BakeComplexAnimation|ResampleAnimationCurves', 'Export|IncludeGrp|Animation|BakeComplexAnimation|HideComplexAnimationBakedWarning', 'Export|IncludeGrp|Animation|Deformation', 'Export|IncludeGrp|Animation|Deformation|Skins', 'Export|IncludeGrp|Animation|Deformation|Shape', 'Export|IncludeGrp|Animation|CurveFilter', 'Export|IncludeGrp|Animation|CurveFilter|CurveFilterApplyCstKeyRed', 'Export|IncludeGrp|Animation|CurveFilter|CurveFilterApplyCstKeyRed|CurveFilterCstKeyRedTPrec', 'Export|IncludeGrp|Animation|CurveFilter|CurveFilterApplyCstKeyRed|CurveFilterCstKeyRedRPrec', 'Export|IncludeGrp|Animation|CurveFilter|CurveFilterApplyCstKeyRed|CurveFilterCstKeyRedSPrec', 'Export|IncludeGrp|Animation|CurveFilter|CurveFilterApplyCstKeyRed|CurveFilterCstKeyRedOPrec', 'Export|IncludeGrp|Animation|CurveFilter|CurveFilterApplyCstKeyRed|AutoTangentsOnly', 'Export|IncludeGrp|Animation|PointCache', 'Export|IncludeGrp|Animation|PointCache|SelectionSetNameAsPointCache', 'Export|IncludeGrp|Animation|ConstraintsGrp|Constraint', 'Export|IncludeGrp|Animation|ConstraintsGrp|Character', 'Export|IncludeGrp|CameraGrp|Camera', 'Export|IncludeGrp|LightGrp|Light', 'Export|IncludeGrp|Audio', 'Export|IncludeGrp|EmbedTextureGrp|EmbedTexture', 'Export|IncludeGrp|BindPose', 'Export|IncludeGrp|PivotToNulls', 'Export|IncludeGrp|BypassRrsInheritance', 'Export|IncludeGrp|InputConnectionsGrp|IncludeChildren', 'Export|IncludeGrp|InputConnectionsGrp|InputConnections', 'Export|AdvOptGrp|UnitsGrp|DynamicScaleConversion', 'Export|AdvOptGrp|UnitsGrp|UnitsSelector', 'Export|AdvOptGrp|AxisConvGrp|UpAxis', 'Export|AdvOptGrp|UI|ShowWarningsManager', 'Export|AdvOptGrp|UI|GenerateLogData', 'Export|AdvOptGrp|FileFormat|Obj|Triangulate', 'Export|AdvOptGrp|FileFormat|Obj|Deformation', 'Export|AdvOptGrp|FileFormat|Motion', '_Base|MotionFrameCount', 'Export|AdvOptGrp|FileFormat|Motion', '_Base|MotionFromGlobalPosition', 'Export|AdvOptGrp|FileFormat|Motion', '_Base|MotionFrameRate', 'Export|AdvOptGrp|FileFormat|Motion', '_Base|MotionGapsAsValidData', 'Export|AdvOptGrp|FileFormat|Motion', '_Base|MotionC', 'Export|AdvOptGrp|FileFormat|Motion', '_Base|MotionASFSceneOwned', 'Export|AdvOptGrp|FileFormat|Biovision', '_BVH|MotionTranslation', 'Export|AdvOptGrp|FileFormat|Acclaim', '_ASF|MotionTranslation', 'Export|AdvOptGrp|FileFormat|Acclaim', '_ASF|MotionFrameRateUsed', 'Export|AdvOptGrp|FileFormat|Acclaim', '_ASF|MotionFrameRange', 'Export|AdvOptGrp|FileFormat|Acclaim', '_ASF|MotionWriteDefaultAsBaseTR', 'Export|AdvOptGrp|FileFormat|Acclaim', '_AMC|MotionTranslation', 'Export|AdvOptGrp|FileFormat|Acclaim', '_AMC|MotionFrameRateUsed', 'Export|AdvOptGrp|FileFormat|Acclaim', '_AMC|MotionFrameRange', 'Export|AdvOptGrp|FileFormat|Acclaim', '_AMC|MotionWriteDefaultAsBaseTR', 'Export|AdvOptGrp|Fbx|AsciiFbx', 'Export|AdvOptGrp|Fbx|ExportFileVersion', 'Export|AdvOptGrp|Dxf|Deformation', 'Export|AdvOptGrp|Dxf|Triangulate', 'Export|AdvOptGrp|Collada|Triangulate', 'Export|AdvOptGrp|Collada|SingleMatrix', 'Export|AdvOptGrp|Collada|FrameRate']
    edit_config = {}
    for attr in attributes:
        try:
            value = mel.eval("FBXProperty %s -q" % attr)
            if old_config.get(attr, value) != value:
                edit_config[attr] = value
            old_config[attr] = value
        except RuntimeError:
            pass
    print edit_config


def fbx_export(path=None, st=1, et=120):
    if st is not None:
        pm.playbackOptions(e=1, min=st)
    if et is not None:
        pm.playbackOptions(e=1, max=et)
    pm.FBXResetExport()
    pm.mel.eval("FBXExportSmoothingGroups -v true")
    pm.mel.eval("FBXExportInputConnections -v false")
    pm.mel.eval("FBXProperty  Export|IncludeGrp|Geometry|SmoothingGroups -v true")
    pm.mel.eval("FBXProperty  Export|IncludeGrp|Geometry|SmoothMesh -v true")
    pm.mel.eval("FBXProperty  Export|IncludeGrp|Geometry|ContainerObjects -v true")
    pm.mel.eval("FBXProperty  Export|IncludeGrp|Geometry|Triangulate -v false")
    pm.mel.eval("FBXProperty  Export|AdvOptGrp|UI|ShowWarningsManager -v false")
    pm.mel.eval("FBXProperty  Export|IncludeGrp|Audio -v false")
    pm.mel.eval("FBXProperty  Export|IncludeGrp|CameraGrp|Camera -v false")
    pm.mel.eval("FBXProperty  Export|IncludeGrp|LightGrp|Light -v false")

    pm.mel.eval("FBXProperty Export|IncludeGrp|Animation|BakeComplexAnimation -v true")
    pm.mel.eval("FBXProperty Export|IncludeGrp|Animation|BakeComplexAnimation|BakeFrameStart -v %s" % st)
    pm.mel.eval("FBXProperty Export|IncludeGrp|Animation|BakeComplexAnimation|BakeFrameEnd -v %s" % et)
    pm.mel.eval("FBXProperty Export|IncludeGrp|Animation|BakeComplexAnimation|BakeFrameStep -v 1")
    pm.mel.eval("FBXProperty Export|IncludeGrp|Animation|BakeComplexAnimation|ResampleAnimationCurves -v true")
    pm.exportSelected(path, type="FBX export", f=1)


def load_bs_plug():
    version = int(round(float(pm.about(q=1, v=1))))
    path = os.path.abspath(__file__+"/../pv_bs/maya%04d/pv_bs.mll" % version)
    if not os.path.isfile(path):
        return pm.warning("can not find ocd")
    if not pm.pluginInfo(path, q=1, l=1):
        pm.loadPlugin(path)


def convert_bs(st=None, et=None):
    if st is not None:
        pm.playbackOptions(e=1, min=st)
    if et is not None:
        pm.playbackOptions(e=1, max=et)
    load_bs_plug()
    pm.mel.convert_bs()


def _get_selected_polygon(root, polygons):
    if root.type() == "mesh":
        polygon = root.getParent()
        if polygon not in polygons:
            polygons.append(polygon)
    elif root.type() == "transform":
        for child in root.getChildren():
            _get_selected_polygon(child, polygons)


def get_selected_polygons():
    polygons = []
    for sel in pm.selected(o=1, type="transform"):
        _get_selected_polygon(sel, polygons)
    return polygons


def convert_triangulate():
    polygons = get_selected_polygons()
    for polygon in polygons:
        pm.polyTriangulate(polygon, ch=True)
        pm.select(polygon)
        pm.mel.BakeNonDefHistory()


def get_st_et():
    st = int(round(pm.playbackOptions(q=1, min=1)))
    et = int(round(pm.playbackOptions(q=1, max=1)))
    return st, et


def scene_name():
    return str(pm.sceneName().basename().splitext()[0])


def get_name_joint(root):
    data = {}
    for joint in pm.listRelatives(root, ad=1):
        name = joint.name().split("|")[-1].split(":")[-1]
        data[name] = joint
    return data


def get_joint_matrix(*roots):
    name_joints = [get_name_joint(root) for root in roots]
    joint_matrix = []
    for name in name_joints[0].keys():
        joints = [name_joint.get(name, None) for name_joint in name_joints]
        if None in joints:
            continue
        joint_matrix.append(joints)
    return joint_matrix


def get_root():
    root = pm.ls("|root")
    if len(root) == 1:
        return root[0]
    deform = pm.ls("DeformationSystem", "*:DeformationSystem")
    if len(deform) != 1:
        return "can not find deformation"
    deform = deform[0]
    root = pm.joint(None, n="root")
    dup = deform.duplicate()[0]
    temp_group = pm.group(em=1, n="constraint_group")
    for src, dst in get_joint_matrix(deform, dup):
        pm.parent(pm.parentConstraint(src, dst), temp_group)
        src.scale.connect(dst.scale)
    for child in dup.getChildren():
        child.setParent(root)
    pm.delete(deform)
    return root


def add_skin():
    polygons = get_selected_polygons()
    print polygons
    root = get_root()
    for polygon in polygons:
        bs = pm.listHistory(polygon, type="blendShape")
        if len(bs):
            bs[0].envelope.set(0)
        print root, polygon
        pm.skinCluster(root, polygon, mi=1, tsb=1)
        if len(bs):
            bs[0].envelope.set(1)


def rename_sg():
    for sg in pm.ls(type="shadingEngine"):
        for mat in sg.surfaceShader.inputs():
            try:
                sg.rename(mat.name() + "_SG")
            except:
                pass


def debug_five_edge_face():
    pm.mel.polyCleanupArgList(4, ["0", "1", "1", "0", "1", "0", "0", "0", "0", "1e-05", "0",
                                  "1e-05", "0", "1e-05", "0", "-1", "0", "0"])


def convert_face_mat():
    for sg in pm.ls(type="shadingEngine"):
        for elem in sg.elements():
            print elem
            if hasattr(elem, "type") and elem.type() == "mesh":
                try:
                    pm.sets("initialShadingGroup", e=1, forceElement=elem.f[:])
                    pm.sets(sg, e=1, forceElement=elem.f[:])
                except:
                    pass


def abc_export(path=None, st=None, et=None):
    # check mesh
    if cmds.ls(sl=1, type="mesh", o=1):
        pm.mel.warning("please selected polygon, don't selected vertex, Edge,Face")
        return
    check_same_name()
    if st is not None:
        pm.playbackOptions(e=1, min=st)
    if et is not None:
        pm.playbackOptions(e=1, max=et)

    # check_all_triangulate()
    root = u" -root ".join([u""]+[sel.fullPath() for sel in pm.selected()])
    j = u"-frameRange {st} {et} -stripNamespaces -uvWrite -writeFaceSets -worldSpace -writeUVSets -dataFormat ogawa{root} -file {path}"
    pm.AbcExport(j=j.format(**locals()))


def default_abc_path():
    return pm.sceneName()[:-2]+"abc"


def _check_same_name():
    polygons = cmds.ls(sl=1, type="transform")
    for polygon in polygons:
        if "|" in polygon:
            new_name = polygon.replace("|", "_")
            if new_name[0] == "_":
                new_name = new_name[1:]
            cmds.rename(polygon, new_name)


def check_same_name():
    for i in range(3):
        _check_same_name()


def is_shape(polygon_name, typ="mesh"):
    if not cmds.objExists(polygon_name):
        return False
    if cmds.objectType(polygon_name) != "transform":
        return False
    shapes = cmds.listRelatives(polygon_name, s=1, f=1)
    if not shapes:
        return False
    if cmds.objectType(shapes[0]) != typ:
        return False
    return True


def api_ls(*names):
    selection_list = MSelectionList()
    for name in names:
        selection_list.add(name)
    return selection_list


def check_triangulate(fn_mesh):
    for polygon_id in range(fn_mesh.numPolygons):
        connects = fn_mesh.getPolygonVertices(polygon_id)
        if len(connects) != 3:
            return False
    return True


def check_all_triangulate():
    sel = cmds.ls(sl=1)
    polygons = [polygon for polygon in cmds.ls(sl=1, o=1, type="transform") if is_shape(polygon)]
    for polygon in polygons:
        fn_mesh = MFnMesh(api_ls(polygon).getDagPath(0))
        if check_triangulate(fn_mesh):
            continue
        pm.polyTriangulate(polygon, ch=True)
        pm.select(polygon)
        pm.mel.BakeNonDefHistory()
    cmds.select(cmds.ls(sel))


def doit():
    from maya import cmds
    # cmds.select([u'group1|pSphere1', u'group2|pSphere1'])
    # check_all_triangulate()
    abc_export(path="D:/work/x3_pv/aaa.abc", st=1, et=10)
    # convert_triangulate()