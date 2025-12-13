# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       : exoprt_ani_fbx
# Describe   : 导出动画fbx基本函数
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2023/4/27__17:12
# -------------------------------------------------------
import maya.cmds as cmds
import maya.mel as mel
import lib.maya.process.maya_bake as _maya_bake

def export_animation_clip_fbx(objlist, export_path,clip='', dis=1, hi=1, startframe=0, endframe=0, bake=True, bakestart=0, bakeend=1,
                         animationonly=1, UpAxis='y', warning=0, instances=0, log=0, constrains=0, shape=0,usescenename=0):
    u"""
    导出动画fbx
    :param objlist:
    :return:
    """
    try:
        mel.eval('FBXProperty Export|AdvOptGrp|UI|ShowWarningsManager -v {}'.format(warning))
        mel.eval('FBXProperty Export|AdvOptGrp|UI|GenerateLogData -v {}'.format(log))
    except:
        pass

    if hi == True:
        cmds.select(objlist, hierarchy=1)
    else:
        cmds.select(objlist)

    #设置
    mel.eval("FBXExportSplitAnimationIntoTakes -clear")
    _cmd = '''FBXExportSplitAnimationIntoTakes -v {} {} {};FBXExportInstances -v {};FBXExportAnimationOnly -v {};FBXExportGenerateLog -v {};FBXExportConstraints -v {};FBXExportUseSceneName -v {};FBXExportUpAxis  {};FBXExport -f "{}" -s;'''.format(
        clip,bakestart,bakeend,instances, animationonly, log, constrains, usescenename,UpAxis, export_path)
    if bake == True:
        _maya_bake.bake(objlist, startframe=startframe, endframe=endframe, shape=shape)
        # _cmd += '''FBXExportBakeComplexAnimation -v true;FBXExportBakeComplexStart -v {};FBXExportBakeComplexEnd -v {};'''.format(
        #     bakestart, bakeend)
    if dis == True:
        _disconnet(objlist)
    # 设置起始帧
    cmds.playbackOptions(min=startframe)
    # 设置结束帧
    cmds.playbackOptions(max=endframe)
    # 执行命令
    try:
        mel.eval(_cmd)
        mel.eval("FBXExportSplitAnimationIntoTakes -clear")
        return export_path
    except:
        return False



def export_animation_fbx(objlist, export_path, dis=1, hi=1, startframe=0, endframe=0, bake=1, bakestart=0, bakeend=1,
                         animationonly=1, UpAxis='y', warning=0, instances=0, log=0, constrains=0, shape=0,usescenename=1):
    u"""
    导出动画fbx
    :param objlist:
    :return:
    """
    try:
        mel.eval('FBXProperty Export|AdvOptGrp|UI|ShowWarningsManager -v {}'.format(warning))
        mel.eval('FBXProperty Export|AdvOptGrp|UI|GenerateLogData -v {}'.format(log))
    except:
        pass

    if hi == True:
        cmds.select(objlist, hierarchy=1)
    else:
        cmds.select(objlist)
    _cmd = '''FBXExportInstances -v {};FBXExportAnimationOnly -v {};FBXExportGenerateLog -v {};FBXExportConstraints -v {};FBXExportUseSceneName -v {};FBXExportUpAxis  {};FBXExport -f "{}" -s;'''.format(
        instances, animationonly, log, constrains, usescenename,UpAxis, export_path)

    if dis == True:
        _disconnet(objlist)
    if bake == True:
        _maya_bake.bake(objlist, startframe=bakestart, endframe=bakeend, shape=shape)
        # _cmd += '''FBXExportBakeComplexAnimation -v true;FBXExportBakeComplexStart -v {};FBXExportBakeComplexEnd -v {};FBXExportBakeComplexStep -v 1'''.format(
        #     bakestart, bakeend)
    mel.eval("FBXExportSplitAnimationIntoTakes -clear")
    # 设置起始帧
    cmds.playbackOptions(min=startframe)
    # 设置结束帧
    cmds.playbackOptions(max=endframe)
    # 执行命令
    try:
        mel.eval(_cmd)
        # mel.eval("FBXExportBakeComplexAnimation -v false")
        return export_path
    except:
        return False


def _disconnet(objs=['Roots']):
    u"""
    断开连接
    :return:
    """
    if objs:
        for obj in objs:
            if obj and cmds.ls(obj):
                cons = cmds.listConnections(obj, s=1, p=1, c=1)
                if cons:
                    for i in range(0, (len(cons) - 1), 2):
                        try:
                            cmds.disconnectAttr(cons[i + 1], cons[i])
                        except:
                            pass
