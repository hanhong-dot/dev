# coding:utf-8
from .adPose2.general_ui import *
from .adPose2.ADPose import ADPoses, comb_target_to_targets
from .adPose2 import bs
from .adPose2 import joints
from . import FKSdk
import re
from . import blend


class TargetList(QListWidget):
    mirrorTargets = Signal(list)

    def __init__(self, parent=None):
        QListWidget.__init__(self, parent)
        self.setSelectionMode(self.ExtendedSelection)
        self.menu = QMenu(self)
        self.menu.addAction(u"添加/修改", self.auto_edit_by_selected_target)
        self.menu.addAction(u"插入姿势", self.auto_insert_pose)
        self.menu.addAction(u"骨骼驱动", self.auto_edit_body_deform)
        self.menu.addAction(u"FK驱动/修改", self.auto_edit_FKSdk_body_deform)
        self.menu.addAction(u'FK Set to Zero', self.auto_edit_FKSdk_body_deform_setToZero)
        self.menu.addAction(u"删除Pose", self.delete_targets)
        self.menu.addAction(u"删除选择模型目标体", self.delete_selected_targets)
        self.menu.addAction(u"镜像", self.mirror_targets)
        self.menu.addAction(u"传递", self.warp_copy_targets)
        self.menu.addAction(u"刚性烘焙", self.rigid_bs)

        self.menu.addAction(u"反算法线", self.repair_normal_targets)

        unity_sdk = QMenu("unity sdk")
        unity_sdk.addAction(u"添加控制器/骨骼", blend.add_selected)
        unity_sdk.addAction(u"移除控制器/骨骼", blend.del_selected)
        unity_sdk.addAction(u"添加/修改Pose", self.edit_unity_sdk_target)
        unity_sdk.addAction(u"移除Pose", self.delete_unity_sdk_targets)

        self.menu.addMenu(unity_sdk)

        self.itemDoubleClicked.connect(self.set_pose)
        self.text = ""
        self.reload()

    def repair_normal_targets(self):
        from .adPose2 import invert_normal
        invert_normal.repair_normal_targets(self.selected_targets())


    def auto_insert_pose(self):
        ADPoses.auto_insert_pose(self.text.split(","))
        self.reload()

    def rigid_bs(self):
        from . import rigid_bs
        rigid_bs.tool_rigid_bake(self.selected_targets())

    def edit_unity_sdk_target(self):
        blend.edit_target(self.selected_targets()[0])

    def delete_unity_sdk_targets(self):
        for target_name in self.selected_targets():
            blend.del_target(target_name)

    def delete_selected_targets(self):
        bs.delete_selected_targets(self.selected_targets())

    def auto_edit_by_selected_target(self):
        ADPoses.auto_edit_by_selected_target(self.text.split(","))
        self.reload()

    def auto_edit_body_deform(self):
        joints.body_deform_sdk(self.text.split(","))
        self.reload()

    def auto_edit_FKSdk_body_deform(self):
        FKSdk.FKSdk_body_deform_sdk(self.text.split(","))
        self.reload()

    def auto_edit_FKSdk_body_deform_setToZero(self):
        FKSdk.FKSdk_body_deform_sdk_setToZero(self.selected_targets())
        self.reload()

    def set_pose(self):
        ADPoses.set_pose_by_targets(self.selected_targets())

    def mirror_targets(self):
        self.mirrorTargets.emit(self.selected_targets())

    def delete_targets(self):
        ADPoses.delete_by_targets(self.selected_targets())
        self.reload()

    def selected_targets(self):
        return [item.text() for item in self.selectedItems()]

    def warp_copy_targets(self):
        bs.tool_part_warp_copy(ADPoses.warp_copy_targets)(self.selected_targets())

    def reload(self):
        self.clear()
        self.addItems(ADPoses.get_targets())
        self.query()

    def query(self):
        # 加载模型时，只显示模型的bs
        fields = [field.replace("*", ".+") for field in self.text.split(",") if field]
        targets = []
        for field in list(fields):
            if "+" in field:
                continue
            polygons = pm.ls(field, type="transform")
            if len(polygons) == 0:
                continue
            polygon = polygons[0]
            if not (polygon.getShape() is not None and polygon.getShape().type() == "mesh"):
                continue
            fields.remove(field)
            for _bs in polygon.listHistory(type="blendShape"):
                targets.extend(_bs.weight.elements())
        # 使用*过滤

        for i in range(self.count()):
            if not any([bool(re.findall(field, self.item(i).text())) for field in fields]+[not bool(fields)]):
                self.setItemHidden(self.item(i), True)
            else:
                self.setItemHidden(self.item(i), False)
            if targets and self.item(i).text() not in targets:
                self.setItemHidden(self.item(i), True)

    def set_text(self, text):
        self.text = text
        self.query()

    def load_objs(self, text):
        self.text = text
        self.reload()
        self.query()

    def contextMenuEvent(self, event):
        self.menu.exec_(event.globalPos())

    def get_targets(self):
        return [self.item(i).text() for i in range(self.count())]


class TargetEditTool(Tool):
    button_text = u"复制/修改"

    def __init__(self, parent=None):
        Tool.__init__(self, parent)
        self.polygons = MayaObjLayouts(u"模型：", 40)
        self.query = MayaObjLayouts(u"搜索：", 40)
        self.query.line.setReadOnly(False)
        self.slider = TargetSlider()
        self.list = TargetList(self)
        self.kwargs_layout.addLayout(self.slider)
        self.kwargs_layout.addLayout(self.polygons)
        self.kwargs_layout.addLayout(self.query)
        self.kwargs_layout.addWidget(self.list)
        self.query.textChanged.connect(self.list.load_objs)
        self.query.line.textChanged.connect(self.list.set_text)
        self.list.mirrorTargets.connect(self.mirror)
        self.slider.slider.valueChanged.connect(self.set_ib_pose_by_targets)
        self.slider.button.clicked.connect(self.esc)

    def set_ib_pose_by_targets(self, value):
        ADPoses.set_pose_by_targets(self.list.selected_targets(), [], value)
        pm.refresh()

    def apply(self):
        polygons = self.get_polygons()
        if polygons is not None:
            pm.select(polygons)
        _joints = self.query.line.text().split(",")
        ADPoses.auto_apply(_joints)
        self.list.reload()

    @staticmethod
    def esc():
        ADPoses.auto_edit(False)

    def get_polygons(self):
        polygons = pm.ls(self.polygons.line.text().split(","), type="transform")
        polygons = [poly for poly in polygons if bs.is_polygon(poly)]
        if not len(polygons):
            polygons = None
        return polygons

    def mirror(self, targets):
        ADPoses.mirror_by_targets(targets)
        self.list.reload()
