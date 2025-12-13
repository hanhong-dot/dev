# -*- coding: utf-8 -*-
# -----------------------------------
# @File    : ai_video_match_fun.py
# @Author  : linhuan
# @Time    : 2025/7/10 16:45
# @Description : 
# -----------------------------------
PROJECT_NAME = 'X3'
import apps.tools.common.ai_video_match_tool.ai_video_requests as ai_video_requests
import lib.common.md5 as common_md5

import os
from sg_login import Config


def find_squence_data_by_squence_name(sg, squence_name):
    filters = [['project.Project.name', 'is', PROJECT_NAME], ['code', 'is', squence_name]]
    fields = ['id', 'code']
    try:
        squence_data = sg.find_one('Sequence', filters, fields)
        return True, squence_data
    except Exception as e:
        return False, None


def find_shots_by_squence_id(sg, squence_id):
    filters = [['project.Project.name', 'is', PROJECT_NAME], ['sg_sequence.Sequence.id', 'is', squence_id]]
    fields = ['id', 'code']
    try:
        shots_data = sg.find('Shot', filters, fields)
        return True, shots_data
    except Exception as e:
        return False, None


def find_shot_laster_version_by_task_list(sg, shot_id, task_list):
    """
    查找shot的最新版本
    :param sg: Shotgun连接对象
    :param shot_id: Shot ID
    :param task_list: 任务列表
    :return: bool, list of versions
    """
    filters = [['project.Project.name', 'is', PROJECT_NAME], ['entity.Shot.id', 'is', shot_id]]
    fields = ['id', 'code', 'sg_task.Task.content', 'sg_path_to_frames', 'sg_ai_npz_path']

    versions = sg.find('Version', filters, fields)

    laster_version = None
    laster_id = 0
    if not versions:
        return False, None
    for __version in versions:
        __task_name = __version['sg_task.Task.content'] if 'sg_task.Task.content' in __version else None
        __version_id = __version['id'] if 'id' in __version else None
        if not __task_name or not __version_id:
            continue
        if __task_name in task_list and __version_id > laster_id:
            laster_version = __version
            laster_id = __version_id
    return True, laster_version


def find_shots_laster_version_data_by_squence_id(sg, squence_id, task_list):
    ok, shots = find_shots_by_squence_id(sg, squence_id)
    if not ok or not shots:
        return False, u'场次下没有Shot数据'
    __data = []
    for shot in shots:
        shot_id = shot['id']
        shot_name = shot['code']
        ok, laster_version = find_shot_laster_version_by_task_list(sg, shot_id, task_list)
        if not ok:
            continue
        if laster_version:
            __data.append({'shot_name': shot_name, 'shot_id': shot_id, 'laster_version': laster_version})
    if not __data:
        return False, u'没有找到符合条件的版本数据'
    return True, __data


def find_sequences_shots_laster_version_data(sg, squences, task_list):
    if not squences:
        return False, u'没有场次数据'
    if not task_list:
        return False, u'没有任务列表数据'
    __data = []
    for squence in squences:
        if not squence or 'id' not in squence or 'code' not in squence:
            return False, u'未在SG中找到场次数据,请检查输入的场次名称是否正确'
        squence_id = squence['id']
        sequence_code = squence['code']
        ok, shots_data = find_shots_laster_version_data_by_squence_id(sg, squence_id, task_list)
        if not ok:
            continue
        if shots_data:
            __data.append({'squence_code': sequence_code, 'squence_id': squence_id, 'shots_data': shots_data})
    if not __data:
        return False, u'没有找到符合条件的版本数据'
    return True, __data


def read_json_file(file_path):
    import json
    if not os.path.exists(file_path):
        return None
    with open(file_path, 'r') as f:
        data = json.load(f)
        f.close()
    return data


