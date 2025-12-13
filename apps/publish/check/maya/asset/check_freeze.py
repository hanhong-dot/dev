# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       : check_freeze
# Describe   : 绑定监测joins 世界座标
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2023/1/30__18:50
# -------------------------------------------------------
import lib.maya.node.grop as group_common
import lib.common.loginfo as info
import lib.maya.node.nodes as node_common
import maya.cmds as cmds

CHECKJOINS = ['Roots', 'RootMotion']


class Check(object):
    u"""
    检测文件中(组下)是否有未freeze物体
    """

    def __init__(self, TaskData, grpsname=None, is_checkobjs=True):
        u"""
        检测文件（特定组下)是否有未freeze物体
        :param grpsname: 组名(如果为None，则会检测文件中所有大组),不为空时，则为list，例如['MODEL']
        :param is_checkobjs: 为True时，检测组及组下物体；为False时，则仅检测大组列表，不检测组下物体
        """
        self._taskdata = TaskData
        self._assettype = self._taskdata.asset_type
        self.groups = grpsname
        self.is_checkobjs = is_checkobjs
        self._error = u"请检查以下物体未在原点(或世界坐标轴向不正确),请检查"
        self.end = u"已检测骨骼freeze('Roots', 'RootMotion')"
        self._end = u"此项不用检测"
        if self.groups == None:
            self.groups = group_common.BaseGroup().get_root_groups()

    def checkinfo(self):
        if self._assettype and self._assettype.lower() in ['npc', 'enemy']:
            errlist = self.run()
            _infolist = []
            if errlist:
                _infolist.append(self._error)
                _infolist.extend(errlist)

            if errlist:
                return False, info.displayErrorInfo(objList=_infolist)
            else:
                return True, info.displayInfo(objList=[self.end])
        else:
            return True, info.displayInfo(objList=[self._end])

    def run(self):
        u"""
        freeze物体检测
        :return: errdict
        """
        errlist = []
        checkobjs = []
        if self.groups and self.is_checkobjs == True:
            for i in range(len(self.groups)):
                if cmds.ls(self.groups[i]):
                    objs = group_common.Group(self.groups[i]).select_group_transforms()
                    if objs:
                        checkobjs.extend(objs)
        if self.groups:
            checkobjs.extend(self.groups)
        if checkobjs:
            errlist = self._freezecheck(checkobjs)
        return errlist

    def fix(self):
        u"""
        修复未freeze物体（将未freeze物体，进行freeze)
        :return: 为True时，修复成功,为False时，未修复成功
        """
        errlist = self.run()
        result = True
        if errlist:
            result = self._freeze(errlist)
        errlist = self.run()
        if errlist:
            result = self._freeze(errlist)

        return result

    def _freeze(self, objlist):
        u"""
        将objlist列表中的物体(或组)进行freeze
        :param objlist: 需要freeze的物体列表
        :return: True，修复成功,False，未修复成功
        """
        import maya.mel as mel
        no_freezelist = []
        _Num = [1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0]
        _piv = [0, 0, 0]
        if objlist:
            # 解锁
            node_common.BaseNodeProcess().unlock_nodelist(objlist)
            # freeze
            for obj in objlist:
                cmds.xform(obj, m=_Num, ws=1)
                cmds.xform(obj, piv=_piv, ws=1)

        if no_freezelist:
            return False
        else:
            return True

    def _freezecheck(self, objlist):
        u"""
        检查objs中没有frezze的物体
        :param objs: 物体列表
        :return: nofreezelist
        """
        _Num = [1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0]
        _piv = [0, 0, 0, 0, 0, 0]
        _error = []
        _errorn = []
        if objlist:
            _errorn = []
            for obj in objlist:
                if obj and cmds.ls(obj):
                    xfom_ws = cmds.xform(obj, q=1, m=1, ws=1)
                    for i in range(len(xfom_ws)):
                        if abs(xfom_ws[i] - _Num[i]) >= 0.0001:
                            _errorn.append(obj)
                            break
            # _errorn=[i for i in objlist if (i and cmds.ls(i) and cmds.xform(i, q=1, m=1, ws=1) != _Num)]
        _errorp = [i for i in objlist if (i and cmds.ls(i) and cmds.xform(i, q=1, piv=1, ws=1) != _piv)]
        if _errorn:
            _error.extend(_errorn)
        if _errorp:
            _error.extend(_errorp)
        if _error:
            return list(set(_error))


if __name__ == '__main__':
    # 测试代码
    import method.shotgun.get_task as get_task

    reload(get_task)
    _filename = cmds.file(q=1, exn=1)

    test_task_data = get_task.TaskInfo(_filename, 'X3', 'maya', 'publish')
    _handle = Check(test_task_data)
    print(_handle.run())
