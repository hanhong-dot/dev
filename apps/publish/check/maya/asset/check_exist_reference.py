# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       : check_exist_reference
# Describe   : 检测文件中是否有reference
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2022/6/24__18:31
# -------------------------------------------------------
import lib.common.loginfo as info


class Check(object):
    """
    检查项目当前使用maya软件的相关信息
    """

    def __init__(self):
        """
        实例初始化
        """
        # 即使直接派生自object，最好也调用一下super().__init__，
        # 不然可能造成多重继承时派生层次中某些类的__init__被跳过。
        super(Check, self).__init__()

        self.tooltip = u'检查文件中是否存在reference'
        # <editor-fold desc="===先罗列所有异常键值===">
        self._maya_version_error_key = u'■文件中有以下reference节点，请检查：'

    def checkinfo(self):
        """
        显示检查信息
        :return:
        """
        _error = self.run()
        _error_list = []
        if _error:
            _error_list.append(self._maya_version_error_key)
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
        _reflist = cmds.ls(type="reference")
        return _reflist


    def fix(self):
        import maya.cmds as cmds
        """
        修复相关内容
        :return:
        """
        _error = self.run()
        if _error:
            import method.maya.common.reference as refcommon
            reload(refcommon)
            refcommon.remove_reference()
        _error_n= self.run()
        if _error_n:
            for _err_node in _error_n:
                cmds.lockNode(_err_node, lock=False)
                cmds.delete(_err_node)


if __name__ == "__main__":
    # 测试代码
    print(Check().checkinfo())
