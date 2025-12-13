# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       : nodes
# Describe   : 说明描述
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2022/6/27__14:43
# -------------------------------------------------------
import maya.cmds as cmds

import pymel.core as pm


class BaseNodeProcess(object):
    u"""
    关于node节点处理的基本函数(删除,解锁,创建，复制)
    """

    def __init__(self):
        # 文件中存在的节点类型
        self.nodetyps = cmds.ls(nt=1)

    def judge_node_exists(self, node):
        u"""
        判断节点或节点+属性是否存在
        :param node: 节点名 或节点+属性名（例如:'MSH_Hi_C_Lowergum_bumpValue_file')
        或'MSH_Hi_C_Lowergum_bumpValue_file.fileTextureName'）
        :return: 返回为Ture时，存在，返回为False时，不存在
        """
        if node and cmds.ls(node):
            return True
        else:
            return False

    def judge_node_attribute(self, node, attribute):
        u"""
        判断节点属性是否存在
        :param node: 节点名
        :param attribute: 属性名
        :return: 为True时，代表存在该节点属性
        """
        node_attr = self.select_node_attribute_nodeattr(node, attribute)
        if node_attr and self.judge_node_exists(node_attr) == True:
            return True
        else:
            return False

    def get_all_nodes_exrdefault(self):
        u"""
        文件中所有节点(长名),排除defaultNodes
        :return:nodelist 节点列表
        """
        return list(set(self.get_all_nodes()) - set(self.nodetyps))

    def get_all_nodes(self, islong=False):
        u"""
        文件中所有节点
        :param islong: 为True时，为长名
        :return: nodelist
        """
        if islong == True:
            return cmds.ls(l=1)
        else:
            return cmds.ls()

    def get_node_type(self, node):
        u"""
        获得节点类型
        :param node: 节点名(例如:'MSH_Hi_C_Lowergum_bumpValue_file')
        :return: 节点类型（例如:'file')
        """
        if node and self.judge_node_exists(node) == True:
            return cmds.nodeType(node)

    def get_node_UUID(self, node):
        u"""
        获得节点UUID码
        :param node: 节点名
        :return: UUID
        """
        if node and self.judge_node_exists(node) == True and cmds.ls(node, uuid=True):
            return cmds.ls(node, uuid=True)[0]

    def get_node_uniqueid(self, node, prefixid):
        u"""
        获得uniqueid(prefixid__uuid)
        :param node: 节点名
        :param prefixid: 前缀id
        :return:
        """
        uuid = self.get_node_UUID(node)
        if uuid:
            if prefixid:
                return u'{}__{}'.format(prefixid, uuid)
            else:
                return uuid

    def select_uuid_node(self, uuid):
        u"""
        根据uuid值获得节点名
        :param uuid: uuid,例如:u'97252577-4FDA-25EA-BBAF-D491AF0AFCB4'
        :return:节点名,例如:biaopan01
        """
        if uuid and cmds.ls(uuid):
            return cmds.ls(uuid)[0]

    def get_node_uuid5(self, node):
        u"""
        创建节点id(使用uuid5的方式)
        :param node:节点名
        :return:id(str)
        """
        import uuid
        if node and self.judge_node_exists(node) == True:
            return str(uuid.uuid5(uuid.NAMESPACE_DNS, str(node)))

    def select_nodetype_nodes(self, nodetype):
        u"""
        根据节点类型获取文件中所有该类型的节点(例如,file)
        :param nodetype:
        :return:
        """
        if nodetype and nodetype in self.nodetyps:
            return cmds.ls(type=nodetype, l=1)

    def rename_node_nodenew(self, node, nodenew):
        u"""
        重命名节点名
        :param node: 节点名
        :param nodenew: 重命名后的节点名
        :return: 重命名后的节点名
        """
        if self.judge_node_exists(node) == True:
            # 解锁节点
            self.unlock_node(node)
            # 重命名
            try:
                return cmds.rename(node, nodenew)
            except:
                return False
        return False

    def get_nodeattr_key(self, node, attribute):
        u"""
        获得节点相对应属性的值或节点文件
        :param node: 文件名 (例如:"FA000014shc_MSHHi_shugan_input_file")
        :param attribute: 属性名(例如:".uvTilingMode"
        :return:count(例如:1），注意类型不一定，有可能为str,也有可能为float,或bool，或int
        """
        _nodeattribute = self.select_node_attribute_nodeattr(node, attribute)
        if node and attribute and cmds.ls(_nodeattribute):

            _path=cmds.getAttr(_nodeattribute)
            try:
                _path=cmds.getAttr(_nodeattribute)
                if _path:
                    return u'{}'.format(_path)
            except:
                return

    def set_nodeattr_key(self, node, attribute, key):
        u"""
        设置节点
        :param node: 节点名(例如:'MSH_Hi_C_Lowergum_bumpValue_file’）
        :param attribute: 属性名（例如".fileTextureName")
        :param key:需要设置的值，或文件（类型不一定，有可能为str,也有可能为float,或bool，或int）
        :return:为True时，成功设置，为Flase时，未成功设置
        """
        _nodeattribute = self.select_node_attribute_nodeattr(node, attribute)
        # 先解锁
        self.unlock_node_attr(node, attribute)
        # 如果key是字符串类型
        if (isinstance(key, str) or isinstance(key, unicode)) and cmds.ls(_nodeattribute):
            try:
                attributen = pm.Attribute(_nodeattribute)
                attributen.unlock()
                attributen.__apimplug__().setString(key)
                return True
            except:
                return False
            # try:
            #     cmds.setAttr(_nodeattribute, key,type='string')
            # except:
            #     pass
        # 如果key是数字类型(int,bool,float)
        if isinstance(key, int) or isinstance(key, float):
            try:
                cmds.setAttr(_nodeattribute, key)
                return True
            except:
                return False
        # 如果key是列表(例如[0.1,0.2, 0.1])
        if isinstance(key, list) and len(list) == 3:
            try:
                cmds.setAttr(_nodeattribute, key[0], key[1], key[2], type='double3')
                return True
            except:
                return False
        return False

    def set_nodeattrdict_key(self, nodeattrdict):
        u"""
        根据字典设置节点
        :param nodeattrdict: {（节点+属性）:key(需要设置的值或str)} 例如{'MSH_Hi_C_Lowergum_bumpValue_file.fileTextureName':"D:/tree.png"}
        :return: {True:{(节点+属性):key},False:{(节点+属性):key} True 成功设置的，False 为未成功设置的
        """
        # 总字典
        _dict = {}
        # 成功设置的字典
        _set_dict = {}
        # 未成功设置的字典
        _no_set_dict = {}

        if nodeattrdict:
            for k, v in nodeattrdict.items():
                result = self.set_nodeattr_key(self.select_nodeattr_node(k), self.select_nodeattr_attr(k), v)
                if result == True:
                    _set_dict[k] = v
                if result == False:
                    _no_set_dict[k] = v
        if _set_dict:
            _dict[True] = _set_dict
        if _no_set_dict:
            _dict[False] = _no_set_dict
        return _dict

    def select_node_attribute_nodeattr(self, node, attribute):
        u"""
        获得节点+节点属性名
        :param node: 节点名(例如:"FA000014shc_MSHHi_shugan_dependNode_file")
        :param attribute: 节点属性名(例如:".fileTextureName")
        :return:节点+属性名(例如:"FA000014shc_MSHHi_shugan_dependNode_file.fileTextureName")
        """
        if '.' in attribute:
            return u"{}{}".format(node, attribute)
        else:
            return u"{}.{}".format(node, attribute)

    def select_nodeattr_node(self, nodeattr):
        u"""
        根据节点+属性 名获得节点名
        :param nodeattr: 节点+属性(例如:'MSH_Hi_C_Lowergum_bumpValue_file.fileTextureName')
        :return:节点名（例如'MSH_Hi_C_Lowergum_bumpValue_file')
        """
        return nodeattr.split('.')[0]

    def select_nodeattr_attr(self, nodeattr):
        u"""
        根据节点+属性 名获得属性
        :param nodeattr: 节点+属性(例如:'MSH_Hi_C_Lowergum_bumpValue_file.fileTextureName')
        :return:属性（例如'.fileTextureName')
        """
        return nodeattr.split('.')[-1]

    def delete_node_attribute(self, node, attribute):
        u"""
        删除节点属性
        :param node: 节点名
        :param attribute: 属性名
        :return: True，代表删除成功,False，代表删除失败
        """
        # 解锁属性
        self.unlock_node_attr(node, attribute)
        # 删除属性
        if node and attribute and self.judge_node_attribute(node, attribute):
            try:
                cmds.deleteAttr(self.select_node_attribute_nodeattr(node, attribute))
                return True
            except:
                return False

    def delete_nodes(self, nodelist):
        u"""
        删除物体(节点)
        :param nodelist: 需要删除的物体列表
        :return: 删除成功的物体(删除不成功的物体)字典，例如{True:[obj01,obj02],False:[obj03,obj04]}
        """
        _delete_objlist = []
        _no_delete_objlist = []
        try:
            cmds.delete(nodelist)
            _delete_objlist = nodelist
        except:
            for obj in nodelist:
                try:
                    cmds.lockNode(obj, l=0)
                    cmds.delete(obj)
                    _delete_objlist.append(obj)
                except:
                    _no_delete_objlist.append(obj)
        return {True: _delete_objlist, False: _no_delete_objlist}

    def unlock_node_attr(self, node, attribute):
        u"""
        解锁节点属性
        :param node: 节点名(例如:'AN_seq019_sc011_StereoCam')
        :param attribute: 属性(例如:'translateX',translateY')
        :return:解锁成功True, 解锁失败False
        """

        # 解锁节点
        self.unlock_node(node)
        # 解锁节点属性
        _node_attr = self.select_node_attribute_nodeattr(node, attribute)
        try:
            cmds.setAttr(_node_attr, l=0)
            return True
        except:
            return False

    def lock_node_attr(self, node, attribute):
        u"""
        锁定节点属性
        :param node: 节点名(例如:'AN_seq019_sc011_StereoCam')
        :param attribute: 属性(例如:'translateX',translateY')
        :return:锁定成功True, 锁定失败False
        """

        # 解锁节点
        self.unlock_node(node)
        # 锁定节点属性
        _node_attr = self.select_node_attribute_nodeattr(node, attribute)
        try:
            cmds.setAttr(_node_attr, l=1)
            return True
        except:
            return False

    def unlock_node(self, node):
        u"""
        解锁节点
        :param node: 节点名(例如：'AN_seq019_sc011_StereoCam')
        :return: True(False)
        """
        try:
            cmds.lockNode(node, l=0)
            return True
        except:
            return False

    def lock_node(self, node):
        u"""
        锁定节点
        :param node: 节点名(例如：'AN_seq019_sc011_StereoCam')
        :return: True(False)
        """
        try:
            cmds.lockNode(node, l=1)
            return True
        except:
            return False

    def get_node_allattrs(self, node):
        u"""
        获得节点所有属性
        :param node:节点名
        :return:
        """
        return cmds.listAttr(node)

    def lock_nodelist(self, nodelist, nodelock=False):
        u"""
        锁定nodelist及其属性
        :param nodelist:节点列表
        :param nodelock:nodelock 为False时，不锁定节点，为True时，锁定节点
        :return:
        """
        if nodelist:
            for node in nodelist:
                attrs = self.get_node_allattrs(node)
                if attrs:
                    for attribut in attrs:
                        self.lock_node_attr(node, attribut)
                if nodelock == True:
                    self.lock_node(node)
        return True

    def unlock_nodelist(self, nodelist):
        u"""
        解锁nodelist及锁定的属性
        :return: 为True时，成功执行，为False时，执行失败
        """
        if nodelist:
            for node in nodelist:
                lock_attributes = BaseNodeAttribute(node).get_node_lockattrs()
                if lock_attributes:
                    for attribute in lock_attributes:
                        self.unlock_node_attr(node, attribute)
                else:
                    self.unlock_node(node)
        return True

    def duplicate_node_general(self, node_source, node_targe):
        u"""
        常规复制(复制到node_source 同一组下，无连接)
        :param node_source:原始节点名(例如：'AN_seq019_sc011_StereoCam'）
        :param node_targe: 复制后节点名(例如：'AN_seq019_sc011_StereoCam_bake'）
        :return: [复制后节点名] (例如：['AN_seq019_sc011_StereoCam_bake'])
        """
        return cmds.duplicate(node_source, n=node_targe, rr=1)

    def duplicate_node_inputConnections(self, node_source, node_targe):
        u"""
        带连接复制（带原节点动画曲线等连接信息的复制)，复制到node_source 同一组下
        :param node_source:原始节点名(例如：'AN_seq019_sc011_StereoCam'）
        :param node_targe: 复制后节点名(例如：'AN_seq019_sc011_StereoCam_bake'）
        :return: [复制后节点名] (例如：['AN_seq019_sc011_StereoCam_bake'])
        """
        return cmds.duplicate(node_source, n=node_targe, rr=1, ic=1)

    def duplicate_node_inputConnections_world(self, node_source, node_targe):
        u"""
        带连接复制（带原节点动画曲线等连接信息的复制)，复制到root
        :param node_source:原始节点名(例如：'AN_seq019_sc011_StereoCam'）
        :param node_targe: 复制后节点名(例如：'AN_seq019_sc011_StereoCam_bake'）
        :return: [复制后节点名] (例如：['AN_seq019_sc011_StereoCam_bake'])
        """
        node_duplicate = cmds.duplicate(node_source, n=node_targe, rr=1, ic=1)
        if node_duplicate:
            try:
                return cmds.parent(node_duplicate, w=1)
            except:
                return node_duplicate


