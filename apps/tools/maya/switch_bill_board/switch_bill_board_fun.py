# -*- coding: utf-8 -*-#
# -------------------------------------------------------
# NAME       : __init__.py
# Describe   : 说明描述
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2025/6/30__16:19
# -------------------------------------------------------
import maya.cmds as cmds
from lib.maya.node.mesh import Mesh
import numpy as np

import math
from method.common import calculate_fun

reload(calculate_fun)

FACEVECTOR = [1.0, 0.0, 0.0]


def get_bill_board_meshs():
    """
    获取场景中所有的BillBoard Mesh
    :return: list
    """
    meshs = cmds.ls(type='mesh')
    bill_board_meshs = []
    for mesh in meshs:
        if cmds.listRelatives(mesh, parent=True, type='transform'):
            parent = cmds.listRelatives(mesh, type='transform', parent=True)[0]
            if parent.endswith('_Billboard'):
                bill_board_meshs.append(parent)
    return bill_board_meshs


def switch_bill_board_meshs_to_face(uv_set_name='map2', distance=0.00001):
    __meshs = get_select_sphere_meshs()
    __judge_sphere=False
    if not __meshs:
        __meshs = get_bill_board_meshs()
        __judge_sphere = judge_sphere_is_bill_board(get_mesh_structure(__meshs[0]))
    else:
        __judge_sphere = True
    if __judge_sphere:
        cmds.select(__meshs)
        ok, result = switch_spheres_to_faces()
        if not ok:
            return False, result
        return True, u'已将Sphere模型转换为BillBoard面模型'
    else:
        __cover_meshs = []
        if not __meshs:
            return False, u'没有BillBoard模型，请检查'
        __meshs = list(set(__meshs))
        for __mesh in __meshs:
            ok, result = switch_bill_board_point_to_face(__mesh, uv_set_name=uv_set_name, distance=distance)
            if not ok:
                return False, result
            __cover_meshs.append(__mesh)
        return True, u'已将BillBoard点模型转换为面模型,请检查'


def switch_bill_board_meshs_to_point(uv_set_name='map2', distance=0.00001):
    bill_board_meshs = get_bill_board_meshs()
    if not bill_board_meshs:
        return False, u'没有BillBoard模型，请检查'
    __judge_sphere = judge_sphere_is_bill_board(get_mesh_structure(bill_board_meshs[0]))
    if __judge_sphere:
        return False, u'BillBoard模型是Sphere类型,请先将Sphere转换为面模型'
    __meshs = list(set(bill_board_meshs))

    for __mesh in __meshs:
        ok, result = switch_bill_board_face_to_point(__mesh, uv_set_name=uv_set_name, distance=distance)
        if not ok:
            return False, result
    return True, u'已将BillBoard面模型转换为点模型,请检查'


def switch_bill_board_meshs_to_sphere(uv_set_name='map2', distance=0.00001):
    bill_board_meshs = get_bill_board_meshs()
    if not bill_board_meshs:
        return False, u'没有BillBoard模型，请检查'
    __judge_sphere = judge_sphere_is_bill_board(get_mesh_structure(bill_board_meshs[0]))
    if __judge_sphere:
        return False, u'BillBoard模型是Sphere类型,请先将Sphere转换为面模型'
    __meshs = list(set(bill_board_meshs))
    for __mesh in __meshs:
        ok, result = judge_mesh_is_bill_board(__mesh)
        if not ok:
            return False, result
        if result == 'model':
            ok, result = switch_face_mesh_bill_board_to_sphere(__mesh, uv_set_name=uv_set_name, distance=distance)
            if not ok:
                return False, result
        elif result == 'point':
            ok, result = switch_bill_board_point_to_face(__mesh, uv_set_name=uv_set_name, distance=distance)
            if not ok:
                return False, result
            ok, result = switch_face_mesh_bill_board_to_sphere(__mesh, uv_set_name=uv_set_name, distance=distance)
            if not ok:
                return False, result
    return True, u'已将BillBoard模型转换为Sphere显示球,请检查'


