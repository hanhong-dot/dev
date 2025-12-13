# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       : unknow_clean
# Describe   : 清理海龟节点，unknow节点，unknow 插件
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2022/6/21__10:54
# -------------------------------------------------------
import maya.cmds as cmds

noDelList = ['Shoulder_L_bind_RBFposereader', 'Shoulder_R_bind_RBFposereader',
             'Spine2_M_bind_RBFposereader', 'Wrist_L_bind_RBFposereader', 'Wrist_R_bind_RBFposereader',
             'squash_FFD_Squash_sur_lcMatrixToJoint', 'squash_FFD_Squash_sur_lcSurfaceRibbon',
             'squash_M_dn_sur_lcMatrixToJoint', 'squash_M_dn_sur_lcSurfaceRibbon',
             'squash_M_up_sur_lcMatrixToJoint', 'squash_M_up_sur_lcSurfaceRibbon', 'squash_lcChainVolume']


def unknowdelete(unknowNode=0, unknowPlugin=0, turtle=0, anzov=0):
    '''
    删除无用节点，unknowplgin,海龟节点
    :param unknowNode: 为1时，清理无用节点,为0时，不清理
    :param unknowPlugin: 为1时，清理unknowPlugin,为0时，不清理unknowPlugin
    :param turtle: 为1时，清理海龟节点,为0时，不清理海龟节点
    :return:
    '''
    import time
    time.sleep(1)
    fileName = cmds.file(q=1, shn=1, sn=1)
    if unknowNode == 1:
        unknow = cmds.ls(type='unknown')
        for u in unknow:
            try:
                cmds.lockNode(u, l=0)
                cmds.delete(u)
                print 'delete --- ' + u
            except:
                print 'something wrong.pass it!'
        unknowDag = cmds.ls(type='unknownDag')
        for u in unknowDag:
            if u not in noDelList:
                try:
                    cmds.lockNode(u, l=0)
                    cmds.delete(u)
                    print 'delete --- ' + u
                except:
                    print 'something wrong.pass it!'
        # cleanUnuseNode()
    if unknowPlugin == 1:
        unknownPlugins = cmds.unknownPlugin(list=1, q=1)
        PluginList = []
        if unknownPlugins:
            for plug in unknownPlugins:
                try:
                    cmds.unknownPlugin(plug, r=1)
                    print '【%s】插件已删除' % plug
                except:
                    cmds.warning(u'【%s】多余插件未删除，请检查' % plug)
    if turtle == 1:
        turtleNodes = cmds.ls(type='ilrBakeLayer') + cmds.ls(type='ilrUIOptionsNode') + cmds.ls(
            type='ilrOptionsNode') + cmds.ls(type='ilrBakeLayerManager') + cmds.ls(type='fosterParent')
        for node in turtleNodes:
            # 非参考才执行删除
            if cmds.referenceQuery(node, inr=1):
                pass
            else:
                if cmds.ls(node):
                    cmds.lockNode(node, l=0)
                    cmds.delete(node)
    if anzov == 1:
        anzolist = ['anzovinDeleteScript', 'AnzovinInterfaceNode', 'anzovinSetupScript', 'fmSceneOpenPluginCheckScript']
        for i in range(len(anzolist)):
            if cmds.ls(anzolist[i]):
                nodes = cmds.ls(anzolist[i])
                for node in nodes:
                    if cmds.ls(node):
                        try:
                            cmds.lockNode(node, lock=False)
                            cmds.delete(node)
                        except:
                            pass
    # cleanAbBlastPanel()
    HIKClean()
    UnlockLambertNode()
    eliminate_outliner_callback()
    cleanUnuseExpression()

    return 0

def cleanUnuseExpression():
    exNode = cmds.ls(typ='script')
    if exNode:
        for ii in exNode:
            if 'xgmRefresh' in ii or 'xgen' in ii:
                cmds.delete(ii)

def cleanUnuseNode():
    import maya.mel as mel
    mel.eval('hyperShadePanelMenuCommand("", "deleteUnusedNodes")')

def eliminate_outliner_callback():
    import maya.mel as mel
    all_panels = cmds.getPanel(type="outlinerPanel") or []
    for panel in all_panels:
        sc = cmds.outlinerEditor(panel, q=True, selectCommand=True)
        if sc != None:
            mel.eval('outlinerEditor -edit -selectCommand "" "{}";'.format(panel))
            cmds.file(uiConfiguration=False)  # mark as do not save ui info within scene file
            print("KILL INFECTED outliner!!!")


def cleanAbBlastPanel():
    evilEvent = ['CgAbBlastPanelOptChangeCallback','onModelChange3dc']
    for model_panel in cmds.getPanel(typ="modelPanel"):
        callback = cmds.modelEditor(model_panel, query=True, editorChanged=True)
        if callback in evilEvent:
            cmds.modelEditor(model_panel, edit=True, editorChanged="")
    if cmds.objExists('uiConfigurationScriptNode'):
        cmds.delete('uiConfigurationScriptNode')

def UnlockLambertNode():
    cmds.lockNode("initialShadingGroup", l=0, lu=0)

def HIKClean():
    hiknode = cmds.ls(typ=('HIKSkeletonGeneratorNode','HIKProperty2State'))
    if hiknode:
        for ii in hiknode:
            if cmds.objectType(ii) == 'HIKProperty2State':
                conn = cmds.listConnections(ii+'.message',s=False,d=True)
                if conn:
                    bone = cmds.listConnections(conn[0],s=True,d=False)
                    if len(bone) == 1:
                        cmds.delete(ii)
                else:
                    cmds.delete(ii)
            elif cmds.objectType(ii) == 'HIKSkeletonGeneratorNode':
                conn = cmds.listConnections(ii,s=True,d=True)
                if conn:
                    pass
                else:
                    cmds.delete(ii)

if __name__ == "__main__":
    unknowNode = 1
    unknowPlugin = 1
    turtle = 1
    anzov = 1
    unknowdelete(unknowNode, unknowPlugin, turtle, anzov)
