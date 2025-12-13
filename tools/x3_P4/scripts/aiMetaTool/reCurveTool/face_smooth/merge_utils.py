# vim:ts=4:sw=4:expandtab
# -*- coding: utf-8 -*-
# @brief
# @author huangsheng@papegames.net
# @version v1.0.0
# @file: merge_utils.py
# @time: 2025/8/21 18:09


class IntervalOperator:
    MIN_MERGE_LENGTH = 6
    MAX_GAP_LENGTH = 30
    MAX_GAP_RATIO = 1.5

    @classmethod
    def build_interval(cls, noise_idx, merge_length=None):
        if len(noise_idx) == 0:
            return []

        if merge_length is None:
            merge_length = cls.MIN_MERGE_LENGTH
        if merge_length < 0:
            merge_length = 0
        noise_interval = []
        interval_start = interval_end = noise_idx[0]
        for i in noise_idx[1:]:
            if i - interval_end <= merge_length:
                interval_end = i
            else:
                noise_interval.append([interval_start, interval_end])
                interval_start = interval_end = i
        noise_interval.append([interval_start, interval_end])
        return noise_interval

    @classmethod
    def merge_interval(cls, noise_interval, merge_length=None):

        if len(noise_interval) == 0:
            return []

        if merge_length is None:
            merge_length = cls.MIN_MERGE_LENGTH
        if merge_length < 0:
            merge_length = 0
        merged_interval = []
        pre_start, pre_end = noise_interval[0]
        for next_start, next_end in noise_interval[1:]:
            if next_start - pre_end > merge_length:
                merged_interval.append([pre_start, pre_end])
                pre_start = next_start
            pre_end = max(next_end, pre_end)

        merged_interval.append([pre_start, pre_end])
        return merged_interval

    @classmethod
    def cluster_interval(cls, noise_interval, split_length=None, split_ratio=None):
        if split_length is None:
            split_length = cls.MAX_GAP_LENGTH
        if split_ratio is None:
            split_ratio = cls.MAX_GAP_RATIO

        noise_parts = []
        noise_parts_interval = []
        for i in range(len(noise_interval) - 1):
            pre_start, pre_end = noise_interval[i]
            next_start, next_end = noise_interval[i + 1]

            noise_parts_interval.append(noise_interval[i])
            pre_length = pre_end - pre_start + 1
            next_length = next_end - next_start + 1
            gap_length = next_start - pre_end - 1
            # never merge if absolute or relative gap length is greater than threshold.
            if gap_length >= split_length or (
                    split_ratio > 0 and gap_length >= (pre_length + next_length) * split_ratio):
                noise_parts.append(noise_parts_interval)
                noise_parts_interval = []
        noise_parts_interval.append(noise_interval[-1])
        noise_parts.append(noise_parts_interval)
        return noise_parts
