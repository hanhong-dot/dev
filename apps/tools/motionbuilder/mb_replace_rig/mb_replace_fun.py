# -*- coding: utf-8 -*-
# author: linhuan
# file: mb_replace_fun.py
# time: 2025/10/15 15:41
# description:
import os
import sys
from pyfbsdk import *
import stat
import apps.tools.motionbuilder.mb_replace_rig.fbx_process as fbx_process
import time


def batch_replace_character_from_dir(batch_process_dir, rig_name, new_character_file, log_handle=None):
    if not os.path.exists(batch_process_dir):
        if log_handle:
            log_handle.error(u'批量处理目录不存在: {}'.format(batch_process_dir))
        return False, u'批量处理目录不存在: {}'.format(batch_process_dir)

    # check_ok, check_result = check_fbx_file(new_character_file, rig_name)
    # if not check_ok:
    #     if log_handle:
    #         log_handle.error(check_result)
    #     return False, check_result
    # new_file_rig_name, mod_grp_list = check_result

    batch_process_files = get_fbx_files_in_dir(batch_process_dir)
    log_handle.info("批量处理目录下FBX文件数量: {}".format(len(batch_process_files)))
    if not batch_process_files:
        if log_handle:
            log_handle.error(u'批量处理目录下没有FBX文件: {}'.format(batch_process_dir))
        return False, u'批量处理目录下没有FBX文件: {}'.format(batch_process_dir)
    return batch_replace_character(batch_process_files, rig_name, new_character_file, log_handle)


def check_fbx_file(fbx_file, rig_name):
    if not os.path.exists(fbx_file):
        return False, u'FBX文件不存在: {}'.format(fbx_file)
    ok, result = fbx_process.get_fbx_data(fbx_file, rig_name)
    if not ok:
        return False, result
    return True, result


def get_fbx_files_in_dir(batch_process_dir):
    fbx_files = []
    if not os.path.exists(batch_process_dir):
        return fbx_files
    files = os.listdir(batch_process_dir)
    for file in files:
        if file.endswith('.fbx') or file.endswith('.FBX'):
            fbx_file = os.path.join(batch_process_dir, file)
            fbx_files.append(fbx_file)
    return fbx_files


def batch_replace_character(batch_process_files, rig_name, new_character_file, log_handle=None):
    if not batch_process_files:
        return False, u'没有需要处理的文件'
    if not rig_name:
        return False, u'没有指定需要替换的角色名称'
    if not new_character_file or not os.path.exists(new_character_file):
        return False, u'替换角色文件不存在: {}'.format(new_character_file)
    error_list = []

    for mb_file in batch_process_files:
        try:
            mb_file_new()
        except Exception as e:
            pass
        log_handle.info("开始处理文件: {}".format(mb_file))
        try:
            change_file_permission(mb_file)
        except Exception as e:
            if log_handle:
                log_handle.error("文件权限修改失败: {}, 错误信息: {}".format(mb_file, str(e)))

        ok, result = open_mbx_file(mb_file)
        if not ok:
            error_list.append(mb_file)
            if log_handle:
                log_handle.error(result)
            continue
        rig_node = get_node_by_node_name(str(rig_name))
        if not rig_node:
            error_list.append(mb_file)
            if log_handle:
                log_handle.error("文件: {}, 未找到角色节点: {}".format(mb_file, rig_name))
            mb_file_new()
            continue
        start_frame = FBSystem().CurrentTake.LocalTimeSpan.GetStart().GetFrame()
        end_frame = FBSystem().CurrentTake.LocalTimeSpan.GetStop().GetFrame()
        ok, result = replace_character(rig_node, new_character_file, start_frame, end_frame, log_handle)
        if not ok:
            error_list.append(mb_file)
            if log_handle:
                log_handle.error("文件: {}, 替换失败: {}".format(mb_file, result))
            mb_file_new()
            continue
        ok, result = save_mbx_file(mb_file)
        if not ok:
            error_list.append(mb_file)
            if log_handle:
                log_handle.error(result)
            log_handle.info("文件: {}, 保存失败".format(mb_file))
            mb_file_new()
            continue
        mb_file_new()
        if log_handle:
            log_handle.info("文件: {}, 角色替换成功".format(mb_file))
    if error_list:
        error_list = list(set(error_list))
        if len(error_list) == len(batch_process_files):
            return False, u'所有文件替换失败:\n{}'.format('\n'.join(error_list))
        else:
            return False, u'部分文件替换失败:\n{}'.format('\n'.join(error_list))
    else:
        return True, u'批量替换角色完成'


