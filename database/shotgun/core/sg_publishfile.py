# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       : sg_publishfile
# Describe   : 说明描述
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2022/6/20__20:16
# -------------------------------------------------------
PUBLISHFILE_TYPE = ['Maya Scene', 'Maya FBX', 'Motion Builder FBX', 'MoBu Export FBX', 'Mocap Scene', 'UE Scene','Unity_FBX','Unity_XML']


def get_publishfile_type(name='Maya Scene'):
    u"""
    获取
    """
    if name == 'Maya Scene':
        return {'id': 1, 'name': 'Maya Scene', 'type': 'PublishedFileType'}
    elif name == 'Maya FBX':
        return {'id': 46, 'name': 'Maya FBX', 'type': 'PublishedFileType'}
    elif name == 'Alembic Cache':
        return {'id': 6, 'name': 'Alembic Cache', 'type': 'PublishedFileType'}
    elif name == 'Motion Builder FBX':
        return {'id': 48, 'name': 'Motion Builder FBX', 'type': 'PublishedFileType'}
    elif name == 'MoBu Export FBX':
        return {'id': 65, 'name': 'MoBu Export FBX', 'type': 'PublishedFileType'}
    elif name == 'Mocap Scene':
        return {'id': 86, 'name': 'Mocap Scene', 'type': 'PublishedFileType'}
    elif name == 'UE Scene':
        return {'id': 87, 'name': 'UE Scene', 'type': 'PublishedFileType'}
    elif name =='Unity_FBX':
        return {'id': 93, 'name': 'Unity_FBX', 'type': 'PublishedFileType'}
    elif name == 'Unity_XML':
        return {'id': 94, 'name': 'Unity_XML', 'type': 'PublishedFileType'}