class BaseNodeAttribute(object):
    u"""
    获得节点属性列表
    """

    def __init__(self, nodename):
        u"""
        获得节点属性列表
        :param nodename: 节点名
        """
        self.nodename = nodename

    def get_node_lockattrs(self):
        u"""
        获得节点被lock的属性列表
        :return:属性列表
        """
        return cmds.listAttr(self.nodename, l=1)


class Addattribute(BaseNodeProcess):
    u"""
    节点(列表)添加属性
    """

    def __init__(self):
        BaseNodeProcess.__init__(self)

    def add_uniqueid_nodes(self, nodelist, prefixid, attribute='uniqueid', attributetype='string'):
        u"""
        节点添加
        :param nodelist: 需要添加属性的节点列表
        :param prefixid: id前缀名
        :param attribute: 属性名
        :param attributetype:属性类型,例如 "string"
        :return:
        """
        if nodelist:
            for node in nodelist:
                # 获得节点uniqueid
                uniqueid = self.get_node_uniqueid(node, prefixid)
                # 添加属性
                self.add_node_attribute(node, attribute, attributetype)
                # 设置uniqueid值
                self.set_nodeattr_key(node, attribute, uniqueid)
                # 锁定uniqueid属性
                self.lock_node_attr(node, attribute)
        return nodelist

    def add_uuid5_nodes(self, nodelist, attribute='uuid5', attributetype='string'):
        u"""
        节点添加uuid5属性
        :param nodelist: 节点列表
        :return:
        """
        if nodelist:
            for node in nodelist:
                # 获得节点uuid5值
                uuid5 = self.get_node_uuid5(node)
                # 添加属性
                self.add_node_attribute(node, attribute, attributetype)
                # 设置uuid5属性值
                self.set_nodeattr_key(node, attribute, uuid5)
                # 锁定uuid5属性
                self.lock_node_attr(node, attribute)
        return nodelist

    def add_node_attribute(self, node, attribute, attributetype, parent=None, defaultvalue=1):
        u"""
        节点添加属性(基本)
        :param node: 节点名，例如:"MSH_Hi_C_yifu"
        :param attribute: 属性名,例如 "uuid5"
        :param attributeType:属性类型,例如 "string" ,'float3','float' 等等
        :param parent 继承属性下(如果为None，则创建的属性不会在其他属性下)
        :return: 为True时，属性添加成功，为False时，属性没有添加成功
        """
        # 先解锁节点
        self.unlock_node(node)
        try:
            if attributetype in ['double', 'bool']:
                if not parent:
                    cmds.addAttr(node, ln=attribute, attributeType=attributetype, k=1, dv=defaultvalue)
                else:
                    cmds.addAttr(node, ln=attribute, attributeType=attributetype, k=1, dv=defaultvalue,
                                 parent=parent)
            else:
                if not parent:
                    cmds.addAttr(node, ln=attribute, dt=attributetype)
                else:
                    cmds.addAttr(node, ln=attribute, dt=attributetype, parent=parent)
            return True
        except:
            return False

    def add_node_attribute_double3(self, node, attribute, subattributs=['X', 'Y', 'Z'], defaultvalues=[1, 1, 1]):
        U"""
        double3 类型属性添加
        :param node: 节点名
        :param attribute: 属性名
        :param defaultvalue: 默认值
        :param subattributs: 子属性
        :return:为True时，属性添加成功，为False时，属性没有添加成功
        """
        # 先解锁节点
        self.unlock_node(node)
        try:
            # 先添加属性
            self.add_node_attribute(node, attribute, 'double3')
            # 再添加子属性
            if subattributs:
                for i in range(len(subattributs)):
                    subattribut = u'{}{}'.format(attribute, subattributs[i])
                    self.add_node_attribute(node, subattribut, attributetype='double', parent=attribute,
                                            defaultvalue=defaultvalues[i])
            return True

        except:
            return False

    def break_node_connection(self, node, attributelist):
        """
        断开指定节点的关联
        :param node: 节点名称
        :param attributelist: 属性列表，如['KsColor','color','emission','emissionColor'，'inMesh']
        :return:
        """
        attributes = []
        if isinstance(attributelist, str):
            attributes = [attributelist]
        if isinstance(attributelist, list):
            attributes = attributelist

        for att in attributes:
            try:
                attName = node + '.' + att
                allAttribs = cmds.listAttr(attName)  # 对于一些double型的属性，会再有[*X, *Y, *Z]
                # print('allAttribs==>', allAttribs)
                for at in allAttribs:
                    atName = node + '.' + at
                    allConnections = cmds.listConnections(atName, d=False, s=True, connections=True, plugs=True)
                    # print('allConnections==>', allConnections)
                    if allConnections:
                        i = 0
                        while i < len(allConnections):
                            cmds.disconnectAttr(allConnections[i + 1], allConnections[i])
                            i += 2
                if cmds.getAttr(attName, type=True) == 'float':
                    cmds.setAttr(attName, 0)
                if cmds.getAttr(attName, type=True) == 'float3':
                    cmds.setAttr(attName, 0, 0, 0, type='double3')
                return True
            except:
                return False