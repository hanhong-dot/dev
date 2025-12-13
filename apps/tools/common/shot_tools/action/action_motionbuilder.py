# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       : action_motionbuilder
# Describe   : 说明描述
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2023/3/21__14:27
# -------------------------------------------------------
import os

from pyfbsdk import FBApplication
from pyfbsdk import FBFbxOptions
from pyfbsdk import FBElementAction
from pyfbsdk import FBStringList
from pyfbsdk import FBSystem
from pyfbsdk import FBMessageBox


def action(infos):
    """
    Import contents of the given file into the scene.

    :param path: Path to file.
    :param sg_publish_data: Shotgun data dictionary with all the standard publish fields.
    """
    if not infos:
        FBMessageBox("error", "not asset info,please check" "OK")
        return
    error = []
    importfiles=[]
    for i in range(len(infos)):

        _path = infos[i]["path"]
        _entityname = infos[i]["name"]

        import_file(_path , _entityname)
        importfiles.append(_path)

        # except:
        #     _entityname = infos[i]["entity"]
        #     _taskname = infos[i]["task_name"]
        #     error.append('{} {}'.format(_entityname, _taskname))


def judge_namespace(namespace, split='_'):
    namespacelist = _getnamespacelist()
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


def import_file(path, entity_name):
    namespace = '{}'.format(entity_name)
    namespace = namespace.replace(" ", "_")
    namespace = judge_namespace(namespace, split='__')
    path='{}'.format(path)

    fbxLoadOptions = FBFbxOptions(True, path)
    fbxLoadOptions.NamespaceList = namespace
    fbxLoadOptions.SetAll(FBElementAction.kFBElementActionMerge, True)
    for takeIndex in range(0, fbxLoadOptions.GetTakeCount()):
        fbxLoadOptions.SetTakeSelect(takeIndex, 0)
    app = FBApplication()
    app.FileMerge(path, False, fbxLoadOptions)


def _getnamespacelist():
    """

    """
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



# infos=[{'project_name': 'X3', 'name': u'YG001S',
#   'entity': {'type': 'Shot', 'id': 2910, 'name': 'CutScene_ML_C10S1_S01_P01'}, 'asset_state': u'rev',
#   'task_name': u'rbf', 'path': u'M:\\projects\\x3\\publish\\assets\\role\\YG001S\\rbf\\maya\\data\\fbx\\YG001S_MB.fbx',
#   'asset_type': u'role'}]
# action(infos)
