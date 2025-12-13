# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       : jsonio
# Describe   : 说明描述
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2022/5/5__18:22
# -------------------------------------------------------
import os
import json
try:
    import sys
    reload(sys)
    sys.setdefaultencoding('utf-8')
except:
    pass

__all__ = ["read", "write"]

'''
json读写集合
'''


def read(path, rtype="r", hook=None):
    '''读取json文件信息
    参数：
        path-->路径
        rtype-->文件读取方式
    '''
    if not os.path.exists(path):
        return None
    with open(path, rtype) as f:
        _data = json.load(f, object_pairs_hook=hook)
        f.close()
    return _data





def write(info, path, wtype="w"):
    '''写入json文件信息
    参数：
        info-->信息
        path-->路径
        wtype-->文件写入方式
    '''
    _path = os.path.dirname(path)
    if not os.path.exists(_path):
        os.makedirs(_path)
    with open(path, wtype) as f:
        json.dump(info, f, indent=4, separators=(',', ':'))
        f.close()
    return True

# if __name__ == '__main__':
#     # 假设你的中文字符串是这样的
#     # chinese_text = u"你好，世界"
#     # import json
#     #
#     # json_text = json.dumps({"message": chinese_text})
#     # print(json_text)
#     #
#     # # 如果需要写入文件，可以这样操作
#     # with open('//10.10.201.151/share/netrender/submission/shogun/marker_clean_up/test.json', 'w') as f:
#     #     f.write(json_text)
#
#     info = read('//10.10.201.151/share/netrender/submission/shogun/marker_clean_up/test.json')
#     for k,v in info.items():
#         k=k.decode('utf-8')
#         v=v.decode('utf-8')
#         print k,v

