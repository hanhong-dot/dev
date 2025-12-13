# coding:utf-8
# python maya plugin for MyToolsDemo

import sys
sys.path.append(r'D:\dev\apps\oem')
from maya import cmds
from maya.api import OpenMaya as om


def maya_useNewAPI():
    pass


kPluginCmdName = 'X3pipelineTools'
kPluginVendor='linhuan'
kPluginVersion='2024.03.21'

import pipline_menu




# Menu and Shelf
# ----------------------------------------------------------------------
def removeMenu(menuName=kPluginCmdName):
    """remove menu when plugin unload"""
    if cmds.menu(menuName, q=True, exists=True):
        cmds.deleteUI(menuName, menu=True)


def makeMenu(menuName=kPluginCmdName):
    import pipline_menu
    """make menu when plugin load"""
    removeMenu(menuName)
    pipline_menu.create_pipline_menu(menuName)




def create_pipline_menu(menuName):
    # 检查菜单是否已存在，如果存在则删除
    if cmds.menu(menuName, exists=True):

        cmds.deleteUI(menuName, menu=True)

    # 创建菜单
    pipeline_menu = cmds.menu(menuName, label=u'X3 Pipeline Tools', parent='MayaWindow', tearOff=True)

    cmds.menuItem(label='模型检测', parent=pipeline_menu, command=perform_model_check)
# Plugin class
# ----------------------------------------------------------------------
class X3pipelineTools(om.MPxCommand):
    def __init__(self):
        super(X3pipelineTools, self).__init__()

    def doIt(self, args):
        print('starting %s'%kPluginCmdName)
        try:
            import MyWindow
            reload(MyWindow)
            MyWindow.main()
        except Exception as ex:
            cmds.error(ex.message())

    @staticmethod
    def creator():
        return X3pipelineTools()


# Initialize
# ----------------------------------------------------------------------
def initializePlugin(mobject):
    """Initialize the plug-in and add menu"""
    errMsg = u'Failed to register command: %s\n' % kPluginCmdName
    plugin = om.MFnPlugin(mobject, kPluginVendor, kPluginVersion)
    try:
        plugin.registerCommand(kPluginCmdName, X3pipelineTools.creator)
        makeMenu(menuName=kPluginCmdName)
        # makeShelf(shelfName=kPluginCmdName)
    except:
        sys.stderr.write(errMsg)
        raise

# Uninitialize
# ----------------------------------------------------------------------
def uninitializePlugin(mobject):
    """Uninitialize the plug-in and delete menu"""
    plugin = om.MFnPlugin(mobject)
    try:
        plugin.deregisterCommand(kPluginCmdName)
        removeMenu(menuName=kPluginCmdName)
        # removeShelf(shelfName=kPluginCmdName)
    except:
        sys.stderr.write('Failed to unregister command: %s\n' % kPluginCmdName)
        raise