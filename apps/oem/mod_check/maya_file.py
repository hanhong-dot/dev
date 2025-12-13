# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       : file
# Describe   : 说明描述
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2022/6/11__3:19
# -------------------------------------------------------
import os

import maya.cmds as cmds


class BaseFile(object):
    # maya文件基本处理
    def __init__(self):
        pass

    def current_file(self):
        u"""
        当前文件名(文件路径+文件名)
        :return:
        """
        return cmds.file(q=1, exn=1)

    def new_file(self):
        u"""
        生成一个空的maya文件
        :return:
        """
        try:
            cmds.file(force=True, new=True)
        except:
            raise Exception(u'无法创建新文件'.encode('gbk'))

    def new_file_filename(self, filename):
        u"""
        创建一个新文件，并保存为filename文件
        :param filename: 文件夹+文件名
        :return:
        """
        # 创建新文件
        self.new_file()
        # 保存
        self.save_file(filename)

        return filename

    def get_format(self, _file):
        u"""
        获取文件格式
        """
        _sub = os.path.splitext(_file)[-1]
        _format = ''
        if _sub == '.mb':
            _format = 'mayaBinary'
        else:
            _format = 'mayaAscii'
        return _format

    def open_file(self, openfile):
        u"""
        打开文件
        :param openfile:  需要打开的文件(文件路径+文件名)
        :return:
        """
        _format = self.get_format(openfile)
        cmds.file(openfile, options='v=0', type=_format, f=1, o=1, ignoreVersion=1, pmt=0, rer=0)
        # try:
        #     cmds.file(openfile, options='v=0', type=_format, f=1, o=1, ignoreVersion=1, pmt=0, rer=0)
        # except:
        #     raise Exception(u'无法打开文件'.encode('gbk'))

    def save_current_file(self):
        u"""
        保存至当前文件
        :return:
        """
        _filename = self.current_file()
        if _filename:
            self.save_file(_filename)
            return

    def open_current_file(self):
        u"""
        重新打开当前文件
        :return:
        """
        _filename = self.current_file()
        if _filename:
            self.open_file(_filename)
            return

    def save_file(self, filename):
        u"""
        保存文件
        :param filename: 文件夹+文件名
        :return: 保存成功,返回filename;保存失败,返回False
        """
        _format = self.get_format(filename)

        if _format and _format != False:
            try:
                _path = os.path.dirname(filename)
                if not os.path.exists(_path):
                    os.makedirs(_path)
                cmds.file(rename=filename)
                cmds.file(save=True, type=_format, f=True)
            except:
                raise Exception(u'文件未保存成功'.encode('gbk'))

    def export_file(self, objlist, filename, format="mayaAscii"):
        u"""
        导出文件(选择objlist，并导出)
        :param objlist: 需要导出的物体节点
        :param filename: 导出的文件(文件路径+文件名)
        :return:
        """
        _format = self.get_format(filename)
        if objlist and filename:
            try:
                cmds.select(objlist)
                cmds.file(filename, options='v=0', f=1, type=format, preserveReferences=1, es=1)
            except:
                raise Exception(u'文件未导出成功'.encode('gbk'))

    def get_suffix(self, filename):
        u"""
        根据文件名，获得文件后缀
        :param filename: 文件名
        :return: 文件后缀
        """
        return os.path.splitext(filename)[-1]

    def _select_file_namespace(self, filename):
        u"""
        从参考的文件获取namespace
        :param filename: 文件
        :return:
        """
        return os.path.basename(filename)[0].split('_')[0]

    def reference_info_dict(self, load=True):
        u"""
        文件参考信息
        :param load: 为True时，只读取load的参考，为False时，读取所有参考(没有load的参考也读取)
        :return:
        """
        refs = cmds.file(q=1, r=1)
        result = {}
        if not refs:
            pass

        for ref in refs:
            refRN = cmds.referenceQuery(ref, referenceNode=1)
            _isload = cmds.referenceQuery(refRN, isLoaded=1)
            if (_isload and load == 1) or load == 0:
                refPath = ref
                ns = cmds.file(refPath, namespace=1, q=1)
                if '{' in refPath:
                    refPath = refPath.split('{')[0]
                if os.path.exists(refPath):
                    result[ns] = [refRN, refPath]
        return result

    def reference_file(self, filename, namespace=':', load='all'):
        u"""
        参考文件
        :param filename: 需要参考的文件
        :param namespace: namespace
        :param load: 为'all'时，参考时加载，为'none'时，参考时不加载
        :return:参考成功，返回True;参考不成功，返回False
        """
        try:
            cmds.file(filename, r=1, namespace=namespace, ignoreVersion=1, loadReferenceDepth=load, pmt=0)
            return True
        except:
            raise Exception(u'文件未参考成功,请检查'.encode('gbk'))

    def splitpath(self, filename):
        '''
        文件分离
        根据文件名，获取路径，分割符，文件名
        :param filename:文件名(文件夹+文件名)
        :return:路径,分割符,文件名
        '''
        dirname, basename = os.path.split(filename)
        separator = filename.replace(dirname, "")
        separator = separator.replace(basename, "")
        return dirname, separator, basename

    def import_file(self, import_file, namespace=":"):
        u"""
        导入文件
        :param import_file: 导入的文件
        :param namespace: namespace
        :return:
        """
        try:
            return cmds.file(import_file, i=1, type=self.get_format(import_file), ignoreVersion=1, namespace=namespace,
                             pr=1, pmt=0)
        except:
            return False

    def import_filetype_file(self, import_file, filetype="Alembic", namespace=":"):
        u"""
        导入特定格式的文件
        :param import_file: 导入的文件
        :param filetype: 文件类型
        :param namespce: 导入的nameapce
        :return:
        """

        try:
            return cmds.file(import_file, i=1, type=filetype, ignoreVersion=1, namespace=namespace,
                             pr=1, importTimeRange="combine")
        except:
            return False

    def clear_unload_reference(self):
        u"""
        清理未加载的参考
        :return:
        """
        _refinofo = self.reference_info_dict()
        if _refinofo:
            for k, v in _refinofo.items():
                if k and v:
                    load = cmds.referenceQuery(v[0], isLoaded=1)
                    if load == False:
                        cmds.file(rfn=v[0], removeReference=1)
                        return True

        return False


