# -*- coding: utf-8 -*-#
# Python     :
# -------------------------------------------------------
# NAME       :
# Describe   :
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2025/03/044 11:50
# -------------------------------------------------------
import sys

def main(*args):
    if not args:
        print('error,not input args,please check')
        return
    return process_cover_to_maya2018(args[0][0], args[0][1])


def process_cover_to_maya2018(source_path, targe_path):
    import sys

    LAUNCHPATH = 'Z:/dev'
    sys.path.append(LAUNCHPATH)
    from apps.tools.maya.sub_animation_cover import cover_maya_2018
    import apps.launch.maya.interface.maya_launch as maya_launch
    maya_launch.launch('batch')
    return cover_maya_2018.cover_animation(source_path, targe_path)


def run():
    data = main(sys.argv[1:])
    data = '{}'.format(data)
    print(data)
    return data


if __name__ == '__main__':
    run()
