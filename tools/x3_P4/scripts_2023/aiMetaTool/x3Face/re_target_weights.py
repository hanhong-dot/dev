import numpy as np
import os
import json
import trimesh
import glob
from scipy.optimize import lsq_linear


def load_bs(bs_path):
    cache_path = os.path.join(bs_path, "cache.npz")
    if os.path.exists(cache_path):
        data = np.load(cache_path)
        return data["base_points"], data["target_points"], data["target_names"]
    obj_paths = glob.glob(os.path.join(bs_path, "*.obj"))
    data = {}
    for obj_path in obj_paths:
        obj = trimesh.load(obj_path, merge_norm=True, merge_tex=True)
        vertices = np.array(obj.vertices)
        name = os.path.basename(obj_path)[:-4]
        data[name] = vertices
    base_points = data.pop("base")
    target_names = sorted(data.keys())
    target_points = np.array([data[name] for name in target_names])
    base_points = base_points.reshape(-1)
    target_points = target_points.reshape(len(target_names), -1)
    target_points -= base_points

    np.savez(cache_path, base_points=base_points, target_points=target_points, target_names=target_names)
    return base_points, target_points, target_names

def load_weights(path, names=None):
    data = json.load(open(path))
    if names is None:
        names = sorted(data[0].keys())
    weights = [[row.get(n, 0) for n in names] for row in data]
    return np.array(weights, dtype=np.float32)

class Bs(object):

    def __init__(self, bs_path):
        self.base, self.target_points, self.target_names = load_bs(bs_path)

    def get_points_ani(self, weights_ani):
        return weights_ani@self.target_points+self.base

    def get_points_ani_by_path(self, path):
        weights_ani = load_weights(path, self.target_names)
        return self.get_points_ani(weights_ani)

    def mask_targets(self, mask):
        n_targets = len(self.target_names)
        target_points = self.target_points.reshape(n_targets, -1, 3)
        target_points *= mask[None, :, None]
        self.target_points = target_points.reshape(n_targets, -1)


    def get_weights_ani(self, points_ani):
        points_ani = points_ani - self.base
        n_frames = points_ani.shape[0]
        weights = []
        for i in range(n_frames):
            res = lsq_linear(self.target_points.T, points_ani[i], bounds=(0, 1))
            weights.append(res.x)
        weights = np.array(weights)
        weights[weights < 1e-5] = 0
        return weights

    def get_weights_ani_v2(self, points_ani):
        weights = self.get_weights_ani(points_ani)
        weights[weights<0.1] = 0.0
        base_weights = 1-weights.max(axis=1, keepdims=True)
        weights = np.concatenate((weights, base_weights), axis=1)
        weights /= weights.sum(axis=1, keepdims=True)
        smooth_weights(weights)
        weights /= weights.sum(axis=1, keepdims=True)
        return np.array(weights)

    def get_weights_ani_v3(self, points_ani):
        from linear_regression import solve_weight
        points_ani = points_ani - self.base
        value_count = self.target_points.shape[1]
        points = np.concatenate([self.target_points, np.zeros((1, value_count))], axis=0).T
        weights = []
        for p in points_ani:
            weights.append(solve_weight(points, p))
        weights = np.array(weights)
        return weights[:, :-1]


    def save_weight_dict(self, weights, path):
        data = [dict(zip(self.target_names, ws.tolist()))for ws in weights]
        dir_path = os.path.dirname(path)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        with open(path, "w") as f:
            json.dump(data, f, indent=4)


def convert_face_to_rom():
    convert_weight_dict(
        r"D:\work\x3_ai_face\st_faces",
        r"D:\work\x3_ai_face\st_aiMeta_55",
        r"D:\work\x3_ai_face\test_face_anim\face5",
        r"D:\work\x3_ai_face\test_face_anim\rom55",
    )


def random_weights(frame_count=1024, face_count=5):
    weights = np.random.random((frame_count, face_count+1))
    row_ids = np.arange(frame_count)
    for i in range(face_count+1):
        zero_id = np.random.randint(0, face_count + 1, size=frame_count)
        weights[row_ids, zero_id] = 0
    norm = np.sum(weights, axis=1, keepdims=True)
    norm[norm<1e-6] = 1
    weights /= norm
    weights = weights[:, :face_count]
    return weights

def random_data(src_bs, dst_bs, data_dir):
    src = Bs(src_bs)
    dst = Bs(dst_bs)
    for i in range(512):
        src_weights = random_weights(1024, len(src.target_names))
        points_ani = src.get_points_ani(src_weights)
        dst_weights = dst.get_weights_ani(points_ani)
        path = os.path.join(data_dir, "random_%03d.npz" % i)
        np.savez(path, src_weights=src_weights, dst_weights=dst_weights)


