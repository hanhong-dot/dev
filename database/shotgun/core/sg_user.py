# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       : sg_user
# Describe   : 说明描述
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2022/5/23__18:53
# -------------------------------------------------------
import database.shotgun.core.sg_base as sg_base


def get_user_userID(sg, user_name):
    """
    获取用户ID
    :param sg: sg实体
    :param user: 用户名
    :return: 获取资产ID的列表，否则为[] 如：[{'type': 'HumanUser', 'id': 207}]
    """
    fields = ['id']
    filters = [
        ['name', 'is', user_name],
    ]
    return sg.find('HumanUser', filters, fields)


def select_email_user(sg, user_email, user_fields=['name']):
    u"""
    从email 获取用户名
    :param sg: sg 实体
    :param user_email: email
    :param user_fields:
    :return:
    """
    filters = [
        ['email', 'is', user_email],
    ]
    return sg.find('HumanUser', filters, user_fields)


def select_user_user(sg, user_id, user_fields=['email']):
    '''
    查询用户信息
    :param sg: sg实体
    :param user_id: 用户ID
    :param user_fields: 用户字段,例如['email']
    :return: 用户列表 例如：{'type': 'HumanUser', 'id': 208, 'tags': [{'type': 'Tag', 'id': 209, 'name': '\xe6\xb7\xb1\xe5\x9c\xb3'}]}
    '''
    return sg_base.select_entity(sg, "HumanUser", user_id, user_fields)


def update_user_user(sg, user_id, **kwargs):
    '''
    更新用户信息
    :param sg: sg实体
    :param user_id: 用户ID
    :param kwargs:用户字段
    :return:True
    '''
    result = sg_base.update_entity(sg, "HumanUser", user_id, kwargs)
    if result:
        return True
    else:
        return False



def select_user_task(sg, user_ids, project_id=0, task_fields=[]):
    '''
    查询用户链接的任务信息
    :param sg: sg实体
    :param user_ids: 人员ID列表
    :param project_id: 项目ID, 如果有值，则返回该项目的任务
    :param task_fields: 任务字段
    :return: 任务列表 例如：[{'content': 'Lay_lay', 'project': {'type': 'Project', 'id': 91, 'name': 'XCM_2022DY'}, 'type': 'Task', 'id': 66666}]
    '''
    user_array = []
    for user_id in user_ids:
        user_dict = {'type': 'HumanUser', 'id': user_id}
        user_array.append(user_dict)

    project_data = {'type': 'Project', 'id': project_id}

    fields = ['content', 'project'] + task_fields
    if project_id == 0:
        filters = [
            ['task_assignees', 'is', user_array]
        ]
    else:
        filters = [['project', 'is', project_data],
                   ['task_assignees', 'is', user_array]
                   ]
    task_infos = sg.find("Task", filters, fields)
    return task_infos


# def get_current_useremaill():
#     u"""
#     获取当前用户邮箱
#     :return:
#     """
#     try:
#         import sgtk
#         from sgtk.descriptor import Descriptor
#         sg_auth = sgtk.authentication.ShotgunAuthenticator()
#         return sg_auth.get_user().login
#     except:
#         return ''

def get_current_useremaill():
    u"""
    获取当前用户邮箱
    :return:
    """
    import getpass
    return getpass.getuser()


def get_current_user():
    u"""
    获得当前用户信息
    :param sg: sg 实例
    :return:
    """
    import getpass
    return getpass.getuser()



def get_current_user_data(conf='Z:/dev/database/shotgun/toolkit/x3'):
    u"""

    Returns:

    """
    try:
        import sys
        sys.path.append('{}/install/core/python'.format(conf))
        import sgtk
        import getpass
        tk = sgtk.sgtk_from_path(conf)
        return tk_current_user(tk)
    except:
        get_current_user()

def tk_current_user(tk):
    u"""
    获取当前登录用户名
    Args:
        tk:

    Returns:

    """
    from tank import api
    import getpass
    user=api.get_authenticated_user()
    if user and user.login:
        current_login = user.login
    else:
        current_login = tk.execute_core_hook("get_current_login")



    if current_login is None:
        current_login  = getpass.getuser()

    fields = [
        "id",
        "type",
        "email",
        "login",
        "name",
        "image",
        "firstname",
        "lastname",
    ]
    g_shotgun_current_user_cache = tk.shotgun.find_one(
        "HumanUser", filters=[["login", "is", current_login]], fields=fields
    )
    return g_shotgun_current_user_cache


# def get_current_user():
#     u"""
#     获得当前用户信息
#     :param sg: sg 实例
#     :return:
#     """
#     import getpass
#     try:
#         import sgtk
#         from sgtk.descriptor import Descriptor
#         sg_auth = sgtk.authentication.ShotgunAuthenticator()
#         return sg_auth.get_user().login
#     except:
#         return getpass.getuser()


def get_current_username():
    u"""
    获取当前用户名
    :param sg:
    :return:
    """
    _user = get_current_user()
    try:
        return _user[0]['name']
    except:
        return _user


def get_current_userid(sg,user_name):
    u"""
    获取当前用户id
    :param sg:
    :return:
    """
    fields = ['id']
    filters = [
        ['login', 'is', user_name],
    ]
    return sg.find('HumanUser', filters, fields)



