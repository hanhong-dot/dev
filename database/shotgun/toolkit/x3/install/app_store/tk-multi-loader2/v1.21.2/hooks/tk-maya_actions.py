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

import glob
import os
import re
import maya.cmds as cmds
import maya.mel as mel
import sgtk

from tank_vendor import six

HookBaseClass = sgtk.get_hook_baseclass()


class MayaActions(HookBaseClass):

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
        if "open" in actions:
            action_instances.append(
                {
                    "name": "open",
                    "params": None,
                    "caption": "Open File",
                    "description": "This will Open File.",
                }
            )
        if "reference" in actions:
            action_instances.append(
                {
                    "name": "reference",
                    "params": None,
                    "caption": "Create Reference",
                    "description": "This will add the item to the scene as a standard reference.",
                }
            )
        if "replace_reference" in actions:
            action_instances.append(
                {
                    "name": "replace_reference",
                    "params": None,
                    "caption": "Replace reference",
                    "description": "This will replace reference ",
                }
            )

        if "import" in actions:
            action_instances.append(
                {
                    "name": "import",
                    "params": None,
                    "caption": "Import into Scene",
                    "description": "This will import the item into the current scene.",
                }
            )

        if "reference_no" in actions:
            action_instances.append(
                {
                    "name": "reference_no_namespace",
                    "params": None,
                    "caption": "Create Reference No Namespace",
                    "description": "This will add the item to the scene as a standard reference.",
                }
            )
        if "import_no" in actions:
            action_instances.append(
                {
                    "name": "import_no_namespace",
                    "params": None,
                    "caption": "Import into Scene No Namespace",
                    "description": "This will import the item into the current scene.",
                }
            )

        if "fbx_dir" in actions:
            action_instances.append(
                {
                    "name": "fbx_dir",
                    "params": None,
                    "caption": "Open Fbx Dir",
                    "description": "This will open fbx dir",
                }
            )
        if "tex_dir" in actions:
            action_instances.append(
                {
                    "name": "tex_dir",
                    "params": None,
                    "caption": "Open Tex Dir",
                    "description": "This will open tex dir",
                }
            )

        if "publish_dir" in actions:
            action_instances.append(
                {
                    "name": "copy_publishs",
                    "params": None,
                    "caption": "Copy PublishFiles",
                    "description": "This will copy the publish file to the local computer",
                }
            )

        if "texture_node" in actions:
            action_instances.append(
                {
                    "name": "texture_node",
                    "params": None,
                    "caption": "Create Texture Node",
                    "description": "Creates a file texture node for the selected item..",
                }
            )

        if "udim_texture_node" in actions:
            # Special case handling for Mari UDIM textures as these currently only load into
            # Maya 2015 in a nice way!
            if self._get_maya_version() >= 2015:
                action_instances.append(
                    {
                        "name": "udim_texture_node",
                        "params": None,
                        "caption": "Create Texture Node",
                        "description": "Creates a file texture node for the selected item..",
                    }
                )

        if "image_plane" in actions:
            action_instances.append(
                {
                    "name": "image_plane",
                    "params": None,
                    "caption": "Create Image Plane",
                    "description": "Creates an image plane for the selected item..",
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

        # resolve path
        # toolkit uses utf-8 encoded strings internally and Maya API expects unicode
        # so convert the path to ensure filenames containing complex characters are supported
        path = six.ensure_str(self.get_publish_path(sg_publish_data))

        if name == "reference":
            self._create_reference(path, sg_publish_data)
        if name == "replace_reference":
            self._replace_reference(path, sg_publish_data)

        if name == "import":
            self._do_import(path, sg_publish_data)

        if name == "open":
            self._do_open(path, sg_publish_data)

        if name == "reference_no_namespace":
            self._do_reference_nonamespace(path, sg_publish_data)

        if name == "import_no_namespace":
            self._do_import_nonameapce(path, sg_publish_data)

        if name == "fbx_dir":
            self._open_fbx_dir(path, sg_publish_data)
        if name == "tex_dir":
            self._open_tex_dir(path, sg_publish_data)
        # if name == "publish_dir":
        #     self._open_publish_dir(path, sg_publish_data)
        if name == "copy_publishs":
            self._copy_publishs(path, sg_publish_data)

        if name == "texture_node":
            self._create_texture_node(path, sg_publish_data)

        if name == "udim_texture_node":
            self._create_udim_texture_node(path, sg_publish_data)

        if name == "image_plane":
            self._create_image_plane(path, sg_publish_data)

    ##############################################################################################################
    # helper methods which can be subclassed in custom hooks to fine tune the behaviour of things

    def _create_reference(self, path, sg_publish_data):
        """
        Create a reference with the same settings Maya would use
        if you used the create settings dialog.

        :param path: Path to file.
        :param sg_publish_data: Shotgun data dictionary with all the standard publish fields.
        """
        if not os.path.exists(path):
            raise Exception("File not found on disk - '%s'" % path)

        # make a name space out of entity name + publish name
        # e.g. bunny_upperbody
        namespace = "%s" % (
            sg_publish_data.get("entity").get("name")
        )
        namespace = namespace.replace(" ", "_")

        namespace = self.judge_reference_namespace(namespace, split='__')

        # Now create the reference object in Maya.
        cmds.file(
            path,
            reference=True,
            loadReferenceDepth="all",
            mergeNamespacesOnClash=False,
            namespace=namespace,
        )

    def _open_publish_dir(self, path, sg_publish_data):
        """

        :param path: Path to file.
        :param sg_publish_data: Shotgun data dictionary with all the standard publish fields.
        :return:
        """
        if not os.path.exists(path):
            raise Exception("File not found on disk - '%s'" % path)
        _publish_dir = os.path.dirname(path)

        cmd = 'cmd.exe /C start "Folder" "%s"' % _publish_dir
        exit_code = os.system(cmd)
        if exit_code != 0:
            raise Exception("Failed to launch '%s'!" % cmd)

    def _copy_publishs(self, path, sg_publish_data):
        """
        :param path: Path to file
        :param sg_publish_data: Shotgun data dictionary with all the standard publish fields.
        :return:
        """
        if not os.path.exists(path):
            raise Exception("File not found on disk - '%s'" % path)

        _dir = os.path.dirname(path)
        _sub = _dir.split('publish')[-1]
        _local_dir = self._find_local_dir('Info_Temp/X3/publish')
        _root_local_dir = self._find_local_dir('Info_Temp/X3/publish/{}'.format(_sub))
        self._copy_files(_dir, _local_dir)
        cmd = 'cmd.exe /C start "Folder" "%s"' % _root_local_dir
        exit_code = os.system(cmd)
        if exit_code != 0:
            raise Exception("Failed to launch '%s'!" % cmd)

    def _copy_files(self, scr_dir, _tar_dir):
        u"""

        :param scr_dir:
        :param _tar_dir:
        :return:
        """
        _filelist = self._query_all_file(scr_dir)
        if _filelist:
            for _file in _filelist:
                _sub = os.path.dirname(_file).split('publish')[-1]
                if _sub:
                    _tar = '{}/{}'.format(_tar_dir, _sub)
                else:
                    _tar = _tar_dir
                if _tar and not os.path.exists(_tar):
                    os.makedirs(_tar)
                self._copy_file(_file, _tar)

    def _query_all_file(self, dir_path=''):
        file_list = []
        try:
            for current_dir, sub_dirs, files in os.walk(dir_path):
                for file_name in files:
                    current_dir = current_dir.replace('/', '\\')
                    if '\\back' not in current_dir:
                        temp_file = os.path.join(current_dir, file_name)
                        file_list.append(temp_file)
            return file_list
        except:
            return []

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

    def _replace_reference(self, path, sg_publish_data):
        """
        Replace reference with the same settings Maya would use
        if you used the create settings dialog.

        :param path: Path to file.
        :param sg_publish_data: Shotgun data dictionary with all the standard publish fields.
        """

        if not os.path.exists(path):
            raise Exception("File not found on disk - '%s'" % path)

        reference_info_switch = {}
        reference_info = self.get_reference_info(fromSelect=True)
        # self._import_parent_ref(reference_info)
        namespace = "%s" % (
            sg_publish_data.get("entity").get("name")
        )
        namespace = namespace.replace(" ", "_")

        namespace = self.judge_reference_namespace(namespace, split='__')

        _parent_refinfo = self._get_parent_ref(reference_info)
        if not _parent_refinfo:
            if reference_info:
                for refRN in reference_info:
                    ns = reference_info[refRN][0]
                    ref_path = reference_info[refRN][1]
                    refPath = path
                    # print('new_refPath==>', new_refPath)
                    if ref_path != refPath:
                        reference_info_switch[refRN] = [ns, refPath]
            if reference_info_switch:
                self._replace_ref(reference_info_switch, namespace)
        else:
            self._replace_parent_ref(_parent_refinfo, path, namespace)

    def _replace_parent_ref(self, _parent_refinfo, refpath, namespace):
        self.plugin_load(['atomImportExport'])

        _dict = self.export_parent_anim(_parent_refinfo)
        if not _dict:
            raise Exception("The animation curve was not exported successfully")
        try:
            self._remove_ref(_parent_refinfo)
        except:
            raise Exception("Reference was not remove successfully |{}".format(_parent_refinfo))

        for k, v in _dict.items():
            self._remove_ns(k)
            try:
                self._creat_ref(k, refpath)
            except:
                raise Exception("Reference was not create successfully")
            if v:
                for _file, _ctr in v.items():
                    try:
                        self._import_par_anim(k, _file, _ctr)
                    except:
                        pass
            try:
                namespace = self.judge_reference_namespace(namespace, split='__')
                self._rename_namespace(k, namespace)
            except:
                raise Exception("Namespace was not rename successfully")

    def _remove_ns(self, ns):
        ns = ns.split(':')[-1]
        _nsobjs = []
        try:
            _nsobjs = cmds.namespaceInfo(ns, listNamespace=True)
        except:
            pass
        nslist = cmds.namespaceInfo(listNamespace=True, listOnlyNamespaces=True)
        if ns in nslist:
            if _nsobjs:
                try:
                    cmds.delete(_nsobjs)
                except:
                    pass
            try:
                cmds.namespace(rm=ns)
            except:
                pass

    def _replace_ref(self, reference_info_switch, namespace):
        for k, v in reference_info_switch.items():

            if v and len(v) > 1 and v[-1]:
                cmds.file(v[-1], loadReference=k)
                ns = cmds.referenceQuery(k, namespace=1)
                if v[0] != namespace:
                    try:
                        cmds.namespace(ren=[ns, namespace])
                    except:
                        pass
                cmds.select(k)

    def _rename_namespace(self, srcns, targens):
        if srcns != targens:
            if srcns and ':' in srcns and srcns.split(':')[0] == '':
                srcns = srcns.split(':')[-1]
            cmds.namespace(ren=[srcns, targens])
            # try:
            #     cmds.namespace(ren=[srcns, targens])
            # except:
            #     pass

    def _get_parent_ref(self, reference_info):
        _dict = {}
        if reference_info:
            for k, v in reference_info.items():
                pr = cmds.referenceQuery(v[-1], referenceNode=True, parent=True)
                ch = cmds.referenceQuery(v[-1], referenceNode=True, ch=True)
                if pr or ch:
                    _tprn = cmds.referenceQuery(v[-1], referenceNode=True, tr=True)
                    if _tprn:
                        _tp_ns = cmds.referenceQuery(_tprn, namespace=1)
                        _tp_path = cmds.referenceQuery(_tprn, filename=True)
                        if '{' in _tp_path:
                            _tp_path = _tp_path.split('{')[0]
                    _dict[_tprn] = [_tp_ns, _tp_path]
        return _dict

    def _select_refrn_refinfo(self, refrn):
        _dict = {}
        if refrn:
            refPath = cmds.referenceQuery(refrn, filename=True)
            if refPath:
                if '{' in refPath:
                    refPath = refPath.split('{')[0]
            ns = cmds.referenceQuery(refrn, namespace=1)
            _dict[refrn] = [ns, refPath]
        return _dict

    def _creat_ref(self, ns, refile):
        ns = ns.split(':')[-1]
        try:
            cmds.file(refile, reference=True, loadReferenceDepth="all", mergeNamespacesOnClash=False, namespace=ns)
        except:
            pass

    def _import_par_anim(self, ns, _animfile, _objlist):
        # _objlist = self._get_ctrls(ns)
        _objs = self._get_exist_objs(_objlist)

        cmds.select(_objs)

        try:
            cmds.file(_animfile, i=1, pr=1, importTimeRange='combine', mergeNamespacesOnClash=0, namespace=ns,
                      options="targetTime=3;option=scaleReplace;match=hierarchy;;selected=selectedOnly;search=;replace=;prefix=;suffix=;",
                      type='atomImport', ignoreVersion=1, ra=1)
        except:
            pass

    def _get_exist_objs(self, _objlist):
        _objs = []
        if _objlist:
            for _obj in _objlist:
                if cmds.ls(_obj) and _obj not in _objs:
                    _objs.extend([_obj])
        return _objs

    def _remove_ref(self, refinfo):
        if refinfo:
            for k, v in refinfo.items():
                cmds.file(rfn=k, removeReference=1)

    def export_parent_anim(self, refinfo):
        _dict = {}
        if refinfo:
            for k, v in refinfo.items():
                _exr_dict = {}

                if v and len(v) > 1:
                    _export_file = self._get_atomfile(k)
                    _ctrl_list = self._get_ctrls(v[0])
                    if _ctrl_list:
                        for _ctrl in _ctrl_list:
                            _file = self._get_export_file(_export_file, _ctrl)
                            if _file and os.path.exists(_file):
                                try:
                                    # os.chmod(_file, 0777)
                                    os.remove(_file)
                                except:
                                    pass
                            # _ctrls = self._get_ctrls_c(_ctrl)

                            # self._export_anim([_ctrl], _file)
                            _ctrls = self._get_c_ctrls(_ctrl)
                            self._export_anim_select(_ctrls, _file)
                            _exr_dict[_file] = _ctrls
                    if _exr_dict:
                        _dict[v[0]] = _exr_dict

        return _dict

    def _get_c_ctrls(self, _ctrl):
        _ctrls = []
        _ctr_all = []
        if _ctrl and cmds.ls(_ctrl):
            _ctrls.extend([_ctrl])
            _trs = cmds.listRelatives(_ctrl, ad=1, type='transform', f=1)
            if _trs:
                for _tr in _trs:
                    _shapes = cmds.listRelatives(_tr, f=1, s=1)
                    if _shapes:
                        for _shape in _shapes:
                            if cmds.nodeType(_shape) in ['nurbsCurve', 'nurbsSurface']:
                                _ctrls.extend([_tr])

        if _ctrls:
            _ctr_all.extend(_ctrls)
            for _ct in _ctrls:
                _p = cmds.listRelatives(_ct, p=1, type='transform', f=1)
                if _p and not cmds.listRelatives(_p[0], s=1, f=1):
                    _ctr_all.extend([_p[0]])
        if _ctr_all:
            _ctr_all = list(set(_ctr_all))
        return _ctr_all

    def _export_anim_select(self, objlist, exportfile, opt=''):
        try:
            cmds.select(objlist)
            if not opt:
                opt = "precision=8;statics=1;baked=1;sdk=1;constraint=1;animLayers=1;selected=selectedOnly;whichRange=1;hierarchy=none;controlPoints=1;useChannelBox=2;options=keys;"
            cmds.file(exportfile, f=1, options=opt, typ="atomExport", es=1)
            return exportfile
        except:
            raise Exception("The animation curve was not exported successfully\n[{};{}]".format(objlist, exportfile))

    def _get_export_file(self, _export_file, _ctrl):
        if _export_file and _ctrl:
            _path, _file = os.path.split(_export_file)
            _base, _exr = os.path.splitext(_file)
            _short = _ctrl.split('|')[-1].split(':')[-1]
            return '{}/{}__{}{}'.format(_path, _base, _short, _exr)

    def _import_parent_ref(self, reference_info):
        if reference_info:
            for k, v in reference_info.items():
                _parent_refrn = cmds.referenceQuery(v[-1], referenceNode=True, parent=True)
                if _parent_refrn:
                    refPath = cmds.referenceQuery(_parent_refrn, filename=True)
                    if refPath:
                        if '{' in refPath:
                            refPath = refPath.split('{')[0]
                        try:
                            cmds.file(refPath, ir=1)
                        except:
                            pass

    def _export_anim(self, objlist, exportfile, opt=''):
        try:
            cmds.select(objlist)
            if not opt:
                opt = "precision=8;statics=1;baked=1;sdk=1;constraint=1;animLayers=1;selected=selectedOnly;whichRange=1;hierarchy=none;controlPoints=1;useChannelBox=1;options=keys;copyKeyCmd=-animation objects -option keys -hierarchy none -controlPoints 1 "
            cmds.file(exportfile, f=1, options=opt, typ="atomExport", es=1)
            return exportfile
        except:
            raise Exception("The animation curve was not exported successfully\n[{};{}]".format(objlist, exportfile))

    def _get_atomfile(self, ns):
        if ':' in ns:
            ns = ns.replace(':', '_')
        if ns[0] == '_':
            ns = ns.strip('_')
        _dir = self.get_localtemppath('atom')
        if not os.path.exists(_dir):
            os.makedirs(_dir)
        return '{}/{}.atom'.format(_dir, ns)

    def get_localtemppath(self, add_path):
        if os.path.exists('D:\\'):
            localInfoPath = 'D:/temp_info/' + add_path
        elif os.path.exists('E:\\'):
            localInfoPath = 'E:/temp_info/' + add_path
        elif os.path.exists('F:\\'):
            localInfoPath = 'F:/temp_info/' + add_path
        elif os.path.exists('C:\\'):
            localInfoPath = 'C:/temp_info/' + add_path
        else:
            raise Exception(u'no locatpath')
        return localInfoPath

    def _get_ctrls(self, ns):
        _root_grps = self._get_roots(ns)
        _ctrls = []
        if _root_grps:
            for _grp in _root_grps:
                _objs = cmds.listRelatives(_grp, c=1, f=1)
                if _objs:
                    for _obj in _objs:
                        if self._judge_ctrl(_obj) == True:
                            _ctrls.extend([_obj])
        if _ctrls:
            return list(set(_ctrls))

        # _main = '{}:Main'.format(ns)
        # if _main and cmds.ls(_main):
        #     _ctrls.extend(cmds.ls(_main, l=1))

    def _judge_ctrl(self, _obj):
        _result = False
        if _obj and cmds.ls(_obj):
            shape = cmds.listRelatives(_obj, s=1, type='nurbsCurve')
            if shape:
                _result = True
            _ctrls = cmds.listRelatives(_obj, ad=1, type='nurbsCurve')
            if _ctrls:
                _result = True

        return _result

    def _get_roots(self, ns):
        import maya.cmds as cmds
        transformlist = cmds.ls('{}:*'.format(ns), transforms=True, long=True)
        rootlist = []
        if transformlist:
            for tr in transformlist:
                _inf = tr.split('|')
                if _inf and len(_inf) <= 2 and tr not in rootlist and not cmds.listRelatives(tr, s=1):
                    rootlist.append(tr)
        return rootlist

    def plugin_load(self, pluginlist):
        if pluginlist:
            for plug in pluginlist:
                load = cmds.pluginInfo(plug, loaded=1, q=1)
                if load != True:
                    cmds.loadPlugin(plug, qt=1)
            return True

    def get_reference_info(self, fromSelect=1):
        result = {}
        if fromSelect:
            selObjs = cmds.ls(sl=1, l=1)
            # print('selObjs==>', selObjs)
            if selObjs:
                for obj in selObjs:
                    refRN = ''
                    try:
                        refRN = cmds.referenceQuery(obj, referenceNode=1)
                    except:
                        pass
                    # print('refRN==>', refRN)
                    if refRN:
                        try:
                            ns = cmds.referenceQuery(refRN, namespace=1)
                        except:
                            ns = ''
                        # print('ns==>', ns)
                        refPath = cmds.referenceQuery(refRN, filename=True)
                        if '{' in refPath:
                            refPath = refPath.split('{')[0]
                        result[refRN] = [ns, refPath]
        else:
            refs = cmds.file(q=1, r=1)
            if refs:
                for ref in refs:
                    refRN = cmds.referenceQuery(ref, referenceNode=1)
                    refPath = ref
                    ns = cmds.file(refPath, namespace=1, q=1)
                    if '{' in refPath:
                        refPath = refPath.split('{')[0]
                    result[refRN] = [ns, refPath]

        return result

    def reference_info_dict(self, load=True):
        refs = cmds.file(q=1, r=1)
        result = {}
        if not refs:
            pass

        for ref in refs:
            refRN = cmds.referenceQuery(ref, referenceNode=1)
            _isload = cmds.referenceQuery(refRN, isLoaded=1)
            if (_isload and load == 1) or load == 0:
                refPath = ref
                ns = cmds.file(refPath, namespace=1, q=1)
                if '{' in refPath:
                    refPath = refPath.split('{')[0]
                if os.path.exists(refPath):
                    result[ns] = [refRN, refPath]
        return result

    def _import_reference(self, reffiles):
        if reffiles:
            for _reffile in reffiles:
                try:
                    cmds.file(_reffile, ir=1)
                except:
                    pass

    def judge_reference_namespace(self, namespace, split='_'):
        namespacelist = self.reference_info_dict().keys()
        if namespace not in namespacelist:
            return namespace
        if namespace in namespacelist:
            while namespace in namespacelist:
                if split not in namespace:
                    namespace = u"{}{}01".format(namespace, split)
                else:
                    namespace = u"{}{}0{}".format(namespace.split(split)[0], split, int(namespace.split(split)[-1]) + 1)
                if namespace not in namespacelist:
                    return namespace

    def _do_import(self, path, sg_publish_data):
        """
        Create a reference with the same settings Maya would use
        if you used the create settings dialog.

        :param path: Path to file.
        :param sg_publish_data: Shotgun data dictionary with all the standard publish fields.
        """
        if not os.path.exists(path):
            raise Exception("File not found on disk - '%s'" % path)

        # make a name space out of entity name + publish name
        # e.g. bunny_upperbody
        namespace = "%s %s" % (
            sg_publish_data.get("entity").get("name"),
            sg_publish_data.get("name"),
        )
        namespace = namespace.replace(" ", "_")

        # perform a more or less standard maya import, putting all nodes brought in into a specific namespace
        cmds.file(
            path,
            i=True,
            renameAll=True,
            namespace=namespace,
            loadReferenceDepth="all",
            preserveReferences=True,
        )

    def _do_reference_nonamespace(self, path, sg_publish_data):
        """
        Create a reference with the same settings Maya would use
        if you used the create settings dialog.
        :param path: Path to file.
        :param sg_publish_data: Shotgun data dictionary with all the standard publish fields.
        """
        cmds.file(
            path,
            reference=True,
            loadReferenceDepth="all",
            mergeNamespacesOnClash=False,
            namespace=":",
        )

    def _do_import_nonameapce(self, path, sg_publish_data):
        """
        Import with the same settings Maya would use
        if you used the create settings dialog.

        :param path: Path to file.
        :param sg_publish_data: Shotgun data dictionary with all the standard publish fields.
        """
        if not os.path.exists(path):
            raise Exception("File not found on disk - '%s'" % path)

        # make a name space out of entity name + publish name
        # e.g. bunny_upperbody

        # perform a more or less standard maya import, putting all nodes brought in into a specific namespace
        cmds.file(
            path,
            i=True,
            renameAll=True,
            namespace=":",
            loadReferenceDepth="all",
            preserveReferences=True,
        )

    def _do_open(self, path, sg_publish_data):
        """
        Open the same settings Maya would use
        if you used the create settings dialog.

        :param path: Path to file.
        :param sg_publish_data: Shotgun data dictionary with all the standard publish fields.
        """
        inf = cmds.confirmDialog(title=u'Waring',
                                 message=u'Please confirm if you want to open the file {}'.format(path),
                                 button=['Yes', 'No'], defaultButton='Yes')
        if inf == 'No':
            return
        if not os.path.exists(path):
            raise Exception("File not found on disk - '%s'" % path)

        # make a name space out of entity name + publish name
        # e.g. bunny_upperbody

        # perform a more or less standard maya import, putting all nodes brought in into a specific namespace
        cmds.file(
            path,
            o=True,
            options='v=0',
            f=1,
            ignoreVersion=1

        )

    def _open_fbx_dir(self, path, sg_publish_data):
        """
        Create a reference with the same settings Maya would use
        if you used the create settings dialog.

        :param path: Path to file.
        :param sg_publish_data: Shotgun data dictionary with all the standard publish fields.
        """
        _fbx_dir = '{}\\data\\fbx'.format(os.path.dirname(path))

        if not os.path.exists(_fbx_dir):
            raise Exception("File not found on disk - '%s'" % _fbx_dir)

        cmd = 'cmd.exe /C start "Folder" "%s"' % _fbx_dir
        exit_code = os.system(cmd)
        if exit_code != 0:
            raise Exception("Failed to launch '%s'!" % cmd)

    def _open_tex_dir(self, path, sg_publish_data):
        """
        Create a tex dir the same settings Maya would use
        if you used the create settings dialog.

        :param path: Path to file.
        :param sg_publish_data: Shotgun data dictionary with all the standard publish fields.
        """
        _tex_dir = '{}\\data\\tex'.format(os.path.dirname(path))

        if not os.path.exists(_tex_dir):
            raise Exception("File not found on disk - '%s'" % _tex_dir)

        cmd = 'cmd.exe /C start "Folder" "%s"' % _tex_dir
        exit_code = os.system(cmd)
        if exit_code != 0:
            raise Exception("Failed to launch '%s'!" % cmd)

    def _create_texture_node(self, path, sg_publish_data):
        """
        Create a file texture node for a texture

        :param path:             Path to file.
        :param sg_publish_data:  Shotgun data dictionary with all the standard publish fields.
        :returns:                The newly created file node
        """
        file_node = cmds.shadingNode("file", asTexture=True)
        cmds.setAttr("%s.fileTextureName" % file_node, path, type="string")
        return file_node

    def _create_udim_texture_node(self, path, sg_publish_data):
        """
        Create a file texture node for a UDIM (Mari) texture

        :param path:             Path to file.
        :param sg_publish_data:  Shotgun data dictionary with all the standard publish fields.
        :returns:                The newly created file node
        """
        # create the normal file node:
        file_node = self._create_texture_node(path, sg_publish_data)
        if file_node:
            # path is a UDIM sequence so set the uv tiling mode to 3 ('UDIM (Mari)')
            cmds.setAttr("%s.uvTilingMode" % file_node, 3)
            # and generate a preview:
            mel.eval("generateUvTilePreview %s" % file_node)
        return file_node

    def _create_image_plane(self, path, sg_publish_data):
        """
        Create a file texture node for a UDIM (Mari) texture

        :param path: Path to file.
        :param sg_publish_data: Shotgun data dictionary with all the standard
            publish fields.
        :returns: The newly created file node
        """

        app = self.parent
        has_frame_spec = False

        # replace any %0#d format string with a glob character. then just find
        # an existing frame to use. example %04d => *
        frame_pattern = re.compile("(%0\dd)")
        frame_match = re.search(frame_pattern, path)
        if frame_match:
            has_frame_spec = True
            frame_spec = frame_match.group(1)
            glob_path = path.replace(frame_spec, "*")
            frame_files = glob.glob(glob_path)
            if frame_files:
                path = frame_files[0]
            else:
                app.logger.error(
                    "Could not find file on disk for published file path %s" % (path,)
                )
                return

        # create an image plane for the supplied path, visible in all views
        (img_plane, img_plane_shape) = cmds.imagePlane(
            fileName=path, showInAllViews=True
        )
        app.logger.debug("Created image plane %s with path %s" % (img_plane, path))

        if has_frame_spec:
            # setting the frame extension flag will create an expression to use
            # the current frame.
            cmds.setAttr("%s.useFrameExtension" % (img_plane_shape,), 1)

    def _get_maya_version(self):
        """
        Determine and return the Maya version as an integer

        :returns:    The Maya major version
        """
        if not hasattr(self, "_maya_major_version"):
            self._maya_major_version = 0
            # get the maya version string:
            maya_ver = cmds.about(version=True)
            # handle a couple of different formats: 'Maya XXXX' & 'XXXX':
            if maya_ver.startswith("Maya "):
                maya_ver = maya_ver[5:]
            # strip of any extra stuff including decimals:
            major_version_number_str = maya_ver.split(" ")[0].split(".")[0]
            if major_version_number_str and major_version_number_str.isdigit():
                self._maya_major_version = int(major_version_number_str)
        return self._maya_major_version
