# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       : down_version_file
# Describe   : 下载version文件
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2023/9/8__16:52
# -------------------------------------------------------
import sys

sys.path.append('Z:/dev')


import database.shotgun.tools.actionitem.action_item_server as action_item_server


import os
import time

VERSIONDIR = r'\\10.10.201.151\share\development\version\x3_performance\playlist'
RUNAS = r'Z:/dev/tools/runas/runas_n.exe'

import method.common.dir as dircommon
import subprocess


class DownVersionFiles(object):
    def __init__(self):
        super(DownVersionFiles, self).__init__()
        self.project = sys.argv[1]
        self.select_ids = sys.argv[2].split(',')
        self.entity_type = sys.argv[3]



        self.sg = action_item_server.action_login()
        self.no_version_error = u'\n未下载成功,该版本没有上传文件,请检查版本文件'
        self.no_playlist_error = u'\n未下载成功,该版本没有关联playlist,请检查版本文件'
        self.bat_file = self.get_bat_file()
        self.runas = RUNAS
        if not self.select_ids:
            print u'未选择【{}】,请选择'.format(self.entity_type)
            return

    def down_version_files(self):
        versions = self.get_versions()
        self.apply_copy_version_files(versions)
        cmd = 'cmd.exe /C start "Folder" "%s"' % VERSIONDIR
        result = os.system(cmd)
        if versions and result == 0:
            for version in versions:
                if 'version_file' in version:
                    version_file = u'{}'.format(version['version_file'])
                    print version_file.replace('\\', '/').replace('//10.10.201.151/share/product', 'M:')
                if 'target_file' in version:
                    targe_file = u'{}'.format(version['target_file'])
                    print targe_file.replace('\\', '/').replace('//10.10.201.151/share/development', 'Z:')
        return versions

    def get_versions(self):
        versions = []
        if self.entity_type == 'Version':
            for version_id in self.select_ids:
                versions.extend(self.get_version_file_down(int(version_id)))
        elif self.entity_type == 'Playlist':
            for playlist_id in self.select_ids:
                version_ids = self.get_versins_from_playlist(int(playlist_id))
                playlist_name = self.get_playlist_name(int(playlist_id))
                if not version_ids:
                    print u'未找到playlist:{}关联的version,请检查'.format(playlist_id)
                    continue
                for version_id in version_ids:
                    versions.extend(self.get_version_file_down(version_id, playlist_name))
        return versions

    def get_playlist_name(self, playlist_id):
        playlist_name = ''
        playlist = self.sg.find_one('Playlist', [['id', 'is', playlist_id]], ['code'])
        if playlist and 'code' in playlist:
            playlist_name = playlist['code']
        return self.cover_ud(playlist_name)

    def get_versins_from_playlist(self, playlist_id):
        version_ids = []
        versions = self.sg.find('Playlist', [['id', 'is', playlist_id]], ['versions'])
        if versions and 'versions' in versions[0]:
            version_list = versions[0]['versions']
            if version_list:
                for version in version_list:
                    version_ids.append(version['id'])
        return version_ids

    def apply_copy_version_files(self, versions):
        if not versions:
            return
        self.write_bat(versions)
        _info, _error = self.run_bat()

        if _error:
            print u'下载失败,请检查'
            print _error
        if _info:
            print _info

        print u'下载成功,请检查 %s' % VERSIONDIR.replace(r'\\10.10.201.151\share\development', 'Z:\\dev')

    def run_bat(self):
        if not os.path.exists(self.bat_file):
            return
        cmd = '{} {}'.format(self.runas, self.bat_file)

        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        _info, _error = p.communicate()
        return _info, _error

    def write_bat(self, versions):
        import io
        if not versions:
            return
        version_infos = self.get_version_infos(versions)
        with io.open(self.bat_file, 'w', encoding="gb18030") as f:
            f.write(version_infos)
        return self.bat_file

    def get_version_infos(self, versions):
        if not versions:
            return

        playlist_dirs=self.get_playlist_dir_from_versions(versions)
        if playlist_dirs:
            playlist_infos= u'echo "-----------------------------------"plylist" delete is started-----------------------------------"'
            playlist_infos = playlist_infos + '\n'
            for playlist_dir in playlist_dirs:
                playlist_dir=self.cover_ud(playlist_dir)

                playlist_infos += u'if exist "{}" (del "{}" /f /s /q) \n'.format(playlist_dir,playlist_dir)
            playlist_infos =playlist_infos+ u'echo "-----------------------------------"plylist" delete is end-----------------------------------"'
            playlist_infos = playlist_infos + '\n'
            version_infos = playlist_infos+u'echo "-----------------------------------"version" files to fileSystem is started-----------------------------------"'

        else:
            version_infos = u'echo "-----------------------------------"version" files to fileSystem is started-----------------------------------"'
        version_infos = version_infos + '\n'
        for _version in versions:
            if _version and 'playlist_dir' in _version:
                playlist_dir= self.cover_ud(_version['playlist_dir'])
                version_infos += u'echo f | if exist "{}" (del "{}" /f /s /q) \n'.format( playlist_dir, playlist_dir)

            version_file = _version['version_file'].replace('/', '\\').replace('M:',
                                                                               r'\\10.10.201.151\share\product').replace(
                'm:', r'\\10.10.201.151\share\product')

            target_file = _version['target_file'].replace('/', '\\')
            if os.path.exists(version_file):
                version_infos += u'echo f | xcopy "{}" "{}" /h /y \n'.format(version_file, target_file)
        version_infos = version_infos + u'echo "-----------------------------------"version" files to fileSystem is end-----------------------------------"'
        return version_infos

    def get_playlist_dir_from_versions(self, versions):
        play_list_dirs = []
        if versions:
            for _version in versions:
                if _version and 'playlist_dir' in _version and _version['playlist_dir'] not in play_list_dirs:
                    play_list_dirs.append(_version['playlist_dir'])
        if play_list_dirs:
            return list(set(play_list_dirs))


    def get_version_file_down(self, version_id, playlist_name=None):
        version_file = self.get_version_file(version_id)
        version_name = self.get_version_name(version_id)
        __list = []
        if not version_file:
            print '{}:{}'.format(self.no_version_error, version_name)
            return
        if not playlist_name:
            playlists = self.get_playlist(version_id)
            if not playlists:
                print '{}:{}'.format(self.no_playlist_error, version_name)
                return
            for playlist in playlists:
                playlist_name = self.cover_ud(playlist['code'])

                target_file = u'{}/{}/{}'.format(VERSIONDIR, playlist_name, version_name)

                __list.append({'version_file': version_file, 'target_file': target_file})
        else:
            target_file = u'{}/{}/{}'.format(VERSIONDIR, playlist_name, version_name)
            targe_dir= u'{}'.format(os.path.dirname(target_file)).encode('gbk')
            __list.append({'version_file': version_file, 'target_file': target_file,'playlist_dir':targe_dir})

        # targe_dir = u'{}'.format(os.path.dirname(target_file)).encode('gbk')
        # if not os.path.exists(targe_dir):
        #     os.makedirs(targe_dir)

        return __list

    def get_bat_file(self):
        local_dir = dircommon.get_localtemppath('down_version')
        if not os.path.exists(local_dir):
            os.makedirs(local_dir)
        curent_time = time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime(time.time()))
        return '{}/down_version_{}.bat'.format(local_dir, curent_time)

    def cover_ud(self, name):
        # 转中文
        return str(name).decode("utf8", errors='ignore')

    def get_playlist(self, version_id):
        try:
            return self.sg.find('Playlist', [['versions', 'is', {'type': 'Version', 'id': version_id}]], ['code'])
        except:
            return None

    def get_version_name(self, version_id):
        try:
            return self.sg.find_one('Version', [['id', 'is', version_id]], ['code'])['code']
        except:
            return None

    def get_version_file(self, version_id):
        try:
            return self.sg.find_one('Version', [['id', 'is', version_id]], ['sg_path_to_frames'])['sg_path_to_frames']
        except:
            return None


if __name__ == '__main__':
    DownVersionFiles().down_version_files()
    # print sys.argv
    # DownVersionFiles().down_version_files()
    # DownVersionFiles().down_version_files()
    # print DownVersionFiles().get_versions()
    # sg = sg_analysis.Config().login()
    # project='X3'
    # entity_type='Playlist'
    # select_ids=['9463']
    # # # # print sg.find_one('Version', [['id', 'is', version_id]], ['sg_path_to_frames'])['sg_path_to_frames']
    # # #
    # handle=DownVersionFiles(project,select_ids,entity_type)
    # # # handle.get_versions()
    # handle.down_version_files()

    # cmd='D:/dev/tools/runas/runas_n.exe D:/temp_info/down_version/down_version_2023-09-09-15-18-17.bat'
    # print subprocess.call(cmd, shell=True)
    # sg = sg_analysis.Config().login()
    # # print time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime(time.time()))
    # playlist_id = 9418
    # print sg.find('Playlist', [['id', 'is', playlist_id]], ['versions'])[0]['versions']
