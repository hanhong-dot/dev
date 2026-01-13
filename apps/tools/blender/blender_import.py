# -*- coding: utf-8 -*-#
# Python     : Python 3.10
# -------------------------------------------------------
# NAME       : blender_import
# Describe   : 带材质导入blender(修改自小龙虾，PapeGameImporter)
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2024/4/17
# -------------------------------------------------------
import os
# import bpy
import sys

sys.path.append('z:/')
import bpy

import xml.etree.ElementTree as ET

X3BASEMAT = r'Z:\dev\apps\tools\blender\X3BaseMat.blend'
X3BaseMatVeg = r'Z:\dev\apps\tools\blender\X3BaseMatVeg.blend'

import lib.common.log as log
import method.common.dir as common_dir
import uuid


class PapeGameBlenderImport(object):

    def __init__(self, fbx_file, log_file=None):
        super(PapeGameBlenderImport, self).__init__()
        self._fbx_file = fbx_file
        if not self._fbx_file or not os.path.exists(self._fbx_file):
            raise Exception(u'fbx不存在,请检查,{}'.format(self._fbx_file))
        self._xml_file = self._fbx_file.replace('.fbx', '.xml')
        if not os.path.exists(self._xml_file):
            raise Exception(u'xml文件不存在,请检查,{}'.format(self._xml_file))
        self._root = self._get_xml_root()
        self.texsPath = self.get_texs_path()
        if log_file:
            self.log_handle = log.Logger(log_file)
            self.log_handle.info('fbx_file:{}'.format(self._fbx_file))

    def blender_import_with_mat(self, context):
        imported_objects = self._import_fbx()
        self.log_handle.info('imported_objects:{}'.format(str(imported_objects)))
        if not imported_objects:
            return False, u'导入失败,请检查fbx文件是否正确'

        self.log_handle.info('context_imp'.format(bpy.context))
        blender_dict = self._import_mat_blend(imported_objects)
        self.log_handle.info('blender_dict:{}'.format(str(blender_dict)))
        if not blender_dict:
            return False, u'导入材质失败'
        self._builder_pre_mesh(blender_dict)
        self._remove_cube()

    def _reset_context(self):
        for area in bpy.context.screen.areas:
            if area.type == "SEQUENCE_EDITOR":
                override = bpy.context.copy()
                # change context to the sequencer
                override["area"] = area
                override["region"] = area.regions[-1]
                # run the command with the correct context
                with bpy.context.temp_override(**override):
                    bpy.ops.sequencer.view_all()
                break

    def _remove_cube(self):
        if 'Cube' in bpy.data.objects:
            bpy.data.objects.remove(bpy.data.objects['Cube'])

    def _builder_pre_mesh(self, blender_dict):
        objects = self._root.find("ObjectPart")
        for mesh in objects.findall("Mesh"):
            self.buildMaterial(mesh, blender_dict)

    def buildMaterial(self, mesh, blender_dict):
        for obj in bpy.data.objects:
            obj.select_set(state=False)
        material_datas = mesh.findall("Material")
        mesh_name, blends, suffix = self.get_mesh_grps_from_mesh_dict(mesh, blender_dict)

        if material_datas:
            for i in range(len(material_datas)):

                mat_shader_name = material_datas[i].attrib["shaderName"]
                mat_name = material_datas[i].attrib["matName"]

                if mat_shader_name == "null":
                    continue

                mat = bpy.data.materials.get(mat_name)
                self.log_handle.info('mat:{}'.format(mat))
                if mat is None:
                    continue
                mat.name = '{}__{}'.format(mesh_name.replace('.', '_'), mat_name)

                mat.use_nodes = True
                matnodes = mat.node_tree.nodes
                matnodes.clear()
                uv_judge = False
                mesh_obj = bpy.data.objects[mesh_name]
                for uv_map in mesh_obj.data.uv_layers:
                    if uv_map.name == "1u":
                        uv_judge = True
                        break

                if "SceneDecal" in mat_shader_name:
                    self.setBattleDecalNode(i, matnodes, mat, mat_shader_name, material_datas, suffix, blends, uv_judge)
                elif "SceneUnlit" in mat_shader_name:
                    self.setSceneUnlitNode(i, matnodes, mat, mat_shader_name, material_datas, suffix, blends, uv_judge)
                elif "SceneBlend" in mat_shader_name:
                    self.setSceneBlendNode(i, matnodes, mat, mat_shader_name, material_datas, suffix, blends, uv_judge)
                elif "NewVegetation" in mat_shader_name:
                    self.setVegetationNode(i, matnodes, mat, mat_shader_name, material_datas, suffix, blends, uv_judge)
                else:
                    self.setSceneNode(i, matnodes, mat, mat_shader_name, material_datas, suffix, blends, uv_judge)

    def setVegetationNode(self, i, matnodes, mat, matShaderName, material_datas, suffix, blends, uv_judge):
        group = matnodes.new(type='ShaderNodeGroup')

        self.log_handle.info('matnodes:{}'.format(matnodes))
        self.log_handle.info('mat:{}'.format(mat))
        self.log_handle.info('matShaderName:{}'.format(matShaderName))
        self.log_handle.info('i:{}'.format(i))
        self.log_handle.info('material_datas:{}'.format(material_datas))
        self.log_handle.info('suffix:{}'.format(suffix))
        self.log_handle.info('blends:{}'.format(blends))

        self.log_handle.info('{}'.format(blends))
        group.node_tree = bpy.data.node_groups[blends[0]]
        group.location = (-500, 0)
        out = matnodes.new(type='ShaderNodeOutputMaterial')
        self.log_handle.info('group.outputs')
        self.log_handle.info('{}'.format(str(group.outputs)))

        group_random = matnodes.new(type='ShaderNodeGroup')
        group_random.node_tree = bpy.data.node_groups[blends[1]]
        group_random.location = (-800, -200)

        mat.node_tree.links.new(group.outputs['BSDF'], out.inputs['Surface'])
        for node in matnodes:
            node.select = False

        group.select = True
        # matnodes.active = group
        # bpy.ops.node.group_ungroup()

        matnodes = mat.node_tree.nodes

        attr = material_datas[i].find("Attribute").attrib
        self.log_handle.info('attr:{}'.format(attr))

        # if "Transparent" in matShaderName or "SceneDecal" in matShaderName:
        #     mat.blend_method = 'HASHED'
        #     mat.use_backface_culling = True
        #     group.inputs["isOpaque"].default_value = 0.0
        # else:
        #     if float(attr["AlphaClip"]) > 0.5:
        #         group.inputs["isOpaque"].default_value = 0.0
        #         mat.blend_method = 'CLIP'
        #         mat.alpha_threshold = float(attr["Cutoff"])
        #     else:
        #         group.inputs["isOpaque"].default_value = 1.0
        #         mat.blend_method = 'OPAQUE'

        if float(attr["AlphaClip"]) > 0.5:
            mat.blend_method = 'CLIP'
            mat.alpha_threshold = float(attr["Cutoff"])
        else:
            mat.blend_method = 'OPAQUE'

        Roughness = float(attr["Roughness"])
        RoughnessMin = float(attr.get("RoughnessMin", "0.0"))
        EmissionUvChoose = int(attr.get("EmissionUvChoose", "0"))
        RampOFF = int(attr.get("RampOFF", "0"))
        randomOffset = float(attr.get("randomOffset", "0.0"))
        unhealthySoft = float(attr.get("unhealthySoft", "0.0"))
        unhealthyStep = float(attr.get("unhealthyStep", "0.0"))
        topLeaveAOSoft = float(attr.get("topLeaveAOSoft", "0.0"))
        topLeaveAOStep = float(attr.get("topLeaveAOStep", "0.0"))
        thicknessRemapX = float(attr.get("thicknessRemapX", "0.0"))
        thicknessRemapY = float(attr.get("thicknessRemapY", "0.0"))
        GRADIENTIDCOUNT = int(attr.get("GRADIENTIDCOUNT", "0")) - 1
        variantBlend = float(attr.get("variantBlend", "0.0"))
        variantID0 = int(attr.get("variantID0", "0"))
        variantID1 = int(attr.get("variantID1", "0"))
        BkgRGBA = attr["RGBA"].split(",")
        # BkgRGBA = attr["RGBA"].split(",")
        TexRGBA = attr["TexRGBA"].split(",")
        EmiRGBA = attr["EmiRGBA"].split(",")
        unhealthyColorRGBA = attr.get("unhealthyColorRGBA", "1,1,1,1").split(",")
        rampBaseColor0RGBA = attr.get("rampBaseColor0RGBA", "1,1,1,1").split(",")
        rampBaseColor1RGBA = attr.get("rampBaseColor1RGBA", "1,1,1,1").split(",")
        rampBaseColor2RGBA = attr.get("rampBaseColor2RGBA", "1,1,1,1").split(",")
        rampBaseColor3RGBA = attr.get("rampBaseColor3RGBA", "1,1,1,1").split(",")
        rampBaseColor4RGBA = attr.get("rampBaseColor4RGBA", "1,1,1,1").split(",")
        RampTex_TexelSize = attr.get("RampTex_TexelSize", "0,0,0,0").split(",")

        # MainTex_ST = attr["MainTex_ST"].split(",")
        TexAlbedoMap_ST = attr["TexAlbedoMap_ST"].split(",")
        TexNormalMap_ST = attr["TexNormalMap_ST"].split(",")
        # MainTexEmi_ST = attr["MainTexEmi_ST"].split(",")
        group.inputs["Cutoff"].default_value = float(attr["Cutoff"])
        group.inputs['RampOFF'].default_value = RampOFF
        group.inputs['UnhealthySoft'].default_value = unhealthySoft
        group.inputs['UnhealthyStep'].default_value = unhealthyStep

        group.inputs["Color"].default_value = (
            float(BkgRGBA[0]), float(BkgRGBA[1]), float(BkgRGBA[2]), float(BkgRGBA[3]))
        group.inputs["ColorAlpha"].default_value = float(BkgRGBA[3])  # alpha

        group.inputs["TexColor"].default_value = (
            float(TexRGBA[0]), float(TexRGBA[1]), float(TexRGBA[2]), float(TexRGBA[3]))
        group.inputs["TexColorAlpha"].default_value = float(TexRGBA[3])  # alpha

        group.inputs["EmissionColor"].default_value = (
            float(EmiRGBA[0]), float(EmiRGBA[1]), float(EmiRGBA[2]), float(EmiRGBA[3]))

        group.inputs["UnhealthyColor"].default_value = (
            float(unhealthyColorRGBA[0]), float(unhealthyColorRGBA[1]), float(unhealthyColorRGBA[2]),
            float(unhealthyColorRGBA[3]))
        group.inputs["RampBaseColor0"].default_value = (
            float(rampBaseColor0RGBA[0]), float(rampBaseColor0RGBA[1]), float(rampBaseColor0RGBA[2]),
            float(rampBaseColor0RGBA[3]))
        group.inputs["RampBaseColor1"].default_value = (
            float(rampBaseColor1RGBA[0]), float(rampBaseColor1RGBA[1]), float(rampBaseColor1RGBA[2]),
            float(rampBaseColor1RGBA[3]))
        group.inputs["RampBaseColor2"].default_value = (
            float(rampBaseColor2RGBA[0]), float(rampBaseColor2RGBA[1]), float(rampBaseColor2RGBA[2]),
            float(rampBaseColor2RGBA[3]))
        group.inputs["RampBaseColor3"].default_value = (
            float(rampBaseColor3RGBA[0]), float(rampBaseColor3RGBA[1]), float(rampBaseColor3RGBA[2]),
            float(rampBaseColor3RGBA[3]))
        group.inputs["RampBaseColor4"].default_value = (
            float(rampBaseColor4RGBA[0]), float(rampBaseColor4RGBA[1]), float(rampBaseColor4RGBA[2]),
            float(rampBaseColor4RGBA[3]))

        group.inputs['Roughness'].default_value = Roughness
        group.inputs['RoughnessMin'].default_value = RoughnessMin
        group.inputs['ThicknessRemapX'].default_value = thicknessRemapX
        group.inputs['ThicknessRemapY'].default_value = thicknessRemapY
        group.inputs['GRADIENTIDCOUNT-1'].default_value = GRADIENTIDCOUNT
        group.inputs['VariantBlend'].default_value = variantBlend

        group_random.inputs['RandomOffset'].default_value = randomOffset
        group_random.inputs['TopLeaveAOSoft'].default_value = topLeaveAOSoft
        group_random.inputs['TopLeaveAOStep'].default_value = topLeaveAOStep
        group_random.inputs['VariantID0'].default_value = variantID0
        group_random.inputs['VariantID1'].default_value = variantID1

        group_random.inputs['_RampTex_TexelSize'].default_value[0] = float(RampTex_TexelSize[0])
        group_random.inputs['_RampTex_TexelSize'].default_value[1] = float(RampTex_TexelSize[1])
        group_random.inputs['_RampTex_TexelSize'].default_value[2] = float(RampTex_TexelSize[2])

        if float(attr["TexBlendMode"]) < 0.5:  # 0
            group.inputs['isColorMode1'].default_value = 0.0
            group.inputs['isColorMode2'].default_value = 0.0
        elif float(attr["TexBlendMode"]) < 1.5:  # 1
            group.inputs['isColorMode1'].default_value = 1.0
            group.inputs['isColorMode2'].default_value = 0.0
        else:  # 2
            group.inputs['isColorMode1'].default_value = 0.0
            group.inputs['isColorMode2'].default_value = 1.0

        if float(attr["NmlBlendMode"]) < 0.5:  # 0
            group.inputs['isNormalMode1'].default_value = 0.0
            group.inputs['isNormalMode2'].default_value = 0.0
        elif float(attr["NmlBlendMode"]) < 1.5:  # 1
            group.inputs['isNormalMode1'].default_value = 1.0
            group.inputs['isNormalMode2'].default_value = 0.0
        else:  # 2
            group.inputs['isNormalMode1'].default_value = 0
            group.inputs['isNormalMode2'].default_value = 1

        hasBkgTex, hasBkgNormal, hasTexTex, hasTexNormal = False, False, False, False

        for tex in material_datas[i].findall("Texture"):
            texName = tex.attrib["Name"]
            self.log_handle.info('texName:{}'.format(texName))
            texShaderName = tex.attrib["ShaderName"]
            self.log_handle.info('texShaderName:{}'.format(texShaderName))

            if (texShaderName == "_MainTex"):
                if (texName != "null"):
                    bkgtex_node = self.buildTextureNode(mat.node_tree, self.texsPath[texName], False, [], uv_judge)
                    if bkgtex_node is not None:
                        mat.node_tree.links.new(bkgtex_node.outputs['Color'], group.inputs["MainTex"])
                        mat.node_tree.links.new(bkgtex_node.outputs['Alpha'], group.inputs['MainTexAlpha'])
                        hasBkgTex = True
            if (texShaderName == "_NormalMap"):
                if (texName != "null"):
                    bkgnormal_node = self.buildTextureNode(mat.node_tree, self.texsPath[texName], False, [], uv_judge)
                    if bkgnormal_node is not None:
                        bkgnormal_node.image.colorspace_settings.name = "Linear Rec.709"
                        mat.node_tree.links.new(bkgnormal_node.outputs['Color'], group.inputs['NormalTex'])
                        mat.node_tree.links.new(bkgnormal_node.outputs['Alpha'], group.inputs['NormalTexAlpha'])
                        hasBkgNormal = True

            if (texShaderName == "_VegMaskTex"):
                if (texName != "null"):
                    vegmaskl_node = self.buildTextureNode(mat.node_tree, self.texsPath[texName], False, [], uv_judge)
                    if vegmaskl_node is not None:
                        vegmaskl_node.image.colorspace_settings.name = "Linear Rec.709"
                        mat.node_tree.links.new(vegmaskl_node.outputs['Color'], group.inputs['MaskTex'])
                        mat.node_tree.links.new(vegmaskl_node.outputs['Color'], group_random.inputs['MaskTex'])
                        mat.node_tree.links.new(vegmaskl_node.outputs['Alpha'], group_random.inputs['MaskTexAlpha'])

            if (texShaderName == "_TexAlbedoMap"):
                if (texName != "null"):
                    textex_node = self.buildTextureNode(mat.node_tree, self.texsPath[texName], True, TexAlbedoMap_ST,
                                                        uv_judge)
                    if textex_node is not None:
                        mat.node_tree.links.new(textex_node.outputs['Color'], group.inputs['TexTex'])
                        mat.node_tree.links.new(textex_node.outputs['Alpha'], group.inputs['TexTexAlpha'])
                        hasTexTex = True
            if (texShaderName == "_EmissionMap"):
                if (texName != "null"):
                    if EmissionUvChoose == 0:
                        emimap_node = self.buildTextureNode(mat.node_tree, self.texsPath[texName], False,
                                                            TexAlbedoMap_ST, uv_judge)
                    else:

                        emimap_node = self.buildTextureNode(mat.node_tree, self.texsPath[texName], True,
                                                            TexAlbedoMap_ST, uv_judge)
                    if emimap_node is not None:
                        mat.node_tree.links.new(emimap_node.outputs['Color'], group.inputs['EmissionMap'])
            if (texShaderName == "_TexNmlMatMap"):
                if (texName != "null"):
                    texnormal_node = self.buildTextureNode(mat.node_tree, self.texsPath[texName], True, TexNormalMap_ST,
                                                           uv_judge)
                    if texnormal_node is not None:
                        texnormal_node.image.colorspace_settings.name = "Linear Rec.709"
                        mat.node_tree.links.new(texnormal_node.outputs['Color'], group.inputs['TexNormal'])
                        mat.node_tree.links.new(texnormal_node.outputs['Alpha'], group.inputs['TexNormalAlpha'])
                        hasTexNormal = True
            if (texShaderName == "_AlbedoRampTex"):

                if (texName != "null"):

                    abedo_node01 = self.buildTextureNodeWithoutUV(mat.node_tree, self.texsPath[texName],[])
                    abedo_node02 = self.buildTextureNodeWithoutUV(mat.node_tree, self.texsPath[texName],[])
                    # textex_node02= self.buildTextureNode(mat.node_tree, self.texsPath[texName], True, [])
                    if abedo_node01 is not None:
                        mat.node_tree.links.new(abedo_node01.outputs['Color'], group.inputs['RampTexResult0'])
                        mat.node_tree.links.new(group_random.outputs['RampTexUV0'], abedo_node01.inputs['Vector'])
                        hasBkgNormal = True
                    if abedo_node02 is not None:
                        mat.node_tree.links.new(abedo_node02.outputs['Color'], group.inputs['RampTexResult1'])
                        mat.node_tree.links.new(group_random.outputs['RampTexUV1'], abedo_node02.inputs['Vector'])
                        hasBkgNormal = True
        if not hasTexTex:  # 1
            group.inputs['isColorMode1'].default_value = 1.0
            group.inputs['isColorMode2'].default_value = 0.0
            group.inputs['TexTexAlpha'].default_value = 0.0
        elif not hasBkgTex:  # 2
            group.inputs['isColorMode1'].default_value = 0.0
            group.inputs['isColorMode2'].default_value = 1.0
            group.inputs['BkgTexAlpha'].default_value = 0.0

        if not hasTexNormal:
            group.inputs['isNormalMode1'].default_value = 1.0
            group.inputs['isNormalMode2'].default_value = 0.0
            group.inputs['BlendNormal'].default_value = 0.0
        elif not hasBkgNormal:
            group.inputs['isNormalMode1'].default_value = 0.0
            group.inputs['isNormalMode2'].default_value = 1.0
            group.inputs['BlendNormal'].default_value = 0.0

    def get_mesh_grps_from_mesh_dict(self, mesh, blender_dict):
        mesh_name = mesh.attrib['objname']

        blends = []
        suffix = ''
        for k, v in blender_dict.items():
            infos = k.split('.')
            if len(infos) > 1:
                if infos[0] == mesh.attrib['objname']:
                    mesh_name = k
                    blends = v
                    suffix = infos[-1]
                    break
            else:
                if k == mesh.attrib['objname']:
                    mesh_name = k
                    blends = v
                    break
        return mesh_name, blends, suffix

    def get_texs_path(self):
        texsPath = {}
        for tex in self._root.find("TexturePart").findall('ImportTexture'):
            texname = tex.attrib['Name']
            texpath = tex.attrib['Path']
            texsPath[texname] = texpath
        return texsPath

    def setSceneNode(self, i, matnodes, mat, matShaderName, material_datas, suffix, blends, uv_judge):
        print(blends)
        group = matnodes.new(type='ShaderNodeGroup')

        self.log_handle.info('{}'.format(blends))
        group.node_tree = bpy.data.node_groups[blends[0]]
        group.location = (-500, 0)
        out = matnodes.new(type='ShaderNodeOutputMaterial')
        self.log_handle.info('group.outputs')
        self.log_handle.info('{}'.format(str(group.outputs)))

        mat.node_tree.links.new(group.outputs['BSDF'], out.inputs['Surface'])
        for node in matnodes:
            node.select = False

        group.select = True
        # matnodes.active = group
        # bpy.ops.node.group_ungroup()

        matnodes = mat.node_tree.nodes

        attr = material_datas[i].find("Attribute").attrib

        if "Transparent" in matShaderName or "SceneDecal" in matShaderName:
            mat.blend_method = 'HASHED'
            mat.use_backface_culling = True
            group.inputs["isOpaque"].default_value = 0.0
        else:
            if float(attr["AlphaClip"]) > 0.5:
                group.inputs["isOpaque"].default_value = 0.0
                mat.blend_method = 'CLIP'
                mat.alpha_threshold = float(attr["Cutoff"])
            else:
                group.inputs["isOpaque"].default_value = 1.0
                mat.blend_method = 'OPAQUE'

        BkgRGBA = attr["RGBA"].split(",")
        TexRGBA = attr["TexRGBA"].split(",")
        EmiRGBA = attr["EmiRGBA"].split(",")
        MainTex_ST = attr["MainTex_ST"].split(",")
        TexAlbedoMap_ST = attr["TexAlbedoMap_ST"].split(",")
        TexNormalMap_ST = attr["TexNormalMap_ST"].split(",")
        MainTexEmi_ST = attr["MainTexEmi_ST"].split(",")

        group.inputs["BkgColor"].default_value = (
            float(BkgRGBA[0]), float(BkgRGBA[1]), float(BkgRGBA[2]), float(BkgRGBA[3]))
        group.inputs["BkgColorAlpha"].default_value = float(BkgRGBA[3])  # alpha

        group.inputs["TexColor"].default_value = (
            float(TexRGBA[0]), float(TexRGBA[1]), float(TexRGBA[2]), float(TexRGBA[3]))
        group.inputs["TexColorAlpha"].default_value = float(TexRGBA[3])  # alpha

        group.inputs["EmissionColor"].default_value = (
            float(EmiRGBA[0]), float(EmiRGBA[1]), float(EmiRGBA[2]), float(EmiRGBA[3]))

        group.inputs['Metallic'].default_value = float(attr["Matallic"])
        group.inputs['Roughness'].default_value = float(attr["Roughness"])

        if float(attr["TexBlendMode"]) < 0.5:  # 0
            group.inputs['isColorMode1'].default_value = 0.0
            group.inputs['isColorMode2'].default_value = 0.0
        elif float(attr["TexBlendMode"]) < 1.5:  # 1
            group.inputs['isColorMode1'].default_value = 1.0
            group.inputs['isColorMode2'].default_value = 0.0
        else:  # 2
            group.inputs['isColorMode1'].default_value = 0.0
            group.inputs['isColorMode2'].default_value = 1.0

        if float(attr["NmlBlendMode"]) < 0.5:  # 0
            group.inputs['isNormalMode1'].default_value = 0.0
            group.inputs['isNormalMode2'].default_value = 0.0
        elif float(attr["NmlBlendMode"]) < 1.5:  # 1
            group.inputs['isNormalMode1'].default_value = 1.0
            group.inputs['isNormalMode2'].default_value = 0.0
        else:  # 2
            group.inputs['isNormalMode1'].default_value = 0
            group.inputs['isNormalMode2'].default_value = 1

        hasBkgTex, hasBkgNormal, hasTexTex, hasTexNormal = False, False, False, False

        for tex in material_datas[i].findall("Texture"):
            texName = tex.attrib["Name"]
            texShaderName = tex.attrib["ShaderName"]
            if (texShaderName == "_MainTex"):
                if (texName != "null"):
                    bkgtex_node = self.buildTextureNode(mat.node_tree, self.texsPath[texName], False, MainTex_ST,
                                                        uv_judge=uv_judge)
                    if bkgtex_node is not None:
                        mat.node_tree.links.new(bkgtex_node.outputs['Color'], group.inputs['BkgTex'])
                        mat.node_tree.links.new(bkgtex_node.outputs['Alpha'], group.inputs['BkgTexAlpha'])
                        hasBkgTex = True
            if (texShaderName == "_BkgNormalMap"):
                if (texName != "null"):
                    bkgnormal_node = self.buildTextureNode(mat.node_tree, self.texsPath[texName], False, MainTex_ST,
                                                           uv_judge=uv_judge)
                    if bkgnormal_node is not None:
                        bkgnormal_node.image.colorspace_settings.name = "Linear Rec.709"
                        mat.node_tree.links.new(bkgnormal_node.outputs['Color'], group.inputs['BkgNormal'])
                        mat.node_tree.links.new(bkgnormal_node.outputs['Alpha'], group.inputs['BkgNormalAlpha'])
                        hasBkgNormal = True
            if (texShaderName == "_TexAlbedoMap"):
                if (texName != "null"):
                    textex_node = self.buildTextureNode(mat.node_tree, self.texsPath[texName], True, TexAlbedoMap_ST,
                                                        uv_judge=uv_judge)
                    if textex_node is not None:
                        mat.node_tree.links.new(textex_node.outputs['Color'], group.inputs['TexTex'])
                        mat.node_tree.links.new(textex_node.outputs['Alpha'], group.inputs['TexTexAlpha'])
                        hasTexTex = True
            if (texShaderName == "_TexNormalMap"):
                if (texName != "null"):
                    texnormal_node = self.buildTextureNode(mat.node_tree, self.texsPath[texName], True, TexNormalMap_ST,
                                                           uv_judge=uv_judge)
                    if texnormal_node is not None:
                        texnormal_node.image.colorspace_settings.name = "Linear Rec.709"
                        mat.node_tree.links.new(texnormal_node.outputs['Color'], group.inputs['TexNormal'])
                        mat.node_tree.links.new(texnormal_node.outputs['Alpha'], group.inputs['TexNormalAlpha'])
                        hasTexNormal = True
            if (texShaderName == "_BkgEmissionMap"):
                if (texName != "null"):
                    texnormal_node = self.buildTextureNode(mat.node_tree, self.texsPath[texName], False, MainTexEmi_ST,
                                                           uv_judge=uv_judge)
                    if texnormal_node is not None:
                        mat.node_tree.links.new(texnormal_node.outputs['Color'], group.inputs['EmissionMap'])
                        hasTexNormal = True

        if not hasTexTex:  # 1
            group.inputs['isColorMode1'].default_value = 1.0
            group.inputs['isColorMode2'].default_value = 0.0
            group.inputs['TexTexAlpha'].default_value = 0.0
        elif not hasBkgTex:  # 2
            group.inputs['isColorMode1'].default_value = 0.0
            group.inputs['isColorMode2'].default_value = 1.0
            group.inputs['BkgTexAlpha'].default_value = 0.0

        if not hasTexNormal:
            group.inputs['isNormalMode1'].default_value = 1.0
            group.inputs['isNormalMode2'].default_value = 0.0
            group.inputs['BlendNormal'].default_value = 0.0
        elif not hasBkgNormal:
            group.inputs['isNormalMode1'].default_value = 0.0
            group.inputs['isNormalMode2'].default_value = 1.0
            group.inputs['BlendNormal'].default_value = 0.0

    def setSceneBlendNode(self, i, matnodes, mat, matShaderName, material_datas, suffix, blends, uv_judge):
        group = matnodes.new(type='ShaderNodeGroup')
        group.node_tree = bpy.data.node_groups[blends[1]]
        group.location = (-500, 0)
        out = matnodes.new(type='ShaderNodeOutputMaterial')
        mat.node_tree.links.new(group.outputs['BSDF'], out.inputs['Surface'])
        for node in matnodes:
            node.select = False

        group.select = True
        # matnodes.active = group
        # bpy.ops.node.group_ungroup()

        matnodes = mat.node_tree.nodes

        attr = material_datas[i].find("Attribute").attrib
        RGBA = attr["RGBA"].split(",")
        RGBA2 = attr["RGBA2"].split(",")
        RGBA3 = attr["RGBA3"].split(",")

        group.inputs["Color1"].default_value = (
            float(RGBA[0]), float(RGBA[1]), float(RGBA[2]), float(RGBA[3]))

        group.inputs["Color2"].default_value = (
            float(RGBA2[0]), float(RGBA2[1]), float(RGBA2[2]), float(RGBA2[3]))

        group.inputs["Color3"].default_value = (
            float(RGBA3[0]), float(RGBA3[1]), float(RGBA3[2]), float(RGBA3[3]))

        group.inputs['Metallic1'].default_value = float(attr["Metallic"])
        group.inputs['Roughness1'].default_value = float(attr["Roughness"])

        group.inputs['Metallic2'].default_value = float(attr["Metallic2"])
        group.inputs['Roughness2'].default_value = float(attr["Roughness2"])

        group.inputs['Metallic3'].default_value = float(attr["Metallic3"])
        group.inputs['Roughness3'].default_value = float(attr["Roughness3"])

        group.inputs['BlendPower1'].default_value = float(attr["BlendPower1"])
        group.inputs['BlendPower2'].default_value = float(attr["BlendPower2"])
        group.inputs['BlendPower3'].default_value = float(attr["BlendPower3"])

        for tex in material_datas[i].findall("Texture"):
            texName = tex.attrib["Name"]
            texShaderName = tex.attrib["ShaderName"]
            if (texShaderName == "_MainTex"):
                if (texName != "null"):
                    tex_node = self.buildTextureNode(mat.node_tree, self.texsPath[texName], False, uv_judge=uv_judge)
                    if tex_node is not None:
                        mat.node_tree.links.new(tex_node.outputs['Color'], group.inputs['MainTex1'])
            if (texShaderName == "_BumpMap"):
                if (texName != "null"):
                    normal_node = self.buildTextureNode(mat.node_tree, self.texsPath[texName], False, uv_judge=uv_judge)
                    if normal_node is not None:
                        normal_node.image.colorspace_settings.name = "Linear Rec.709"
                        mat.node_tree.links.new(normal_node.outputs['Color'], group.inputs['BumpMap1'])
                        mat.node_tree.links.new(normal_node.outputs['Alpha'], group.inputs['RoughnessMap1'])
            if (texShaderName == "_MainTex2"):
                if (texName != "null"):
                    tex_node2 = self.buildTextureNode(mat.node_tree, self.texsPath[texName], False, uv_judge=uv_judge)
                    if tex_node2 is not None:
                        mat.node_tree.links.new(tex_node2.outputs['Color'], group.inputs['MainTex2'])
            if (texShaderName == "_BumpMap2"):
                if (texName != "null"):
                    normal_node2 = self.buildTextureNode(mat.node_tree, self.texsPath[texName], False,
                                                         uv_judge=uv_judge)
                    if normal_node2 is not None:
                        normal_node2.image.colorspace_settings.name = "Linear Rec.709"
                        mat.node_tree.links.new(normal_node2.outputs['Color'], group.inputs['BumpMap2'])
                        mat.node_tree.links.new(normal_node2.outputs['Alpha'], group.inputs['RoughnessMap2'])
            if (texShaderName == "_MainTex3"):
                if (texName != "null"):
                    tex_node3 = self.buildTextureNode(mat.node_tree, self.texsPath[texName], False, uv_judge=uv_judge)
                    if tex_node3 is not None:
                        mat.node_tree.links.new(tex_node3.outputs['Color'], group.inputs['MainTex3'])
            if (texShaderName == "_BumpMap3"):
                if (texName != "null"):
                    normal_node3 = self.buildTextureNode(mat.node_tree, self.texsPath[texName], False,
                                                         uv_judge=uv_judge)
                    if normal_node3 is not None:
                        normal_node3.image.colorspace_settings.name = "Linear Rec.709"
                        mat.node_tree.links.new(normal_node3.outputs['Color'], group.inputs['BumpMap3'])
                        mat.node_tree.links.new(normal_node3.outputs['Alpha'], group.inputs['RoughnessMap3'])
            if (texShaderName == "_BlendMask"):
                if (texName != "null"):
                    mask_node = self.buildTextureNode(mat.node_tree, self.texsPath[texName], False, uv_judge=uv_judge)
                    if mask_node is not None:
                        mask_node.image.colorspace_settings.name = "Linear Rec.709"
                        mat.node_tree.links.new(mask_node.outputs['Color'], group.inputs['BlendMask'])

    def setSceneUnlitNode(self, i, matnodes, mat, matShaderName, material_datas, suffix, blends, uv_judge):
        group = matnodes.new(type='ShaderNodeGroup')
        group.node_tree = bpy.data.node_groups[blends[0]]
        group.location = (-500, 0)
        out = matnodes.new(type='ShaderNodeOutputMaterial')
        mat.node_tree.links.new(group.outputs['BSDF'], out.inputs['Surface'])
        for node in matnodes:
            node.select = False

        group.select = True
        # matnodes.active = group
        # bpy.ops.node.group_ungroup()

        matnodes = mat.node_tree.nodes
        if "Transparent" in matShaderName or "SceneDecal" in matShaderName:
            mat.blend_method = 'HASHED'

        attr = material_datas[i].find("Attribute").attrib
        BkgRGBA = attr["RGBA"].split(",")

        group.inputs["BkgColor"].default_value = (0.0, 0.0, 0.0, 0.0)
        group.inputs["BkgColorAlpha"].default_value = 1.0  # alpha

        group.inputs["TexColor"].default_value = (0.0, 0.0, 0.0, 0.0)
        group.inputs["TexColorAlpha"].default_value = 1.0  # alpha

        brightness = float(attr["Brightness"])

        for tex in material_datas[i].findall("Texture"):
            texName = tex.attrib["Name"]
            texShaderName = tex.attrib["ShaderName"]
            if (texShaderName == "_MainTex"):
                if (texName != "null"):
                    bkgtex_node = self.buildTextureNode(mat.node_tree, self.texsPath[texName], False, uv_judge=uv_judge)
                    if bkgtex_node is not None:
                        mat.node_tree.links.new(bkgtex_node.outputs['Color'], group.inputs['EmissionMap'])
                        group.inputs["EmissionColor"].default_value = (
                            float(BkgRGBA[0]) * brightness, float(BkgRGBA[1]) * brightness,
                            float(BkgRGBA[2]) * brightness, float(BkgRGBA[3]))

    def setBattleDecalNode(self, i, matnodes, mat, matShaderName, material_datas, suffix, blends, uv_judge):
        group = matnodes.new(type='ShaderNodeGroup')
        group.node_tree = bpy.data.node_groups[blends[0]]
        group.location = (-500, 0)
        out = matnodes.new(type='ShaderNodeOutputMaterial')
        mat.node_tree.links.new(group.outputs['BSDF'], out.inputs['Surface'])
        for node in matnodes:
            node.select = False

        group.select = True
        # matnodes.active = group
        # bpy.ops.node.group_ungroup()

        matnodes = mat.node_tree.nodes
        group.inputs["isOpaque"].default_value = 1.0
        # Transparent
        if "Transparent" in matShaderName or "SceneDecal" in matShaderName:
            mat.blend_method = 'HASHED'
            group.inputs["isOpaque"].default_value = 0.0

        attr = material_datas[i].find("Attribute").attrib
        BkgRGBA = attr["RGBA"].split(",")
        EmisRGBA = attr["_BkgEmissionColor"].split(",")

        group.inputs["BkgColor"].default_value = (
            float(BkgRGBA[0]), float(BkgRGBA[1]), float(BkgRGBA[2]), float(BkgRGBA[3]))
        group.inputs["BkgColorAlpha"].default_value = float(BkgRGBA[3])  # alpha

        group.inputs["TexColor"].default_value = (1.0, 1.0, 1.0, 1.0)
        group.inputs["TexColorAlpha"].default_value = 1.0  # alpha

        group.inputs['Roughness'].default_value = float(attr["Roughness"])

        for tex in material_datas[i].findall("Texture"):
            texName = tex.attrib["Name"]
            texShaderName = tex.attrib["ShaderName"]
            if (texShaderName == "_MainTex"):
                if (texName != "null"):
                    bkgtex_node = self.buildTextureNode(mat.node_tree, self.texsPath[texName], False, uv_judge=uv_judge)
                    if bkgtex_node is not None:
                        mat.node_tree.links.new(bkgtex_node.outputs['Color'], group.inputs['BkgTex'])
                        mat.node_tree.links.new(bkgtex_node.outputs['Alpha'], group.inputs['BkgTexAlpha'])
            if (texShaderName == "_BkgNormalMap"):
                if (texName != "null"):
                    bkgnormal_node = self.buildTextureNode(mat.node_tree, self.texsPath[texName], False,
                                                           uv_judge=uv_judge)
                    if bkgnormal_node is not None:
                        bkgnormal_node.image.colorspace_settings.name = "Linear Rec.709"
                        mat.node_tree.links.new(bkgnormal_node.outputs['Color'], group.inputs['BkgNormal'])
                        mat.node_tree.links.new(bkgnormal_node.outputs['Alpha'], group.inputs['BkgNormalAlpha'])
            if (texShaderName == "_BkgEmissionMap"):
                if (texName != "null"):
                    bkgnormal_node = self.buildTextureNode(mat.node_tree, self.texsPath[texName], False,
                                                           uv_judge=uv_judge)
                    if bkgnormal_node is not None:
                        mat.node_tree.links.new(bkgnormal_node.outputs['Color'], group.inputs['EmissionMap'])
                        group.inputs["EmissionColor"].default_value = (
                            float(EmisRGBA[0]), float(EmisRGBA[1]), float(EmisRGBA[2]), float(EmisRGBA[3]))

    def _import_mat_blend(self, imported_objects):

        inner_path = "NodeTree"
        mesh_grp_dict = {}
        # original_type = bpy.context.area.type

        # bpy.context.area.type = 'print(bpy.context.area.type)'
        # self.log_handle.info('original_type:{}'.format(original_type))
        #
        # bpy.context.area.type = "CONSOLE"

        for imported_object in imported_objects:
            object_name = imported_object.name
            shader_names = self.get_shader_name_by_mesh(object_name)
            self.log_handle.info('object_name:{}'.format(object_name))
            self.log_handle.info('shader_names:{}'.format(str(shader_names)))

            if shader_names and shader_names[0] == "Papegame/NewVegetation":
                node_path = X3BaseMatVeg
                append_names = ["X3Vegetation", "X3VegetationRampTexUV", "UVScaleOffset"]

            else:
                node_path = X3BASEMAT
                append_names = ["X3NodeGroup", "X3SceneBlend", "UVScaleOffset"]
            grps = []

            # 获取添加节点组之前的节点组名称列表
            original_group_names = [group.name for group in bpy.data.node_groups]
            before_names = list(original_group_names)

            for append_name in append_names:

                bpy.ops.wm.append(
                    filepath=os.path.join(node_path, inner_path, append_name),
                    directory=os.path.join(node_path, inner_path),
                    filename=append_name
                )

                after_names = [group.name for group in bpy.data.node_groups]

                new_group_names = list(set(after_names) - set(before_names))

                before_names = list(after_names)

                gp = ''
                for grp in new_group_names:
                    if grp.split('.')[0] == append_name:
                        gp = grp
                        break
                if gp:
                    grps.append(gp)

            mesh_grp_dict[object_name] = grps
        # bpy.context.area.type= original_type

        return mesh_grp_dict

    def get_shader_name_by_mesh(self, mesh_name):
        objects = self._root.find("ObjectPart")
        shader_names = []
        for mesh in objects.findall("Mesh"):
            if mesh.attrib['objname'] == mesh_name:
                material_datas = mesh.findall("Material")
                for i in range(len(material_datas)):
                    mat_shader_name = material_datas[i].attrib["shaderName"]
                    shader_names.append(mat_shader_name)
                break
        return shader_names

    def get_group_names(self):
        return [grp.name for grp in bpy.data.node_groups]

    def get_import_groups(self, before_groups, after_groups):

        return list(set(after_groups) - set(before_groups))

    def buildTextureNode(self, mat_nodetree, texPath, isUV2=False, tex_ST=[], uv_judge=True):
        if os.path.exists(texPath):
            tex = mat_nodetree.nodes.new(type='ShaderNodeTexImage')
            tex.image = bpy.data.images.load(filepath=texPath)
            # set UV
            uv_node = mat_nodetree.nodes.new(type='ShaderNodeUVMap')
            if uv_judge == True:
                if isUV2:
                    uv_node.uv_map = "2u"
                else:
                    uv_node.uv_map = "1u"
            else:
                if isUV2:
                    uv_node.uv_map = "UVSet2"
                else:
                    uv_node.uv_map = "UVSet0"

            if len(tex_ST) > 0:
                vectMath_node = mat_nodetree.nodes.new(type='ShaderNodeVectorMath')
                vectMath_node.operation = 'MULTIPLY_ADD'
                vectMath_node.inputs[1].default_value[0] = float(tex_ST[0])
                vectMath_node.inputs[1].default_value[1] = float(tex_ST[1])
                vectMath_node.inputs[2].default_value[0] = float(tex_ST[2])
                vectMath_node.inputs[2].default_value[1] = float(tex_ST[3])

                mat_nodetree.links.new(uv_node.outputs['UV'], vectMath_node.inputs[0])
                mat_nodetree.links.new(vectMath_node.outputs[0], tex.inputs['Vector'])
            else:
                mat_nodetree.links.new(uv_node.outputs['UV'], tex.inputs['Vector'])
            return tex
        else:
            return None

    def buildTextureNodeWithoutUV(self, mat_nodetree, texPath,tex_ST=[]):
        if os.path.exists(texPath):
            tex = mat_nodetree.nodes.new(type='ShaderNodeTexImage')
            tex.image = bpy.data.images.load(filepath=texPath)

            if len(tex_ST) > 0:
                vectMath_node = mat_nodetree.nodes.new(type='ShaderNodeVectorMath')
                vectMath_node.operation = 'MULTIPLY_ADD'
                vectMath_node.inputs[1].default_value[0] = float(tex_ST[0])
                vectMath_node.inputs[1].default_value[1] = float(tex_ST[1])
                vectMath_node.inputs[2].default_value[0] = float(tex_ST[2])
                vectMath_node.inputs[2].default_value[1] = float(tex_ST[3])
                mat_nodetree.links.new(vectMath_node.outputs[0], tex.inputs['Vector'])
            return tex
        else:
            return None

    def _import_fbx(self):

        bpy.ops.import_scene.fbx(filepath=self._fbx_file)
        # bpy.ops.wm.read_factory_settings()
        imported_objects = self._get_select_objects()

        # imported_objects = self._get_select_objects()
        return imported_objects

    def _get_select_objects(self):
        all_objects = bpy.context.scene.objects
        self.log_handle.info('all_objects:{}'.format(str(all_objects)))
        return [obj for obj in all_objects if obj.select_get()]

    def _get_xml_root(self):
        tree = ET.parse(self._xml_file)
        return tree.getroot()

    def _find_xml_info_by_tag(self, tag='ImportTexture'):
        return [obj.attrib for obj in self._root.iter(tag)]

    def _get_shader_type_by_xml(self):
        pass