def __creat_sphere_by_mesh(vtx_list):
    count = 1

    __center_pos = [0, 0, 0]
    vtx_list = sorted(vtx_list)
    pts = [cmds.pointPosition(vtx, w=True) for vtx in vtx_list]
    center = [0, 0, 0]
    for pt in pts:
        center = vector_add(center, pt)
    center = vector_div(center, len(pts))

    width = vector_length(vector_sub(pts[1], pts[0]))
    height = vector_length(vector_sub(pts[3], pts[0]))
    scale = (width + height) / 2.0

    _vector = get_vector(pts[0], pts[1])
    __rotation = get_rotation_by_vector(FACEVECTOR, _vector)

    __sphere_name = 'billboard_sphere_0{}'.format(count)
    if cmds.objExists(__sphere_name):
        while cmds.objExists(__sphere_name):
            count += 1
            __sphere_name = 'billboard_sphere_0{}'.format(count)
    __sphere = cmds.polySphere(name=__sphere_name, radius=0.5, subdivisionsX=10, subdivisionsY=10)[0]
    cmds.polySoftEdge(__sphere, angle=180, ch=1)

    cmds.setAttr(__sphere + ".translate", center[0], center[1], center[2], type="double3")
    cmds.setAttr(__sphere + ".scale", scale, scale, scale, type="double3")
    cmds.setAttr(__sphere + ".rotate", __rotation[0], __rotation[1], __rotation[2], type="double3")
    return True, __sphere


def get_rotation_by_vector(v1, v2):
    return calculate_fun.get_rotation_by_two_vectors(v1, v2)


def normalize(v):
    length = math.sqrt(v[0] * v[0] + v[1] * v[1] + v[2] * v[2])
    return np.array([v[0] / length, v[1] / length, v[2] / length, 0.0])


def get_normal_by_face_vers(face_vers):
    """
    输入面顶点列表，返回法线向量
    :param face_vers: [v1, v2, v3, ...]，每个是maya顶点名
    :return: 法线向量 [x, y, z]
    """
    if len(face_vers) < 3:
        return False, u'面顶点数量不足，无法计算法线向量'
    v1 = cmds.pointPosition(face_vers[0], w=True)
    v2 = cmds.pointPosition(face_vers[1], w=True)
    v3 = cmds.pointPosition(face_vers[2], w=True)
    vector1 = np.array(v2) - np.array(v1)
    vector2 = np.array(v3) - np.array(v1)
    normal = np.cross(vector1, vector2)
    norm = np.linalg.norm(normal)
    if norm == 0:
        return False, u'法线向量长度为0'
    return True, normal / norm


def switch_face_mesh_bill_board_to_sphere(mesh, uv_set_name='map2', distance=0.00001):
    mesh_structure = get_mesh_structure(mesh)
    if not mesh_structure:
        return False, u'该模型没有拓扑结构信息,请检查'
    for k, v in mesh_structure.items():
        if not v or len(v) != 4:
            return False, u'该模型不是四边形面,请检查'
        ok, __sphere = __creat_sphere_by_mesh(v)
        if not ok:
            return False, __sphere
    cmds.delete(mesh)

    return True, u'已将BillBoard面模型转换为Sphere显示球,请检查'


# elif result == 'point':
#     ok, result = switch_bill_board_point_to_face(mesh, uv_set_name=uv_set_name, distance=distance)
#     if not ok:
#         return False, result
#     for k, v in mesh_structure.items():
#         ok, __sphere = __creat_sphere_by_mesh(v)
#         if not ok:
#             return False, __sphere
#     cmds.delete(mesh)
# return True, u'已将BillBoard模型转换为Sphere显示球,请检查'


def get_vector(v1, v2):
    return normalize_vector([v2[0] - v1[0], v2[1] - v1[1], v2[2] - v1[2]])


def normalize_vector(vector):
    length = math.sqrt(vector[0] ** 2 + vector[1] ** 2 + vector[2] ** 2)
    if length == 0:
        return [0, 0, 0]
    return [vector[0] / length, vector[1] / length, vector[2] / length]


