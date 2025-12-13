# vim:ts=4:sw=4:expandtab
# -*- coding: utf-8 -*-
# @brief
# @author huangsheng@papegames.net
# @version v1.0.0
# @file: jitter_detector.py
# @time: 2025/8/21 18:02


import numpy as np
from .merge_utils import IntervalOperator
from .preprocess import PreprocessGap, PreprocessCurve

UNIT = 100
EPS = 1e-8


def calc_vel_acc(marker_pos):
    vel = marker_pos[1:] - marker_pos[:-1]  # N-1 x 3
    left_vel = np.concatenate([vel[:1], vel], axis=0)  # N x 3, left derivation
    right_vel = np.concatenate([vel, vel[-1:]], axis=0)  # N x 3, right derivation
    acc = right_vel - left_vel  # N x 3
    return left_vel, right_vel, acc


class JitterDetector:
    NUM_ADJACENT_FRAME = 5
    NUM_MIDDLE_FRAME = 15

    MINI_MAX_VEL = 0.05
    MINI_MIN_VEL = 0.025
    MINI_SIDE_VEL = 0.03
    MINI_STRIDE_VEL = 0.01
    MINI_MAX_ACC = 0.05
    NUM_MINI_INTERVAL = 1
    MINI_SLOPE_RATIO = 2.0
    MINI_MIN_RATIO = 3.0
    MINI_MAX_RATIO = 5.0
    MINI_MULTIPLIER = 0.4
    MINI_DIFF_DIS = 0.15

    @classmethod
    def build_gap_num_array(cls, is_key):
        left_gap_num = np.ones(is_key.shape, dtype=int)
        right_gap_num = np.ones(is_key.shape, dtype=int)

        gap_index = np.where(~is_key)[0].tolist()
        gap_intervals = IntervalOperator.build_interval(gap_index, merge_length=1)

        for gap_start, gap_end in gap_intervals:
            gap_num = gap_end - gap_start + 2
            if gap_end < is_key.shape[-1] - 1:
                left_gap_num[gap_end + 1] = gap_num
            if gap_start > 0:
                right_gap_num[gap_start - 1] = gap_num
        return left_gap_num, right_gap_num

    @classmethod
    def delete_noise_interval(cls, marker_pos, is_key, noise_intervals):
        cleanup_is_key = PreprocessGap.update_key_mask(is_key, noise_intervals)
        marker_pos = PreprocessGap.preprocess_gap_interval(marker_pos, cleanup_is_key)
        return marker_pos, cleanup_is_key

    @classmethod
    def detect_flatten_mini_jitter(cls, marker_pos, is_key):
        marker_pos, cleanup_is_key = cls.delete_noise_interval(marker_pos, is_key, [])

        left_gap_num, right_gap_num = cls.build_gap_num_array(cleanup_is_key)

        right_gap_num[right_gap_num > cls.NUM_ADJACENT_FRAME + 1] = 1

        left_vel, right_vel, acc = calc_vel_acc(marker_pos) # 前一帧速度，后一帧速度，当前帧速度
        left_vel_norm = np.linalg.norm(left_vel, axis=-1)
        right_vel_norm = np.linalg.norm(right_vel, axis=-1)
        stride_vel = (left_vel + right_vel) / 2
        stride_vel_norm = np.linalg.norm(stride_vel, axis=-1)

        flatten_mask = (left_vel_norm < cls.MINI_MAX_VEL) | (right_vel_norm < cls.MINI_MAX_VEL) | (
                stride_vel_norm < cls.MINI_MAX_VEL)

        flatten_index = np.where(flatten_mask)[0].tolist()
        flatten_intervals = IntervalOperator.build_interval(flatten_index, cls.NUM_MIDDLE_FRAME)

        mini_noise_intervals = []
        not_match_noise_idx = []
        for flatten_start, flatten_end in flatten_intervals:
            mini_part_intervals = []
            candidate_noise_idx = []
            i = flatten_start
            while i < flatten_end:
                if (left_vel_norm[i] < cls.MINI_MAX_VEL < right_vel_norm[i] and np.linalg.norm(
                        right_vel[i] - left_vel[i]) > cls.MINI_MAX_ACC) or (
                        i - 1 >= 0 and left_vel_norm[i - 1] < cls.MINI_MAX_VEL < left_vel_norm[i] < right_vel_norm[i]
                        and np.linalg.norm(right_vel[i] - left_vel[i]) > cls.MINI_MAX_ACC) or (
                        i + 1 < marker_pos.shape[0] and left_vel_norm[i] < cls.MINI_MIN_VEL and (
                        left_vel_norm[i + 1] > cls.MINI_MAX_VEL or right_vel_norm[i + 1] > cls.MINI_MAX_VEL) and
                        stride_vel_norm[i + 1] < cls.MINI_STRIDE_VEL):
                    # assume that scale of noise start point and end point matches.
                    # scale_ratio = min(right_vel_norm[i] * right_gap_num[i] / cls.MINI_MAX_VEL,
                    #                   np.linalg.norm(right_vel[i] * right_gap_num[i] - left_vel[i]) /
                    #                   cls.MINI_MAX_ACC)
                    scale_ratio = min(right_vel_norm[i] / cls.MINI_MAX_VEL,
                                      np.linalg.norm(right_vel[i] - left_vel[i]) / cls.MINI_MAX_ACC)
                    ratio = int(scale_ratio * 2) / 2
                    scores = {}
                    # alternative_scores = {}
                    side_vel_threshold = cls.MINI_SIDE_VEL
                    match_scale = np.clip(cls.MINI_MULTIPLIER * scale_ratio - 1, 1.0, 3.0)
                    # constrain match range to prevent from influencing by possibly wrong trend and
                    # thus deleting too much frames.
                    match_range = cls.NUM_ADJACENT_FRAME \
                        if right_gap_num[i] * scale_ratio < cls.MINI_MIN_RATIO and \
                           ((left_vel_norm[i] > cls.MINI_SIDE_VEL and
                             (left_vel[i] * right_vel[i])[abs(right_vel[i] - left_vel[i]).argmax()] < 0) or
                            ((abs(right_vel[i:i + cls.NUM_ADJACENT_FRAME + 1].sum(0) / (
                                    cls.NUM_ADJACENT_FRAME + 1)) > cls.MINI_MIN_VEL) &
                             (abs(right_vel[i:i + cls.NUM_ADJACENT_FRAME + 1]).sum(0) - abs(
                                 right_vel[i:i + cls.NUM_ADJACENT_FRAME + 1].sum(
                                     0)) < cls.MINI_MIN_VEL)).any()) else cls.NUM_MIDDLE_FRAME

                    for j in range(i + 1, min(i + match_range, marker_pos.shape[0] - 1)):
                        # find two candidate end point, but the second one is near the first one.
                        if scores and j - list(scores.values())[0]["end_idx"] > cls.NUM_ADJACENT_FRAME:
                            break
                        if cleanup_is_key[j] and (right_vel_norm[j] > side_vel_threshold or
                                                  ~cleanup_is_key[j + 1: j + 1 + cls.NUM_ADJACENT_FRAME].any()):
                            end_idx = j
                            while end_idx + 1 < marker_pos.shape[0] - 1 and not cleanup_is_key[end_idx + 1]:
                                end_idx += 1
                            vel = (marker_pos[end_idx + 1] - marker_pos[i]) / (end_idx - i + 1)
                            vel_norm = np.linalg.norm(vel)
                            acc_norm = np.linalg.norm(vel - left_vel[i])
                            if vel_norm < cls.MINI_MIN_VEL or acc_norm < cls.MINI_MIN_VEL:
                                scores[-min(vel_norm, acc_norm)] = {"no_gap_end": j, "end_idx": end_idx, "vel": vel,
                                                                    "vel_norm": vel_norm}
                                # if scale the first candidate end point matches, no need to find the second candidate
                                if right_vel_norm[j] * right_gap_num[j] > cls.MINI_SIDE_VEL * ratio:
                                    break
                                else:
                                    side_vel_threshold = cls.MINI_SIDE_VEL * ratio
                            elif right_gap_num[i] * scale_ratio > cls.MINI_MAX_RATIO and (
                                    vel_norm < cls.MINI_MIN_VEL * match_scale or
                                    acc_norm < cls.MINI_MIN_VEL * match_scale):
                                scores[-min(vel_norm, acc_norm)] = {"no_gap_end": j, "end_idx": end_idx, "vel": vel,
                                                                    "vel_norm": vel_norm}

                    if not scores:
                        if right_gap_num[i] * scale_ratio > cls.MINI_MAX_RATIO:
                            candidate_noise_idx.append(i)
                        elif right_gap_num[i] * scale_ratio > cls.MINI_MIN_RATIO:
                            not_match_noise_idx.append(i)

                    if scores:
                        max_score = max(scores.keys())
                        end_idx = scores[max_score]["end_idx"]

                        mini_part_intervals.append([i + right_gap_num[i], scores[max_score]["no_gap_end"]])
                        # no need to update stride vel, because previous stride vel is not used.
                        right_vel[i:end_idx + 1] = scores[max_score]["vel"]
                        left_vel[i + 1:end_idx + 2] = scores[max_score]["vel"]
                        right_vel_norm[i: end_idx + 1] = scores[max_score]["vel_norm"]
                        left_vel_norm[i + 1:end_idx + 2] = scores[max_score]["vel_norm"]
                        cleanup_is_key[i + 1: end_idx + 1] = False
                        i = end_idx

                i += 1

            # find long region mini noise.
            if candidate_noise_idx:
                # print("exist candidate: ", candidate_noise_idx)
                candidate_noise_idx = np.array(candidate_noise_idx)
                start_idx_list = np.where(candidate_noise_idx > -1)[0]
                # mini_long_intervals = []
                while start_idx_list.shape[0]:
                    i = start_idx_list.min()
                    next_start = start_idx = candidate_noise_idx[i]
                    start_right_dis = right_vel[start_idx] * right_gap_num[start_idx]

                    for end_idx in candidate_noise_idx[i + 1:]:
                        end_right_dis = right_vel[end_idx] * right_gap_num[end_idx]

                        if np.linalg.norm(start_right_dis + end_right_dis) < cls.MINI_DIFF_DIS:
                            # mini_long_intervals.append([start_idx + right_gap_num[start_idx], end_idx])
                            mini_noise_intervals.append([start_idx + right_gap_num[start_idx], end_idx])
                            next_start = end_idx
                            break
                    start_idx_list = np.where(candidate_noise_idx > next_start)[0]
                    if start_idx == next_start:
                        not_match_noise_idx.append(next_start)

            if mini_part_intervals:
                cluster_mini_intervals = IntervalOperator.cluster_interval(mini_part_intervals, split_ratio=0)
                for mini_cluster in cluster_mini_intervals:
                    if len(mini_cluster) >= cls.NUM_MINI_INTERVAL:
                        mini_noise_intervals.extend(mini_cluster)
        # if not_match_noise_idx:
        #     print("not match", not_match_noise_idx)
        return mini_noise_intervals, not_match_noise_idx, left_vel, right_vel

    @classmethod
    def detect_slope_mini_jitter(cls, left_vel, right_vel):

        abs_left_vel = abs(left_vel)
        slope_start_mask = abs_left_vel > cls.MINI_MAX_VEL
        abs_right_vel = abs(right_vel)
        slope_end_mask = abs_right_vel > cls.MINI_MAX_VEL
        abs_acc = abs(right_vel - left_vel)

        # don't delete peak in normal trend
        left_region_vel = np.stack([np.roll(left_vel, shift=i, axis=0) for i in range(cls.NUM_ADJACENT_FRAME)])
        right_region_vel = np.stack([np.roll(right_vel, shift=-i, axis=0) for i in range(cls.NUM_ADJACENT_FRAME)])
        is_peak_mask = ((left_region_vel > 0).all(axis=0) & (right_region_vel < 0).all(axis=0)) | \
                       ((left_region_vel < 0).all(axis=0) & (right_region_vel > 0).all(axis=0))

        slope_noise_mask = ((((abs_acc > abs_left_vel * cls.MINI_SLOPE_RATIO) & slope_start_mask) |
                             ((abs_acc > abs_right_vel * cls.MINI_SLOPE_RATIO) & slope_end_mask)) &
                            (left_vel * right_vel < 0) & ~is_peak_mask).any(axis=-1)
        slope_noise_index = np.where(slope_noise_mask)[0].tolist()
        slope_noise_intervals = IntervalOperator.build_interval(slope_noise_index, merge_length=1)

        single_point_mask = slope_noise_mask & ~np.roll(slope_noise_mask, shift=1) & ~np.roll(slope_noise_mask,
                                                                                              shift=-1)
        single_point_idx = np.where(single_point_mask)[0]

        stride_vel = (left_vel + right_vel) / 2
        abs_stride_vel = abs(stride_vel)

        for i in range(single_point_idx.shape[0] - 1):
            start = single_point_idx[i]
            end = single_point_idx[i + 1]
            if end - start == 2 and (right_vel[start] - left_vel[end]).sum():
                abs_acc_previous = abs(stride_vel[start] - left_vel[start - 1])
                abs_acc_next = abs(right_vel[end + 1] - stride_vel[end])
                is_jitter_start = (((abs_acc_previous > abs_left_vel[start - 1] * cls.MINI_SLOPE_RATIO) &
                                    (abs_left_vel[start - 1] > cls.MINI_MAX_VEL)) |
                                   ((abs_acc_previous > abs_stride_vel[start] * cls.MINI_SLOPE_RATIO) &
                                    (abs_stride_vel[start] > cls.MINI_MAX_VEL))) & \
                                  (left_vel[start - 1] * stride_vel[start] < 0)
                is_jitter_end = (((abs_acc_next > abs_right_vel[end + 1] * cls.MINI_SLOPE_RATIO) &
                                  (abs_right_vel[end + 1] > cls.MINI_MAX_VEL)) |
                                 ((abs_acc_next > abs_stride_vel[end] * cls.MINI_SLOPE_RATIO) &
                                  (abs_stride_vel[end] > cls.MINI_MAX_VEL))) & \
                                (right_vel[end + 1] * stride_vel[end] < 0)
                if (is_jitter_start & is_jitter_end).any():
                    slope_noise_intervals.append([start + 1, end - 1])

        return slope_noise_intervals

    @classmethod
    def detect_mini_jitter_by_matching(cls, marker_pos, is_key):
        mini_noise_intervals, not_match_idx, left_vel, right_vel = cls.detect_flatten_mini_jitter(marker_pos, is_key)

        slope_noise_intervals = cls.detect_slope_mini_jitter(left_vel, right_vel)

        for i in not_match_idx:
            # if is_key is False, means it may provide wrong tendency.
            if is_key[i + 1]:
                mini_noise_intervals.append([i + 1, i + 1])

        return IntervalOperator.merge_interval(sorted(mini_noise_intervals + slope_noise_intervals), 1)

    @classmethod
    def smooth_controller_curve(cls, controller_curve_info):
        cleanup_controller_curve_info = {}
        for controller_name, controller_curve in controller_curve_info.items():
            pos, is_key, offset, traj_length = PreprocessCurve.build_data(controller_curve["tc_y"],
                                                                          controller_curve["vc_y"],
                                                                          controller_curve.get("tc_x"),
                                                                          controller_curve.get("vc_x"))
            scale = UNIT / (pos.max(0) - pos.min(0) + EPS)
            scale_pos = pos * scale
            mini_noise_intervals = cls.detect_mini_jitter_by_matching(scale_pos, is_key)

            cleanup_scale_pos, cleanup_is_key = cls.delete_noise_interval(scale_pos, is_key, mini_noise_intervals)

            cleanup_pos = cleanup_scale_pos / scale

            tc = list(range(offset, offset + traj_length))
            cleanup_controller_curve_info[controller_name] = {"tc_y": tc, "vc_y": cleanup_pos[:, -1]}
            if controller_curve.get("vc_x") is not None:
                cleanup_controller_curve_info[controller_name]["tc_x"] = tc
                cleanup_controller_curve_info[controller_name]["vc_x"] = cleanup_pos[:, 0]
        return cleanup_controller_curve_info

    @classmethod
    def smooth_one_curve(cls, tc, vc):
        pos, is_key, offset, traj_length = PreprocessCurve.build_data(tc, vc)  # 帧数值，是否有帧, 起始帧，总帧数
        scale = UNIT / (pos.max(0) - pos.min(0) + EPS)
        scale_pos = pos * scale
        mini_noise_intervals = cls.detect_mini_jitter_by_matching(scale_pos, is_key)