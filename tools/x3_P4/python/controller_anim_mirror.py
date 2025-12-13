# encoding=UTF-8
import pymel.core as pm
import re
import maya.api.OpenMaya as om
try:
    from PySide.QtGui import *
    from PySide.QtCore import *
    from PySide.QtNetwork import *
except ImportError:
    from PySide2.QtGui import *
    from PySide2.QtCore import *
    from PySide2.QtWidgets import *
print '-------'

# -----------------------------------------------------------


def get_all_anim_layer():
    try:
        root_layer = pm.animLayer(q=True, r=True)
        return pm.animLayer(root_layer, q=True, c=True)+[root_layer]
    except RuntimeError:
        return []


def get_name_spaces():
    return list(set([cnt.namespace() for cnt in pm.ls(type='nurbsCurve')]))


def get_fks_by_name_space(n_space):
    return [pm.PyNode(cnt.replace('Shape', '')) for cnt in pm.ls(type='nurbsCurve') if cnt.startswith(n_space+'FK') and not cnt.startswith(n_space+'FKIK')]


def get_root_x_by_name_space(n_space):
    return pm.PyNode(n_space+'RootX_M')


def get_hip_swing_by_name_space(n_space):
    if not pm.objExists(n_space+'HipSwinger_M'):
        return
    return pm.PyNode(n_space+'HipSwinger_M')


def get_iks_by_name_space(n_space):
    return [pm.PyNode(cnt.replace('Shape', '')) for cnt in pm.ls(type='nurbsCurve') if cnt.startswith(n_space+'IK')] + \
           [pm.PyNode(cnt.replace('Shape', '')) for cnt in pm.ls(type='nurbsCurve') if cnt.startswith(n_space+'Roll')] + \
           [pm.PyNode(cnt.replace('Shape', '')) for cnt in pm.ls(type='nurbsCurve') if cnt.startswith(n_space+'Pole')]


def get_ikfk_blend_by_name_space(n_space):
    return [pm.PyNode(cnt.replace('Shape', '')) for cnt in pm.ls(type='nurbsCurve') if cnt.startswith(n_space+'FKIK')]


class TR:

    def __init__(self, trans, rot):
        self.trans = trans
        self.rot = rot


def current_itme():
    return int(round(pm.currentTime()))


def is_lr(name):
    if name.endswith('_L') or name.endswith('_R'):
        return True
    return False


# def order_zxy_mirror_yz(_trans, _rot):  # adv脊椎
#     _trans.y *= -1
#     _rot.x *= -1
#     _rot.y *= -1
#
#
# def order_zxy_mirror_xy(_trans, _rot):
#     _trans.z *= -1
#     _rot.x *= -1
#     _rot.y *= -1
#
#
# def order_xyz_mirror_yz(_trans, _rot):  # adv RootX_M
#     _trans.x *= -1
#     _rot.y *= -1
#     _rot.z *= -1
#
#
# def order_xyz_mirror_xy(_trans, _rot):
#     _trans.z *= -1
#     _rot.y = 180 - _rot.y
#     _rot.z *= -1
#
#
# def get_xyz_func(p):
#     if p == 'xy':
#         return order_xyz_mirror_xy
#     if p == 'yz':
#         return order_xyz_mirror_yz
#
#
# def get_zxy_func(p):
#     if p == 'xy':
#         return order_zxy_mirror_xy
#     if p == 'yz':
#         return order_zxy_mirror_yz


