# -*- coding: utf-8 -*-#
# Python       : python 2.7.18
# -------------------------------------------------------------------------------
# NAME         : collect_nodefile
# Describe     : 收集节点文件
# Version      : v0.01
# Author       : hanhong.2022
# Email        : hanhong.2022@bytedance.com
# DateTime     : 2022/2/24__16:34
# -------------------------------------------------------------------------------
# -------------------------------------------------------------------------------
# example:
# 
# -------------------------------------------------------------------------------
import lib.maya.analysis.analyze_data as analyze_data

import lib.maya.node.nodes as node

import lib.maya.node.nodefile as nodefile

import lib.common.any_sequence as sequence

reload(sequence)

import os

import lib.common.md5 as _md5

import method.common.dir as dir

COVERFORM = ['.tga']


class CollectNodeFile(object):
    def __init__(self, targepath='', nodetypelist=None, addsuffix=['.tx']):
        u"""
        收集节点文件
        """
        # 节点类型列表
        self._nodetypelist = nodetypelist
        # 收集到的目标路径
        self._targepath = targepath
        # 节点信息
        self._nodefile_data = analyze_data.AnalyData().get_data_info()["FILE_ATTR"]
        # 需要一起复制的带后缀的文件
        self.addsuffix = addsuffix

        # 本机路径
        self.local_dir = dir.set_localtemppath('temp_info/imgcover')
        # 如果 nodetypelist 为None 则读取所有的节点类型
        if not self._nodetypelist:
            self._nodetypelist = self._nodefile_data.keys()

    def collect_nodefiles(self, ex=False, _cover=None, _set=True,_copy=True):
        u"""
        收集节点文件
        :param ex: ex:为True时,节点文件存在时设置，为False时,节点文件无论是否存在都会设置
        :param _cover: 转换格式,为None时，则不转换贴图格式
        :return:
        """

        # 获得相应的node节点字典
        _dict = self._get_nodedict()
        #
        _node_dict = self._get_nodefiles(_dict)
        # 序列帧初始化设置
        self.set_sequence(_node_dict)
        # 获得相应节点文件
        _node_file_dict = self._get_nodefiles(_node_dict)
        # 转换贴图格式
        if _cover != None and _cover.lower() in COVERFORM:
            _node_file_dict = self.cover_nodefile_dict(_node_file_dict, _cover=_cover)
        #获取需要要复制(上传)的文件
        _node_file_dict_copy=self._get_node_file_dict(_node_file_dict)
        # 将文件复制到对应目标路径
        _copy_dict,_source_targe_dict = self.copy_nodefile_dict(_node_file_dict_copy, self._targepath,_copy)
        # 将设置到对应目标路径
        if _set == True:
            _list = self.set_targe_nodefiles(_node_file_dict, self._targepath, ex)

        return _source_targe_dict

    def _get_node_file_dict(self,_node_file_dict):
        """
        获得节点文件字典
        """
        import lib.common.md5 as _md5
        _dict = {}
        if _node_file_dict:
            for k, v in _node_file_dict.items():
                if v:
                    _node_fildict = {}
                    for _node, _nodefile in v.items():
                        _base_name=os.path.basename(_nodefile)
                        _judge=True
                        _target_file = os.path.join(self._targepath, _base_name)
                        if _target_file and os.path.exists(_target_file):
                            _con=_md5.Md5().contrast_md5(_nodefile, _target_file)
                            if _con == True:
                                _judge=False
                        if _judge==True:
                            _node_fildict[_node]=_nodefile
                    if _node_fildict:
                        _dict[k]=_node_fildict
        return _dict



    def cover_nodefile_dict(self, _dict, _cover=None):
        u"""
        转换节点文件格式
        :param _dict: 点文件字典({nodetype:{node:nodefile}}
        :param _cover: 转换的格式
        :return:
        """
        _cover_dict = {}
        if _cover and _dict:
            for k, v in _dict.items():
                if v:
                    _cov_dict = v
                    for _node, _nodefile in v.items():
                        if _nodefile and os.path.exists(_nodefile):
                            _basename = os.path.basename(_nodefile)
                            _base, _suffix = os.path.splitext(_basename)
                            if _suffix.lower() != _cover:
                                _nodefilen = u'{}/{}{}'.format(self.local_dir, _base, _cover)
                                _result = self._cover_nodefile(_nodefile, _nodefilen)
                                if _result == True:
                                    node.BaseNodeProcess().set_nodeattr_key(_node, self._nodefile_data[k], _nodefilen)
                                    _cov_dict[_node] = _nodefilen
                    if _cov_dict:
                        _cover_dict[k] = _cov_dict
        return _cover_dict

    def _cover_nodefile(self, _sorcefile, _targefile):
        u"""
        转换贴图格式
        :param _sorcefile: 源文件(转换前)
        :param _targefile: 目标文件(转换后)
        :return:
        """

        import lib.maya.process.image_process as _img
        if _targefile and os.path.exists(_targefile):
            try:
                os.remove(_targefile)
            except:
                pass

        try:
            _img.cover_imgageform(_sorcefile, _targefile)
            return True
        except:
            return False

    def copy_nodefile_dict(self, _nodefile_dict, _targedir,_copy):
        u"""
        复制贴图到目标路径
        :param _nodefile_dict:节点文件字典({nodetype:{node:nodefile}}
        """
        _dict = {}
        _source_target_dict = {}
        import lib.common.md5 as _md5
        if _nodefile_dict:
            for k, v in _nodefile_dict.items():
                if v:
                    for _node, _nodefile in v.items():
                        _filelist = []
                        _targefile = ''
                        _seq_handle = sequence.FileselectSequence(_nodefile)
                        # udim文件判断
                        if nodefile.judge_udim(k, _node, _nodefile) in [1]:
                            _filelist = _seq_handle.select_udim_filelist()
                        elif nodefile.judge_frame(k, _node, _nodefile) in [1]:
                            _filelist = _seq_handle.select_frame_filelist()
                        elif nodefile.judge_assframe(k, _node, _nodefile) in [1]:
                            _filelist = _seq_handle.select_ass_filelist()
                        else:
                            _filelist = [_nodefile]

                        if _filelist:
                            _addlist = self.select_nodefiles_addsuffix(_filelist)
                            if _addlist:
                                _filelist.extend(_addlist)
                            # 复制贴图
                            if _copy==True:
                                _copy_dict = self._copy_files(_filelist, _targedir)
                                if _copy_dict:
                                    _dict.update(_copy_dict)
                            for _file in _filelist:
                                _path, _basename = os.path.split(_file)
                                _target_file=u'{}/{}'.format(_targedir, _basename)
                                _judge=True
                                _con=_md5.Md5().contrast_md5(_nodefile, _target_file)
                                if _con==True:
                                    _judge=False
                                if _judge==True:
                                    _source_target_dict[_file]=_target_file

        return _dict,_source_target_dict

    def select_nodefiles_addsuffix(self, _nodefilelist):
        """
        由节点文件列表，获得相对应的附加文件列表
        """
        _list = []
        if _nodefilelist and self.addsuffix:
            for i in range(len(_nodefilelist)):
                _fil, _suffix = os.path.splitext(_nodefilelist[i])
                for j in range(len(self.addsuffix)):
                    _newfile = u"{}{}".format(_fil, self.addsuffix[j])
                    if _newfile and os.path.exists(_newfile) and _newfile not in _list:
                        _list.append(_newfile)
        return _list

    def set_targe_nodefiles(self, _nodefile_dict, _targedir, ex=False):
        u"""
        将节点文件 设置到目标路径
        :param _nodefile_dict:节点文件字典({nodetype:{node:nodefile}}
        :param _targedir:目标文件夹
        :param ex:为True时,节点文件存在时设置，为False时,节点文件无论是否存在都会设置
        """
        _list = []
        if _nodefile_dict and _targedir:
            for k, v in _nodefile_dict.items():
                if v:
                    for _node, _nodefile in v.items():
                        _targe_file = self._get_targefile(_nodefile, _targedir)
                        if ex != True and _targe_file:
                            # 设置
                            try:
                                node.BaseNodeProcess().set_nodeattr_key(_node, self._nodefile_data[k], _targe_file)
                                _list.append(node)
                            except:
                                pass
                        if ex == True and _targe_file and os.path.exists(_targe_file):
                            # 设置
                            try:
                                node.BaseNodeProcess().set_nodeattr_key(_node, self._nodefile_data[k], _targe_file)
                                _list.append(node)
                            except:
                                pass

        return _list

    def _get_targefile(self, _sorcefile, _targedir):
        u"""
        获取目标文件
        """
        if _sorcefile and _targedir:
            return os.path.join(_targedir, os.path.basename(_sorcefile))

    def set_sequence(self, _attr_dict):
        """
        序列帧设置(是序列帧，但指向不是序列帧序列，进行序列帧序列设置)
        :param _attr_dict:例如{u'file': {u'MapFBXASC032FBXASC03514': u'D:/test/tex/TEX/T_1012_Hair.png'}}
        """
        if _attr_dict:
            for k, v in _attr_dict.items():
                if v:
                    for m, n in v.items():
                        seq_handle = sequence.SequenceselectFile(n)
                        _framefile = ''
                        if nodefile.judge_udim(k, m, n) == 2:
                            _framefile = seq_handle.select_file_udim()
                        if nodefile.judge_frame(k, m, n) == 2:
                            _framefile = seq_handle.select_file_frame()
                        if nodefile.judge_assframe(k, m, n) == 2:
                            _framefile = seq_handle.select_file_ass()
                        if _framefile:
                            node.BaseNodeProcess().set_nodeattr_key(m, self._nodefile_data[k], _framefile)
        return True

    def _get_nodedict(self):
        u"""
        获得相应node节点字典({'file':[u'tank_logo_1']})
        """
        if self._nodetypelist:
            return {i: node.BaseNodeProcess().select_nodetype_nodes(i) for i in self._nodetypelist if
                    node.BaseNodeProcess().select_nodetype_nodes(i)}

    def _get_nodefiles(self, nodedict):
        u"""
        获得相应节点文件
        """
        _dict = {}
        if nodedict:
            for k, v in nodedict.items():
                _attr = self._nodefile_data[k]
                if v:
                    _node_fildict = {i: (node.BaseNodeProcess().get_nodeattr_key(i, _attr).replace('..', '/')) for i in
                                     v if node.BaseNodeProcess().get_nodeattr_key(i, _attr)}
                if _node_fildict:
                    _dict[k] = _node_fildict
        return _dict

    def _copy_files(self, _sourcefiles, _targedir):
        u"""
        将列表源文件，复制到目标路径
        :param _sourcefiles:需要复制的文件列表
        :parm _targedir:目标路径f
        """
        import lib.common.md5 as _md5
        _dict = {}
        _copy_dict = {}
        _error_dict = {}
        _nocopy_dict = {}
        if _sourcefiles and _targedir:
            if not os.path.exists(_targedir):
                self._creat_dir(_targedir)
            for _file in _sourcefiles:
                if _file and os.path.exists(_file):
                    _copy=True
                    _targe_file = os.path.join(_targedir, os.path.basename(_file))
                    if _targe_file and os.path.exists(_targe_file):
                        _con=_md5.Md5().contrast_md5(_file, _targe_file)
                        if _con == True:
                            _copy=False
                    if _copy==True:
                        _result = self._copy_file(_file, _targe_file)
                        if _result and _result == True:
                            _copy_dict[_file] = _targe_file
                        elif _result == False:
                            _error_dict[_file] = _targe_file
                        else:
                            _nocopy_dict[_file] = _targe_file
        if _copy_dict:
            _dict['copy_ok'] = _copy_dict
        if _error_dict:
            _dict['copy_error'] = _error_dict
        if _nocopy_dict:
            _dict['copy_no'] = _nocopy_dict
        return _dict

    def _copy_file(self, _sourcefile, _targefile):
        u"""
        复制文件
        :param _sourcefile:需要复制的文件
        :param _targefile:复制后的目标文件
        """
        import shutil
        import os
        _targedir = os.path.split(_targefile)[0]
        # 创建路径
        if not os.path.exists(_targedir):
            self._creat_dir(_targedir)
        # 复制
        if _md5.Md5().contrast_md5(_sourcefile, _targefile) != True:
            if os.path.exists(_targefile):
                try:
                    os.chmod(_targefile, 0777)
                    os.remove(_targefile)
                except:
                    pass

            try:
                shutil.copy2(_sourcefile, _targefile)
                return True
            except:
                return False

    def contrast_files(self, _sorcefile, _targefile):
        u"""
        对比文件
        :param _sourcefile:需要复制的文件
        :param _targefile:复制后的目标文件
        :return 为True时，代表源文件 ,目标文件均存在，且两个文件相同，为False时，代表文件均在且两个文件不一致，为None时，代理有文件不存在
        """
        _result = None
        if _sorcefile and _targefile and os.path.exists(_sorcefile) and os.path.exists(_targefile):
            if _sorcefile == _targefile:
                return True
            if _sorcefile != _targefile:
                _md5_sorce = nodefile.get_MD5(_sorcefile)
                _md5_targe = nodefile.get_MD5(_targefile)
                if _md5_sorce == _md5_targe:
                    return True
                else:
                    return False
        return _result

    def _creat_dir(self, dir):
        u"""
        创建路径
        :param dir: 路径名，例如"D:/temp"
        :return: 为True时，创建成功，为False时，未创建成功
        """
        if dir and not os.path.exists(dir):
            try:
                os.makedirs(dir)
                return True
            except:
                return False

# if __name__ == '__main__':
#     _targepath = 'D:/test'
#     _handle = CollectNodeFile(_targepath, ['file'])
#     _handle.collect_nodefiles(ex=True,_cover='.tif')


#     _handle.collect_nodefiles()
