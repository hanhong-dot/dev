# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       : sg_image
# Describe   : 缩略图相关函数
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2022/10/22__15:26
# -------------------------------------------------------
import database.shotgun.core.sg_base as sg_base
import urllib
import os
def select_entity_thumbnaildata(sg,entity_type, entity_id):
    u"""
    从实体获得缩略图
    :param sg:
    :param entity_type:
    :param entity_id:
    :return:
    """
    return sg_base.select_entity(sg, entity_type, entity_id, ['code', 'image'])

def updata_entity_thumbnaildata(sg,entity_type, entity_id,imagepath):
    u"""
    更新实体略图
    :param sg:
    :param entity_type:
    :param entity_id:
    :param imagepath:
    :return:
    """
    try:
        return sg_base.update_entity(sg, entity_type, entity_id, data={"image":imagepath})
    except:
        return

def download_entity_thumbnail(sg,entity_type,entity_id,imagepath):
    u"""
    下载缩略图
    :param sg:
    :param entity_type: 实体类型
    :param entity_id: id
    :param imagepath: 要下载到的缩略图(文件夹+文件名)
    :return:
    """

    entity_thumbnail = select_entity_thumbnaildata(sg,entity_type, entity_id)
    if not entity_thumbnail:
        return ""
    url = entity_thumbnail['image']

    if url:
        urllib.urlretrieve(url, imagepath)
        return imagepath
    else:
        return ''

if __name__ == '__main__':
    import database.shotgun.core.sg_analysis as sg_analysis

    import database.shotgun.core.templates_analysis as templates_analysis


    sg = sg_analysis.Config().login()
    # entity_type='Asset'
    # entity_id=12637

    # entity_type = 'Task'
    # entity_id=81622
    # # print(sg_base.select_entity(sg, entity_type, entity_id, ['image']))
    # imagepath='D:/test/f/test01_task.png'
    # download_entity_thumbnail(sg, entity_type, entity_id, imagepath)

    entity_type='Task'
    _entity_datas={}
    fields = ['id','content',"entity",'step']
    filters=[['project.Project.name', 'is', 'X3']]
    _task_datas=[]
    _datas=sg.find(entity_type, filters=filters, fields=fields)
    _project='X3'
    for i in range(len(_datas)):
        _task_data={}
        # print(_datas[i]['id'])
        # print(_datas[i]['content'])
        # print(_datas[i]['entity']['name'])
        # print(_datas[i])

        if 'step' in _datas[i] and _datas[i]['step'] and 'entity' in _datas[i] and _datas[i]['entity']:
            _task_data['id']=_datas[i]['id']
            _task_data['name']=_datas[i]['content']
            _task_data['entity_name']=_datas[i]['entity']['name']
            _task_data['step_name'] = _datas[i]['step']['name']
            _task_data['entity_id'] = _datas[i]['entity']['id']
            _task_data['entity_type']=_datas[i]['entity']['type']
        if _task_data:
            _task_datas.append(_task_data)

    for j in  range(len(_task_datas)):
        try:

            _task_id=_task_datas[j]['id']
            _task_name=_task_datas[j]['name']
            _step_name=_task_datas[j]['step_name']
            _entity_name=_task_datas[j]['entity_name']
            _entity_type=_task_datas[j]['entity_type']
            _entity_id=_task_datas[j]['entity_id']
            _assettype=''
            if _entity_type=='Asset':
                _assettype=sg_base.select_entity(sg, _entity_type, _entity_id, ['sg_asset_type'])['sg_asset_type']
            _handle=templates_analysis.AnalysisMayaTemplates(_project, _entity_type, _entity_name, _step_name, _task_name, _version=1, _assettype=_assettype, _dcc='maya')
            _task_thumbnail=_handle.get_task_thumbnail()
            _entity_thumbnail=_handle.get_thumbnail()
            _path_task=os.path.dirname(_task_thumbnail)
            _path_entity=os.path.dirname(_entity_thumbnail)

            if not os.path.exists(_path_task):
                os.makedirs(_path_task)
            if not os.path.exists(_path_entity):
                os.makedirs(_path_entity)

            #下载资产缩略图到
            # _img_thumbnail=sg_base.select_entity(sg, _entity_type, _entity_id, ['image'])['image']
            # print(entity_type)
            # print(_entity_id)
            # print(_img_thumbnail)
            print(download_entity_thumbnail(sg, _entity_type, _entity_id, _entity_thumbnail))

            #下载task缩略图
            # _img_thumbnail=sg_base.select_entity(sg, entity_type, _task_id, ['image'])['image']
            print(download_entity_thumbnail(sg,  entity_type, _task_id, _task_thumbnail))
        except:
            print('============')
            print(_task_datas[j]['entity_name'])
            print(_task_datas[j]['name'])
            print('============')