def mirror_ikfk_blend_curve(all_ikfk):
    temps = list()
    for ikfk in all_ikfk:  # 创建镜像temp，右手temp存左手数据
        anim_curves = pm.keyframe(pm.PyNode(ikfk), query=True, name=True)
        if is_lr(ikfk):
            if ikfk.endswith('_L'):
                side_ikfk = re.sub(r"_L$", "_R", str(ikfk))
            else:
                side_ikfk = re.sub(r"_R$", "_L", str(ikfk))
            temp = pm.duplicate(ikfk, parentOnly=1, inputConnections=False, name=side_ikfk + '_temp')[0]
            temps.append(temp)
            for curve in anim_curves:
                pm.cutKey(curve, option="curve")
                pm.pasteKey(temp, option="replaceCompletely")

    for ikfk in all_ikfk:
        if is_lr(ikfk):  # 如果左右对称，拿temp数据，复制曲线
            anim_curves = pm.keyframe(pm.PyNode(ikfk+'_temp'), query=True, name=True)
            for curve in anim_curves:
                pm.cutKey(curve, option="curve")
                pm.pasteKey(pm.PyNode(ikfk), option="replaceCompletely")
    pm.delete(temps)


def mirror_fingers_toes_curve(n_space):
    for rig_name in ['Fingers', 'Toes']:
        finger_lr_temp = list()
        controls = [pm.PyNode(cnt.replace('Shape', '')) for cnt in pm.ls(n_space + rig_name + '*', type='nurbsCurve')]
        if len(controls) != 0:
            for lr_node in controls:
                if is_lr(lr_node):
                    if lr_node.endswith('_L'):
                        side_node = re.sub(r"_L$", "_R", str(lr_node))
                    else:
                        side_node = re.sub(r"_R$", "_L", str(lr_node))
                    rl_node_temp = pm.duplicate(lr_node, parentOnly=1, inputConnections=False, name=side_node + '_temp')[0]
                    anim_curves = pm.keyframe(lr_node, query=True, name=True)
                    for curve in anim_curves:
                        pm.cutKey(curve, option="curve")
                        pm.pasteKey(rl_node_temp, option="replaceCompletely")
                    finger_lr_temp.append(rl_node_temp)

            for temp_node in finger_lr_temp:
                anim_curves = pm.keyframe(temp_node, query=True, name=True)
                lr_node = temp_node.replace('_temp', '')
                if len(anim_curves) == 0:
                    for c in pm.keyframe(pm.PyNode(lr_node), query=True, name=True):
                        pm.delete(c)
                    for temp_attr, new_attr in zip(pm.listAttr(temp_node, userDefined=True, hasData=True, visible=True),
                                                   pm.listAttr(pm.PyNode(lr_node), userDefined=True, hasData=True, visible=True)):
                        pm.PyNode(lr_node).attr(new_attr).set(temp_node.attr(temp_attr).get())
                else:
                    for curve in anim_curves:
                        pm.cutKey(curve, option="curve")
                        pm.pasteKey(pm.PyNode(lr_node), option="replaceCompletely")
            pm.delete(finger_lr_temp)


def check_global_same(shoulder_global_anim_curve):
    pm.keyframe(shoulder_global_anim_curve, )


def get_global_before_data(t, nodes, bake=False):  # 镜像之前必须归0，否则镜像动画会有问题
    global_before_data = dict()
    pm.currentTime(t)
    for shoulder in nodes:
        elbow = shoulder.replace('Shoulder', 'Elbow')
        wrist = shoulder.replace('Shoulder', 'Wrist')
        anim_curves_shoulder = pm.keyframe(pm.PyNode(shoulder), query=True, name=True)
        anim_curves_elbow = pm.keyframe(pm.PyNode(elbow), query=True, name=True)
        anim_curves_wrist = pm.keyframe(pm.PyNode(wrist), query=True, name=True)
        if not bake:
            if any(is_curve_key(t, anim_curves) for anim_curves in [anim_curves_shoulder, anim_curves_elbow, anim_curves_wrist]):
                fk_rt_shoulder = pm.PyNode(shoulder).getMatrix(ws=1)
                fk_rt_elbow = pm.PyNode(elbow).getMatrix(ws=1)
                fk_rt_wrist = pm.PyNode(wrist).getMatrix(ws=1)
                global_before_data[shoulder] = [fk_rt_shoulder, fk_rt_elbow, fk_rt_wrist]
        else:
            fk_rt_shoulder = pm.PyNode(shoulder).getMatrix(ws=1)
            fk_rt_elbow = pm.PyNode(elbow).getMatrix(ws=1)
            fk_rt_wrist = pm.PyNode(wrist).getMatrix(ws=1)
            global_before_data[shoulder] = [fk_rt_shoulder, fk_rt_elbow, fk_rt_wrist]
    return global_before_data


