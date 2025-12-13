# -*- coding: utf-8 -*-#
# -------------------------------------------------------
# NAME       : import_pose
# Describe   : 说明描述
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2025/4/28__下午8:24
# -------------------------------------------------------

import os
from apps.publish.ui.message.messagebox import msgview

ATTRS = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz']


def import_pose(pose_file_path):
    """
    导入pose
    :param pose_file_path: pose文件路径
    """
    result = msgview(u'请确定是否导入Pose文件', 1, 1)
    if result == 0:
        return

    pose_file_path = pose_file_path.decode('utf-8')
    if not pose_file_path or not os.path.exists(pose_file_path):
        msgview(u'Pose文件不存在,请检查', 1)
        return
    all_joins = procee_rig_file()
    __result = import_fbx_file(pose_file_path)
    # objs_key_transitions(all_joins, frame=10)

    if not __result:
        msgview(u'未正确导入Pose,请检查', 1)
        return
    else:
        msgview(u'已导入Pose,请检查当前文件', 2)
        return True

def import_db_pose(pose_file_path):
    """
    导入pose
    :param pose_file_path: pose文件路径
    """
    result = msgview(u'请确定是否导入DBPose文件', 1, 1)
    if result == 0:
        return

    pose_file_path = pose_file_path.decode('utf-8')
    if not pose_file_path or not os.path.exists(pose_file_path):
        msgview(u'DBPose文件不存在,请检查', 1)
        return
    all_joins = procee_rig_file()
    __result = import_fbx_file(pose_file_path)
    # objs_key_transitions(all_joins, frame=10)

    if not __result:
        msgview(u'未正确导入DBPose,请检查', 1)
        return
    else:
        msgview(u'已导入DBPose,请检查当前文件', 2)
        return True

def import_fbx_file(fbx_file):
    import maya.cmds as cmds
    if not fbx_file or not os.path.exists(fbx_file):
        return False

    try:
        cmds.file(fbx_file, i=True, type='FBX', ignoreVersion=True, ra=True, mergeNamespacesOnClash=False,
                  options="v=0;p=17,f=0", pr=True, importTimeRange="combine", loadReferenceDepth="all")
        return True
    except:
        return False


def procee_rig_file():
    import_reference()
    all_joins = get_all_joins()
    break_connect(all_joins)
    # objs_key_transitions(all_joins, frame=1)
    return all_joins


def break_connect(objs):
    if not objs:
        return
    for obj in objs:
        break_node_transform(obj)


def objs_key_transitions(objs, frame):
    import maya.cmds as cmds
    attrs = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz']
    if not objs:
        return
    cmds.currentTime(frame)

    for attr in attrs:
        cmds.setKeyframe(objs, attribute=attr)


def break_node_transform(obj):
    import maya.cmds as cmds
    if not obj:
        return
    for attr in ATTRS:
        if cmds.attributeQuery(attr, node=obj, exists=True):
            if cmds.listConnections(obj + '.' + attr):
                cons = cmds.listConnections((obj + '.' + attr), c=1, p=1)
                for i in range(0, len(cons), 2):
                    if cmds.nodeType(cons[i]) == 'animCurve':
                        cmds.delete(cons[i])
                    else:
                        try:
                            cmds.disconnectAttr(cons[i + 1], cons[i])
                        except:
                            pass


def get_all_joins():
    import maya.cmds as cmds
    all_joints = cmds.ls(type='joint')
    all_joints = [joint for joint in all_joints if not cmds.referenceQuery(joint, isNodeReferenced=True)]
    return all_joints


def import_reference():
    import method.maya.common.reference as refcommon
    refcommon.import_all_reference()
