# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       : check_hair_model
# Describe   : 检查hair资产中需要有"_Hair'字段的字体
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2024/4/20__18:50
# -------------------------------------------------------
import lib.maya.node.grop as group_common
import lib.common.loginfo as info
import lib.maya.node.nodes as node_common
import maya.cmds as cmds

ASSETTYPE = ['hair']
MODELNAMES = ['_Hair']



class Check(object):
    u"""
    检测文件中(组下)是否有未freeze物体
    """

    def __init__(self, TaskData):
        u"""
        """
        self._taskdata = TaskData
        self._assettype = self._taskdata.asset_type
        self._entity_name = self._taskdata.entity_name


        self._error = u"文件中缺少'_Hair'模型,请检查"
        self.end = u"已检测'Hair'模型"
        self._end = u"此项不用检测"

    def checkinfo(self):
        if self._assettype and self._assettype.lower() in ASSETTYPE:
            err_result = self.run()
            _infolist = []
            if err_result:
                _infolist.extend(err_result)
                return False, info.displayErrorInfo(objList=_infolist)
            else:
                return True, info.displayInfo(objList=[self.end])


        else:
            return True, info.displayInfo(objList=[self._end])

    def run(self):
        return self._get_hair_model()

    def _get_hair_model(self):
        error=[]
        hairs=[]

        grp='{}_HD'.format(self._entity_name)
        if not cmds.ls(grp):
            error.append(u'文件中缺少{}组,检查'.format(grp))
            return error
        meshs= cmds.listRelatives(grp, ad=1, type='mesh')
        if not meshs:
            error.append(u'{}组下没有mesh模型,检查'.format(grp))
            return error
        for mesh in meshs:
            tr = cmds.listRelatives(mesh, p=1)[0]
            if '_Hair' in tr:
                hairs.append(tr)
        if not hairs:
            error.append(u'{}组下没有_Hair模型,检查'.format(grp))


        return error


if __name__ == '__main__':
    # 测试代码
    import method.shotgun.get_task as get_task

    reload(get_task)
    _filename = cmds.file(q=1, exn=1)

    test_task_data = get_task.TaskInfo(_filename, 'X3', 'maya', 'publish')
    _handle = Check(test_task_data)
    print(_handle.run())
