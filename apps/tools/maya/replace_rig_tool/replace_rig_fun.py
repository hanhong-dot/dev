# -*- coding: utf-8 -*-
# -----------------------------------
# @File    : replace_rig_fun.py
# @Author  : linhuan
# @Time    : 2025/10/9 11:31
# @Description : 
# -----------------------------------
import method.maya.common.reference as common_reference
import method.maya.common.file as common_file
import os

import maya.cmds as cmds

import os

from apps.tools.maya.replace_rig_tool import cover_maya_2018

reload(cover_maya_2018)


def replace_rig(need_to_replace_rig_file, replace_rig_file, log_handle=None):
    replace_info = common_reference.get_reference_info()
    if not replace_info:
        cmds.warning(u'当前场景没有参考文件'.encode('gbk'))
        if log_handle:
            log_handle.warning('当前场景没有参考文件')
        return

    need_to_replace_rig_file = need_to_replace_rig_file.replace('\\', '/')
    replace_rig_file = replace_rig_file.replace('\\', '/')
    replace_list = []

    for k, v in replace_info.items():
        if not k or not v:
            continue
        refRN = k
        ns, ref_file = v
        ref_file = ref_file.replace('\\', '/')
        __name_space = get_namespace_by_rig_file(replace_rig_file)
        if ref_file == need_to_replace_rig_file:
            try:
                cmds.file(replace_rig_file, loadReference=refRN)
                cmds.namespace(ren=[ns, __name_space])
                replace_list.append(ref_file)
            except:
                cmds.warning(u'替换失败:{}'.format(ref_file).encode('gbk'))
                if log_handle:
                    log_handle.warning('替换失败:{}'.format(ref_file))
                continue
    if not replace_list:
        cmds.warning(u'没有找到需要替换的绑定文件:{}'.format(need_to_replace_rig_file).encode('gbk'))
        if log_handle:
            log_handle.warning('没有找到需要替换的绑定文件:{}'.format(need_to_replace_rig_file))
        return False
    return True


def batch_replace_rig(batch_process_files, need_to_replace_rig_file, replace_rig_file, log_handle=None):
    maya_process_handle = common_file.BaseFile()
    __remove_files=[]
    for __file in batch_process_files:
        if log_handle:
            log_handle.info('开始处理:{}'.format(__file))
        if not __file:
            log_handle.info('文件路径为空，跳过')
            continue
        __file = __file.replace('\\', '/')

        if not os.path.isfile(__file):
            if log_handle:
                log_handle.append(u'文件不存在:{}'.format(__file).encode('gbk'))
            continue
        __new_file = __file.replace('.ma', '_changeRig.ma')
        cover_maya_2018.pre_process(__file, __new_file)
        if not os.path.isfile(__new_file):
            __new_file = __file

        try:
            maya_process_handle.open_file(__new_file)
        except:
            pass
        __result = False
        try:
            __result = replace_rig(need_to_replace_rig_file, replace_rig_file, log_handle)
        except:
            pass

        if not __result:
            continue
        maya_process_handle.save_file(__file)
        log_handle.info('替换完成:{}'.format(__file))
        if os.path.exists(__new_file):
            os.remove(__new_file)
        __remove_files.append(__new_file)
    if __remove_files:
        for __remove_file in __remove_files:
            if os.path.exists(__remove_file):
                os.remove(__remove_file)

    maya_process_handle.new_file()



def get_namespace_by_rig_file(rig_file):
    rig_file = rig_file.replace('\\', '/')
    rig_file_name = os.path.basename(rig_file)
    name_space = rig_file_name.split('.')[0]
    name_space = judge_reference_namespace(name_space)
    return name_space


def judge_reference_namespace(namespace, split='_'):
    namespacelist = reference_info().keys()
    if not namespacelist or namespace not in namespacelist:
        return namespace
    if namespace in namespacelist:
        while namespace in namespacelist:
            if split not in namespace:
                namespace = u"{}{}01".format(namespace, split)
            else:
                namespace = u"{}{}0{}".format(namespace.split(split)[0], split, int(namespace.split(split)[-1]) + 1)
            if namespace not in namespacelist:
                return namespace


def reference_info():
    return common_reference.get_reference_info()


if __name__ == '__main__':
    need_to_replace_rig_file = 'M:/projects/X3/publish/assets/role/FY006S/rig/maya/FY006S.drama_rig.ma'
    replace_rig_file = 'M:/projects/x3/publish/assets/role/FY005C/rbf/maya/FY005C.rbf.ma'
    replace_rig(need_to_replace_rig_file, replace_rig_file)
