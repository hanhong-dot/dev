# -*- coding: utf-8 -*-
# -----------------------------------
# @File    : process_media.py
# @Author  : linhuan
# @Time    : 2025/8/30 14:55
# @Description : 
# -----------------------------------
import subprocess

APP_PATH = "Z:\\dev\\tools\\ffmpeg\\bin\\ffmpeg.exe"
APPR_PATH = "Z:\\dev\\tools\\ffmpeg\\bin\\ffprobe.exe"
from apps.tools.common.ai_video_match_tool import ai_video_match_fun
import os
import time


def comb_move_side(video1, video2, output):
    command = [
        APP_PATH,
        '-i', video1,
        '-i', video2,
        '-filter_complex', 'hstack',
        '-c:v', 'libx264',
        '-crf', '23',
        '-preset', 'veryfast',
        output
    ]
    p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    output, error = p.communicate()
    if p.returncode != 0:
        p.kill()
    try:
        return output.decode('utf-8')
    except:
        return output.decode('gbk', 'ignore').encode('utf-8)')


def comb_mov_seq_side(video1, video2, video1_start_frame, video1_end_frame, video2_start_frame,
                      video2_end_frame, sc=0.5, fps=30):
    local_dir = ai_video_match_fun.get_local_video_lib_path()
    com_dir = '{}/com_video'.format(local_dir)
    if not os.path.exists(com_dir):
        os.makedirs(com_dir)
    com_lib_dir = '{}/com_lib'.format(local_dir)
    if not os.path.exists(com_lib_dir):
        os.makedirs(com_lib_dir)
    video_1_cut_out_path = '{}/{}-{}_{}.mp4'.format(com_lib_dir, os.path.basename(video1).split('.')[0],
                                                    video1_start_frame, video1_end_frame)
    video_2_cut_out_path = '{}/{}-{}_{}.mp4'.format(com_lib_dir, os.path.basename(video2).split('.')[0],
                                                    video2_start_frame,
                                                    video2_end_frame)
    com_out_path = '{}/{}/com-{}_{}.mp4'.format(com_dir, os.path.basename(video2).split('.')[0], video2_start_frame,
                                                video2_end_frame)
    if not os.path.exists(os.path.dirname(com_out_path)):
        os.makedirs(os.path.dirname(com_out_path))

    video1_width, video1_height = get_size_about_media(video1).values()
    video2_width, video2_height = get_size_about_media(video2).values()

    max_width = max(video1_width, video2_width)
    max_height = max(video1_height, video2_height)

    video1_width_add = (max_width - video1_width) * sc
    video1_height_add = (max_height - video1_height) * sc
    video2_width_add = (max_width - video2_width) * sc
    video2_height_add = (max_height - video2_height) * sc
    if os.path.exists(video_1_cut_out_path):
        try:
            os.remove(video_1_cut_out_path)
        except:
            pass
    if os.path.exists(video_2_cut_out_path):
        try:
            os.remove(video_2_cut_out_path)
        except:
            pass
    if os.path.exists(com_out_path):
        try:
            os.remove(com_out_path)
        except:
            pass

    cut_and_resize_video(video1, video_1_cut_out_path, video1_start_frame, video1_end_frame, int(video1_width * sc),
                         int(video1_height * sc), int(video1_width_add), int(video1_height_add), fps=fps)

    cut_and_resize_video(video2, video_2_cut_out_path, video2_start_frame, video2_end_frame, int(video2_width * sc),
                         int(video2_height * sc), int(video2_width_add), int(video2_height_add), fps=fps)

    time.sleep(1)
    comb_move_side(video_1_cut_out_path, video_2_cut_out_path, com_out_path)
    if not os.path.exists(com_out_path):
        return False, 'error,not output file'
    return True, com_out_path


def get_size_about_media(media_path):
    import ffmpeg
    _media_info = ffmpeg.probe(media_path.encode("gbk"), cmd=APPR_PATH)

    info = _media_info["streams"]
    width = info[0]["coded_width"] if "coded_width" in info[0] else info[-1]["coded_width"]
    height = info[0]["coded_height"] if "coded_height" in info[0] else info[-1]["coded_height"]

    return {"width": width, "height": height}