def mb_file_new():
    app = FBApplication()
    app.FileNew()
    return True, u'新建文件成功'


def change_file_permission(filepath):
    # type: (str) -> None
    current_permissions = os.stat(filepath).st_mode
    new_permissions = current_permissions | stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH
    chmod(filepath, new_permissions)


def chmod(fp, mode):
    os.chmod(long_path(fp), mode)


def long_path(path):
    if path.startswith('\\\\?\\'):
        return os.path.normpath(path).replace('\\', '/').replace('/', '\\')
    elif path.startswith('//?/'):
        return os.path.normpath(path).replace('\\', '/').replace('/', '\\')
    else:
        return ('\\\\?\\' + os.path.normpath(path)).replace('\\', '/').replace('/', '\\')


def save_mbx_file(mbx_file):
    if isinstance(mbx_file, unicode):
        mbx_file = mbx_file.encode('utf8')
    app = FBApplication()
    app.FileSave(mbx_file)
    return True, mbx_file


def open_mbx_file(mbx_file):
    if isinstance(mbx_file, unicode):
        mbx_file = mbx_file.encode('utf8')
    if not os.path.exists(mbx_file):
        return False, u'文件不存在: {}'.format(mbx_file)
    app = FBApplication()
    app.FileOpen(mbx_file)
    return True, mbx_file


def replace_character(rig_node, new_character_file, start_frame, end_frame, log_handle=None):
    character_list = get_all_characters()
    if not character_list:
        return False, u'场景中没有Hik角色'
    rig_node_long_name = rig_node.LongName
    rig_node_name = rig_node.Name

    target_character = get_character_by_rig(rig_node, character_list)
    if not target_character:
        return False, u'未找到相关character,请检查: {}'.format(rig_node_long_name)
    if ':' in target_character.LongName:
        old_name_space = target_character.LongName.split(':')[0]
    else:
        old_name_space = None

    if log_handle:
        log_handle.info("开始合并角色文件: {}".format(new_character_file))
    name_space = os.path.basename(str(new_character_file)).split('.')[0].split('_MB')[0]
    name_space_new = name_space
    __list = []
    for character in character_list:
        if character.LongName.startswith(name_space + ':'):
            ns = character.LongName.split(':')[0]
            if ns == name_space_new:
                __list.append(ns)
    if not __list:
        name_space_new = name_space
    else:
        index = 1
        while True:
            name_space_new = "{}_{}".format(name_space, index)
            if name_space_new not in __list:
                break
            index += 1
        name_space_new = '{}_{}'.format(name_space, index)

    ok, result = merge_fbx_file(str(new_character_file), namespace=name_space_new)
    set_current_take_time_range(start_frame, end_frame)
    if not ok:
        if log_handle:
            log_handle.error(result)
        return False, result
    if log_handle:
        log_handle.info("合并角色文件完成: {}".format(new_character_file))

    new_character_list = get_all_characters()
    if log_handle:
        log_handle.info("合并后场景中角色数量: {}".format(len(new_character_list)))

    new_character = get_character_by_namespace(name_space_new, new_character_list)
    new_ref_ctrls = get_character_all_ref_ctrls(new_character)
    if log_handle:
        log_handle.info("new_character: {}".format(new_character.Name if new_character else None))
    if not new_character:
        if log_handle:
            log_handle.error('未找到新角色，请检查角色文件: {}'.format(new_character_file))
        return False, u'未找到新角色，请检查角色文件: {}'.format(new_character_file)

    if log_handle:
        log_handle.info("找到新角色: {}".format(new_character.LongName))
        log_handle.info('name_space: {}'.format(name_space))
    set_current_frame(start_frame)

    old_constraints_data = get_handle_constraints_data(target_character)
    ref_ctrls = get_character_all_ref_ctrls(target_character)
    set_current_character(new_character)
    # 设置Source Control
    # new_character.InputType = FBCharacterInputType.kFBCharacterInputCharacter
    new_character.ConnectControlRig(target_character.GetCurrentControlSet(), True, True)
    new_character.Active = True
    props = new_character.PropertyList.Find('Match Source')
    props.Data = True
    FBSystem().Scene.Evaluate()
    set_current_character(new_character)

    bake_all()
    bake_to_skeleton(character=new_character)
    bake_to_control_rig(character=new_character)
    set_current_frame(start_frame)
    set_current_character(new_character)

    set_new_character_contraints(new_character, old_constraints_data)
    bake_to_skeleton(character=new_character)
    set_current_character(None)

    # 删除旧的角色
    if old_name_space:
        FBDeleteObjectsByName(None, str(old_name_space), None)
    else:
        # delete_character_and_related(target_character)
        delect_objs = []
        delect_objs.append(target_character)

        delete_children_recursive(rig_node)

        if ref_ctrls:
            delect_objs.extend(ref_ctrls)
        if delect_objs:
            delect_objs = list(set(delect_objs))
            for obj in delect_objs:
                try:
                    obj.FBDelete()
                except:
                    pass

    # new_ref_ctrls = all_ref_ctrls_by_ctrl_rig(new_contral_rig)
    for ctrl in new_ref_ctrls:
        try:
            ctrl.FBDelete()
        except:
            pass




    bake_all()
    set_current_frame(start_frame)
    rig_node = get_node_by_long_name(rig_node_long_name)
    if rig_node:
        count=0
        while  count<=100:
            all_ch_nodes=get_all_children(rig_node)

            if not all_ch_nodes:
                break
            delete_nodes(all_ch_nodes)
            count+=1

    # new_ref_ctrls = all_ref_ctrls_by_ctrl_rig(new_contral_rig)
    # for ctrl in new_ref_ctrls:
    #     try:
    #         ctrl.FBDelete()
    #     except:
    #         pass
    # set_current_character(new_character)

    return True, u'角色替换成功'



