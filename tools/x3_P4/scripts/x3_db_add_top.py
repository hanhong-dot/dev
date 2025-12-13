from maya import cmds


def undo(fun):
    def undo_fun(*args, **kwargs):
        cmds.undoInfo(openChunk=1)
        fun(*args, **kwargs)
        cmds.undoInfo(closeChunk=1)
    return undo_fun


@undo
def x3_db_add_top():
    for sel in cmds.ls(sl=1, type="joint"):
        children = cmds.listRelatives(sel)
        top = cmds.rename(sel, sel+"_top")
        tx = cmds.softSelect(q=1, ssd=1)
        cmds.softSelect(q=1, ssd=1)
        cmds.joint(top, n=sel)
        cmds.setAttr(sel+".tx", tx)
        for child in children:
            cmds.parent(child, sel)


if __name__ == '__main__':
    x3_db_add_top()