def get_select_sphere_meshs():
    meshs = cmds.ls(sl=True, type='transform')
    select_meshs = []
    for mesh in meshs:
        __sphere = False
        if cmds.listRelatives(mesh, s=1, type='mesh'):
            shapes = cmds.listRelatives(mesh, s=1, type='mesh', f=1)
            if not shapes:
                continue
            for __shape in shapes:
                cons = cmds.listConnections('{}.inMesh'.format(__shape), type='polySoftEdge')
                if cons:
                    __sphere = True
                    break
        if __sphere:
            select_meshs.append(mesh)
    return select_meshs


def get_mesh_structure(mesh):
    return Mesh(mesh).get_pology_structure()


def judge_mesh_is_bill_board(mesh):
    mesh_structure = get_mesh_structure(mesh)
    if not mesh_structure:
        return False, u'该模型没有拓扑结构信息,请检查'
    __judge_triangle = jude_mesh_is_triangle(mesh_structure)
    __judge_model = 'point'
    if __judge_triangle:
        __judge_model = judge_mesh_poins_distance(mesh_structure)
        if __judge_model == 'point':
            return True, 'point'
        else:
            return False, u'该模型已三角化，但点之间距离大于0.001,请检查模型是否为坍塌为点的BillBoard模型'
    else:
        __judge_model = judge_mesh_poins_distance(mesh_structure)
        if __judge_model == 'model':
            return True, 'model'
        else:
            return False, u'该模型不是三角化的BillBoard模型，请检查模型是否为未坍塌前的BillBoard面模型'


def switch_bill_board_point_to_face(mesh, uv_set_name='map2', distance=0.00001):
    ok, reslut = judge_mesh_is_bill_board(mesh)
    if not ok:
        return False, reslut

    if reslut == 'model':
        return False, u'该模型已经是模型类型的BillBoard模型,无需转换'

    # cover_structure_to_quad(mesh)
    # cover_mesh_to_quad(mesh)
    ok, result = switch_uv_set(mesh, uv_set_name)
    if ok == False:
        return False, result
    __mesh_structure = get_mesh_structure(mesh)

    ok, __face_vers = cover_mesh_structure_to_quad(__mesh_structure)
    if not ok:
        return False, __face_vers

    for face_vers in __face_vers:
        ok, center_pos = get_center_position(face_vers)
        if not ok:
            return False, center_pos
        for i in range(len(face_vers)):
            ok, result = cover_point_to_face_by_face_vers(face_vers, distance)
            if not ok:
                return False, result

    delete_uv_map(mesh, uv_set_name)
    cover_structure_to_quad(mesh)
    cover_mesh_to_quad(mesh)
    set_vertices_display(mesh, 0)
    remove_history(mesh)

    return True, u'点转换为面成功'


def cover_point_to_face_by_face_vers(face_vers, distance):
    ok, center_pos = get_center_position(face_vers)
    if not ok:
        return False, center_pos
    for i in range(len(face_vers)):
        ok, __distance = get_ver_uv_point(face_vers[i])
        if not ok:
            return False, __distance
        pos = cmds.pointPosition(face_vers[i], w=True)
        __ver_pos = get_position_vector_distance(center_pos, pos, (__distance + distance))
        cmds.xform(face_vers[i], t=(__ver_pos[0], __ver_pos[1], __ver_pos[2]), ws=1)
    return True, u'点转换为面成功'


def cover_uv_to_mesh(mesh):
    """
    将UV转换为Mesh
    :param mesh: str, mesh name
    :return: bool, str
    """
    if not cmds.objExists(mesh):
        return False, u'模型不存在'

    all_uv_sets = cmds.polyUVSet(mesh, query=True, allUVSets=True)
    if 'map1' not in all_uv_sets:
        return False, u'缺少map1 UV集,请检查'

    cmds.polyUVSet(mesh, currentUVSet=True, uvSet='map1')
    cmds.polyMapSewMove(mesh, sew=1)
    return True, u'UV转换为Mesh成功'


