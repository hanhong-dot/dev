# -*- coding: utf-8 -*-#
# Python       : python 2.7.16
# -------------------------------------------------------------------------------
# NAME         : process_package
# Describe     : 处理程序打包字典
# Version      : v0.01
# Author       : linhuan
# Email        : hanhong@papegames.net
# DateTime     : 2022/6/11__13:37
# -------------------------------------------------------------------------------
# -------------------------------------------------------------------------------
# example:  {'publish': [{u'des_path': 'D:/aaa.bmp',
# 	                     u'src_path': 'Y:/Project/x3/Assets/Chr/CB001002xiongda/Mod/Mod_hig/version/maya/aaa.bmp'}]}
# -------------------------------------------------------------------------------

def datapack(filepaths, tag, down=False, up=False,work_file='', ref_info='',*args, **kwargs):
    '''
    给process处理函数封装字典
    :param filepaths:列表
    :param tag:  publish,master,tex,ass等  注意：标记publish,master是要上传到数据库的
    :param args:
    :param kwargs: 其他字典参数
    :return: 字典
    '''
    _baselist = []
    _basedict = {}
    for obj in filepaths:
        _baselist.append({u'src_path': obj[0], u'des_path': obj[1], 'down_path': down, 'up_path': up,'work_file':work_file,'ref_info':ref_info})
    return {tag: _baselist}




def datapack_dict(filedict, down=False, up=False):
    u"""
    将{sourcefile:targefile} 字典，转换成 [{u'src_path': sourcefile,u'des_path': targefile}] 列表
    :param filedict: 字典，例如{"D:/tree.abc":"Y:/tree.abc","D:/stone.abc":"Y:/stone.abc"}
    :return: 上传打包列表，
    """
    _filelist = []
    _down_path = ''
    _up_path = ''
    if filedict:
        for k, v in filedict.items():
            _dict = {}
            if k and v:
                _filelist.append({u'src_path': k, u'des_path': v, 'down_path': down, 'up_path': up})
    return _filelist


def mergedict(a_dict, b_dict):
    """
    合并字典，如key值相同的则把value值添加加上，不同key值则连同key：value同时续接上
    :param a_dict: {'fbx': [{'a': 'b'}, {'e': 'f'}], 'yeti': [{'y1': 'g1'}], 'abc': [{'a1': 'b1'}, {'e1': 'f1'}]}
    :param b_dict: {'fbx': [{'c': 'd'}], 'yeti': [{'y2': 'g2'}], 'xgen': [{'h': 'i'}]}
    :return: 字典 如： {'fbx': [{'a': 'b'}, {'e': 'f'}, {'c': 'd'}], 'xgen': [{'h': 'i'}],
                      'abc': [{'a1': 'b1'}, {'e1': 'f1'}], 'yeti': [{'y1': 'g1'}, {'y2': 'g2'}]}
    """
    if a_dict.values() and b_dict.values():
        # return {a_dict.keys()[0]:a_dict.values()[0] + b_dict.values()[0]}  # 取消该旧的方式
        result_dict = a_dict
        for key in b_dict.keys():
            if key in result_dict.keys():
                result_dict[key] += b_dict[key]  # 等于自身+新值
            else:
                result_dict[key] = b_dict[key]
        return result_dict

    elif a_dict.values and not b_dict.values():
        return a_dict
    else:
        return b_dict


# if __name__ == '__main__':
#     a_dict = {'fbx': [{'a': 'b'}, {'e': 'f'}], 'yeti': [{'y1': 'g1'}], 'abc': [{'a1': 'b1'}, {'e1': 'f1'}]}
#     b_dict = {'fbx': [{'c': 'd'}], 'yeti': [{'y2': 'g2'}], 'xgen': [{'h': 'i'}]}
#     print(mergedict(a_dict, b_dict))
