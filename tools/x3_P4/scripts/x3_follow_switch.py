from maya import cmds


def create_node(typ, name, parent=None):
    if cmds.objExists(name):
        return name
    if parent is not None:
        return cmds.createNode(typ, n=name, p=parent, ss=True)
    else:
        return cmds.createNode(typ, n=name, ss=True)


def create_group(name, parent=None):
    return create_node("transform", name, parent)


def set_parent(child, parent):
    if parent is None:
        return
    if not cmds.objExists(parent):
        return
    real_parent = cmds.listRelatives(child, p=1)
    if not real_parent:
        cmds.parent(child, parent)
    elif parent not in real_parent:
        cmds.parent(child, parent)


def build_hry(*names):
    for parent, child in zip(names, names[1:]):
        if not cmds.objExists(parent):
            create_group(parent)
        create_group(child, parent)
        set_parent(child, parent)
        cmds.xform(child, ws=0, m=[1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1])


def sub_suffixes(prefix, *suffixes):
    return [prefix+suf for suf in suffixes]


def create_loc(name, parent):
    loc = create_group(name, parent)
    shape = create_node("locator", loc+"Shape", loc)
    cmds.setAttr(shape+".v", 0)
    return loc


def re_shape(src, dst):
    for shape in cmds.listRelatives(src, s=1, f=1) or []:
        cmds.parent(shape, dst, s=1, add=1)


def re_link(src, dst):
    for trs in "trs":
        for xyz in "xyz":
            attr = src+"."+trs+xyz
            for src_attr in cmds.listConnections(attr, s=1, d=0, p=1) or []:
                is_referenced = cmds.referenceQuery(src_attr.split(".")[0], isNodeReferenced=True)
                if is_referenced:
                    continue
                cmds.disconnectAttr(src_attr, src+"."+trs+xyz)
                cmds.connectAttr(src_attr, dst+"."+trs+xyz)


def create_follow():
    parents = cmds.ls(sl=1)
    orig_ctrl = parents.pop(0)
    pre = orig_ctrl + "Follow"
    pre = pre.replace(":", "_")
    root, temp = sub_suffixes(pre, "System", "Temp")
    if cmds.objExists(root):
        cmds.delete(root)
    build_hry(root, temp)
    cmds.setAttr(temp+".v", 0)
    re_shape(orig_ctrl, temp)
    dup_temp = cmds.duplicate(temp, n=temp+"_dup")[0]
    cmds.setAttr(dup_temp+".s", 1.2, 1.2, 1.2)
    cmds.makeIdentity(dup_temp, apply=1, t=1, r=1, s=1)
    parents.append(cmds.listRelatives(orig_ctrl, p=1)[0])
    ctrls = []
    for parent in parents:
        _pre = pre+parent.split(":")[-1]
        grp, ctrl = sub_suffixes(_pre, "Group", "Ctrl")
        build_hry(root, grp, ctrl)
        re_shape(dup_temp, ctrl)
        cmds.parentConstraint(parent, grp)
        cmds.scaleConstraint(parent, grp)
        ctrls.append(ctrl)
    re_link(orig_ctrl, ctrls[-1])
    pc = cmds.parentConstraint(ctrls, orig_ctrl)[0]
    wal = cmds.parentConstraint(pc, q=1, wal=1)
    for attr in wal:
        ln = attr[len(pre):-1] + "eight"
        if not cmds.objExists(ctrls[-1]+"."+ln):
            cmds.addAttr(ctrls[-1], ln=ln, at="double", min=0, max=1, dv=0, k=1)
        cmds.connectAttr(ctrls[-1]+"."+ln, pc+"."+attr)
    cmds.setAttr(ctrls[-1]+"."+wal[-1][len(pre):-1] + "eight", 1)


def doit():
    names = [u'nurbsCircle1', u'nurbsCircle2', u'nurbsCircle3']
    names = [u"aaa:"+n for n in names]
    cmds.select(names)
    create_follow()


if __name__ == '__main__':
    create_follow()