def delete_nodes(nodes):
    for node in nodes:
        node.FBDelete()


def delete_children_recursive(model):
    for child in list(model.Children):
        delete_children_recursive(child)
        child.FBDelete()


def has_namespace(name):
    return ":" in name


def get_character_related_models(character):
    related = set()

    for slot in character.PropertyList:
        prop = slot
        if isinstance(prop, FBProperty):
            if prop.GetPropertyTypeName() == "object":
                obj = prop.Value
                if isinstance(obj, FBModel) and obj not in related:
                    related.add(obj)

    queue = list(related)
    while queue:
        m = queue.pop()
        # 向上
        if m.Parent and isinstance(m.Parent, FBModel) and m.Parent not in related:
            related.add(m.Parent)
            queue.append(m.Parent)
        # 向下
        for c in m.Children:
            if isinstance(c, FBModel) and c not in related:
                related.add(c)
                queue.append(c)

    cs = character.GetCurrentControlSet()
    if cs:
        for ctrl in cs.Nodes:
            model = ctrl.Model
            if model:
                related.add(model)

    return list(related)


def delete_character_and_related(character):
    # 收集相关节点
    related = get_character_related_models(character)

    # 删除 Character 本体
    FBSystem().Scene.Characters.remove(character)

    # 删除关联模型
    for m in related:
        try:
            m.FBDelete()
        except Exception as e:
            print("Delete failed:", m.Name, e)


def set_current_take_time_range(start_frame, end_frame):
    take = FBSystem().CurrentTake
    take.LocalTimeSpan = FBTimeSpan(FBTime(0, 0, 0, start_frame, 0), FBTime(0, 0, 0, end_frame, 0))


def get_fk_effectors(character):
    fkEffectors = []
    if character:
        for nodeId in FBBodyNodeId.values.values():
            if nodeId not in [FBBodyNodeId.kFBInvalidNodeId, FBBodyNodeId.kFBLastNodeId]:
                effector = character.GetCtrlRigModel(nodeId)
                if effector:
                    fkEffectors.append(effector)
    return fkEffectors


def get_ik_effectors(character):
    ikEffectors = []
    if character:
        ctrlRig = select_control_rig_from_character(character)
        if ctrlRig:
            for nodeId in FBEffectorId.values.values():
                if nodeId not in [FBEffectorId.kFBInvalidEffectorId, FBEffectorId.kFBLastEffectorId]:
                    effector = ctrlRig.GetIKEffectorModel(nodeId, 0)
                    if effector:
                        ikEffectors.append(effector)
            if ikEffectors == []:
                ikEffectors = None
    return ikEffectors


