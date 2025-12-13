# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       : scriptjob
# Describe   : 说明描述
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2022/6/21__10:16
# -------------------------------------------------------
import maya.cmds as cmds
import lib.common.fileio as fileio


def lod_script_job():
    u"""
    加载maya运行脚本
    """
    #
    mayadefender()
    # 开启maya时执行的命令
    sceneopened()
    # 打开maya文件时执行的命令
    postsceneread()
    #
    # # 保存文件
    scenesaved()
    pass


def mayadefender():
    u"""
    加载防御脚本
    """
    _load_maya_umbrella()


def scenesaved():
    '''保存文件时执行的脚本
    '''
    _order = "saveMaya"

    cmds.scriptJob(event=('SceneSaved', _kill_job))
    # cmds.scriptJob(event=('SceneSaved', 'import pymel.core as pm'))
    # 清理

    cmd = 'import lib.maya.unknow_clean as unknowclean\nreload(unknowclean)\nunknowclean.unknowdelete(1,1,0,0)'
    try:
        cmds.scriptJob(event=('SceneSaved', cmd))
    except:
        pass
    cmds.scriptJob(event=('SceneSaved', _save_work_json))
    cmds.scriptJob(event=('SceneSaved', _delete_unuse_node))


def _save_work_json():
    import apps.tools.maya.work_save as work_save
    try:

        work_save.work_write_json_maya()
    except:
        pass


def _delete_unuse_node():
    import maya.mel as mel

    mel.eval('hyperShadePanelMenuCommand("hyperShadePanel1", "deleteUnusedNodes")')


def _set_gpu_override():
    import maya.mel as mel
    cmds.evaluationManager(mode='parallel')
    mel.eval(
        "optionVar -iv gpuOverride  false; if(false) {turnOnOpenCLEvaluatorActive();} else {turnOffOpenCLEvaluatorActive();  };")


def sceneopened():
    u"""
    open maya文件时执行的命令
    """
    # _order = "openMaya"
    # if _order:
    #     # 杀毒
    #     cmds.scriptJob(event=('SceneOpened', _kill_job))
    # 关闭材质刷新
    cmds.scriptJob(event=('SceneOpened', 'cmds.renderThumbnailUpdate(False)'))
    #
    # cmds.scriptJob(event=('SceneOpened', _set_DirectX11))

    # 清理病毒
    # cmds.scriptJob(event=('SceneOpened', _kill_job))
    #
    # cmds.scriptJob(event=('SceneOpened', _set_gpu_override))
    #
    # cmds.scriptJob(event=('NewSceneOpened', _set_gpu_override))

    cmds.scriptJob(event=('SceneOpened', _set_fps))
    cmds.scriptJob(event=('NewSceneOpened', _set_fps))

    # cmds.scriptJob(event=('NewSceneOpened', _set_frame_range))

    #
    # cmds.scriptJob(event=('SceneOpened', _load_maya_umbrella))

    # cmds.scriptJob(event=('SceneOpened', _load_colormanage))
    # 加载色彩管理
    # cmds.scriptJob(event=('SceneOpened', _load_colormanage))

    # cmds.scriptJob(event=('SceneOpened', load_shapes_brush))


def _load_maya_umbrella():
    import sys
    sys.path.append(r'Z:\dev\tools\maya\maya_umbrella\scripts')
    from maya_umbrella import get_defender_instance

    defender = get_defender_instance()
    defender.setup()


def _load_colormanage():
    import apps.tools.maya.load_colorspace.load_colormanage as load_colormanage
    enable_corlor_managenment = cmds.colorManagementPrefs(q=1, cmEnabled=1)
    if enable_corlor_managenment == True:
        load_colormanage.ColorManageLoad('x3').load_colorsapce()


def _add_maya_env():
    import sys
    sys.path.append('Z:/dev')
    import apps.launch.maya.interface.add_environment as _config
    _config.maya_env_add()


def _set_DirectX11(_eng='DirectX11'):
    u"""
    设置显示为DFirectX 11显示(vp2)
    :return:
    """
    import maya.mel as mel
    if mel.eval('optionVar -query vp2RenderingEngine') != _eng:
        mel.eval("optionVar -sv vp2RenderingEngine {}".format(_eng))
        mel.eval('updateVP2RenderingEngine')


