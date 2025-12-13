# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       : reference
# Describe   : reference 相关函数
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2022/7/15__17:25
# -------------------------------------------------------

import maya.cmds as cmds


def import_all_reference():
    u"""
    导入文件中多重参考
    Returns:

    """

    _reffiles = get_root_reffiles()
    while _reffiles:
        import_reference(_reffiles)
        _reffiles = get_root_reffiles()


def import_root_references():
    u"""
    导入最外层参考
    Returns:

    """
    _reffiles = get_root_reffiles()
    # 导入参考
    import_reference(_reffiles)


def get_reference_info(fromSelect=0):
    """
    文件参考信息
    :param fromSelect: 是否选择物体——0代表获取整个场景的参考信息，1代表从选中物体获取参考信息。
    :return: 参考namespace,参考RN节点,参考路径
    """
    result = {}
    if fromSelect:
        selObjs = cmds.ls(sl=1)
        # print('selObjs==>', selObjs)
        if selObjs:
            for obj in selObjs:
                refRN = ''
                try:
                    refRN = cmds.referenceQuery(obj, referenceNode=1)
                except:
                    pass
                # print('refRN==>', refRN)
                if refRN:
                    ns = cmds.referenceQuery(refRN, namespace=1)
                    # print('ns==>', ns)
                    refPath = cmds.referenceQuery(refRN, filename=True)  # 获取参考节点中的参考文件路径
                    if '{' in refPath:
                        refPath = refPath.split('{')[0]
                    result[refRN] = [ns, refPath]
    else:
        refs = cmds.file(q=1, r=1)
        if refs:
            for ref in refs:
                refRN = cmds.referenceQuery(ref, referenceNode=1)
                refPath = ref
                ns = cmds.file(refPath, namespace=1, q=1)
                if '{' in refPath:
                    refPath = refPath.split('{')[0]
                result[refRN] = [ns, refPath]

        return result


def import_reference(reffiles):
    u"""
    导入参考
    Args:
        reffiles: 参考列表

    Returns:

    """
    if reffiles:
        for _reffile in reffiles:
            try:
                cmds.file(_reffile, ir=1)
            except:
                pass


def get_root_reffiles():
    u"""
    获取文件内参考文件
    Returns:

    """
    return cmds.file(q=1, r=1)


def get_root_refrn():
    u"""
    获取文件内参考节点(最外层)
    Returns:

    """
    _ref_files = get_root_reffiles()
    if _ref_files:
        return [select_reffile_refrn(i) for i in _ref_files]


def select_reffile_refrn(_reffile):
    u"""
    从参考文件获取参考节点
    Args:
        _reffile:

    Returns:

    """
    if _reffile and cmds.ls(_reffile):
        return cmds.referenceQuery(_reffile, referenceNode=1)


def remove_reference(checkload=False):
    u"""
    清理参考
    :param checkload: checkload 为True时，清理unload 参考，为False时，不判断load，清理所有参考)
    :return:
    """
    _refinfo = get_reference_info()
    if _refinfo:
        for k, v in _refinfo.items():
            if k and v:
                if checkload==True:
                    load = cmds.referenceQuery(k, isLoaded=1)
                    if load == False:
                        remove_ref(k)
                else:
                    remove_ref(k)


def remove_ref(_refn):
    u"""
    :param _refn: 参考的refRN节点
    :return:
    """

    try:
        cmds.file(rfn=_refn, removeReference=1)
    except:
        pass


if __name__ == '__main__':
    import_all_reference()
