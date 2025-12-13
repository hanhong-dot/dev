# coding=utf-8
import numpy as np


def gaussian_kernel(window_length, sigma=None):
    if window_length % 2 == 0:
        raise ValueError("窗口长度必须是奇数")
    if sigma is None:
        sigma = 0.3 * ((window_length - 1) * 0.5 - 1) + 0.8
    x = np.linspace(-(window_length - 1) / 2, (window_length - 1) / 2, window_length)
    kernel = np.exp(-x ** 2 / (2 * sigma ** 2))
    kernel = kernel / np.sum(kernel)
    return kernel


def smooth_with_gaussian(times, values, window_length=1, sigma=1.0):
    window_length = 1+window_length*2
    padded_values = np.pad(values, window_length, mode='reflect')
    padded_values[:window_length] = 2*values[0]-padded_values[:window_length]
    padded_values[-window_length:] = 2*values[-1]-padded_values[-window_length:]
    kernel = gaussian_kernel(window_length, sigma)
    smoothed = np.convolve(padded_values, kernel, mode='same')
    new_values = smoothed[window_length:-window_length]
    return times, new_values


def smooth_with_z_nose(times, values):
    smooth_power = 30
    g1, g2, smooth_weight = get_grad_weight(values)
    smooth_weight[g1*g2 > -1e-8] = 0
    smooth_weight = np.pad(smooth_weight, (1, 1), 'constant', constant_values=0)
    two_weight = np.zeros_like(smooth_weight)
    two_weight[smooth_weight> 1e-4] = 1
    k5 = np.convolve(two_weight, np.array([1, 1, 1, 1, 1]) / 5, mode='same')
    k3 = np.convolve(two_weight, np.array([1, 1, 1]) / 3, mode='same')
    smooth_weight[np.all([k5<0.5, k3<0.5])] = 0
    smooth_weight *= smooth_power
    smooth_weight = np.clip(smooth_weight, 0, 1)
    _, smooth_weight = smooth_with_gaussian(None, smooth_weight)
    smooth_weight = np.clip(smooth_weight*2, 0, 1)
    new_values = values.copy()
    kernel = np.array([1, 1, 1]) / 3  # 平均核
    for i in range(3):
        next_new_values =  np.convolve(new_values, kernel, mode='same')
        new_values += (next_new_values - new_values)*smooth_weight
    return times, new_values


def get_grad_weight(values):
    v0 = values[0:-2]
    v1 = values[1:-1]
    v2 = values[2:]
    g1 = v2 - v1
    g2 = v1 - v0
    smooth_weight = np.abs(g1 - g2)
    smooth_weight /= (np.max(smooth_weight) + 1e-6)
    return g1, g2, smooth_weight


def smooth_with_grad(times, values, keep_power=0.5):
    _, smooth_values = smooth_with_gaussian(None, values, 1, 1.0)
    _, _, weights = get_grad_weight(smooth_values)
    max_value = np.sort(weights)[int(len(weights)*keep_power)]
    weights /= max_value+ 1e-8
    weights = np.pad(weights, (1, 1), 'constant', constant_values=1.0)
    weights = np.clip(weights, 0, 1)
    blend_grad = values * weights + smooth_values * (1 - weights)
    return times, blend_grad


def remove_nose_and_auto_smooth(times, values):
    _, values = smooth_with_z_nose(times, values)
    for i in range(3):
        _, values = smooth_with_grad(times, values)
    return times, values

def remove_nose_and_auto_smooth2(times, values):
    _, values = smooth_with_z_nose(times, values)
    return times, values
