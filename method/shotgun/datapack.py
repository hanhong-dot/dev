# -*- coding: utf-8 -*-#
# Python       : python 2.7.16
# -------------------------------------------------------------------------------
# NAME         : datapack
# Describe     : 打包数据
# Version      : v0.01
# Author       : linhuan
# Email        : hanhong@papegames.net
# DateTime     : 2022/5/25__16:45
# -------------------------------------------------------------------------------
# -------------------------------------------------------------------------------
# example:
# 
# -------------------------------------------------------------------------------

class Pack(object):
    '''
    数据打包类
    '''
    # 预设写入数据库的类型
    __databasetype__ = {
        "publish": {
            "file_link_type": "local",
            "status": "fin"
        },
        "version": {
            "file_link_type": "upload",
            "status": "fin"
        },
    }
    # 预设的简化版信息类型
    __simplifybaseitem__ = ["src_path", "des_path"]

    # 预设的完整信息类型
    __baseitem__ = [
        "src_path",  # 源地址
        "des_path",  # 目标地址
        "down_path",  # 下环节
        "up_path",  # 上环节
        "description",  # 上传描述
        "task_type",  # 文件类型(支持参数:asset,shot,sequence,episode)
        "task_name",  # 任务名
        "entity_name",  # 实体名:  资产名，镜头名,集数名，场次名
        "episode_name",  # 集数名
        "sequence_name",  # 场次名
        "project_name",  # 项目名
        "file_link_type",  # sg连接，缺省
        "status",  # 任务状态
        "task_thumbnail",  # sg缩略图
        "tags",  # 文件标签
        "relationship",
        "dcc"  # 软件
    ]

    # 预设类型字段映射，发布一下类型标签的文件才会进入数据库
    __link_type__ = {
        "publish": ["publish", "master", "fbx", "mbfbx", "mocap", "ue", 'unityfbx', 'unityxml'],
        "version": ["version", "attachment"]
    }

    @classmethod
    def get_upload_type(cls, tag):
        '''
        根据tag获取上传类型
        :param tag:
        :return:
        '''
        for k, v in cls.__link_type__.items():
            if tag in v:
                return k
        return tag

    @classmethod
    def get_file_type(cls, tag, dcc):
        u"""
        根据tag获取文件publish类型
        """
        for k, v in cls.__link_type__.items():
            if k == 'publish' and tag in v:
                if tag == 'publish' and dcc.lower() == 'maya':
                    return 'Maya Scene'
                if tag == 'fbx' and dcc.lower() == 'maya':
                    return 'Maya FBX'
                if tag == 'mbfbx':
                    return 'Motion Builder FBX'
                if tag == 'mbexfbx':
                    return 'MoBu Export FBX'
                if tag == 'mocap':
                    return 'Mocap Scene'
                if tag == 'ue':
                    return 'UE Scene'
                if tag == 'unityfbx':
                    return 'Unity_FBX'
                if tag == 'unityxml':
                    return 'Unity_XML'

    @classmethod
    def set_info(cls,
                 src_path=None,
                 des_path=None,
                 down_path=None,
                 up_path=None,
                 description=None,
                 task_type=None,
                 task_name=None,
                 entity_name=None,
                 episode_name=None,
                 sequence_name=None,
                 project_name=None,
                 file_link_type=None,
                 status=None,
                 task_thumbnail=None,
                 tags=None,
                 relationship=None,
                 dcc=None,
                 thumbnail=None,
                 work_file=None,
                 ref_info=None,
                 send_jenkins=None,
                 wbx=None,
                 parent_asset=None,
                 updata_model=None,
                 pl_face=None,
                 add_tangent=None,
                 bs_setting=None


                 ):
        '''

        :param src_path: 原始路径
        :param des_path: 目标路径
        :param down_path: 下一环节文件
        :param up_path: 上一环节文件
        :param description: 描述
        :param task_type: 实体类型 Asset ,Shot , Sequence , Episode
        :param task_name: 任务名
        :param entity_name: 实体名称，Asset Name , Shot Name
        :param episode_name: 集数名称
        :param sequence_name: 场次名称
        :param project_name: 项目名
        :param file_link_type: 文件上传服务器的类型 local,upload，url
        :param status: publish 和 version 的状态
        :param task_thumbnail: 本地缩略图路径
        :param tags: 标记
        :param relationship: version和publish的关系
        :return:
        '''
        _basedict, _dict = {}, {}
        _upload_type = cls.get_upload_type(tags)
        _publish_file_type = {}
        if dcc:
            _publish_file_type = cls.get_file_type(tags, dcc)
        if _upload_type in cls.__databasetype__:
            for _item in cls.__baseitem__:
                _basedict[_item] = eval(_item)
            if not file_link_type:
                _basedict["file_link_type"] = cls.__databasetype__[_upload_type]["file_link_type"]
            if not status:
                _basedict["status"] = cls.__databasetype__[_upload_type]["status"]
        else:
            for _item in cls.__simplifybaseitem__:
                _basedict[_item] = eval(_item)

        if _dict:
            _basedict['relationship'] = relationship
            _basedict.update(_dict)
        _basedict["upload_type"] = _upload_type
        if _publish_file_type:
            _basedict["publish_file_type"] = _publish_file_type
        _basedict["thumbnail"] = thumbnail
        _basedict["work_file"] = work_file
        _basedict["ref_info"] = ref_info
        _basedict["send_jenkins"] = send_jenkins
        _basedict["wbx"] = wbx
        _basedict["parent_asset"] = parent_asset
        _basedict["updata_model"] = updata_model
        _basedict["pl_face"] = pl_face
        _basedict["add_tangent"] = add_tangent
        _basedict["bs_setting"] = bs_setting
        return _basedict

    @classmethod
    def combine(cls, unpacklist):
        '''整合发布信息并打包成规范格式
        '''
        _alldict = {"collecter": {},
                    "shotgun": {}
                    }
        _versionlist = []
        _publishlist = []
        for _item in unpacklist:
            _upload_type = _item["upload_type"]
            if _upload_type in cls.__databasetype__:
                if _upload_type not in _alldict["shotgun"]:
                    _alldict["shotgun"][_upload_type] = []
                _alldict["shotgun"][_upload_type].append(_item)
            else:
                if _upload_type not in _alldict["collecter"]:
                    _alldict["collecter"][_upload_type] = []
                _alldict["collecter"][_upload_type].append(_item)
        return _alldict

