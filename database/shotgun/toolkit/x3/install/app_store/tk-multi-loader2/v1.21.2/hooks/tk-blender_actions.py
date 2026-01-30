# ----------------------------------------------------------------------------
# Copyright (c) 2020, Diego Garcia Huerta.
#
# Your use of this software as distributed in this GitHub repository, is
# governed by the Apache License 2.0
#
# Your use of the Shotgun Pipeline Toolkit is governed by the applicable
# license agreement between you and Autodesk / Shotgun.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------


"""
Hook that loads defines all the available actions, broken down by publish type.
"""

import os
from contextlib import contextmanager

import bpy
import sgtk
from sgtk.errors import TankError

__author__ = "Diego Garcia Huerta"
__contact__ = "https://www.linkedin.com/in/diegogh/"

HookBaseClass = sgtk.get_hook_baseclass()

VEGSHADERLIST = ["Papegame/NewVegetation", "Papegame/GIVegetation"]
def get_view3d_operator_context():
    """
    Adapted from several sources, it seems like  io ops needs a
    specific context that if run external to the Blender console needs to
    be specified
    """
    for window in bpy.context.window_manager.windows:
        for area in window.screen.areas:
            if area.type == "VIEW_3D":
                for region in area.regions:
                    if region.type == "WINDOW":
                        context_override = {
                            "window": window,
                            "screen": window.screen,
                            "area": area,
                            "region": region,
                            "scene": bpy.context.scene,
                        }
                        return context_override
    return None


