# vim:ts=4:sw=4:expandtab
# -*- coding: utf-8 -*-
# @brief
# @author huangsheng@papegames.net
# @version v1.0.0
# @file: preprocess.py.py
# @time: 2025/8/21 18:20


import numpy as np

from .merge_utils import IntervalOperator


class PreprocessGap:
    @classmethod
    def linear_gap_filling(cls, start_value=None, end_value=None, length=1):
        # if start value and end value is None, gap last all the time, and we fill gap with 0.
        if start_value is None and end_value is None:
            start_value = end_value = 0
        # if start value or end value is None, we fill gap with horizontal line.
        elif start_value is None and end_value is not None:
            start_value = end_value
        elif start_value is not None and end_value is None:
            end_value = start_value

        step_delta = (end_value - start_value) / length
        return start_value + np.arange(1, length)[:, None] * step_delta

    @classmethod
    def preprocess_gap_interval(cls, marker_pos, is_key):
        gap_idx = np.where(~is_key)[0].tolist()
        gap_intervals = IntervalOperator.build_interval(gap_idx, merge_length=1)
        marker_pos = marker_pos.copy()
        for start, end in gap_intervals:
            start_value = marker_pos[start - 1] if start > 0 else None
            end_value = marker_pos[end + 1] if end < marker_pos.shape[0] - 1 else None
            length = end - start + 2
            marker_pos[start: end + 1] = cls.linear_gap_filling(start_value, end_value, length)
        return marker_pos

    @classmethod
    def update_key_mask(cls, is_key, noise_intervals):
        reserve_mask = np.full(is_key.shape[0], True)
        for noise_start, noise_end in noise_intervals:
            reserve_mask[noise_start: noise_end + 1] = False

        cleanup_is_key = is_key & reserve_mask
        return cleanup_is_key


class PreprocessCurve:

    @classmethod
    def build_data(cls, tc_y, vc_y, tc_x=None, vc_x=None):
        if tc_x is not None:
            offset = min(tc_x.min(), tc_y.min())
            traj_length = max(tc_x.max(), tc_y.max()) - offset + 1
            pos_x, is_key_x = cls.build_data_from_tc_vc(tc_x, vc_x, traj_length, offset)
            pos_y, is_key_y = cls.build_data_from_tc_vc(tc_y, vc_y, traj_length, offset)
            is_key = is_key_x & is_key_y
            pos = np.stack([pos_x, pos_y], axis=1)
        else:
            offset = tc_y.min()
            traj_length = tc_y.max() - offset + 1
            pos, is_key = cls.build_data_from_tc_vc(tc_y, vc_y, traj_length, offset)
            pos = pos[:, None]

        pos = PreprocessGap.preprocess_gap_interval(pos, is_key)

        return pos, is_key, offset, traj_length

    @classmethod
    def build_data_from_tc_vc(cls, tc, vc, traj_length, offset):
        pos = np.zeros(traj_length)
        is_key = np.zeros(traj_length)

        for t, v in zip(tc, vc):
            idx = t - offset
            is_key[idx] = 1
            pos[idx] = v

        return pos, is_key.astype(bool)


    @classmethod
    def on_curve_build_data(cls, tc, vc):
        offset = tc.min()
        traj_length = tc.max() - offset + 1
        pos, is_key = cls.build_data_from_tc_vc(tc, vc, traj_length, offset)
        pos = pos[:, None]
        pos = PreprocessGap.preprocess_gap_interval(pos, is_key)
        return pos, is_key, offset, traj_length