# -*- coding: utf-8 -*-#
# Python       : python 2.7.16
# -------------------------------------------------------------------------------
# NAME         : panel
# Describe     : maya 面板相关函数
# Version      : v0.01
# Author       : linhuan
# Email        : hanhong.2022@bytedance.com
# DateTime     : 2024/5/30__13:36
# -------------------------------------------------------------------------------
# -------------------------------------------------------------------------------
# example:
# 
# -------------------------------------------------------------------------------
import maya.cmds as cmds
import maya.mel as mel


class Panel(object):
	u"""
	maya面板操作基本函数
	"""
	
	def __init__(self):
		pass
	
	def display_viewpanel(self):
		u"""
		面板显示物体
		:return:为True时，面板显示物体执行成功，为False时，面板显示物体执行失败
		"""
		try:
			_isolated_panel = self.get_viewpanel()
			cmds.editor(_isolated_panel, edit=True, lockMainConnection=True, mainListConnection='activeList')
			cmds.isolateSelect(_isolated_panel, state=0)
			return True
		except:
			False
	
	def undisplay_viewpanel(self):
		u"""
		面板关闭物体显示（不显示物体，可用于前台bake,解算等加快交互速度)
		:return:为True时，面板关闭物体显示执行成功，为False时，面板关闭物体显示执行失败
		"""
		try:
			_isolated_panel = self.get_viewpanel()
			cmds.editor(_isolated_panel, edit=True, lockMainConnection=True, mainListConnection='activeList')
			cmds.isolateSelect(_isolated_panel, state=1)
			return True
		except:
			False
	
	def set_persp_boundingBox(self):
		u"""
		设置当前视窗为独立的persp视角，并显示为boundingBox模式
		return:
		"""
		mel.eval('setNamedPanelLayout("Single Perspective View")')
		modelPanelActiv = self.get_viewpanel()
		# print('modelPanelActiv==>', modelPanelActiv)
		cmds.modelEditor(modelPanelActiv, e=1, allObjects=0)  # 首先隐藏所有物体
		cmds.modelEditor(modelPanelActiv, e=1, polymeshes=1, hud=1, ca=0, pluginShapes=0, lt=0, nurbsCurves=1,
		                 displayAppearance='boundingBox')  # 再勾起显示想要显示的内容（如：poly，curves）
	
	def set_persp_viewFit(self, objects=None, fitFactor=1.0):
		"""
		设置当前视窗为独立的persp视角，并设置适合的聚焦视觉角度。
		:param objects: 要聚焦视觉的物体（或物体列表），如果为None，则是对当前的文件里的所有物体聚焦；
		return:
		"""
		mel.eval('setNamedPanelLayout("Single Perspective View")')
		if objects is None:
			cmds.viewFit('persp', all=True, fitFactor=fitFactor)
		else:
			objs = []
			if isinstance(objects, (tuple, list)):
				objs = [i for i in objects if cmds.objExists(i)]
			elif isinstance(objects, str):
				if cmds.objExists(objects):
					objs = [objects]
			cmds.select(objs)
			cmds.viewFit('persp', fitFactor=fitFactor)
			cmds.select(cl=1)
	
	def get_viewpanel(self):
		u"""
		获得当前view面板
		:return:返回当前view面板(string)
		"""
		_isolated_panel = cmds.paneLayout('viewPanes', q=True, pane1=True)
		if _isolated_panel == 'StereoPanel':
			return 'StereoPanelEditor'
		else:
			return _isolated_panel


# if __name__ == '__main__':
# 	import libs.maya.v2_0.panel as panel_common
#
# 		# 当前view面板关闭显示物体
# 	panel_common.Panel().undisplay_viewpanel()
#
# 	# 当前view面板显示物体
# 	panel_common.Panel().display_viewpanel()
#
# 	# 设置当前视窗为独立的persp视角，并显示为boundingBox模式
# 	panel_common.Panel().set_persp_boundingBox()
#
# 	# 设置当前视窗为独立的persp视角，并设置适合的聚焦视觉角度
#