def main(fbx_file, context):
    local_log_dir = common_dir.get_localtemppath('blender_import/log')
    log_file = '{}/{}.log'.format(local_log_dir, uuid.uuid4())

    handle = PapeGameBlenderImport(fbx_file, log_file)

    handle.log_handle.info('context:{}'.format(context))
    handle.blender_import_with_mat(context)


if __name__ == '__main__':
    fbx_file = r'E:\blender_test\20260109\tree_ygd0024_002.fbx'
    # local_log_dir = common_dir.get_localtemppath('blender_import/log')
    # log_file = '{}/{}.log'.format(local_log_dir, uuid.uuid4())
    #
    # handle = PapeGameBlenderImport(fbx_file, log_file)
    main(fbx_file, bpy.context)

#     fbx_file = r'M:\projects\x3\publish\assets\envprop\ufocatcher_doubletype_standard_01_static\mod\unity\ufocatcher_doubletype_standard_01_static.drama_mdl.fbx'
#     main(fbx_file)
#     log_file = r'F:\p4_1818\Testbed-Dev\Assets\Scripts\TestBedOnly\Editor\Scene\SceneAssetLibTool\test31.log'
#     handle = PapeGameBlenderImport(fbx_file, log_file)
#     handle.blender_import_with_mat()
# loghandle=log.Logger(r'F:\p4_1818\Testbed-Dev\Assets\Scripts\TestBedOnly\Editor\Scene\SceneAssetLibTool\test.log')
# loghandle.info('{}'.format(blender_dict))

# print(PapeGameBlenderImport(fbx_file).blender_import_with_mat())