def sender_data_to_ai_video_lib(data, frame_out=10, log_handle=None):
    if not data:
        return False, u'没有数据需要发送'

    sender_versions = []
    video_lib_versions = []
    errors = []
    sg = Config().login()

    for __data in data:
        squence_code = __data['squence_code']
        squence_id = __data['squence_id']
        shots_data = __data['shots_data']
        for shot_data in shots_data:
            shot_name = shot_data['shot_name']
            shot_id = shot_data['shot_id']
            laster_version = shot_data['laster_version']
            npz_file = laster_version['sg_ai_npz_path']
            vesion_file = laster_version['sg_path_to_frames']
            if vesion_file  and os.path.exists(vesion_file) and (not npz_file or (npz_file and not npz_file.endswith('.npz') or not os.path.exists(npz_file))):
                sender_versions.append({'squence_name': squence_code, 'shot_name': shot_name, 'shot_id': shot_id,
                                        'version_file': vesion_file, 'id': laster_version['id'],
                                        'task_name': laster_version['sg_task.Task.content']})
            if vesion_file and os.path.exists(vesion_file) and npz_file and os.path.exists(npz_file) and npz_file.endswith('.npz'):
                video_lib_versions.append({'squence_name': squence_code, 'shot_name': shot_name, 'shot_id': shot_id,
                                           'version_file': vesion_file, 'npz_file': npz_file,
                                           'id': laster_version['id'],
                                           'task_name': laster_version['sg_task.Task.content']})

    if sender_versions:
        for __version in sender_versions:
            __current_time_id = get_current_time_id()
            squence_name = __version['squence_name']
            shot_name = __version['shot_name']
            shot_id = __version['shot_id']
            version_file = __version['version_file']
            task_id = '{}_{}'.format(shot_name, __current_time_id)
            out_path = get_out_path_zip()


            ok, result = ai_video_requests.get_ai_video_data(task_id, version_file, out_path, url="get_embeddings",frame_out=frame_out)
            if log_handle:
                log_handle.info('task_id: {}'.format(task_id))
                log_handle.info('version_file: {}'.format(version_file))
                log_handle.info('ok: {}'.format(ok))
                log_handle.info('result: {}'.format(result))

            if not ok:
                errors.append(u'发送数据失败: {}-{}-{}: {}'.format(squence_name, shot_name, shot_id, result))
                continue

            if not result:
                errors.append(u'没有返回数据: {}-{}-{}'.format(squence_name, shot_name, shot_id))
                continue
            __local_npz_file = result[0]

            __server_npz_file = get_server_video_lib_path(version_file)
            ok = copy_file(__local_npz_file, __server_npz_file)
            if not ok:
                errors.append(
                    u'复制Numpy文件失败: {}-{}-{}: {}'.format(squence_name, shot_name, shot_id, __local_npz_file))
                continue

            ok, rsult = updata_version_npy_file(sg, __version['id'], __server_npz_file)
            if not ok:
                errors.append(u'更新Numpy文件失败: {}-{}-{}: {}'.format(squence_name, shot_name, shot_id, rsult))
                continue

            video_lib_versions.append({
                'squence_name': squence_name,
                'shot_name': shot_name,
                'shot_id': shot_id,
                'version_file': version_file,
                'npz_file':__server_npz_file
            })
    # if log_handle:
    #     log_handle.info('sender_versions: {}'.format(sender_versions))
    #     log_handle.info('video_lib_versions: {}'.format(video_lib_versions))
    #     log_handle.info('errors: {}'.format(errors))

    return True, (video_lib_versions, errors)


def updata_version_npy_file(sg, version_id, npy_file):
    if not npy_file or not os.path.exists(npy_file):
        return False, u'Numpy文件路径不存在或无效: {}'.format(npy_file)

    if version_id is None:
        return False, u'version_id不能为空'

    data = {'sg_ai_npz_path': npy_file}
    try:
        sg.update('Version', version_id, data)
        return True, u'更新成功'
    except Exception as e:
        return False, u'更新失败: {}'.format(e)


