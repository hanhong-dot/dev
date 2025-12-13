# Copyright (c) 2015 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

"""
Hook that loads defines all the available actions, broken down by publish type.
"""
import sgtk
from pyfbsdk import FBApplication
import os

HookBaseClass = sgtk.get_hook_baseclass()


class MotionbuilderActions(HookBaseClass):

    ##############################################################################################################
    # public interface - to be overridden by deriving classes

    def generate_actions(self, sg_publish_data, actions, ui_area):
        """
        Returns a list of action instances for a particular publish.
        This method is called each time a user clicks a publish somewhere in the UI.
        The data returned from this hook will be used to populate the actions menu for a publish.

        The mapping between Publish types and actions are kept in a different place
        (in the configuration) so at the point when this hook is called, the loader app
        has already established *which* actions are appropriate for this object.

        The hook should return at least one action for each item passed in via the
        actions parameter.

        This method needs to return detailed data for those actions, in the form of a list
        of dictionaries, each with name, params, caption and description keys.

        Because you are operating on a particular publish, you may tailor the output
        (caption, tooltip etc) to contain custom information suitable for this publish.

        The ui_area parameter is a string and indicates where the publish is to be shown.
        - If it will be shown in the main browsing area, "main" is passed.
        - If it will be shown in the details area, "details" is passed.
        - If it will be shown in the history area, "history" is passed.

        Please note that it is perfectly possible to create more than one action "instance" for
        an action! You can for example do scene introspection - if the action passed in
        is "character_attachment" you may for example scan the scene, figure out all the nodes
        where this object can be attached and return a list of action instances:
        "attach to left hand", "attach to right hand" etc. In this case, when more than
        one object is returned for an action, use the params key to pass additional
        data into the run_action hook.

        :param sg_publish_data: Shotgun data dictionary with all the standard publish fields.
        :param actions: List of action strings which have been defined in the app configuration.
        :param ui_area: String denoting the UI Area (see above).
        :returns List of dictionaries, each with keys name, params, caption and description
        """
        app = self.parent
        app.log_debug(
            "Generate actions called for UI element %s. "
            "Actions: %s. Publish Data: %s" % (ui_area, actions, sg_publish_data)
        )

        action_instances = []

        if "import" in actions:
            action_instances.append(
                {
                    "name": "import",
                    "params": None,
                    "caption": "Merge Contents",
                    "description": "This will imports the file contents into the current scene.",
                }
            )
        if "merge" in actions:
            action_instances.append(
                {
                    "name": "merge",
                    "params": None,
                    "caption": "Merge Contents",
                    "description": "This will merge the file contents into the current scene.",
                }
            )
        if "copy_publish" in actions:
            action_instances.append(
                {
                    "name": "copy_publish",
                    "params": None,
                    "caption": "Copy PublishFiles",
                    "description": "This will copy the publish file to the local computer.",
                }
            )

        return action_instances

    def execute_multiple_actions(self, actions):
        """
        Executes the specified action on a list of items.

        The default implementation dispatches each item from ``actions`` to
        the ``execute_action`` method.

        The ``actions`` is a list of dictionaries holding all the actions to execute.
        Each entry will have the following values:

            name: Name of the action to execute
            sg_publish_data: Publish information coming from Shotgun
            params: Parameters passed down from the generate_actions hook.

        .. note::
            This is the default entry point for the hook. It reuses the ``execute_action``
            method for backward compatibility with hooks written for the previous
            version of the loader.

        .. note::
            The hook will stop applying the actions on the selection if an error
            is raised midway through.

        :param list actions: Action dictionaries.
        """
        for single_action in actions:
            name = single_action["name"]
            sg_publish_data = single_action["sg_publish_data"]
            params = single_action["params"]
            self.execute_action(name, params, sg_publish_data)

    def execute_action(self, name, params, sg_publish_data):
        """
        Execute a given action. The data sent to this be method will
        represent one of the actions enumerated by the generate_actions method.

        :param name: Action name string representing one of the items returned by generate_actions.
        :param params: Params data, as specified by generate_actions.
        :param sg_publish_data: Shotgun data dictionary with all the standard publish fields.
        :returns: No return value expected.
        """
        app = self.parent
        app.log_debug(
            "Execute action called for action %s. "
            "Parameters: %s. Publish Data: %s" % (name, params, sg_publish_data)
        )

        # resolve path - forward slashes on all platforms in motionbuilder
        path = self.get_publish_path(sg_publish_data).replace(os.path.sep, "/")

        if name == "import":
            self._import(path, sg_publish_data)
        if name == 'merge':
            self._merge(path, sg_publish_data)
        if name == 'copy_publish':
            self._copy_publish(path, sg_publish_data)

    ##############################################################################################################
    # helper methods which can be subclassed in custom hooks to fine tune the behavior of things

    def _import(self, path, sg_publish_data):
        """
        Import contents of the given file into the scene.

        :param path: Path to file.
        :param sg_publish_data: Shotgun data dictionary with all the standard publish fields.
        """
        from pyfbsdk import FBApplication
        from pyfbsdk import FBFbxOptions
        from pyfbsdk import FBElementAction

        if not os.path.exists(path):
            raise Exception("File not found on disk - '%s'" % path)

        (_, ext) = os.path.splitext(path)

        if ext.lower() != ".fbx":
            raise Exception(
                "Unsupported file extension for '%s'. Only FBX files are supported."
                % path
            )
        namespace = "%s" % (
            sg_publish_data.get("entity").get("name")
        )

        entity_type = sg_publish_data.get("entity").get("type")

        asset_type = self.get_asset_type(sg_publish_data)
        if asset_type:
            asset_type = asset_type['sg_asset_type']

        namespace = namespace.replace(" ", "_")
        namespace = self.judge_namespace(namespace, split='__')

        if asset_type in ["weapon", "rolaccesory", "hair"]:
            entity_id = sg_publish_data.get("entity").get("id")
            parent_assets = self.__get_parent_assets(entity_type, entity_id)
            all_characters = self._get_all_characters()
            character_names = [c.LongName.split(":")[0] for c in all_characters ]
            parent_assets = [p for p in parent_assets if p['name'] in character_names]
            if parent_assets:
                namespace = parent_assets[0]['name']
            else:
                current_character = self.get_current_character()
                if current_character:
                    namespace = current_character.LongName.split(":")[0]

        fbxLoadOptions = FBFbxOptions(True, path)
        fbxLoadOptions.NamespaceList = namespace
        fbxLoadOptions.SetAll(FBElementAction.kFBElementActionMerge, True)
        for takeIndex in range(0, fbxLoadOptions.GetTakeCount()):
            fbxLoadOptions.SetTakeSelect(takeIndex, 0)
        app = FBApplication()
        app.FileMerge(path, False, fbxLoadOptions)

    def __get_parent_assets(self, entity_type, entity_id):
        if entity_type == 'Asset':
            filters = [
                ['id', 'is', entity_id]
            ]
            fields = ['parents']
            try:
                return self.parent.shotgun.find_one(entity_type, filters, fields)['parents']
            except:
                return None
        return None

    def _get_all_characters(self):
        from pyfbsdk import FBSystem
        return FBSystem().Scene.Characters

    def _copy_publish(self, path, sg_publish_data):
        """
        :param path: Path to file
        :param sg_publish_data: Shotgun data dictionary with all the standard publish fields.
        :return:
        """
        if not os.path.exists(path):
            raise Exception("File not found on disk - '%s'" % path)
        (_, ext) = os.path.splitext(path)

        if ext.lower() != ".fbx":
            raise Exception(
                "Unsupported file extension for '%s'. Only FBX files are supported."
                % path
            )
        _sub = os.path.dirname(path).split('publish')[-1]
        _local_dir = self._find_local_dir('Info_Temp/MB/X3/{}'.format(_sub))
        self._copy_file(path, _local_dir)
        cmd = 'cmd.exe /C start "Folder" "%s"' % _local_dir
        exit_code = os.system(cmd)
        if exit_code != 0:
            raise Exception("Failed to launch '%s'!" % cmd)

    def get_asset_type(self, sg_publish_data):
        entity_id = sg_publish_data.get("entity").get("id")
        entity_type = sg_publish_data.get("entity").get("type")
        if entity_type == 'Asset':
            filters = [
                ['id', 'is', entity_id]
            ]
            fields = ['sg_asset_type']
            return self.parent.shotgun.find_one(entity_type, filters, fields)

    def _copy_file(self, _scr, _tar):
        import shutil
        if _scr and os.path.exists(_scr):
            try:
                shutil.copy2(_scr, _tar)
            except:
                pass

    def _find_local_dir(self, sub_dir='Info_Temp/MB/X3'):
        _root = ''
        if os.path.exists('D:/'):
            _root = 'D:/'
        elif os.path.exists('E:/'):
            _root = 'E:/'
        elif os.path.exists('F:/'):
            _root = 'F:/'
        elif os.path.exists('C:/'):
            _root = 'C:/'
        if not _root:
            return False
        _local_dir = _root + sub_dir
        if not os.path.exists(_local_dir):
            try:
                os.makedirs(_local_dir)
            except:
                return False
        return _local_dir

    def _getnamespacelist(self):
        """

        """
        from pyfbsdk import FBStringList
        from pyfbsdk import FBSystem

        _namespacelist = []
        NS = FBStringList()
        Count = FBSystem().Scene.NamespaceGetChildrenList(NS)
        for i in NS:
            try:
                localNS = FBSystem().Scene.NamespaceGet(i)
                _namespacelist.append(localNS.Name)
            except:
                pass
        if _namespacelist:
            return list(set(_namespacelist))

    def judge_namespace(self, namespace, split='_'):
        namespacelist = self._getnamespacelist()
        if namespacelist:
            if namespace in namespacelist:
                while namespace in namespacelist:
                    if split not in namespace:
                        namespace = "{}{}01".format(namespace, split)
                    else:
                        namespace = "{}{}0{}".format(namespace.split(split)[0], split,
                                                     int(namespace.split(split)[-1]) + 1)
                    if namespace not in namespacelist:
                        return namespace
            else:
                return namespace
        else:
            return namespace

    def _merge(self, path, sg_publish_data):
        """
        Import contents of the given file into the scene.

        :param path: Path to file.
        :param sg_publish_data: Shotgun data dictionary with all the standard publish fields.
        """
        from pyfbsdk import FBApplication
        from pyfbsdk import FBFbxOptions

        if not os.path.exists(path):
            raise Exception("File not found on disk - '%s'" % path)

        (_, ext) = os.path.splitext(path)

        if ext.lower() != ".fbx":
            raise Exception(
                "Unsupported file extension for '%s'. Only FBX files are supported."
                % path
            )
        fbxLoadOptions = FBFbxOptions(True)
        for takeIndex in range(0, fbxLoadOptions.GetTakeCount()):
            fbxLoadOptions.SetTakeSelect(takeIndex, 0)
        app = FBApplication()
        app.FileMerge(path, False, fbxLoadOptions)

    def get_current_character(self):
        return FBApplication().CurrentCharacter
