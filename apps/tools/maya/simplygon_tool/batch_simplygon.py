# -*- coding: utf-8 -*-
# author: linhuan
# file: batch_simplygon.py
# time: 2025/11/1 13:22
# description:
import sys
import re
sys.path.append('z:/dev')
import maya.cmds as cmds
from lib.maya.plugin import plugin_load
import os
from lib.maya.process.export_fbx import export_fbx
from lib.common.log import Logger
import shutil
NOTNEEDPROCESSDIR='Z:/TD/fbx_process/miss_fbx_NotNeedProcess'



class BatchSimplygon(object):
    def __init__(self, input_fbx_dir, tex_dir, output_dir,error_dir=None):
        self.__current_time = self.__get_current_time_str()
        log_file = r'Z:\TD\fbx_process\logs\batch_simplygon_{}.log'.format(self.__current_time)
        self.__logger = Logger(log_file)
        self.__input_fbx_dir = input_fbx_dir.replace('\\', '/')
        self.__tex_dir = tex_dir.replace('\\', '/')
        self.__plant_json_file = r'Z:\dev\apps\tools\maya\simplygon_tool\vegetation.json'
        self.__object_json_file = r'Z:\dev\apps\tools\maya\simplygon_tool\object.json'
        self.__error_dir= error_dir

        self.__output_dir = output_dir

    def __get_current_time_str(self):
        import time
        return time.strftime("%Y%m%d-%H%M%S", time.localtime())

    def __load_plugin(self):
        plugin_list = ['SimplygonMaya2018', 'fbxmaya', 'SimplygonMaya2018UI']
        return plugin_load(plugin_list)

    def run(self):
        return self.__batch_process()

    def __judge_mode(self, fbx_file):
        fbx_file = fbx_file.replace('\\', '/')
        meshs=self._get_all_meshs()
        second_part = fbx_file.split(self.__input_fbx_dir)[-1].split('/')[1]
        threed_part = fbx_file.split(self.__input_fbx_dir)[-1].split('/')[2]
        if (second_part.lower() == 'plant' and threed_part != 'tree') or second_part.lower() == 'plantflowers' and (meshs and len(meshs)<=1):
            self.__mode = 'plant'
            self.__json_file = self.__plant_json_file
        else:
            self.__mode = 'object'
            self.__json_file = self.__object_json_file

    def __batch_process(self):
        self.__load_plugin()
        fbx_files = self.__get_fbx_files()
        self.__logger.info("Found {} FBX files to process.".format(len(fbx_files)))

        process_fbx_list = []
        for fbx_file in fbx_files:
            ok, result = self.process_fbx_file(fbx_file)
            if not ok:
                self.__logger.error("Failed to process FBX: {}. Reason: {}".format(fbx_file, result))
                if self.__error_dir:
                    self.copy_fbx_file_to_error_dir(fbx_file)
                cmds.file(new=1, f=1)
                continue
            output_fbx=result
            process_fbx_list.append(output_fbx)
            cmds.file(new=1, f=1)
        if not process_fbx_list:
            self.__logger.info("No FBX files were processed.")
        self.__logger.info("Batch processing completed.")
        self.__logger.info("Processed FBX Number: {}".format(len(process_fbx_list)))
        return True, process_fbx_list


    def copy_fbx_file_to_error_dir(self,fbx_file):
        if not self.__error_dir:
            return
        fbx_file = fbx_file.replace('\\', '/')
        __dir, __file = os.path.split(fbx_file)
        __base_dir = __dir.split(self.__input_fbx_dir)[-1]
        output_fbx = '{}/{}/{}'.format(self.__error_dir, __base_dir, __file).replace('\\', '/')
        output_fbx_dir = os.path.dirname(output_fbx)
        if not os.path.exists(output_fbx_dir):
            os.makedirs(output_fbx_dir)
        shutil.copy2(fbx_file, output_fbx)
    def process_fbx_file(self,fbx_file):

        fbx_file = fbx_file.replace('\\', '/')
        self.__logger.info("Processing file: {}".format(fbx_file))
        __dir, __file = os.path.split(fbx_file)
        __base_name = os.path.splitext(__file)[0]
        __base_dir = __dir.split(self.__input_fbx_dir)[-1]
        output_fbx = '{}/{}/{}'.format(self.__output_dir, __base_dir, __file).replace('\\', '/')
        output_fbx_dir = os.path.dirname(output_fbx)
        if not os.path.exists(output_fbx_dir):
            os.makedirs(output_fbx_dir)
        self.__open_fbx_file(fbx_file)
        self.__judge_mode(fbx_file)
        tex_dir = ''
        check, result = self.check_LOD1_exists()
        if not check:
            self.__logger.error("LOD1 check failed for file: {}. Reason: {}".format(fbx_file, result))
            return False, result
        if self.__mode == 'plant':
            ok, result = self._assign_simplygon_materials(fbx_file)
            if not ok:
                self.__logger.error("Material assignment failed for file: {}. Reason: {}".format(fbx_file, result))
                return False,result
            tex_dir = result

        ok, result = self.__simplygon_fbx_reduction_by_json()
        if not ok:
            self.__logger.error("Simplygon processing failed for file: {}. Reason: {}".format(fbx_file, result))
            return False,result

        if self.__mode == 'plant':
            ok, result = self._process_plant(tex_dir, __base_name)
            if not ok:
                self.__logger.error("Plant processing failed for file: {}. Reason: {}".format(fbx_file, result))
                return False,result
        __exported_objs = self.__get_all_exported_objects()
        if not __exported_objs:
            self.__logger.error("No exportable objects found in file: {}".format(fbx_file))
            return False,"No exportable objects found"
        self.__export_fbx(__exported_objs, output_fbx)
        self.__logger.info("Processed and exported: {}".format(output_fbx))


        return True,output_fbx


    def check_LOD1_exists(self):
        meshs=self._get_all_meshs()
        for mesh in meshs:
            __short_name=mesh.split('|')[-1]
            if '_LOD1' in __short_name:
                return False,'LOD1 exists:{}'.format(mesh)
        return True,'No LOD1 exists'



    def get_not_need_to_process_fbxs(self):
        if not NOTNEEDPROCESSDIR or not os.path.exists(NOTNEEDPROCESSDIR):
            return []
        fbx_list=[]
        for root, dirs, files in os.walk(NOTNEEDPROCESSDIR):
            for file in files:
                if file.lower().endswith('.fbx') and '.meta' not in file.lower():
                    fbx_file = os.path.join(root, file)
                    fbx_file = fbx_file.replace('\\', '/')
                    fbx_list.append(fbx_file)
        if not fbx_list:
            return []
        __not_to_process_fbx_list=[]
        for fbx_path in fbx_list:
            fbx_path=fbx_path.replace('\\','/')
            base_name=fbx_path.split(NOTNEEDPROCESSDIR)[-1].lstrip('/')
            __not_to_process_fbx_list.append(base_name)
        return __not_to_process_fbx_list


    def _process_plant(self, tex_dir, base_name):
        ok, reslut = self.__plant_process_obj(base_name)
        if not ok:
            return False, reslut
        _billboard = reslut
        self.__logger.info("Processing plant billboard material for: {}".format(_billboard))
        ok, reslut = self.porcess_plant_billboard_material(tex_dir, _billboard,base_name)
        if not ok:
            return False, reslut
        return True, "Plant processing completed for: {}".format(base_name)

    def _process_plant_with_txt(self, tex_dir, base_name):
        ok, reslut = self.__plant_process_obj(base_name)
        if not ok:
            return False, reslut
        _billboard = reslut
        self.__logger.info("Processing plant billboard material for: {}".format(_billboard))
        ok, reslut = self.porcess_plant_billboard_material(tex_dir, _billboard,base_name)
        if not ok:
            return False, reslut
        self.__rename_palant_shader(base_name)
        return True, "Plant processing completed for: {}".format(base_name)


    def porcess_plant_billboard_material(self, tex_dir, billboard_obj,base_name):
        _shader = self.__get_shader_from_billboard(billboard_obj)
        self.__logger.info("Found shader {} for billboard {}".format(_shader, billboard_obj))
        _color_file_path = ''
        _mask_file_path = ''
        if not _shader:
            return False, "No shader found for billboard: {}".format(billboard_obj)
        _color_tex_file = cmds.listConnections('{}.color'.format(_shader))
        if not _color_tex_file:
            return False, "No color texture file connected to shader: {}".format(_shader)
        _color_tex_file_node = _color_tex_file[0]
        _color_file_path = cmds.getAttr('{}.fileTextureName'.format(_color_tex_file_node))
        if not _color_file_path:
            return False, "No file path found for texture node: {}".format(_color_tex_file_node)
        if not os.path.exists(_color_file_path):
            return False, "Texture file does not exist: {}".format(_color_file_path)
        _color_file_path = _color_file_path.replace('\\', '/')
        # _ext = os.path.splitext(_color_file_path)[-1]
        # if _ext.lower() == '.tga':
        #     ok,reslut=self.__cover_tga_to_tif(_color_file_path)
        #     if not ok:
        #         return False,reslut
        #     _color_file_path=reslut



        __dir, __color_file = os.path.split(_color_file_path)
        __base_name, __ext = os.path.splitext(__color_file)
        __color_file_new='{}_d_billboard{}'.format(base_name,__ext)

        _color_file_new_path = '{}/{}'.format(tex_dir, __color_file_new).replace('\\', '/')

        self.__copy_file(_color_file_path, _color_file_new_path)
        if _color_file_new_path:
            cmds.setAttr('{}.fileTextureName'.format(_color_tex_file_node), _color_file_new_path, type='string')

        _transition_tex_file = cmds.listConnections('{}.transparency'.format(_shader))

        if _transition_tex_file:
            _transition_tex_file_node = _transition_tex_file[0]
            _transition_file_path = cmds.getAttr('{}.fileTextureName'.format(_transition_tex_file_node))

            if _transition_file_path:
                _transition_file_path = _transition_file_path.replace('\\', '/')
            if _transition_file_path and os.path.exists(_transition_file_path):
                __dir, __transition_file = os.path.split(_transition_file_path)
                __ext = os.path.splitext(__transition_file)[-1]
                __transition_file_new_name = '{}_transition_billboard{}'.format(base_name, __ext)
                _transition_file_new_path = '{}/{}'.format(tex_dir, __transition_file_new_name).replace('\\', '/')
                self.__copy_file(_transition_file_path, _transition_file_new_path)
                if _transition_file_new_path and os.path.exists(_transition_file_new_path):
                    cmds.setAttr('{}.fileTextureName'.format(_transition_tex_file_node), _transition_file_new_path,
                                 type='string')


        _mask_tex_file = cmds.listConnections('{}.ambientColor'.format(_shader))
        if _mask_tex_file:
            _mask_tex_file_node = _mask_tex_file[0]
            _mask_file_path = cmds.getAttr('{}.fileTextureName'.format(_mask_tex_file_node))

            if _mask_file_path:
                _mask_file_path = _mask_file_path.replace('\\', '/')
            if _mask_file_path and os.path.exists(_mask_file_path):
                __dir, __mask_file = os.path.split(_mask_file_path)
                _mask_ext = os.path.splitext(__mask_file)[-1]
                _mask_file_new_name = 'alter_{}_mask_billboard{}'.format(base_name, _mask_ext)
                _mask_file_new_path = '{}/{}'.format(tex_dir, _mask_file_new_name).replace('\\', '/')
                self.__copy_file(_mask_file_path, _mask_file_new_path)
                if _mask_file_new_path and os.path.exists(_mask_file_new_path):
                    cmds.setAttr('{}.fileTextureName'.format(_mask_tex_file_node), _mask_file_new_path, type='string')

        return True, "Billboard material processing completed for: {}".format(billboard_obj)



    def __rename_palant_shader(self,base):
        reduce_mat="simplygon_reduce_mat"
        new_shader_name="{base}_mat".format(base=base)
        simply_cast_mat="SimplygonCastMaterial"
        new_simply_cast_mat="{base}_billboard_mat".format(base=base)
        self.__rename_shader(reduce_mat,new_shader_name)
        self.__rename_shader(simply_cast_mat,new_simply_cast_mat)

    def __rename_shader(self, old_shader_name, new_shader_name):
        if not cmds.objExists(old_shader_name):
            return False, "Shader does not exist: {}".format(old_shader_name)
        try:
            cmds.rename(old_shader_name, new_shader_name)
            return True, new_shader_name
        except Exception as e:
            return False, "Failed to rename shader from {} to {}. Reason: {}".format(old_shader_name, new_shader_name, str(e))


    def __copy_file(self, src_file, dst_file):
        dst_dir = os.path.dirname(dst_file)
        if not os.path.exists(dst_dir):
            os.makedirs(dst_dir)
        try:
            shutil.copy2(src_file, dst_file)
            return True, dst_file
        except Exception as e:
            return False, "Failed to copy file from {} to {}. Reason: {}".format(src_file, dst_file, str(e))

    def __cover_tga_to_tif(self, tga_file):
        if not os.path.exists(tga_file):
            return False, "Texture file does not exist: {}".format(tga_file)

    def __get_shader_from_billboard(self, billboard_obj):
        shapes = cmds.listRelatives(billboard_obj, s=1, ni=1, f=1)
        if not shapes:
            return None
        shader = None

        sg = cmds.listConnections(shapes[0], type='shadingEngine')
        if not sg:
            return False, "No shading group for billboard: {}".format(billboard_obj)
        shader_node = cmds.listConnections('{}.surfaceShader'.format(sg[0]))
        if shader_node:
            shader = shader_node[0]

        return shader

    def __plant_process_obj(self, base_name):
        _grp= self._get_group(base_name)
        if not _grp:
            _grp = self._creat_group(base_name)
        if not _grp:
            return False, "No group : {}".format(base_name)
        mesh_objs = self._get_meshs_in_group(_grp)
        if not mesh_objs:
            return False, "No mesh in group : {}".format(base_name)
        _billboard = self._get_billboard()
        if not _billboard:
            return False, "No billboard found"
        _billboard_new_name = '{}_LOD{}'.format(base_name, len(mesh_objs))
        self.__logger.info("Renaming billboard {} to {}".format(_billboard[0], _billboard_new_name))
        cmds.rename(_billboard[0], _billboard_new_name)
        try:
            cmds.parent(_billboard_new_name, _grp)
        except:
            pass
        return True, _billboard_new_name

    def _get_billboard(self):
        return cmds.ls('BillboardCloudProxy_0_LOD*', tr=1)

    def _get_group(self, base_name):
        objs = cmds.ls(base_name + '*', tr=1, l=1)
        group_objs = []
        if not objs:
            return group_objs
        for obj in objs:
            shapes = cmds.listRelatives(obj, s=1, ni=1, f=1)
            if not shapes:
                group_objs.append(obj)
        if not group_objs:
            return None
        return group_objs[0]

    def _creat_group(self,base_name):
        if cmds.objExists(base_name):
            return base_name
        grp=cmds.group(em=1, n=base_name)
        __all_meshs=self._get_all_meshs()
        if __all_meshs:
            cmds.parent(__all_meshs,grp)

        return base_name


    def _get_all_meshs(self):
        meshs=cmds.ls(type='mesh',l=1)
        __list=[]
        if not meshs:
            return []
        for mesh in meshs:
            tr=cmds.listRelatives(mesh,p=1,type='transform')
            if tr:
                __list.append(tr[0])
        return __list


    def _get_meshs_in_group(self, grp):
        mesh_objs = []
        ad_meshs = cmds.listRelatives(grp, ad=1, type='mesh', f=1)
        if not ad_meshs:
            return mesh_objs
        for mesh in ad_meshs:
            tr = self._get_mesh_tr(mesh)
            if tr and '_LOD' in tr:
                mesh_objs.append(tr)
        return mesh_objs

    def _get_mesh_tr(self, mesh):
        tr = cmds.listRelatives(mesh, p=1, f=1)
        if not tr:
            return None
        return tr[0]

    def _assign_simplygon_materials(self, fbx_file):
        mesh_objects = cmds.ls(type='mesh')
        if not mesh_objects:
            return False, "No mesh objects found"

        ok, reslut = self._create_simplygon_metrials(fbx_file)
        if not ok:
            return False, reslut
        sg, fbx_dir = reslut
        for mesh in mesh_objects:
            tr = cmds.listRelatives(mesh, p=1, f=1)
            if not tr:
                continue
            tr = tr[0]

            cmds.sets(tr, e=1, forceElement=sg)

        return True, fbx_dir

    def _create_simplygon_metrials(self, fbx_file, type='lambert', shader_name="simplygon_reduce_mat"):
        fbx_file = fbx_file.replace('\\', '/')
        __dir, __file = os.path.split(fbx_file)
        __base_dir = __dir.split(self.__input_fbx_dir)[-1]
        __fbx_dir = '{}/{}'.format(self.__tex_dir, __base_dir).replace('\\', '/')
        __base_name = os.path.splitext(__file)[0]
        __tex_data = self.__get_tif_files_from_dir_by_base_name(__fbx_dir, __base_name)
        if not __tex_data:
            return False, "No texture files found for {}".format(fbx_file)
        mask_tif = __tex_data.get('mask_tif', '')
        d_tif = __tex_data.get('d_tif', '')
        if not d_tif:
            return False, "No D texture file found for {}".format(fbx_file)

        sg = '{}SG'.format(shader_name)
        if cmds.ls(shader_name, type='lambert'):
            cmds.delete(shader_name)
        if cmds.ls(sg, type='shadingEngine'):
            cmds.delete(sg)

        shader = cmds.shadingNode(type, asShader=True, n=shader_name)

        sg = cmds.sets(renderable=1, noSurfaceShader=1, em=1, n=sg)

        cmds.connectAttr(('%s.outColor' % shader), ('%s.surfaceShader' % sg))

        if d_tif:
            file_node_d = cmds.shadingNode('file', asTexture=1, isColorManaged=1, n='{}_d_file'.format(shader_name))
            cmds.setAttr('{}.fileTextureName'.format(file_node_d), d_tif, type='string')
            self.__createPlace2dTexture(file_node_d)

            cmds.connectAttr('{}.outTransparency'.format(file_node_d), '{}.transparency'.format(shader))
            cmds.connectAttr('{}.outColor'.format(file_node_d), '{}.color'.format(shader))
        if mask_tif:
            file_node_mask = cmds.shadingNode('file', asTexture=1, isColorManaged=1,
                                              n='{}_mask_file'.format(shader_name))
            cmds.setAttr('{}.fileTextureName'.format(file_node_mask), mask_tif, type='string')
            self.__createPlace2dTexture(file_node_mask)
            cmds.connectAttr('{}.outColor'.format(file_node_mask), '{}.ambientColor'.format(shader))
        return True, (sg, __fbx_dir)

    def __get_tif_files_from_dir_by_base_name(self, dir, base_name):
        __tex_data = {}

        if not os.path.exists(dir):
            return

        mask_tif = '{}/alter_{}_mask.tif'.format(dir, base_name)

        d_tif = '{}/{}_d.tif'.format(dir, base_name)
        if os.path.exists(mask_tif):
            __tex_data['mask_tif'] = mask_tif.replace('\\', '/')
        else:
            mask_tif = '{}/{}_mask.tif'.format(dir, base_name)
            if os.path.exists(mask_tif):
                __tex_data['mask_tif'] = mask_tif.replace('\\', '/')
        if os.path.exists(d_tif):
            __tex_data['d_tif'] = d_tif.replace('\\', '/')
        __tex_data['tex_dir'] = dir.replace('\\', '/')
        return __tex_data

    def __get_all_exported_objects(self):
        __objs = []
        for obj in cmds.ls(tr=1, l=1):
            shapes = cmds.listRelatives(obj, s=1, ni=1, f=1)
            if not shapes:
                __objs.append(obj)
            if shapes and cmds.nodeType(shapes[0]) == 'mesh':
                __objs.append(obj)
        if __objs:
            __objs = list(set(__objs))
        return __objs

    def __export_fbx(self, objlist, output_fbx):
        return export_fbx(objlist, output_fbx, hi=1)

    def __get_fbx_files(self):
        fbx_files = []
        not_need_to_process_fbx_list = self.get_not_need_to_process_fbxs()
        for root, dirs, files in os.walk(self.__input_fbx_dir):
            for file in files:
                if file.lower().endswith('.fbx') and '.meta' not in file.lower():
                    fbx_file = os.path.join(root, file)
                    fbx_file = fbx_file.replace('\\', '/')
                    base_path = fbx_file.split(self.__input_fbx_dir)[-1].lstrip('/')
                    if not_need_to_process_fbx_list and base_path in not_need_to_process_fbx_list:
                        self.__logger.info("Skipping not needed to process FBX: {}".format(fbx_file))
                        continue
                    fbx_files.append(fbx_file)
        return fbx_files

    def __simplygon_fbx_reduction_by_json(self):
        try:


            mesh_objects = cmds.ls(type='mesh')
            if not mesh_objects:
                return False, "No mesh objects found"
            cmds.select(cl=1)
            cmds.select(mesh_objects)
            clean_object_names()
            rename_mesh()
            cmds.select(all=True)

            print("Starting Simplygon processing with {} objects".format(len(mesh_objects)))
            reductionPipeline = cmds.SimplygonPipeline(c='ReductionPipeline')
            cmds.Simplygon(sf=self.__json_file)
            cmds.SimplygonPipeline(cl=True)
            rename_mesh()
            return True, "Simplygon processing completed"

        except:
            import traceback
            error_msg = traceback.format_exc()
            return False, error_msg

    def __open_fbx_file(self, fbx_file):
        return cmds.file(fbx_file, options='v=0', f=1, o=1, ignoreVersion=1, pmt=0, rer=0)

    def __createPlace2dTexture(self, file, place2d=''):
        if not place2d:
            place2d = cmds.shadingNode('place2dTexture', asUtility=True)
        else:
            if not cmds.objExists(place2d):
                place2d = cmds.shadingNode('place2dTexture', asUtility=True, n=place2d)
        cmds.connectAttr((place2d + ".coverage"), (file + ".coverage"))
        cmds.connectAttr((place2d + ".translateFrame"), (file + ".translateFrame"))
        cmds.connectAttr((place2d + ".rotateFrame"), (file + ".rotateFrame"))
        cmds.connectAttr((place2d + ".mirrorU"), (file + ".mirrorU"))
        cmds.connectAttr((place2d + ".mirrorV"), (file + ".mirrorV"))
        cmds.connectAttr((place2d + ".stagger"), (file + ".stagger"))
        cmds.connectAttr((place2d + ".wrapU"), (file + ".wrapU"))
        cmds.connectAttr((place2d + ".repeatUV"), (file + ".repeatUV"))
        cmds.connectAttr((place2d + ".offset"), (file + ".offset"))
        cmds.connectAttr((place2d + ".rotateUV"), (file + ".rotateUV"))
        cmds.connectAttr((place2d + ".noiseUV"), (file + ".noiseUV"))
        cmds.connectAttr((place2d + ".vertexUvOne"), (file + ".vertexUvOne"))
        cmds.connectAttr((place2d + ".vertexUvTwo"), (file + ".vertexUvTwo"))
        cmds.connectAttr((place2d + ".vertexUvThree"), (file + ".vertexUvThree"))
        cmds.connectAttr((place2d + ".vertexCameraOne"), (file + ".vertexCameraOne"))
        cmds.connectAttr((place2d + ".outUV"), (file + ".uv"))
        cmds.connectAttr((place2d + ".outUvFilterSize"), (file + ".uvFilterSize"))



