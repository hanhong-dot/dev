# -*- coding: utf-8 -*-#
# Python       :
# -------------------------------------------------------------------------------
# NAME         : check_modelShape
# Describe     : 检查模型的Shape型节点（检测关联复制或重名；检测多个Shape节点；检测[*Shape]命名规则等）
# Version      : v0.01
# Author       : linhuan
# Email        :
# DateTime     : 2022/6/27__17:00
# -------------------------------------------------------------------------------
# -------------------------------------------------------------------------------
# example:
#
#
# -------------------------------------------------------------------------------

import maya.cmds as cmds

import lib.common.loginfo as info


class Check(object):
    """
    检查模型的Shape型节点
    """

    def __init__(self, TaskData,groups=None, check_type='allError'):
        """
        实例初始化
        :param groups: 组名(如果为None，则会检测文件中所有mesh模型物体)；
                       不为空时，可以list列表，例如['MODEL', 'RIG']代表检查多个组下物体
                       或直接'MODEL'组。
        :param check_type: 'allError'-检测Shape节点的所有异常相关内容；
                           'instanceError'-检测关联复制或重名的Shape节点；
                           'multipleShapeError'-检测多个的Shape节点；
                           'shapeNameError'-检测不符合[*Shape]命名规则；
                           也可以使用列表组合来检测其中几项内容，如['instanceError', 'shapeNameError']；
        """
        super(Check, self).__init__()
        self._groups = groups
        self._groups_list = self._get_groups()
        self._check_type = check_type

        self._all_error_str = 'allError'
        self._all_check_type_dict = {'instanceError': u'■关联复制或重名的Shape节点异常，请检查：',
                                     'multipleShapeError': u'■多个的Shape节点异常，请检查：',
                                     'shapeNameError': u'■不符合[*Shape]命名规则，请检查：',
                                     'unusedShapeError': u'■无用的Shape节点，请检查：'}

        self._check_type_list = self._get_check_type()  # 从输入的check_type的参数判断出要检查的内容

        self._asset_type = TaskData.asset_type

        self.name = u'检查模型的Shape形节点'
        self.tooltip = u'检查模型的Shape型节点(检测关联复制；检测多个Shape节点；检测[*Shape]命名规则)'
        self._checkinfo=u"已检测模型的Shape形节点"

        self._filterMultipleShapeAttr = ['eyeFFD']  # 排除有添加的自定义属性模型(如:眼睛使用晶格压缩的模型)
        # <editor-fold desc="===先罗列所有异常键值===">
        self._instanceError_key = self._all_check_type_dict['instanceError']
        self._multipleShapeError_key = self._all_check_type_dict['multipleShapeError']
        self._shapeNameError_key = self._all_check_type_dict['shapeNameError']
        self._unusedShapeError_key = self._all_check_type_dict['unusedShapeError']
        # </editor-fold>
        # self._allErrorDict = {self._instanceError_key: [], self._multipleShapeError_key: [],
        #                       self._shapeNameError_key: [], self._unusedShapeError_key: []}
        self._allErrorDict = { self._multipleShapeError_key: [],
                              self._shapeNameError_key: [], self._unusedShapeError_key: []}


    def checkinfo(self):
        """
        显示检查信息
        :return:
        """
        _errorInfoDict={}
        if self._asset_type.lower() not in ['fx','cartoon_fx']:
            _errorInfoDict = self.run()


        error_info = _errorInfoDict
        error_list = []
        if error_info:
            for k,v in error_info.items():
                error_list.append(k)
                if isinstance(v,list):
                    for i in v:
                        if isinstance(i,dict):
                            for key,value in i.items():
                                error_list.append(key)
                                error_list.append(value)
                        if isinstance(i,str) or isinstance(i,unicode):
                            error_list.append(i)
                        if isinstance(i,list):
                            error_list.extend(i)
                if isinstance(v,str) or isinstance(v,unicode):
                    error_list.append(v)
                if isinstance(v,dict):
                    for key, value in v.items():
                        error_list.append(key)
                        error_list.append(value)

        if error_list:
            return False, info.displayErrorInfo(title=self.tooltip,objList=error_list)
        else:
            return True, info.displayInfo(title=self._checkinfo)

    def run(self):
        """
        检查maya相关版本信息
        :return:
        """
        # <editor-fold desc="===0-变量预设内容===">
        info_dict = {}  # 异常信息总字典
        # </editor-fold>

        # <editor-fold desc="===1-放置要检查内容代码===">
        # 放置要检查内容代码
        shapeList = []  # 关联复制的Shape模型
        _all_meshs = self._get_meshs()

        for obj in _all_meshs:
            shapes = cmds.listRelatives(obj, pa=1, s=1, type='mesh', f=1)
            shortshape = ''
            if shapes:
                if '|' in shapes[0]:
                    shortshape = shapes[0].split('|')[-1]
                else:
                    shortshape = shapes[0]

                # 判断Shape节点是否有用
                for shape in shapes:
                    if self.check_unused_shape(shape) and shape not in self._allErrorDict[self._unusedShapeError_key]:
                        print('unuse')
                        self._allErrorDict[self._unusedShapeError_key].append(shape)

                # 只有一个Shape型节点时
                if len(shapes) == 1:
                    name = obj.split('|')[-1] + 'Shape'
                    # Shape型节点命名异常
                    if shortshape != name and obj not in self._allErrorDict[self._shapeNameError_key]:
                        self._allErrorDict[self._shapeNameError_key].append({obj: u'正确命名为：{}'.format(name)})

                    # 关联复制Shape型节点
                    if shortshape not in shapeList:
                        shapeList.append(shortshape)
                    #去掉重名检测 2022.06.27 linhuan
                    # elif shortshape in shapeList and obj not in self._allErrorDict[self._instanceError_key]:
                    #     self._allErrorDict[self._instanceError_key].append(obj)

                # 多个Shape型节点
                else:
                    # 如果有多个Shape型节点，再判断是否为要过滤属性物体
                    isFilterObj = self.check_object_filter_attr(obj, self._filterMultipleShapeAttr)
                    _judge_bs=self._judgue_bs(obj)
                    if obj not in self._allErrorDict[self._multipleShapeError_key] and not isFilterObj and _judge_bs!=True:
                        self._allErrorDict[self._multipleShapeError_key].append(obj)

        # </editor-fold>

        # <editor-fold desc="===2-对所有检查异常提示键总字典进行遍历，封装到异常信息总字典里===">
        for key in self._allErrorDict:
            if self._allErrorDict[key]:
                for var in self._check_type_list:
                    if self._all_check_type_dict[var] == key:  # 只有当是要检查的check_type内容时，才写入信息
                        info_dict[key] = self._allErrorDict[key]
        # </editor-fold>

        # <editor-fold desc="===3-异常信息总字典输出===">
        if info_dict:
            return info_dict
        else:
            return None
        # </editor-fold>

    def _judgue_bs(self,mesh):
        result=False
        if cmds.ls(type='blendShape'):
            bs = cmds.ls(type='blendShape')
            for b in bs:
                if cmds.listConnections(b) and mesh in cmds.listConnections(b):
                    result=True
                    break
        return result


    def fix(self):
        """
        修复相关内容
        :return:
        """
        self._errorInfoDict=self.run()
        if self._errorInfoDict:
            # 在各个异常提示键填写对应修复的代码
            if self._shapeNameError_key in self._errorInfoDict.keys():  # 不符合[*Shape]命名规则修复
                for obj_info in self._errorInfoDict[self._shapeNameError_key]:
                    objs = obj_info.keys()
                    for obj in objs:
                        if obj and cmds.ls(obj):
                            shape = cmds.listRelatives(obj, pa=1, ni=1, s=1, type='mesh', f=1)
                            if shape and len(shape) == 1:
                                shortshape = shape[0].split('|')[-1]
                                shortgrp = obj.split('|')[-1]
                                if shortshape != shortgrp + 'Shape':
                                    # cmds.rename(shape, shortgrp + 'Shape')
                                    try:
                                        cmds.rename(shape, shortgrp + 'Shape')
                                    except:
                                        pass
            if self._unusedShapeError_key in self._errorInfoDict.keys():  # 无用的Shape节点删除修复
                cmds.delete(self._errorInfoDict[self._unusedShapeError_key])

    def _get_groups(self):
        """
        获取要检测的组
        """
        group_list = []
        if isinstance(self._groups, str):
            group_list = [self._groups]
        if isinstance(self._groups, list):
            group_list = self._groups
        return group_list

    def _get_check_type(self):
        """
        获取要检查的类型
        """
        check_type_list = []
        if isinstance(self._check_type, str):  # 如果输入的check_type参数是字符串
            if self._check_type == self._all_error_str:  # 判断该字符串是否为"allError"，如果是则为检查所有
                check_type_list = self._all_check_type_dict.keys()
            if self._check_type in self._all_check_type_dict.keys():  # 判断该字符串是否只是其中一项，如果是则单独检查该项
                check_type_list = [self._check_type]

        elif isinstance(self._check_type, list):  # 如果输入的check_type参数是列表
            for i in self._check_type:
                if i == self._all_error_str:  # 如果该列表中包含有"allError"，如果是则为检查所有
                    check_type_list = self._all_check_type_dict.keys()
                    break
                if i in self._all_check_type_dict.keys():
                    check_type_list.append(i)

        return check_type_list

    def _get_meshs(self):
        """
        获取要检查的mesh模型
        """
        all_meshs = []
        if self._groups_list:
            for grp in self._groups_list:
                if cmds.objExists(grp):
                    # meshs_shepe = group_common.Group(grp).select_group_meshs()  # 取消使用group模块的common，因为关联复制的mesh没法获取
                    trans = cmds.listRelatives(grp, allDescendents=1, type='transform', f=1)
                    if trans:
                        for obj in trans:
                            shape = cmds.listRelatives(obj, s=1, type='mesh')
                            if shape and obj not in all_meshs:
                                all_meshs.append(obj)
        else:
            # all_meshs = cmds.ls(type="mesh")  # 取消使用该方式,因为关联复制的mesh没法获取到
            trans = cmds.ls(type="transform")
            all_meshs = [obj for obj in trans if cmds.listRelatives(obj, s=1, type='mesh')]
        return all_meshs

    def filter_attr_object(self, object_list, filter_attrs, result_type=0):
        u"""
        获取要过滤特定属性物体
        :param object_list: 物体列表
        :param filter_attrs: 过滤属性
        :param result_type: 0-返回没带有过滤属性物体列表；1-返回带有过滤属性物体列表；
        """
        attr_result = []
        no_attr_result = []
        if object_list:
            for obj in object_list:
                for attr in filter_attrs:
                    if cmds.objExists('%s.%s' % (obj, attr)) and cmds.getAttr('%s.%s' % (obj, attr)):
                        attr_result.append(obj)
                    else:
                        no_attr_result.append(obj)
        if result_type:
            return attr_result
        else:
            return no_attr_result

    def check_object_filter_attr(self, obj, filter_attrs):
        """
        检查物体是否有筛选属性
        :param obj: 物体
        return：如果是有筛选属性返回True；没有有筛选属性返回False；
        """
        result = False
        if filter_attrs:
            for attr in filter_attrs:
                if cmds.objExists('%s.%s' % (obj, attr)) and cmds.getAttr('%s.%s' % (obj, attr)):
                    result = True
                    break
        return result

    def check_unused_shape(self, shape):
        """
        检查该shape节点是否有用
        :param shape: shape节点
        """
        unused = False
        # .io(intermediate object中间物体)一般Orig或无用shape节点该属性都勾起
        io = cmds.getAttr(shape + '.intermediateObject')
        if io:
            out = cmds.listConnections("%s.worldMesh" % shape, d=1)
            input = cmds.listConnections("%s.inMesh" % shape, s=1, d=0)
            if not out:
                #  如果没有连接输出，大都没有用
                unused = True
            else:
                for ou in out:
                    if cmds.nodeType(ou) == 'mesh':
                        unused = True
        return unused


# if __name__ == "__main__":
#     # 测试代码
#     # 多种方式
#     import method.shotgun.get_task as get_task
#     file_=cmds.file(q=1,exn=1)
#     task_data=get_task.TaskInfo(file_, 'X3', 'maya', 'publish')
#     check_handle = Check(task_data)
#     # check_handle = Check(groups='MODEL')
#     # check_handle = Check(groups=['MODEL'])
#     # check_handle = Check(groups=['MODEL'], check_type='allError')
#     # check_handle = Check(groups=['MODEL'], check_type='instanceError')
#     # check_handle = Check(groups=['MODEL'], check_type=['allError'])
#     # check_handle = Check(groups=['MODEL'], check_type=['instanceError', 'multipleShapeError'])
#     # check_handle = Check(groups=['MODEL'], check_type=['instanceError', 'shapeNameError'])  # 绑定环节可以使用这个检测方式
#     # check_handle = Check(groups=['MODEL'], check_type=['instanceError', 'multipleShapeError', 'shapeNameError'])
#
#     print(check_handle.run())
