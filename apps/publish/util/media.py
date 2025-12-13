# -*- coding: utf-8 -*-#
# Python       : python 2.7.16
# -------------------------------------------------------------------------------
# NAME         : version_media
# Describe     : 说明描述
# Version      : v0.01
# Author       : linhuan
# Email        : hanhong@papegames.net
# DateTime     : 2022/5/18__17:25
# -------------------------------------------------------------------------------
# -------------------------------------------------------------------------------
# example: 对提交version视频文件进行处理
# 
# -------------------------------------------------------------------------------


import apps.publish.util.analyze_xml as _get_data



class MediaProcess(object):
    def __init__(self,
                 task_data=None,
                 project_name='',
                 task_type='',
                 step='',
                 asset_type='',
                 task_engine='',
                 task_name='',
                 entity_name='',
                 sequence_name='',
                 entity_type=''):
        super(MediaProcess, self).__init__()

        if task_data:
            self.task_data = task_data
            self._project_name = self.task_data.project_name
            # self._project_type = self.task_data.project_type
            self._task_type = self.task_data.task_type
            self._step = self.task_data.step_name
            self._asset_type = self.task_data.asset_type
            self._task_engine = self.task_data.task_launch_soft
            self._task_name = self.task_data.task_name
            self._entity_name = self.task_data.entity_name
            self._sequence_name = self.task_data.sequence_name
            self._entity_type=self.task_data.entity_type
            # self._episode_name = self.task_data.episode_name
        else:
            self._project_name = project_name
            # self._project_type = project_type
            self._task_type = task_type
            self._step = step
            self._asset_type = asset_type
            self._task_engine = task_engine
            self._task_name = task_name
            self._entity_name = entity_name
            self._sequence_name = sequence_name
            self._entity_type=entity_type
            
            # self._episode_name = episode_name
        self._analyse_data = _get_data.GetXLMData(None,
                                                  self._project_name,
                                                  self._task_type,
                                                  self._step,
                                                  self._asset_type,
                                                  self._task_engine,
                                                  self._task_name,
                                                  self._entity_type)

    
    def check_media(self, path, **kwargs):
        '''
        调用解析文件对视频进行检测
        :param path: 媒体文件路径
        :return: True,False
        '''

        kwargs = {
            'project_name': self._project_name,
            'task_type': self._task_type,
            'step': self._step,
            'asset_type': self._asset_type,
            'dcc': self._task_engine,
            'task_name': self._task_name,
            'entity_name': self._entity_name,
            'sequence_name': self._sequence_name,
            # 'episode_name': self._episode_name
        }

        xml_message = self._analyse_data.get_meidadata()
        _result = {
            "status": True,
            "error_msg": ""
        }
        if xml_message:
            for checkitem in xml_message:
                _check_command = checkitem['check_command']
                if isinstance(_check_command, str):
                    _command = _check_command.split(';')[-1]
                    exec (_check_command[0:len(_check_command) - len(_command)])
                    if _command:
                        _result = eval(_command)

        return _result

    def process_media(self, path, **kwargs):
        '''
        调用解析文件对视频处理
        :param path:
        :param args:
        :return:
        '''
        kwargs = {
            'project_name': self._project_name,
            'task_type': self._task_type,
            'step': self._step,
            'asset_type': self._asset_type,
            'dcc': self._task_engine,
            'task_name': self._task_name,
            'entity_name': self._entity_name,
            'sequence_name': self._sequence_name,
            # 'episode_name': self._episode_name
        }

        xml_message = self._analyse_data.get_meidadata()
        if xml_message:
            for checkitem in xml_message:
                _check_command = checkitem['process_command']
                if isinstance(_check_command, str):
                    _command = _check_command.split(';')[-1]
                    exec (_check_command[0:len(_check_command) - len(_command)])
                    if _command:
                        _result = eval(_command)

# if __name__ == '__main__':
#     # import method.shotgun.get_task as get_task
#
#     _handle= _get_data.GetXLMData(None,
#                          'X3_test04',
#                          'Task',
#                          'mod',
#                          'prp',
#                          'maya',
#                          'drama_mdl',
#                          'Asset')
#     print _handle.get_meidadata()

    # media_handle = MediaProcess(get_task.TaskInfo('ST001S.drama_mdl.v001.ma', 'X3_test04', 'maya', 'publish'))
    # print media_handle._analyse_data.get_meidadata()