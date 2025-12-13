# -*- coding: utf-8 -*-
# author: linhuan
# file: process_thum.py
# time: 2025/10/25 16:20
# description:
# -*- coding: utf-8 -*-
"""
自动裁切 + 拼合图片脚本
author: linhuan
description: 自动检测非背景区域，裁切空白并横向拼合。
"""

from PIL import Image
import numpy as np
import os, sys

# -*- coding: utf-8 -*-
"""
功能: 自动识别横向五视图，提取第1和第5个并拼合保存。
作者: linhuan
"""

from PIL import Image
import numpy as np
import os, sys

def auto_split_5_and_merge(input_path, output_path=None, count=5, margin=4):
    img = Image.open(input_path).convert("RGB")
    arr = np.array(img)
    h, w = arr.shape[:2]

    # 估计背景色（取四角平均）
    corners = np.vstack([
        arr[0:10, 0:10].reshape(-1, 3),
        arr[0:10, -10:].reshape(-1, 3),
        arr[-10:, 0:10].reshape(-1, 3),
        arr[-10:, -10:].reshape(-1, 3),
    ])
    bg_color = np.median(corners, axis=0)

    # 计算垂直方向非背景的像素和，用来判断人物之间的空白
    diff = np.linalg.norm(arr - bg_color.reshape(1, 1, 3), axis=2)
    col_sum = diff.sum(axis=0)
    content_cols = np.where(col_sum > 10)[0]

    # 根据内容列分段（每段对应一个人物）
    groups = []
    if content_cols.size > 0:
        start = content_cols[0]
        prev = start
        for x in content_cols[1:]:
            if x - prev > 20:  # 空隙阈值 -> 新段
                groups.append((max(0, start - margin), min(w, prev + margin)))
                start = x
            prev = x
        groups.append((max(0, start - margin), min(w, prev + margin)))
    else:
        groups = [(0, w)]

    # 若数量过多/过少，根据目标数量进行分段修正
    if len(groups) != count:

        seg_w = w // count
        groups = [(i * seg_w, (i + 1) * seg_w) for i in range(count)]

    # 提取第1和第5段
    first_x0, first_x1 = groups[0]
    last_x0, last_x1 = groups[-1]
    first = img.crop((first_x0, 0, first_x1, h))
    last = img.crop((last_x0, 0, last_x1, h))

    # 拼接两张
    total_w = first.width + last.width
    result = Image.new("RGB", (total_w, h), tuple(map(int, bg_color)))
    result.paste(first, (0, 0))
    result.paste(last, (first.width, 0))

    if not output_path:
        root, ext = os.path.splitext(input_path)
        output_path = root + "_1and5" + ext
    result.save(output_path, quality=95)

    return output_path






from PIL import Image
import numpy as np
import argparse
import os
import sys

def detect_content_columns(band):
    gray = (0.299 * band[:,:,0] + 0.587 * band[:,:,1] + 0.114 * band[:,:,2]).astype(np.float32)
    col_var = np.var(gray, axis=0)
    metric = col_var + np.sum(np.abs(gray - np.median(gray)), axis=0) * 0.1
    thr = max(metric.max() * 0.05, metric.mean() + metric.std() * 0.5)
    cols = np.where(metric > thr)[0]
    if cols.size < 3:
        thr = metric.max() * 0.02
        cols = np.where(metric > thr)[0]
    return cols

def trim_blank(band, trim_ratio):
    cols = detect_content_columns(band)
    if cols.size == 0:
        return band, 0, 0
    bw = band.shape[1]
    left, right = int(cols[0]), int(cols[-1])
    left_blank = left
    right_blank = bw - 1 - right
    new_left = int(left_blank * trim_ratio)
    new_right = bw - int(right_blank * trim_ratio)
    new_left = max(0, min(new_left, bw-1))
    new_right = max(new_left+1, min(new_right, bw))
    trimmed = band[:, new_left:new_right]
    return trimmed, left_blank, right_blank

def auto_split_5_and_merge_trim(input_path, output_path=None, count=5,
                                margin=4, trim_ratio=0.5, outer_trim=0.5, debug=True):
    img = Image.open(input_path).convert("RGB")
    arr = np.array(img)
    h, w = arr.shape[:2]

    gray = (0.299 * arr[:,:,0] + 0.587 * arr[:,:,1] + 0.114 * arr[:,:,2]).astype(np.float32)
    col_var = np.var(gray, axis=0)
    metric = col_var + np.sum(np.abs(gray - np.median(gray)), axis=0) * 0.1
    thr = max(metric.max() * 0.05, metric.mean() + metric.std() * 0.5)
    cols = np.where(metric > thr)[0]
    groups = []
    if cols.size > 0:
        start = int(cols[0])
        prev = start
        for x in cols[1:]:
            if int(x) - int(prev) > 20:
                groups.append((max(0, start - margin), min(w, prev + margin)))
                start = int(x)
            prev = int(x)
        groups.append((max(0, start - margin), min(w, prev + margin)))
    else:
        groups = [(0, w)]
    if len(groups) != count:
        seg_w = w // count
        groups = [(i * seg_w, (i + 1) * seg_w) for i in range(count)]

    first_x0, first_x1 = groups[0]
    last_x0, last_x1 = groups[-1]
    first_band = arr[:, first_x0:first_x1]
    last_band = arr[:, last_x0:last_x1]

    f_trim, f_lb, f_rb = trim_blank(first_band, trim_ratio)
    l_trim, l_lb, l_rb = trim_blank(last_band, trim_ratio)

    # 拼接
    first_img = Image.fromarray(f_trim)
    last_img = Image.fromarray(l_trim)
    total_w = first_img.width + last_img.width
    bg_color = tuple(map(int, np.median(arr.reshape(-1,3), axis=0)))
    merged = Image.new("RGB", (total_w, h), bg_color)
    merged.paste(first_img, (0,0))
    merged.paste(last_img, (first_img.width, 0))

    # 再整体裁掉外层空白
    merged_arr = np.array(merged)
    merged_trim, o_lb, o_rb = trim_blank(merged_arr, outer_trim)
    merged_final = Image.fromarray(merged_trim)

    if not output_path:
        root, ext = os.path.splitext(input_path)
        output_path = "%s_1and5_trim%.2f_outer%.2f%s" % (root, trim_ratio, outer_trim, ext)
    merged_final.save(output_path, quality=95)

    if debug:
        sys.stdout.write("[✔] 保存: %s\n" % output_path)
        sys.stdout.write("第一段 左右空白: %d / %d\n" % (f_lb, f_rb))
        sys.stdout.write("第五段 左右空白: %d / %d\n" % (l_lb, l_rb))
        sys.stdout.write("整体外层裁剪: 左右空白 %d / %d\n" % (o_lb, o_rb))
        sys.stdout.write("输出尺寸: %dx%d\n" % (merged_final.size[0], merged_final.size[1]))
    return output_path


