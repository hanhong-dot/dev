# coding=utf-8
import os
import shutil
import subprocess


def convert_video_to_jpg_frames(video_path):
    ffmpeg_cmd = "ffmpeg.exe"
    video_path = video_path.replace("\\", "/")
    out_template = os.path.splitext(video_path)[0]+".wav"
    print(video_path, out_template)
    cmd = f'{ffmpeg_cmd} -i "{video_path}"  "{out_template}"'
    return subprocess.Popen(cmd, shell=False)


def convert_all_videos_in_folder(folder_path):
    video_ext = ('.mp4', '.mov', '.avi', '.mkv', '.flv', '.wmv', '.mpeg', '.mpg', '.webm', '.m4v')
    names = sorted(os.listdir(folder_path))
    results = []
    for name in names:
        path = os.path.join(folder_path, name)
        if os.path.isfile(path):
            ext = os.path.splitext(name)[1].lower()
            if ext in video_ext:
                try:
                    out = convert_video_to_jpg_frames(path)
                    results.append(out)
                except Exception as e:
                    try:
                        print("转换失败: {0}, 错误: {1}".format(path, e))
                    except Exception:
                        pass
    for r in results:
        r.wait()
    return results


if __name__ == "__main__":
    # 简单命令行入口（兼容 Python 2）：仅接受视频完整路径\
    convert_all_videos_in_folder(r"D:\work\x3_ai_face\x3_face_anim")