def set_data_after_global(t, frame_global_before_data, value):
    pm.currentTime(t)
    nodes_data = frame_global_before_data[t]
    for shoulder, node_data in nodes_data.items():
        elbow = shoulder.replace('Shoulder', 'Elbow')
        wrist = shoulder.replace('Shoulder', 'Wrist')
        pm.PyNode(shoulder).Global.set(value)
        pm.PyNode(shoulder).setMatrix(node_data[0], ws=1)
        pm.PyNode(elbow).setMatrix(node_data[1], ws=1)
        pm.PyNode(wrist).setMatrix(node_data[2], ws=1)
        pm.setKeyframe(shoulder, time=t)
        pm.setKeyframe(elbow, time=t)
        pm.setKeyframe(wrist, time=t)


def lr_fk_anim_curve_mirror(all_fk):
    temps = list()
    for fk in all_fk:  # 创建镜像temp，右手temp存左手数据
        anim_curves = pm.keyframe(pm.PyNode(fk), query=True, name=True)
        if is_lr(fk):
            if fk.endswith('_L'):
                side_fk = re.sub(r"_L$", "_R", str(fk))
            else:
                side_fk = re.sub(r"_R$", "_L", str(fk))
            temp = pm.duplicate(fk, parentOnly=1, inputConnections=False, name=side_fk + '_temp')[0]
            # temp = pm.group(em=1, n=side_fk + '_temp')
            temps.append(temp)
            for curve in anim_curves:
                pm.cutKey(curve, option="curve")
                pm.pasteKey(temp, option="replaceCompletely")
            anim_curves2 = pm.keyframe(temp, query=True, name=True)
            for curve2 in anim_curves2:
                if any(attr in curve2 for attr in ['translateX', 'translateY', 'translateZ']):
                    set_translate_key_scale(curve2)
    pm.select(temps)
    for fk in all_fk:
        if is_lr(fk):  # 如果左右对称，拿temp数据，复制曲线
            if not pm.objExists(fk+'_temp'):
                continue
            anim_curves = pm.keyframe(pm.PyNode(fk+'_temp'), query=True, name=True)
            for curve in anim_curves:
                pm.cutKey(curve, option="curve")
                pm.pasteKey(pm.PyNode(fk), option="replaceCompletely")
        else:  # 不是左右对称的直接-x -y
            anim_curves = pm.keyframe(pm.PyNode(fk), query=True, name=True)
            for curve in anim_curves:
                if 'translateZ' in curve:
                    set_translate_key_scale(curve)
            set_translate_key_scale(fk + ".rotateX")
            set_translate_key_scale(fk + ".rotateY")
    pm.delete(temps)


def md_other_anim_curve_mirror(root_x_node, hip_swing_node):
    if hip_swing_node:
        set_translate_key_scale(hip_swing_node + ".rotateY")
        set_translate_key_scale(hip_swing_node + ".rotateZ")
    if root_x_node:
        set_translate_key_scale(root_x_node + '.translateX')
        set_translate_key_scale(root_x_node + ".rotateY")
        set_translate_key_scale(root_x_node + ".rotateZ")



def BuildQuat(v0, v1, v2):
    mat = om.MMatrix(((v0.x, v0.y, v0.z, 0), (v1.x, v1.y, v1.z, 0), (v2.x, v2.y, v2.z, 0), (0, 0, 0, 1)))
    return om.MTransformationMatrix(mat).rotation(True)


def MatRow(mat, row):
    return om.MVector(mat.getElement(row, 0), mat.getElement(row, 1), mat.getElement(row, 2))


