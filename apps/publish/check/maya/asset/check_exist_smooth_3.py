# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       : check_exist_smooth3
# Describe   : 检测文件中是否有按3smooth的物体
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2024/9/19__19:52
# -------------------------------------------------------
import lib.common.loginfo as info


class Check(object):

    def __init__(self):
        super(Check, self).__init__()

        self.tooltip = u'检查文件中是否存在按3smooth的模型'
        self._error_key = u'■文件中有以下模型按3smooth，请检查：'

    def checkinfo(self):
        """
        显示检查信息
        :return:
        """
        _error = self.run()
        _error_list = []
        if _error:
            _error_list.append(self._error_key )
            _error_list.extend(_error)
            return False, info.displayErrorInfo(title=self.tooltip, objList=_error_list)
        else:
            return True, info.displayInfo(title=self.tooltip)

    def run(self):
        """
        检查maya相关版本信息
        :return:
        """
        import maya.cmds as cmds
        _smooth_3 = cmds.ls(type="mesh", l=1)
        _error = []
        for _node in _smooth_3:
            _smooth = cmds.getAttr("{}.displaySmoothMesh".format(_node))
            if _smooth  and _smooth !=0:
                tr=cmds.listRelatives(_node, p=1, f=1,type='transform')
                if tr and tr not in _error:
                    _error.append(tr[0])
        return _error




    def fix(self):
        import maya.cmds as cmds
        """
        修复相关内容
        :return:
        """
        _error = self.run()
        if _error:
            for _node in _error:
                cmds.setAttr("{}.displaySmoothMesh".format(_node), 0)
            return True, info.displayInfo(title=self.tooltip)


#
# if __name__ == "__main__":
#     # 测试代码
#     print(Check().checkinfo())
