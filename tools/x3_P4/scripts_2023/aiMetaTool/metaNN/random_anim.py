import os.path
import random
import shutil
from maya.api.OpenMayaAnim import *
from ..anim_solve import *
from ..x6_ai_67 import *
from .config import load_json_data


def solve_mh_low(path):
    path = os.path.splitext(os.path.splitext(path)[0])[0]
    exe_path = os.path.abspath(__file__+"/../../aiMetaExe")
    temp_exe_path = os.path.join(path+"_script", "temp_aiMetaExe").replace("\\", "//")
    if not os.path.isdir(temp_exe_path):
        os.makedirs(temp_exe_path)
    if os.path.isdir(temp_exe_path):
        shutil.rmtree(temp_exe_path)
    shutil.copytree(exe_path, temp_exe_path)
    temp_script = os.path.dirname(temp_exe_path)
    if temp_script not in sys.path:
        sys.path.insert(0, temp_script)
    import temp_aiMetaExe.ai_meta_exe as temp_exe
    clear_orig_detail()
    export_base_anis(path)
    convert_base_anim(path, convert_low_data)
    sub = temp_exe.solve_mh_low(path)
    sub.wait()
    convert_tongue_data(path)
    os.remove(path+".json")
    # os.remove(path+".npy")
    os.remove(path+"_base.json")
    rename_file(path+"_ai_result.json", path+"_aiMeta.json")
    try:
        shutil.rmtree(temp_script)
    except:
        pass


def solve_ai_67(path):
    path = os.path.splitext(os.path.splitext(path)[0])[0]
    exe_path = os.path.abspath(__file__+"/../../aiMetaExe")
    temp_exe_path = os.path.join(path+"_script", "temp_aiMetaExe").replace("\\", "//")
    if not os.path.isdir(temp_exe_path):
        os.makedirs(temp_exe_path)
    if os.path.isdir(temp_exe_path):
        shutil.rmtree(temp_exe_path)
    shutil.copytree(exe_path, temp_exe_path)
    temp_script = os.path.dirname(temp_exe_path)
    if temp_script not in sys.path:
        sys.path.insert(0, temp_script)
    import temp_aiMetaExe.ai_meta_exe as temp_exe

    clear_orig_detail()
    export_base_anis(path)
    convert_base_anim(path, convert_x6_data)

    sub = temp_exe.solve_x6_52_bs(path)
    sub.wait()
    rename_file(path+"_ai_result.json", path+"_arkit.json")

    sub = temp_exe.solve_x6_67_bs(path)
    sub.wait()
    convert_ai_67_data(path)

    try:
        shutil.rmtree(temp_script)
    except:
        pass


def random_anim_values(use_range):
    driver_count = len(use_range)
    values = np.array([random.uniform(r[0], r[1]) for r in use_range])
    for i in range(driver_count//5):
        index = random.randint(0, driver_count - 1)
        values[index] = use_range[index][random.randint(0, 1)]
    for rate in [1.0, 0.7, 0.4, 0.1]:
        for i in range(int(driver_count*0.6)):
            values[random.randint(0, driver_count-1)] *= random.uniform(0.0, rate)
    return values


def get_anim_curve(attr):
    node, at = attr.split(".")
    cmds.setKeyframe(node, at=at, t=0, v=0)
    typs = ["animCurveTA", "animCurveTU", "animCurveTL"]
    anim_curves = cmds.listConnections(attr, s=1, d=0)
    if not anim_curves:
        return ""
    anim_curve = anim_curves[0]
    if cmds.nodeType(anim_curve) not in typs:
        return ""
    return anim_curve


def api_ls(*names):
    selection_list = MSelectionList()
    for name in names:
        selection_list.add(name)
    return selection_list


def set_attr_anis(attr, frames, values):
    if not cmds.objExists(attr):
        return
    anim_curve = get_anim_curve(attr)
    if not anim_curve:
        return
    mel.eval('cutKey -clear -time ":" '+attr)
    node, at = attr.split(".")
    cmds.setKeyframe(node, at=at, t=frames[0], v=values[0])
    anim_curve = MFnAnimCurve(api_ls(attr).getPlug(0))
    fps = MTime.uiUnit()
    offset = 0
    times = [MTime(f+offset, fps) for f in frames]
    anim_curve.addKeys(times, values)


def random_anim_100(path):
    time_count = 256
    open_scene()
    path = os.path.splitext(os.path.splitext(path)[0])[0]
    gui_names = load_json_data("gui_names")
    use_gui_names = load_json_data("use_gui_names")
    gui_ranges = load_json_data("gui_ranges")
    use_raw_names = load_json_data("use_raw_names")
    use_range = [gui_ranges[gui_names.index(name)] for name in use_gui_names]
    cmds.currentUnit(time="30fps")
    cmds.playbackOptions(min=1, ast=1, max=time_count, aet=time_count)
    gui_anim = np.array([random_anim_values(use_range) for _ in range(time_count)])
    frames = list([i + 1 for i in range(time_count)])
    for i, name in enumerate(use_gui_names):
        set_attr_anis(name, frames, gui_anim[:, i].tolist())
    raw_anim = []
    ctrl_exp_names = [name.replace("CTRL_expressions_", "CTRL_expressions.") for name in use_raw_names]
    for i in range(time_count):
        cmds.currentTime(i+1)
        raw_values = [cmds.getAttr(name) for name in ctrl_exp_names]
        raw_anim.append(raw_values)
    gui_anim = np.array(gui_anim, dtype=np.float32)
    raw_anim = np.array(raw_anim, dtype=np.float32)
    np.save(path + "_gui_anim.npy", gui_anim)
    np.save(path + "_raw_anim.npy", raw_anim)
    solve_ai_67(path)
    cmds.quit(f=1)


def open_scene():
    plug = os.path.abspath(__file__+"/../embeddedRL4.mll").replace("\\", "/")
    if not cmds.pluginInfo("embeddedRL4.mll", q=1, l=1):
        cmds.loadPlugin(plug)
    from ..batchSolve.solve_anim_all import open_myles
    open_myles()


def doit():
    # open_scene()
    random_anim_100('K:/mh_face_random/v2/random_102')
