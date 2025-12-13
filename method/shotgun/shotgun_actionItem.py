# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       : shotgun_actionItem
# Describe   : 说明描述
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2022/5/27__20:48
# -------------------------------------------------------
import sys
import os
import yaml

sys.path.append('Z:/dev')
import database.shotgun.core.root_path as root_path
import database.shotgun.core.sg_event_field as sg_event_field
import database.shotgun.core.sg_analysis as sg_analysis

CONFIG_FILE = "shotgun-menuAction-config.yml"


class ShotgunMenuAction:
    def __init__(self, getdata=[]):
        self.get_data = getdata
        self.init_dict = {}
        self.data_dict = {}
        self.mid_path = 'database\\shotgun\\conf\\core\\'
        self.config_path = root_path.RoothPath().roothpath() + self.mid_path + CONFIG_FILE

    def init_getData(self):
        '''
        返回key:自定义url
            value:event_log_entry_id
        :return:字典
        '''
        custom_url = ''
        envent_id = ''
        if len(self.get_data) >= 2:
            url = self.get_data[1]
            if url:
                if '?' in url and '=' in url:
                    custom_url = url.split('?')[0][0:-1]
                    envent_id = url.split('?')[-1].split('=')[-1]
        else:
            return

        if custom_url and envent_id:
            self.init_dict = {'url': custom_url, 'eventID': envent_id}

        return self.init_dict

    def _get_selectedData(self):
        '''
        key:选择的实体类型和选择的id
        :return: 字典
        '''

        data = self.init_getData()
        # import pprint
        # pprint.pprint(data)
        id = ''
        metaData = []
        entity_type = ''
        selected_ids = ''
        project_name = ''
        column_display_names = ''
        column_ids = ''
        cols = ''
        url=''
        if data:
            id = int(data['eventID'])
            url = data['url']

        if id:
            sg_event = sg_event_field.ShotgunEventFind()
            metaData = sg_event.get_Meta_Data(id)

        if metaData:
            entity_type = metaData[0]['meta']['ami_payload']['entity_type']
            selected_ids = metaData[0]['meta']['ami_payload']['selected_ids']
            column_display_names = metaData[0]['meta']['ami_payload']['column_display_names']
            column_ids = metaData[0]['meta']['ami_payload']['ids']
            cols = metaData[0]['meta']['ami_payload']['cols']
            try:
                project_name = metaData[0]['meta']['ami_payload']['project_name']
            except:
                selected_id = selected_ids.split(',')[0]
                sg_instace = sg_analysis.Config().login()
                filter_data = [['id', 'is', int(selected_id)]]
                query_info = sg_instace.find_one(entity_type, filter_data, ['project.Project.name'])
                project_name = query_info['project.Project.name']

        if entity_type and selected_ids and url:
            self.data_dict = {'entity_type': entity_type, 'selected_ids': selected_ids, 'url': url,
                              'project_name': project_name, 'column_display': column_display_names,
                              'column_ids': column_ids, 'cols': cols}
        else:
            return
        return self.data_dict

    def _analysis(self):
        with open(self.config_path) as f:
            config_dict = yaml.load(f, Loader=yaml.FullLoader)
        return config_dict

    def Run_Action(self):
        config = self._analysis()
        dict_Data = self._get_selectedData()

        project = dict_Data['project_name']
        select_ids = dict_Data['selected_ids']
        column_display_names = self._list_cover_str(dict_Data['column_display'])



        entity_type = dict_Data['entity_type']
        column_ids = dict_Data['column_ids']
        cols = self._list_cover_str(dict_Data['cols'])

        if dict_Data:
            import subprocess
            python_file = config[dict_Data['url']]

            cmd = 'C:/2.7.18-x64/python.exe %s %s %s %s "%s" %s %s' % (
                python_file, project, select_ids, entity_type, column_display_names, column_ids, cols)
            subprocess.Popen(cmd)

    def _list_cover_str(self, _list):
        u"""
        list 列表转为string
        :param _list:
        :return:
        """
        if _list:
            d = ''
            for i in range(len(_list)):
                if i == 0:
                    d = '{}'.format(_list[0])
                else:
                    d = '{},{}'.format(d, _list[i])
            # if ' ' in d:
            #     d=d.replace(' ',';')
            return d


if __name__ == '__main__':
    # tt = ShotgunMenuAction(sys.argv)
    # tt.Run_Action()
    # import pprint
    # pprint.pprint(sys.argv[1])
    tt = ShotgunMenuAction(sys.argv)
    tt.Run_Action()
    os.system("pause")