def get_world_transform(node):
    global_matrix = FBMatrix()

    node.GetMatrix(global_matrix, FBModelTransformationType.kModelTransformation)

    translation = [global_matrix[12], global_matrix[13], global_matrix[14]]

    return translation


def set_current_frame(target_frame):
    u"""
    设置当前帧为指定帧
    """

    player_control = FBPlayerControl()
    player_control.Goto(FBTime(0, 0, 0, target_frame))
    FBSystem().Scene.Evaluate()


def set_new_character_contraints(new_character, constraints_data):
    if not new_character or not constraints_data:
        return
    for i in range(len(constraints_data)):
        constraint_info = constraints_data[i]
        point_node_name = constraint_info['point_node_name']

        old_point_node = constraint_info['point_node']
        constraints = constraint_info['constraints']

        if not point_node_name or not constraints or not old_point_node:
            continue
        new_point_node = get_node_by_name_character(new_character, point_node_name)
        for constraint, targe_data in constraints:
            constraint.Active = False
            if not constraint:
                continue
            targe = constraint.ReferenceGet(0)
            if not targe:
                continue
            rotation = targe_data['rotation']
            targe.SetVector(FBVector3d(rotation), FBModelTransformationType.kModelRotation)
            FBSystem().Scene.Evaluate()
            new_point_node_tr = get_world_transform(new_point_node)

            dif_pos = targe_data['diff_transition']

            targe_tr = FBVector3d(new_point_node_tr) - FBVector3d(dif_pos)

            targe.SetVector(FBVector3d(targe_tr), FBModelTransformationType.kModelTranslation)

            FBSystem().Scene.Evaluate()

            constraint.ReferenceRemove(1, old_point_node)

            if not new_point_node:
                continue
            constraint.ReferenceAdd(1, new_point_node)
            FBConstraint.Snap(constraint)
            constraint.Active = True


def get_node_world_rotation(node):
    # type: (FBModel) -> FBVector3d
    from lib.mobu.agorithm_fun import Quaternion

    global_matrix = FBMatrix()

    node.GetMatrix(global_matrix, FBModelTransformationType.kModelTransformation)

    quaternion = FBVector4d()
    FBMatrixToQuaternion(quaternion, global_matrix)
    return Quaternion(quaternion).Euler()


def get_handle_constraints_data(character):
    left_hand_point_name = 'HPoint_hand_L'
    right_handle_point_name = 'HPoint_hand_R'
    __point_nodes = []
    __data = []
    if not character:
        return __data
    root = character.GetModel(FBBodyNodeId.kFBHipsNodeId)
    child_nodes = get_all_children(root)
    if not child_nodes:
        return __data
    for node in child_nodes:
        if node.Name == left_hand_point_name or node.Name == right_handle_point_name:
            __point_nodes.append(node)
    if not __point_nodes:
        return __data
    for point_node in __point_nodes:

        constraints = get_node_constraints(point_node)
        if constraints:
            data = {}
            data['point_node_name'] = point_node.Name
            data['point_node'] = point_node
            data['constraints'] = constraints
            if data:
                __data.append(data)
    return __data


def get_node_by_name_character(character, node_name):
    root = character.GetModel(FBBodyNodeId.kFBHipsNodeId)
    child_nodes = get_all_children(root)
    if not child_nodes:
        return None
    for node in child_nodes:
        if node.Name == node_name:
            return node

    return None


def get_node_constraints(node):
    __data = {}
    if not node:
        return __data
    constraints = []
    for c in FBSystem().Scene.Constraints:
        if not c:
            continue
        source = c.ReferenceGet(1)
        if not source:
            continue
        if source == node:
            targe = c.ReferenceGet(0)
            if not targe:
                continue
            targe_data = {}
            source_transition = get_world_transform(source)
            targe_transition = get_world_transform(targe)
            diff_transition = FBVector3d(source_transition) - FBVector3d(targe_transition)
            targe_rotation = get_node_world_rotation(targe)
            targe_scaling = targe.Scaling.Data

            targe_data['diff_transition'] = diff_transition
            targe_data['rotation'] = targe_rotation
            targe_data['scaling'] = targe_scaling

            constraints.append([c, targe_data])
            break
    return constraints


def get_character_by_namespace(namespace, character_list):
    for character in character_list:
        if character.LongName.startswith(namespace + ':'):
            return character
    return None


