# -*- coding: utf-8 -*-

import subprocess
import os

PYTHONPATH = r"C:\Program Files\Autodesk\Maya2018\bin\mayapy.exe"
LOCAL_PYTHON_PATH = r"z:\dev"


CREATE_NO_WINDOW = 0x08000000

def run_process_cover_to_maya2018(json_path):
    py = r"z:\dev\apps\tools\motionbuilder\cover_mb_to_maya\batch_cover_maya.py"
    cmd = [PYTHONPATH, py, json_path]

    print("[MAYAPY CALL] ", cmd)

    # 强制隐藏窗口
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    startupinfo.wShowWindow = 0  # SW_HIDE

    try:
        p = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=False,
            startupinfo=startupinfo,
            creationflags=CREATE_NO_WINDOW
        )
        out_bytes, err_bytes = p.communicate()
        ret = p.returncode

    except Exception as e:
        print("========== ERROR DETAILS ==========")
        print("TYPE:", type(e))
        print("MSG :", str(e))
        print("===================================")
        raise

    stdout = out_bytes.decode("utf-8", "replace")
    stderr = err_bytes.decode("utf-8", "replace")

    if ret != 0:
        raise Exception(
            u"mayapy 执行失败: {}\nstdout:\n{}\nstderr:\n{}".format(
                ret, stdout, stderr
            )
        )

    return stdout.strip()


# if __name__ == '__main__':
#     json_path = r'D:\Info_Temp\mobu\cover_mb_to_maya\output\data\DC_B_ML_C1S1_S01_P01_Act_Other_Award_01+1.json'
#     run_process_cover_to_maya2018(json_path)
