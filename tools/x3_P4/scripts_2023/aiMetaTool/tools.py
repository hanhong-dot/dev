from . import anim_driver
from . import anim_ctrl_driver
from . import anim_solve
from .bs import connect_driver_bs
from .batchSolve.solve_anim_all import solve_all_bs_anim
from .batchSolve.play_anim_all import load_all_bs_anim
from .batchSolve.solve_ai_speak import batch_convert_speak, load_ai_speak_ue_ctrl_anim
from .face_nn_client import seed_to_server_tran
from . import face_anim_retarget
from .poses_to_bs import ai_meta_convert_blend_shape
from . import load_runtime
from . import x6_ai_67

action_config = dict(
    arkit=dict(
        solve_anim=anim_solve.arkit_solve,
        pose_driver=anim_driver.x6_poses_to_driver,
        load_anim=anim_ctrl_driver.load_x6_anim,
        export_anim=face_anim_retarget.export_arkit_anim,
        convert_bs=ai_meta_convert_blend_shape,
        load_runtime=load_runtime.load_runtime_arkit,
    ),
    x6ai67=dict(
        solve_anim=x6_ai_67.x6_ai_67_solve,
        pose_driver=anim_driver.x6_poses_to_driver,
        load_anim=x6_ai_67.load_ai_67_anim,
        export_anim=face_anim_retarget.export_arkit_anim,
        convert_bs=ai_meta_convert_blend_shape,
        load_runtime=x6_ai_67.load_runtime_ai_67,
    ),
    aiMeta=dict(
        solve_anim=anim_solve.solve_mh_low,
        pose_driver=anim_ctrl_driver.x3_55_poses_to_driver,
        load_anim=anim_ctrl_driver.load_mh_low_ctrl_anim,
        export_anim=face_anim_retarget.export_ai_meta_anim,
        convert_bs=ai_meta_convert_blend_shape,
        load_runtime=load_runtime.load_runtime_ai_meta,
    )
)