def read_txt_file(file_path):
    lines = []
    if not os.path.exists(file_path):
        return lines

    with open(file_path, 'r') as file:
        for line in file:
            lines.append(line.strip())
    return lines



def clean_object_names():
    """清理对象名称末尾的下划线"""
    # 获取所有transform节点
    transform_nodes = cmds.ls(type='transform')

    if not transform_nodes:
        return

    cleaned_count = 0
    for transform in transform_nodes:
        current_name = transform
        # 清理名称末尾的下划线
        clean_name = current_name.rstrip('_')
        if clean_name != current_name:
            try:
                cmds.rename(transform, clean_name)
                cleaned_count += 1
                print("Cleaned underscores: {} to {}".format(current_name, clean_name))
            except Exception as e:
                print("Failed to clean {}: {}".format(current_name, str(e)))

    print("Cleaned {} objects with trailing underscores".format(cleaned_count))


def rename_mesh():
    """重命名选中的mesh形状节点，确保以_LOD结尾"""
    # 获取所有选中的mesh形状节点
    selected_meshes = cmds.ls(type='mesh')

    if not selected_meshes:
        cmds.error("No mesh objects selected")
        return

    renamed_count = 0
    for mesh in selected_meshes:
        # 获取mesh的父transform节点（使用完整路径）
        parents = cmds.listRelatives(mesh, parent=True, fullPath=True)
        if not parents:
            continue

        transform_node = parents[0]  # 这是完整路径
        current_name = transform_node.split('|')[-1]  # 只取最后一部分作为名称
        print("Transform名字 {}".format(transform_node))

        # 检查是否以 _LOD0_001, _LOD0_002 等结尾

        lod_pattern = re.search(r'_LOD0_(\d+)$', current_name)
        if lod_pattern:
            # 提取数字并转换为LOD级别
            lod_number = int(lod_pattern.group(1))
            new_name = current_name.replace('_LOD0_{:03d}'.format(lod_number), '_LOD{}'.format(lod_number))
            cmds.rename(transform_node, new_name)
            renamed_count += 1
            print("Renamed {} to {}".format(current_name, new_name))
            continue

        # 检查是否以_LOD0或_lod0结尾
        if current_name.endswith('_LOD0'):
            continue
        elif current_name.endswith('_lod0'):
            # 小写_lod0改为大写_LOD0
            new_name = current_name[:-5] + '_LOD0'
            cmds.rename(transform_node, new_name)
            renamed_count += 1
        else:
            # 没有LOD后缀，添加_LOD0
            new_name = current_name + '_LOD0'
            cmds.rename(transform_node, new_name)
            renamed_count += 1

    print("Renamed {} mesh objects with _LOD0 suffix".format(renamed_count))


