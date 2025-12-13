from . handle_controller_curve import *
from . jitter_detector import JitterDetector





def test_smooth_attr():
    controller_attr = "CTRL_R_eye_blink.translateY"
    anim_curve_name = find_anim_curve(controller_attr)
    if anim_curve_name is None:
        return
    tc, vc = get_time_values(anim_curve_name)

    tc = np.array(tc).astype(int)
    vc = np.array(vc)
    JitterDetector.smooth_one_curve(tc, vc)


    # cleanup_controller_curve_info = JitterDetector.smooth_controller_curve(controller_curve_info)


def doit():
    test_smooth_attr()