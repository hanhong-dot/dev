import glob
import os
import shutil

path = "K:/mh_face_random/v1"

def copy_data():
    src = "K:/mh_face_random/v1"
    dst = r"D:/work/x3_ai_face/x3_face_to_xinghuo/rom55_to_face5\rom55"
    for src_path in glob.glob(os.path.join(src, "*_task_aiMeta.json")):
        dst_path = os.path.join(dst, os.path.basename(src_path))
        if not os.path.exists(dst_path):
            shutil.copyfile(src_path, dst_path)


if __name__ == '__main__':
    copy_data()
