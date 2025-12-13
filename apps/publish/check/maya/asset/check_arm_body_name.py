# -*- coding: utf-8 -*-#
# Python     : 
# -------------------------------------------------------
# NAME       :check_arm_body_name.py
# Describe   :
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2024/11/18 17:43
# -------------------------------------------------------

import maya.cmds as cmds
import lib.common.loginfo as info

CAMS = ['persp', 'top', 'front', 'side']

OBJNAMES = ['Arm', 'Body']


class Check(object):
    def __init__(self, TaskData):
        super(Check, self).__init__()
        self.__task_data = TaskData

        self.__asset_type = self.__task_data.asset_type
        self.__title = u'检查模型名称是否符合规范("Arm","Body")'
        self.__error=u'以下模型名称不符合规范,请检查("Arm","Body")'
        self.__info=u'已检查模型名称是否符合规范("Arm","Body")'
        self.__fix_info=u'已修复模型名称'


    def checkinfo(self):
        error = self.run()
        _error_list = []
        if error:
            _error_list.append(self.__error)
            _error_list.extend(error)
        if _error_list:
            return False, info.displayErrorInfo(title=self.__title, objList=_error_list)
        else:
            return True, info.displayInfo(title=self.__info)

    def run(self):
        if self.__asset_type.lower() not in ['body', 'role','cartoon_body','cartoon_role']:
            return
        else:
            return self.__check_arm_body_name()

    def __check_arm_body_name(self):
        meshs = self.__get_meshs()
        if not meshs:
            return
        return self.__get_error_objs(meshs)

    def __get_error_objs(self, meshs):
        error_objs = []
        if not meshs:
            return error_objs
        for mesh in meshs:
            if self.__check_name(mesh) == False:
                error_objs.append(mesh)
        return error_objs

    def __check_name(self, mesh):
        __lower_list = [name.lower() for name in OBJNAMES]
        __short_mesh_name = mesh.split('|')[-1]
        __infos = __short_mesh_name.split('_')
        __result = True
        for __info in __infos:
            if __info.lower() in __lower_list and __info not in OBJNAMES:
                __result = False
                break
        return __result

    def __get_meshs(self):
        meshs = []
        root_grps = self._get_root_grps()
        for root_grp in root_grps:
            mesh_list = self._get_meshs_from_grp(root_grp)
            if mesh_list:
                meshs.extend(mesh_list)
        return meshs

    def _get_meshs_from_grp(self, grp):
        mesh_list = []
        meshs = cmds.listRelatives(grp, allDescendents=True, type='mesh', f=1)
        if meshs:
            for mesh in meshs:
                tr = cmds.listRelatives(mesh, parent=True, type='transform', f=1)
                if tr:
                    mesh_list.append(tr[0])

        return mesh_list

    def _get_root_grps(self):
        roots = cmds.ls(assemblies=True)
        root_grps = []
        for root in roots:
            __judge = self.__judge_grp(root)
            if root.split('|')[-1] not in CAMS and __judge:
                root_grps.append(root)
        return root_grps

    def __judge_grp(self, grp):
        __shape = cmds.listRelatives(grp, shapes=True)
        if __shape:
            return False
        else:
            return True


    def fix(self):
        error = self.run()
        if error:
            for obj in error:
                self.__fix_arm_body_name(obj)
            return True, info.displayInfo(title=self.__fix_info)
        else:
            return False, info.displayInfo(title=u'无需修复')

    def __fix_arm_body_name(self, obj):
        __short_mesh_name = obj.split('|')[-1]
        __infos = __short_mesh_name.split('_')
        __new_name = []

        for i in range(len(__infos)):
            __info=__infos[i]
            __info_new=__info
            for j in range(len(OBJNAMES)):
                if __info.lower() == OBJNAMES[j].lower():
                    __info_new = OBJNAMES[j]
            __new_name.append(__info_new)
        __new_name = '_'.join(__new_name)

        if __new_name != __short_mesh_name:
            try:
                cmds.rename(__short_mesh_name, __new_name)
                return True,__new_name
            except:
                return False,__new_name



