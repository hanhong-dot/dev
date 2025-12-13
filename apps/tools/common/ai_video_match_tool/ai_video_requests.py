# -*- coding: utf-8 -*-#
# -------------------------------------------------------
# NAME       :
# Describe   : 说明描述
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2025/7/3
# -------------------------------------------------------
import requests
import os
import time
import zipfile
import stat

# SERVERURL = "http://10.10.188.149:5000"
# SERVERURL = "http://10.10.207.210:5000"
# SERVERURL = "http://10.10.188.133:5000"
SERVERURL = "https://x3-dino-video-match.diezhi.net"


def get_ai_video_data(task_id, video_path, out_path, url="get_embeddings", frame_out=10):
    url = '{}/{}'.format(SERVERURL, url)
    data = {
        "task_id": task_id,
        "frame_out": frame_out
    }
    files = {
        ("videos", open(video_path, "rb")),
    }
    files = set(files)
    response = requests.post(url, files=files, data=data)
    content_type = response.headers.get("Content-Type", "")
    if "application/json" in content_type:
        data = response.json()
        print(data)
        return False, u'AI服务器堵塞，请联系@水月@林欢'

    elif "application/zip" in content_type:
        with open(out_path, "wb") as f:
            f.write(response.content)
        return True, get_zip_data(out_path)
    else:
        return False, response.text


def sender_com_video_request(task_id, long_video_npz_file, shot_video_npz_list, url="segmentation", frame_out=10,
                             fps=30):
    # print('start_time:', time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
    url = '{}/{}'.format(SERVERURL, url)
    files = {
        ("long", open(u'{}'.format(long_video_npz_file), "rb")),
    }
    files = set(files)
    if not shot_video_npz_list:
        return False, "No shot video npz files provided."
    for shot_video_npy in shot_video_npz_list:
        files.add(("embeddings", open(u'{}'.format(shot_video_npy), "rb")))
    data = {
        "task_id": task_id,
        "frame_out": frame_out,
        "fps": fps
    }
    response = requests.post(url, files=files, data=data)
    content_type = response.headers.get("Content-Type", "")
    # print('end_time:', time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
    if "application/json" in content_type:
        data = response.json()
        return True, data


def sender_com_video(task_id, long_video, shot_video_list, json_file, output, url="extract_video"):
    url = '{}/{}'.format(SERVERURL, url)
    files = {
        ("long", open(long_video, "rb")),
    }
    files = set(files)

    files = {
        ("long_video", open(u'{}'.format(long_video), "rb")),
        ("json_file", open(u'{}'.format(json_file), "rb"))

    }
    files = set(files)
    if not shot_video_list:
        return False, "No shot video files provided."
    for shot_video in shot_video_list:
        files.add(("short_videos", open(u'{}'.format(shot_video), "rb")))
    data = {
        "task_id": task_id,
        "video_type": "long"

    }
    response = requests.post(url, files=files, data=data)
    content_type = response.headers.get("Content-Type", "")
    print(content_type)
    if "application/json" in content_type:
        data = response.json()
        return True, data
    elif "application/zip" in content_type:
        with open(output, "wb") as f:
            f.write(response.content)
        return True, get_zip_data(output)
    elif "video/mp4" in content_type:
        with open(output, "wb") as f:
            f.write(response.content)
        return True, output


def get_zip_data(zip_path):
    if not os.path.exists(zip_path):
        return None

    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(os.path.dirname(zip_path))
    extracted_files = zip_ref.namelist()
    data = []
    for file_name in extracted_files:
        if file_name.endswith('.json'):
            with open(os.path.join(os.path.dirname(zip_path), file_name), 'r', encoding='utf-8') as f:
                data.append(f.read())
        elif file_name.endswith('.mp4'):
            data.append(os.path.join(os.path.dirname(zip_path), file_name))
        elif file_name.endswith('.npz'):
            data.append(os.path.join(os.path.dirname(zip_path), file_name))
    if os.path.exists(zip_path):
        os.remove(zip_path)
    return data


def sender_ai_compute_similarity_request(task_id, video_segment_json, long_video, shot_video_list, frame_out=30,
                                         log_handle=None,
                                         url="compute_similarity", out_path=None):
    url = '{}/{}'.format(SERVERURL, url)

    files = {
        ("json_file", open(u'{}'.format(video_segment_json), "rb")),
        ("long_video", open(u'{}'.format(long_video), "rb"))
    }
    files = set(files)
    if not shot_video_list:
        return False, "No shot video files provided."
    for shot_video in shot_video_list:
        files.add(("short_videos", open(u'{}'.format(shot_video), "rb")))

    data = {
        "task_id": task_id,
        "frame_out": frame_out
    }
    response = requests.post(url, files=files, data=data)
    content_type = response.headers.get("Content-Type", "")
    if log_handle:
        log_handle.info('task_id: {}, url: {}, data: {}'.format(task_id, url, data))
        log_handle.info('Response Status Code: {}'.format(response.status_code))

    if "application/json" in content_type:
        data = response.json()
        return True, data
    elif "application/zip" in content_type:
        with open(out_path, "wb") as f:
            f.write(response.content)
        return True, get_zip_data(out_path)
    else:
        return False, response.text