def cover_mesh_structure_to_quad(mesh_structure):
    __vers = []
    triangle_vers = []
    if not mesh_structure:
        return False, u'该模型没有拓扑结构信息,请检查'
    for k, v in mesh_structure.items():
        if len(v) == 3:
            triangle_vers.append(sorted([v[0], v[1], v[2]]))
    if not triangle_vers:
        return False, u'该模型没有三角面信息,请检查'

    quad_faces = []
    used_triangles = set()
    for i in range(len(triangle_vers)):
        if i in used_triangles:
            continue
        __triangle_vers = triangle_vers[i]
        for j in range(i + 1, len(triangle_vers)):
            if j in used_triangles:
                continue
            __other_triangle_vers = triangle_vers[j]
            shared_vertices = list(set(__triangle_vers) & set(__other_triangle_vers))
            if len(shared_vertices) == 2:
                quad_face = list(set(__triangle_vers + __other_triangle_vers))
                quad_faces.append(quad_face)
                used_triangles.add(i)
                used_triangles.add(j)
                break
    return True, quad_faces


def delete_uv_map(mesh, uv_set_name='map2'):
    if not cmds.objExists(mesh):
        return False, u'模型不存在'

    all_uv_sets = cmds.polyUVSet(mesh, query=True, allUVSets=True)
    if uv_set_name not in all_uv_sets:
        return False, u'缺少{} UV集,请检查'.format(uv_set_name)

    cmds.polyUVSet(mesh, delete=True, uvSet=uv_set_name)
    return True, u'UV集删除成功'


def switch_bill_board_face_to_point(mesh, uv_set_name='map2', distance=0.00001):
    from apps.publish.process.maya import process_billboard_face
    reload(process_billboard_face)
    ok, reslut = judge_mesh_is_bill_board(mesh)
    if not ok:
        return False, reslut
    if reslut == 'point':
        return False, u'该模型已经是点类型的BillBoard模型,无需转换'
    process_handle = process_billboard_face.ProcessBillboardFace()
    process_handle.copy_uv_set(mesh)
    __mesh_structure = get_mesh_structure(mesh)
    triangulate_mesh(mesh)

    for k, v in __mesh_structure.items():
        process_handle.process_billboard_face_by_data(k, v, distance)
    process_handle.set_meshs_vertex_display([mesh])
    remove_history(mesh)
    return True, u'面转换为点成功'


def remove_history(meshs):
    cmds.bakePartialHistory(meshs, prePostDeformers=True)


def triangulate_mesh(mesh):
    cmds.polyTriangulate(mesh, ch=1)


def set_vertices_display(mesh, display=1):
    attr = '{}.displayVertices'.format(mesh)
    if attr:
        try:
            cmds.setAttr(attr, display)
            return True
        except:
            return False


def get_ver_uv_point(ver):
    _uv = cmds.polyListComponentConversion(ver, tuv=1)
    _uv_point = cmds.polyEditUV(_uv, query=True)
    if not _uv_point:
        return False, u'获取UV点失败，请检查模型是否有UV信息'
    return True, _uv_point[0] / 1.4142


def switch_uv_set(mesh, uv_set_name):
    if not cmds.objExists(mesh):
        return False, u'模型不存在'

    all_uv_sets = cmds.polyUVSet(mesh, query=True, allUVSets=True)
    if uv_set_name not in all_uv_sets:
        return False, u'缺少{} UV集,请检查'.format(uv_set_name)

    cmds.polyUVSet(mesh, currentUVSet=True, uvSet=uv_set_name)
    return True, u'UV集切换成功'


def get_center_position(poins):
    num = len(poins)
    if num == 0:
        return False, u'没有点信息，无法计算中心位置'
    for i in range(num):
        if i == 0:
            center_pos = np.array(cmds.pointPosition(poins[i], w=True))
        else:
            center_pos += np.array(cmds.pointPosition(poins[i], w=True))
    return True, center_pos / num


