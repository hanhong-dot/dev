# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       : batch_process
# Describe   : 说明描述
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2024/1/3__14:37
# -------------------------------------------------------
import subprocess
import threading
import time


def batch_item_publish(file_path):
    """
    批量发布
    :param task_data:
    :return:
    """
    maya_batch = r"C:\Program Files\Autodesk\Maya2018\bin\mayabatch.exe"
    command="execfile(\"Z:/dev/apps/publish/batch_publish/batch_item_publish.py\")"


    # batch_command = u"import apps.publish.batch_publish.item_batch_publish as item_batch_publish\nreload(item_batch_publish)\nitem_batch_publish.MayaBatchCheckPublish(r'%s').batch_process()" % file_path
    command = u"python(\"{}\")".format(command)

    cmd='"{}" -file {} -command "{}"'.format(maya_batch,file_path,command)

    print cmd

    return process_run(cmd, file_path)




def batch_item_publish_run(file_path):
    import method.maya.common.file as file_common
    file_common.BaseFile().open_file(file_path)
    import sys
    sys.path.append(r'Z:\dev\database\shotgun\toolkit\x3\install\core\python')
    import apps.launch.maya.interface.maya_launch as maya_launch
    maya_launch.load_env_py2()
    import apps.publish.batch_publish.item_batch_publish as item_batch_publish
    reload(item_batch_publish)
    return item_batch_publish.MayaBatchCheckPublish(file_path).batch_process()


def process_run(commond,file_path):
    p=subprocess.Popen(commond, stdin=subprocess.PIPE).communicate(input=file_path)
    # p = subprocess.Popen(commond, stdout=subprocess.PIPE, bufsize=1)
    # output, error = p.communicate()
    #
    # return output.decode('utf-8')


def batch_item_check_publish(task_data):
    from apps.publish.batch_publish.item_batch_publish import MayaBatchCheckPublish
    return MayaBatchCheckPublish(task_data).batch_process()


def get_commond(python, py, fun=None, *args):
    commond = [python, py]
    if fun:
        commond.extend([fun])
    if args:
        for arg in args:
            commond.extend(arg)
    return commond


# if __name__ == '__main__':
#     file_path = 'E:/p/card_cream_fx_003.drama_mdl.v002.ma'
#     print batch_item_publish(file_path)
    # args  =["C:\Program Files\Autodesk\Maya2018\bin\mayabatch.exe","-command","python(\"import sys\\nsys.path.append(\\\"Z:/dev\\\")\\nimport apps.publish.batch_publish.batch_process as batch_process\\nbatch_process.batch_item_publish_run({})\")".format(file_path)]
    # subprocess_cmd = subprocess.Popen(args,stdin=subprocess.PIPE).communicate(input=file_path)
    # print(subprocess_cmd)
    # output, error = p.communicate()
    # print(output.decode('utf-8'))
    # file_path = r'E:\p\card_cream_fx_003.drama_mdl.v002.ma'
    # print batch_item_publish(file_path)
    # import sys
    #
    # sys.path.append('z:/dev')
    # sys.path.append(r'Z:\dev\database\shotgun\toolkit\x3\install\core\python')
    #
    #
    # import apps.launch.maya.interface.maya_launch as maya_launch
    #
    # maya_launch.load_env()
    # import apps.publish.batch_publish.item_batch_publish as item_batch_publish
    #
    # reload(item_batch_publish)
    # item_batch_publish.MayaBatchCheckPublish(file_path).batch_process()

    # n=batch_item_publish(file_path)
    # print(n)