def get_out_path_zip():
    local_path = get_local_video_lib_path()
    return '{}/output.zip'.format(local_path)


def sender_to_ai_video_npz(version_file, frame_out=10, log_handle=None):
    local_dir = get_local_video_lib_path()
    __long_video_path = '{}/local_video'.format(local_dir)
    if not os.path.exists(__long_video_path):
        os.makedirs(__long_video_path)
    __current_time_id = get_current_time_id()
    __dir, __file = os.path.split(version_file)
    __base_name, __ext = os.path.splitext(__file)
    __id = get_id_by_str(cover_ud(__base_name))
    __new_version_file = '{}/video_{}_{}{}'.format(__long_video_path, __id, __current_time_id, __ext)
    result = copy_file(version_file, __new_version_file)
    log_handle.info('version_file: {}'.format(version_file))
    log_handle.info('new_version_file: {}'.format(__new_version_file))
    if not result:
        log_handle.error('复制文件失败: {}'.format(version_file))
        return False, u'复制文件失败: {}'.format(version_file)
    task_id = 'video_{}_{}'.format(__id, __current_time_id)
    log_handle.info('task_id: {}'.format(task_id))
    out_path = get_out_path_zip()
    ok, result = ai_video_requests.get_ai_video_data(task_id, __new_version_file, out_path, url="get_embeddings",
                                                     frame_out=frame_out)

    if not ok:
        return False, u'发送数据失败: {}: {}'.format(__new_version_file, result)

    if not result:
        return False, u'没有返回数据: {}'.format(__new_version_file)
    npz_file = result[0]
    if log_handle:
        log_handle.info('task_id: {}'.format(task_id))
        # log_handle.info(u'version_file: {}'.format(version_file))
        # log_handle.info('new_version_file: {}'.format(__new_version_file))
        # log_handle.info('ok: {}'.format(ok))
        # log_handle.info('result: {}'.format(result))
        # log_handle.info('npy_file: {}'.format(npy_file))

    return True, {'video_file': __new_version_file, 'npz_file': npz_file, 'old_video_file': version_file}


def cover_ud(name):
    if isinstance(name, unicode):
        return name.encode("utf8", "ignore")
    return str(name)


def copy_file(source_file, dest_file):
    """
    Copies a file from source to destination.
    :param source_file: str, path to the source file
    :param dest_file: str, path to the destination file
    :return: bool, True if successful, False otherwise
    """
    import shutil
    from lib.common.md5 import Md5
    __dir, __file = os.path.split(dest_file)
    if not os.path.exists(__dir):
        os.makedirs(__dir)
    if dest_file and os.path.exists(dest_file):
        juduge = Md5().contrast_md5(source_file, dest_file)
        if juduge:
            return True
        else:
            try:
                os.remove(dest_file)
            except Exception as e:
                print("Error removing file {}: {}".format(dest_file, e))
                pass

    try:
        shutil.copy2(source_file, dest_file)
        return True
    except Exception as e:
        print("Error copying file from {} to {}: {}".format(source_file, dest_file, e))
        return False


