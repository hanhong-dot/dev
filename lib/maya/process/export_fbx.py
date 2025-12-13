# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       : export_fbx
# Describe   : 导出fbx
# version    : v0.01
# Author     : linhuan角场附近景点
# Email      : hanhong@papegames.net
# DateTime   : 2022/6/16__15:29
# -------------------------------------------------------

import maya.cmds as cmds
import maya.mel as mel



def fbxCommonOptions():
    # mel.eval("FBXExportSmoothingGroups -v true")
    # mel.eval("FBXExportSmoothMesh -v true")
    # mel.eval("FBXExportHardEdges -v true")
    # mel.eval("FBXExportTangents -v false")
    # mel.eval("FBXExportInstances -v false")
    # mel.eval('FBXExportTriangulate -v false')

    mel.eval("FBXExportBakeComplexAnimation -v false")
    # mel.eval('FBXExportAnimationOnly -v false')
    # mel.eval('FBXExportApplyConstantKeyReducer -v false')
    # mel.eval('FBXExportCacheFile -v false')

    # mel.eval('FBXExportFileVersion -v FBX201600')
    # mel.eval('FBXExportInAscii -v false')
    # mel.eval('FBXExportAxisConversionMethod convertAnimation')
    # mel.eval('FBXExportScaleFactor 10')

    # mel.eval('FBXExportConvertUnitString cm')
    # mel.eval("FBXExportUseSceneName -v false")
    # mel.eval("FBXExportQuaternion -v euler")
    #
    # # Constraints
    # mel.eval("FBXExportConstraints -v false")
    # # Cameras
    #
    # # Lights
    # mel.eval("FBXExportLights -v false")
    # # Embed Media
    # mel.eval("FBXExportEmbeddedTextures -v false")
    # # Connections
    # mel.eval("FBXExportInputConnections -v false")
    # # Axis Conversion
    # mel.eval("FBXExportUpAxis y")

def export_fbx(objlist, export_path, hi=1,triangulate=0,tangents=0, soothgroups=1, soothmesh=1, skins=1, shapes=1, instances=0, embtex=0,
               cameras=0, lights=0, log=0, constrains=0, skeletondef=0, UpAxis='z', warning=0):
    u"""
    导出fbx
    """
    try:
        mel.eval('FBXProperty Export|AdvOptGrp|UI|ShowWarningsManager -v {}'.format(warning))
        mel.eval('FBXProperty Export|AdvOptGrp|UI|GenerateLogData -v {}'.format(log))
        # mel.eval("FBXExportBakeComplexAnimation -v false")
    except:
        pass
    # fbxCommonOptions()
    if hi == True:
        cmds.select(objlist, hierarchy=1)
    else:
        cmds.select(objlist)

    _cmd = '''FBXExportTriangulate -v {};FBXExportTangents -v {};FBXExportSmoothingGroups -v {};FBXExportSmoothMesh -v {};FBXExportSkins -v {}; FBXExportShapes -v
    {};FBXExportInstances -v {};FBXExportEmbeddedTextures -v {};FBXExportCameras -v {}; FBXExportLights -v
    {};FBXExportGenerateLog -v {};FBXExportConstraints -v {};FBXExportSkeletonDefinitions -v
    {};FBXExportUpAxis {};FBXExport -f "{}" -s;'''.format(triangulate,tangents,soothgroups, soothmesh, skins, shapes, instances, embtex,
                                                          cameras, lights, log, constrains, skeletondef, UpAxis,
                                                          export_path)

    try:
        mel.eval(_cmd)
        return export_path
    except:
        return False