def postsceneread():
    '''打开maya文件时执行的脚本
    '''
    _order = "postscene"
    if _order:
        # 清理
        # cmd = 'import lib.maya.unknow_clean as unknowclean\nreload(unknowclean)\nunknowclean.unknowdelete(1,1,0,0)'
        # # 清理无用插件,无用节点
        # cmds.scriptJob(event=('PostSceneRead', cmd))

        cmds.scriptJob(event=('NewSceneOpened', _set_fps))
        cmds.scriptJob(event=('SceneOpened', _set_fps))
        cmds.scriptJob(event=('PostSceneRead', _set_fps))

        # cmds.scriptJob(event=('NewSceneOpened', _set_frame_range))
        # cmds.scriptJob(event=('PostSceneRead', _set_frame_range))

        # # 加载色彩管理
        # cmds.scriptJob(event=('PostSceneRead', _load_colormanage))
        # cmds.scriptJob(event=('PostSceneRead', color_space_reapply))
        # # 设置显示贴图
        # cmds.scriptJob(event=('PostSceneRead', _set_texmaxresolution))
        # # 设置解锁贴图列表
        # cmds.scriptJob(event=('PostSceneRead', _set_textlistlu))


def _set_frame_range(start_frame=0, end_frame=150, ast=0, aet=200):
    u"""
    设置帧范围
    :param start_frame:
    :param end_frame:
    :return:
    """
    cmds.playbackOptions(min=start_frame, max=end_frame, ast=ast, aet=aet)


def _set_textlistlu():
    textlists = cmds.ls(type='defaultTextureList')
    for textlist in textlists:
        try:
            cmds.lockNode(textlist, l=0, lu=0)
        except:
            pass


def _set_fps():
    cmds.currentUnit(time='ntsc')


def _set_texmaxresolution():
    try:
        cmds.setAttr("hardwareRenderingGlobals.textureMaxResolution", 1024)
    except:
        pass


def clear_maya_pttq():
    '''
    清除maya启动文件普天同庆恶意代码
    '''
    import os
    # 清除animImportExport.pres.mel
    _list = ['ja_JP', 'zh_CN', 'en_US']
    _mayapath = os.getenv('MAYA_LOCATION')
    if _list:
        for _filePath in _list:
            _file = '{}/resources/l10n/{}/plug-ins/animImportExport.pres.mel'.format(_mayapath, _filePath)
            if _file and os.path.exists(_file):
                _clear_file(_file)
    # 清除userSetup
    _scriptpath = os.getenv('MAYA_SCRIPT_PATH')
    if _scriptpath:
        for _path in _scriptpath.split(';'):
            _usersetup = '{}/userSetup.mel'.format(_path)
            # print '_usersetup=',_usersetup
            if _usersetup and os.path.exists(_usersetup):
                _clear_file(_usersetup)
            _usersetuppy = '{}/userSetup.py'.format(_path)
            if _usersetuppy and os.path.exists(_usersetuppy):
                _clear_file(_usersetuppy)
            # 清除大将军
            _vaccine = '{}/vaccine.py'.format(_path)
            if _vaccine and os.path.exists(_vaccine):
                os.remove(_vaccine)
            _vaccinePyc = '{}/vaccine.pyc'.format(_path)
            if _vaccinePyc and os.path.exists(_vaccinePyc):
                os.remove(_vaccinePyc)