# def com_version(long_video,shot_video,long_frame_range,shot_frame_range,fps=30):
#     import subprocess
#     ffmpeg_path="Z:\\dev\\tools\\ffmpeg\\bin\\ffmpeg.exe"
#     #生成拼合视频
#     if not long_video or not os.path.exists(long_video):
#         return False, u'长视频文件不存在: {}'.format(long_video)
#     if not shot_video or not os.path.exists(shot_video):
#         return False, u'短视频文件不存在: {}'.format(shot_video)
#     out_dir='{}/com_video'.format(get_local_video_lib_path())
#     if not os.path.exists(out_dir):
#         os.makedirs(out_dir)
#     shot_file=os.path.basename(shot_video)
#     out_file='{}/com_{}'.format(out_dir,shot_file)
#     cmds='"{}" -i "{}" -i "{}" -filter_complex "[0:v]trim=start_frame={}:end_frame={},setpts=PTS-STARTPTS[v0];[1:v]trim=start_frame={}:end_frame={},setpts=PTS-STARTPTS[v1];[v0][v1]concat=n=2:v=1:a=0[out]" -map "[out]" -r {} -y "{}"'.format(
#         ffmpeg_path.encode("gbk"),
#         long_video.encode("gbk"),
#         shot_video.encode("gbk"),
#         long_frame_range[0],long_frame_range[1],
#         shot_frame_range[0],shot_frame_range[1],
#         fps,
#         out_file.encode("gbk")
#     )
#     popen_info = subprocess.Popen(cmds, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
#     print(popen_info )
#     if popen_info:
#         return out_file
#     else:
#         return ''


def get_local_video_lib_path():
    import method.common.dir as common_dir
    local_path = common_dir.get_localtemppath("ai_video_lib")
    if not os.path.exists(local_path):
        os.makedirs(local_path)
    return local_path


def get_server_video_lib_path(version_file):
    if not version_file:
        return None
    version_file = version_file.replace('\\', '/')
    __dir, __file = os.path.split(version_file)

    __npz_dir = __dir.replace('/publish/', '/npz/')
    if not os.path.exists(__npz_dir):
        os.makedirs(__npz_dir)
    __npz_file = __file.replace('.mov', '.npz').replace('.mp4', '.npz')
    return '{}/{}'.format(__npz_dir, __npz_file)


def get_id_by_str(str_name):
    """
    获取字符串的MD5值作为ID
    :param str_name: str
    :return: str
    """
    if not str_name:
        return None
    return common_md5.Md5().get_md5(str_name)


def get_current_time_id():
    """
    获取当前时间戳
    :return: int
    """
    import time
    return int(time.time() * 1000)


def get_sender_to_ai_get_json(long_vide_npy, shot_npy_list, frame_out=30, fps=30, log_handle=None):
    task_id = '{}_{}'.format(get_base_name(long_vide_npy), get_current_time_id())
    json_file = '{}/match_{}.json'.format(get_local_video_lib_path(), task_id)
    ok, result = ai_video_requests.sender_ai_match_range_request(task_id, long_vide_npy, shot_npy_list,
                                                                 frame_out=frame_out, fps=fps)

    if log_handle:
        log_handle.info('task_id: {}'.format(task_id))
        log_handle.info('frame_out: {}'.format(frame_out))
    if not ok:
        return False, result
    ok = write_json_to_file(result, json_file, wtype="w")
    if not ok:
        return False, u'写入JSON文件失败: {}'.format(json_file)
    if log_handle:
        log_handle.info('json_file: {}'.format(json_file))
    return True, json_file


def get_base_name(__file):
    """
    获取文件的基本名称，不包含路径和扩展名
    :param __file: str, 文件路径
    :return: str, 基本名称
    """
    __dir, __file = os.path.split(__file)
    __base_name, __ext = os.path.splitext(__file)
    return __base_name


def get_ai_compute_similarity_request(long_npz_file, shot_video_npz_list,frame_out=10,fps=30, log_handle=None,url="segmentation"):
    task_id = 'segmentation_{}'.format(get_current_time_id())
    json_file = 'Z:/Data/ai_video_matc/jsons/match_{}.json'.format(task_id)

    ok, result = ai_video_requests.sender_com_video_request(task_id, long_npz_file,shot_video_npz_list,url=url,frame_out=frame_out,fps=fps)

    if log_handle:
        log_handle.info('task_id: {}'.format(task_id))
    if not ok:
        return False, result
    if result and 'result' in result:
        result = result['result']
        write_json_to_file(result, json_file, wtype="w")
        if log_handle:
            log_handle.info('json_file: {}'.format(json_file))
        return True, result
    else:
        return False, u'没有返回结果'


