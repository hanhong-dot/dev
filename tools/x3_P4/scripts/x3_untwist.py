from maya import cmds


def create_node(typ, name):
    if not cmds.objExists(name):
        return cmds.createNode(typ, n=name)
    if cmds.objectType(name) != typ:
        return cmds.createNode(typ, n=name)
    return name


def is_attr(attr):
    if not isinstance(attr, basestring):
        return False
    if "." not in attr:
        return False
    if not cmds.objExists(attr):
        return False
    return True


def check_connect_attr(src, dst):
    if not cmds.isConnected(src, dst):
        cmds.connectAttr(src, dst, f=1)


def set_or_connect(attr, value):
    if is_attr(value):
        check_connect_attr(value, attr)
    else:
        if cmds.getAttr(attr, type=1) == "double3":
            cmds.setAttr(attr, *value)
        else:
            cmds.setAttr(attr, value)


def rig_node(typ, name, output, inputs):
    node = create_node(typ, name)
    for key, value in inputs.items():
        set_or_connect(node + "." + key, value)
    if isinstance(output, (list, tuple)):
        return [node + "." + out for out in output]
    else:
        return node + "." + output


def rig_mul_matrix(name, *matrices):
    return rig_node("multMatrix", name, "matrixSum", {"matrixIn[%i]" % i: matrix for i, matrix in enumerate(matrices)})


def rig_vector_mul_matrix(name, vector, matrix):
    return rig_node("pointMatrixMult", name, "output", dict(inPoint=vector, inMatrix=matrix, vectorMultiply=True))


def rig_two_vector_ro_euler(name, vector1, vector2):
    return rig_node("angleBetween", name, "euler", dict(vector1=vector1, vector2=vector2))


def rig_compose_matrix(name, t, r, s):
    return rig_node("composeMatrix", name, "outputMatrix", dict(inputTranslate=t, inputRotate=r, inputScale=s))


def rig_decompose_matrix(name, matrix):
    return rig_node("decomposeMatrix", name, ["outputTranslate", "outputRotate", "outputScale"],
                    dict(inputMatrix=matrix))


def get_parent(name):
    return (cmds.listRelatives(name, p=1) or [None])[0]


def create_joint(name, parent):
    if cmds.objExists(name):
        if get_parent(name) != parent:
            cmds.parent(name, parent)
        return name
    else:
        return cmds.joint(parent, n=name)


def create_untwist(parent, driver):
    if not cmds.objExists(parent):
        return
    if not cmds.objExists(driver):
        return
    pre = driver + "_x3_untwist_"
    local_matrix = rig_mul_matrix(pre+"local_matrix", driver+".worldMatrix[0]", parent+".worldInverseMatrix[0]")
    x_axis = rig_vector_mul_matrix(pre+"x_axis", (1, 0, 0), local_matrix)
    swing_euler = rig_two_vector_ro_euler(pre+"swing_euler", (1, 0, 0), x_axis)
    skin = create_joint(driver + "_No_Twist", parent)
    set_or_connect(skin+".rotate", swing_euler)
    translate, _, _ = rig_decompose_matrix(pre+"translate", local_matrix)
    set_or_connect(skin + ".translate", translate)

    matrix = rig_mul_matrix(pre+"matrix", skin+".worldMatrix[0]", driver+".worldInverseMatrix[0]")
    no_twist = create_joint(driver + "_No_Twist_Skin", driver)
    _, rotate, _ = rig_decompose_matrix(pre+"rotate", matrix)
    set_or_connect(no_twist + ".rotate", rotate)


def create_all_untwist():
    create_untwist("Elbow_R", "ElbowPart1_R")
    create_untwist("ElbowPart1_R", "ElbowPart2_R")
    create_untwist("Knee_R", "KneePart1_R")
    create_untwist("KneePart1_R", "KneePart2_R")
    create_untwist("Elbow_L", "ElbowPart1_L")
    create_untwist("ElbowPart1_L", "ElbowPart2_L")
    create_untwist("Knee_L", "KneePart1_L")
    create_untwist("KneePart1_L", "KneePart2_L")


def doit():
    create_all_untwist()


if __name__ == '__main__':
    create_all_untwist()