def get_position_vector_distance(pos01, pos02, distance):
    pos01 = np.array(pos01)
    pos02 = np.array(pos02)
    v = pos02 - pos01
    v_length = np.linalg.norm(v)
    if v_length == 0:
        return pos01
    v = v / v_length
    return pos01 + v * distance


def cover_structure_to_quad(mesh):
    return cmds.polyQuad(mesh, a=30, kgb=0, ktb=0, khe=0, ws=0, ch=1)


def cover_mesh_to_quad(mesh):
    mesh_structure = get_mesh_structure(mesh)
    edges = []
    all_edges = []
    share_edges = []
    vers = []
    faces = []
    if not mesh_structure:
        return False, u'该模型没有拓扑结构信息,请检查'
    for k, v in mesh_structure.items():
        __edges = get_edges_from_face(k)
        for i in range(len(v)):
            edge = tuple(sorted([v[i], v[(i + 1) % len(v)]]))
            if edge not in edges:
                edges.append(edge)
            else:
                for __edge in __edges:
                    __vers = cmds.polyListComponentConversion(__edge, tv=1)
                    if len(__vers) == 2:
                        __vers = tuple(sorted([__vers[0], __vers[1]]))
                    elif len(__vers) == 1:
                        __base = __vers[0].split('[')[0]
                        __ver01 = __vers[0].split('[')[-1].split(':')[0]
                        __ver02 = __vers[0].split('[')[-1].split(':')[-1].split(']')[0]
                        __vers = tuple(sorted(['{}[{}]'.format(__base, __ver01), '{}[{}]'.format(__base, __ver02)]))

                    if (__vers[0] == edge[0] and __vers[-1] == edge[1]) or (
                            __vers[0] == edge[1] and __vers[-1] == edge[0]):
                        share_edges.append(__edge)
    if share_edges:
        for edge in share_edges:
            try:
                cmds.delete(edge)
            except:
                pass
    return True, u'模型转换为四边形成功'


def get_edges_from_face(face):
    base_name = face.split('|')[-1].split('.f[')[0]
    edge_list = []
    edges = cmds.polyInfo(face, fe=True)
    if not edges:
        return []
    for edge in edges:
        __edges_num_list = edges[0].split(":   ")[-1].split(' \n')[0].split("   ")
        for edge_num in __edges_num_list:
            if edge_num != '':
                edge = '{}.e[{}]'.format(base_name, edge_num)
                edge_list.append(edge)
    return edge_list


def judge_mesh_poins_distance(mesh_structure):
    __judge_model = 'model'
    for k, v in mesh_structure.items():
        for i in range(len(v)):
            pos = cmds.pointPosition(v[i], w=1)
            for j in range(len(v)):
                pos_01 = cmds.pointPosition(v[j], w=1)
                if v[i] != v[j]:
                    distance = ((pos[0] - pos_01[0]) ** 2 + (pos[1] - pos_01[1]) ** 2 + (
                            pos[2] - pos_01[2]) ** 2) ** 0.5
                    if distance <= 0.001:
                        __judge_model = 'point'
                        return __judge_model
                    if distance > 0.01:
                        __judge_model = 'model'
                        return __judge_model

    return __judge_model


def jude_mesh_is_triangle(mesh_structure):
    for k, v in mesh_structure.items():
        if len(v) != 3:
            return False
    return True


def judge_sphere_is_bill_board(mesh_structure):
    same_points = []
    points = []
    for k, v in mesh_structure.items():
        if v and len(v) == 3:
            for point in v:
                if point not in points:
                    points.append(point)
                else:
                    same_points.append(point)
    if len(same_points) > 0:
        for i in range(len(same_points)):
            __same = []
            for j in range(len(same_points)):
                if same_points[i] == same_points[j]:
                    __same.append(same_points[j])
            if __same and len(__same) > 4:
                return True
    return False


