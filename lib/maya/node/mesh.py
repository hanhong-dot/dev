# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       : mesh
# Describe   : polygon 模型相关函数
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2022/6/29__10:50
# -------------------------------------------------------
import hashlib
import json
import math
import time
import traceback
from functools import partial, wraps
import maya.cmds as cmds
import maya.api.OpenMaya as om2


def logTime(func=None, msg="Elapsed Time:"):
    u"""
    logTime用于统计记录时间
    Elapsed Time:经过的时间， log function running time
    :param func: function get from decorators, defaults to None
    :type func: function, optional
    :param msg: default print message, defaults to "elapsed time:"
    :type msg: str, optional
    :return: decorator function return
    :rtype: dynamic type
    """
    if not func:
        return partial(logTime, msg=msg)

    @wraps(func)
    def wrapper(*args, **kwargs):
        curr = time.time()
        res = func(*args, **kwargs)
        print(msg, time.time() - curr)
        return res

    return wrapper


class Mesh(object):
    """
    Mesh物体类——包含相关操作处理的核心代码
    使用maya.api.OpenMaya——python API 2.0版本编写代码
    """

    def __init__(self, meshName):
        self.meshName = meshName
        try:
            # selList = om2.MSelectionList()
            # selList.add(meshName)
            selList = om2.MGlobal.getSelectionListByName(self.meshName)  # 首先判断物体是否存在
        except:
            raise Exception("Object does not exist")
        obj = selList.getDependNode(0)

        if obj.apiType() == om2.MFn.kTransform:
            dagPath = selList.getDagPath(0)
            dagFn = om2.MFnDagNode(dagPath)
            child = dagFn.child(0)
            if child.apiType() != om2.MFn.kMesh:  # 判断物体是否为mesh类型
                raise Exception("It isn't polygon mesh")
            obj = child
        # 此时的obj只是OpenMaya.MObject类型
        self.mesh = obj
        self.mFnMesh = om2.MFnMesh(self.mesh)


        # 取消以下的可遍历的实例写法，这些实例最好写在要调用的相应方法里。
        # 否则在使用if语句直接获取得到相应值的时候，再查询该值常异常。
        # self.mItEdge = om2.MItMeshEdge(self.mesh)
        # self.mItPoly = om2.MItMeshPolygon(self.mesh)
        # self.mItVertex = om2.MItMeshVertex(self.mesh)
        # self.mItFaceVertex = om2.MItMeshFaceVertex(self.mesh)

    # __str__()返回用户看到的字符串
    def __str__(self):
        return 'MeshName:{}'.format(self.meshName)

    # 而__repr__()返回程序开发者看到的字符串，也就是说，__repr__()是为调试服务的
    __repr__ = __str__

    @property
    def numVertices(self):
        u"""
        返回mesh物体的点数
        """
        return om2.MFnMesh(self.mesh).numVertices  # mesh物体的点数

    @property
    def numEdges(self):
        u"""
        返回mesh物体的边线数
        """
        return om2.MFnMesh(self.mesh).numEdges  # mesh物体的边线数

    @property
    def numNormals(self):
        u"""
        返回mesh物体的法线数
        """
        return om2.MFnMesh(self.mesh).numNormals  # mesh物体的法线数

    @property
    def numFaces(self):
        u"""
        返回mesh物体的面数
        """
        return om2.MFnMesh(self.mesh).numPolygons  # mesh物体的面数

    @property
    def numTris(self):
        u"""
        返回mesh物体的三角面点数
        """
        _data = om2.MFnMesh(self.mesh).getTriangles()
        _num = 0
        if _data:
            for i in range(len(_data[0])):
                if i == 0:
                    _num = _data[0][i]
                else:
                    _num = _num + _data[0][i]
        return _num

    @property
    def currentColorSetName(self):
        u"""
        返回当前的颜色集名称
        """
        return om2.MFnMesh(self.mesh).currentColorSetName()

    @property
    def currentUVSetName(self):
        u"""
        返回当前的UVSet的名称
        """
        return om2.MFnMesh(self.mesh).currentUVSetName()  # mesh物体当前的UVSet

    @property
    def ColorSetNames(self):
        u"""
        返回该mesh物体的所有颜色集名称，元组
        """
        return om2.MFnMesh(self.mesh).getColorSetNames()  # mesh物体所有的颜色集名称

    @property
    def allUVSetNames(self):
        u"""
        返回该mesh物体的所有UVSet名称，元组
        """
        return om2.MFnMesh(self.mesh).getUVSetNames()  # mesh物体所有的UVSet名称

    @property
    def numUVShells(self):
        u"""
        mesh物体当前uv_set的shell数目
        """
        return om2.MFnMesh(self.mesh).getUvShellsIds(uvSet=om2.MFnMesh(self.mesh).currentUVSetName())[0]

    @property
    def numUVs(self):
        u"""
        mesh物体当前UVSet的uv点数目
        """
        return om2.MFnMesh(self.mesh).numUVs(uvSet=om2.MFnMesh(self.mesh).currentUVSetName())

    @property
    def numColors(self):
        u"""
        mesh物体当前颜色集的颜色数目
        """
        return om2.MFnMesh(self.mesh).numColors(colorSet=om2.MFnMesh(self.mesh).currentColorSetName())

    @property
    def getColors(self):
        u"""
        返回mesh当前颜色集的颜色数据
        """
        return om2.MFnMesh(self.mesh).getColors(colorSet=om2.MFnMesh(self.mesh).currentColorSetName())

    @property
    def getFaceVertexColors(self):
        u"""
        返回mesh当前颜色集的面点颜色数据
        """
        return om2.MFnMesh(self.mesh).getFaceVertexColors(colorSet=om2.MFnMesh(self.mesh).currentColorSetName())


    def get_vertex_normals(self,tol=1e-4):
        u"""
        返回mesh当前点的法线数据
        """
        points=self.get_pology_points()
        vertex_normals = []
        mfnMesh= om2.MFnMesh(self.mesh)
        for point in points:
            vertex_index= int(point.split('[')[-1][:-1])
            normals=self.get_not_repetitive_normals_of_vertex(vertex_index,tol)
            vertex_normals.extend(normals)


        return vertex_normals

    def get_num_vertex_normals(self,tol=0.01):
        vertex_normals= self.get_vertex_normals(tol)
        return len(vertex_normals)








    def get_all_normals_of_vertex(self,vertex_index):

        sel = om2.MSelectionList()
        sel.add(self.meshName)
        dagPath = sel.getDagPath(0)
        mfnMesh = om2.MFnMesh(dagPath)

        itMeshVertex = om2.MItMeshVertex(dagPath)
        itMeshVertex.setIndex(vertex_index)
        connected_faces = itMeshVertex.getConnectedFaces()

        normals = []
        for face_id in connected_faces:
            n = mfnMesh.getFaceVertexNormal(face_id, vertex_index,om2.MSpace.kWorld)
            normals.append(n)




        return normals


    def get_not_repetitive_normals_of_vertex(self,vertex_index, tol=1e-4):
        all_normals = self.get_all_normals_of_vertex(vertex_index)
        unique_normals = []
        for n in all_normals:
            is_unique = True
            for un in unique_normals:
                if (n - un).length() <= tol:
                    is_unique = False
                    break
            if is_unique:
                unique_normals.append(n)
        return unique_normals


    def is_vertex_split_normal(self,vertex_index, tol=1e-4):
        normals = self.get_all_normals_of_vertex(vertex_index)
        if not normals:
            return None

        ref = normals[0]
        for n in normals[1:]:
            if (ref - n).length() > tol:
                return False
        return True



    def numVertexNormal(self):
        u"""
        返回mesh当前点的法线数目
        """
        vertex_normals = self.getVertexNormals




    @property
    def getVertexColors(self):
        u"""
        返回mesh当前颜色集的点颜色数据
        """
        return om2.MFnMesh(self.mesh).getVertexColors(colorSet=om2.MFnMesh(self.mesh).currentColorSetName())

    @property
    def UVsDate(self):
        """
        返回mesh当前UVSet的(list(u), list(v))列表数据元组
        """
        u, v = om2.MFnMesh(self.mesh).getUVs(uvSet=self.currentUVSetName)
        # data = [list(u), list(v)]  # 列表返回
        data = (list(u), list(v))  # 元组返回<--最终选用这种方式，主要是为了之后能用u, v = ***通行写法。
        # 其实无论data是使用列表方式，还是元组的方式，
        # 最终通过json.dumps(data)转换str的之后，得到的都是列表字符串形式。
        return data

    @property
    def UVsMd5(self):
        """
        把UVsDate数据转换为字符串，再转为md5值返回。
        """
        return hashlib.md5(json.dumps(self.UVsDate)).hexdigest()

    @property
    def topologyStructure(self):
        """
        拓扑结构数据[[每个面点ID，每个面点ID，...], [], [], .....]
        """
        data = []
        mItPoly = om2.MItMeshPolygon(self.mesh)
        while not mItPoly.isDone():
            # vtx_list = om2.MIntArray()
            vtx_list = mItPoly.getVertices()
            data.append(list(vtx_list))
            try:
                mItPoly.next()
            except:
                mItPoly.next(None)
        return data

    @property
    def topologyMd5(self):
        """
        把topologyStructure数据转换为字符串，再转为md5值返回。
        """
        return hashlib.md5(json.dumps(self.topologyStructure)).hexdigest()

    def get_pology_structure(self):
        structur_data={}

        structure_data=self.topologyStructure
        for i in range(len(structure_data)):
            face_data=[]
            for ver_id in structure_data[i]:
                face_data.append('{}.vtx[{}]'.format(self.meshName, ver_id))
            structur_data['{}.f[{}]'.format(self.meshName, i)]=face_data
        return structur_data

    def get_pology_points(self):
        u"""
        返回mesh物体的点id数据
        """
        points=[]
        mItVertex = om2.MItMeshVertex(self.mesh)
        while not mItVertex.isDone():
            points.append('{}.vtx[{}]'.format(self.meshName, mItVertex.index()))
            mItVertex.next()
        return points


    def get_pology_Vertices(self):
        u"""
        返回mesh物体的点数据
        """
        vertices=[]
        points=om2.MFnMesh(self.mesh).getPoints()
        if points:
            for i in range(len(points)):
                vertices.append([points[i][0], points[i][1], points[i][2]])

        return vertices





    def get_tangents(self):
        return om2.MFnMesh(self.mesh).getTangents()

    def get_point_tangents(self):
        """
        获取每个点对应的切线数据
        返回格式：[{'imp.vtx[1050]': (-0.53, -0.15, -0.82)}]
        """
        tangents = []
        tangents_data = self.get_tangents()
        for vertex_id, tangent in enumerate(tangents_data):
            tangents.append({
                '{}.vtx[{}]'.format(self.meshName, vertex_id): [tangent.x, tangent.y, tangent.z]
            })
        return tangents

    def set_point_tangents(self, tangents_data):
        """
        设置每个点的切线数据
        :param tangents_data: 切线数据，格式为 [{'imp.vtx[1050]': [x, y, z]}, ...]
        """
        tangents = []
        face_vertex_ids = []

        for tangent_info in tangents_data:
            for vertex, tangent in tangent_info.items():
                vertex_id = int(vertex.split('[')[-1][:-1])  # 提取点的索引
                face_vertex_ids.append(vertex_id)
                tangents.append(om2.MVector(*tangent))  # 转换为 MVector

        # 设置切线数据
        self.mFnMesh.setTangents(tangents, face_vertex_ids, om2.MSpace.kWorld)



    def get_normals(self):
        u"""
        返回mesh物体的法线数据
        """
        return om2.MFnMesh(self.mesh).getNormals()

    def get_normals_num(self):
        u"""
        返回mesh物体的法线数目
        """
        normals = self.get_normals()
        normal_list = []
        for i in range(len(normals)):
            normal_list.append('{}'.format([normals[i][0], normals[i][1], normals[i][2]]))
        if normal_list:
            normal_list = list(set(normal_list))
        return len(normal_list)

    def uvToUdim(self, u, v):
        u"""
        return UDIM tile corresponding to UV coord
        """
        return 1000 + (int(u) + 1) + (int(v) * 10)

    def get_uvs_date(self, uv_set):
        """
        获取该uv_set的数据
        """
        u, v = self.mFnMesh.getUVs(uvSet=uv_set)
        data = (list(u), list(v))
        return data

    def get_uvs_num(self, uv_set):
        u"""
        获取当前uv_set的UVs的数目
        """
        return self.mFnMesh.numUVs(uvSet=uv_set)

    def get_udim_list(self, uv_set):
        u"""
        返回当前uv_set的udims值，如[1001, 1002, 1003, 1011, 1012, 1013]
        return a list of udims
        """
        u, v = self.mFnMesh.getUVs(uv_set)
        shell_count, shell_indices = self.mFnMesh.getUvShellsIds(uvSet=uv_set)
        udim_list = set()
        shells = {}
        for x in xrange(0, len(u)):
            if not shells.get(shell_indices[x]):
                shells[shell_indices[x]] = {'min_u': 100, 'min_v': 100, 'max_u': -100, 'max_v': -100}
            shell = shells.get(shell_indices[x])
            shell['min_u'] = min(shell['min_u'], u[x])
            shell['max_u'] = max(shell['max_u'], u[x])
            shell['min_v'] = min(shell['min_v'], v[x])
            shell['max_v'] = max(shell['max_v'], v[x])
        for shell in shells.values():
            min_u = (shell.get('max_u') - shell.get('min_u')) * 0.001 + shell.get('min_u')
            max_u = (shell.get('max_u') - shell.get('min_u')) * 0.999 + shell.get('min_u')
            min_v = (shell.get('max_v') - shell.get('min_v')) * 0.001 + shell.get('min_v')
            max_v = (shell.get('max_v') - shell.get('min_v')) * 0.999 + shell.get('min_v')
            cur_u = min_u
            cur_v = min_v
            while cur_u <= max_u and cur_v <= max_v:
                # udim_list.add(uvToUdim(cur_u, cur_v))
                udim_list.add(1000 + (int(cur_u) + 1) + (int(cur_v) * 10))
                cur_u += 1
                if cur_u > max_u:
                    cur_u = min_u
                    cur_v += 1
        return sorted(udim_list)

    def get_triangles(self):
        u"""
        获取三角面
        Get triangles
        :return: Component list
        :rtype: list
        """
        indices = ['{0}.f[{1}]'.format(self.meshName, i) for i in xrange(self.mFnMesh.numPolygons) if
                   self.mFnMesh.polygonVertexCount(i) == 3]
        return indices

    def get_ngons(self):
        u"""
        获取超过4条边的面（正常为4边面quad）
        Get faces larger than 4 sides
        :return: Component list
        :rtype: list
        """
        indices = ['{0}.f[{1}]'.format(self.meshName, i) for i in xrange(self.mFnMesh.numPolygons) if
                   self.mFnMesh.polygonVertexCount(i) >= 5]
        return indices

    def get_nonmanifold_edges(self):
        u"""
        获取非流形边（存在3个或以上面共一条边），因为这种情况下的局部区域自相交而无法摊开展平为一个平面。
        模型必须为流形（Manifold）
        Non-manifold edges
        :return: edge index
        :rtype: list
        """
        indices = []
        mItEdge = om2.MItMeshEdge(self.mesh)
        while not mItEdge.isDone():
            if mItEdge.numConnectedFaces() > 2:
                # indices.append(mItEdge.index())
                indices.append('{}.e[{}]'.format(self.meshName, mItEdge.index()))
            mItEdge.next()
        return indices

    def get_lamina_faces(self):
        u"""
        层状体面(共享所有边面)
        lamina faces(face sharing all edges)
        :return: Component list
        :rtype: list
        """
        indices = []
        mItPoly = om2.MItMeshPolygon(self.mesh)
        while not mItPoly.isDone():
            if mItPoly.isLamina():
                # indices.append(mItPoly.index())
                indices.append('{}.f[{}]'.format(self.meshName, mItPoly.index()))
            try:
                mItPoly.next()
            except:
                mItPoly.next(None)
        return indices

    def get_bivalent_faces(self):
        u"""
        获取二价面
        bivalent faces
        :return: vertex index
        :rtype: list
        """
        indices = []
        mItVertex = om2.MItMeshVertex(self.mesh)
        while not mItVertex.isDone():
            connect_faces = mItVertex.getConnectedFaces()
            connect_edges = mItVertex.getConnectedEdges()

            if len(connect_faces) == 2 and len(connect_edges) == 2:
                # indices.append(self.mItVertex.index())
                indices.append('{}.vtx[{}]'.format(self.meshName, mItVertex.index()))
            mItVertex.next()
        return indices

    def get_zero_area_faces(self, maxFaceArea=0.00001):
        u"""
        获取零面积面
        zero area faces
        :param float maxFaceArea: max face area
        :return: face index
        :rtype: list
        """
        indices = []
        mItPoly = om2.MItMeshPolygon(self.mesh)
        while not mItPoly.isDone():
            # if mItPoly.getArea() < maxFaceArea:  # 暂取消这种maxFaceArea对比方式，由于小数点后的getArea有损失，准确度不能非常精确。
            #     indices.append('{}.f[{}]'.format(self.meshName, mItPoly.index()))
            if mItPoly.zeroArea():
                indices.append('{}.f[{}]'.format(self.meshName, mItPoly.index()))
            try:
                mItPoly.next()
            except:
                mItPoly.next(None)
        return indices

    def get_border_edges(self):
        u"""
        获取mesh边界边缘
        mesh border edges
        :return: edge index
        :rtype: list
        """
        indices = []
        mItEdge = om2.MItMeshEdge(self.mesh)
        while not mItEdge.isDone():
            if mItEdge.onBoundary():
                # indices.append(mItEdge.index())
                indices.append('{}.e[{}]'.format(self.meshName, mItEdge.index()))
            mItEdge.next()
        return indices

    def get_crease_edges(self):
        u"""
        折痕边缘
        mesh border edges
        :return: edge index
        :rtype: list
        """
        indices = []
        try:
            edge_ids, crease_data = self.mFnMesh.getCreaseEdges()  # 如果没有折痕边的物体直接执行该命名会报错
        except:
            return indices

        for index in xrange(len(edge_ids)):
            if crease_data[index] != 0:
                # indices.append(edge_ids[index])
                indices.append('{}.e[{}]'.format(self.meshName, edge_ids[index]))
        return indices

    def get_zero_length_edges(self, minEdgeLength=0.000001):
        u"""
        获取零长度边
        mesh zero length edges
        :param float minEdgeLength: min edge length
        :return: edge index
        :rtype: list
        """
        indices = []
        mItEdge = om2.MItMeshEdge(self.mesh)
        while not mItEdge.isDone():
            if mItEdge.length() < minEdgeLength:
                # indices.append(mItEdge.index())
                indices.append('{}.e[{}]'.format(self.meshName, mItEdge.index()))
            mItEdge.next()
        return indices

    def has_vertex_pnts_attr(self):
        u"""
        顶点点属性
        """
        pass

    def get_double_faces(self):
        """
        all points common to both faces
        :return: vertex index
        :rtype: list
        """
        vertex_indices = []
        face_id = []
        mItVertex = om2.MItMeshVertex(self.mesh)
        while not mItVertex.isDone():
            connect_faces = mItVertex.getConnectedFaces()
            connect_edges = mItVertex.getConnectedEdges()
            if len(connect_faces) == 5 and len(connect_edges) == 4:

                vertex_indices.append(mItVertex.index())
                if not face_id:
                    face_id = list(connect_faces)
                else:
                    face_id = list(set(face_id).intersection(set(list(connect_faces))))
            mItVertex.next()
        indices = ['{}.f[{}]'.format(self.meshName, i) for i in face_id]
        return indices

    def get_face_normal_reversed(self):
        """
        face normal reversed  面法线翻转
        where we check the winding of the vertices against it's neighbour.
        If any group of two vertices match the order of another group of two,
        the winding is opposite and he normals face in different directions.

        We do a better check on the first normal to make sure it's correct.
        """

        def is_normal_reversed(mItMeshPolygon, mFnMesh):
            """
            Check the normal faces in or out of the model by doing a simple ray cast and
            count results. Evens face out, odds face in.

            This is costly, so we're only doing it for the first poly. Everything else is
            compared to this.

            :param MItMeshPolygon mItMeshPolygon: The current poly face.
            :param MFnMesh mFnMesh: The current mesh object.

            :returns: :class:`bool` True = normal reversed
            """
            space = om2.MSpace.kWorld
            center = om2.MFloatPoint(mItMeshPolygon.center(space=space))
            normal = om2.MFloatVector(mItMeshPolygon.getNormal(space=space))
            point = center + (normal * 0.001)  # has to be just off the surface to not get current poly
            hit_count = 0
            hit_nothing = False
            while not hit_nothing:
                point, _, face_id, _, _, _ = mFnMesh.closestIntersection(point, normal, space, 10000, False)
                if face_id == -1:
                    hit_nothing = True
                    break
                point = point + (normal * 0.001)
                hit_count += 1
            return bool(hit_count & 1)

        # ============================================
        # ============================================
        mesh_list = om2.MSelectionList()
        mesh_list.add(self.meshName)
        dag_path = mesh_list.getDagPath(0)

        mfn_mesh = om2.MFnMesh(dag_path)
        mItPoly = om2.MItMeshPolygon(dag_path)

        visited = set([0])
        incorrect = set([])  # 不正确的
        indices = []

        if is_normal_reversed(mItPoly, mfn_mesh):
            incorrect.add(mItPoly.index())
        while not mItPoly.isDone():
            current = mItPoly.index()
            vertices = mfn_mesh.getPolygonVertices(current)
            connected_faces = mItPoly.getConnectedFaces()
            main_count = len(vertices)

            for face in connected_faces:
                if face in visited:
                    continue
                visited.add(face)
                face_verts = mfn_mesh.getPolygonVertices(face)
                vert_count = len(face_verts)
                is_different = False
                matched = False
                for indexA in range(main_count):
                    indexB = (indexA + 1) % main_count
                    for vert_indexA in range(vert_count):
                        vert_indexB = (vert_indexA + 1) % vert_count
                        matching_verts = all((
                            vertices[indexA] == face_verts[vert_indexA],
                            vertices[indexB] == face_verts[vert_indexB]
                        ))
                        if matching_verts:
                            is_different = True
                            break
                    # face is incorrect if winding is different compared to correct face
                    # or is the same and an incorrect face
                if is_different:
                    if current not in incorrect:
                        incorrect.add(face)
                elif current in incorrect:
                    incorrect.add(face)
            try:
                mItPoly.next()
            except:
                mItPoly.next(None)

        if incorrect:
            indices = ["{}.f[{}]".format(dag_path, i) for i in incorrect]
        return indices

    def get_face_normal_flipped(self):
        """
        face normal flipped  面法线翻转
        """
        pass

    def get_lock_normals(self):
        """
        获取点法线被锁的点
        """
        indices = []
        mItFaceVertex = om2.MItMeshFaceVertex(self.mesh)
        while not mItFaceVertex.isDone():
            vertexId = mItFaceVertex.vertexId()
            normalId = mItFaceVertex.normalId()
            vtx = '{0}.vtx[{1}]'.format(self.meshName, vertexId)
            if self.mFnMesh.isNormalLocked(normalId) and vtx not in indices:
                indices.append(vtx)

            mItFaceVertex.next()
        return indices

    def get_harden_edges(self):
        """
        获取硬化边(排除网格边界边缘边)
        """
        indices = []
        mItEdge = om2.MItMeshEdge(self.mesh)
        while not mItEdge.isDone():
            if not mItEdge.onBoundary() and not mItEdge.isSmooth:
                indices.append('{0}.e[{1}]'.format(self.meshName, mItEdge.index()))
            mItEdge.next()

        return indices

    #  =======================================================================
    #  UV ====================================================================
    #  =======================================================================

    def get_cross_quadrant_uv_faces(self):
        u"""
        获取穿过象限的uv面(不完善，没有可忽略精度)
        uv face cross quadrant
        :return: face index
        :rtype: list
        """
        currentUVSet = self.mFnMesh.currentUVSetName()
        indices = []

        mItPoly = om2.MItMeshPolygon(self.mesh)
        while not mItPoly.isDone():
            hasUVs = mItPoly.hasUVs(currentUVSet)
            if hasUVs:  # 首先要判断面是否有分好UV
                uvs = mItPoly.getUVs()  # uvs——获得为每个面的u列表值与v列表值。
                # 理论上一个面每一个点的uv值必须在同一个象限内，如果该面横跨了多象限，则抓取出来。
                """
                # <editor-fold desc="===方式1===">
                u_quadrant = None  # U象限值
                v_quadrant = None  # V象限值
                for index, uv_coordinates in enumerate(uvs):
                    # u
                    if index == 0:
                        for u_coordinate in uv_coordinates:  # 遍历所有的u坐标值
                            if u_quadrant is None:
                                u_quadrant = int(u_coordinate)
                            if u_quadrant != int(u_coordinate):  # if u_coordinate - u_quadrant >= maxUvBorderDistance:
                                component_name = '{0}.f[{1}]'.format(meshName, face_it.index())
                                if component_name not in indices:
                                    indices.append(component_name)
                    # v
                    if index == 1:
                        for v_coordinate in uv_coordinates:  # 遍历所有的v坐标值
                            if v_quadrant is None:
                                v_quadrant = int(v_coordinate)
                            if v_quadrant != int(v_coordinate):
                                component_name = '{0}.f[{1}]'.format(meshName, face_it.index())
                                if component_name not in indices:
                                    indices.append(component_name)
                # </editor-fold>
                """
                # <editor-fold desc="===方式2===">
                u = uvs[0]
                v = uvs[1]
                udim_list = []
                for i in xrange(0, len(u)):
                    udim_list.append(1000 + (int(u[i]) + 1) + (int(v[i]) * 10))
                if len(set(udim_list)) > 1:
                    component_name = '{0}.f[{1}]'.format(self.meshName, mItPoly.index())
                    if component_name not in indices:
                        indices.append(component_name)
                # </editor-fold>
            try:
                mItPoly.next()
            except:
                mItPoly.next(None)
        return indices

    def get_intersections_uv_udim(self, maxUvBorderDistance=0.001):
        u"""
        获取UDIM边界与uv相交的uv_map点，待续~~~~
        :param str maxUvBorderDistance: max Uv border distance.
        :return:
        :rtype:
        """
        pass

    def get_no_uv_faces(self):
        u"""
        获取未映射UV面
        Non-mapped UV faces
        :return: face index
        :rtype: list
        """
        indices = []
        mItPoly = om2.MItMeshPolygon(self.mesh)
        currentUVSet = self.mFnMesh.currentUVSetName()
        while not mItPoly.isDone():
            hasUVs = mItPoly.hasUVs(currentUVSet)
            if not hasUVs:
                indices.append('{0}.f[{1}]'.format(self.meshName, mItPoly.index()))
            try:
                mItPoly.next()
            except:
                mItPoly.next(None)
        return indices

    def get_zero_uv_faces(self, minUVArea=0.000001):
        u"""
        获取零面积Uv面
        Zero-area Uv faces
        :param float minUVArea: default 0.000001'
        :return: face index
        :rtype: list
        """
        indices = []
        mItPoly = om2.MItMeshPolygon(self.mesh)
        currentUVSet = self.mFnMesh.currentUVSetName()
        while not mItPoly.isDone():
            hasUVs = mItPoly.hasUVs(currentUVSet)
            if hasUVs:  # 首先要判断面是否有分好UV
                # area = mItPoly.getUVArea(currentUVSet)
                # if math.sqrt(area) < minUVArea:
                #     indices.append('{}.f[{}]'.format(self.meshName, mItPoly.index()))
                if mItPoly.zeroUVArea(currentUVSet):
                    indices.append('{}.f[{}]'.format(self.meshName, mItPoly.index()))
            try:
                mItPoly.next()
            except:
                mItPoly.next(None)
        return indices

    def get_negative_space_uvs(self):
        """
        获取在负象限空间中的UV
        UVs in negative space
        :return: UV index
        :rtype: list
        """
        indices = []
        currentUVSet = self.mFnMesh.currentUVSetName()
        uList, vList = self.mFnMesh.getUVs(uvSet=currentUVSet)

        for i, u in enumerate(uList):
            uv_map = '{}.map[{}]'.format(self.meshName, i)
            if u < 0.0 and uv_map not in indices:
                indices.append(uv_map)
            if vList[i] < 0.0 and uv_map not in indices:
                indices.append(uv_map)
        return indices

    def get_reversed_uv_faces(self):
        u"""
        获取uv翻转面
        """
        indices = []
        currentUVSet = self.mFnMesh.currentUVSetName()
        mItPoly = om2.MItMeshPolygon(self.mesh)
        while not mItPoly.isDone():
            hasUVs = mItPoly.hasUVs(currentUVSet)
            if hasUVs:  # 首先要判断该面是否有分好UV。如果没有UV，就不用判断UV翻转不翻转的情况。
                flip = self.mFnMesh.isPolygonUVReversed(mItPoly.index())
                if flip:
                    indices.append('{0}.f[{1}]'.format(self.meshName, mItPoly.index()))
            try:
                mItPoly.next()
            except:
                mItPoly.next(None)
        return indices

    # @logTime
    def get_overlap_uv_faces(self):
        u"""
        获取uv重叠面，其一方式
        Return overlapping faces
        """

        def create_bounding_circle(meshfn):
            """
            Parameter: meshfn - MFnMesh
            Represent a face by a center and radius, i.e.
            center = [center1u, center1v, center2u, center2v, ... ]
            radius = [radius1, radius2,  ... ]
            return (center, radius)
            """
            center = []
            radius = []
            for i in xrange(meshfn.numPolygons):
                # get uvs from face
                uarray = []
                varray = []
                for j in range(len(meshfn.getPolygonVertices(i))):
                    try:  # 排除一些物体没有uv的情况
                        uv = meshfn.getPolygonUV(i, j)
                        uarray.append(uv[0])
                        varray.append(uv[1])
                    except:
                        pass

                # loop through all vertices to construct edges/rays
                cu = 0.0
                cv = 0.0
                for j in range(len(uarray)):
                    cu += uarray[j]
                    cv += varray[j]
                if uarray:
                    cu /= len(uarray)
                if varray:
                    cv /= len(varray)
                rsqr = 0.0
                for j in range(len(varray)):
                    du = uarray[j] - cu
                    dv = varray[j] - cv
                    dsqr = du * du + dv * dv
                    rsqr = dsqr if dsqr > rsqr else rsqr

                center.append(cu)
                center.append(cv)
                radius.append(math.sqrt(rsqr))

            return center, radius

        def create_ray_given_face(meshfn, faceId):
            """
            Represent a face by a series of edges(rays), i.e.
            orig = [orig1u, orig1v, orig2u, orig2v, ... ]
            vec  = [vec1u,  vec1v,  vec2u,  vec2v,  ... ]
            return false if no valid uv's.
            return (true, orig, vec) or (false, None, None)
            """
            orig = []
            vec = []
            # get uvs
            uarray = []
            varray = []
            for i in range(len(meshfn.getPolygonVertices(faceId))):
                try:  # 排除一些物体没有uv的情况
                    uv = meshfn.getPolygonUV(faceId, i)
                    uarray.append(uv[0])
                    varray.append(uv[1])
                except:
                    pass

            if len(uarray) == 0 or len(varray) == 0:
                return False, None, None

            # loop throught all vertices to construct edges/rays
            if uarray and varray:
                u = uarray[-1]
                v = varray[-1]
                for i in xrange(len(uarray)):
                    orig.append(uarray[i])
                    orig.append(varray[i])
                    vec.append(u - uarray[i])
                    vec.append(v - varray[i])
                    u = uarray[i]
                    v = varray[i]

            return True, orig, vec

        def area(orig):
            """
            area
            """
            sum = 0.0
            num = len(orig) / 2
            for i in xrange(num):
                idx = 2 * i
                idy = (i + 1) % num
                idy = 2 * idy + 1
                idy2 = (i + num - 1) % num
                idy2 = 2 * idy2 + 1
                sum += orig[idx] * (orig[idy] - orig[idy2])

            return math.fabs(sum) * 0.5

        def check_crossing_edges(face1Orig, face1Vec, face2Orig, face2Vec):
            """
            Check if there are crossing edges between two faces. Return true
            if there are crossing edges and false otherwise. A face is represented
            by a series of edges(rays), i.e.
            faceOrig[] = [orig1u, orig1v, orig2u, orig2v, ... ]
            faceVec[]  = [vec1u,  vec1v,  vec2u,  vec2v,  ... ]
            """
            face1Size = len(face1Orig)
            face2Size = len(face2Orig)
            for i in xrange(0, face1Size, 2):
                o1x = face1Orig[i]
                o1y = face1Orig[i + 1]
                v1x = face1Vec[i]
                v1y = face1Vec[i + 1]
                n1x = v1y
                n1y = -v1x
                for j in xrange(0, face2Size, 2):
                    # Given ray1(O1, V1) and ray2(O2, V2)
                    # Normal of ray1 is (V1.y, V1.x)
                    o2x = face2Orig[j]
                    o2y = face2Orig[j + 1]
                    v2x = face2Vec[j]
                    v2y = face2Vec[j + 1]
                    n2x = v2y
                    n2y = -v2x

                    # Find t for ray2
                    # t = [(o1x-o2x)n1x + (o1y-o2y)n1y] / (v2x * n1x + v2y * n1y)
                    denum = v2x * n1x + v2y * n1y
                    # Edges are parallel if denum is close to 0.
                    if math.fabs(denum) < 0.000001:
                        continue
                    t2 = ((o1x - o2x) * n1x + (o1y - o2y) * n1y) / denum
                    if (t2 < 0.00001 or t2 > 0.99999):
                        continue

                    # Find t for ray1
                    # t = [(o2x-o1x)n2x + (o2y-o1y)n2y] / (v1x * n2x + v1y * n2y)
                    denum = v1x * n2x + v1y * n2y
                    # Edges are parallel if denum is close to 0.
                    if math.fabs(denum) < 0.000001:
                        continue
                    t1 = ((o2x - o1x) * n2x + (o2y - o1y) * n2y) / denum

                    # Edges intersect
                    if (t1 > 0.00001 and t1 < 0.99999):
                        return 1

            return 0

        # ======================================================
        # 主函数=================================================
        # ======================================================
        faces = []
        mFnMesh = om2.MFnMesh(self.mesh)

        center, radius = create_bounding_circle(mFnMesh)
        for i in xrange(mFnMesh.numPolygons):
            rayb1, face1Orig, face1Vec = create_ray_given_face(mFnMesh, i)
            if not rayb1:
                continue
            cui = center[2 * i]
            cvi = center[2 * i + 1]
            ri = radius[i]
            # Exclude the degenerate face
            # if(area(face1Orig) < 0.000001) continue;
            # Loop through face j where j != i
            for j in range(i + 1, mFnMesh.numPolygons):
                cuj = center[2 * j]
                cvj = center[2 * j + 1]
                rj = radius[j]
                du = cuj - cui
                dv = cvj - cvi
                dsqr = du * du + dv * dv
                # Quick rejection if bounding circles don't overlap
                if (dsqr >= (ri + rj) * (ri + rj)):
                    continue

                rayb2, face2Orig, face2Vec = create_ray_given_face(mFnMesh, j)
                if not rayb2:
                    continue
                # Exclude the degenerate face
                # if(area(face2Orig) < 0.000001): continue;
                if check_crossing_edges(face1Orig, face1Vec, face2Orig, face2Vec):
                    face1 = '%s.f[%d]' % (mFnMesh.name(), i)
                    face2 = '%s.f[%d]' % (mFnMesh.name(), j)
                    if face1 not in faces:
                        faces.append(face1)
                    if face2 not in faces:
                        faces.append(face2)
        return faces

    # @logTime
    def get_uv_overlap(self):
        """
        使用的是maya2018之后版本内置了该方法函数
        """
        indices = cmds.polyUVOverlap('{}.f[:]'.format(self.meshName), noc=True)
        if indices:
            return indices

    def maya_to_unity_vertices(self):
        sel = om2.MSelectionList()
        sel.add(self.meshName)


        dag_path = sel.getDagPath(0)
        mesh_fn = om2.MFnMesh(dag_path)
        vertices = mesh_fn.getPoints(om2.MSpace.kWorld)
        it_poly = om2.MItMeshPolygon(dag_path)

        unity_vertices = []
        unity_indices = []
        vertex_map = {}

        while not it_poly.isDone():
            face_vert_count = it_poly.polygonVertexCount()
            for i in range(face_vert_count):
                vtx_idx = it_poly.vertexIndex(i)
                try:
                    uv = it_poly.getUV(i)
                except:
                    uv = (0.0, 0.0)
                normal = it_poly.getNormal(i, om2.MSpace.kWorld)

                key = (vtx_idx,
                       round(uv[0], 6), round(uv[1], 6),
                       round(normal.x, 6), round(normal.y, 6), round(normal.z, 6))
                if key not in vertex_map:
                    vertex_map[key] = len(unity_vertices)
                    unity_vertices.append({
                        'pos': (vertices[vtx_idx].x, vertices[vtx_idx].y, vertices[vtx_idx].z),
                        'normal': (normal.x, normal.y, normal.z),
                        'uv': (uv[0], uv[1])
                    })
                unity_indices.append(vertex_map[key])

            try:
                it_poly.next(None)
            except:
                it_poly.next()

        return unity_vertices, unity_indices

    def maya_to_unity_mesh_num(self):
        """
        计算maya转unity后的mesh顶点数目
        """
        unity_vertices, _ = self.maya_to_unity_vertices()
        return len(unity_vertices)

class MeshUV(Mesh):
    u"""
    继承于Mesh类
    """

    @logTime
    def __eq__(self, other):
        u"""
        可常用于直接对比两个mesh物体UV是否一致
        用法如：print(MeshUV(sourceObject) == MeshUV(targetObject))
        uvMd5对比方式，准确丝毫不差。
        """
        if self.numUVShells != other.numUVShells or self.numUVs != other.numUVs:
            return False
        # 只有当物体的UVShells、uvs的数目一致的时候才进行uvMd5的对比，毕竟转换uv数据为MD5会比较耗时。
        return self.UVsMd5 == other.UVsMd5


class MeshTopology(Mesh):
    """
    继承于Mesh类
    """

    @logTime
    def __eq__(self, other):
        """
        可常用于直接对比两个mesh物体Topology是否一致
        用法如：print(MeshTopology(sourceObject) == MeshTopology(targetObject))
        topologyMd5对比方式，准确丝毫不差。
        """
        if self.numVertices != other.numVertices or self.numEdges != other.numEdges or self.numFaces != other.numFaces:
            return False
        # 只有当点-线-面数一致的时候才进行topologyMd5的对比，毕竟转换拓扑数据为MD5会比较耗时。
        return self.topologyMd5 == other.topologyMd5


