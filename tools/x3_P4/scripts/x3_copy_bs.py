from maya.api.OpenMaya import *
from maya import cmds


def find_bs(polygon):
    if not cmds.objExists(polygon):
        return
    shapes = set(cmds.listRelatives(polygon, s=1, f=1) or [])
    for bs in cmds.ls(cmds.listHistory(polygon), type="blendShape"):
        if not cmds.blendShape(bs, q=1, g=1):
            continue
        if cmds.ls(cmds.blendShape(bs, q=1, g=1), l=1)[0] in shapes:
            return bs


def get_bs(polygon):
    bs = find_bs(polygon)
    if bs is None:
        bs = cmds.blendShape(polygon, automatic=True, n=polygon.split("|")[-1] + "_bs")[0]
    return bs


def get_next_index(bs):
    elem_indexes = cmds.getAttr(bs+".weight", mi=1) or []
    index = len(elem_indexes)
    for i in range(index):
        if i == elem_indexes[i]:
            continue
        index = i
        break
    return index


def get_index(bs, target):
    return api_ls(bs+"."+target).getPlug(0).logicalIndex()


def add_real_target(polygon, bs, target, target_polygon):
    print("real", polygon)
    if cmds.objExists(bs + "." + target):
        index = get_index(bs, target)
    else:
        index = get_next_index(bs)
    cmds.blendShape(bs, e=1, t=[polygon, index, target_polygon, 1])
    bs_attr = bs+'.weight[%i]' % index
    cmds.aliasAttr(bs_attr, rm=1)
    cmds.aliasAttr(target, bs_attr)
    
    
def api_ls(*names):
    selection_list = MSelectionList()
    for name in names:
        selection_list.add(name)
    return selection_list


def connect_attr(src, dst):
    if not src:
        return
    if not cmds.objExists(dst):
        return
    if cmds.isConnected(src, dst):
        return
    cmds.connectAttr(src, dst, f=1)


def dis_connect_attr(src, dst):
    if not src:
        return
    if not cmds.objExists(dst):
        return
    if not cmds.isConnected(src, dst):
        return
    cmds.disconnectAttr(src, dst)


def get_driver_attr(attr):
    for src_attr in cmds.listConnections(attr, s=1, d=0, p=1) or []:
        return src_attr


def copy_bs(src, warp, dst):
    src_bs = find_bs(src)
    if not src_bs:
        return
    print("dst bs", dst)
    dst_bs = get_bs(dst)

    for target in cmds.listAttr(src_bs+".weight", m=1) or []:
        wt_attr = src_bs + "." + target
        driver_attr = get_driver_attr(src_bs + "." + target)
        dis_connect_attr(driver_attr, wt_attr)
        cmds.setAttr(wt_attr, 1)
        dup_target = cmds.duplicate(warp, n=dst+target)[0]
        cmds.setAttr(wt_attr, 0)
        add_real_target(dst, dst_bs, target, dup_target)
        connect_attr(driver_attr, wt_attr)
        connect_attr(driver_attr, dst_bs+"."+target)
        cmds.delete(dup_target)


def clear_orig(polygon):
    orig_list = [shape for shape in cmds.listRelatives(polygon, s=1, f=1) or [] if cmds.getAttr(shape + '.io')]
    if orig_list:
        cmds.delete(orig_list)


def tool_copy_bs():
    sel = cmds.ls(sl=1, type="transform")
    if len(sel) == 1:
        src = sel[0]
        warp = src
        dst = cmds.duplicate(warp, n="dup_"+warp)[0]
        clear_orig(dst)
        copy_bs(src, warp, dst)
        return dst
    elif len(sel) == 2:
        src, warp = sel
        dst = cmds.duplicate(warp, n="dup_"+warp)[0]
        clear_orig(dst)
        copy_bs(src, warp, dst)
        return dst
    elif len(sel) == 3:
        src, warp, dst = sel
        clear_orig(dst)
        copy_bs(src, warp, dst)
        return dst


def doit():
    # cmds.select("NPC_EM03_Head", "NPC_EM03_Eyeshell_fx", "NPC_EM03_Eyeshell")
    cmds.select("NPC_EM03_Head", "NPC_EM03_Eyelashes_fx", "NPC_EM03_Eyelashes")
    print(len(cmds.ls(sl=1)))
    tool_copy_bs()
    # cmds.select("dup_head_lod0_mesh")
    # tool_copy_bs()

if __name__ == '__main__':
    tool_copy_bs()

