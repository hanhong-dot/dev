# coding=utf-8
from .adPose2.general_ui import *
from .adPose2.config import ConfigTool
from .targets import TargetEditTool
from .adPose2.grid import UVPoseTool
from .adPose2.facs_ui import FaceTargetEditTool
from .adPose2.twist_ui import TwistTargetEditTool
from . import tools
from .adPose2 import ocd
from .adPose2 import bs
from .adPose2 import tools as tools0
from .adPose2 import ADPose
from .adPose2 import joints
from . import FKSdk
from . import sdr_export_bs
from . import ocd_batch_baking
from .adPose2 import little
from . import sdr
from . import check_json_fbx
from functools import partial
from .adPose2.main_ui import MainEditTool


class ADPoseTool(QDialog):

    def __init__(self):
        QDialog.__init__(self, get_host_app())
        self.setObjectName("UVPoseTool")
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 2, 0, 0)
        try:
            layout.setMargin(5)
        except AttributeError:
            pass
        self.setLayout(layout)
        self.config = ConfigTool(self)
        menu_bar = QMenuBar()
        layout.setMenuBar(menu_bar)

        self.list = TargetEditTool(self)
        self.face = FaceTargetEditTool(self)
        self.grid = UVPoseTool()
        self.tab = QTabWidget(self)
        self.twist = TwistTargetEditTool(self)

        layout.addWidget(button(u"刷新", self.button_refresh))

        layout.addWidget(self.tab)
        self.tab.addTab(self.list, u"列表")
        self.tab.addTab(self.grid, u"网格")
        self.tab.addTab(self.face, u"表情")
        self.tab.addTab(self.twist, u"twist")

        self.main_ui = MainEditTool()
        self.tab.addTab(self.main_ui, u"main")

        self.setBaseSize(10, 10)

        self.bake_ocd = ocd.BakeOcd(self)
        self.bake_deform = ocd.BakeDeform(self)
        self.bake_deform_batch = ocd_batch_baking.BakeDeform_batch(self)
        self.export_bs_to_unity = sdr_export_bs.ExportBSToUnityTool(self)
        tool_menu = menu_bar.addMenu(u"工具")
        tool_menu.addAction(u"配置", self.config.showNormal)
        tool_menu.addAction(u"清理orig", ocd.clear_orig)
        tool_menu.addAction(u"冻结骨骼旋转值", ADPose.free_joints)
        tool_menu.addAction(u"自定义镜像", self.custom_mirror)

        tool_menu.addAction(u"导出BS和驱动", tools0.export_blend_shape_sdk_data_ui)
        # tool_menu.addAction(u"导出旧版BS和驱动", tools.export_old_blend_shape_sdk_data_ui)
        tool_menu.addAction(u"导入BS和驱动", tools0.load_blend_shape_sdk_data_ui)
        tool_menu.addAction(u"导入BS并覆盖驱动", partial(tools0.load_blend_shape_sdk_data_ui, True))
        tool_menu.addAction(u"合并模型并保留蒙皮BS", tools0.comb_skin_bs)
        tool_menu.addAction(u"清理空目标体", self.clear_un_use_bs_target)
        tool_menu.addAction(u"清理选择点的BS", self.del_bs_for_points_on_targets)
        tool_menu.addAction(u"重置目标体", self.init_targets)
        tool_menu.addAction(u"传递目标体", self.copy_targets)

        tool_menu.addAction(u"使用热盒模式", little.open_tool)
        tool_menu.addAction(u"清理空pose", self.clear_useless_pose)

        # tool_menu.addAction(u"导出FK驱动", tools_FKSdk.export_fk_sdk_data_ui)
        # tool_menu.addAction(u"导入FK驱动", tools_FKSdk.load_fk_sdk_data_ui)

        ocd_menu = menu_bar.addMenu(u"ocd")
        ocd_menu.addAction(u"创建ocd", ocd.create_ocd)
        ocd_menu.addAction(u"根据蒙皮创建ocd", ocd.create_ocd_by_skin)
        ocd_menu.addAction(u"烘焙修型", self.bake_deform.show)
        ocd_menu.addAction(u"烘焙修型自定义方案", self.bake_deform_batch.show)
        ocd_menu.addAction(u"烘焙ocd", self.bake_ocd.show)

        sdr_menu = menu_bar.addMenu(u"sdr")
        # sdr_menu.addAction(u"修型转骨骼", self.sdr_driver.showNormal)
        # sdr_menu.addAction(u"镜像骨骼驱动", sdr.mirror_sdr_joints)
        # sdr_menu.addAction(u"自动key帧", sdr.auto_key)
        # sdr_menu.addAction(u"转成骨骼动画", self.sdr_ani.showNormal)
        # sdr_menu.addAction(u"转为骨骼驱动", sdr.plane_sdk)
        # sdr_menu.addAction(u"修复骨骼驱动", sdr.re_plane_sdk)

        sdr_menu.addAction(u"导出到unity", sdr.export_to_unity_ui)
        sdr_menu.addAction(u"导出bs信息到unity", self.export_bs_to_unity.show)
        sdr_menu.addAction(u"记录跟随模型点信息", sdr_export_bs.tool_add_point_drive)
        sdr_menu.addAction(u"检查BS修型数据", check_json_fbx.show)
        sdr_menu.addAction(u"导出Pose", sdr.export_pose_data_ui)
        sdr_menu.addAction(u"导入修型模型", sdr.import_pose_data_ui)

        self.create_joint_tool = joints.CreateJointTool(self)
        joints_menu = menu_bar.addMenu(u"骨骼")
        joints_menu.addAction(u"创建骨骼", self.create_joint_tool.showNormal)
        joints_menu.addAction(u"镜像骨骼", joints.mirror_joints)

        def _create_plane_by_selected():
            tools.add_selected_joint_to_fk_sdk_set()
            joints.create_plane_by_selected()
        joints_menu.addAction(u"创建驱动", _create_plane_by_selected)
        joints_menu.addAction(u"创建FK面片", FKSdk.create_FK_attach)
        joints_menu.addAction(u"镜像FK面片", FKSdk.mirror_FK_attach)
        joints_menu.addAction(u"创建临时控制器", joints.create_temp_fk)
        self.tab.currentChanged.connect(self.button_refresh)

    def clear_un_use_bs_target(self):
        target_names = bs.clear_un_use_bs()
        message = QDialog(self)
        message.setWindowTitle(u"清理空目标体：")
        lay = QHBoxLayout()
        message.setLayout(lay)
        list_widget = QListWidget(self)
        lay.addWidget(list_widget)
        list_widget.addItems(target_names)
        message.exec_()

    def button_refresh(self):
        if self.tab.currentIndex() == 0:
            self.list.list.reload()
        elif self.tab.currentIndex() == 1:
            self.grid.grid.set_control([0, 0])
            self.grid.reload()
        elif self.tab.currentIndex() == 2:
            self.face.list.reload()
        elif self.tab.currentIndex() == 3:
            self.twist.list.reload()
        elif self.tab.currentIndex() == 4:
            self.main_ui.list.reload()

    def get_selected_targets_list(self):
        if self.tab.currentIndex() == 0:
            targets = self.list.list.selected_targets()
            return targets
        elif self.tab.currentIndex() == 1:
            return []
        elif self.tab.currentIndex() == 2:
            targets = self.face.list.selected_targets()
            return targets
        elif self.tab.currentIndex() == 3:
            targets = self.twist.list.selected_targets()
            return targets
        elif self.tab.currentIndex() == 4:
            targets = self.main_ui.list.selected_targets()
            return targets

    def del_bs_for_points_on_targets(self):
        targets = self.get_selected_targets_list()
        bs.delete_bs_for_points(targets)

    def init_targets(self):
        bs.init_targets(self.get_selected_targets_list())

    def custom_mirror(self):
        bs.custom_mirror(self.get_selected_targets_list())

    def copy_targets(self):
        bs.tool_copy_targets(self.get_selected_targets_list())

    def clear_useless_pose(self):
        ADPose.ADPoses.clear_useless_pose()
        self.button_refresh()



window = None


def show():
    global window
    if window is None:
        window = ADPoseTool()
    window.show()


def show_in_maya():
    global window
    if int(str(pm.about(api=True))[:4]) > 2017:
        while pm.control("uvPoseTool_dock", query=True, exists=True):
            pm.deleteUI("uvPoseTool_dock")
        while pm.control("UVPoseTool", query=True, exists=True):
            pm.deleteUI("UVPoseTool")
        dock = pm.mel.getUIComponentDockControl("Channel Box / Layer Editor", False)
        pm.workspaceControl("uvPoseTool_dock", ttc=(dock, -1), r=1, l=u"UVPoseTool", retain=True)
        window = ADPoseTool()
        pm.control(window.objectName(), e=1, p="uvPoseTool_dock")
    else:
        if window is None:
            if pm.dockControl("uvPoseTool_dock", ex=1):
                pm.deleteUI("uvPoseTool_dock")
            window = ADPoseTool()
            pm.dockControl("uvPoseTool_dock", area='right', content="UVPoseTool",
                           allowedArea=['right', 'left'], l=u"UVPose")
        pm.dockControl("uvPoseTool_dock", e=1, vis=0)
        pm.dockControl("uvPoseTool_dock", e=1, vis=1)