def switch_bill_board_face_to_sphere(meshs, grp='BillBoard_Sphere_Grp', shader_name='BillBoard_Sphere_Shader',
                                     sg_name='BillBoard_Sphere_ShaderSG'):
    """
    将BillBoard面转换为球体
    :param mesh: str, mesh name
    :param uv_set_name: str, UV set name
    :param distance: float, distance for point conversion
    :return: bool, str
    """
    data_list = []
    for mesh in meshs:
        ok, reslut = judge_mesh_is_bill_board(mesh)
        if not ok:
            return False, reslut

        if reslut == 'point':
            return False, u'BillBoard需要是面类型,请检查'

        mesh_structure = get_mesh_structure(mesh)
        ok, result = create_sphere_by_mesh_structure(mesh_structure, grp, shader_name, sg_name)
        if not ok:
            return False, result
        data_list.extend(result)

    # ok, result = set_sphere_position_and_scale(data_list)
    # if not ok:
    #     return False, result
    # bind_sphere_to_vertices_to(data_list, expression_name="BillBoard_multi_sphere_expr")
    delecte_scriptJob()
    bind_vertices_to_sphere(data_list)
    return True, u'BillBoard面已创建Sphere显示,请检查'


def clear_bill_board_sphere(grp='BillBoard_Sphere_Grp', shader_name='BillBoard_Sphere_Shader',
                            sg_name='BillBoard_Sphere_ShaderSG'):
    delecte_scriptJob()
    if not cmds.objExists(grp) and not cmds.objExists(shader_name) and not cmds.objExists(sg_name):
        return True, u'BillBoard无显示球,无需操作'

    ok, result = clear_billbord_sphere()
    if not ok:
        return False, result

    if cmds.objExists(grp):
        cmds.delete(grp)
    if cmds.objExists(shader_name):
        cmds.delete(shader_name)
    if cmds.objExists(sg_name):
        cmds.delete(sg_name)
    return True, u'BillBoard Sphere显示已清除'


def clear_billbord_sphere():
    clear_list = []
    for _tr in cmds.ls(type='transform'):
        if '_Billboard_sphere0' in _tr.split('|')[-1]:
            clear_list.append(_tr)

    if not clear_list:
        return True, u'没有BillBoard Sphere显示球需要清除'
    cmds.delete(clear_list)
    return True, u'BillBoard Sphere显示球已清除'


def create_sphere_by_mesh_structure(mesh_structure, grp, shader_name, sg_name):
    if not mesh_structure:
        return False, u'该模型没有拓扑结构信息,请检查'

    __data = []
    mesh_name = mesh_structure.keys()[0].split('|')[-1].split('.f[')[0]

    shader_sg = create_lambert_shader_by_mesh_name(shader_name, sg_name)

    if not cmds.objExists(grp):
        cmds.group(empty=True, name=grp)

    count = 1
    for k, v in mesh_structure.items():
        __v_data = {}
        if len(v) != 4:
            return False, u'该模型不是四边形面,请检查'

        __sphere_name = '{}_Billboard_sphere0{}'.format(mesh_name, count)
        if cmds.objExists(__sphere_name):
            while cmds.objExists(__sphere_name):
                count += 1
                __sphere_name = '{}_Billboard_sphere0{}'.format(mesh_name, count)

        __sphere = cmds.polySphere(name=__sphere_name, radius=0.5, subdivisionsX=20, subdivisionsY=20)[0]
        __v_data['object'] = __sphere.split('|')[-1]
        __v_data['vertices'] = v
        cmds.sets(__sphere, forceElement=shader_sg)

        cmds.parent(__sphere, grp)

        __data.append(__v_data)
    return True, __data


def create_lambert_shader_by_mesh_name(shader_name, sg_name):
    if not cmds.objExists(shader_name):
        cmds.shadingNode('lambert', asShader=True, name=shader_name)

    if not cmds.objExists(sg_name):
        cmds.sets(renderable=1, noSurfaceShader=1, em=1, n=sg_name)

    con = cmds.listConnections(shader_name, type='shadingEngine')
    if not con or sg_name not in con:
        try:
            cmds.connectAttr(shader_name + '.outColor', sg_name + '.surfaceShader', force=True)
        except:
            pass
    cmds.setAttr(shader_name + '.color', 0, 0.4, 0, type='double3')
    cmds.setAttr(shader_name + '.transparency', 0.5, 0.5, 0.5, type='double3')
    return sg_name


