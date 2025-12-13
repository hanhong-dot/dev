try:
    from importlib import reload
except ImportError:
    pass


# def init_np():
#     import sys
#     path = r"L:\scripts\np_lib"
#     path.replace("\\", "/")
#     if path not in sys.path:
#         sys.path.insert(0, path)
#     import numpy as np
#
# init_np()


from . import anim_driver
from . import anim_ctrl_driver
from . import anim_solve
from . import x6_ai_67
from . import load_runtime
from . import bs
from .aiMetaExe import ai_meta_exe
from . import tools
from . import poses_rig
from . import poses_anis
from . import batchSolve
from . import face_nn_client
from . import face_anim_retarget
from . import ui
from . import poses_to_bs
from . import reCurveTool
from .convert_video import convert
reload(ai_meta_exe)
reload(anim_driver)
reload(anim_ctrl_driver)
reload(anim_solve)
reload(x6_ai_67)
reload(bs)
reload(face_nn_client)
reload(face_anim_retarget)
reload(poses_rig)
reload(poses_anis)
reload(batchSolve)
reload(poses_to_bs)
reload(load_runtime)
reload(x6_ai_67)
reload(convert)
reload(tools)
reload(reCurveTool)
reload(ui)