class BlenderActions(HookBaseClass):

    ###########################################################################
    # public interface - to be overridden by deriving classes

    def generate_actions(self, sg_publish_data, actions, ui_area):
        """
        Returns a list of action instances for a particular publish. This
        method is called each time a user clicks a publish somewhere in the UI.
        The data returned from this hook will be used to populate the actions
        menu for a publish.

        The mapping between Publish types and actions are kept in a different
        place (in the configuration) so at the point when this hook is called,
        the loader app has already established *which* actions are appropriate
        for this object.

        The hook should return at least one action for each item passed in via
        the actions parameter.

        This method needs to return detailed data for those actions, in the
        form of a list of dictionaries, each with name, params, caption and
        description keys.

        Because you are operating on a particular publish, you may tailor the
        output  (caption, tooltip etc) to contain custom information suitable
        for this publish.

        The ui_area parameter is a string and indicates where the publish is to
        be shown.
        - If it will be shown in the main browsing area, "main" is passed.
        - If it will be shown in the details area, "details" is passed.
        - If it will be shown in the history area, "history" is passed.

        Please note that it is perfectly possible to create more than one
        action "instance" for an action!
        You can for example do scene introspectionvif the action passed in
        is "character_attachment" you may for examplevscan the scene, figure
        out all the nodes where this object can bevattached and return a list
        of action instances: "attach to left hand",v"attach to right hand" etc.
        In this case, when more than  one object isvreturned for an action, use
        the params key to pass additional data into the run_action hook.

        :param sg_publish_data: Shotgun data dictionary with all the standard
                                publish fields.
        :param actions: List of action strings which have been
                        defined in the app configuration.
        :param ui_area: String denoting the UI Area (see above).
        :returns List of dictionaries, each with keys name, params, caption
         and description
        """

        app = self.parent
        app.log_debug(
            "Generate actions called for UI element %s. "
            "Actions: %s. Publish Data: %s" % (ui_area, actions, sg_publish_data)
        )

        action_instances = []

        if "link" in actions:
            action_instances.append(
                {
                    "name": "link",
                    "params": None,
                    "caption": "Link Library file",
                    "description": (
                        "This will link the contents of the chosen item"
                        " to the current collection."
                    ),
                }
            )

        if "import" in actions:
            action_instances.append(
                {
                    "name": "import",
                    "params": None,
                    "caption": "Import into Collection",
                    "description": (
                        "This will import the item into the current collection."
                    ),
                }
            )

        if "append" in actions:
            action_instances.append(
                {
                    "name": "append",
                    "params": None,
                    "caption": "Append Library File",
                    "description": (
                        "This will add the contents of the chosen item"
                        " to the current collection."
                    ),
                }
            )

        if "asCompositorNodeMovieClip" in actions:
            action_instances.append(
                {
                    "name": "asCompositorNodeMovieClip",
                    "params": None,
                    "caption": "As Compositor Movie Clip",
                    "description": (
                        "This will create a new compositor node and load the movie into it"
                    ),
                }
            )

        if "asCompositorNodeImage" in actions:
            action_instances.append(
                {
                    "name": "asCompositorNodeImage",
                    "params": None,
                    "caption": "As Compositor Image Node",
                    "description": (
                        "This will create a new compositor node and load the image into it"
                    ),
                }
            )

        if "asSequencerImage" in actions:
            action_instances.append(
                {
                    "name": "asSequencerImage",
                    "params": None,
                    "caption": "As Sequencer Image (channel 3)",
                    "description": (
                        "This will create a new sound clip in the sequencer in channel 3"
                    ),
                }
            )

        if "asSequencerMovie" in actions:
            action_instances.append(
                {
                    "name": "asSequencerMovie",
                    "params": None,
                    "caption": "As Sequencer Movie (channel 1)",
                    "description": (
                        "This will create a new sound clip in the sequencer in channel 1"
                    ),
                }
            )

        if "asSequencerSound" in actions:
            action_instances.append(
                {
                    "name": "asSequencerSound",
                    "params": None,
                    "caption": "As Sequencer Sound (channel 2)",
                    "description": (
                        "This will create a new sound clip in the sequencer in channel 2"
                    ),
                }
            )

        return action_instances

    def execute_multiple_actions(self, actions):
        """
        Executes the specified action on a list of items.

        The default implementation dispatches each item from ``actions`` to
        the ``execute_action`` method.

        The ``actions`` is a list of dictionaries holding all the actions to
        execute.
        Each entry will have the following values:

            name: Name of the action to execute
            sg_publish_data: Publish information coming from Shotgun
            params: Parameters passed down from the generate_actions hook.

        .. note::
            This is the default entry point for the hook. It reuses the
            ``execute_action`` method for backward compatibility with hooks
             written for the previous version of the loader.

        .. note::
            The hook will stop applying the actions on the selection if an
            error is raised midway through.

        :param list actions: Action dictionaries.
        """
        app = self.parent
        for single_action in actions:
            app.log_debug("Single Action: %s" % single_action)
            name = single_action["name"]
            sg_publish_data = single_action["sg_publish_data"]
            params = single_action["params"]

            self.execute_action(name, params, sg_publish_data)

    def execute_action(self, name, params, sg_publish_data):
        """
        Execute a given action. The data sent to this be method will
        represent one of the actions enumerated by the generate_actions method.

        :param name: Action name string representing one of the items returned
                     by generate_actions.
        :param params: Params data, as specified by generate_actions.
        :param sg_publish_data: Shotgun data dictionary with all the standard
                                publish fields.
        :returns: No return value expected.
        """
        app = self.parent
        app.log_debug(
            "Execute action called for action %s. "
            "Parameters: %s. Publish Data: %s" % (name, params, sg_publish_data)
        )

        # resolve path
        # toolkit uses utf-8 encoded strings internally and Blender API
        # expects unicode so convert the path to ensure filenames containing
        # complex characters are supported
        path = self.get_publish_path(sg_publish_data).replace(os.path.sep, "/")

        if name == "link":
            self._create_link(path, sg_publish_data)

        if name == "append":
            self._create_append(path, sg_publish_data)

        if name == "import":
            self._do_import(path, sg_publish_data)

        if name == "asCompositorNodeMovieClip":
            self._create_compositor_node_movie_clip(path, sg_publish_data)

        if name == "asCompositorNodeImage":
            self._create_compositor_node_image(path, sg_publish_data)

        if name == "asSequencerImage":
            self._create_sequencer_image(path, sg_publish_data)

        if name == "asSequencerMovie":
            self._create_sequencer_movie(path, sg_publish_data)

        if name == "asSequencerSound":
            self._create_sequencer_sound(path, sg_publish_data)

    ###########################################################################
    # helper methods which can be subclassed in custom hooks to fine tune the
    # behaviour of things

    def _create_link(self, path, sg_publish_data):
        """
        Create a reference with the same settings Blender would use
        if you used the create settings dialog.

        :param path: Path to file.
        :param sg_publish_data: Shotgun data dictionary with all the standard
                                publish fields.
        """
        if not os.path.exists(path):
            raise TankError("File not found on disk - '%s'" % path)

        with bpy.data.libraries.load(path, link=True) as (data_from, data_to):
            data_to.collections = data_from.collections

        for collection in data_to.collections:
            new_collection = bpy.data.objects.new(collection.name, None)
            new_collection.instance_type = "COLLECTION"
            new_collection.instance_collection = collection
            bpy.context.scene.collection.objects.link(new_collection)

    def _create_append(self, path, sg_publish_data):
        """
        Create a reference with the same settings Blender would use
        if you used the create settings dialog.

        :param path: Path to file.
        :param sg_publish_data: Shotgun data dictionary with all the standard
                                publish fields.
        """
        if not os.path.exists(path):
            raise TankError("File not found on disk - '%s'" % path)

        with bpy.data.libraries.load(path, link=False) as (data_from, data_to):
            data_to.collections = data_from.collections

        for collection in data_to.collections:
            new_collection = bpy.data.objects.new(collection.name, None)
            new_collection.instance_type = "COLLECTION"
            new_collection.instance_collection = collection
            bpy.context.scene.collection.objects.link(new_collection)

    def _do_import(self, path, sg_publish_data):
        """
        Create a reference with the same settings Blender would use
        if you used the create settings dialog.

        :param path: Path to file.
        :param sg_publish_data: Shotgun data dictionary with all the standard
                                publish fields.
        """
        if not os.path.exists(path):
            raise TankError("File not found on disk - '%s'" % path)


        self.blender_import_with_mat(path)
        # result=self._batch_import(path)

        # _, extension = os.path.splitext(path)
        #
        # extension_name = extension.lower()[1:]
        #
        # context = get_view3d_operator_context()
        #
        # if extension_name in ("abc",):
        #     bpy.ops.wm.alembic_import(context, filepath=path, as_background_job=False)
        #
        # elif extension_name in ("dae",):
        #     bpy.ops.wm.collada_import(context, filepath=path, as_background_job=False)
        #
        # elif extension_name in dir(bpy.ops.import_scene):
        #     if extension_name not in ["fbx"]:
        #         importer = getattr(bpy.ops.import_scene, extension_name)
        #         importer(filepath=path)
        #     else:
        #        from apps.tools.blender import blender_import
        #        path=str(path).replace("\\","/")
        #        blender_import.main(path)
        #
        # elif extension_name in dir(bpy.ops.import_mesh):
        #     importer = getattr(bpy.ops.import_mesh, extension_name)
        #     importer(filepath=path)
        #
        # elif extension_name in dir(bpy.ops.import_curve):
        #     importer = getattr(bpy.ops.import_curve, extension_name)
        #     importer(filepath=path)
        #
        # elif extension_name in dir(bpy.ops.import_anim):
        #     importer = getattr(bpy.ops.import_anim, extension_name)
        #     importer(filepath=path)
        #
        # else:
        #     raise TankError(
        #         "File extension not supported %s - '%s'" % (extension_name, path)
        #     )

    # def _batch_import(self, path):
    #     py = r"E:\dev\apps\tools\blender\blender_import.py"
    #     return self._process_batch_py(py, path)

    # def _process_batch_py(self, py, path):
    #     blend_exe = r"blender.exe"
    #     cmd = '"{}" -b -P {} -- {}'.format(str(blend_exe), py, path)
    #     return os.system(cmd)

    def _create_compositor_node_movie_clip(self, path, sg_publish_data):
        """
        Create a new clip compositor node and load the selected publish into it.

        :param path: Path to file.
        :param sg_publish_data: Shotgun data dictionary with all the standard
                                publish fields.
        """
        if not bpy.context.scene.node_tree:
            bpy.context.scene.use_nodes = True

        node = bpy.context.scene.node_tree.nodes.new("CompositorNodeMovieClip")

        # store the ids of the current clips
        # I use id from python because I could not find another way to
        # uniquely identify the data
        current_movie_clip_ids = list(map(id, bpy.data.movieclips))

        filename_path, filename_file = os.path.split(path)
        bpy.ops.clip.open(
            directory=filename_path,
            files=[{"name": filename_file, "name": filename_file}],
            relative_path=True,
        )

        app = self.parent

        app.sgtk.teamplate_from_path()

        # find the newly import clip
        for clip in bpy.data.movieclips:
            if id(clip) not in current_movie_clip_ids:
                node.clip = clip
                break

    def _create_compositor_node_image(self, path, sg_publish_data):
        """
        Create a new image compositor node and load the selected publish into it.

        :param path: Path to file.
        :param sg_publish_data: Shotgun data dictionary with all the standard
                                publish fields.
        """

        if not bpy.context.scene.node_tree:
            bpy.context.scene.use_nodes = True

        node = bpy.context.scene.node_tree.nodes.new("CompositorNodeImage")

        # store the ids of the current images
        # I use id from python because I could not find another way to
        # uniquely identify the data
        current_ids = list(map(id, bpy.data.movieclips))

        filename_path, filename_file = os.path.split(path)

        bpy.ops.image.open(
            filepath=path,
            directory=filename_path,
            files=[{"name": filename_file}],
            relative_path=False,
        )

        # find the newly import image
        for image in bpy.data.images:
            if id(image) not in current_ids:
                node.image = image
                break

    def _create_sequencer_sound(self, path, sg_publish_data):
        """
        Create a new sound for the sequence editor and load the selected publish into it.
        Note we always use channel 2

        :param path: Path to file.
        :param sg_publish_data: Shotgun data dictionary with all the standard
                                publish fields.
        """

        filename_path, filename_file = os.path.split(path)
        bpy.context.scene.sequence_editor.sequences.new_sound(
            filename_file,
            filepath=path,
            channel=2,
            frame_start=bpy.context.scene.frame_current,
        )

    def _create_sequencer_movie(self, path, sg_publish_data):
        """
        Create a new movie for the sequence editor and load the selected publish into it.
        Note we always use channel 1

        :param path: Path to file.
        :param sg_publish_data: Shotgun data dictionary with all the standard
                                publish fields.
        """

        filename_path, filename_file = os.path.split(path)
        bpy.context.scene.sequence_editor.sequences.new_movie(
            filename_file,
            filepath=path,
            channel=1,
            frame_start=bpy.context.scene.frame_current,
        )

    def _create_sequencer_image(self, path, sg_publish_data):
        """
        Create a new image for the sequence editor and load the selected publish into it.
        Note we always use channel 3

        :param path: Path to file.
        :param sg_publish_data: Shotgun data dictionary with all the standard
                                publish fields.
        """

        filename_path, filename_file = os.path.split(path)
        bpy.context.scene.sequence_editor.sequences.new_image(
            filename_file,
            filepath=path,
            channel=3,
            frame_start=bpy.context.scene.frame_current,
        )

    def blender_import_with_mat(self, path):
        xml_file = path.replace(".fbx", ".xml")
        self._root = self._get_xml_root(xml_file)

        imported_objects = self._import_fbx(path)

        if not imported_objects:
            raise TankError("File not found import objects")

        blender_dict = self._import_mat_blend( xml_file,imported_objects)

        self._builder_pre_mesh(xml_file, blender_dict)
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

    def _builder_pre_mesh(self, xml_file, blender_dict):
        self.texsPath = self.get_texs_path()
        self._root = self._get_xml_root(xml_file)

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

                if mat is None:
                    continue
                mat.name = '{}__{}'.format(mesh_name.replace('.', '_'), mat_name)
                mesh_obj = bpy.data.objects[mesh_name]
                uv_judge = False
                try:
                    for uv_map in mesh_obj.data.uv_layers:
                        if uv_map.name == "1u":
                            uv_judge = True
                            break
                except:
                    continue

                mat.use_nodes = True
                matnodes = mat.node_tree.nodes
                matnodes.clear()

                if "SceneDecal" in mat_shader_name:
                    self.setBattleDecalNode(i, matnodes, mat, mat_shader_name, material_datas, suffix, blends, uv_judge)
                elif "SceneUnlit" in mat_shader_name:
                    self.setSceneUnlitNode(i, matnodes, mat, mat_shader_name, material_datas, suffix, blends, uv_judge)
                elif "SceneBlend" in mat_shader_name:
                    self.setSceneBlendNode(i, matnodes, mat, mat_shader_name, material_datas, suffix, blends, uv_judge)
                elif mat_shader_name in VEGSHADERLIST:
                    self.setVegetationNode(i, matnodes, mat, mat_shader_name, material_datas, suffix, blends, uv_judge)
                else:
                    self.setSceneNode(i, matnodes, mat, mat_shader_name, material_datas, suffix, blends, uv_judge)

    def get_mesh_grps_from_mesh_dict(self, mesh, blender_dict):
        mesh_name = mesh.attrib['objname']

        blends = []
        suffix = ''
        for k, v in blender_dict.items():
            name = k.name
            infos = name.split('.')
            if len(infos) > 1:
                if infos[0] == mesh.attrib['objname']:
                    mesh_name = name
                    blends = v
                    suffix = infos[-1]
                    break
            else:
                if name == mesh.attrib['objname']:
                    mesh_name = name
                    blends = v
                    break
        return mesh_name, blends, suffix

    def setVegetationNode(self, i, matnodes, mat, matShaderName, material_datas, suffix, blends, uv_judge):
        group = matnodes.new(type='ShaderNodeGroup')

        group.node_tree = bpy.data.node_groups[blends[0]]
        group.location = (-500, 0)
        out = matnodes.new(type='ShaderNodeOutputMaterial')

        group_random = matnodes.new(type='ShaderNodeGroup')
        group_random.node_tree = bpy.data.node_groups[blends[1]]
        group_random.location = (-800, -200)

        mat.node_tree.links.new(group.outputs['BSDF'], out.inputs['Surface'])
        for node in matnodes:
            node.select = False
        group.select = True
        attr = material_datas[i].find("Attribute").attrib
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

            texShaderName = tex.attrib["ShaderName"]

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

                    abedo_node01 = self.buildTextureNodeWithoutUV(mat.node_tree, self.texsPath[texName], [])
                    abedo_node02 = self.buildTextureNodeWithoutUV(mat.node_tree, self.texsPath[texName], [])
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
            group.inputs['TexTexAlpha'].default_value = 1.0
        elif not hasBkgTex:  # 2
            group.inputs['isColorMode1'].default_value = 0.0
            group.inputs['isColorMode2'].default_value = 1.0
            group.inputs['BkgTexAlpha'].default_value = 1.0

        if not hasTexNormal:
            group.inputs['isNormalMode1'].default_value = 1.0
            group.inputs['isNormalMode2'].default_value = 0.0
            group.inputs['BlendNormal'].default_value = 0.0
        elif not hasBkgNormal:
            group.inputs['isNormalMode1'].default_value = 0.0
            group.inputs['isNormalMode2'].default_value = 1.0
            group.inputs['BlendNormal'].default_value = 0.0

    def buildTextureNodeWithoutUV(self, mat_nodetree, texPath, tex_ST=[]):
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

    def get_texs_path(self):
        texsPath = {}
        for tex in self._root.find("TexturePart").findall('ImportTexture'):
            texname = tex.attrib['Name']
            texpath = tex.attrib['Path']
            texsPath[texname] = texpath
        return texsPath

    def setSceneNode(self, i, matnodes, mat, matShaderName, material_datas, suffix, blends, uv_judge):

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
        TexRGBA1 = attr["TexRGBA1"].split(",")
        TexRGBA2 = attr["TexRGBA2"].split(",")
        GradientStep = attr["GradientStep"].split(",")
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

        group.inputs["TexColor1"].default_value = (
            float(TexRGBA1[0]), float(TexRGBA1[1]), float(TexRGBA1[2]), float(TexRGBA1[3]))

        group.inputs["TexColor2"].default_value = (
            float(TexRGBA2[0]), float(TexRGBA2[1]), float(TexRGBA2[2]), float(TexRGBA2[3]))

        group.inputs["GradientStepXYZ"].default_value = (
            float(GradientStep[0]), float(GradientStep[1]), float(GradientStep[2]))
        group.inputs["GradientStepW"].default_value = float(GradientStep[3])  # alpha

        group.inputs["EmissionColor"].default_value = (
            float(EmiRGBA[0]), float(EmiRGBA[1]), float(EmiRGBA[2]), float(EmiRGBA[3]))

        group.inputs['Metallic'].default_value = float(attr["Matallic"])
        group.inputs['Roughness'].default_value = float(attr["Roughness"])
        group.inputs['BkgNormalScale'].default_value = float(attr["BkgNmlScale"])
        group.inputs['TexNormalScale'].default_value = float(attr["TexNmlScale"])

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
            group.inputs['TexTexAlpha'].default_value = 1.0
        elif not hasBkgTex:  # 2
            group.inputs['isColorMode1'].default_value = 0.0
            group.inputs['isColorMode2'].default_value = 1.0
            group.inputs['BkgTexAlpha'].default_value = 1.0

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

    def _import_mat_blend(self, xml_file, imported_objects):

        X3BASEMAT = r'Z:\dev\apps\tools\blender\X3BaseMat.blend'
        inner_path = "NodeTree"
        mesh_grp_dict = {}
        context_override = get_view3d_operator_context()

        for imported_object in imported_objects:
            if not imported_object or imported_object.type != 'MESH':
                continue
            object_name = imported_object.name
            # shader_names = self.get_shader_name_by_mesh(object_name, xml_file)
            #
            # if shader_names and shader_names[0] in VEGSHADERLIST:
            #     node_path = X3BaseMatVeg
            #     append_names = ["X3Vegetation", "X3VegetationRampTexUV", "UVScaleOffset"]
            #
            # else:
            #     node_path = X3BASEMAT
            #     append_names = ["X3NodeGroup", "X3SceneBlend", "UVScaleOffset"]
            node_path = X3BASEMAT
            append_names = ["X3NodeGroup", "X3SceneBlend", "X3Vegetation", "X3VegetationRampTexUV", "UVScaleOffset"]
            grps = []

            original_group_names = [group.name for group in bpy.data.node_groups]
            before_names = list(original_group_names)

            for append_name in append_names:
                with bpy.context.temp_override(**context_override):
                    bpy.ops.wm.append(
                        filepath=os.path.join(node_path, inner_path, append_name),
                        directory=os.path.join(node_path, inner_path),
                        filename=append_name

                    )

                after_names = [group.name for group in bpy.data.node_groups]
                new_group_names = list(set(after_names) - set(before_names))
                before_names = list(after_names)

                for grp in new_group_names:
                    if grp.split('.')[0] == append_name:
                        grps.append(grp)
                        break

            mesh_grp_dict[imported_object] = grps

        return mesh_grp_dict

    def get_shader_name_by_mesh(self, mesh_name, xml_file):
        root = self._get_xml_root(xml_file)
        objects = root.find("ObjectPart")
        shader_names = []
        for mesh in objects.findall("Mesh"):
            if mesh and mesh.attrib['objname'] == mesh_name:
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

    def _import_fbx(self, path):

        context_override = get_view3d_operator_context()
        with bpy.context.temp_override(**context_override):
            bpy.ops.import_scene.fbx(filepath=path)
        # bpy.ops.wm.read_factory_settings()
        imported_objects = self._get_select_objects()

        # imported_objects = self._get_select_objects()
        return imported_objects

    def _get_select_objects(self):
        all_objects = bpy.context.scene.objects
        return [obj for obj in all_objects if obj.select_get()]

    def _get_xml_root(self, xml_file):
        import xml.etree.ElementTree as ET
        tree = ET.parse(xml_file)
        return tree.getroot()

    def _find_xml_info_by_tag(self, tag='ImportTexture'):
        return [obj.attrib for obj in self._root.iter(tag)]