def creat_match_range_json(json_file, task_id, long_vide_npy, short_video_npy_list,
                           url="segmentation", frame_out=30, fps=30):
    url = '{}/{}'.format(SERVERURL, url)
    ok, result = sender_ai_match_range_request(task_id, long_vide_npy, short_video_npy_list, url, frame_out=frame_out,
                                               fps=fps)
    if not ok:
        return False, result
    if isinstance(result, dict):
        data = result
        write_json_to_file(data, json_file)
        return True, json_file
    return False, result


def sender_ai_match_range_request(task_id, long_vide_npy, short_video_npy_list, out_path=None,
                                  url="segmentation", frame_out=30, fps=30):
    url = '{}/{}'.format(SERVERURL, url)

    files = {
        ("long", open(u'{}'.format(long_vide_npy), "rb"))}
    files = set(files)
    if not short_video_npy_list:
        return False, "No short video npy files provided."
    for short_video_npy in short_video_npy_list:
        files.add(("embeddings", open(u'{}'.format(short_video_npy), "rb")))
    data = {
        "task_id": task_id,
        "frame_out": frame_out,
        "fps": fps
    }
    response = requests.post(url, files=files, data=data)
    print(response.json())
    content_type = response.headers.get("Content-Type", "")
    if "application/json" in content_type:
        data = response.json()
        return True, data
    elif "application/zip" in content_type:
        with open(out_path, "wb") as f:
            f.write(response.content)
        return True, get_zip_data(out_path)
    else:
        return False, response.text


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
    # long_video = r'F:\AITest\YS_D0026.mp4'
    shot_video_list = [
        'M:/projects/X3/publish/shots/CutScene/CutScene_YG_AnimCard_Act_Other_YG_D_0026_CC01_01/lgt/lgt_final/version/CutScene_YG_AnimCard_Act_Other_YG_D_0026_CC01_01.lgt_final.v002.mp4',
        'M:/projects/X3/publish/shots/CutScene/CutScene_YG_AnimCard_Act_Other_YG_D_0026_CC01A_01/lgt/lgt_final/version/CutScene_YG_AnimCard_Act_Other_YG_D_0026_CC01A_01.lgt_final.v002.mp4',
        'M:/projects/X3/publish/shots/CutScene/CutScene_YG_AnimCard_Act_Other_YG_D_0026_CC01B_01/lgt/lgt_final/version/CutScene_YG_AnimCard_Act_Other_YG_D_0026_CC01B_01.lgt_final.v002.mp4',
        'M:/projects/X3/publish/shots/CutScene/CutScene_YG_AnimCard_Act_Other_YG_D_0026_CC02_01/lgt/lgt_final/version/CutScene_YG_AnimCard_Act_Other_YG_D_0026_CC02_01.lgt_final.v002.mp4',
        'M:/projects/X3/publish/shots/CutScene/CutScene_YG_AnimCard_Act_Other_YG_D_0026_CC02A_01/lgt/lgt_final/version/CutScene_YG_AnimCard_Act_Other_YG_D_0026_CC02A_01.lgt_final.v002.mp4',
        'M:/projects/X3/publish/shots/CutScene/CutScene_YG_AnimCard_Act_Other_YG_D_0026_CC02A_02/lgt/lgt_final/version/CutScene_YG_AnimCard_Act_Other_YG_D_0026_CC02A_02.lgt_final.v002.mp4',
        'M:/projects/X3/publish/shots/CutScene/CutScene_YG_AnimCard_Act_Other_YG_D_0026_CC02A_03/lgt/lgt_final/version/CutScene_YG_AnimCard_Act_Other_YG_D_0026_CC02A_03.lgt_final.v002.mp4',
        'M:/projects/X3/publish/shots/CutScene/CutScene_YG_AnimCard_Act_Other_YG_D_0026_CC02A_04/lgt/lgt_final/version/CutScene_YG_AnimCard_Act_Other_YG_D_0026_CC02A_04.lgt_final.v002.mp4',
        'M:/projects/X3/publish/shots/CutScene/CutScene_YG_AnimCard_Act_Other_YG_D_0026_CC02A_05/lgt/lgt_final/version/CutScene_YG_AnimCard_Act_Other_YG_D_0026_CC02A_05.lgt_final.v002.mp4',
        'M:/projects/X3/publish/shots/CutScene/CutScene_YG_AnimCard_Act_Other_YG_D_0026_CC02B_01/lgt/lgt_final/version/CutScene_YG_AnimCard_Act_Other_YG_D_0026_CC02B_01.lgt_final.v002.mp4',
        'M:/projects/X3/publish/shots/CutScene/CutScene_YG_AnimCard_Act_Other_YG_D_0026_CC02B_02/lgt/lgt_final/version/CutScene_YG_AnimCard_Act_Other_YG_D_0026_CC02B_02.lgt_final.v002.mp4',
        'M:/projects/X3/publish/shots/CutScene/CutScene_YG_AnimCard_Act_Other_YG_D_0026_EndingA_01/lgt/lgt_final/version/CutScene_YG_AnimCard_Act_Other_YG_D_0026_EndingA_01.lgt_final.v002.mp4',
        'M:/projects/X3/publish/shots/CutScene/CutScene_YG_AnimCard_Act_Other_YG_D_0026_EndingB_01/lgt/lgt_final/version/CutScene_YG_AnimCard_Act_Other_YG_D_0026_EndingB_01.lgt_final.v002.mp4',
        'M:/projects/X3/publish/shots/CutScene/CutScene_YG_AnimCard_Loop_Idle_YG_D_0026_01/lgt/lgt_final/version/CutScene_YG_AnimCard_Loop_Idle_YG_D_0026_01.lgt_final.v002.mp4',
        'M:/projects/X3/publish/shots/CutScene/CutScene_YG_AnimCard_Loop_Idle_YG_D_0026_02/lgt/lgt_final/version/CutScene_YG_AnimCard_Loop_Idle_YG_D_0026_02.lgt_final.v002.mp4',
        'M:/projects/X3/publish/shots/CutScene/CutScene_YG_AnimCard_Act_Other_YG_D_0026_CC01_01/cts/version/CutScene_YG_AnimCard_Act_Other_YG_D_0026_CC01_01.cts_final.v025.mp4',
        'M:/projects/X3/publish/shots/CutScene/CutScene_YG_AnimCard_Act_Other_YG_D_0026_CC02_01/cts/cts_final/version/CutScene_YG_AnimCard_Act_Other_YG_D_0026_CC02_01.cts_final.v023.mp4',
        'M:/projects/X3/publish/shots/CutScene/CutScene_YG_AnimCard_Act_Other_YG_D_0026_CC02A_01/cts/version/CutScene_YG_AnimCard_Act_Other_YG_D_0026_CC02A_01.cts_final.v017.mp4',
        'M:/projects/X3/publish/shots/CutScene/CutScene_YG_AnimCard_Act_Other_YG_D_0026_CC02B_01/cts/version/CutScene_YG_AnimCard_Act_Other_YG_D_0026_CC02B_01.cts_final.v019.mp4',
        'M:/projects/X3/publish/shots/CutScene/CutScene_YG_AnimCard_Act_Other_YG_D_0026_CC03_01/cts/cts_final/version/CutScene_YG_AnimCard_Act_Other_YG_D_0026_CC03_01.cts_final.v023.mp4',
        'M:/projects/X3/publish/shots/CutScene/CutScene_YG_AnimCard_Act_Other_YG_D_0026_CC03A_01/cts/version/CutScene_YG_AnimCard_Act_Other_YG_D_0026_CC03A_01.cts_final.v017.mp4',
        'M:/projects/X3/publish/shots/CutScene/CutScene_YG_AnimCard_Act_Other_YG_D_0026_CC03B_01/cts/cts_final/version/CutScene_YG_AnimCard_Act_Other_YG_D_0026_CC03B_01.cts_final.v018.mp4',
        'M:/projects/X3/publish/shots/CutScene/CutScene_YG_AnimCard_Act_Other_YG_D_0026_CC04_01/cts/cts_final/version/CutScene_YG_AnimCard_Act_Other_YG_D_0026_CC04_01.cts_final.v024.mp4',
        'M:/projects/X3/publish/shots/CutScene/CutScene_YG_AnimCard_Act_Other_YG_D_0026_CC05_01/cts/cts_final/version/CutScene_YG_AnimCard_Act_Other_YG_D_0026_CC05_01.cts_final.v023.mp4']
    _file = r'M:\projects\x3\publish\shots\CutScene\CutScene_YG_AnimCard_Act_Other_YG_D_0026_CC01_01\lgt\lgt_final\version\CutScene_YG_AnimCard_Act_Other_YG_D_0026_CC01_01.lgt_final.v002.mp4'

    _shot_file = 'M:/projects/X3/publish/shots/CutScene/CutScene_YG_AnimCard_Act_Other_YG_D_0026_CC01_01/lgt/lgt_final/version/CutScene_YG_AnimCard_Act_Other_YG_D_0026_CC01_01.lgt_final.v002.mp4'
    task_id = 'test_task_001_sender_2025_01208_05'
    # long_video_npy = get_ai_video_data(task_id,_shot_file, r'E:\aitest\output.zip', frame_out=30)

    # sender_com_video_request()
    # task_id='test_task_20251205'
    # shot_video_npz=r'E:\aitest\CutScene_YG_AnimCard_Act_Other_YG_D_0026_CC01_01.lgt_final.v002.npz'
    # long_video=r'Z:\test-AI\YGD0026_PV.mp4'
    # output=r'E:\aitest\output_sender_com_video_request.zip'
    # print(os.path.exists(_shot_file))
    # long_video_npz = get_ai_video_data(task_id, long_video, r'E:\aitest\output.zip', frame_out=10)
    # print(long_video_npz)
    # long_video_npz_file='E:\\aitest\\YGD0026_PV.npz'
    # shot_video_npz_list=['E:\\aitest\\CutScene_YG_AnimCard_Act_Other_YG_D_0026_CC01_01.lgt_final.v002.npz']
    #
    # ok,result=sender_com_video_request(task_id, long_video_npz_file, shot_video_npz_list, url="segmentation", frame_out=10,
    #                          fps=30)
    # print(ok,result)
    # long_video_npz=r'E:\aitest\YGD0026_PV.npz'
    #
    #
    # print(sender_com_video_request(task_id,long_video_npz,[shot_video_npz],url="segmentation",frame_out=10,fps=30))
    # print(long_video_npy)
    # task_id='test_task_002_sender'
    # shot_npy_list=[]
    # for shot_video in shot_video_list:
    #     ok,result=get_ai_video_data(task_id, shot_video, r'F:\AITest\test\output.zip', frame_out=30)
    #     if ok:
    #         shot_npy_list.append(result[0])
    # long_vide_npy=r'F:\AITest\test\CutScene_YG_AnimCard_Act_Other_YG_D_0026_CC01_01.lgt_final.v002.npy'
    # shot_npy_list=['M:/projects/X3/npy/shots/CutScene/CutScene_YG_AnimCard_Act_Other_YG_D_0026_CC01_01/lgt/lgt_final/version/CutScene_YG_AnimCard_Act_Other_YG_D_0026_CC01_01.lgt_final.v002.npy', 'M:/projects/X3/npy/shots/CutScene/CutScene_YG_AnimCard_Act_Other_YG_D_0026_CC01A_01/lgt/lgt_final/version/CutScene_YG_AnimCard_Act_Other_YG_D_0026_CC01A_01.lgt_final.v002.npy', 'M:/projects/X3/npy/shots/CutScene/CutScene_YG_AnimCard_Act_Other_YG_D_0026_CC01B_01/lgt/lgt_final/version/CutScene_YG_AnimCard_Act_Other_YG_D_0026_CC01B_01.lgt_final.v002.npy', 'M:/projects/X3/npy/shots/CutScene/CutScene_YG_AnimCard_Act_Other_YG_D_0026_CC02_01/lgt/lgt_final/version/CutScene_YG_AnimCard_Act_Other_YG_D_0026_CC02_01.lgt_final.v002.npy', 'M:/projects/X3/npy/shots/CutScene/CutScene_YG_AnimCard_Act_Other_YG_D_0026_CC02A_01/lgt/lgt_final/version/CutScene_YG_AnimCard_Act_Other_YG_D_0026_CC02A_01.lgt_final.v002.npy', 'M:/projects/X3/npy/shots/CutScene/CutScene_YG_AnimCard_Act_Other_YG_D_0026_CC02A_02/lgt/lgt_final/version/CutScene_YG_AnimCard_Act_Other_YG_D_0026_CC02A_02.lgt_final.v002.npy', 'M:/projects/X3/npy/shots/CutScene/CutScene_YG_AnimCard_Act_Other_YG_D_0026_CC02A_03/lgt/lgt_final/version/CutScene_YG_AnimCard_Act_Other_YG_D_0026_CC02A_03.lgt_final.v002.npy', 'M:/projects/X3/npy/shots/CutScene/CutScene_YG_AnimCard_Act_Other_YG_D_0026_CC02A_04/lgt/lgt_final/version/CutScene_YG_AnimCard_Act_Other_YG_D_0026_CC02A_04.lgt_final.v002.npy', 'M:/projects/X3/npy/shots/CutScene/CutScene_YG_AnimCard_Act_Other_YG_D_0026_CC02A_05/lgt/lgt_final/version/CutScene_YG_AnimCard_Act_Other_YG_D_0026_CC02A_05.lgt_final.v002.npy', 'M:/projects/X3/npy/shots/CutScene/CutScene_YG_AnimCard_Act_Other_YG_D_0026_CC02B_01/lgt/lgt_final/version/CutScene_YG_AnimCard_Act_Other_YG_D_0026_CC02B_01.lgt_final.v002.npy', 'M:/projects/X3/npy/shots/CutScene/CutScene_YG_AnimCard_Act_Other_YG_D_0026_CC02B_02/lgt/lgt_final/version/CutScene_YG_AnimCard_Act_Other_YG_D_0026_CC02B_02.lgt_final.v002.npy', 'M:/projects/X3/npy/shots/CutScene/CutScene_YG_AnimCard_Act_Other_YG_D_0026_EndingA_01/lgt/lgt_final/version/CutScene_YG_AnimCard_Act_Other_YG_D_0026_EndingA_01.lgt_final.v002.npy', 'M:/projects/X3/npy/shots/CutScene/CutScene_YG_AnimCard_Act_Other_YG_D_0026_EndingB_01/lgt/lgt_final/version/CutScene_YG_AnimCard_Act_Other_YG_D_0026_EndingB_01.lgt_final.v002.npy', 'M:/projects/X3/npy/shots/CutScene/CutScene_YG_AnimCard_Loop_Idle_YG_D_0026_01/lgt/lgt_final/version/CutScene_YG_AnimCard_Loop_Idle_YG_D_0026_01.lgt_final.v002.npy', 'M:/projects/X3/npy/shots/CutScene/CutScene_YG_AnimCard_Loop_Idle_YG_D_0026_02/lgt/lgt_final/version/CutScene_YG_AnimCard_Loop_Idle_YG_D_0026_02.lgt_final.v002.npy', 'M:/projects/X3/npy/shots/CutScene/CutScene_YG_AnimCard_Act_Other_YG_D_0026_CC02_01/cts/cts_final/version/CutScene_YG_AnimCard_Act_Other_YG_D_0026_CC02_01.cts_final.v023.npy', 'M:/projects/X3/npy/shots/CutScene/CutScene_YG_AnimCard_Act_Other_YG_D_0026_CC02A_01/cts/version/CutScene_YG_AnimCard_Act_Other_YG_D_0026_CC02A_01.cts_final.v017.npy', 'M:/projects/X3/npy/shots/CutScene/CutScene_YG_AnimCard_Act_Other_YG_D_0026_CC02B_01/cts/version/CutScene_YG_AnimCard_Act_Other_YG_D_0026_CC02B_01.cts_final.v019.npy', 'M:/projects/X3/npy/shots/CutScene/CutScene_YG_AnimCard_Act_Other_YG_D_0026_CC03_01/cts/cts_final/version/CutScene_YG_AnimCard_Act_Other_YG_D_0026_CC03_01.cts_final.v023.npy', 'M:/projects/X3/npy/shots/CutScene/CutScene_YG_AnimCard_Act_Other_YG_D_0026_CC03A_01/cts/version/CutScene_YG_AnimCard_Act_Other_YG_D_0026_CC03A_01.cts_final.v017.npy', 'M:/projects/X3/npy/shots/CutScene/CutScene_YG_AnimCard_Act_Other_YG_D_0026_CC03B_01/cts/cts_final/version/CutScene_YG_AnimCard_Act_Other_YG_D_0026_CC03B_01.cts_final.v018.npy', 'M:/projects/X3/npy/shots/CutScene/CutScene_YG_AnimCard_Act_Other_YG_D_0026_CC04_01/cts/cts_final/version/CutScene_YG_AnimCard_Act_Other_YG_D_0026_CC04_01.cts_final.v024.npy', 'M:/projects/X3/npy/shots/CutScene/CutScene_YG_AnimCard_Act_Other_YG_D_0026_CC05_01/cts/cts_final/version/CutScene_YG_AnimCard_Act_Other_YG_D_0026_CC05_01.cts_final.v023.npy']
    # # task_id='test_task_005_sender_range'
    # # ok, result = sender_ai_match_range_request(task_id, long_vide_npy, shot_npy_list)
    # # _data=result['result']
    # _json_file=r'F:\AITest\test\test_task_005_sender_range.json'
    # task_id='test_task_006_sender_similarity'
    # # write_json_to_file(_data, _json_file, wtype="w")
    # ok,result=sender_ai_compute_similarity_request(task_id, _json_file, long_video, shot_video_list, out_path=r'F:\AITest\test\output.zip')
    # _json_file=r'F:\AITest\test\test_task_006_sender_similarity.json'
    # # _data=result['result']
    # # write_json_to_file(_data, _json_file, wtype="w")
    # task_id='test_task_101_sender_com_video'
    # long_video=r'F:\AITest\test\YGD0026_PV.mp4'
    # output=r'F:\AITest\test\output.mp4'
    #
    # print(sender_com_video(task_id, long_video, shot_video_list,_json_file,output, url="extract_video"))

    # long_video=u'D:/temp_info/ai_video_lib/local_video/【YS_D0026】250228 YS愿缘长.mp4'
    # json_file=r"D:\temp_info\ai_video_lib\match_video_b28733dbc15613924cc054b7c7303d09_1755686777330_1755687005246.json"
    # shot_video="M:/projects/X3/publish/shots/CutScene/CutScene_YS_AnimCard_Act_Other_YS_D_0026_CC01_01/cts/cts_final/version/CutScene_YS_AnimCard_Act_Other_YS_D_0026_CC01_01.cts_final.v019.mp4"
    #
    #
    # print(sender_com_video(task_id, long_video, [shot_video],json_file, url="extract_video"))
    # task_id = '6186b64f9f987954fc1b3c62d737829f_1753088460960'
    # long_vide_npy=r'D:\temp_info\ai_video_lib\video_bc9c89a3590be93927ea86380429684d_1752809606630.npy'
    # shot_npy_list = ['M:/projects/X3/npy/shots/CutScene/CutScene_YS_AnimCard_Act_Other_YS_D_0026_CC04C_01/cts/cts_final/version/CutScene_YS_AnimCard_Act_Other_YS_D_0026_CC04C_01.cts_final.v019.npy','M:/projects/X3/npy/shots/CutScene/CutScene_YS_AnimCard_Act_Other_YS_D_0026_CC04B_01/cts/cts_final/version/CutScene_YS_AnimCard_Act_Other_YS_D_0026_CC04B_01.cts_final.v019.npy']
    # ok, result = sender_ai_match_range_request(task_id, long_vide_npy, shot_npy_list)
    # print(result)

    # task_id='6186b64f9f987954fc1b3c62d737829f_1753088460960'
    # video_segment_json='D:/temp_info/ai_video_lib/match_video_d2d7545086489eafb49583a80a659ff5_1753087220050_1753087367251.json'
    # long_video = 'D:/temp_info/ai_video_lib/video_d2d7545086489eafb49583a80a659ff5_1752835994482.mp4'
    # shot_video_list = [
    #     'M:/projects/X3/publish/shots/CutScene/CutScene_YS_AnimCard_Act_Other_YS_D_0026_CC06_01/cts/cts_final/version/CutScene_YS_AnimCard_Act_Other_YS_D_0026_CC06_01.cts_final.v020.mp4',
    #     'M:/projects/X3/publish/shots/CutScene/CutScene_YS_AnimCard_Act_Other_YS_D_0026_CC03_01/cts/cts_final/version/CutScene_YS_AnimCard_Act_Other_YS_D_0026_CC03_01.cts_final.v019.mp4',
    #     'M:/projects/X3/publish/shots/CutScene/CutScene_YS_AnimCard_Act_Other_YS_D_0026_Ending_02/cts/cts_final/version/CutScene_YS_AnimCard_Act_Other_YS_D_0026_Ending_02.cts_final.v002.mp4',
    #     'M:/projects/X3/publish/shots/CutScene/CutScene_YS_AnimCard_Act_Other_YS_D_0026_CC01_01/cts/cts_final/version/CutScene_YS_AnimCard_Act_Other_YS_D_0026_CC01_01.cts_final.v019.mp4',
    #     'M:/projects/X3/publish/shots/CutScene/CutScene_YS_AnimCard_Act_Other_YS_D_0026_CC04C_01/cts/cts_final/version/CutScene_YS_AnimCard_Act_Other_YS_D_0026_CC04C_01.cts_final.v019.mp4',
    #     'M:/projects/X3/publish/shots/CutScene/CutScene_YS_AnimCard_Act_Other_YS_D_0026_CC07_01/cts/cts_final/version/CutScene_YS_AnimCard_Act_Other_YS_D_0026_CC07_01.cts_final.v021.mp4',
    #     'M:/projects/X3/publish/shots/CutScene/CutScene_YS_AnimCard_HeadLittle_YS_D_0026_CC02_01/lgt/lgt_final/version/CutScene_YS_AnimCard_HeadLittle_YS_D_0026_CC02_01.lgt_final.v008.mp4',
    #     'M:/projects/X3/publish/shots/CutScene/CutScene_YS_AnimCard_Act_Other_YS_D_0026_CC06_02/cts/cts_final/version/CutScene_YS_AnimCard_Act_Other_YS_D_0026_CC06_02.cts_final.v020.mp4',
    #     'M:/projects/X3/publish/shots/CutScene/CutScene_YS_AnimCard_Loop_Idle_YS_D_0026_01/lgt/lgt_final/version/CutScene_YS_AnimCard_Loop_Idle_YS_D_0026_01.lgt_final.v008.mp4',
    #     'M:/projects/X3/publish/shots/CutScene/CutScene_YS_AnimCard_Act_Other_YS_D_0026_CC04A_01/cts/cts_final/version/CutScene_YS_AnimCard_Act_Other_YS_D_0026_CC04A_01.cts_final.v020.mp4',
    #     'M:/projects/X3/publish/shots/CutScene/CutScene_YS_AnimCard_Act_Other_YS_D_0026_CC03A_01/cts/cts_final/version/CutScene_YS_AnimCard_Act_Other_YS_D_0026_CC03A_01.cts_final.v019.mp4',
    #     'M:/projects/X3/publish/shots/CutScene/CutScene_YS_AnimCard_BellyBig_YS_D_0026_CC05_02/lgt/lgt_final/version/CutScene_YS_AnimCard_BellyBig_YS_D_0026_CC05_02.lgt_final.v009.mp4',
    #     'M:/projects/X3/publish/shots/CutScene/CutScene_YS_AnimCard_Act_Other_YS_D_0026_CC01_02/cts/cts_final/version/CutScene_YS_AnimCard_Act_Other_YS_D_0026_CC01_02.cts_final.v019.mp4',
    #     'M:/projects/X3/publish/shots/CutScene/CutScene_YS_AnimCard_ChestBig_YS_D_0026_CC06_01/lgt/lgt_final/version/CutScene_YS_AnimCard_ChestBig_YS_D_0026_CC06_01.lgt_final.v008.mp4',
    #     'M:/projects/X3/publish/shots/CutScene/CutScene_YS_AnimCard_Act_Other_YS_D_0026_CC04B_01/cts/cts_final/version/CutScene_YS_AnimCard_Act_Other_YS_D_0026_CC04B_01.cts_final.v019.mp4',
    #     'M:/projects/X3/publish/shots/CutScene/CutScene_YS_AnimCard_ChestLittle_YS_D_0026_CC06_02/lgt/lgt_final/version/CutScene_YS_AnimCard_ChestLittle_YS_D_0026_CC06_02.lgt_final.v008.mp4',
    #     'M:/projects/X3/publish/shots/CutScene/CutScene_YS_AnimCard_Act_Other_YS_D_0026_CC02_02/cts/cts_final/version/CutScene_YS_AnimCard_Act_Other_YS_D_0026_CC02_02.cts_final.v019.mp4',
    #     'M:/projects/X3/publish/shots/CutScene/CutScene_YS_AnimCard_Act_Other_YS_D_0026_Ending_01/lgt/lgt_final/version/CutScene_YS_AnimCard_Act_Other_YS_D_0026_Ending_01.lgt_final.v008.mp4',
    #     'M:/projects/X3/publish/shots/CutScene/CutScene_YS_AnimCard_Act_Other_YS_D_0026_CC05_01/cts/cts_final/version/CutScene_YS_AnimCard_Act_Other_YS_D_0026_CC05_01.cts_final.v019.mp4',
    #     'M:/projects/X3/publish/shots/CutScene/CutScene_YS_AnimCard_NeckBig_YS_D_0026_CC01_01/lgt/lgt_final/version/CutScene_YS_AnimCard_NeckBig_YS_D_0026_CC01_01.lgt_final.v007.mp4',
    #     'M:/projects/X3/publish/shots/CutScene/CutScene_YS_AnimCard_Act_Other_YS_D_0026_CC03B_01/cts/cts_final/version/CutScene_YS_AnimCard_Act_Other_YS_D_0026_CC03B_01.cts_final.v019.mp4',
    #     'M:/projects/X3/publish/shots/CutScene/CutScene_YS_AnimCard_Act_Other_YS_D_0026_CC03_01/lgt/lgt_final/version/CutScene_YS_AnimCard_Act_Other_YS_D_0026_CC03_01.lgt_final.v007.mp4',
    #     'M:/projects/X3/publish/shots/CutScene/CutScene_YS_AnimCard_Act_Other_YS_D_0026_Start_01/lgt/lgt_final/version/CutScene_YS_AnimCard_Act_Other_YS_D_0026_Start_01.lgt_final.v008.mp4',
    #     'M:/projects/X3/publish/shots/CutScene/CutScene_YS_AnimCard_Loop_Idle_YS_D_0026_02/lgt/lgt_final/version/CutScene_YS_AnimCard_Loop_Idle_YS_D_0026_02.lgt_final.v007.mp4',
    #     'M:/projects/X3/publish/shots/CutScene/CutScene_YS_AnimCard_BellyLittle_YS_D_0026_CC05_01/lgt/lgt_final/version/CutScene_YS_AnimCard_BellyLittle_YS_D_0026_CC05_01.lgt_final.v008.mp4',
    #     'M:/projects/X3/publish/shots/CutScene/CutScene_YS_AnimCard_Loop_Idle_YS_D_0026_02/cts/cts_final/version/CutScene_YS_AnimCard_Loop_Idle_YS_D_0026_02.cts_final.v019.mp4',
    #     'M:/projects/X3/publish/shots/CutScene/CutScene_YS_AnimCard_Act_Other_YS_D_0026_CC02_01/cts/cts_final/version/CutScene_YS_AnimCard_Act_Other_YS_D_0026_CC02_01.cts_final.v019.mp4',
    #     'M:/projects/X3/publish/shots/CutScene/CutScene_YS_AnimCard_Loop_Idle_YS_D_0026_01/cts/cts_final/version/CutScene_YS_AnimCard_Loop_Idle_YS_D_0026_01.cts_final.v019.mp4',
    #     'M:/projects/X3/publish/shots/CutScene/CutScene_YS_AnimCard_Act_Other_YS_D_0026_CC04_01/cts/cts_final/version/CutScene_YS_AnimCard_Act_Other_YS_D_0026_CC04_01.cts_final.v020.mp4',
    #     'M:/projects/X3/publish/shots/CutScene/CutScene_YS_AnimCard_WaistBig_YS_D_0026_CC04_02/lgt/lgt_final/version/CutScene_YS_AnimCard_WaistBig_YS_D_0026_CC04_02.lgt_final.v008.mp4',
    #     'M:/projects/X3/publish/shots/CutScene/CutScene_YS_AnimCard_HeadBig_YS_D_0026_CC07_01/lgt/lgt_final/version/CutScene_YS_AnimCard_HeadBig_YS_D_0026_CC07_01.lgt_final.v007.mp4',
    #     'M:/projects/X3/publish/shots/CutScene/CutScene_YS_AnimCard_Act_Other_YS_D_0026_CC07_02/cts/cts_final/version/CutScene_YS_AnimCard_Act_Other_YS_D_0026_CC07_02.cts_final.v020.mp4',
    #     'M:/projects/X3/publish/shots/CutScene/CutScene_YS_AnimCard_WaistLittle_YS_D_0026_CC04_01/lgt/lgt_final/version/CutScene_YS_AnimCard_WaistLittle_YS_D_0026_CC04_01.lgt_final.v007.mp4']
    #
    # ok,result=sender_ai_compute_similarity_request(task_id, video_segment_json, long_video, shot_video_list)
    # print(ok, result)
    # video_path = r'F:\AITest\YS_D0026.mp4'
    # out_path = r'F:\AITest\output.zip'
    #
    # ok, reslut = get_ai_video_data(task_id, video_path, out_path, url="get_embeddings", frame_out=30)
    # print(ok, reslut)
    # task_id = "test_compute_similarity_05"
    #
    # long_video = ""
    # json_file = "D:/temp_info/ai/lang/{}.json".format(task_id)
    # long_vide_np = r"D:\temp_info\ai\lang\YS_D0026.npy"
    # short_video_npy_list = [
    #     r"D:\temp_info\ai\short\CutScene_YS_AnimCard_Act_Other_YS_D_0026_CC01_01.npy",
    # ]
    # ok, reslut = sender_ai_match_range_request(task_id, long_vide_np, short_video_npy_list)
    # print(reslut)

    # ok,result=creat_match_range_json(json_file, task_id, long_vide_np, short_video_npy_list)
    # print(ok, result)
    # video_segment_json = 'D:/temp_info/ai/lang/test_match_06.json'
    # long_video = r'F:\AITest\YS_D0026.mp4'
    # shot_video_list = [r'F:\AITest\AnimCard_YS_D0026\CutScene_YS_AnimCard_Act_Other_YS_D_0026_CC01_01.mp4']
    #
    # ok, result = sender_ai_compute_similarity_request(task_id, video_segment_json, long_video, shot_video_list)
    # print(ok, result)

    # video_path = u'F:/AITest/【YS_D0026】250228 YS愿缘长.mp4'
    # task_id = "test_task_004"
    # out_path = u'D:/temp_info/ai/lang/【YS_D0026】250228 YS愿缘长.zip'
    # data = get_ai_video_data(task_id, video_path, out_path)
    # print(data)
