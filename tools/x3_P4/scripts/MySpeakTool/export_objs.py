# coding=utf-8
import pymel.core as pm
import maya.cmds as cmds
import os
import speak_tool_facs
'''
给冬豪出的一个用phn批量导出obj的功能
'''

def get_BS_node(mesh):
    '''
    获取bs节点
    :param mesh: transform   带bs的模型
    :return: bs节点
    '''
    BS_node = mesh.getShape().listHistory(type='blendShape')
    return BS_node[0] if BS_node else None

def export_obj(prefix, suffix, obj_path):
    '''
    导出obj
    :param prefix: str   前缀名，比如"ST","base"
    :param suffix: str   后缀名，记录动画帧
    :param obj_path: str   obj导出路径
    '''
    meshes = [pm.PyNode(prefix + '_Head'), pm.PyNode(prefix + '_Teeth')]
    dup_meshes = [pm.duplicate(mesh, n=str(mesh.name().split('|')[-1]) + suffix)[0] for mesh in meshes]
    pm.parent(dup_meshes, w=1)
    pm.select(dup_meshes)
    cmds.file(obj_path + '/%s_speak_anim_%s.obj' % (prefix, suffix), f=1, type='OBJexport',
              op='groups=1;ptgroups=1;materials=0;smoothing=1;normals=1', pr=1, es=1)
    pm.delete(dup_meshes)

def export_base_obj(prefix, obj_path):
    '''
    导出一个初始状态的模型obj
    '''
    head_mesh = pm.PyNode(prefix+'_Head')
    BS_node = get_BS_node(head_mesh)
    if BS_node:
        BS_node.envelope.set(0)
    export_obj(prefix, 'base', obj_path)
    if BS_node:
        BS_node.envelope.set(1)

def export_dup_obj(prefix, obj_path):
    '''
    导出动画过程中的模型obj
    '''
    now_time = int(pm.currentTime(q=1))
    export_obj(prefix, '%04d' % now_time, obj_path)

def export_one_anim_objs(prefix, obj_path):
    '''
    导出此场景内现有动画的模型obj
    '''
    pm.currentUnit(time='ntscf')
    min_time = int(pm.playbackOptions(q=1, min=1))
    max_time = int(pm.playbackOptions(q=1, max=1))
    for time in range(max_time - min_time + 1):
        pm.currentTime(min_time + time)
        export_dup_obj(prefix, obj_path)
        export_dup_obj(prefix, obj_path)

def export_phn_anim_objs(prefix, obj_path, phn_path):
    '''
    导出加载phn后每段动画的模型obj
    :param prefix: str   前缀名，比如"ST","base"
    :param obj_path: str   obj导出路径
    :param phn_path: str   phn所在路径
    '''
    ctrl = pm.PyNode('speakControl')
    names = []
    for name in os.listdir(phn_path):
        _, ext = os.path.splitext(name)
        if ext != ".phn":
            continue
        names.append(name)
    for name in names:
        pm.select(ctrl)
        speak_tool_facs.load_phn(phn_path + '/' + name)
        path = obj_path + '/' + name[:-4]
        if not os.path.exists(path):
            os.makedirs(path)
        export_one_anim_objs(prefix, path)

def main(iflist, prefix, obj_path, phn_path):
    '''
    导出动画obj主函数
    :param iflist: bool   True：phn列表内的动画；False：maya场景内现有的动画
    :param prefix: str   前缀名，比如"ST","base"
    :param obj_path: str   obj导出路径
    :param phn_path: str   phn所在路径
    '''
    if not pm.objExists(prefix + '_Head'):
        return cmds.warning(u'找不到%s模型' % (prefix + '_Head'))
    if not pm.objExists(prefix + '_Teeth'):
        return cmds.warning(u'找不到%s模型' % (prefix + '_Teeth'))

    if not os.path.exists(obj_path+'/%s_speak_anim_base.obj' % prefix):
        export_base_obj(prefix, obj_path)

    if not iflist:
        export_one_anim_objs(prefix, obj_path)
    else:
        export_phn_anim_objs(prefix, obj_path, phn_path)