def write_json_to_file(data, file_path, wtype="w"):
    import json
    _path = os.path.dirname(file_path)
    if not os.path.exists(_path):
        os.makedirs(_path)
    with open(file_path, wtype) as f:
        json.dump(data, f, indent=4, separators=(',', ':'))
        f.close()
    return True


if __name__ == '__main__':
    from sg_login import Config

    sg = Config().login()
    # sequence=find_squence_data_by_squence_name(sg, 'AnimCard_YG_D0026')
    # print(sequence)
    squences = [{'code': 'AnimCard_YG_D0026', 'type': 'Sequence', 'id': 862}]
    task_list = ['cts_final', 'lgt_final', 'lut', 'sfx_final', 'hair_all']
    ok, data = find_sequences_shots_laster_version_data(sg, squences, task_list)
    npy_list = []
    # print(len(data))
    data = data[0]['shots_data']
    short_video_list = []
    for i in range(len(data)):
        laster_version = data[i]['laster_version']
        npy_file = laster_version['sg_ai_npz_path']
        short_video_path = laster_version['sg_path_to_frames']
        if npy_file and os.path.exists(npy_file):
            npy_list.append(npy_file)
        if short_video_path and os.path.exists(short_video_path):
            short_video_list.append(short_video_path)
    # print(short_video_list)
    print(npy_list)

    # long_video=u'D:/temp_info/ai_video_lib/local_video/【YS_D0026】250228 YS愿缘长.mp4'
    # shot_video="M:/projects/X3/publish/shots/CutScene/CutScene_YS_AnimCard_Act_Other_YS_D_0026_CC01_01/cts/cts_final/version/CutScene_YS_AnimCard_Act_Other_YS_D_0026_CC01_01.cts_final.v019.mp4"
    # long_frame_range=[66,95]
    # shot_frame_range=[38,67]

    # print(com_version(long_video, shot_video, long_frame_range, shot_frame_range, fps=30))

    # long_vide_npy=r'D:/temp_info/ai_video_lib/video_d2d7545086489eafb49583a80a659ff5_1752835994482.npy'
    # shot_npy_list=['M:/projects/X3/npy/shots/CutScene/CutScene_YS_AnimCard_Act_Other_YS_D_0026_CC03_01/lgt/lgt_final/version/CutScene_YS_AnimCard_Act_Other_YS_D_0026_CC03_01.lgt_final.v007.npy']
    # ok,result=get_sender_to_ai_get_json(long_vide_npy, shot_npy_list, frame_out=30)
    # print('ok:', ok)
    # print('result:', result)

    # from sg_login import Config

    # sg = Config().login()
    # sequences = ['AnimCard_YS_D0026']
    # sequence_list = []
    #
    # for __sequence in sequences:
    #
    #     ok, result = find_squence_data_by_squence_name(sg, __sequence)
    #     if ok:
    #         sequence_list.append(result)
    #
    # print('sequence_list:', sequence_list)
    # task_list = ['cts_final', 'lgt_final', 'lut', 'sfx_final', 'hair_all']
    #
    # ok, data = find_sequences_shots_laster_version_data(sg, sequence_list, task_list)
    # print('data:', data)
    #
    # ok, reslut = sender_data_to_ai_video_lib(data, frame_out=30)
    # print('reslut:', reslut)

    # squence_name = 'AnimCard_FY_D0002'
    # ok, squence_data = find_squence_data_by_squence_name(sg, squence_name)
    # squence_id = squence_data['id']
    # # print(find_shots_by_squence_id(sg, squence_id))
    # # shot_id = 10439
    # task_list = ['cts_final', 'lgt_final', 'lut', 'sfx_final', 'hair_all', 'check']
    # # print(find_shot_laster_version_by_task_list(sg, shot_id, task_list))
    #
    # print(find_shots_laster_version_data_by_squence_id(sg, squence_id, task_list))