class Process_File(BaseFile):
    u"""
    文件处理
    """

    def __init__(self):
        BaseFile.__init__(self)

    def judge_reference_namespace(self, namespace, split='_'):
        u"""
        判断参考的namepace
        :param namespace: namespace名
        :param split: namespace分离符号
        :return: 如果参考中没有该namespace,则返回namespace,如果文件中重复的namespace名，则返回namespace_01 这样的namespace
        """
        namespacelist = self.reference_info_dict().keys()
        if namespace not in namespacelist:
            return namespace
        if namespace in namespacelist:
            while namespace in namespacelist:
                if split not in namespace:
                    namespace = u"{}{}01".format(namespace, split)
                else:
                    namespace = u"{}{}0{}".format(namespace.split(split)[0], split, int(namespace.split(split)[-1]) + 1)
                if namespace not in namespacelist:
                    return namespace

    def reference_file_namespace(self, reference_file, namespace):
        u"""
        项目内参考文件
        :param reference_file:参考文件
        :param namespace: namespace名称
        :return:
        """
        if reference_file and namespace and os.path.exists(reference_file):
            return self.reference_file(reference_file, self.judge_reference_namespace(namespace))

    def import_file_namespace(self, import_file, namespace=":"):
        u"""
        导入文件
        :param import_file: 导入的文件
        :param namespace: namespace
        :return:
        """
        if import_file and namespace and os.path.exists(import_file):
            return self.reference_file(import_file, self.judge_reference_namespace(namespace))

    def select_process_objs(self, objspre, objsend):
        u"""
        获得处理后的物体
        :param objspre: 处理前物体列表
        :param objsend: 处理后物体列表
        :return:
        """
        return list(set(objsend) - set(objspre))
