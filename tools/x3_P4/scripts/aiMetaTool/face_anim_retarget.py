import math
import numpy as np
from .anim_driver import *


def get_arkit_targets():
    return sorted(read_text_targets("arkit_targets"))


def get_ai_meta_targets():
    return sorted([t for t in read_text_targets("mh_low_targets") if "_" not in t])


def is_target_attr(attr):
    if cmds.getAttr(attr, type=1) != "double":
        return False
    return True


def get_arkit_target_attrs(ani_ns):
    ctrl = ani_ns[:-1]+"_ctrl:QMeta_expressions"
    if not cmds.objExists(ctrl):
        return []
    return [ctrl+"." + target for target in get_arkit_targets()]


def get_ai_meta_target_attrs(ani_ns):
    ctrl = ani_ns[:-1]+"_ctrl:QMeta_expressions"
    if not cmds.objExists(ctrl):
        return []
    return [ctrl+"." + target for target in get_ai_meta_targets()]


def get_target_attrs(ctrl):
    attrs = cmds.listAttr(ctrl, ud=1)
    attrs = [ctrl+"."+attr for attr in attrs]
    attrs = list(sorted(filter(is_target_attr, attrs)))
    return attrs


def get_range():
    st = int(round(cmds.playbackOptions(q=1, min=1)))
    et = int(round(cmds.playbackOptions(q=1, max=1)))
    return st, et


def filter_data_1000(data, min_dis):
    data_length = len(data)
    near_matrix = np.linalg.norm(data[:, None] - data, axis=2) < min_dis
    mask = np.ones(data_length, dtype=bool)
    for i in np.random.permutation(data_length):
        if not mask[i]:
            continue
        mask[near_matrix[i]] = False
        mask[i] = True
    return np.arange(data_length)[mask]


def filter_data(data, min_dis=0.2):
    data_length = len(data)
    masks = []
    for i in range(0, data_length, 1000):
        cut_data = data[i: i+1000]
        masks.append(filter_data_1000(cut_data, min_dis)+i)
    mask = np.concatenate(masks)
    mask = mask[filter_data_1000(data[mask], min_dis)]
    return mask


def get_short_name(attr):
    if attr.count(".") != 1:
        return attr
    node, attr = attr.split(".")
    short_name = cmds.attributeQuery(attr, node=node, shortName=True)
    return node+"."+short_name


def export_anim_data(ani_ns, ctrl_set, target_attrs, path):
    ctrl_attrs = list(sorted(get_attrs_by_set(ctrl_set)))
    ctrl_attrs = [ani_ns+attr.split(":")[-1] for attr in ctrl_attrs]
    ctrl_attrs = [attr for attr in ctrl_attrs if cmds.objExists(attr)]
    ctrl_attrs = [get_short_name(attr) for attr in ctrl_attrs]
    ctrl_attrs = list(sorted(ctrl_attrs))
    st, et = get_range()
    target_values, ctrl_values = [], []
    for i in range(st, et+1):
        cmds.currentTime(i)
        target_values.append(np.array([cmds.getAttr(attr) for attr in target_attrs], dtype=np.float32))
        ctrl_values.append(np.array([cmds.getAttr(attr) for attr in ctrl_attrs], dtype=np.float32))
    target_values = np.array(target_values, dtype=np.float32)
    ctrl_values = np.array(ctrl_values, dtype=np.float32)

    target_attrs = [attr.split(".")[-1] for attr in target_attrs]
    # clear attr

    anim_attr_ids = (np.max(ctrl_values, axis=0) - np.min(ctrl_values, axis=0)) > 1e-4
    anim_attr_ids = np.arange(anim_attr_ids.shape[0])[anim_attr_ids]
    ctrl_values = ctrl_values[:, anim_attr_ids]
    ctrl_attrs = [ctrl_attrs[i] for i in anim_attr_ids]
    # clear frames
    frame_ids = filter_data(target_values, 0.11)
    ctrl_values = ctrl_values[frame_ids]
    target_values = target_values[frame_ids]
    # re rotate
    for i, attr in enumerate(ctrl_attrs):
        if cmds.getAttr(attr, type=1) == "doubleAngle":
            ctrl_values[:, i] = ctrl_values[:, i] / 180.0 * math.pi
    # remove ns
    ctrl_attrs = [attr.split(":")[-1] for attr in ctrl_attrs]
    np.savez(
        path,
        target_values=target_values,
        target_attrs=target_attrs,
        ctrl_values=ctrl_values,
        ctrl_attrs=ctrl_attrs,
    )


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


