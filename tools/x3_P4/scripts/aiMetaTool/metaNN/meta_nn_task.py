import os
import subprocess
import sys


def to_str(arg):
    if isinstance(arg, (str, u"".__class__)):
        return r"'%s'" % arg.replace("\\", "/")
    return str(arg)


def run_in_maya_prompt(module, fun, *args):
    maya_paths = [r'C:\Program Files\Autodesk\Maya2018\bin\mayabatch.exe']
    maya_path = maya_paths[0]
    for _path in maya_paths:
        if os.path.isfile(_path):
            maya_path = _path

    cmd_format = r'"{maya_path}" -prompt -command "python(\"{command}\")"'
    args = ",".join(map(to_str, args))
    command = "import {module};{module}.{fun}({args});".format(module=module, fun=fun, args=args)
    cmd = cmd_format.format(command=command, maya_path=maya_path)
    popen = subprocess.Popen(cmd.encode("gbk"))
    popen.wait()


def run_one():
    path = "K:/mh_face_random/v3/meta_nn_00000_task"
    for i, k in enumerate(sys.argv):
        if k == "-path":
            path = sys.argv[i + 1]
    run_in_maya_prompt("aiMetaTool2.metaNN.random_anim", "random_anim_100", path)
    # print "run one"

if __name__ == '__main__':
    run_one()