def delecte_scriptJob():
    for job in cmds.scriptJob(lj=True):
        if "update_sphere" in job:
            job_id = int(job.split(":")[0])
            cmds.scriptJob(kill=job_id, force=True)


def vector_add(v1, v2): return [v1[0] + v2[0], v1[1] + v2[1], v1[2] + v2[2]]


def vector_div(v, scalar): return [v[0] / scalar, v[1] / scalar, v[2] / scalar]


def vector_sub(v1, v2): return [v1[0] - v2[0], v1[1] - v2[1], v1[2] - v2[2]]


def vector_length(v): return math.sqrt(v[0] ** 2 + v[1] ** 2 + v[2] ** 2)


def set_sphere_position_and_scale(data_list):
    if not data_list:
        return False, u'没有提供数据列表'
    for item in data_list:
        vtx_list = item['vertices']
        sphere_name = item['object']
        try:
            pts = [cmds.pointPosition(vtx, w=True) for vtx in vtx_list]
            center = vector_add(pts[0], vector_add(pts[1], vector_add(pts[2], pts[3])))
            center = vector_div(center, 4.0)

            width = vector_length(vector_sub(pts[1], pts[0]))
            height = vector_length(vector_sub(pts[3], pts[0]))
            scale = (width + height) / 2.0

            if not cmds.objExists(sphere_name):
                delecte_scriptJob()
                continue

            cmds.setAttr(sphere_name + ".translate", center[0], center[1], center[2], type="double3")
            cmds.setAttr(sphere_name + ".scale", scale, scale, scale, type="double3")
        except Exception as e:
            print("❌ 错误更新 %s: %s" % (sphere_name, str(e)))
    return True, u'所有球体位置和缩放已更新'


def switch_spheres_to_faces():
    meshs = cmds.ls(sl=True, tr=1)
    if not meshs:
        return False, u'请选择需要转换的模型(球)'
    try:
        cmds.GeometryToBoundingBox(keepOriginal=True)
    except Exception as e:
        pass
    cmds.CenterPivot()
    cmds.DeleteHistory()
    process_meshs = []

    for i in range(len(meshs)):
        short_name = meshs[i].split('|')[-1]
        bbx_mesh = '{}_BBox'.format(short_name)
        if cmds.objExists(bbx_mesh):
            new_name = '{}_Billboard'.format(short_name)
            new_name = cmds.rename(bbx_mesh, new_name)
            if cmds.objExists(new_name):
                process_meshs.append(new_name)

    if not process_meshs:
        return False, '没有模型GeometryToBoundingBox,请检查'

    for __mesh in process_meshs:
        cmds.select(clear=True)
        cmds.select(__mesh)
        cmds.scale(1, 0, 1, r=True)
        cmds.delete(__mesh + '.f[1]', __mesh + '.f[2]', __mesh + '.f[3]')

        cmds.polyAutoProjection()

        remove_history(__mesh)

        merge_mesh_close_ver(__mesh, dis_thr=0.01)
        remove_history(__mesh)
    return True, process_meshs


