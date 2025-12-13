# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       : image_process
# Describe   : 图片处理
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2022/6/12__14:06
# -------------------------------------------------------
import maya.OpenMaya
import os
FORMATDICT = {
    "jpg": "jpeg"
}


def image_resize(src, pixel=[256, 128], dst=None, imgform='png'):
    u"""
    转换图片尺寸
    """
    img = maya.OpenMaya.MImage()
    img.readFromFile(src)
    if pixel:
        img.resize(pixel[0], pixel[1])
    else:
        _w,_h=img.getSize()
        _num=_w/256
        _h_new=int(_h/_num)
        img.resize(256, _h_new)
    img.writeToFile(dst, imgform)


def image_resize_n(src, pixel=[256, 128], dst=None, imgform='png'):
    u"""
    转换图片尺寸
    """
    from PIL import Image
    img = Image.open(src)
    if pixel:
        img = img.resize(pixel)
    else:
        _w,_h=img.size
        _num=_w/256
        _h_new=int(_h/_num)
        img = img.resize((256, _h_new))
    img.save(dst, imgform)
def _cover_imageform(src, dst, imgform='png'):
    u"""
    转换图片格式(尺寸不变)
    """
    img = maya.OpenMaya.MImage()
    img.readFromFile(src)
    img.writeToFile(dst, imgform)

def cover_imgageform(src,dst):
    u"""
    转换图片格式(由dst后缀判断格式
    :param scr: 源文件
    :param dst: 目标文件
    :return:
    """
    _format = get_format(os.path.splitext(dst)[-1])
    _cover_imageform(src,dst)

def get_format(suffix):
    '''
    获取映射格式
    :param suffix:解析格式
    :return:str
    '''
    if suffix.startswith("."):
        suffix = suffix[1:]

    if suffix in FORMATDICT:
        return FORMATDICT[suffix].upper()
    return suffix.upper()

if __name__ == '__main__':
    path = 'C:/Users/linhuan/Downloads/test.jpg'
    _thumbnall_local = 'D:/temp_info/maya/assets/prp/ST001S/Task/drama_mdl/maya/work/thumbnail/ST001S.drama_mdl.v001.png'
    image_resize(path, [256, 128], dst=_thumbnall_local)
