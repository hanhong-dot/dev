import numpy as np
import json
import os
from .anim_ctrl_driver import set_ctrl_anim


def load_json_data(name):
    with open(os.path.abspath(__file__ + "/../data/%s.json" % name), "r") as fp:
        return json.load(fp)


def nn_linear(x, data, pre):
    if pre+"weight" in data:
        x = np.matmul(x, data[pre+"weight"].T)
    if pre+"bias" in data:
        x = x + data[pre+"bias"]
    return x


def nn_layer_normal(x, data, pre):
    mean = np.mean(x, axis=-1, keepdims=True)
    var = np.var(x, axis=-1, keepdims=True)
    x = (x - mean) / np.sqrt(var + 1e-5)
    if pre+"weight" in data:
        x = x * data[pre+"weight"]
    if pre+"bias" in data:
        x = x + data[pre+"bias"]
    return x


def nn_relu(x, *args):
    x[x < 0] = 0
    return x


def nn_leaky_relu(x, *args):
    alpha = 0.01
    return np.maximum(alpha * x, x)


def run_sq_mlp_model(x, data):
    for i, fn in enumerate(data["layers"]):
        x = globals()["nn_"+fn](x, data, str(i)+".")
    return x


def load_iphone_data(path):
    lines = open(path).readlines()
    anim_data = []
    for i in range(0, len(lines), 269):
        frame_lines = lines[i:i + 270]
        if len(frame_lines) != 270:
            continue
        frame = "".join(frame_lines)
        if frame[-2] == "{":
            frame = frame[:-2]
        if frame[0] == "}":
            frame = frame[1:]
        frame_data = json.loads(frame)
        anim_data.append(frame_data)
    return anim_data


def load_iphone_data2(path):
    lines = open(path).readlines()
    anim_data = []
    frame_lines = []
    for line in lines:
        frame_lines.append(line)
        if "{" not in frame_lines[0]:
            frame_lines = []
            continue
        if "}" not in frame_lines[-1]:
            continue
        if len(frame_lines) < 2:
            continue
        data = list(frame_lines)
        if "{" in line:
            frame_lines = [line]
        else:
            frame_lines = []
        data[0] = "{"+data[0].split("{")[-1]
        data[-1] = data[-1].split("}")[0]+"}"
        data = "".join(data)
        try:
            frame_data = json.loads(data)
            anim_data.append(frame_data)
        except Exception as e:
            pass
    # print(len(anim_data))
    return anim_data


def predict_iphone_data(iphone_data, nn="aiMeta_runtime_nn"):
    keep_targets = load_json_data("ai_meta_keep_targets")
    npz_path = os.path.abspath(__file__ + "/../data/%s.npz" % nn)
    npz_data = dict(np.load(npz_path))
    use_raw_names = load_json_data("use_raw_names")
    raw_names = load_json_data("raw_names")
    use_indexes = [raw_names.index(name) for name in use_raw_names]
    use_raw_names = [name.replace("CTRL_expressions_", "") for name in use_raw_names]
    keep_ids = [use_raw_names.index(name) for name in keep_targets]
    # tran
    full_driver_data = [frame_data["ControlValues"] for frame_data in iphone_data]
    full_driver_data = np.array(full_driver_data, dtype=np.float32)
    driver_data = full_driver_data[:, use_indexes]
    max_int_16 = 65535.0
    driver_data = driver_data / max_int_16
    output_data = run_sq_mlp_model(driver_data, npz_data)
    # keep
    keep_data = driver_data[:, keep_ids]
    output_data = np.concatenate([output_data, keep_data], axis=1)
    return output_data


def load_runtime_ai_meta(iphone_data_path, st):
    iphone_data = load_iphone_data2(iphone_data_path)
    output_data = predict_iphone_data(iphone_data)
    # tongue
    raw_names = load_json_data("raw_names")
    raw_names = [name.replace("CTRL_expressions_", "") for name in raw_names]
    tongue_names = ["tongueDown", "tonguePress", "tongueTipDown", "tongueTipUp"]
    tongue_indexes = [raw_names.index(name) for name in tongue_names]
    full_driver_data = [frame_data["ControlValues"] for frame_data in iphone_data]
    full_driver_data = np.array(full_driver_data, dtype=np.float32)
    max_int_16 = 65535.0
    full_driver_data = full_driver_data / max_int_16
    tongue_data = full_driver_data[:, tongue_indexes]
    output_data = np.concatenate([output_data, tongue_data], axis=1)
    output_targets = load_json_data("ai_meta_train_targets") + load_json_data("ai_meta_keep_targets") + tongue_names
    # key frames
    key_runtime_frame(iphone_data, output_data, output_targets, load_json_data("mh_low_sdk"), st)

def key_runtime_frame(iphone_data, output_data, output_targets, sdk_data, st):
    frames = [frame_data["FrameNumber"] for frame_data in iphone_data]
    st = frames[0] - st
    frames = [frame - st for frame in frames]
    anim_curve_data = {}
    for i, target in enumerate(output_targets):
        values = output_data[:, i].tolist()
        anim_curve_data[target] = dict(frames=frames, values=values)
    set_ctrl_anim(anim_curve_data, sdk_data)


def load_runtime_arkit(iphone_data_path, st=0):
    iphone_data = load_iphone_data2(iphone_data_path)
    output_data = predict_iphone_data(iphone_data, "x6_ai_67_runtime_nn")
    output_targets = load_json_data("ai_67_train_targets") + load_json_data("ai_meta_keep_targets")
    key_runtime_frame(iphone_data, output_data, output_targets, load_json_data("arkit_sdk"), st)



def doit():
    # iphone_data_path = r"D:\work\AI_mh\x6\AI67\runtime_anim\10.10.33.91_Take_BB.json"
    iphone_data_path = r"D:\work\x3_npc_auto_55\anim\TestRecord.json"
    load_iphone_data2(iphone_data_path)
    iphone_data_path = r"D:\work\x3_npc_auto_55\anim\faceData_iphone.json"
    load_iphone_data2(iphone_data_path)

    # load_runtime_ai_meta(iphone_data_path)
    # load_runtime_arkit(iphone_data_path)

