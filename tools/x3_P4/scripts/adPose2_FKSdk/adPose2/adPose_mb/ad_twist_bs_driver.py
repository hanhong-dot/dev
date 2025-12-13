from ad_core import *


def get_ad_twist_data():
    mesh_list = find_all_mesh()
    driver_data = {}
    target_mesh_data = {}
    real_mesh_list = []
    for mesh in mesh_list:
        for attr in mesh.PropertyList:
            target_name = attr.Name
            match = re.match(r"^(?P<joint>\w+)_twistX_(?P<plus_minus>plus|minus)(?P<value>[0-9]{1,2})$", target_name)
            if not match:
                continue
            if "Part" not in target_name:
                continue
            attr.SetAnimated(True)
            value = int(match.groupdict()["value"])
            if match.groupdict()["plus_minus"] == "minus":
                value *= -1
            driver_data.setdefault(match.groupdict()["joint"], {}).setdefault(target_name, value)
            target_mesh_data.setdefault(target_name, []).append(mesh)
            if mesh not in real_mesh_list:
                real_mesh_list.append(mesh)
    return driver_data, target_mesh_data, real_mesh_list


def get_real_twist(joint_name):
    return find_by_name(joint_name)


def get_twist_sdk_data(values, value):
    values = list(sorted(list(values) + [0, -180, 180]))
    index = values.index(value)
    sdk_times = [values[i+index] for i in [-1, 0, 1]]
    sdk_values = [0, 1, 0]
    if sdk_times[0] == -180.0:
        sdk_values[0] = 1
    if sdk_times[-1] == 180.0:
        sdk_values[-1] = 1

    sdk_values = [i*100 for i in sdk_values]
    return [[t, v] for t, v in zip(sdk_times, sdk_values)]


def main():
    driver_data, target_mesh_data, real_mesh_list = get_ad_twist_data()
    if not driver_data:
        return
    if not real_mesh_list:
        return
    delete_node_by_name("CHAR_Deformation_TwistBlendShapeSDK", "Constraints")
    relation = FBConstraintRelation("CHAR_Deformation_TwistBlendShapeSDK")
    NODE_W = 500
    NODE_H = 400
    mesh_box_list = []
    for j, mesh in enumerate(real_mesh_list):
        open_blend_shape_anim(mesh)
        mesh_box = relation.ConstrainObject(mesh)
        relation.SetBoxPosition(mesh_box, int(NODE_W * (4+0.1*j)), 0)
        mesh_box_list.append(mesh_box)
    i = 0
    for joint_name, value_data in driver_data.items():
        real_twist = get_real_twist(joint_name)
        if not real_twist:
            continue

        src_box = relation.SetAsSource(real_twist)
        relation.SetBoxPosition(src_box, NODE_W * 0, NODE_H * (i+0))

        parent_box = relation.SetAsSource(real_twist.Parent)
        relation.SetBoxPosition(parent_box, NODE_W * 0, NODE_H * (i+1))

        relative = relation.CreateFunctionBox("Rotation", "Global To Local")
        relation.SetBoxPosition(relative, NODE_W * 1, NODE_H * (i+0))

        connect(src_box, "Rotation", relative, "Global Rot")
        connect(parent_box, "Rotation", relative, "Base")

        vector_to_number = relation.CreateFunctionBox('Converters', 'Vector To Number')
        relation.SetBoxPosition(vector_to_number, NODE_W * 2, NODE_H * i)
        connect(relative, "Local Rot", vector_to_number, "V")
        values = list(value_data.values())

        for j, (target_name, value) in enumerate(value_data.items()):
            sdk_data = get_twist_sdk_data(values, value)
            sdk = create_driver_3d_node(relation, 3 * NODE_W, int((i+0.5*j) * NODE_H), sdk_data)
            FBConnect(
                FindAnimationNode(vector_to_number.AnimationNodeOutGet(), "X"),
                sdk["Input_value"]
            )
            for mesh_box in mesh_box_list:
                FBConnect(
                    sdk["Output_value"],
                    FindAnimationNode(mesh_box.AnimationNodeInGet(), target_name)
                )
        i += 2
    relation.Active = True

def test():
    main()