def cut_and_resize_video(input_path, output_path, start_frame, end_frame, width, height, add_width=0, add_height=0,
                         fps=30, use_gpu=True):
    start_sec = float(start_frame) / fps
    end_sec = float(end_frame) / fps
    duration = end_sec - start_sec

    vf_filter = "scale={}:{},pad={}:{}:{}:{}:black".format(width, height, width + add_width, height + add_height,
                                                           int(add_width / 2), int(add_height / 2))

    command = [
        APP_PATH,
        "-ss", str(start_sec),
        "-i", input_path,
        "-t", str(duration),
        "-vf", vf_filter,
        "-c:v", "libx264",
        output_path
    ]

    p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


    output, error = p.communicate()
    if p.returncode != 0:
        p.kill()

    return output_path


# def combined_comparison_video(input_video1, input_video2, output_video):
#     """
#     合并对比视频
#     :param input_video1: 输入视频1路径
#     :param input_video2: 输入视频2路径
#     :param output_video: 输出视频路径
#     :return: None
#     """
#     command = [
#         APP_PATH,
#         '-i', input_video1,
#         '-i', input_video2,
#         '-filter_complex', 'hstack',
#         '-c:v', 'libx264',
#         '-crf', '23',
#         '-preset', 'veryfast',
#         output_video
#     ]
#     open_info = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
#     print(open_info)

# if __name__ == '__main__':
#     # video1 = r'D:\temp_info\ai_video_lib\local_video\YGD0026_PV.mp4'
#     # size01=get_size_about_media(video1)
#     # video2 = r'D:\temp_info\ai_video_lib\AnimCard_YG_D0026\CutScene_YG_AnimCard_Act_Other_YG_D_0026_CC01_01_old\CutScene_YG_AnimCard_Act_Other_YG_D_0026_CC01_01_old.mp4'
#     # size02=get_size_about_media(video2)
#     #
#     # _width01=size01["width"]
#     # _height01=size01["height"]
#     # _width02=size02["width"]
#     # _height02=size02["height"]
#     # print(_width01,_height01)
#     # print(_width02,_height02)
#     # #
#     # max_height=max(_height01,_height02)
#     # max_width=max(_width01,_width02)
#     # print(max_width,max_height)
#
#     # min_height_m = 1920 * 0.5
#     # min_width_m = 2560 * 0.5
#     # w1 = 2560 * 0.5
#     # h1 = 1440 * 0.5
#     # h1_h = min_height_m - h1
#     # input_video = r'D:\temp_info\ai_video_lib\local_video\YGD0026_PV.mp4'
#     # output_video = r'D:\temp_info\ai_video_lib\YGD0026_PV_01_test10.mp4'
#     # width = 2560 * 0.5
#     # height = 1440 * 0.5
#     # add_width = 0
#     # add_height = h1_h if h1_h > 0 else 0
#     # start_frame = 222
#     # stop_frame = 444
#     # input_video='D:/temp_info/ai_video_lib/local_video/YGD0026_PV.mp4'
#     # output_video='D:/temp_info/ai_video_lib/com_lib/YGD0026_PV-222_238.mp4'
#     # start_frame=222
#     # stop_frame=238
#     # width=1280
#     # height=960
#     # add_width=0
#     # add_height=240
#     # cut_and_resize_video(input_video, output_video, start_frame, stop_frame, width, height, add_width, add_height)
#     video1 = 'D:/temp_info/ai_video_lib/local_video/YGD0026_PV.mp4'
#     video2 = 'D:/temp_info/ai_video_lib/AnimCard_YG_D0026/CutScene_YG_AnimCard_Act_Other_YG_D_0026_CC02_01_old/CutScene_YG_AnimCard_Act_Other_YG_D_0026_CC02_01_old.mp4'
#     video1_start_frame = 222
#     video1_end_frame = 238
#     video2_start_frame = 42
#     video2_end_frame = 58
#     print(comb_mov_seq_side(video1, video2, video1_start_frame, video1_end_frame, video2_start_frame, video2_end_frame,
#                             sc=0.5, fps=30))

    # cover_viedeo_size(input_video, output_video,start_frame, stop_frame,width, height, add_width, add_height)

    # if min_height==_height01:
    #     new_width02=int(_width02*min_height/_height02)
    #     print(new_width02)
    #     new_width01=_width01

    # output = r'D:\temp_info\ai_video_lib\output.mp4'
    # comb_mov_seq_side(video1, video2, output)
