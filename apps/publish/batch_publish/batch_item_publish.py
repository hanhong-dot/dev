# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       : batch_item_publish
# Describe   : 说明描述
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2024/1/4__17:24
# -------------------------------------------------------

def batch_publish(file_path, log_file):
    import sys

    sys.path.append(r'Z:\dev\database\shotgun\toolkit\x3\install\core\python')
    sys.path.append(r'z:\dev')

    import method.maya.common.file as file_common

    file_common.BaseFile().open_file(file_path)

    import apps.launch.maya.interface.maya_launch as maya_launch
    maya_launch.load_env_py2()
    import apps.publish.batch_publish.item_batch_publish as item_batch_publish
    reload(item_batch_publish)
    return item_batch_publish.MayaBatchCheckPublish(file_path, log_file).batch_process()

def batch_cover_fbx_publish(file_path, log_file):
    import sys

    sys.path.append(r'Z:\dev\database\shotgun\toolkit\x3\install\core\python')
    sys.path.append(r'z:\dev')
    import method.maya.common.file as file_common

    import apps.launch.maya.interface.maya_launch as maya_launch
    maya_launch.load_env_py2()
    import apps.publish.batch_publish.batch_cover_fbx_to_publish as batch_cover_fbx_to_publish
    reload(batch_cover_fbx_to_publish)
    return batch_cover_fbx_to_publish.BatchCoverFbxToPublish(file_path, log_file).batch_process()
