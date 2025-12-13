# -*- coding: utf-8 -*-
# -----------------------------------
# @File    : add_subtasks.py
# @Author  : linhuan
# @Time    : 2025/8/13 11:00
# @Description : 
# -----------------------------------
import sys
import os

sys.path.append('Z:/dev')

import database.shotgun.tools.actionitem.action_item_server as action_item_server
import database.shotgun.core.sg_base as sg_base

INHERIT = ['step', 'entity']


class AddSubTasks(object):
    def __init__(self):
        self.project = sys.argv[1]
        self.select_ids = sys.argv[2].split(',')

        self.entity_type = sys.argv[3]
        self.sg = action_item_server.action_login()
        self.project_data = self.get_project()

    def add_sub_tasks(self):
        if not self.select_ids:
            return False, u"没有选择任务"
        for task_id in self.select_ids:
            task_id = int(task_id)
            if not task_id:
                continue
            if not self.entity_type:
                return False, u"没有选择实体类型"
            if not self.project:
                return False, u"没有选择项目"
            if not self.sg:
                return False, u"没有连接到Shotgun服务器"

            result, msg = self.add_sub_tasks_by_assigned_to(task_id)
            print(result)
            print(msg)

            if not result:
                return result, msg

    def add_sub_tasks_by_assigned_to(self, task_id):
        assigend_to = self.get_assigned_to(self.entity_type, task_id)

        if not assigend_to:
            return False, "This task has not been assigned to a responsible person"
        sub_tasks = self.get_sub_tasks(task_id)
        count = self.get_laster_count_by_sub_tasks(sub_tasks)
        # count = 0
        # if sub_tasks:
        #     count = len(sub_tasks)

        ex_assined_to = []
        cr_assigned_to = []
        task_name = self.get_entity_name(self.entity_type, task_id)

        if sub_tasks:
            for sub_task in sub_tasks:
                if sub_task.get('task_assignees'):
                    ex_assined_to.extend(sub_task['task_assignees'])
            ex_assined_to_ids = []

            if not ex_assined_to:
                cr_assigned_to = assigend_to
            else:
                ex_assined_to_ids = [x['id'] for x in ex_assined_to]
            if not ex_assined_to_ids:
                cr_assigned_to = assigend_to
            for assigned in assigend_to:
                if assigned['id'] not in ex_assined_to_ids:
                    cr_assigned_to.append(assigned)
        else:
            cr_assigned_to = assigend_to
        if not cr_assigned_to:
            return False, u"There is no responsible person who needs to add subtasks"
        __sub_tasks = []

        sub_task_name = ''
        for i in range(len(cr_assigned_to)):
            __letter = num_to_letter(i + count)
            __sub_task_name = "{}_{}".format(task_name, __letter)

            if i == 0:
                sub_task_name = __sub_task_name
            else:
                sub_task_name = "{},{}".format(sub_task_name, __sub_task_name)
            sub_task = self.add_sub_task(task_id, __sub_task_name, cr_assigned_to[i])
            if sub_task:
                __sub_tasks.append(sub_task)
        if sub_tasks:
            __sub_tasks.extend(sub_tasks)
        if __sub_tasks:
            self.updata_parent_task(task_id, __sub_tasks)
        return True, u"{} adding subtasks succeeded({})".format(task_name, sub_task_name)

    def get_sub_tasks(self, parent_task_id):
        sub_tasks = self.sg.find('Task',
                                 [['sg_parent_task', 'is', {'type': self.entity_type, 'id': int(parent_task_id)}]],
                                 ['id', 'content', 'task_assignees'])
        return sub_tasks

    def get_laster_count_by_sub_tasks(self, sub_tasks):
        count = 0
        __sub_task_names = []
        if sub_tasks:
            for sub_task in sub_tasks:
                if sub_task.get('content'):
                    __sub_task_names.append(sub_task['content'])
        if __sub_task_names:
            __sub_task_names.sort()
            last_name = __sub_task_names[-1]
            if last_name:
                last_letter = last_name.split('_')[-1]
                count = letter_to_num(last_letter)+1
        return count

    def get_assigned_to(self, entity_type, entity_id):
        entity = self.sg.find_one(entity_type, [['id', 'is', int(entity_id)]], ['task_assignees'])
        if entity and entity['task_assignees']:
            return entity['task_assignees']
        return None

    def get_entity_name(self, entity_type, entity_id):
        entity = self.sg.find_one(entity_type, [['id', 'is', int(entity_id)]], ['content'])
        if entity and entity.get('content'):
            return entity['content']
        return None

    def get_inherit_data(self, entity_type, entity_id):
        entity = self.sg.find_one(entity_type, [['id', 'is', int(entity_id)]], INHERIT)
        if entity:
            inherit_data = {}
            for key in INHERIT:
                if key in entity:
                    inherit_data[key] = entity[key]
            return inherit_data
        return None

    def add_sub_task(self, parent_task_id, sub_task_name, assigned_to=None):
        data = {
            'project': self.project_data,
            'content': sub_task_name,
            'sg_status_list': 'wtg',
            'sg_parent_task': {'type': self.entity_type, 'id': parent_task_id}
        }

        inherit_data = self.get_inherit_data(self.entity_type, parent_task_id)
        if inherit_data:
            data.update(inherit_data)
        if assigned_to:
            if isinstance(assigned_to, dict):
                assigned_to = [assigned_to]
            elif isinstance(assigned_to, list):
                assigned_to = assigned_to

            data['task_assignees'] = assigned_to

        new_task = self.sg.create('Task', data)
        return new_task

    def updata_parent_task(self, parent_task_id, sub_tasks):
        self.sg.update(self.entity_type, int(parent_task_id), {'task_sg_parents_tasks': sub_tasks})

    def get_project(self):
        """获取项目"""
        project = self.sg.find_one('Project', [['name', 'is', self.project]], ['id', 'name'])
        return project


