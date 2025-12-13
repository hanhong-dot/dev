# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       : shotgunfuns
# Describe   : 说明描述
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2023/3/14__14:05
# -------------------------------------------------------
import getpass
import pprint
import re
import database.shotgun.core.sg_asset as sg_asset
import database.shotgun.core.sg_analysis as sg_config
# import shotgun.v2_0.core.sg_episode as sg_episode
import database.shotgun.core.sg_user as sg_people
import database.shotgun.core.sg_sequence as sg_sequence
import database.shotgun.core.sg_shot as sg_shot
import database.shotgun.core.sg_task as sg_task
import database.shotgun.core.sg_image as sg_image
# import workfile.v2_0.config.workfile_config as workfile_config
from database.shotgun.core import sg_base


class ShotgunClass(object):
    def __init__(self):
        self.sg_login = sg_config.Config().login()

        # temp = self.sg_login.schema_field_read('Asset',field_name='sg_asset_type')
        # temp = self.sg_login.schema_entity_read()

        # filters = [['project', 'is', {'type': 'Project', 'id': 91}]]
        # field = ['project', 'sg_status_list']
        # summary_fields = [{'field': 'id', 'type': 'record_count'}]
        # temp = self.sg_login.summarize(entity_type='Version', filters=filters, summary_fields=summary_fields)
        # pprint.pprint(temp)
        # temp = self.get_step_entity("ani", "Asset")
        # pprint.pprint(temp)
        self.user_name = getpass.getuser()
        self.user_entity_list = sg_people.get_user_userID(self.sg_login, self.user_name)
        self.user_entity = dict()
        self.user_id = 0
        if self.user_entity_list:
            self.user_entity = self.user_entity_list[0]
            self.user_id = self.user_entity['id']

    def get_calculate_worktime(self, plan_time, actual_time):
        actual = 0.0
        plan = 0.0
        if actual_time and actual_time > 0:
            actual = actual_time
        if plan_time and plan_time > 0:
            plan = plan_time
        return str('%.2f' % actual) + "/" + str('%.2f' % (plan / 60.0))

    # def get_task_status_icon(self, task_status):
    #     if not task_status:
    #         task_status = "none"
    #     icon_path = r'Y:\Development\Modules\Python\Resources\icon\shotgun\task'
    #     icon_path += '\\'
    #     icon_path += task_status
    #     icon_path += ".png"
    #     return icon_path

    def get_mytask_list(self, project_id=0):
        fields = ['content',
                  'project',
                  'project.Project.sg_type',
                  'entity',
                  'step',
                  'sg_status_list',
                  'start_date',
                  'due_date',
                  'sg_description',
                  'est_in_mins',
                  'task_assignees',
                  'sg_custom_totalrealwork',
                  'entity.Asset.sg_asset_type',
                  'entity.Shot.sg_sequence.Sequence.code',
                  'entity.Shot.sg_sequence.Sequence.episode.Episode.code']
        task_entity_list = sg_people.select_people_task(self.sg_login, [self.user_id], project_id=project_id,
                                                        task_fields=fields)
        return task_entity_list

    def get_entity_list(self, entity_type, project_id=0, config=None, limit=50, page=0, contain_text=None,
                        filter_list=[]):
        if config:
            _config = config

        filters = [
            ['project.Project.id', 'is', project_id]
        ]

        if contain_text:
            contains = ['code', 'contains', contain_text]
            filters.append(contains)

        result_complex_filter = self.get_complex_filter(entity_type, _config, filter_list)
        filters += result_complex_filter
        field = _config['Entity'][entity_type]['field']
        hide_field = _config['Entity'][entity_type]['hide_field']
        fields = field + hide_field
        return self.sg_login.find(entity_type, filters, fields, limit=limit, page=page)

    def get_project_list(self):
        filters = [
            ["sg_status", "is", "Active"]
        ]
        fields = ["name", "sg_status"]
        return self.sg_login.find("Project", filters, fields)

    def get_project_list_with_image(self, user_name):
        filters = [
            ["sg_status", "is", "Active"],
            ["users.HumanUser.login", "is", user_name],
        ]
        fields = ["name", "sg_status", "image", "sg_type"]
        return self.sg_login.find("Project", filters, fields)

    def get_complex_filter(self, entity_type, config, filter_list):
        result_filters = []
        if filter_list:
            items = [config['Filter'][entity_type][_filter] for _filter in filter_list if
                     filter_list and '=' not in _filter]
            # 排序
            items.sort(key=lambda x: x[0])

            # 分类
            dic = dict()
            for item in items:
                key = item[0]
                dic[key] = dic.get(key, []) + [item]

            # 生成分类后的列表
            filter_items_list = list(dic.values())
            # 加入复杂过滤器
            for filter_items in filter_items_list:
                complex_filter = {
                    "filter_operator": "any",
                    "filters": filter_items
                }
                result_filters.append(complex_filter)
        return result_filters

    def get_search_entity_list(self, entity_type, project_id=0, contain_text=None, field=[]):

        filters = [
            ['project.Project.id', 'is', project_id]
        ]

        if contain_text:
            non_chinese = re.findall(r'[\u4e00-\u9fff]+', contain_text)
            if non_chinese:
                contains = ['code', 'contains', contain_text]
            else:
                contains = ['sg_chinesename', 'contains', contain_text]
            filters.append(contains)

        fields = field
        return self.sg_login.find(entity_type, filters, fields)

    def get_asset_type(self):
        asset_type_entity = self.sg_login.schema_field_read('Asset', field_name='sg_asset_type')
        asset_type_list = asset_type_entity['sg_asset_type']['properties']['valid_values']['value']
        asset_type_list.sort()
        asset_type_list_temp = []
        for index in range(len(asset_type_list)):
            asset_type_dict = dict()
            asset_type_dict['type'] = 'AssetType'
            asset_type_dict['id'] = index
            asset_type_dict['code'] = asset_type_list[index]
            asset_type_list_temp.append(asset_type_dict)
        return asset_type_list_temp

    def get_asset_list(self, project_id, asset_type=None, config=None):
        if config:
            _config = config

        filters = [
            ['project.Project.id', 'is', project_id],
            ['sg_asset_type', 'is', asset_type]
        ]

        field = _config['field']
        hide_field = _config['hide_field']
        fields = field + hide_field
        return self.sg_login.find("Asset", filters, fields)

    def get_sequence_list(self, project_id, config=None, limiter=0):
        if config:
            _config = config

        filters = [
            ['project.Project.id', 'is', project_id]
        ]

        field = _config['field']
        hide_field = _config['hide_field']
        fields = field + hide_field
        return self.sg_login.find("Sequence", filters, fields, limit=limiter)

    def get_episode_list(self, project_id, config=None, limiter=0):
        if config:
            _config = config

        filters = [
            ['project.Project.id', 'is', project_id]
        ]

        field = _config['field']
        hide_field = _config['hide_field']
        fields = field + hide_field

        return self.sg_login.find("Episode", filters, fields, limit=limiter)

    def get_sequence_shot(self, entity_id, config=None):
        if config:
            _config = config

        field = _config['field']
        hide_field = _config['hide_field']
        fields = field + hide_field
        return sg_sequence.select_sequence_shot2(self.sg_login, entity_id, shot_fields=fields)

    def get_entity_task(self, entity_type, entity_id, config=None):
        if config:
            _config = config

        field = _config['field']
        hide_field = _config['hide_field']
        fields = field + hide_field
        if entity_type == 'Asset':
            return sg_asset.select_asset_task2(self.sg_login, entity_id, task_fields=fields)
        if entity_type == 'Shot':
            return sg_shot.select_shot_task2(self.sg_login, entity_id, task_fields=fields)
        if entity_type == 'Sequence':
            return sg_sequence.select_sequence_task2(self.sg_login, entity_id, task_fields=fields)

    def get_asset_task(self, entity_id, config=None):
        if config:
            _config = config

        field = _config['field']
        hide_field = _config['hide_field']
        fields = field + hide_field
        return sg_asset.select_asset_task2(self.sg_login, entity_id, task_fields=fields)

    def get_shot_task(self, entity_id, config=None):
        if config:
            _config = config

        field = _config['field']
        hide_field = _config['hide_field']
        fields = field + hide_field
        return sg_shot.select_shot_task2(self.sg_login, entity_id, task_fields=fields)

    def get_sequence_task(self, entity_id, config=None):
        if config:
            _config = config

        field = _config['field']
        hide_field = _config['hide_field']
        fields = field + hide_field
        return sg_sequence.select_sequence_task2(self.sg_login, entity_id, task_fields=fields)

    def get_task_version(self, task_id, config=None):
        if config:
            _config = config

        field = _config['field']
        hide_field = _config['hide_field']
        fields = field + hide_field
        return self.select_task_version(self.sg_login, task_id=task_id, version_fields=fields)

    def get_task_publish(self, task_id, config=None):
        if config:
            _config = config

        field = _config['field']
        hide_field = _config['hide_field']
        fields = field + hide_field
        return sg_task.select_task_publish(self.sg_login, task_id=task_id, publish_fields=fields)

    def get_task_timelog(self, task_id, config=None):
        if config:
            _config = config

        field = _config['field']
        hide_field = _config['hide_field']
        fields = field + hide_field
        entity_list = sg_task.select_task_timelog(self.sg_login, task_id=task_id, timelog_fields=fields)

        # 过滤用户
        entity_list_temp = []
        for entity in entity_list:
            if 'duration' in entity:
                entity['duration'] = str(entity['duration'] / 60.0) + ' hour'
            if 'user' in entity and entity['user']['id'] == self.user_id:
                entity_list_temp.append(entity)
        return entity_list_temp

    def create_task_timelog(self, task_id, description, duration, date):
        task_entity = sg_task.select_task_task(self.sg_login, task_id=task_id, task_fields=['project'])
        project_entity = task_entity['project']
        user_entity = self.user_entity
        return sg_task.create_task_timelog(self.sg_login, project_entity, user_entity, description, date, task_entity,
                                           duration)

    def delete_task_timelog(self, timelog_id):
        return sg_task.delete_task_timelog(self.sg_login, timelog_id)

    def get_dcc_type(self, task_template_name, task_name):
        filters = [
            ['task_template.TaskTemplate.code', 'contains', task_template_name],
            # ['task_template.TaskTemplate.code', 'is', task_template_name],
            ['content', 'is', task_name]
        ]
        fields = ['content', 'sg_software_dcc']
        return self.sg_login.find_one("Task", filters, fields)

    def get_dcc_type2(self, task_template_name, step_name):
        filters = [
            ['task_template.TaskTemplate.code', 'contains', task_template_name],
            ['step.Step.code', 'is', step_name]
        ]
        fields = ['content', 'sg_software_dcc']
        return self.sg_login.find_one("Task", filters, fields)

    def get_step_entity(self, step_name, link_entity_type):
        filters = [
            ['code', 'is', step_name],
            ['entity_type', 'is', link_entity_type]
        ]
        fields = ['code', 'entity_type']
        return self.sg_login.find_one("Step", filters, fields)

    def get_shot_frame(self, project_name, shot_name):
        filters = [
            ['project.Project.name', 'is', project_name],
            ['code', 'is', shot_name]
        ]
        fields = ['sg_text_1', 'description']
        return self.sg_login.find_one("Shot", filters, fields)

    def get_asset_entity(self, project_name, asset_name):
        '''
        read asset entity using project name
        :param project_name: Project name
        :param asset_name: Asset name which you want to get
        :return: Asset entity
        '''
        filters = [
            ['project.Project.name', 'is', project_name],
            ['code', 'is', asset_name]
        ]
        fields = ["id", "type", "code", "description", "sg_asset_type", "image", "sg_published_files", "tasks"]
        return self.sg_login.find_one("Asset", filters, fields)

    def get_published_file_src_path(self, project_name, published_file_id):
        '''
        get published file source path
        :param project_name: Project name
        :param published_file_id: Published file id
        :return: File source path
        '''
        filters = [
            ['project.Project.name', 'is', project_name],
            ['id', 'is', published_file_id]
        ]
        fields = ['code', 'sg_src_path', 'version']
        return self.sg_login.find_one("PublishedFile", filters, fields)

    def get_published_file_src_path2(self,task_id):
        '''
        get published file source path
        :param project_name: Project name
        :param asset_name: Asset name
        :param task_id: Task id
        :return: File source path
        '''
        filters = [
            ['task.Task.id', 'is', task_id],
        ]

        fields = ['code', 'published_file_type', 'version','path']
        return self.sg_login.find("PublishedFile", filters, fields)





    def get_task_status(self, project_name, task_id):
        filters = [
            ['project.Project.name', 'is', project_name],
            ['id', 'is', task_id]
        ]
        fields = ["content", "sg_status_list"]
        return self.sg_login.find_one("Task", filters, fields)

    def get_asset_subassets_list(self, project_name, asset_name):
        '''
        Get the asset list link below the sub_assets entity
        :param project_name: Project name
        :param asset_name: Asset name
        :return: SubAsset list
        '''
        filters = [
            ['project.Project.name', 'is', project_name],
            ['code', 'is', asset_name]
        ]
        fields = ['assets', 'sg_asset_type']
        return self.sg_login.find_one("Asset", filters, fields)

    def get_shot_assets_list(self, project_name, shot_name):
        '''
        Get the asset list link below the shot entity
        :param project_name: Project name
        :param shot_name: Shot name
        :return: Asset list
        '''
        filters = [
            ['shot.Shot.project.Project.name', 'is', project_name],
            ['shot.Shot.code', 'is', shot_name]
        ]
        fields = ['asset.Asset.sg_asset_type', 'asset.Asset.code', 'asset.Asset.id', 'asset.Asset.description',
                  'asset.Asset.image',
                  'asset.Asset.sg_published_files', 'asset.Asset.tasks']
        return self.sg_login.find("AssetShotConnection", filters, fields)

    def get_camera_assets_list(self,project_name,assetname):
        filters = [
            ['project.Project.name', 'is', project_name],
            ['code', 'is', assetname]
        ]

        fields = ['sg_asset_type', 'code', 'description', 'image',
                  'sg_published_files', 'tasks']
        return self.sg_login.find("Asset",filters,fields )
    def get_assets_list_form_type(self, project_name, asset_type):
        '''
        Get the asset list link below the shot entity
        :param project_name: Project name
        :param asset_type: asset type
        :return: Asset list
        '''
        filters = [
            ['project.Project.name', 'is', project_name],
            ['sg_asset_type', 'is', asset_type]
        ]
        fields = ['sg_asset_type', 'code', 'sg_chinesename', 'image',
                  'sg_published_files', 'tasks']
        return self.sg_login.find("Asset", filters, fields)

    def create_shot(self, project_entity, sequence_name, shot_name, frame):
        sequence_entity = sg_sequence.get_sequence_sequenceID(self.sg_login, project_entity['name'], sequence_name)
        if sequence_entity:
            sequence_entity = sequence_entity[0]

            shot_entity = sg_shot.get_shot_shotID(self.sg_login, project_entity['name'], shot_name, sequence_name)
            if shot_entity:
                # 如果镜头存在,则更新
                try:
                    if frame:
                        result = sg_base.update_entity(self.sg_login, "Shot", shot_entity[0]['id'],
                                                       {'sg_cut_duration': frame})
                        return True, result
                    else:
                        return True, shot_entity[0]
                except Exception as e:
                    return False, e.message
            else:
                data = {
                    "project": project_entity,
                    "sg_sequence": sequence_entity,
                    "code": shot_name,
                    'sg_cut_duration': frame,
                }
                try:
                    result = self.sg_login.create("Shot", data)
                    return True, result
                except Exception as e:
                    return False, e.message
        else:
            return False, 'Not Found The Sequence Entity: {}'.format(sequence_name)

    def create_shot_task(self, project_entity, shot_entity, task_name):
        task_list = sg_shot.select_shot_task2(self.sg_login, shot_entity["id"], task_fields=['content'])

        task_exist = False
        result = {}
        for task in task_list:
            if any([True for k, v in task.items() if re.search(task_name, str(v), re.IGNORECASE)]):
                task_exist = True
                result = task

        if task_exist:
            # 如果任务存在,则返回
            return True, result
        else:
            # 如果任务不存在,则创建该任务
            # 获取step entity
            step_str = task_name.split("_")[0]
            step_entity = self.get_step_entity(step_str, "Shot")
            data = {
                'project': project_entity,
                'content': task_name,
                'entity': shot_entity,
                'step': step_entity,
            }
            try:
                result = self.sg_login.create("Task", data)
                return True, result
            except Exception as e:
                return False, e.message

    def create_sequence(self, project_entity, episode_name, sequence_name):
        if episode_name:
            episode_entity = sg_episode.get_episode_episodeID(self.sg_login, project_entity['name'], episode_name)
            if episode_entity:
                episode_entity = episode_entity[0]
                sequence_entity = sg_sequence.get_sequence_sequenceID(self.sg_login, project_entity['name'],
                                                                      sequence_name, episode_name)

                if sequence_entity:
                    # 如果场次存在
                    return True, sequence_entity[0]
                else:
                    # 如果场次不存在，则创建场次
                    data = {
                        "project": project_entity,
                        "episode": episode_entity,
                        "code": sequence_name
                    }
                    try:
                        result = self.sg_login.create("Sequence", data)
                        return True, result
                    except Exception as e:
                        return False, e.message
            else:
                return False, 'Not Found The Episode Entity: {}'.format(sequence_name)

        else:
            sequence_entity = sg_sequence.get_sequence_sequenceID(self.sg_login, project_entity['name'],
                                                                  sequence_name)

            if sequence_entity:
                # 如果场次存在
                return True, sequence_entity[0]
            else:
                # 如果场次不存在，则创建场次
                data = {
                    "project": project_entity,
                    "code": sequence_name
                }
                try:
                    result = self.sg_login.create("Sequence", data)
                    return True, result
                except Exception as e:
                    return False, e.message

    def create_sequence_task(self, project_entity, sequence_entity, task_name):
        task_list = sg_sequence.select_sequence_task2(self.sg_login, sequence_entity["id"], task_fields=['content'])

        task_exist = False
        result = {}
        for task in task_list:
            if any([True for k, v in task.items() if re.search(task_name, str(v), re.IGNORECASE)]):
                task_exist = True
                result = task

        if task_exist:
            # 如果任务存在,则返回
            return True, result
        else:
            # 如果任务不存在,则创建该任务
            # 获取step entity
            step_str = task_name.split("_")[0]
            step_entity = self.get_step_entity(step_str, "Sequence")
            data = {
                'project': project_entity,
                'content': task_name,
                'entity': sequence_entity,
                'step': step_entity,
            }
            try:
                result = self.sg_login.create("Task", data)
                return True, result
            except Exception as e:
                return False, e.message

    def select_task_version(self, sg, task_id, version_fields=[]):
        filters = [
            ['sg_task.Task.id', 'is', task_id]
        ]

        return sg.find("Version", filters, version_fields)

    def get_notes(self, from_user_name=None, to_user_name=None, cc_user_name=None, script_id_not=None):
        if from_user_name:
            filters = [
                ['user.HumanUser.login', 'is', from_user_name]
            ]
        elif to_user_name:
            filters = [
                ['addressings_to.HumanUser.login', 'is', to_user_name]
            ]
        elif cc_user_name:
            filters = [
                ['addressings_cc.HumanUser.login', 'is', cc_user_name]
            ]

        if script_id_not:
            filters.append(['user.ApiUser.id', 'is_not', script_id_not])
        fields = ['content', 'user', 'subject', 'created_at', 'sg_client_read_status']
        return self.sg_login.find("Note", filters, fields, limit=50,
                                  order=[{'field_name': 'created_at', 'direction': 'desc'}])

    def set_notes_read(self, note_entity_list):
        batch_data = []
        for note_entity in note_entity_list:
            read_status = note_entity['sg_client_read_status']
            if not read_status or read_status == '':
                note_update_data = {'sg_client_read_status': 'read'}
                batch_data.append({"request_type": "update", "entity_type": "Note", "entity_id": note_entity['id'],
                                   "data": note_update_data})
        if batch_data:
            self.sg_login.batch(batch_data)

    def select_entity_fields(self, entity_type, entity_id, fields=[]):
        return sg_base.select_entity(self.sg_login, entity_type, entity_id, fields=fields)

    def down_entity_thumbnail(self, eitity_type, enity_id, imgpath):
        return sg_image.download_entity_thumbnail(self.sg_login, eitity_type, enity_id, imgpath)


if __name__ == '__main__':
    _handle=ShotgunClass()

    print(_handle.get_step_entity())
    _project_name='X3'
    _entity_name='PL001S'

    publishdata=_handle.get_published_file_src_path2(92608)
    _type=type=['Motion Builder FBX']
    _path=[]
    if publishdata:
        for i in range(len(publishdata)):
            publishtype=publishdata[i]['published_file_type']['name']
            print(publishtype)
            if publishtype in _type:
                print (publishdata[i]['path']['local_path_windows'])