def process(input_path, output_path=None, trim_ratio=0.5, count=5, diff_thresh=10):
    """
    自动裁切并拼接第1和第5段图像，左右空白按比例裁剪
    :param input_path: 输入图像路径
    :param output_path: 输出路径，可为空
    :param trim_ratio: 空白保留比例 (0~1)
    :param count: 横向分段数量（默认5）
    :param diff_thresh: 与背景色差异阈值，用于判定空白列
    """
    img = Image.open(input_path).convert("RGB")
    arr = np.array(img)
    h, w = arr.shape[:2]

    # 背景色（四角平均）
    corners = np.vstack([
        arr[0:10, 0:10].reshape(-1,3),
        arr[0:10, -10:].reshape(-1,3),
        arr[-10:, 0:10].reshape(-1,3),
        arr[-10:, -10:].reshape(-1,3)
    ])
    bg_color = np.median(corners, axis=0)

    # 检测内容列
    col_diff = np.linalg.norm(arr - bg_color.reshape(1,1,3), axis=2).mean(axis=0)
    content_cols = np.where(col_diff > diff_thresh)[0]

    groups = []
    if content_cols.size > 0:
        start = content_cols[0]
        prev = start
        for x in content_cols[1:]:
            if x - prev > 20:
                groups.append((max(0, start), min(w, prev+1)))
                start = x
            prev = x
        groups.append((max(0, start), min(w, prev+1)))
    else:
        groups = [(0, w)]

    if len(groups) != count:
        seg_w = w // count
        groups = [(i*seg_w, (i+1)*seg_w) for i in range(count)]

    # 第1和第5段
    first_x0, first_x1 = groups[0]
    last_x0, last_x1   = groups[-1]
    first_band = arr[:, first_x0:first_x1]
    last_band  = arr[:, last_x0:last_x1]

    # 裁剪左右空白函数
    def trim_band(band, bg_color, trim_ratio=0.5, diff_thresh=10):
        bw = band.shape[1]
        # 每列与背景色差异
        col_diff = np.linalg.norm(band - bg_color.reshape(1,1,3), axis=2).mean(axis=0)
        non_empty_cols = np.where(col_diff > diff_thresh)[0]
        if non_empty_cols.size == 0:
            return band

        left_blank  = non_empty_cols[0]
        right_blank = bw - 1 - non_empty_cols[-1]

        # 分别裁剪左右空白
        left_trim  = min(left_blank, int(left_blank * (1 - trim_ratio)))
        right_trim = min(right_blank, int(right_blank * (1 - trim_ratio)))

        new_left  = left_trim
        new_right = bw - right_trim
        return band[:, new_left:new_right]

    # 裁剪
    first_trim = trim_band(first_band, bg_color, trim_ratio, diff_thresh)
    last_trim  = trim_band(last_band,  bg_color, trim_ratio, diff_thresh)

    # 拼接
    f_img = Image.fromarray(first_trim)
    l_img = Image.fromarray(last_trim)
    total_w = f_img.size[0] + l_img.size[0]
    result = Image.new("RGB", (total_w, h), tuple(map(int,bg_color)))
    result.paste(f_img, (0,0))
    result.paste(l_img, (f_img.size[0],0))

    if not output_path:
        base, ext = os.path.splitext(input_path)
        output_path = "%s_trim%.2f%s" % (base, trim_ratio, ext)

    result.save(output_path, quality=95)
    sys.stdout.write("[✔] saved: %s\n" % output_path)
    return output_path

# -------------------------------
if __name__ == "__main__":
    input_path  = r'D:\test\ST065C\before.jpg'
    output_path = r'D:\test\ST065C\after_1and5_trim.jpg'

    # trim_ratio 控制空白保留比例
    process(input_path, output_path, trim_ratio=0.3, count=5, diff_thresh=10)




















# if __name__ == "__main__":
#     # parser = argparse.ArgumentParser()
#     # parser.add_argument("input", help="输入图像路径")
#     # parser.add_argument("output", nargs="?", default=None, help="输出图像路径")
#     # parser.add_argument("--trim", type=float, default=0.5, help="左右空白减少比例 (0~1)")
#     # args = parser.parse_args()
#     input=r'D:\test\ST065C\before.jpg'
#     output=r'D:\test\ST065C\after_12.jpg'
#
#     process(input,output, trim_ratio=1, keep_margin=1, count=5)
















