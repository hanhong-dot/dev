# Copyright (c) 2013 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

import os

from pyfbsdk import FBMessageBox, FBApplication, FBSystem


def bootstrap_tank():
    try:
        import tank
    except Exception as e:
        FBMessageBox(
            "ShotGrid: Error", "Could not import sgtk! Disabling for now: %s" % e, "Ok"
        )
        return

    if not "TANK_ENGINE" in os.environ:
        FBMessageBox(
            "ShotGrid: Error",
            "Missing required environment variable TANK_ENGINE.",
            "Ok",
        )
        return

    engine_name = os.environ.get("TANK_ENGINE")
    try:
        context = tank.context.deserialize(os.environ.get("TANK_CONTEXT"))
    except Exception as e:
        FBMessageBox(
            "ShotGrid: Error",
            "Could not create context! SG Pipeline Toolkit will be disabled. Details: %s"
            % e,
            "Ok",
        )
        return

    try:
        engine = tank.platform.start_engine(engine_name, context.tank, context)
    except Exception as e:
        FBMessageBox("ShotGrid: Error", "Could not start engine: %s" % e, "Ok")
        return

    # if a file was specified, load it now
    file_to_open = os.environ.get("TANK_FILE_TO_OPEN")
    if file_to_open:
        FBApplication.FileOpen(file_to_open)

    # clean up temp env vars
    for var in ["TANK_ENGINE", "TANK_CONTEXT", "TANK_FILE_TO_OPEN"]:
        if var in os.environ:
            try:
                del os.environ[var]
            except:
                pass


def add_env():
    import sys
    _root = 'Z:\\dev'
    __version = __get_mobu_version()
    if __version == 19000.0:
        _paths = ['Ide\\Python\\2.7.11\\Lib\\site-packages', 'tools\\x3_P4\\motionbuilder']
        sys.path.append(_root)
        _f_path = sys.path
        plugin_paths = [r"Z:\dev\tools\plug-ins\mobu\UnityMeshSync_MotionBuilder\MotionBuilder2019"]
        for i in range(len(_paths)):
            _path = '{}\\{}'.format(_root, _paths[i])
            if _path not in _f_path:
                sys.path.append(_path)
        for j in range(len(plugin_paths)):
            _path = plugin_paths[j]
            if _path not in _f_path:
                sys.path.append(_path)
        os.environ['MOTIONBUILDER_PLUGIN_PATH'] = plugin_paths[0]
    elif __version == 23000.0:
        _paths = ['Ide\\Python\\Python39\\Lib\\site-packages', 'tools\\x3_P4\\motionbuilder_2023']
        sys.path.append(_root)
        _f_path = sys.path
        for i in range(len(_paths)):
            _path = '{}\\{}'.format(_root, _paths[i])
            if _path not in _f_path:
                sys.path.append(_path)
        os.environ['MOTIONBUILDER_PLUGIN_PATH']=''
        # plugin_paths = [r"Z:\dev\tools\plug-ins\mobu\UnityMeshSync_MotionBuilder\MotionBuilder2023"]






def __get_mobu_version():
    return FBSystem().Version


def add_even():
    import apps.launch.motionbuilder.interface.scriptjob as mbscript
    __version = __get_mobu_version()
    if __version in [19000.0,23000.0]:
        mbscript.lod_script_jobs()


def add_x3tools():
    __version = __get_mobu_version()
    if __version == 19000.0:
        import apps.tools.motionbuilder.x3_sg_tools
        import x3_tool_entry
    elif __version ==23000.0:
        import apps.tools.motionbuilder.x3_sg_tools
        import x3_tool_entry

    # env_path = os.environ["PATH"]
    # paths = env_path.split(os.path.pathsep)
    # # Remove folders which have msvcr90.dll from the PATH
    # paths = [path for path in paths if "msvcr90.dll" not in map(
    #     str.lower, os.listdir(path))
    #          ]
    # env_path = os.path.pathsep.join(paths)
    # os.environ["PATH"] = env_path


add_env()
# add_plugin_env()
# add_plugin()
bootstrap_tank()
add_even()
add_x3tools()
# add_plugin_env()