def MirrorYZRot_LocalYZ(rot):  # rot: mquaternion, pos: mvector
    rot = om.MQuaternion(rot)
    mat = rot.asMatrix()
    v1 = MatRow(mat, 1)
    v2 = MatRow(mat, 2)
    v1.x *= -1
    v2.x *= -1
    v0 = v1 ^ v2
    return BuildQuat(v0, v1, v2)


def set_translate_key_scale(anim_curve):
    all_frames = pm.keyframe(anim_curve, query=True)
    all_values = [-(pm.keyframe(anim_curve, query=True, eval=True, time=(frame, frame))[0]) for frame in all_frames]
    for _frame, _value in zip(all_frames, all_values):
        pm.setKeyframe(anim_curve, time=_frame, value=_value)


def lr_ik_anim_curve_mirror(all_ik):
    temps = list()
    for ik in all_ik:  # 创建镜像temp，右手temp存左手数据
        anim_curves = pm.keyframe(pm.PyNode(ik), query=True, name=True)
        if is_lr(ik):
            if ik.endswith('_L'):
                side_ik = re.sub(r"_L$", "_R", str(ik))
            else:
                side_ik = re.sub(r"_R$", "_L", str(ik))
            temp = pm.duplicate(ik, parentOnly=1, inputConnections=False, name=side_ik + '_temp')[0]
            temps.append(temp)
            # if plane == 'xy':
            for curve in anim_curves:
                if 'swivel' in curve:
                    set_translate_key_scale(curve)
                pm.copyKey(curve, option="curve")
                pm.pasteKey(temp, option="replaceCompletely")
            anim_curves2 = pm.keyframe(temp, query=True, name=True)
            for curve2 in anim_curves2:
                if 'translateX' in curve2:
                    set_translate_key_scale(curve2)
                if 'IKArm' in str(ik):
                    if any(attr in curve2 for attr in ['translateY', 'translateZ']):
                        set_translate_key_scale(curve2)
            if 'IKArm' not in str(ik):
                set_translate_key_scale(temp + '.rotateY')
                set_translate_key_scale(temp + '.rotateZ')

    for ik in all_ik:
        if is_lr(ik):  # 如果左右对称，拿temp数据，复制曲线
            for curve in pm.keyframe(pm.PyNode(ik + '_temp'), query=True, name=True):
                pm.copyKey(curve, option="curve")
                pm.pasteKey(pm.PyNode(ik), option="replaceCompletely")
        else:
            for curve in pm.keyframe(pm.PyNode(ik), query=True, name=True):
                if 'translateX' in curve:
                    set_translate_key_scale(curve)
            set_translate_key_scale(ik + ".rotateX")
            set_translate_key_scale(ik + ".rotateY")
    pm.delete(temps)

    # swivel *= -1
    # 极向量 -tx
    # 控制器 -tx -ry -rz
    # arm 的需要位移全部 *= -1


def is_curve_key(timing, curves):
    for curve in curves:
        if timing in pm.keyframe(curve, query=True):
            return True
    return False
# ↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓tool ui↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓


def get_host_app():
    try:
        main_window = QApplication.activeWindow()
        while True:
            last_win = main_window.parent()
            if last_win:
                main_window = last_win
            else:
                break
        return main_window
    except:
        pass