def merge_mesh_close_ver(mesh, dis_thr=0.01):
    mesh_structure = get_mesh_structure(mesh)
    if not mesh_structure or len(mesh_structure.keys()) == 1:
        return
    __vertives = []
    for i in range(len(mesh_structure.values())):
        __vertives.extend(mesh_structure.values()[i])
    __vertives = list(set(__vertives))
    __vertives = sorted(__vertives)
    __close_vertives = []
    __same_vertives = []
    for i in range(len(__vertives)):
        __vertex_tr = cmds.pointPosition(__vertives[i], w=True)
        _clse_ver = []
        for j in range(len(__vertives)):
            if __vertives[i] != __vertives[j]:
                __distance = get_distance_by_two_v(__vertex_tr, cmds.pointPosition(__vertives[j], w=True))
                if __distance <= dis_thr and __vertives[j] not in __same_vertives:
                    _clse_ver.append(__vertives[j])
                    __same_vertives.append(__vertives[j])
        if _clse_ver and __vertives[i] not in __same_vertives:
            _clse_ver.append(__vertives[i])
            __close_vertives.append(_clse_ver)
    if __close_vertives:
        for i in range(len(__close_vertives)):
            cmds.select(__close_vertives[i])
            cmds.polyMergeVertex(__close_vertives[i], d=dis_thr, am=1, ch=1)
    mesh_structure = get_mesh_structure(mesh)
    if mesh_structure and len(mesh_structure.keys()) > 1:
        merge_mesh_close_ver(mesh, dis_thr * 5)

    # mesh_structure=get_mesh_structure(mesh)
    # if mesh_structure and len(mesh_structure.keys()) >1:
    #     merge_mesh_close_ver(mesh, dis_thr=0.1)


def get_distance_by_two_v(v1, v2):
    return ((v1[0] - v2[0]) ** 2 + (v1[1] - v2[1]) ** 2 + (v1[2] - v2[2]) ** 2) ** 0.5


def bind_sphere_to_vertices_to(data_list, expression_name="BillBoard_multi_sphere_expr"):
    offsets = [(-1, 0, -1), (1, 0, -1), (1, 0, 1), (-1, 0, 1)]
    expr_lines = []
    for k in range(len(data_list)):
        vtx_list = data_list[k]["vertices"]
        sphere = data_list[k]["object"]

        for i, vtx in enumerate(vtx_list):
            mesh = vtx.split(".")[0]
            vtx_id = vtx[vtx.find("[") + 1: vtx.find("]")]
            attr_x = "%s.vtx[%s].pntx" % (mesh, vtx_id)
            attr_y = "%s.vtx[%s].pnty" % (mesh, vtx_id)
            attr_z = "%s.vtx[%s].pntz" % (mesh, vtx_id)

            ox, oy, oz = offsets[i]

            expr_lines.append('%s = %s.translateX + %s.scaleX * %.2f;' % (attr_x, sphere, sphere, ox))
            expr_lines.append('%s = %s.translateY + %s.scaleY * %.2f;' % (attr_y, sphere, sphere, oy))
            expr_lines.append('%s = %s.translateZ + %s.scaleZ * %.2f;' % (attr_z, sphere, sphere, oz))
    expr_text = "\n".join(expr_lines)
    if cmds.objExists(expression_name):
        cmds.delete(expression_name)
    cmds.expression(name=expression_name, s=expr_text)


def bind_vertices_to_sphere(data_list):
    def update_sphere():
        for item in data_list:
            vtx_list = item['vertices']
            sphere_name = item['object']
            try:
                pts = [cmds.pointPosition(vtx, w=True) for vtx in vtx_list]
                center = [0, 0, 0]
                for pt in pts:
                    center = vector_add(center, pt)
                center = vector_div(center, 4.0)

                width = vector_length(vector_sub(pts[1], pts[0]))
                height = vector_length(vector_sub(pts[3], pts[0]))
                scale = (width + height) / 2.0
                if not cmds.objExists(sphere_name):
                    cmds.polySphere(n=sphere_name)

                cmds.setAttr(sphere_name + ".translate", center[0], center[1], center[2], type="double3")
                cmds.setAttr(sphere_name + ".scale", scale, scale, scale, type="double3")
            except Exception as e:
                print("❌ 错误更新 %s: %s" % (sphere_name, str(e)))

    job_list = cmds.scriptJob(lj=True)
    for job in job_list:
        if "update_sphere" in job:
            job_id = int(job.split(":")[0])
            cmds.scriptJob(kill=job_id, force=True)

    cmds.scriptJob(idleEvent=update_sphere, runOnce=False, protected=True)
    update_sphere()
