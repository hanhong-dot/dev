import os
import json
import pprint
import subprocess

import numpy as np


def load_default_config():
    path = os.path.abspath(__file__+"/../config/config_default.json").replace("\\", "/")
    with open(path, "r") as fp:
        data = json.load(fp)
    return data


def run_exe_by_config(config):
    exe_path = os.path.abspath(__file__+"/../mh_bs_tool_json.exe").replace("\\", "/")
    config_path = os.path.abspath(__file__+"/../config/config_mutex_bs_10_28.json").replace("\\", "/")
    with open(config_path, "w") as fp:
        json.dump(config, fp, indent=4)
    pprint.pprint(config)
    os.chdir(os.path.dirname(exe_path))
    sub = subprocess.Popen(exe_path, cwd=os.path.dirname(exe_path), shell=False)
    return sub


def repair_plane_dir(target_dir, weight_dir, repair_anim_dir):
    config = load_default_config()
    config["bs_path"] = target_dir.replace("\\", "/")
    config["anim_json"] = weight_dir.replace("\\", "/")
    config["anim_obj"] = repair_anim_dir.replace("\\", "/")
    config["task"] = "fix"
    target_names = []
    for target_name in os.listdir(target_dir):
        if not target_name.endswith(".obj"):
            continue
        target_names.append(target_name[:-4])
    if "base" in target_names:
        target_names.remove("base")
    full_target_path = os.path.abspath(__file__+"/../full_targets.json").replace("\\", "/")
    with open(full_target_path, "w") as fp:
        json.dump(target_names, fp)
    config["bs_name"] = full_target_path
    return run_exe_by_config(config)


def get_target_names(bs_path):
    names = []
    for name in os.listdir(bs_path):
        if not name.endswith(".obj"):
            continue
        name = name.replace(".obj", "")
        if name == "base":
            continue
        names.append(name)
    return names


def re_bs_name_by_bs_path(config):
    names = get_target_names(config["bs_path"])
    with open(config["bs_name"], "w") as fp:
        json.dump(names, fp, indent=4)


def solve_x6_52_bs(base_path):
    base_path = os.path.splitext(base_path)[0].replace("\\", "/")
    config = load_default_config()
    config["bs_path"] = os.path.abspath(__file__+"/../config/data/x6_52/targets").replace("\\", "/")
    config["bs_name"] = os.path.abspath(__file__+"/../config/data/x6_52/bs_name.json").replace("\\", "/")
    config["bs_mutex"] = os.path.abspath(__file__+"/../config/data/x6_52/bs_mutex.json").replace("\\", "/")
    config["anim_obj"] = base_path+".npy"
    config["anim_json"] = base_path+".json"
    config["out_bs_path"] = base_path+"_ai_result.json"
    config["task"] = "fit_part"
    config["vert_mask"] = os.path.abspath(__file__+"/../config/data/lip_mask.json").replace("\\", "/")
    re_bs_name_by_bs_path(config)
    vary_range_targets = ["mouthLeft", "mouthRight", "mouthLowerLipBite", "mouthUpperLipBite", "mouthPress"]
    config["vary_range"] = {name: [2.0, 0.001] for name in vary_range_targets}
    return run_exe_by_config(config)


def solve_x6_67_bs(base_path):
    base_path = os.path.splitext(base_path)[0].replace("\\", "/")
    config = load_default_config()
    config["bs_path"] = os.path.abspath(__file__+"/../config/data/x6_67/targets").replace("\\", "/")
    config["bs_name"] = os.path.abspath(__file__+"/../config/data/x6_67/bs_name.json").replace("\\", "/")
    config["bs_mutex"] = os.path.abspath(__file__+"/../config/data/x6_67/bs_mutex.json").replace("\\", "/")
    config["anim_obj"] = base_path+".npy"
    config["anim_json"] = base_path+".json"
    config["out_bs_path"] = base_path+"_ai_result.json"
    config["task"] = "fit_part"
    config["vert_mask"] = os.path.abspath(__file__+"/../config/data/lip_mask.json").replace("\\", "/")
    re_bs_name_by_bs_path(config)
    vary_range_targets = ["mouthLeft", "mouthRight", "mouthLowerLipBite", "mouthUpperLipBite", "mouthPress"]
    config["vary_range"] = {name: [2.0, 0.001] for name in vary_range_targets}
    return run_exe_by_config(config)


