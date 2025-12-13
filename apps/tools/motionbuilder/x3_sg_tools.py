# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       : x3_sg_tools
# Describe   : X3 motionbuilder工具链
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2023/3/20__11:06
# -------------------------------------------------------
from pyfbsdk import *

#
# _dict={101:['Animation Assembly Tool','print("a")']}



menu_mgr = FBMenuManager()
menu_x3 = menu_mgr.GetMenu("X3PiplieTools")
if not menu_x3:
    menu_mgr.InsertBefore(None, "Help", "X3PiplieTools")
menu_x3= menu_mgr.GetMenu("X3PiplieTools")
menu_x3.InsertLast("动画组装工具" , 101)
menu_x3.InsertLast("检测工具" , 102)
menu_x3.InsertLast("上传工具" , 103)
menu_x3.InsertLast("道具挂点工具" , 104)
menu_x3.InsertLast("批量替换角色体工具" , 105)

menu_x3.InsertLast("Mb转换Maya工具" , 106)
def menu_event(control, event):
    if event.Id==101:
        import apps.tools.motionbuilder.AssemblyTool.assembly_ui as assembly_ui
        reload(assembly_ui)
        assembly_ui.show()
    if event.Id==102:
        import apps.publish.launch.motionbuilder.mb_checkwidget as mb_checkwidget
        reload(mb_checkwidget)
        mb_checkwidget.load_check_ui()
    if event.Id==103:
        import apps.publish.launch.motionbuilder.mb_publishwidget as mb_publishwidget
        reload(mb_publishwidget)
        mb_publishwidget.load_publish_ui()
    if event.Id==104:

        import apps.tools.motionbuilder.item_chr_link.mobu_ui as item_link_ui
        reload(item_link_ui)
        item_link_ui.show()
    if event.Id==105:
        import apps.tools.motionbuilder.mb_replace_rig.load_mb_replace_character_tool as load_mb_replace_character_tool
        reload(load_mb_replace_character_tool)
        load_mb_replace_character_tool.load_replace_character_ui()
    if event.Id==106:
        import apps.tools.motionbuilder.cover_mb_to_maya.load_mb_to_maya_tool as load_mb_to_maya_tool
        reload(load_mb_to_maya_tool)
        load_mb_to_maya_tool.load_cover_mb_to_maya_tool()


menu_x3.OnMenuActivate.Add(menu_event)