def rebuild_character_mapping(character, namespace):
    for nodeId in FBBodyNodeId.values.values():
        if nodeId in [FBBodyNodeId.kFBInvalidNodeId, FBBodyNodeId.kFBLastNodeId]:
            continue
        model = character.GetModel(nodeId)
        if not model:
            name = FBBodyNodeIdToString(nodeId)
            new_name = "{namespace}:{name}".format(namespace=namespace, name=name)
            new_model = FBFindModelByName(new_name)
            if new_model:
                character.SetModel(nodeId, new_model)
    FBSystem().Scene.Evaluate()


def clean_mod_list(current_mod_list, new_mod_list):
    if not current_mod_list:
        return
    remove_list = []
    for node in current_mod_list:
        node_name = node.Name
        if node_name not in new_mod_list:
            remove_list.append(node)
            childern_list = get_node_childern_list(node)
            if childern_list:
                remove_list.extend(childern_list)
    if not remove_list:
        return
    remove_list = list(set(remove_list))
    for node in remove_list:
        try:
            node.FBDelete()
        except:
            pass


def get_mod_list(rig_node):
    mod_list = []
    for child in rig_node.Children:
        if child.__class__ == FBModelNull:
            mod_list.append(child)
    return mod_list


def get_node_childern_list(node):
    children = []
    for child in node.Children:
        children.append(child)
    return children


def get_character_by_rig(rig_node, character_list):
    root_m = get_root_m_by_rig_node(rig_node)
    if not character_list:
        return None
    for character in character_list:
        character_root_m = get_root_m_by_character(character)
        if character_root_m.LongName == root_m.LongName:
            return character
    return None


def get_character_by_rig_node(rig_node):
    chidel_nodes = get_all_children(rig_node)
    for node in chidel_nodes:
        if isinstance(node, FBCharacter):
            return node
    return None


def add_namespace_to_character(character, namespace, roots, log_handle=None):
    # scene = FBSystem().Scene
    # scene.NamespaceAdd(namespace)
    __rename_node = []
    if not character.LongName.startswith(namespace + ':'):
        __rename_node.append(character)
    controls = get_character_controls(character)
    if controls:
        for control in controls:
            if not control:
                continue
            control_name = control.LongName
            if not control_name.startswith(namespace + ':'):
                __rename_node.append(control)
    if roots:
        for root_name in roots:
            if not root_name:
                continue
            root = get_node_by_node_name(root_name)
            if not root:
                continue
            root_long_name = root.LongName
            if ':' in root_long_name:
                root_name = root_long_name.split(':')[-1]
            if not root_long_name.startswith(namespace + ':'):
                __rename_node.append(root)
            children_nodes = get_all_children(root)
            if not children_nodes:
                continue
            for child_node in children_nodes:
                if not child_node:
                    continue
                child_name = child_node.LongName
                if not child_name.startswith(namespace + ':'):
                    __rename_node.append(child_node)

    if not __rename_node:
        return
    for node in __rename_node:
        if not node:
            continue
        # node.Selected = True
        # scene.NamespaceSet(namespace, node)
        node_name = node.LongName
        if ':' in node_name:
            node_name = node_name.split(':')[-1]
        new_name = namespace + ':' + node_name
        node.LongName = new_name
    # scene.NamespaceSelectContent(namespace)
    FBSystem().Scene.Evaluate()


def get_node_by_node_name(node_name):
    all_nodes = get_all_nodes_in_scene()
    for node in all_nodes:
        if node.Name.lower() == node_name.lower():
            return node
    return None


def get_node_by_long_name(node_long_name):
    all_nodes = get_all_nodes_in_scene()
    for node in all_nodes:
        if node.LongName.lower() == node_long_name.lower():
            return node
    return None


def get_root_m_by_rig_node(rig_node, root_name='Root_M'):
    children_nodes = get_all_children(rig_node)
    if not children_nodes:
        return None
    for node in children_nodes:
        if node.Name == root_name:
            return node
    return None


def get_root_m_by_character(character):
    return character.GetModel(FBBodyNodeId.kFBHipsNodeId)


def rename_character_ctrls_by_namespace(character, namespace):
    if not character or not namespace:
        return
    controls = get_character_all_ref_ctrls(character)
    if not controls:
        return
    for control in controls:
        if not control:
            continue
        control_name = control.LongName
        if ':' in control_name:
            control_name = control_name.split(':')[-1]

        if not control_name.startswith(namespace + ':'):
            new_name = namespace + ':' + control_name
            try:
                control.LongName = new_name
            except:
                pass