if __name__ == '__main__':
    input_fbx_dir = r'Z:\TD\fbx_process\Tested-Main\process_fbx_test'
    tex_dir = r'Z:\TD\fbx_process\tex_test'
    output_dir = r'Z:\TD\fbx_process\Tested-Main\fbx_test'
    error_dir = r'Z:\TD\fbx_process\Tested-Main\error_fbx_test'
    batch_simplygon = BatchSimplygon(input_fbx_dir, tex_dir, output_dir,error_dir=error_dir)
    batch_simplygon.run()

# def tga_to_tiff(input_path, output_path=None):
#     if not os.path.exists(input_path):
#         raise IOError("File not found: %s" % input_path)
#
#     im = Image.open(input_path)
#
#     # 确保转换为标准模式（有时TGA为P或RGBA）
#     if im.mode not in ('RGB', 'RGBA'):
#         im = im.convert('RGBA')
#
#     if not output_path:
#         base, _ = os.path.splitext(input_path)
#         output_path = base + ".tif"
#
#     im.save(output_path, format="TIFF", compression="tiff_deflate")







    # input_fbx_dir = r'Z:\TD\fbx_process\plant_fbx'
    # tex_dir = r'Z:\TD\fbx_process\tex'
    # output_dir = r'Z:\TD\fbx_process\fbx'
    # error_dir = r'Z:\TD\fbx_process\error_fbx'
    # batch_simplygon = BatchSimplygon(input_fbx_dir, tex_dir, output_dir,error_dir=error_dir)
    # batch_simplygon.run()
    # file_path=r'Z:\TD\fbx_process\mesh_texture.txt'
    # print read_txt_file(file_path)

    # batch_simplygon.run()
    # fbx_file=r'Z:\TD\fbx_process\need_fbx_f\plant\bush\home_sw_bush_agave_s002.fbx'
    # batch_simplygon = BatchSimplygon(input_fbx_dir, tex_dir, output_dir)
    # batch_simplygon.process_fbx_file(fbx_file)
    # batch_simplygon.run()
    # fbx_file = r'D:\test\sim\test_fbx\plant\flower\home_sw_flower_allium_s001.fbx'
    # batch_simplygon._create_simplygon_metrials(fbx_file)
