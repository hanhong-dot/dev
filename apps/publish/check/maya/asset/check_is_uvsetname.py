# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       : check_is_uvsetname
# Describe   : 检测uvset命名
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2022/6/29__17:28
# -------------------------------------------------------
import lib.common.loginfo as info
import maya.cmds as cmds


class Check(object):
    """
    检查项目当前使用maya软件的相关信息
    """

    def __init__(self, TaskData,group_list=None):
        """
        实例初始化
        """
        # 即使直接派生自object，最好也调用一下super().__init__，
        # 不然可能造成多重继承时派生层次中某些类的__init__被跳过。
        super(Check, self).__init__()
        self.group_list = group_list
        self._asset_type=TaskData.asset_type

        self.tooltip = u'已检测UVSET 命名'

    def checkinfo(self):
        """
        显示检查信息
        :return:
        """
        _error = self.run()
        _error_list = []
        if _error:
            _error_list.append(u"以下物体UVSet 命名不正确,请检查")
            for k,v in _error.items():
                _error_list.append(k)

                _error_list.extend(v)
                if self._asset_type.lower() in ['item']:
                    _error_list.append(u"正确命名是{数字}u,例如1u,2u,3u,请检查")
                else:
                    _error_list.append(u"正确命名是map{数字},例如map1,map2,map3,请检查")
            return False, info.displayErrorInfo(title=self.tooltip, objList=_error_list)
        else:
            return True, info.displayInfo(title=self.tooltip)

    def run(self):

        """
        检查uvset命名是否符合map* 例如map1
        :return:
        """
        import maya.api.OpenMaya as om2
        import lib.maya.node.mesh as meshcommon
        errdict = {}
        meshs = self._mesh_list()
        if meshs:
            for _mesh in meshs:
                #
                try:
                    _mesh_class = meshcommon.Mesh(_mesh)
                    uvsets = om2.MFnMesh(_mesh_class.mesh).getUVSetNames()
                    if uvsets:
                        _error = []
                        for set in uvsets:
                            if self._asset_type.lower() not in ['item']:
                                if set not in ["map%i" % i for i in range(10)]:
                                    _error.append(set)
                            else:
                                if set not in ["%iu" % i for i in range(10)]:
                                    _error.append(set)

                        if _error:
                            errdict[_mesh] = _error
                except:
                    pass

        return errdict

    # </editor-fold>

    def fix(self):
        """
        修复相关内容
        :return:
        """
        error= self.run()
        if self._asset_type.lower() in ['item']:
            if error:
                for k,v in error.items():
                    self.fix_item_uvset(k,v)
        else:
            if error:
                for k,v in error.items():
                    self.fix_map_uvset(k,v)




    def fix_map_uvset(self, mesh, uvsets):
        """
        修复map uvset
        :param mesh:
        :param uvsets:
        :return:
        """
        import maya.api.OpenMaya as om2
        import lib.maya.node.mesh as meshcommon
        _mesh_class = meshcommon.Mesh(mesh)
        if uvsets and mesh:

            for i in range(len(uvsets)):
                uvsets = om2.MFnMesh(_mesh_class.mesh).getUVSetNames()
                uv_name="map%i" % (i+1)
                while uv_name in uvsets:
                    i+=1
                    uv_name="map%i" % i
                om2.MFnMesh(_mesh_class.mesh).renameUVSet(uvsets[i], uv_name)

    def fix_item_uvset(self, mesh, uvsets):
        """
        修复item uvset
        :param mesh:
        :param uvsets:
        :return:
        """
        import maya.api.OpenMaya as om2
        import lib.maya.node.mesh as meshcommon
        _mesh_class = meshcommon.Mesh(mesh)
        if uvsets and mesh:

            for i in range(len(uvsets)):
                uvsets = om2.MFnMesh(_mesh_class.mesh).getUVSetNames()
                uv_name="%iu" % (i+1)
                while uv_name in uvsets:
                    i+=1
                    uv_name="%iu" % i
                om2.MFnMesh(_mesh_class.mesh).renameUVSet(uvsets[i], uv_name)




    def _mesh_list(self):
        u"""
        需要检测的模型
        """
        import lib.maya.node.grop as groupcommon
        if not self.group_list:
            return cmds.ls(type='mesh', l=1)
        else:
            _meshs = []
            for _grop in self.group_list:
                _mesh = groupcommon.Group(_grop).select_group_meshs()
                if _mesh:
                    _meshs.extend(_mesh)
            return _meshs


# if __name__ == "__main__":
#     # 测试代码
#     print(Check().checkinfo())