def get_character_roots(character):
    pass


def get_roots_by_namespace(namespace):
    roots = []

    def condition_callback(model):
        if model.Parent is None and model.Name.startswith(namespace + ':'):
            return True
        return False

    get_children(roots, FBSystem().Scene.RootModel, condition_callback)
    return roots


def get_merge_character(before_character_list, after_character_list):
    for character in after_character_list:
        if character not in before_character_list:
            return character
    return None


def remove_namespace(namespace, log_handle=None):
    system = FBSystem()
    scene = system.Scene
    comps = FBComponentList()
    scene.NamespaceGetContentList(comps, namespace)
    for comp in comps:
        try:
            comp.ProcessObjectNamespace(FBNamespaceAction.kFBRemoveAllNamespace, '', '', False)
        except Exception as e:
            if log_handle:
                log_handle.error("Failed to remove namespace from component: {}, error: {}".format(comp.Name, str(e)))
            print("Failed:", comp.Name, e)
    scene.Evaluate()
    scene.NamespaceCleanup()


def delete_objs_by_namespace(namespace):
    scene = FBSystem().Scene
    return scene.NamespaceDelete(namespace)


def apply_data_to_character(character, character_data):
    if not character or not character_data:
        return
    ik_objects = get_ik_objects(character)
    if not ik_objects:
        return
    for obj in ik_objects:
        if not obj:
            continue
        obj_name = obj.FullName
        if obj_name not in character_data:
            continue
        obj_data = character_data[obj_name]
        if not obj_data:
            continue
        for key_info in obj_data:
            key_frame = key_info['key_frame']
            key_value = key_info['key_value']
            obj.Translation.SetAnimated(True)
            obj.Rotation.SetAnimated(True)
            obj.Scaling.SetAnimated(True)
            obj.Translation.KeyAdd(FBTime(key_frame), key_value)
            obj.Rotation.KeyAdd(FBTime(key_frame), key_value)
            obj.Scaling.KeyAdd(FBTime(key_frame), key_value)
    FBSystem().Scene.Evaluate()


def remove_namespace_from_character(character, namespace):
    if not character or not namespace:
        return
    controls = get_character_controls(character)
    if not controls:
        return
    for control in controls:
        if not control:
            continue
        control_name = control.Name

        if control_name.startswith(namespace + ':'):
            new_name = control_name.replace(namespace + ':', '', 1)
            try:
                control.Name = new_name
            except:
                pass
    FBSystem().Scene.Evaluate()


def pre_process(character):
    set_current_character(character)
    bake_all()
    bake_to_skeleton()
    bake_to_control_rig(character=character)


def get_character_data(character, start_frame, end_frame):
    __data = {}
    ik_objs = get_ik_objects(character)

    if not ik_objs:
        return __data
    for obj in ik_objs:
        if not obj:
            continue
        __curves = get_obj_curves(obj)
        if not __curves:
            continue
        __obj_data = []
        for i in range(len(__curves)):
            fcurve = __curves[i]
            keys = fcurve.Keys
            if not keys:
                continue
            key_pairs = get_key_pairs_from_fcurve(keys)
            for key_pair in key_pairs:
                key_frame = key_pair[0].GetFrame()
                key_value = key_pair[1]

                if key_frame < start_frame or key_frame > end_frame:
                    continue
                __obj_data.append({
                    'key_frame': key_frame,
                    'key_value': key_value
                })

        if __obj_data:
            __data[obj.Name] = __obj_data

    return __data


def get_all_characters():
    return FBSystem().Scene.Characters


def get_obj_curves(obj):
    return [node.FCurve for node in select_transition_animation_nodes_by_objs([obj])]


def select_transition_animation_nodes_by_objs(objs):
    # type: (List[FBModel]) -> List[FBAnimationNode]
    transitionNodes = []
    if objs:
        for obj in objs:
            transition_prop = obj.PropertyList.Find("Lcl Translation")
            rotation_prop = obj.PropertyList.Find("Lcl Rotation")
            if not transition_prop:
                transition_prop.SetAnimated(True)
                transition_prop = obj.PropertyList.Find("Lcl Translation")
            if not rotation_prop:
                rotation_prop.SetAnimated(True)
                rotation_prop = obj.PropertyList.Find("Lcl Rotation")
            if transition_prop and transition_prop.GetAnimationNode() and transition_prop.GetAnimationNode().Nodes:
                transitionNodes.extend(transition_prop.GetAnimationNode().Nodes)
            if rotation_prop and rotation_prop.GetAnimationNode() and rotation_prop.GetAnimationNode().Nodes:
                transitionNodes.extend(rotation_prop.GetAnimationNode().Nodes)
    return transitionNodes


