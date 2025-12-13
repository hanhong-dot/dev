# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       : check_body_mat
# Describe   : 检测body ue 任务的材质(材质名+SG节点名)
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2023/5/4__16:49
# -------------------------------------------------------
import lib.common.loginfo as info
import maya.cmds as cmds


class Check(object):
    """
    检查项目当前使用maya软件的相关信息
    """

    def __init__(self, TaskData):
        """
        实例初始化
        """
        # 即使直接派生自object，最好也调用一下super().__init__，
        # 不然可能造成多重继承时派生层次中某些类的__init__被跳过。
        super(Check, self).__init__()
        self.assettype = TaskData.asset_type
        self.task_name = TaskData.task_name

        self.tooltip = u'已检测材质名和SG节点名'

    def checkinfo(self):
        """
        显示检查信息
        :return:
        """
        _error = self.run()
        _error_list = []
        if _error:
            for k, v in _error.items():
                if k == 'error_sg':
                    for i in range(0, len(v), 2):
                        _error_list.append(u"以下SG节点名不正确，请检查(可点修复)")
                        _error_list.append(v[i])
                        _error_list.append(u"正确命名应该为:")
                        _error_list.append(v[i + 1])
                elif k == 'error_mat':
                    for i in range(0, len(v), 2):
                        _error_list.append(u"以下材质球名不正确，请检查(可点修复)")
                        _error_list.append(v[i])
                        _error_list.append(u"正确命名应该为:")
                        _error_list.append(v[i + 1])
                else:
                    _error_list.append(k)
                    _error_list.extend(v)
            return False, info.displayErrorInfo(title=self.tooltip, objList=_error_list)
        else:
            return True, info.displayInfo(title=self.tooltip)

    def run(self):
        if self.assettype in ['body','cartoon_body'] and self.task_name in ['ue_mdl', 'ue_rig', 'ue_final']:
            return self._check_mat()

    def _get_meshs(self):
        """
        获取场景中_UE组下的mesh 节点
        :return:
        """
        _meshs = []
        grps = cmds.ls('*_UE', type='transform')
        if not grps:
            return []
        for grp in grps:
            if not cmds.listRelatives(grp, s=1):
                _trs = cmds.listRelatives(grp, ad=1, type='transform')
                if _trs:
                    for _tr in _trs:
                        if _tr and cmds.listRelatives(_tr, s=1, type='mesh'):
                            _meshs.append(cmds.listRelatives(_tr, s=1, type='mesh', f=1)[0])
        return _meshs

    def _check_mat(self):
        _error = {}
        _meshs = self._get_meshs()
        _error_no_sg = []
        _error_no_shader = []
        _error_more_sg = []
        _error_more_mat = []
        _error_more_sg_sg = []
        _error_more_mat_mat = []
        _error_mat = []
        _error_sg = []
        for mesh in _meshs:
            _mesh_short = cmds.listRelatives(mesh, p=1, f=1)[0].split('|')[-1]
            _sg = cmds.listConnections(mesh, type='shadingEngine')
            if not _sg:
                _error_no_sg.append(mesh)
            elif len(self._set(_sg)) > 1:
                _error_more_sg.append(mesh)
            else:
                _mes = []
                _meshss = list(set(cmds.listConnections(_sg[0], type='mesh')))
                for _mesh in _meshss:
                    _ms = cmds.listRelatives(_mesh, s=1, f=1)
                    if _ms and _ms[0] in _meshs and _ms[0] not in _mes:
                        _mes.append(_ms[0])

                if len(self._set(_mes)) > 1:
                    _error_more_sg_sg.append(_sg[0])
                else:
                    _shader = cmds.listConnections(_sg[0] + '.surfaceShader')
                    if not _shader:
                        _error_no_shader.append(mesh)
                    elif len(self._set(_shader)) > 1:
                        _error_more_mat.append(mesh)

                    else:
                        _sgs = cmds.listConnections(_shader[0], type='shadingEngine')
                        if len(self._set(_sgs)) > 1:
                            _error_more_mat_mat.append(_shader[0])
                        else:
                            _mat = '{}_mat'.format(_mesh_short)
                            _sg_name = '{}_matSG'.format(_mesh_short)
                            if _sg[0] != _sg_name:
                                _error_sg.extend([_sg[0], _sg_name])
                            if _shader[0] != _mat:
                                _error_mat.extend([_shader[0], _mat])
        if _error_no_sg:
            _error[u'以下模型没有连接SG节点,请检查'] = self._set(_error_no_sg)
        if _error_no_shader:
            _error[u'以下模型没有连接材质,请检查'] = self._set(_error_no_shader)
        if _error_more_sg:
            _error[u'以下模型连接了多个SG节点,请检查'] = self._set(_error_more_sg)
        if _error_more_mat:
            _error[u'以下模型连接了多个材质球,请检查'] = self._set(_error_more_mat)
        if _error_more_sg_sg:
            _error[u'以下SG节点连接了多个模型,请检查'] = self._set(_error_more_sg_sg)
        if _error_more_mat_mat:
            _error[u'以下材质球连接了多个SG节点,请检查'] = self._set(_error_more_mat_mat)
        if _error_sg:
            _error['error_sg'] = _error_sg
        if _error_mat:
            _error['error_mat'] = _error_mat
        return _error

    def _set(self, _list):
        try:
            return list(set(_list))
        except:
            return _list

    def fix(self):
        _error = self.run()
        if _error:
            for k, v in _error.items():
                if k in ['error_sg', 'error_mat']:
                    for i in range(0, len(v), 2):
                        cmds.rename(v[i], v[i + 1])


if __name__ == '__main__':
    import method.shotgun.get_task as get_task

    reload(get_task)
    _filename = cmds.file(q=1, exn=1)

    test_task_data = get_task.TaskInfo(_filename, 'X3', 'maya', 'publish')

    #
    #     # print test_task_data.project_soft
    _handle = Check(test_task_data)
    # print(_handle.fix())
    print(_handle._get_meshs())
