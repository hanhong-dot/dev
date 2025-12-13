# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       : update_playlist
# Describe   : 更新playlist
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2023/9/5__11:10
# -------------------------------------------------------
import sys

sys.path.append('Z:/dev')

import database.shotgun.tools.actionitem.action_item_server as action_item_server


class UpdatePlaylist(object):
    def __init__(self):
        self.project_name = sys.argv[1]
        self.select_ids = sys.argv[2].split(',')
        self.entity_type = sys.argv[3]
        # self.select_ids= version_ids
        # self.project_name = 'x3'
        # self.entity_type = 'Version'


        self.sg = action_item_server.action_login()
        self.select_error = u'\n未选择,请选择需要替换的版本'
        self.status_error = u'\n未替换成功,版本状态需要在apr或fin状态下才可以替换,请检查版本状态'
        self.link_error = u'\n未替换成功,版本需要关联到一个实体,请检查版本关联;\n或该version 已经关联到该playlist,请检查playlist关联'
        self.playlist_error = u'\n未替换成功,请检查该版本实体,playlist关联'
        self.playlists_error = u'\n未替换成功,{}项目没有任何一个添加reupload标签的playlist,请检查playlist'.format(self.project_name)
        self.user_error = u'\n未替换成功,请检查当前账号是否有权限操作playlist,\n或playlist是否存在,\n或同一镜头'
        self.more_error = u'\n未替换成功,请检查版本关联的镜头,有多个版本关联到同一个playlist,请检查以下playlist 和Shot'
        if not self.select_ids:
            print self.select_error
            return

    def apply_update_playlist(self):
        errors, updata_playlists = self.update_playlist()
        if errors:
            for _error in errors:
                for key, value in _error.items():
                    if key==self.more_error:
                        print u'{}:'.format(key)
                        for _value in value:
                            if _value:
                                print u'\nPlayList:【{}】'.format(_value[0].decode("utf8", errors='ignore'))
                                print u'\nShot:{}'.format(_value[1])
                    else:
                        print u'{}:{}'.format(key, value)
        if updata_playlists:
            for updata_playlist in updata_playlists:
                print u'\nversion【{}】替换成功\n请检查以下替换的playlist：'.format(updata_playlist[0])
                for playlist in updata_playlist[1]:
                    print u'【{}】'.format(playlist.decode("utf8", errors='ignore'))

    def update_playlist(self):
        playlist_versions = self.get_playlist_versions()
        playlist_errors = []
        updata_playlists = []
        status_errors = []
        errors = []
        more_errors = []


        if not playlist_versions:
            print self.playlists_error
            return

        for version_id in self.select_ids:
            version_id = int(version_id)
            version_code = u'{}'.format(self._get_version_code(version_id))
            if self._judge_version_status(version_id) == True:
                update_playlists, _errors = self.update_playlist_by_version(playlist_versions, version_id)

                if not update_playlists and not _errors:
                    playlist_errors.append(version_code)
                elif _errors:

                    more_errors.extend(_errors)
                elif update_playlists:
                    updata_playlists.append([version_code, update_playlists])
            else:
                status_errors.append(version_code)

        if status_errors:
            errors.append({self.status_error: status_errors})
        if playlist_errors:
            errors.append({self.playlist_error: playlist_errors})
        if more_errors:
            errors.append({self.more_error: more_errors})

        return [errors, updata_playlists]

    def _get_playlist_code(self, playlist_id):
        return self.sg.find_one('Playlist', [['id', 'is', playlist_id]], ['code'])['code']

    def update_playlist_by_version(self, playlist_versions, version_id):
        update_playlists = []
        error_playlists = []

        enity_id = self._get_version_link(version_id)['id']
        for playlist_version in playlist_versions:
            for playlist_id, versions in playlist_version.items():
                playlist_code = self._get_playlist_code(playlist_id)
                up_judge = False
                version_replaces = []
                version_link_entiy_name = ''
                for i in range(len(versions)):
                    version_link_entiy = self._get_version_link(versions[i]['id'])
                    if version_link_entiy:
                        version_link_entiy_id = version_link_entiy['id']
                        version_link_entiy_name = version_link_entiy['name']
                        if version_link_entiy_id == enity_id:
                            version_replaces.append(versions[i]['id'])
                            versions[i]['id'] = int(version_id)
                if len(version_replaces) > 1:
                    error_playlists.append([playlist_code,version_link_entiy_name])
                    continue
                if len(version_replaces) == 1:
                    up_judge = True
                if up_judge == True:
                    result = self.entity_update_playlist(playlist_id, versions)
                    if result and result == True:
                        playlist_code = self._get_playlist_code(playlist_id)
                        update_playlists.append(playlist_code)
        return update_playlists, error_playlists

    def entity_update_playlist(self, playlist_id, versions):
        try:
            self.sg.update('Playlist', playlist_id, {'versions': versions})
            return True
        except:
            print self.user_error
            return False

    def _judge_version_status(self, version_id):

        status = self._get_version_status(version_id)

        if status in ['apr', 'fin']:
            return True
        else:
            return False

    def _cover_code(self, _str):
        u"""
        转码(解决中文问题)
        :param _str:
        :return:
        """
        if _str and isinstance(_str, str) == True:
            # _str=(u'{}'.format(_str)).decode("utf8").encode('gbk')
            return _str.decode("utf8", errors='ignore')

    def _get_version_code(self, version_id):

        return self.sg.find_one('Version', [['id', 'is', version_id]], ['code'])['code']

    def _get_version_status(self, version_id):
        return self.sg.find('Version', [['id', 'is', version_id]], ['sg_status_list'])[0]['sg_status_list']

    def _get_version_link(self, version_id):
        return self.sg.find('Version', [['id', 'is', version_id]], ['entity'])[0]['entity']

    def get_playlist_versions(self):
        playlist_list = []
        playlists = self.sg.find('Playlist',
                                 [['project.Project.name', 'is', 'X3'], ['tags', 'name_contains', 'reupload']],
                                 ['versions'])

        for playlist in playlists:
            playlist_list.append({playlist['id']: playlist['versions']})
        return playlist_list


if __name__ == '__main__':
    # print(sys.argv)

    # version_ids=[110126]
    # UpdatePlaylist(version_ids).apply_update_playlist()
    UpdatePlaylist().apply_update_playlist()
    # print UpdatePlaylist()._get_version_status(version_id)
    # UpdatePlaylist([version_id]).apply_update_playlist()
    # sg=sg_analysis.Config().login()
    # print sg.find('Playlist', [['project.Project.name', 'is', 'X3'],['tags','name_contains','reupload']], ['tags'])

    # playlist_versions=UpdatePlaylist().get_playlist_versions()
    # for playlist_version in playlist_versions:
    #     for playlist_id,versions in playlist_version.items():
    #         for version in versions:
    #             print version['id']
    #             print UpdatePlaylist()._get_version_link(version)

    # sg = sg_analysis.Config().login()
    # playlists = sg.find('Playlist', [['project.Project.name', 'is', 'X3']], ['versions','tags'])
    # for playlist in playlists:
    #     if playlist['tags'] and playlist['tags'][0]['name']=='reupload':
    #         print playlist['id']
    #         print playlist['versions']