def get_key_pairs_from_fcurve(keys):
    keyPairsList = []
    for i in range(len(keys)):
        KeyTime = keys[i].Time
        KeyValue = keys[i].Value
        keyPairsList.append([KeyTime, KeyValue])
    return keyPairsList


def get_current_character():
    return FBApplication().CurrentCharacter


def get_ik_objects(character=None):
    objects = []
    if character == None:
        character = get_current_character()
    ik_objsects = get_ik_effectors(character)
    if ik_objsects:
        objects.extend(ik_objsects)
    return objects


def get_ik_effectors(character=None):
    if not character:
        character = get_current_character()
    ikEffectors = []
    if character:
        ctrlRig = select_control_rig_from_character(character)
        if ctrlRig:
            for nodeId in FBEffectorId.values.values():
                if nodeId not in [FBEffectorId.kFBInvalidEffectorId, FBEffectorId.kFBLastEffectorId]:
                    effector = ctrlRig.GetIKEffectorModel(nodeId, 0)
                    if effector:
                        ikEffectors.append(effector)
            if ikEffectors == []:
                ikEffectors = None
    return ikEffectors


def get_root_list():
    scene_root = get_scene()
    root_list = []
    for child in scene_root.Children:
        root_list.append(child)
    return root_list


def get_scene():
    return FBSystem().Scene.RootModel


def get_root_by_namespace(namespace):
    root_list = get_root_list()
    __list = []
    if not root_list:
        return None
    for root in root_list:
        if root.LongName.startswith(namespace + ':'):
            __list.append(root.Name)
    return __list


def select_control_rig_from_character(character=None):
    if not character:
        character = get_current_character()
    if character:
        ctrlRig = character.PropertyList.Find("ControlSet")
        if len(ctrlRig) != 0:
            ctrlRig = ctrlRig[0]
        else:
            ctrlRig = None
        if ctrlRig:
            return ctrlRig


def get_all_children(root):
    children = []
    for child in root.Children:
        children.append(child)
        children.extend(get_all_children(child))
    return children


def get_all_jonints(root):
    joints = []
    for child in root.Children:
        if isinstance(child, FBModelSkeleton):
            joints.append(child)
        joints.extend(get_all_jonints(child))
    return joints


def get_children(childrenList, Root=FBSystem().Scene.RootModel, condition_callback=None):  # 遍历子物体并存到list里

    for childModel in Root.Children:
        if condition_callback is not None:
            if not condition_callback(childModel):
                continue
        childrenList.append(childModel)
        get_children(childrenList, childModel, condition_callback)


def bake_all(all_takes=True):
    bake_targets(get_all_nodes_in_scene(), all_takes)


def get_all_nodes_in_scene():
    # type: () -> List[FBModel]
    ret = []
    get_children(ret, FBSystem().Scene.RootModel)
    return ret


def bake_targets(targets, all_takes=True):
    for e in targets:
        e.Translation.SetAnimated(True)
        e.Rotation.SetAnimated(True)
        e.Scaling.SetAnimated(True)

    # 烘焙帧 并清除range之外的帧
    lOptions = FBPlotOptions()
    lOptions.PlotAllTakes = all_takes
    lOptions.PlotOnFrame = True
    lOptions.PlotPeriod = FBTime(0, 0, 0, 1)  # 表示首帧
    lOptions.PlotLockedProperties = True
    lOptions.UseConstantKeyReducer = False
    lOptions.ConstantKeyReducerKeepOneKey = True
    lOptions.RotationFilterToApply = FBRotationFilter.kFBRotationFilterUnroll

    # FBSystem().CurrentTake.PlotTakeOnSelected(lOptions)
    FBSystem().CurrentTake.PlotTakeOnObjects(lOptions, targets)


def set_current_character(character):
    FBApplication().CurrentCharacter = character
    FBSystem().Scene.Evaluate()


def open_fbx_file(fbx_file):
    if isinstance(fbxfile, unicode):
        fbxfile = fbxfile.encode('utf8')
    if not os.path.exists(fbx_file):
        return False, u'文件不存在: {}'.format(fbx_file)
    app = FBApplication()
    app.FileOpen(fbx_file)
    return True, fbx_file


