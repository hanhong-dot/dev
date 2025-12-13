import numpy as np


def normal_weights(weights):
    sum_weights = np.sum(weights)
    if sum_weights < 1e-6:
        weights[:] = 1.0/len(weights)
    else:
        weights /= sum_weights


def solve_weight(points, point):
    n = points.shape[-1]
    weights = np.full(n, 1.0/n)
    one_weights = np.eye(n)
    for _ in range(8):
        for i in range(n):
            weights[i] = 0
            normal_weights(weights)
            zero_point = np.matmul(points, weights)
            v = points[:, i] - zero_point
            p = point - zero_point
            dot_v = np.dot(v, v)
            if dot_v < 1e-6:
                return
            w = np.dot(v, p) / dot_v
            w = np.clip(w, 0, 1)
            weights[:] =  weights * (1 - w) + one_weights[i] * w
            normal_weights(weights)
    return weights