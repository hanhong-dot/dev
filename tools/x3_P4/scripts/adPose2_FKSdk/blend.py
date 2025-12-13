import pymel.core as pm


def load_plugs():
    if not pm.pluginInfo("aiCloth.py", q=1, l=1):
        pm.loadPlugin("aiCloth.py")


def init():
    pm.newFile(f=1)
    pm.unloadPlugin("ADPoseBlend.mll")


class Blend(object):

    def __init__(self):
        self._node = None

    @property
    def node(self):

        if self._node is not None:
            return self._node
        if not pm.pluginInfo("ADPoseBlend.mll", q=1, l=1):
            pm.loadPlugin("ADPoseBlend.mll")
        nodes = pm.ls(type="ADPoseBlend")
        if len(nodes) > 0:
            self._node = nodes[0]
            return self._node
        selected = pm.selected()
        self._node = pm.createNode("ADPoseBlend", n="ADPoeBlend")
        pm.select(selected)
        return self._node

    def add_joint(self, joint):
        if self.is_connect_joint(joint):
            return
        i = self.next_index(self.node.output)
        matrix = joint.getMatrix()
        self.node.output[i].translate.get()
        self.node.output[i].translate.translateX.connect(joint.translateX, f=1)
        self.node.output[i].translate.translateY.connect(joint.translateY, f=1)
        self.node.output[i].translate.translateZ.connect(joint.translateZ, f=1)
        self.node.output[i].rotate.rotateX.connect(joint.rotateX, f=1)
        self.node.output[i].rotate.rotateY.connect(joint.rotateY, f=1)
        self.node.output[i].rotate.rotateZ.connect(joint.rotateZ, f=1)
        self.node.output[i].scale.scaleX.connect(joint.scaleX, f=1)
        self.node.output[i].scale.scaleY.connect(joint.scaleY, f=1)
        self.node.output[i].scale.scaleZ.connect(joint.scaleZ, f=1)
        for attr in ["translate", "rotate", "scale"]:
            for in_attr in joint.attr(attr).inputs(p=1):
                in_attr.disconnect(joint.attr(attr))
        self.node.bindMatrix[i].set(matrix)

    @staticmethod
    def is_connect_joint(joint):
        return bool(joint.translateX.inputs(type="ADPoseBlend"))

    def del_joint(self, joint):
        i = self.joint_logical_index(joint)
        if i is None:
            return
        pm.removeMultiInstance(self.node.output[i], b=1)
        pm.removeMultiInstance(self.node.bindMatrix[i], b=1)
        for j in range(self.node.input.numElements()):
            pm.removeMultiInstance(self.joint.elementByPhysicalIndex(i).matrix[i], b=1)

    def joint_logical_index(self, joint):
        if not self.is_connect_joint(joint):
            return
        attr = joint.translateX.inputs(p=1)[0]
        i = attr.parent().parent().logicalIndex()
        return i

    def get_joints(self):
        num = self.node.output.numElements()
        joints = []
        for i in range(num):
            joints += self.node.output.elementByPhysicalIndex(i).translate.translateX.outputs()
        return joints

    def get_joint_ids(self):
        num = self.node.output.numElements()
        joints = []
        ids = []
        for i in range(num):
            joints += self.node.output.elementByPhysicalIndex(i).translate.translateX.outputs()
            ids.append(self.node.output.elementByPhysicalIndex(i).logicalIndex())
        return joints, ids

    def add_target(self, target_name):
        joints, ids = self.get_joint_ids()
        matrix_list = [joint.getMatrix() * self.node.bindMatrix[i].get().inverse()
                       for i, joint in zip(ids, joints)]
        if not self.has_target(target_name):
            i = self.next_index(self.node.input)
            pm.aliasAttr(target_name, self.node.input[i].weight)
        else:
            i = self.node.attr(target_name).parent().logicalIndex()
        for j, matrix in zip(ids, matrix_list):
            if matrix == pm.datatypes.Matrix():
                continue
            self.node.input[i].matrix[j].set(matrix)

    def has_target(self, target_name):
        return self.node.hasAttr(target_name)

    def del_target(self, target_name):
        attr = self.node.attr(target_name)
        pm.aliasAttr(attr, rm=1)
        pm.removeMultiInstance(attr.parent(), b=1)
        pm.dgdirty(self.node)

    @staticmethod
    def next_index(attr):
        num = attr.numElements()+1
        for i in range(num):
            if attr[i].exists():
                continue
            return i

    @staticmethod
    def driven_node(joint):
        if joint.type() == "joint":
            return joint
        if joint.type() != "transform":
            return
        if joint.getShape() is None:
            return
        if joint.getShape().type() != "nurbsCurve":
            return
        group = joint.getParent()
        sdk_grp_name = joint.name() + "FKSdkGrp"
        if group.name() == sdk_grp_name:
            return group
        group = pm.group(em=1, n=sdk_grp_name, p=joint.getParent())
        group.setMatrix(joint.getMatrix(ws=1), ws=1)
        joint.setParent(group)
        return group

    def re_fk(self):
        for group in self.get_joints():
            if group.type() != "transform":
                continue
            if not group.name().endswith("FKSdkGrp"):
                continue
            ctrl_name = group.name()[:-len("FKSdkGrp")]
            ctrl = pm.PyNode(ctrl_name)
            group.setMatrix(ctrl.getMatrix(ws=1), ws=1)
            ctrl.t.set(0, 0, 0)
            ctrl.r.set(0, 0, 0)
            ctrl.s.set(1, 1, 1)


def add_selected():
    blend = Blend()
    for sel in pm.selected(o=1):
        driven = blend.driven_node(sel)
        if driven is None:
            continue
        blend.add_joint(driven)


def del_selected():
    blend = Blend()
    for sel in pm.selected(o=1):
        driven = blend.driven_node(sel)
        if driven is None:
            continue
        blend.del_joint(driven)


def edit_target(target_name):
    import ADPose
    blend = Blend()
    blend.re_fk()
    blend.add_target(target_name)
    attr = ADPose.ADPoses.add_by_target(target_name)
    if not blend.node.attr(target_name).inputs():
        attr.connect(blend.node.attr(target_name))


def del_target(target_name):
    blend = Blend()
    blend.del_target(target_name)


def doit():
    pm.newFile(f=1)
    joint1 = pm.polyCube(ch=0)[0]
    joint2 = pm.polyCube(ch=0)[0]
    joint3 = pm.polyCube(ch=0)[0]
    Blend().add_joint(joint1)
    Blend().add_joint(joint2)
    Blend().add_joint(joint3)
    Blend().del_joint(joint2)
    joint1.t.set(10, 10, 10)
    joint1.r.set(10, 10, 10)
    joint1.s.set(2, 2, 2)
    joint3.t.set(-10, -10, -10)
    joint3.r.set(10, 10, 10)
    joint3.s.set(2, 2, 2)
    Blend().add_target("targetA")
    Blend().node.targetA.set(0.5)
    Blend().add_target("targetB")
    joint1.t.set(10, 10, 10)
    joint1.r.set(10, 10, 10)
    joint1.s.set(0.5, 0.5, 0.5)
    Blend().add_target("targetC")
    Blend().del_target("targetB")


"""
from adPose2_FKSdk.adPose2 import blend
reload(blend)
blend.doit()

blend.init()
"""