# if __name__ == '__main__':
#     import pprint
#
#
#     _src_path = 'E:/Export/container_outworkshop_001.fbx'
#     _des_path = 'M:/projects/X3/publish/assets/rolaccesory/TDTEST_ROLEACCE/rig/maya/data/fbx/TDTEST_ROLEACCE_MB.fbx'
#     infolist=[]
#     _info = Pack.set_info(src_path=_src_path, des_path=_des_path, tags='unityfbx')
#     infolist.append(_info)
#     print Pack.combine(infolist)

# info1 = Pack.set_info(
#     src_path='ABC',
#     des_path='EFD',
#     description='HAHHA',
#     task_type='Asset',
#     task_name='Srf_hig',
#     entity_name='CA001002',
#     episode_name='seq001_sc001',
#     sequence_name=None,
#     project_name=None,
#     tags='publish',
#     relationship=0
#
# )
# info2 = Pack.set_info(
#     src_path='ABC',
#     des_path='EFD',
#     description='HAHHA',
#     task_type='Asset',
#     task_name='Srf_hig',
#     entity_name='CA001002',
#     episode_name='seq001_sc001',
#     sequence_name=None,
#     project_name=None,
#     file_link_type='upload',
#     tags='version',
#     relationship=0,
#     status='ip'
#
# )
#
# info3 = Pack.set_info(
#     src_path='ABC',
#     des_path='EFD',
#     tags='ass')
#
# info4 = Pack.set_info(
#     src_path='iiii',
#     des_path='qqqq',
#     tags='ass')
#
# info5 = Pack.set_info(
#     src_path='777',
#     des_path='888',
#     tags='master')
#
# # pprint(info2)
# infolist = []
# # # infolist.append(info1)
# infolist.append(info2)
# infolist.append(info3)
# infolist.append(info5)
# pprint(infolist)
# pprint(Pack.combine(infolist))