def num_to_letter(num):
    """数字转字母"""
    if num < 0:
        return ''
    letter = ''
    while num >= 0:
        letter = chr(num % 26 + ord('a')) + letter
        num = num // 26 - 1
    return letter


def letter_to_num(letter):
    """字母转数字"""
    num = 0
    for i, char in enumerate(reversed(letter)):
        num += (ord(char) - ord('a') + 1) * (26 ** i)
    return num - 1


# def get_assigned_to(entity_type, entity_id):
#     sg= action_item_server.action_login()
#     entity = sg.find_one(entity_type, [['id', 'is', int(entity_id)]], ['task_assignees'])
#     print('entity', entity)
#     if entity and entity['task_assignees']:
#         return entity['task_assignees']
#     return None

if __name__ == '__main__':
    # sg = action_item_server.action_login()
    # fields = ['id', 'name']
    # filters = [
    #     ['name', 'is', 'X3']
    # ]
    # project_data = sg.find('Project', filters, fields)
    #
    # data = {'content': 'drama_mdl_a', 'step': {'type': 'Step', 'id': 176, 'name': 'mod'}, 'sg_status_list': 'wtg',
    #         'task_assignees': [{'type': 'HumanUser', 'id': 543, 'name': '\xe5\xa4\xa7\xe7\x9b\x9b'}],
    #         'sg_parent_task': {'type': 'Task', 'id': 199498}, 'project': {'type': 'Project', 'id': 114, 'name': 'X3'},
    #         'entity': {'type': 'Asset', 'id': 21871, 'name': 'YS014C'}}
    #
    # sg.create('Task', data)
    # handle= AddSubTasks()

    # task_id=199498
    # print(get_assigned_to('Task', task_id))

    AddSubTasks().add_sub_tasks()
    # num = 27
    # print(num_to_letter(num))
    # letter= '27'
    # print(letter_to_num(letter))