def run_npz_model(x, data):
    lx = nn_linear(x, data, "")
    for i, fn in enumerate(data["layers"]):
        x = globals()["nn_"+fn](x, data, str(i)+".")
    return lx + x


def load_anim_data(nn_path, anim_path, ani_ns):
    print(nn_path)
    data = np.load(nn_path)
    ctrl_attrs = data["ctrl_attrs"]
    target_attrs = data["target_attrs"]
    bs_weights = json.load(open(anim_path))
    bs_weights = [[f.get(t, 0) for t in target_attrs] for f in bs_weights]
    bs_weights = np.array(bs_weights, dtype=np.float32)
    anim_values = run_npz_model(bs_weights, data)
    set_np_anim(anim_values, ctrl_attrs, ani_ns)


def set_np_anim(anim_values, ctrl_attrs, ani_ns):
    frames = (np.arange(len(anim_values))+1).tolist()
    for i, attr in enumerate(ctrl_attrs):
        attr = ani_ns+attr
        values = anim_values[:, i]
        if not cmds.objExists(attr):
            continue
        if attr.split(".")[-1] in ["scaleX", "scaleY", "scaleZ"]:
            values[np.abs(values-1.0) < 0.0001] = 1.0
        else:
            values[np.abs(values) < 0.0001] = 0.0
        set_attr_anis(attr, frames, values.tolist())


def get_bs_anim_data(data):
    anim_curve_data = {}
    for t, row in enumerate(data):
        for target, w in row.items():
            fvs = anim_curve_data.setdefault(target, dict(frames=[], values=[]))
            fvs["frames"].append(t+1)
            fvs["values"].append(w)


def export_arkit_anim(ani_ns, ctrl_set, path):
    target_attrs = get_arkit_target_attrs(ani_ns)
    export_anim_data(ani_ns, ctrl_set, target_attrs, path)


def export_ai_meta_anim(ani_ns, ctrl_set, path):
    target_attrs = get_ai_meta_target_attrs(ani_ns)
    export_anim_data(ani_ns, ctrl_set, target_attrs, path)


# def set_base_random_anim(targets, sdk_data):
#     anim_data = np.eye(len(targets))
#     anim_curve_data = {}
#     frames = (np.arange(len(anim_data)) + 1).tolist()
#     for target, values in zip(targets, anim_data.T):
#         anim_curve_data[target] = dict(frames=frames, values=values.tolist())
#     set_ctrl_anim(anim_curve_data, sdk_data)


# def export_arkit_base(ani_ns, ctrl_set, path):
#     targets = get_arkit_targets()
#     sdk_data = load_json_data("arkit_sdk")
#     set_base_random_anim(targets, sdk_data)
#     target_attrs = get_arkit_target_attrs(ani_ns)
#     export_anim_data(ani_ns, ctrl_set, target_attrs, path)


def _save_base_anim(targets, name):
    anim_data = np.eye(len(targets))
    data = []
    for values in anim_data:
        data.append({target: float(value) for target, value in zip(targets, values)})
    path = os.path.abspath(__file__+"/../data/base_poses/"+name+".json")
    with open(path, "w") as fp:
        json.dump(data, fp)


def save_base_anim():
    _save_base_anim(get_arkit_targets(), "arkit_base_poses")
    _save_base_anim(get_arkit_targets(), "aiMeta_base_poses")


def test_export_anim():
    path = r"D:\work\AI_mh\x6\x6_nikki_ai_data\lb_rom.npz"
    export_arkit_anim("Nikki1:", "face_set", path)


def test_load_anim():
    nn_path = r"D:\work\AI_mh\x6\x6_nikki_ai_data\npz\result\ai_result_nn.npz"
    anim_path = r"D:\work\AI_mh\x6\x6_nikki_ai_data\ANI_LABIN_ai_result.json"
    anim_path = r"C:\Users\mengya\Documents\maya\scripts\lushTools\aiMetaTool\data\base_poses\arkit_base_poses.json"
    load_anim_data(nn_path, anim_path, "Nikki:")


def doit():
    test_load_anim()
    # test_export_anim()
    # test_load_anim()
    # print("test_load_anim")
    # path = "D:/work/AI_mh/x6/re_data_v14.npz"
    # export_anim_data("Nikki1:", "face_set", path)