def solve_x3_91_bs(base_path):
    base_path = os.path.splitext(base_path)[0].replace("\\", "/")
    config = load_default_config()
    config["bs_path"] = os.path.abspath(__file__+"/../config/data/x3_91/targets").replace("\\", "/")
    config["bs_name"] = os.path.abspath(__file__+"/../config/data/x3_91/bs_name.json").replace("\\", "/")
    config["bs_mutex"] = os.path.abspath(__file__+"/../config/data/x3_91/bs_mutex.json").replace("\\", "/")
    config["anim_obj"] = base_path+".npy"
    config["anim_json"] = base_path+".json"
    config["out_bs_path"] = base_path+"_ai_result.json"
    config["task"] = "fit_part"
    config["vert_mask"] = os.path.abspath(__file__+"/../config/data/lip_mask.json").replace("\\", "/")
    return run_exe_by_config(config)


def test_solve_x6_52_bs():
    base_path = r"D:\work\AI_mh\x6\ai_result\lb_rom_v1.npy"
    solve_x6_52_bs(base_path)


def test_solve_x3_91_bs():
    base_path = r"D:\work\AI_mh\x3\ue_result_ani\myles_think.json"
    solve_x3_91_bs(base_path)


def solve_mh_low(base_path):
    base_path = os.path.splitext(base_path)[0].replace("\\", "/")
    config = load_default_config()
    config["bs_path"] = os.path.abspath(__file__+"/../config/data/low/targets").replace("\\", "/")
    config["bs_name"] = os.path.abspath(__file__+"/../config/data/low/bs_name.json").replace("\\", "/")
    config["bs_mutex"] = os.path.abspath(__file__+"/../config/data/low/bs_mutex.json").replace("\\", "/")
    config["anim_obj"] = base_path+".npy"
    config["anim_json"] = base_path+".json"
    config["out_bs_path"] = base_path+"_ai_result.json"
    config["task"] = "fit_part"
    config["vert_mask"] = os.path.abspath(__file__+"/../config/data/lip_mask.json").replace("\\", "/")
    vary_range_targets = ["mouthLeft", "mouthRight", "mouthLowerLipBite", "mouthUpperLipBite"]
    config["vary_range"] = {name: [2.0, 0.001] for name in vary_range_targets}
    re_bs_name_by_bs_path(config)
    return run_exe_by_config(config)


def solve_max_ctrl(base_path):
    base_path = os.path.splitext(base_path)[0].replace("\\", "/")
    config = load_default_config()
    config["bs_path"] = os.path.join(base_path, "targets").replace("\\", "/")
    config["bs_name"] = os.path.join(base_path, "bs_name.json").replace("\\", "/")
    config["bs_mutex"] = os.path.join(base_path, "bs_mutex.json").replace("\\", "/")
    config["vert_mask"] = os.path.join(base_path, "vert_mask.json").replace("\\", "/")
    config["anim_obj"] = os.path.join(base_path, "anim.npy").replace("\\", "/")
    config["anim_json"] = os.path.join(base_path, "anim.json").replace("\\", "/")
    config["out_bs_path"] = os.path.join(base_path, "ai_result.json").replace("\\", "/")
    config["task"] = "fit_part"
    config["vary_range"] = {}
    config["vert_mask_w"] = [1, 1.5, 0.7]
    re_bs_name_by_bs_path(config)
    targets = get_target_names(config["bs_path"])
    bs_mutex_data = {}
    for target in targets:
        bs_mutex_data.setdefault(target[:-4], []).append(target)
    bs_mutex_data = [v for v in bs_mutex_data.values() if len(v) == 2]
    with open(config["bs_mutex"], "w") as fp:
        json.dump(bs_mutex_data, fp)

    data = np.load(config["anim_obj"])
    frame_count, vtx_count, _ = data.shape
    vert_mask = [0.0] * vtx_count
    with open(config["vert_mask"], "w") as fp:
        json.dump(vert_mask, fp)

    anim_info = dict(
        keep_weight_anis=[{} for _ in range(frame_count)],
        orig_weight_anis=[{target: 0.001 for target in targets} for _ in range(frame_count)],
    )
    with open(config["anim_json"], "w") as fp:
        json.dump(anim_info, fp)
    return run_exe_by_config(config).wait()


def save_solve_obj():
    pass


def test():
    # solve_max_ctrl("D:/work/AI_mh/n4/max_objs")
    pass

if __name__ == '__main__':
    test()