class nameSpaceDialog(QDialog):

    def __init__(self, parent=None):
        super(nameSpaceDialog, self).__init__(parent)
        self.setWindowTitle(u'请选择需要操作的空间名')
        self.setWindowModality(Qt.ApplicationModal)
        layout = QVBoxLayout()
        self.setLayout(layout)

        h_layout = QHBoxLayout()
        layout.addLayout(h_layout)
        label = QLabel(u'请选择需要操作的角色空间名:')
        label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        h_layout.addWidget(label)
        self.n_space_combo = QComboBox()
        h_layout.addWidget(self.n_space_combo)
        self.loadNameSpace()

        h_layout = QHBoxLayout()
        layout.addLayout(h_layout)
        button = QPushButton(u'确定')
        h_layout.addWidget(button)
        button.clicked.connect(self.confirm)
        button = QPushButton(u'取消')
        h_layout.addWidget(button)
        button.clicked.connect(self.cancel)

    def confirm(self):
        self.accept()
        self.close()

    def cancel(self):
        self.reject()
        self.close()

    def loadNameSpace(self):
        n_spaces = get_name_spaces()
        self.n_space_combo.addItem('')
        for n_space in n_spaces:
            self.n_space_combo.addItem(unicode(n_space))

    def exec_(self):
        super(nameSpaceDialog, self).exec_()
        return str(self.n_space_combo.currentText()), bool(self.result())


class globalValueDialog(QDialog):

    def __init__(self, parent=None):
        super(globalValueDialog, self).__init__(parent)
        self.setWindowTitle(u'请选择开启或关闭')
        self.setWindowModality(Qt.ApplicationModal)
        layout = QVBoxLayout()
        self.setLayout(layout)

        h_layout = QHBoxLayout()
        layout.addLayout(h_layout)
        label = QLabel(u'请选择开启或关闭')
        label.setAlignment(Qt.AlignCenter)
        h_layout.addWidget(label)

        h_layout = QHBoxLayout()
        layout.addLayout(h_layout)
        button = QPushButton(u'开启')
        h_layout.addWidget(button)
        button.clicked.connect(self.confirmOn)
        button = QPushButton(u'关闭')
        h_layout.addWidget(button)
        button.clicked.connect(self.confirmOff)
        button = QPushButton(u'取消')
        h_layout.addWidget(button)
        button.clicked.connect(self.cancel)
        self.value = 0

    def confirmOff(self):
        self.value = 0
        self.accept()
        self.close()

    def confirmOn(self):
        self.value = 10
        self.accept()
        self.close()

    def cancel(self):
        self.reject()
        self.close()

    def exec_(self):
        super(globalValueDialog, self).exec_()
        return self.value, bool(self.result())


class askDialog(QDialog):  # 支持输入的参数为list(), 如[标题，提示内容，True按钮名称，False按钮名称]

    def __init__(self, data, parent=None):
        super(askDialog, self).__init__(parent)
        self.setWindowTitle(data[0])
        self.setWindowModality(Qt.ApplicationModal)
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.value = False

        h_layout = QHBoxLayout()
        layout.addLayout(h_layout)
        label = QLabel(data[1])
        label.setAlignment(Qt.AlignCenter)
        h_layout.addWidget(label)

        h_layout = QHBoxLayout()
        layout.addLayout(h_layout)
        button = QPushButton(data[2])
        h_layout.addWidget(button)
        button.clicked.connect(self.confirmTrue)
        button = QPushButton(data[3])
        h_layout.addWidget(button)
        button.clicked.connect(self.confirmFalse)
        button = QPushButton(u'取消')
        h_layout.addWidget(button)
        button.clicked.connect(self.cancel)
        self.value = 0

    def confirmTrue(self):
        self.value = True
        self.accept()
        self.close()

    def confirmFalse(self):
        self.value = False
        self.accept()
        self.close()

    def cancel(self):
        self.reject()
        self.close()

    def exec_(self):
        super(askDialog, self).exec_()
        return self.value, bool(self.result())