def color_space_reapply():
    u"""
    引自maya reapplyRules
    :return:
    """
    # Get the list of color managed nodes.
    cmNodes = cmds.colorManagementPrefs(query=True, colorManagedNodes=True)

    # Avoid warning if mental ray plugin isn't loaded.
    if cmds.pluginInfo('Mayatomr', query=True, loaded=True):
        cmNodes = cmNodes + cmds.ls(type='mentalrayIblShape')

    # Avoid warning if mtoa plugin isn't loaded.
    if cmds.pluginInfo('mtoa', query=True, loaded=True):
        cmNodes = cmNodes + cmds.ls(type='aiImage')

    # Loop over nodes: get each node's file path, evaluate rules, set
    # the color space.
    for nodeName in cmNodes:

        # If ignore file rules is set for that node, don't reapply on it.
        ignoreColorSpaceFileRules = cmds.getAttr(
            nodeName + '.ignoreColorSpaceFileRules')
        if ignoreColorSpaceFileRules:
            continue

        # We should not need to know the list of file name attribute names
        # for all types of color managed nodes, as more color managed node
        # types can be added in the future.
        #
        # As of 5-Nov-2014, we know that the colorManagedNodes query
        # will return two types of nodes: image plane nodes, which have an
        # image file attribute, and file texture nodes, which have a file
        # name attribute.
        #
        # Additionally, we are relying on identical attribute naming for
        # the color space across all node types, which is very weak.
        attrList = cmds.listAttr(nodeName)
        fileAttrName = 'imageName'
        if 'imageName' in attrList:
            fileAttrName = 'imageName'
        elif 'fileTextureName' in attrList:
            fileAttrName = 'fileTextureName'
        elif 'filename' in attrList:  # aiImage
            fileAttrName = 'filename'
        else:
            fileAttrName = 'texture'

        fileName = cmds.getAttr(nodeName + '.' + fileAttrName)

        colorSpace = cmds.colorManagementFileRules(evaluate=fileName)

        cmds.setAttr(nodeName + '.colorSpace', colorSpace, type='string')


def _clear_file(_filename):
    isPttq = False

    _filedata = fileio.read(_filename)
    _newTxt = ''
    if _filedata:
        for _data in _filedata.split('\n'):
            # print '---',_data
            if "// Maya Mel UI Configuration File." in _data:
                print(u'- %s -发现恶意代码，进行清除。' % _filename)
                isPttq = True
                break

            elif 'vaccine' in _data and 'evalDeferred' in _data:
                isPttq = True
            else:
                _newTxt += _data + '\n'

    if isPttq:
        fileio.write(_newTxt, _filename)


def load_shapes_brush():
    from lib.maya.plugin import plugin_load
    from maya import cmds, mel, utils
    import sys
    plug_path = r'Z:\dev\tools\x3_P4\modules\SHAPESBrush\scripts'
    sys.path.append(plug_path)

    plugin_load(['SHAPESBrush'])
    utils.executeDeferred(addMenuItem)


def addMenuItem():
    import maya.mel as mel
    if not cmds.about(batch=True):
        mel.eval("source SHAPESBrushCreateMenuItems; SHAPESBrushAddMenuCommand;")


def _kill_job():
    '''
    处理普天同庆病毒
    :return:
    '''
    import os

    import lib.maya.removes as removes
    import maya.mel as mel
    # 杀毒
    try:
        removes.startup()
    except:
        pass
    # 替换恶意代码函数
    try:
        _cmd = 'global proc autoUpdatcAttrEd(){}'
        mel.eval(_cmd)
        mel.eval('source "C:/Program Files/Autodesk/Maya2018/scripts/others/showEditor.mel"')
        mel.eval('autoUpdateAttrEd')
    except:
        pass
    # 清除普天同庆恶意代码
    try:
        clear_maya_pttq()
    except:
        pass
    # 清除animImportExport.pres.mel
    try:
        _list = ['ja_JP', 'zh_CN', 'en_US']
        _mayapath = os.getenv('MAYA_LOCATION')
        if _list:
            for _filePath in _list:
                _file = '{}/resources/l10n/{}/plug-ins/animImportExport.pres.mel'.format(_mayapath, _filePath)
                if _file and os.path.exists(_file):
                    _clear_file(_file)
    except:
        pass
    # 清除userSetup
    try:
        _scriptpath = os.getenv('MAYA_SCRIPT_PATH')
        if _scriptpath:
            for _path in _scriptpath.split(';'):
                _usersetup = '{}/userSetup.mel'.format(_path)
                # print '_usersetup=',_usersetup
                if _usersetup and os.path.exists(_usersetup):
                    _clear_file(_usersetup)
                _usersetuppy = '{}/userSetup.py'.format(_path)
                if _usersetuppy and os.path.exists(_usersetuppy):
                    _clear_file(_usersetuppy)
                # 清除大将军
                _vaccine = '{}/vaccine.py'.format(_path)
                if _vaccine and os.path.exists(_vaccine):
                    os.remove(_vaccine)
                _vaccinePyc = '{}/vaccine.pyc'.format(_path)
                if _vaccinePyc and os.path.exists(_vaccinePyc):
                    os.remove(_vaccinePyc)
    except:
        pass