def random_face_to_rom():
    random_data(
        r"D:\work\x3_ai_face\st_faces",
        r"D:\work\x3_ai_face\st_aiMeta_55",
        r"D:\work\x3_ai_face\random_face_to_rom"
    )

def convert_rom_to_face():
    convert_weight_dict(
        r"D:\work\x3_ai_face\x3_face_to_xinghuo\objs\rom55",
        r"D:\work\x3_ai_face\x3_face_to_xinghuo\objs\face5",
        r"D:\work\x3_ai_face\x3_face_to_xinghuo\rom55_to_face5\rom55",
        r"D:\work\x3_ai_face\x3_face_to_xinghuo\rom55_to_face5\face5",
    )


def convert_weight_dict(src_bs, dst_bs, src_weight, dst_weight):
    src = Bs(src_bs)
    dst = Bs(dst_bs)
    for path in glob.glob(os.path.join(src_weight, "*.json")):
        points_ani = src.get_points_ani_by_path(path)
        new_weights = dst.get_weights_ani(points_ani)
        new_path = os.path.join(dst_weight, os.path.basename(path))
        dst.save_weight_dict(new_weights, new_path)

def get_limit_data():
    limit_data = r"D:/work/x3_ai_face/x3_face_to_xinghuo/face5_to_rom55_tranData"
    save_path = r"D:/work/x3_ai_face/x3_face_to_xinghuo/max_rom55.npy"
    max_value = []
    for path in glob.glob(os.path.join(limit_data, "*.npz")):
        data = np.load(path)
        max_value.append(data["dst_weights"].max(axis=0))
    max_value = np.array(max_value).max(axis=0)
    np.save(save_path, max_value)
    return max_value

def get_remove_targets():
    return ['eyeBlinkL', 'eyeBlinkR', 'eyeLookDownL', 'eyeLookDownR', 'eyeLookLeftL','eyeLookLeftR', 'eyeLookRightL',
            'eyeLookRightR', 'eyeLookUpL', 'eyeLookUpR','eyeWidenL', 'eyeWidenR']

def convert_rom_to_face_v2():
    src_bs = r"D:\work\x3_ai_face\x3_face_to_xinghuo\objs\rom55"
    dst_bs = r"D:\work\x3_ai_face\x3_face_to_xinghuo\objs\face5"
    src_weight = r"D:\work\x3_ai_face\x3_face_to_xinghuo\iphone_anim\rom55"
    dst_weight = r"D:\work\x3_ai_face\x3_face_to_xinghuo\iphone_anim\face_v2"
    # src_weight = r"D:\work\x3_ai_face\x3_face_to_xinghuo\rom55_to_face5\rom55"
    # dst_weight = r"D:\work\x3_ai_face\x3_face_to_xinghuo\rom55_to_face5\face5_v4"

    limit_weight =  np.load(r"D:/work/x3_ai_face/x3_face_to_xinghuo/max_rom55.npy")

    src = Bs(src_bs)
    dst = Bs(dst_bs)
    mask = np.array(json.load(open(r"L:\scripts\aiMetaTool2\x3Face\wts.json")))
    src.mask_targets(mask)
    dst.mask_targets(mask)
    target_names = src.target_names.tolist()
    zero_ids = [target_names.index(target) for target in get_remove_targets()]
    for path in glob.glob(os.path.join(src_weight, "*.json")):
        weights = load_weights(path, src.target_names)
        weights[weights < 1e-5] = 0
        weights[:, zero_ids] = 0
        weights = np.clip(weights, 0, limit_weight[None, :])
        points_ani = src.get_points_ani(weights)
        # src.save_weight_dict(weights, os.path.join(limit_weight, os.path.basename(path)))
        # new_weights = dst.get_weights_ani(points_ani)
        new_weights = dst.get_weights_ani_v3(points_ani)
        dst.save_weight_dict(new_weights, os.path.join(dst_weight, os.path.basename(path)))

def doit():
    # random_face_to_rom()
    convert_rom_to_face_v2()
    # get_limit_data()


def smooth_weights(weights):
    from smooth_compute_core import smooth_with_gaussian, smooth_with_z_nose
    frames = np.arange(0, len(weights), 1)
    for i in range(weights.shape[1]):
        values = weights[:, i]
        _, values = smooth_with_z_nose(frames, values)
        _, values = smooth_with_gaussian(frames, values, window_length=5, sigma=5)
        weights[:, i] = values


if __name__ == '__main__':
    doit()