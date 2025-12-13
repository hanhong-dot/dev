# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       : mediainfo
# Describe   : 说明描述
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2022/5/20__21:18
# -------------------------------------------------------
import subprocess

APP_PATH = "Z:\\dev\\tools\\ffmpeg\\bin\\ffmpeg.exe"
APPR_PATH = "Z:\\dev\\tools\\ffmpeg\\bin\\ffprobe.exe"

class MediaCollect(object):
    '''只负责处理搜集相关媒体信息。'''

    def __init__(self, ffmpeg_path=APPR_PATH):
        self.ffmpro_path = ffmpeg_path

    def getframes(self):
        # 获取帧数，并返回
        streams = self.media["streams"]
        frames_info = streams[0]
        frame_number = frames_info["nb_frames"]
        return frame_number

    def getcodecname(self):
        # 获取视频编码格式长名，短名，并返回。
        streams = self.media["streams"]
        frames_info = streams[0]
        return {"codec_long_name": frames_info["codec_long_name"], "codec_name": frames_info["codec_name"],
                "avg_frame_rate": frames_info['avg_frame_rate']}

    def getcodecwidthheight(self):
        # 获取视频编码宽和高
        streams = self.media["streams"]
        frames_info = streams[0]
        return {"coded_height": frames_info["coded_height"], "coded_width": frames_info["coded_width"]}

    def getmediadic(self):
        streams = self.media["streams"]
        return streams

    def initffmpeg(self, media_path=""):
        import ffmpeg
        try:
            media_path = media_path.encode("gbk")
        except:
            media_path = media_path.decode("utf8").encode("gbk")
        self.media = ffmpeg.probe(media_path, cmd=self.ffmpro_path)

    def get_image_from_mov(self, seconds="", filepath="", frames="", sizes="",
                           output_name="", ffmpeg_path=APP_PATH):
        '''
        :param seconds: 指定视频的第几秒，要求：参数类型为字符串
        :param filepath: 要截取视频的路径。
        :param frames: 要截取视频在seconds秒的第几帧
        :param sizes: 指定图片的尺寸。参数类型：字符串。例如："460x380".如果没有则为默认尺寸。
        :param output_name: 指定输出的路径。
        :return:
        '''
        # 如果没有指定截图尺寸，使用默认尺寸
        if sizes == "":
            cmds = [ffmpeg_path.encode("gbk"), "-y".encode("gbk"), "-ss".encode("gbk"),
                    seconds.encode("gbk"), "-i".encode("gbk"), filepath.encode("gbk"),
                    "-vframes".encode("gbk"), frames.encode("gbk"), "-f".encode("gbk"),
                    "image2".encode("gbk"), output_name.encode("gbk")]

        else:
            cmds = [ffmpeg_path.encode("gbk"), "-y".encode("gbk"), "-ss".encode("gbk"),
                    seconds.encode("gbk"), "-i".encode("gbk"), filepath.encode("gbk"),
                    "-vframes".encode("gbk"), frames.encode("gbk"), "-f".encode("gbk"),
                    "image2".encode("gbk"), "-s".encode("gbk"), sizes.encode("gbk"),
                    output_name.encode("gbk")]

        popen_info = subprocess.Popen(cmds, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
        if popen_info:
            return output_name
        else:
            return ''

    def get_image_from_image(self, filepath="", sizes="", oupput_name=""
                             , ffmpeg_path=APP_PATH):
        '''

        :param filepath: 原始图片的路径
        :param sizes: 要生成的图片尺寸
        :param oupput_name: 输出文件名字
        :param ffmpeg_path: 输出图片路径
        :return: None
        '''
        cmds = [ffmpeg_path.encode("gbk"), "-i".encode("gbk"), filepath.encode("gbk"),
                "-f".encode("gbk"), "image2".encode("gbk"), "-s".encode("gbk"), sizes.encode("gbk"),
                oupput_name.encode("gbk")]
        popen_info = subprocess.Popen(cmds, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
        return None

    def cover_mov_sequence(self, movpath="", oupput="", fps="30", ffmpeg_path=APP_PATH):
        u"""

        :param movpath: 原始视频的路径
        :param oupput_frame: 输出的序列帧数
        :param fps: 帧速率
        :param ffmpeg_path:
        :return:
        """
        cmds = [ffmpeg_path.encode("gbk"), "-i".encode("gbk"), movpath.encode("gbk"), "-r".encode("gbk"),
                fps.encode("gbk"),
                "-f".encode("gbk"), "image2".encode("gbk"), oupput.encode("gbk")]
        popen_info = subprocess.Popen(cmds, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
        if popen_info:
            return oupput
        else:
            return ''

    def get_size_about_media(self, media_path):
        '''
        获取图片或者视频的分辨率
        :param media_path: 媒体路径
        :return: {'width': 102, 'height': 123}
        '''
        import ffmpeg
        self.media = ffmpeg.probe(media_path.encode("gbk"), cmd=self.ffmpro_path)
        info = self.media["streams"]
        width = info[0]["coded_width"]
        height = info[0]["coded_height"]
        return {"width": width, "height": height}

    def get_frame_about_media(self, media_path):
        import ffmpeg
        _media_info = ffmpeg.probe(media_path.encode("gbk"), cmd=self.ffmpro_path)
        print(_media_info['streams'][0])
        try:
            return _media_info['streams'][0]['nb_frames']
        except:
            pass

    def get_fps_about_media(self, media_path):
        import ffmpeg
        _media_info = ffmpeg.probe(media_path.encode("gbk"), cmd=self.ffmpro_path)
        try:
            return _media_info[0]['nb_frames']
        except:
            pass

    def ssim_contrast(self, _source_media, _targe_media, ffmpeg_path=APP_PATH):
        u"""
        :param _source_media:
        :param _targe_media:
        :param ffmpeg_path:
        :return: 例如{'Y': 0.991175, 'All': 0.993112, 'U': 0.996974, 'V': 0.996999}(Y:图像的亮度信息（luma）,U 和 V:图像的色度信息（chroma）)
        """
        _cmds = '{} -i {} -i {} -lavfi ssim="stats_file=ssim.log" -f null -'.format(ffmpeg_path.encode("gbk"),
                                                                                    _source_media.encode("gbk"),
                                                                                    _targe_media.encode("gbk"))
        info = subprocess.Popen(_cmds, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()


        return self._cover_ssim_dict(list(info)[-1].split("SSIM")[-1])

    def judge_ssim_contrast(self, _cont, _source_media, _targe_media, ffmpeg_path=APP_PATH):
        _ssim_data = self.ssim_contrast(_source_media, _targe_media, ffmpeg_path)
        print('_ssim_data', _ssim_data)
        _result = True
        for k, v in _ssim_data.items():
            if v < _cont:
                _result = False
                break
        return _result

    # def cover_curver(self):

    def resize_mp4_file(self, input_file, output_file, width, height, ffmpeg_path=APP_PATH):
        u"""
        :param input_file: 输入文件路径
        :param output_file: 输出文件路径
        :param width: 宽度
        :param height: 高度
        :param ffmpeg_path:
        :return:
        """
        import os

        if not os.path.exists(os.path.dirname(output_file)):
            os.makedirs(os.path.dirname(output_file))

        # FFmpeg 命令
        ffmpeg_command = [
            ffmpeg_path.encode("gbk"),
            "-i", input_file.encode("gbk"),

            "-vf", "scale={}:{}".format(width, height).encode("gbk"),
            output_file.encode("gbk")
        ]

        # 执行 FFmpeg 命令
        info = subprocess.Popen(ffmpeg_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
        print(info)

    def cover_image_to_mp4(self, image_path, output_path, fps="30", ffmpeg_path=APP_PATH):
        import os
        import subprocess
        _dir, _file = os.path.split(output_path)
        if not os.path.exists(_dir):
            os.makedirs(_dir)

        # FFmpeg 命令
        ffmpeg_command = [
            ffmpeg_path.encode("gbk"),
            "-framerate", fps,
            "-i", image_path.encode("gbk"),

            "-c:v", "libx264",
            "-preset", "slow",
            "-crf", "0",
            "-pix_fmt", "yuv420p",
            output_path.encode("gbk")
        ]

        # 执行 FFmpeg 命令

        info=subprocess.Popen(ffmpeg_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
        print(info)

    def convert_mov_to_mp4(self,input_path, output_path, ffmpeg_path=APP_PATH):
        try:
            command = [
                ffmpeg_path,
                "-i", input_path,
                "-c", "copy",
                output_path
            ]

            # # 执行命令
            # result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            result = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
            return True
        except:
            print('error')
            return False

        #     if result.returncode == 0:
        #         print("转换成功:", output_path)
        #     else:
        #         print("转换失败，错误信息:")
        #         print(result.stderr.decode("utf-8"))
        # except Exception as e:
        #     print("运行错误:", str(e))

    def psnr_contrast(self, _source_media, _targe_media, ffmpeg_path=APP_PATH):
        u"""

        :param _source_media:
        :param _targe_media:
        :param ffmpeg_path:
        :return:
        """
        _cmds = '{} -i {} -i {} -lavfi psnr="stats_file=psnr.log" -f null -'.format(ffmpeg_path.encode("gbk"),
                                                                                    _source_media.encode("gbk"),
                                                                                    _targe_media.encode("gbk"))
        info = subprocess.Popen(_cmds, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
        return self._cover_dict(list(info)[-1].split("PSNR")[-1])

    def judge_psnr_contrast(self, _cont, _source_media, _targe_media, ffmpeg_path=APP_PATH):
        u"""

        :param _cont:
        :param _source_media:
        :param _targe_media:
        :param ffmpeg_path:
        :return:
        """
        _psnr_data = self.psnr_contrast(_source_media, _targe_media, ffmpeg_path)
        _result = True
        for k, v in _psnr_data.items():
            if v < _cont:
                _result = False
                break
        return _result

    def _cover_dict(self, data_str):
        data_dict = {}
        for item in data_str.split():
            key, value = item.split(':')
            data_dict[key] = float(value)
        return data_dict

    def _cover_ssim_dict(self, data_str):
        data_dict = {}
        for item in data_str.split():
            key_value_list = item.split(':')
            if key_value_list and len(key_value_list) > 1:
                key = key_value_list[0]
                value_list = key_value_list[1].split()
                value = float(value_list[0])
                data_dict[key] = value
        return data_dict


def get_psnr(img01, img02):
    import cv2
    import numpy as np

    _img_01 = cv2.imread(img01)
    _img_02 = cv2.imread(img02)
    _img_c_1 = np.array(_img_01, dtype=np.float64)
    _img_c_2 = np.array(_img_02, dtype=np.float64)
    mse = np.mean(np.square(_img_c_2 - _img_c_1))
    if mse < 1.0e-10:
        return 100
    return 10 * np.log10(255 * 255 / mse)

def get_file_list(dir):
    import os
    import glob
    _file_list = glob.glob(os.path.join(dir, '*.png'))
    return _file_list

def get_ssim_data(source_list,targe_list):
    __ssim_data=[]
    for i in range(len(source_list)):
        _source_media=source_list[i]
        _targe_media=targe_list[i]
        __ssim=MediaCollect().ssim_contrast(_source_media, _targe_media)
        __ssim_data.append(__ssim)
    return __ssim_data

def cover_ssim_data(ssim_data):
    r_list=[]
    g_list=[]
    b_list=[]
    a_list=[]
    for i in range(len(ssim_data)):
        r_list.append(ssim_data[i]['R'])
        g_list.append(ssim_data[i]['G'])
        b_list.append(ssim_data[i]['B'])
        a_list.append(ssim_data[i]['All'])
    return r_list,g_list,b_list,a_list




def draw_curve_by_data(y_list, u_list, v_list, all_list):
    import numpy as np
    import matplotlib.pyplot as plt
    x = np.arange(len(y_list))  # x 轴数据

    # 绘制多条曲线
    plt.plot(x, y_list, label='Y', color='red', marker='o')
    # plt.plot(x, u_list, label='U', color='green', marker='o')
    # plt.plot(x, v_list, label='V', color='blue', marker='o')
    # plt.plot(x, all_list, label='All', color='orange', marker='o')

    # 设置 x 轴标签
    plt.xticks(x, fontsize=6, rotation=0)  # 字体大小为 10，水平显示

    # # 添加图例
    # plt.legend(loc='upper right')

    # 显示网格（可选）
    # plt.grid(alpha=0.5)

    # 显示图像
    plt.show()





def read_info(path, rtype="r"):
    import os
    if not os.path.exists(path):
        return None
    with open(path, rtype) as f:
        _data = f.read()
        try:
            _data = _data.decode('utf-8')
        except:
            pass
    return _data

def cover_info(info):
    _info_list=info.split('\n')
    _ssim_data=[]
    y_list=[]
    u_list=[]
    v_list=[]
    all_list=[]
    for i in range(len(_info_list)):
        if 'Y:' in _info_list[i]:
            y_inf=_info_list[i].split('Y:')[-1].split(' ')[0]
            y_list.append(float(y_inf))
        if 'U:' in _info_list[i]:
            u_inf=_info_list[i].split('U:')[-1].split(' ')[0]
            u_list.append(float(u_inf))
        if 'V:' in _info_list[i]:
            v_inf=_info_list[i].split('V:')[-1].split(' ')[0]
            v_list.append(v_inf)
        if 'All:' in _info_list[i]:
            a_inf=_info_list[i].split('All:')[-1].split(' ')[0]
            all_list.append(float(a_inf))
    return y_list,u_list,v_list,all_list





if __name__ == "__main__":
    import os
    # input_pattern = r"F:\record\CutScene_YS_AnimCard_Act_Other_YS_D_0016_CC03_01\frame_%04d.png"
    # output_path = r"F:\record\mp4\CutScene_YS_AnimCard_Act_Other_YS_D_0016_CC03_01.mp4"
    handle = MediaCollect()
    input_file=u'Z:/TD/PV-仅供工具研发测试使用/check/t/D0014.mp4'
    output_file=u'Z:/TD/PV-仅供工具研发测试使用/check/t/D0014_n01.mp4'
    width=1920*0.5
    height=1080*0.5
    handle.resize_mp4_file(input_file, output_file, width, height, ffmpeg_path=APP_PATH)
    # width=1440*0.5
    # height=1920*0.5
    # input_dir=u'Z:/TD/PV-仅供工具研发测试使用/check/t/AnimCard_RY_D0014'
    # output_dir=u'Z:/TD/PV-仅供工具研发测试使用/check/t/AnimCard_RY_D0014_N'

    # files=os.listdir(input_dir)
    # for file in files:
    #     input_file=u'{}/{}'.format(input_dir,file)
    #     output_file=u'{}/{}'.format(output_dir,file)
    #     handle.resize_mp4_file(input_file, output_file, width, height, ffmpeg_path=APP_PATH)




    # handle.resize_mp4_file(input_file, output_file, width, height, ffmpeg_path=APP_PATH)
    # # handle.cover_image_to_mp4(input_pattern, output_path)
    # input_path01=r'E:\cts\move_3_t.mov'
    # output_path01=r'E:\cts\move_3_t.mp4'
    # handle.convert_mov_to_mp4(input_path01, output_path01,ffmpeg_path=APP_PATH)
    #
    # input_path02=r'F:\record\CutScene_YS_AnimCard_Act_Other_YS_D_0016_CC03_01.mov'
    # output_path02=r'F:\record\CutScene_YS_AnimCard_Act_Other_YS_D_0016_CC03_01.mp4'
    # handle.convert_mov_to_mp4(input_path02, output_path02, ffmpeg_path="ffmpeg")
    # _source_media='M:/projects/X3/publish/shots/CutScene/CutScene_RY_AnimCard_Act_Other_RY_D_0014_CC02_01/cts/cts_final/version/CutScene_RY_AnimCard_Act_Other_RY_D_0014_CC02_01.cts_final.v031.mp4'
    # _targe_media='M:/projects/X3/publish/shots/CutScene/CutScene_RY_AnimCard_Act_Other_RY_D_0014_CC02_01/cts/cts_final/version/CutScene_RY_AnimCard_Act_Other_RY_D_0014_CC02_01.cts_final.v030.mp4'
    # import os
    # source_img=r'E:\python_env\python310\Scripts\dist\connn\card_ry_sr_0007.lighting.v001.png'
    # targe_img=r'E:\python_env\python310\Scripts\dist\connn\con007.png'
    # print(MediaCollect().ssim_contrast(source_img, targe_img))

    #画曲线
    # _source_media=r'E:\match\Test\source.mov'
    # _targe_media=r'E:\match\Test\targe.mov'
    #
    # handle.ssim_contrast(_source_media, _targe_media)
    # log_file=r'E:\dev\lib\common\ssim.log'
    # info=read_info(log_file)
    # ssim_data=cover_info(info)
    # y_list,u_list,v_list,all_list=ssim_data
    # draw_curve_by_data(y_list,u_list,v_list,all_list)


    # _ssim_file = r'E:\dev\lib\common\ssim.log'

    # source = 'D:/P4/img/source/CutScene_RY_AnimCard_Act_Other_RY_D_0014_CC02_01.%04d.png'
    # targe='D:/P4/img/targe/CutScene_RY_AnimCard_Act_Other_RY_D_0014_CC02_01.%04d.png'
    # #
    # _source_img= handle.cover_mov_sequence(_source_media, oupput=source)
    # _targe_img= handle.cover_mov_sequence(_targe_media, oupput=targe)

    # source_file_list=get_file_list(r'D:\P4\img\n\source')
    # targe_file_list=get_file_list(r'D:\P4\img\n\targe')
    # print('source_file_list',source_file_list)
    # print('targe_file_list',targe_file_list)
    # ssim_data=get_ssim_data(source_file_list,targe_file_list)
    # result=cover_ssim_data(ssim_data)
    #
    # r_list, g_list, b_list, a_list=result
    # draw_curve_by_data(r_list, g_list, b_list, a_list)




    # print handle.ssim_contrast(_source_media, _targe_media)

    # {
    #     'Last_version_file': 'M:/projects/X3/publish/shots/CutScene/CutScene_RY_AnimCard_Act_Other_RY_D_0014_CC02_01/cts/cts_final/version/CutScene_RY_AnimCard_Act_Other_RY_D_0014_CC02_01.cts_final.v031.mp4',
    #     'second_to_last_version_file': 'M:/projects/X3/publish/shots/CutScene/CutScene_RY_AnimCard_Act_Other_RY_D_0014_CC02_01/cts/cts_final/version/CutScene_RY_AnimCard_Act_Other_RY_D_0014_CC02_01.cts_final.v030.mp4',
    #     'ssim_data': {'Y': 0.894906, 'All': 0.92449, 'U': 0.982099, 'V': 0.985219}}
    # print handle.cover_image_to_mp4('image_001_%04d.png', r'F:\RecordTest\test.mp4', fps="30", ffmpeg_path=APP_PATH)
    # import os
    # import cv2
    # import numpy as np
    # from PIL import Image
    # import glob
    # import lib.common.jsonio as jsonio
    # import shutil
    # media_instance = MediaCollect()
    # #
    # # _file_01 = r'Z:\TD\test\samp\first\CutScene_ML_C1S3_S01_P01.mp4'
    # # _file_02 = r'Z:\TD\test\samp\second\CutScene_ML_C1S3_S01_P01.mp4'
    # # # _file_03 = 'K:/images/UnityCts/X3/cts_final/CutScene_ML_C1S2_S01_P01.mp4'
    # # print(media_instance.psnr_contrast(_file_01, _file_02, ffmpeg_path=APP_PATH))
    # # # print(media_instance.judge_psnr_contrast(30, _file_01, _file_02, ffmpeg_path=APP_PATH))
    # # #
    # # # print(media_instance.psnr_contrast(_file_01, _file_02, ffmpeg_path=APP_PATH))
    # # # print(media_instance.judge_psnr_contrast(30, _file_01, _file_02, ffmpeg_path=APP_PATH))
    # #
    # # print(media_instance.ssim_contrast(_file_01, _file_02, ffmpeg_path=APP_PATH))
    #
    #
    # _dir01=r'Z:\TD\test\samp\0413\first'
    # _dir02=r'Z:\TD\test\samp\0413\second'
    # _filelist01 = glob.glob(os.path.join(_dir01, '*.mp4'))
    # _filelist02 = glob.glob(os.path.join(_dir02, '*.mp4'))
    # _dict={}
    #
    # for i in range(len(_filelist01)):
    #     _base_name=os.path.basename(_filelist01[i])
    #     for j in range(len(_filelist01)):
    #         if _base_name==os.path.basename(_filelist02[j]):
    #             _dict[_filelist01[i]]=_filelist02[j]
    # for k,v in _dict.items():
    #     basename=os.path.splitext(os.path.basename(k))[0]
    #     _ssim=media_instance.ssim_contrast(k,v, ffmpeg_path=APP_PATH)
    #     _psnr=media_instance.psnr_contrast(k,v, ffmpeg_path=APP_PATH)
    #
    #     _info={'ssim':_ssim,'psnr':_psnr}
    #     _dir=r'Z:\TD\test\samp\0413\log'
    #     path='{}\\{}.json'.format(_dir,basename)
    #     _dirn=r'D:\dev\lib\common'
    #     _ssim_file_d='{}\\ssim.log'.format(_dirn)
    #     _psnr_file_d='{}\\psnr.log'.format(_dirn)
    #     _ssim_file='{}\\{}.ssim'.format(_dir,basename)
    #     _ssim_log='{}\\{}.ssim.log'.format(_dir,basename)
    #     _psnr_log='{}\\{}.psnr.log'.format(_dir,basename)
    #     jsonio.write(_info,path,wtype='w')
    #     shutil.copy(_ssim_file_d,_ssim_log)
    #     shutil.copy(_psnr_file_d,_psnr_log)
    #     print(path)
    #     print(_ssim_log)
    #     print(_ssim_log)

    # MediaCollect().

    # print(media_instance.judge_ssim_contrast(0.98,_file_01, _file_02, ffmpeg_path=APP_PATH))
    # print(media_instance.ssim_contrast(_file_01, _file_03, ffmpeg_path=APP_PATH))
    # print(media_instance.judge_ssim_contrast(0.9, _file_01, _file_03, ffmpeg_path=APP_PATH))

    # _file_03 = 'M:/projects/X3/publish/shots/CutScene/CutScene_ML_C6S3_S01_P01B/lgt/version/CutScene_ML_C6S3_S01_P01B.lgt_final.v001.mp4'
    # _file_04 = 'M:/projects/X3/publish/shots/CutScene/CutScene_ML_C6S3_S01_P01B/lgt/version/CutScene_ML_C6S3_S01_P01B.lgt_final.v002.mp4'
    # print(media_instance.ssim_contrast(_file_03, _file_04, ffmpeg_path=APP_PATH))
    #
    # print(media_instance.psnr_contrast(_file_03, _file_04, ffmpeg_path=APP_PATH))

    # path = r"E:\temp_info\note\CutScene_ML_C10S2_S01_P01\attachement\annot_version_65912_v2.*.jpg"
    # files = glob.glob(path)
    #
    # print(files)

    # Z:\dev\tools\ffmpeg\bin\ffmpeg.exe - i K:/images/UnityCts/X3/cts_final/CutScene_ML_C1S1_S01_P01A.mp4 - i K:/images/UnityCts/X3/cts_final/Performance/MainLine/Chapter01/cts_final/CutScene_ML_C1S1_S01_P01A.mp4 - lavfi psnr = "stats_file=psnr_m.log" -f null -

    # ffmpeg - i e: / 1080psrc.mp4 - i e: / 1080pdst_l.mp4 - lavfi
    # psnr = "stats_file=psnr_l.log" - f
    # null -
    # _file_03 = 'K:/images/UnityCts/X3/cts_final/Performance/MainLine/Chapter01/cts_final/CutScene_ML_C1S2_S01_P01.mp4'
    # _imga05 = media_instance.get_image_from_mov(seconds="8", filepath=_file_01, frames="1",
    #                                             output_name='D:/P4/img/test_05.png')

    # oupput01 = 'D:/P4/img/cst01/CutScene_ML_C1S1_S01_P01A.%04d.png'
    # oupput02 = 'D:/P4/img/cst02/CutScene_ML_C1S1_S01_P01A.%04d.png'
    # _min = 100
    # _max=0
    # _count=0
    # # print(media_instance.get_frame_about_media(_file_01))
    # for i in range(470):
    #     _img01 = oupput01.replace('%04d', str(i + 1).zfill(4))
    #     _img02 = oupput02.replace('%04d', str(i + 1).zfill(4))
    #     psnr = get_psnr(_img01, _img02)
    #     _count=_count+psnr
    #     if psnr < _min :
    #         _min  = psnr
    #     if psnr>=_max:
    #         _max=psnr
    # print(_count/470)
    # print(_max)
    # print(_min)

    # print(media_instance.get_frame_about_media(_file_02))

    # img_frame_01 = media_instance.cover_mov_sequence(movpath=_file_01, oupput=oupput01, fps="30", ffmpeg_path=APP_PATH)
    # img_frame_02 = media_instance.cover_mov_sequence(movpath=_file_02, oupput=oupput02, fps="30", ffmpeg_path=APP_PATH)

    # cmds=['Z:\\dev\\tools\\ffmpeg\\bin\\ffmpeg.exe', '-i', 'K:/images/UnityCts/X3/cts_final/CutScene_ML_C1S1_S01_P01A.mp4', '-r', '30', '-f', 'image2', 'D:/P4/img/CutScene_ML_C1S1_S01_P01A/CutScene_ML_C1S1_S01_P01A.%04d.png']
    #
    # popen_info = subprocess.Popen(cmds, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
    # print(popen_info)
    # _img_01 = cv2.imread('D:/P4/img/test_01.png')
    # print(len(_img_01))
# _img_02 =  cv2.imread('D:/P4/img/test_02.png')
# _img_03 = cv2.imread('D:/P4/img/test_03.png')
# _img_04 = cv2.imread('D:/P4/img/test_04.png')
# _img_05 = cv2.imread('D:/P4/img/test_05.png')
# # # _img_03=
# #
# _img_c_1=np.array(_img_01, dtype=np.float64)
# _img_c_2 = np.array(_img_02, dtype=np.float64)
# _img_c_3 = np.array(_img_03, dtype=np.float64)
# _img_c_4 = np.array(_img_04, dtype=np.float64)
# _img_c_5 = np.array(_img_05, dtype=np.float64)


# diff = _img_c_1 - _img_c_2
# mse = np.mean(np.square(diff))
# psnr = 10 * np.log10(255 * 255 / mse)
# print(psnr)

# diff01= _img_c_3 - _img_c_2
# mse01 = np.mean(np.square(diff01))
# print(mse01)
# psnr01 = 10 * np.log10(255 * 255 / mse01)
# print(psnr01)

# diff02= _img_c_4 - _img_c_3
# mse02 = np.mean(np.square(diff02))
# psnr02 = 10 * np.log10(255 * 255 / mse02)
# print(psnr02)

# diff03=_img_c_5 - _img_c_3
# mse03 = np.mean(np.square(diff03))
# psnr03 = 10 * np.log10(255 * 255 / mse03)
# print(psnr03)

# mse = np.mean((_img_01 - _img_02) ** 2)
# max_pixel = 255.0
# psnr = 20 * np.log10(max_pixel / np.sqrt(mse))
# print(psnr)
# print(media_instance.get_size_about_media(path))


# _imga01=media_instance.get_image_from_mov(seconds="1", filepath=_file_01, frames="1", output_name=_img_01)
# _imga02 = media_instance.get_image_from_mov(seconds="1", filepath=_file_02, frames="1", output_name=_img_02)
