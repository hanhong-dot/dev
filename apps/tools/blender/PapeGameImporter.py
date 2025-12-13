bl_info = {
    "name": "PapeGame Importer",
    "blender": (3, 30, 5),
    "category": "Object",
}

import bpy
import os
import xml.etree.ElementTree as ET
from bpy import context
import builtins as __builtin__

# def console_print(*args, **kwargs):
#     for a in context.screen.areas:
#         if a.type == 'CONSOLE':
#             c = {}
#             c['area'] = a
#             c['space_data'] = a.spaces.active
#             c['region'] = a.regions[-1]
#             c['window'] = context.window
#             c['screen'] = context.screen
#             s = " ".join([str(arg) for arg in args])
#             for line in s.split("\n"):
#                 bpy.ops.console.scrollback_append(c, text=line)
#
# def blender_print(*args, **kwargs):
#     """Console print() function."""
#     console_print(*args, **kwargs)  # to py consoles

class PapeGameImporter(bpy.types.Operator):
    """Import PapeGame scene from Unity"""  # Use this as a tooltip for menu items and buttons.
    bl_idname = "object.papegame_import"  # Unique identifier for buttons and menu items to reference.
    bl_label = "PapeGame Import"  # Display name in the interface.
    bl_options = {'REGISTER', 'UNDO'}  # Enable undo for the operator.
    texsPath = {}

    def readXml(self, xml_path, context):
        root = ET.parse(xml_path).getroot()
        mainPath = root.find("MainPath").attrib["UnityMainPath"].replace("\\", "/")
        fileName = root.find("FbxName").attrib["Name"]
        fbxPath = root.find("FbxName").attrib["Path"]
        texPart = root.find("TexturePart")

        for tex in texPart.findall("ImportTexture"):
            texname = tex.attrib["Name"]
            texpath = tex.attrib["Path"]
            self.texsPath[texname] = mainPath + "/" + texpath;
            # texsPath.append(mainPath + "/" + texpath)

        #for key, value in self.texsPath.items():
        #    print(key + "  " + value)

        bpy.ops.import_scene.fbx(filepath=fbxPath)

        if 'X3NodeGroup' not in bpy.data.node_groups or 'X3SceneBlend' not in bpy.data.node_groups:
            node_path = mainPath + "/Tools/BlenderScripts/X3BaseMat.blend"
            inner_path = "NodeTree"
            append_name = "X3NodeGroup"
            append_name2 = "X3SceneBlend"
            append_name3 = "UVScaleOffset"
            bpy.ops.wm.append(
                filepath=os.path.join(node_path, inner_path, append_name),
                directory=os.path.join(node_path, inner_path),
                filename=append_name
            )

            bpy.ops.wm.append(
                filepath=os.path.join(node_path, inner_path, append_name2),
                directory=os.path.join(node_path, inner_path),
                filename=append_name2
            )

            bpy.ops.wm.append(
                filepath=os.path.join(node_path, inner_path, append_name3),
                directory=os.path.join(node_path, inner_path),
                filename=append_name3
            )

        self.buildPreMesh(root, context)
        if 'Cube' in bpy.data.objects:
            bpy.data.objects.remove(bpy.data.objects['Cube'])

    def buildPreMesh(self, xml_root, context):
        objectPart = xml_root.find("ObjectPart")
        for mesh in objectPart.findall("Mesh"):
            objName = mesh.attrib["objname"]
            self.buildMaterial(objName, mesh, context)

    def buildTextureNode(self, mat_nodetree, texPath, isUV2=False, tex_ST = []):
        if os.path.exists(texPath):
            tex = mat_nodetree.nodes.new(type='ShaderNodeTexImage')
            tex.image = bpy.data.images.load(filepath=texPath)
            # set UV
            uv_node = mat_nodetree.nodes.new(type='ShaderNodeUVMap')
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

    def setSceneNode(self, i, matnodes, mat, matShaderName, material_datas):
        group = matnodes.new(type='ShaderNodeGroup')
        group.node_tree = bpy.data.node_groups['X3NodeGroup']
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
                    bkgtex_node = self.buildTextureNode(mat.node_tree, self.texsPath[texName], False, MainTex_ST)
                    if bkgtex_node is not None:
                        mat.node_tree.links.new(bkgtex_node.outputs['Color'], group.inputs['BkgTex'])
                        mat.node_tree.links.new(bkgtex_node.outputs['Alpha'], group.inputs['BkgTexAlpha'])
                        hasBkgTex = True
            if (texShaderName == "_BkgNormalMap"):
                if (texName != "null"):
                    bkgnormal_node = self.buildTextureNode(mat.node_tree, self.texsPath[texName], False, MainTex_ST)
                    if bkgnormal_node is not None:
                        bkgnormal_node.image.colorspace_settings.name = "Linear"
                        mat.node_tree.links.new(bkgnormal_node.outputs['Color'], group.inputs['BkgNormal'])
                        mat.node_tree.links.new(bkgnormal_node.outputs['Alpha'], group.inputs['BkgNormalAlpha'])
                        hasBkgNormal = True
            if (texShaderName == "_TexAlbedoMap"):
                if (texName != "null"):
                    textex_node = self.buildTextureNode(mat.node_tree, self.texsPath[texName], True, TexAlbedoMap_ST)
                    if textex_node is not None:
                        mat.node_tree.links.new(textex_node.outputs['Color'], group.inputs['TexTex'])
                        mat.node_tree.links.new(textex_node.outputs['Alpha'], group.inputs['TexTexAlpha'])
                        hasTexTex = True
            if (texShaderName == "_TexNormalMap"):
                if (texName != "null"):
                    texnormal_node = self.buildTextureNode(mat.node_tree, self.texsPath[texName], True, TexNormalMap_ST)
                    if texnormal_node is not None:
                        texnormal_node.image.colorspace_settings.name = "Linear"
                        mat.node_tree.links.new(texnormal_node.outputs['Color'], group.inputs['TexNormal'])
                        mat.node_tree.links.new(texnormal_node.outputs['Alpha'], group.inputs['TexNormalAlpha'])
                        hasTexNormal = True
            if (texShaderName == "_BkgEmissionMap"):
                if (texName != "null"):
                    texnormal_node = self.buildTextureNode(mat.node_tree, self.texsPath[texName], False, MainTexEmi_ST)
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


    def setBattleDecalNode(self, i, matnodes, mat, matShaderName, material_datas):
        group = matnodes.new(type='ShaderNodeGroup')
        group.node_tree = bpy.data.node_groups['X3NodeGroup']
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
                    bkgtex_node = self.buildTextureNode(mat.node_tree, self.texsPath[texName], False)
                    if bkgtex_node is not None:
                        mat.node_tree.links.new(bkgtex_node.outputs['Color'], group.inputs['BkgTex'])
                        mat.node_tree.links.new(bkgtex_node.outputs['Alpha'], group.inputs['BkgTexAlpha'])
            if (texShaderName == "_BkgNormalMap"):
                if (texName != "null"):
                    bkgnormal_node = self.buildTextureNode(mat.node_tree, self.texsPath[texName], False)
                    if bkgnormal_node is not None:
                        bkgnormal_node.image.colorspace_settings.name = "Linear"
                        mat.node_tree.links.new(bkgnormal_node.outputs['Color'], group.inputs['BkgNormal'])
                        mat.node_tree.links.new(bkgnormal_node.outputs['Alpha'], group.inputs['BkgNormalAlpha'])
            if (texShaderName == "_BkgEmissionMap"):
                if (texName != "null"):
                    bkgnormal_node = self.buildTextureNode(mat.node_tree, self.texsPath[texName], False)
                    if bkgnormal_node is not None:
                        mat.node_tree.links.new(bkgnormal_node.outputs['Color'], group.inputs['EmissionMap'])
                        group.inputs["EmissionColor"].default_value = (
                            float(EmisRGBA[0]), float(EmisRGBA[1]), float(EmisRGBA[2]), float(EmisRGBA[3]))

    def setSceneUnlitNode(self, i, matnodes, mat, matShaderName, material_datas):
        group = matnodes.new(type='ShaderNodeGroup')
        group.node_tree = bpy.data.node_groups['X3NodeGroup']
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
                    bkgtex_node = self.buildTextureNode(mat.node_tree, self.texsPath[texName], False)
                    if bkgtex_node is not None:
                        mat.node_tree.links.new(bkgtex_node.outputs['Color'], group.inputs['EmissionMap'])
                        group.inputs["EmissionColor"].default_value = (
                            float(BkgRGBA[0]) * brightness, float(BkgRGBA[1]) * brightness,
                            float(BkgRGBA[2]) * brightness, float(BkgRGBA[3]))

    def setSceneBlendNode(self, i, matnodes, mat, matShaderName, material_datas):
        group = matnodes.new(type='ShaderNodeGroup')
        group.node_tree = bpy.data.node_groups['X3SceneBlend']
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
                    tex_node = self.buildTextureNode(mat.node_tree, self.texsPath[texName], False)
                    if tex_node is not None:
                        mat.node_tree.links.new(tex_node.outputs['Color'], group.inputs['MainTex1'])
            if (texShaderName == "_BumpMap"):
                if (texName != "null"):
                    normal_node = self.buildTextureNode(mat.node_tree, self.texsPath[texName], False)
                    if normal_node is not None:
                        normal_node.image.colorspace_settings.name = "Linear"
                        mat.node_tree.links.new(normal_node.outputs['Color'], group.inputs['BumpMap1'])
                        mat.node_tree.links.new(normal_node.outputs['Alpha'], group.inputs['RoughnessMap1'])
            if (texShaderName == "_MainTex2"):
                if (texName != "null"):
                    tex_node2 = self.buildTextureNode(mat.node_tree, self.texsPath[texName], False)
                    if tex_node2 is not None:
                        mat.node_tree.links.new(tex_node2.outputs['Color'], group.inputs['MainTex2'])
            if (texShaderName == "_BumpMap2"):
                if (texName != "null"):
                    normal_node2 = self.buildTextureNode(mat.node_tree, self.texsPath[texName], False)
                    if normal_node2 is not None:
                        normal_node2.image.colorspace_settings.name = "Linear"
                        mat.node_tree.links.new(normal_node2.outputs['Color'], group.inputs['BumpMap2'])
                        mat.node_tree.links.new(normal_node2.outputs['Alpha'], group.inputs['RoughnessMap2'])
            if (texShaderName == "_MainTex3"):
                if (texName != "null"):
                    tex_node3 = self.buildTextureNode(mat.node_tree, self.texsPath[texName], False)
                    if tex_node3 is not None:
                        mat.node_tree.links.new(tex_node3.outputs['Color'], group.inputs['MainTex3'])
            if (texShaderName == "_BumpMap3"):
                if (texName != "null"):
                    normal_node3 = self.buildTextureNode(mat.node_tree, self.texsPath[texName], False)
                    if normal_node3 is not None:
                        normal_node3.image.colorspace_settings.name = "Linear"
                        mat.node_tree.links.new(normal_node3.outputs['Color'], group.inputs['BumpMap3'])
                        mat.node_tree.links.new(normal_node3.outputs['Alpha'], group.inputs['RoughnessMap3'])
            if (texShaderName == "_BlendMask"):
                if (texName != "null"):
                    mask_node = self.buildTextureNode(mat.node_tree, self.texsPath[texName], False)
                    if mask_node is not None:
                        mask_node.image.colorspace_settings.name = "Linear"
                        mat.node_tree.links.new(mask_node.outputs['Color'], group.inputs['BlendMask'])

    def buildMaterial(self, obj_name, mesh_xml, context):
        #blender_print(obj_name)
        #if obj_name not in bpy.data.objects:
        #    return

        # if 'Cube' not in bpy.data.objects:
        #     bpy.ops.mesh.primitive_cube_add(enter_editmode=False, location=(0, 0, 0))

        # bpy.ops.object.mode_set(mode='OBJECT')
        for obj in bpy.data.objects:
            obj.select_set(state=False)

        # cube = bpy.data.objects["Cube"]
        # cube.select_set(state=True)
        # bpy.context.view_layer.objects.active = cube

        #material_slots = bpy.data.objects[obj_name].material_slots
        material_datas = mesh_xml.findall("Material")

        #if len(material_slots) > 0:
            #matname_list = []
            #for i in range(len(material_datas)):
            #    matname_list.append(material_slots[i].material.name)

        for i in range(len(material_datas)):
            matShaderName = material_datas[i].attrib["shaderName"]
            matName = material_datas[i].attrib["matName"]
            if matShaderName == "null":
                continue

            #mat = material_slots[i].material
            #if matName in matname_list:
            #    mat = material_slots[matname_list.index(matName)].material
            #else:
            #    continue
            mat = bpy.data.materials.get(matName)
            if mat is None:
                continue
            #blender_print(mat.name)

            # cube.active_material = mat
            # switch to Edit node window
            # type = bpy.context.area.type
            # bpy.context.area.type = 'NODE_EDITOR'

            mat.use_nodes = True
            matnodes = mat.node_tree.nodes
            matnodes.clear()

            # space = context.space_data
            # node_tree = space.node_tree

            if "SceneDecal" in matShaderName:
                self.setBattleDecalNode(i, matnodes, mat, matShaderName, material_datas)
            elif "SceneUnlit" in matShaderName:
                self.setSceneUnlitNode(i, matnodes, mat, matShaderName, material_datas)
            elif "SceneBlend" in matShaderName:
                self.setSceneBlendNode(i, matnodes, mat, matShaderName, material_datas)
            else:
                self.setSceneNode(i, matnodes, mat, matShaderName, material_datas)
            #mat.name = matName

    def execute(self, context):  # execute() is called when running the operator.
        self.readXml("D:\\Temp\\Mat.xml", context)
        return {'FINISHED'}  # Lets Blender know the operator finished successfully.


def menu_func(self, context):
    self.layout.operator(PapeGameImporter.bl_idname)


def register():
    bpy.utils.register_class(PapeGameImporter)
    bpy.types.VIEW3D_MT_object.append(menu_func)  # Adds the new operator to an existing menu.
    #blender_print(111)

def unregister():
    bpy.utils.unregister_class(PapeGameImporter)


# This allows you to run the script directly from Blender's Text editor
# to test the add-on without having to install it.
if __name__ == "__main__":
    register()
