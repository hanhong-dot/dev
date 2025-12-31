# -*- coding: utf-8 -*-
# author: linhuan
# file: check_glass_skin_weight.py
# time: 2025/12/31 11:34
# description:
import maya.cmds as cmds
import lib.common.loginfo as info
import lib.maya.analysis.analyze_structure as structure

reload(structure)
import database.shotgun.fun.get_entity as get_entity
import database.shotgun.core.sg_analysis as sg_analysis

reload(get_entity)
#

CHECKJOINT = 'AP_Face_Glass'


class Check(object):

    def __init__(self, TaskData):
        super(Check, self).__init__()

        self._taskdata = TaskData
        self.__entity_type = self._taskdata.entity_type
        self.__entity_id = self._taskdata.entity_id
        self.__entity_name = self._taskdata.entity_name
        self.__task_id= self._taskdata.task_id
        self._asset_type = self._taskdata.asset_type
        self.__sg = sg_analysis.Config().login()
        self._asset_level = get_entity.BaseGetSgInfo(self.__sg, self.__entity_id, self.__entity_type).get_asset_level()
        self.analyze_handle = structure.AnalyStrue(self._taskdata)
        self.structure = self.analyze_handle.get_structure()
        self._structure = self._get_structure
        self.__tooltip = u'开始检测pl配饰骨骼权重'
        self.__err = u"以下骨骼与女主模型没有有效蒙皮权重,请检查"
        self.__end = u'已检测pl配饰骨骼权重'

    def checkinfo(self):
        __errors = self.run()
        if __errors:
            return False, info.displayErrorInfo(title=self.__err, objList=__errors)
        else:
            return True, info.displayInfo(title=self.__tooltip, objList=[self.__end])

    def run(self):
        __error = []
        if self._asset_type not in ['rolaccesory']:
            return __error
        __task_text = self._get_task_text()
        if u'眼镜标记' not in __task_text:
            return __error
        mod_grps_meshs = self._get_mod_grps_meshs()
        if not mod_grps_meshs:
            return __error
        __skin_meshs=[]
        if not mod_grps_meshs:
            return __error
        if not cmds.ls(CHECKJOINT, type='joint'):
            __error.append(u'场景中没有{}骨骼,请检查'.format(CHECKJOINT))
            return __error
        for mesh in mod_grps_meshs:
            try:
                skin_cluster = cmds.skinCluster(mesh, inf=CHECKJOINT, q=True, dr=True)
                if skin_cluster:
                    __skin_meshs.append(mesh)
            except:
                pass
        if not __skin_meshs:
            __error.append(u'配饰模型没有关联{}骨骼的蒙皮权重,请检查'.format(CHECKJOINT))
            return __error
        return __error




    def _get_task_text(self):
        fields = ['sg_text']
        filters = [
            ['id', 'is', self.__task_id]
        ]
        task= self.__sg.find_one('Task', filters, fields)
        if task and 'sg_text' in task:
            return u'{}'.format(task['sg_text'])
        return ''



    def _judge_empty_joint(self, joint, meshs):
        joint_mesh = []
        if joint and meshs:
            for mesh in meshs:
                try:
                    result = cmds.skinCluster(mesh, inf=joint, q=True, dr=True)
                    if result:
                        joint_mesh.append(mesh)
                except:
                    pass
        if joint_mesh:
            return True
        else:
            return False

    def _get_mod_grps_meshs(self):
        mesh_list = []
        mod_grps = self._get_grps_structure(self._structure)
        if mod_grps:
            for mod_grp in mod_grps:
                if mod_grp and cmds.ls(mod_grp, type='transform'):
                    meshs = cmds.listRelatives(mod_grp, ad=1, type='mesh', f=1)
                    if meshs:
                        trs = cmds.listRelatives(meshs, p=1, f=1)
                        if trs:
                            for tr in trs:
                                if tr and tr not in mesh_list:
                                    mesh_list.append(tr)
        return mesh_list

    def _get_grps_structure(self, structure):
        mod_grps = []
        if isinstance(structure, dict):
            for k, v in structure.items():
                k = cmds.ls(k)
                if not k:
                    continue
                k = k[0]
                if isinstance(v, list):
                    for _v in v:
                        if isinstance(_v, str) or isinstance(_v, unicode):
                            objs = cmds.ls('{}|{}'.format(k, _v))
                            if objs:
                                mod_grps.extend(objs)
                        elif isinstance(_v, dict):
                            mod_grps.extend(self._get_grps_structure(_v))
                elif isinstance(v, str) or isinstance(v, unicode):
                    objs = cmds.ls(v)
                    if objs:
                        mod_grps.extend(objs)
                elif isinstance(v, dict):
                    mod_grps.extend(self._get_grps_structure(v))
        if isinstance(structure, str) or isinstance(structure, unicode):
            objs = cmds.ls(structure)
            if objs:
                mod_grps.extend(objs)
        if isinstance(structure, list):
            for _v in structure:
                if isinstance(_v, str) or isinstance(_v, unicode):
                    objs = cmds.ls(_v)
                    if objs:
                        mod_grps.extend(objs)
                elif isinstance(_v, dict):
                    mod_grps.extend(self._get_grps_structure(_v))
        return mod_grps

    @property
    def _get_structure(self):
        u"""
        获取结构
        :return:
        """
        structure = self.structure

        if (not self._asset_level or self._asset_level < 1) and isinstance(structure,
                                                                           dict) and 'level_0' in self.structure:
            return structure['level_0']
        elif self._asset_level and self._asset_level > 0:
            _key = 'level_{}'.format(self._asset_level)
            if _key and _key in structure:
                return structure[_key]
            elif 'level_0' in structure:
                return structure['level_0']
            else:
                return structure

        else:
            return structure

if __name__ == '__main__':
    import method.shotgun.get_task as get_task

    _filename =cmds.file(q=True,exn=True)

    taskdata = get_task.TaskInfo(_filename, 'X3', 'maya', 'version')
    handle = Check(taskdata)

    print(handle.run())