class mirrorTool(QDialog):

    def __init__(self):
        QDialog.__init__(self, get_host_app())
        self.setWindowTitle(u'动画镜像工具')
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.setMinimumWidth(320)
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)

        box = QGroupBox(u'Shoulder Global 切换')
        box.setMinimumWidth(300)
        box.setMaximumWidth(300)
        box.setMinimumHeight(80)
        box.setMaximumHeight(80)
        layout.addWidget(box)
        h_layout = QHBoxLayout()
        box.setLayout(h_layout)

        button = QPushButton(u'切换选择')
        h_layout.addWidget(button)
        button.clicked.connect(self.callGlobalSwitchSelected)
        button = QPushButton(u'切换全部')
        h_layout.addWidget(button)
        button.clicked.connect(self.callGlobalSwitchAll)

        box = QGroupBox(u'镜像动画')
        box.setMinimumWidth(300)
        box.setMaximumWidth(300)
        box.setMinimumHeight(80)
        box.setMaximumHeight(80)
        layout.addWidget(box)
        h_layout = QHBoxLayout()
        box.setLayout(h_layout)
        button = QPushButton(u'镜像所有动画')
        h_layout.addWidget(button)
        button.clicked.connect(self.mirror_all_animation)

    def callGlobalSwitchSelected(self):
        dialog = globalValueDialog(self)
        value, ok = dialog.exec_()
        if ok:
            dialog2 = askDialog([u'是否烘焙Global切换结果', u'是否烘焙切换结果?\n\n如果仅切换后的FK动画错位严重，请尝试烘焙', u'切换并烘焙', u'仅切换'], self)
            bake, ok2 = dialog2.exec_()
            if ok2:
                all_sel = [sel for sel in pm.selected() if 'Shoulder' in str(sel)]
                if len(all_sel) != 0:
                    frame_global_before_data = dict()
                    for t in range(int(round(pm.playbackOptions(q=1, min=1))), int(round(pm.playbackOptions(q=1, max=1))) + 1):
                        frame_global_before_data[t] = get_global_before_data(t, all_sel, bake)
                    for t in range(int(round(pm.playbackOptions(q=1, min=1))), int(round(pm.playbackOptions(q=1, max=1))) + 1):
                        set_data_after_global(t, frame_global_before_data, value)
                    QMessageBox.information(self, u'切换成功', u'切换成功！')
                else:
                    QMessageBox.information(self, u'切换失败', u'未匹配到ShoulderFK控制器，请重新确认！')

    def callGlobalSwitchAll(self):
        dialog = nameSpaceDialog(self)
        n_space, ok = dialog.exec_()
        if ok:
            dialog2 = globalValueDialog(self)
            value, ok2 = dialog2.exec_()
            if ok2:
                dialog3 = askDialog([u'是否烘焙Global切换结果', u'是否烘焙切换结果?\n\n如果仅切换后的FK动画错位严重，请尝试烘焙', u'切换并烘焙', u'仅切换'], self)
                bake, ok3 = dialog3.exec_()
                if ok3:
                    all_sel = [pm.PyNode(shoulder_fk.replace('Shape', '')) for shoulder_fk in pm.ls(type='nurbsCurve')
                               if shoulder_fk.startswith(n_space + 'FK') and not shoulder_fk.startswith(n_space + 'FKIK') and 'Shoulder' in str(shoulder_fk)]
                    if len(all_sel) != 0:
                        # 用于判断shoulder FK上面在所有K帧中是否存在不一样的情况
                        nodes_values_for_warning = list()
                        all_global_anim_curve_frames = [pm.keyframe(shoulder + '.Global', query=True) for shoulder in all_sel]
                        for shoulder, node_global_frames in zip(all_sel, all_global_anim_curve_frames):
                            single_node_values_for_warning = list()
                            for frame in node_global_frames:
                                f_value = pm.keyframe(shoulder + '.Global', query=True, eval=True, time=(frame, frame))[0]
                                single_node_values_for_warning.append(f_value)
                                nodes_values_for_warning.append(f_value)
                            if len(list(set(single_node_values_for_warning))) != 1:
                                pm.select(shoulder)
                                return QMessageBox.information(self, u'切换失败', u'存在global数值不统一的K帧\n已为你选择问题节点'+str(shoulder)+u'\n请检查')
                        if len(list(set(nodes_values_for_warning))) != 1:
                            return QMessageBox.information(self, u'切换失败', u'存在若干个global数值不统一的FK控制器\n请检查')

                        frame_global_before_data = dict()
                        for t in range(int(round(pm.playbackOptions(q=1, min=1))), int(round(pm.playbackOptions(q=1, max=1))) + 1):  # 第一次是拿数据
                            frame_global_before_data[t] = get_global_before_data(t, all_sel, bake)
                        for t in range(int(round(pm.playbackOptions(q=1, min=1))), int(round(pm.playbackOptions(q=1, max=1))) + 1):  # 第二次是给数据
                            set_data_after_global(t, frame_global_before_data, value)
                        QMessageBox.information(self, u'切换成功', u'切换成功！')
                    else:
                        QMessageBox.information(self, u'切换失败', u'当前场景未匹配到ShoulderFK控制器！')

    def loadNameSpace(self):
        self.n_space_combo.clear()
        n_spaces = get_name_spaces()
        self.n_space_combo.addItem('')
        for n_space in n_spaces:
            self.n_space_combo.addItem(unicode(n_space))

    def mirror_all_animation(self):
        dialog = nameSpaceDialog(self)
        n_space, ok = dialog.exec_()
        if ok:

            if str(n_space) == '':
                return QMessageBox.information(self, u'无效的空间名', u'请重新选择空间名！')

            if len(get_all_anim_layer()) > 1:
                return QMessageBox.information(self, u'存在多个动画层', u'请尝试合并动画层后重试！')

            all_sel = [pm.PyNode(shoulder_fk.replace('Shape', '')) for shoulder_fk in pm.ls(type='nurbsCurve')
                       if shoulder_fk.startswith(n_space + 'FK') and not shoulder_fk.startswith(n_space + 'FKIK') and 'Shoulder' in str(shoulder_fk)]
            if len(all_sel) != 0:
                try:
                    all_global_anim_curve_frames = [pm.keyframe(shoulder.Global, query=True) for shoulder in all_sel]
                except AttributeError:
                    all_global_anim_curve_frames = []
                values = list()
                for shoulder, node_global_frames in zip(all_sel, all_global_anim_curve_frames):
                    for frame in node_global_frames:
                        values.append(pm.keyframe(shoulder+'.Global', query=True, eval=True, time=(frame, frame))[0])
                if any(value != 0 for value in values):
                    dialog3 = askDialog([u'发现Global参数不为0', u'发现存在Global参数不为0的K值，镜像动画需要将此值切换为0\n是否烘焙切换结果?\n\n如果仅切换后的FK动画错位严重，请尝试烘焙', u'切换并烘焙', u'仅切换'], self)
                    bake, ok3 = dialog3.exec_()
                    if ok3:
                        frame_global_before_data = dict()
                        for t in range(int(round(pm.playbackOptions(q=1, min=1))),
                                       int(round(pm.playbackOptions(q=1, max=1))) + 1):
                            frame_global_before_data[t] = get_global_before_data(t, all_sel, bake)
                        for t in range(int(round(pm.playbackOptions(q=1, min=1))),
                                       int(round(pm.playbackOptions(q=1, max=1))) + 1):
                            set_data_after_global(t, frame_global_before_data, 0)
                    else:
                        return

            md_other_anim_curve_mirror(get_root_x_by_name_space(n_space), get_hip_swing_by_name_space(n_space))
            lr_fk_anim_curve_mirror(get_fks_by_name_space(n_space))
            mirror_fingers_toes_curve(n_space)
            lr_ik_anim_curve_mirror(get_iks_by_name_space(n_space))
            mirror_ikfk_blend_curve(get_ikfk_blend_by_name_space(n_space))
            pm.currentTime(int(round(pm.playbackOptions(q=1, min=1))))
            QMessageBox.information(self, u'镜像成功', u'镜像成功！')

    def showNormal(self):
        QDialog.showNormal(self)


window = None


def show():
    global window
    if window is None:
        window = mirrorTool()
    window.showNormal()


show()