def merge_fbx_file(fbx_file, namespace=None):
    if not os.path.exists(fbx_file):
        return False, u'文件不存在: {}'.format(fbx_file)
    system = FBSystem()
    current_take = system.CurrentTake
    original_time_span = current_take.LocalTimeSpan
    original_start = original_time_span.GetStart()
    original_stop = original_time_span.GetStop()

    fbxLoadOptions = FBFbxOptions(True, fbx_file)
    if namespace:
        fbxLoadOptions.NamespaceList = namespace
    fbxLoadOptions.SetAll(FBElementAction.kFBElementActionMerge, True)
    for takeIndex in range(0, fbxLoadOptions.GetTakeCount()):
        fbxLoadOptions.SetTakeSelect(takeIndex, 0)
    app = FBApplication()
    app.FileMerge(fbx_file, False, fbxLoadOptions)

    current_take.LocalTimeSpan = FBTimeSpan(original_start, original_stop)
    return True, fbx_file


def bake_to_control_rig(ikfk=True, character=None):
    plotoptions = FBPlotOptions()
    plotoptions.ConstantKeyReducerKeepOneKey = False
    plotoptions.PlotAllTakes = False
    plotoptions.PlotOnFrame = True
    plotoptions.PlotPeriod = FBTime(0, 0, 0, 1)
    plotoptions.PlotTranslationOnRootOnly = False
    plotoptions.PreciseTimeDiscontinuities = False
    plotoptions.RotationFilterToApply = FBRotationFilter.kFBRotationFilterNone
    plotoptions.UseConstantKeyReducer = False
    if character is None:
        character = get_current_character()
    control_rig = character.GetCurrentControlSet()
    if not control_rig:
        character.CreateControlRig(ikfk)
    if character.ActiveInput != True:
        character.PlotAnimation(FBCharacterPlotWhere.kFBCharacterPlotOnControlRig, plotoptions)


def bake_to_skeleton(character=None):
    plotoptions = FBPlotOptions()
    plotoptions.ConstantKeyReducerKeepOneKey = False
    plotoptions.PlotAllTakes = False
    plotoptions.PlotOnFrame = True
    plotoptions.PlotPeriod = FBTime(0, 0, 0, 1)
    plotoptions.PlotTranslationOnRootOnly = False
    plotoptions.PreciseTimeDiscontinuities = False
    plotoptions.RotationFilterToApply = FBRotationFilter.kFBRotationFilterNone
    plotoptions.UseConstantKeyReducer = False
    if character is None:
        character = get_current_character()
    if character.ActiveInput == True:
        character.PlotAnimation(FBCharacterPlotWhere.kFBCharacterPlotOnSkeleton, plotoptions)


def get_character_all_ref_ctrls(character):
    controls = []
    ctrl_rig = select_control_rig_from_character(character)
    if ctrl_rig:
        for nodeId in FBEffectorId.values.values():
            if nodeId not in [FBEffectorId.kFBInvalidEffectorId, FBEffectorId.kFBLastEffectorId]:
                effector = ctrl_rig.GetIKEffectorModel(nodeId, 0)
                if effector and effector not in controls:
                    controls.append(effector)
        for nodeId in FBBodyNodeId.values.values():
            if nodeId not in [FBBodyNodeId.kFBInvalidNodeId, FBBodyNodeId.kFBLastNodeId]:
                effector = character.GetCtrlRigModel(nodeId)
                if effector:
                    controls.append(effector)

    if controls:
        controls = list(set(controls))
    return controls


def all_ref_ctrls_by_ctrl_rig(ctrl_rig):
    controls = []
    if ctrl_rig:
        for nodeId in FBEffectorId.values.values():
            if nodeId not in [FBEffectorId.kFBInvalidEffectorId, FBEffectorId.kFBLastEffectorId]:
                effector = ctrl_rig.GetIKEffectorModel(nodeId, 0)
                if effector and effector not in controls:
                    controls.append(effector)
    if controls:
        controls = list(set(controls))
    return controls


if __name__ == '__main__':
    rig_name = 'RY_Rig'
    new_character_file = r'M:\projects\x3\publish\assets\role\FY004S_Card\rbf\maya\data\fbx\FY004S_Card_MB.fbx'
