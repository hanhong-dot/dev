# -*- coding: utf-8 -*-#
# Python       : python 2.7.16
# -------------------------------------------------------------------------------
# NAME         : publishwidget
# Describe     : 说明描述
# Version      : v0.01
# Author       : linhuan
# Email        : hanhong@papegames.net
# DateTime     : 2022/5/19__11:40
# -------------------------------------------------------------------------------
# -------------------------------------------------------------------------------
# example:
# 
# -------------------------------------------------------------------------------

__AUTHORZH__ = u"韩虹"
__AUTHOR__ = "linhuan"
__EMAIL__ = "hanhong@papegames.net"

try:
    from PySide2.QtWidgets import *
    from PySide2.QtGui import *
    from PySide2.QtCore import *
except:
    from Qt.QtWidgets import *
    from Qt.QtGui import *
    from Qt.QtCore import *

from functools import partial
import apps.publish.ui.component.baseinfo as _baseinfo
import apps.publish.ui.component.publish_tabwidget as _publish_tabwidget

import apps.publish.ui.component.listwidget as _list
import apps.publish.ui.message.messagebox as _messagebox
import apps.publish.util.analyze_xml as _get_data

import method.shotgun.serversg2 as serversg2

reload(serversg2)
import apps.publish.ui.component.radioitem as _radioitem

import apps.publish.ui.component.checkitem as _checkitem

reload(_checkitem)
import database.shotgun.core.sg_user as user

import method.common.dir as _dir
import lib.common.xmlio as xmlio
import lib.common.timedate as timedate
import method.shotgun.datapack as _datapack

reload(_datapack)

import lib.common.mediainfo as mediainfo

import method.shotgun.task_path as task_path

import method.maya.common.project_info as projectinfo

import apps.publish.util.media as _media

import os, re, threading, time
import method.common.dir as dircommon

import database.shotgun.fun.get_entity as get_entity
import database.shotgun.core.sg_analysis as sg_analysis

sg = sg_analysis.Config().login()

Rig_Tasks = ['drama_rig', 'rbf', 'out_rig', 'fight_rig']


class Append_Signal(QObject):
    Str_Signal = Signal(str)


class PublishWidget(QFrame):
    def __init__(self, task_data, parent=None):
        super(PublishWidget, self).__init__(parent)

        self._task_data = task_data
        self._filename = self._task_data.filename
        # self._project_type = self._task_data.project_type
        self._project_name = self._task_data.project_name
        self._entity_name = self._task_data.entity_name
        self._task_launch_soft = self._task_data.task_launch_soft
        self._asset_type = self._task_data.asset_type
        self.time = timedate.get_currenttime()
        self._analyse_data = _get_data.GetXLMData(self._task_data)
        self.__task_name = self._task_data.task_name
        self._status_list = self._get_status()
        self._status_name = u'任务提交状态选择 : '
        self._special_name = u'文件特殊处理选择:'
        self.__rig_export_fbx_grp_name = u'输出FBX组选择:'
        self._rig_export_fbx_grp_list = []
        self._role_rbf_update_list = [(u'模型迭代'), (u'DB修型迭代')]
        self._role_rbf_updata_label = u'Role Rbf 绑定更新类型选择:'

        if self.__task_name not in Rig_Tasks:
            self._specila_list = [('RigExportMB', u'绑定文件是否输出MB文件'),
                                  ('RigSendJenkins', u'绑定文件是否触发自动化')]

        else:
            self._specila_list = [('RigExportMB', u'绑定文件是否输出MB文件'),
                                  ('RigSendJenkins', u'绑定文件是否触发自动化'),
                                  ('Wbx', u'绑定文件上游环节,是否为Wbx白盒环节')]

        if self.__task_name in Rig_Tasks and self._task_launch_soft == 'maya':
            self._rig_export_fbx_grp_list = self._get_ma_export_fbx_grp_list()

        self._info_data = []
        self._processscrollwidgets = []
        self._processwidgets = []

        if self._analyse_data.get_publishdata()[3]:
            self.sub_widget = self._get_widget(self._analyse_data.get_publishdata()[2])

        self._setup()
        self._publish_button.clicked.connect(self.do_publish)
        # self._workfile = self._get_work_file

    def _setup(self):
        self._baseinfoWidget = _baseinfo.PubInfoWidget(self._task_data, self._get_publishthumbnail())
        # self._statusWidget = _checkitem.CheckItemWidget(self._status_name, self._status_list)
        self._statusWidget = _radioitem.RadioItemWidget(self._status_name, self._status_list)

        self._mbexistWidget = _checkitem.CheckItemWidget(self._special_name, self._specila_list)

        self._rigexoprtgrpWidget = None
        if self._rig_export_fbx_grp_list:
            self._rigexoprtgrpWidget = _checkitem.CheckItemWidget(self.__rig_export_fbx_grp_name,
                                                                  self._rig_export_fbx_grp_list)
            for _grp_check in self._rigexoprtgrpWidget.check_list:
                _grp_check.setChecked(True)

        for _mbexist in self._mbexistWidget.check_list:
            if str(_mbexist.text()) == 'RigExportMB':
                _mbexist.setChecked(True)
            elif str(_mbexist.text()) == 'RigSendJenkins':
                _mbexist.setChecked(False)
            elif str(_mbexist.text()) == 'Wbx':
                _mbexist.setChecked(False)
        self._role_rbf_updata_Widget = _radioitem.RadioItemWidget(self._role_rbf_updata_label,
                                                                  self._role_rbf_update_list)

        self._listwidget = _list.ListWidget()

        self._mb_export = self._get_mb_export()

        self._send_jenkins = self._get_send_jenkins()

        self._wbx = self._get_wbx()

        if self._analyse_data.get_publishdata()[3]:

            self._publsih_tab = _publish_tabwidget.TabWidget(self._task_data, self._analyse_data.get_publishdata()[3],
                                                             self.sub_widget, self._get_processTabname(),
                                                             self._mb_export)
            self._processscrollwidgets = self._publsih_tab.processscrollwidget
            self._processscrollbuttons = self._publsih_tab.processscrollbuttons
        else:
            self._publsih_tab = _publish_tabwidget.TabWidget(self._task_data,
                                                             process_tabname=self._get_processTabname())
            self._processscrollwidgets = self._publsih_tab.processscrollwidget
            self._processscrollbuttons = self._publsih_tab.processscrollbuttons

        self._publish_button = QPushButton()
        self._publish_button.setMinimumHeight(35)
        self._publish_button.setText(u"publish(上传)")

        self._layout = QVBoxLayout(self)
        self._layout.addWidget(self._baseinfoWidget)
        self._layout.addWidget(self._statusWidget)
        self._layout.addWidget(self._mbexistWidget)
        if self._rigexoprtgrpWidget:
            self._layout.addWidget(self._rigexoprtgrpWidget)

        if self._asset_type and ((self._asset_type.lower() == 'role' and self.__task_name == 'rbf') or (self._asset_type.lower() == 'hair' and self.__task_name == 'drama_rig')):
            self._layout.addWidget(self._role_rbf_updata_Widget)
            for _radio in self._role_rbf_updata_Widget._radio_grp.buttons():
                if _radio.text() == u'DB修型迭代':
                    _radio.setChecked(True)
                    self._role_rbf_updata_Widget._get_checkButton(_radio)
        self._layout.addWidget(self._publsih_tab)
        self._layout.addWidget(self._listwidget)
        self._layout.addStretch(0)
        self._layout.addWidget(self._publish_button)
        # self.setMinimumSize(600, 900)

        # processitem信号
        if self._processscrollwidgets:
            for procescrollwidget in self._processscrollwidgets:
                for _processitem in procescrollwidget.get_processwidgets():
                    _processitem._pushbutton1.clicked.connect(partial(self._show_proiteminfo, _processitem))
                    _processitem._pushbutton1.clicked.connect(_processitem.doprocess)
                    _processitem._pushbutton1.clicked.connect(partial(self._show_proiteminfo2, _processitem))
                    _processitem._pushbutton2.clicked.connect(partial(self._process_openlog, _processitem.objectName()))

                    self._processwidgets.append({_processitem: _processitem.objectName()})
            # process_all信号
            if self._processwidgets:
                self._process_alllogname = self._processwidgets[0].values()[0][
                                           :-1] + 'all'
                # _process_allpushbutton
                self._processscrollbuttons[0].clicked.connect(self._show_proallinfo)
                self._processscrollbuttons[0].clicked.connect(self._process_all)
                self._processscrollbuttons[0].clicked.connect(self._show_proallinfo2)
                # _process_allopenlogbutton
                self._processscrollbuttons[1].clicked.connect(self._process_alllog)

    # 创建Tab
    def _get_processTabname(self):
        '''
		获取process Tabname
		:return:
		'''
        if self._analyse_data._get_xml_path('process_config.xml'):
            process_data = xmlio.SelectXML(self._analyse_data._get_xml_path('process_config.xml'))
            process_name = process_data.select_findallattr('process_tab')[0]['tab_name'] if \
                process_data.select_findallattr('process_tab') else None
        else:
            process_name = None
        return process_name

    def _get_widget(self, str_commond):
        '''
		获取sub_widget
		:param str_commond:解析出来的命令
		:return: 返回一个widget
		'''
        _command = str_commond.split(';')[-1]

        _command_new = _command.replace('TaskData', 'self._task_data')

        exec (str_commond[0:len(str_commond) - len(_command)])
        print _command_new
        return eval(_command_new)

    # 获取状态列表
    def _get_status(self):
        return self._analyse_data.get_publishdata()[0]

    def _get_rig_export_fbx_grps(self):
        if self._rigexoprtgrpWidget:
            grp_list = []
            for _grp_check in self._rigexoprtgrpWidget.check_list:
                if _grp_check.isChecked():
                    grp_list.append(str(_grp_check.text()))
            return grp_list
        return []

    # 获取work json 文件
    @property
    def _get_work_jsonfile(self):
        u"""
        获取 work json 文件
        :param TaskData: Task 类
        :return:
        """
        local_dir = dircommon.set_localtemppath('temp_info/work_json')
        if not os.path.exists(local_dir):
            os.makedirs(local_dir)
        _entity_name = self._task_data.entity_name
        _task_name = self._task_data.task_name
        _json_file = u"{}.{}.json".format(_entity_name, _task_name)
        return u"{}/{}".format(local_dir, _json_file)

    @property
    def _get_work_file(self):
        u"""
        获取work 文件
        :return:
        """
        import lib.common.jsonio as jsonio
        try:
            return jsonio.read(self._get_work_jsonfile)['work_file']
        except:
            return

    # process文件处理
    def _show_proiteminfo(self, widget):
        '''
		DCC软件重写  process item 处理按钮触发的第一个槽函数，listwidget显示的首先的信息
		:return:
		'''
        print('item:first')

    # _widget_name = widget.name()
    # self._process_listwidget._listwidget.addItem(_widget_name + ':')

    def _show_proiteminfo2(self, widget):
        '''
		Dcc软件重写 process item 处理按钮触发的最后一个槽函数，listwidget显示的最后的信息
		:return:
		'''
        print('item:last')

    def _show_proallinfo(self):
        '''
		Dcc软件重写 process全部处理按钮触发的第一个槽函数，listwidget显示的第一个信息
		:return:
		'''
        print('all:first')

    def _show_proallinfo2(self):
        '''
		Dcc软件重写  process全部处理按钮触发最后一个槽函数，listwidget显示的最后的信息
		:return:
		'''
        print('all:last')

    def _process_openlog(self, objectname):
        '''
		process item 打开log按钮曹函数
		:param objectname:
		:return:
		'''
        _log = self._processlogfile(objectname)
        try:
            os.startfile(self._exist_processlog(_log))
        except:
            for obj in self._processwidgets:
                if obj.values()[0] == objectname:
                    obj.keys()[0].doprocess()
                    break
            os.startfile(self._exist_processlog(_log))

    def _processlogfile(self, index):
        logname = 'process_' + index + '.log'
        return _dir.get_localtemppath('processInfo/') + logname

    def _exist_processlog(self, file):
        if os.path.exists(file):
            return file
        else:
            raise Exception("Not Found the logfile,please check!!!")

    def _get_ma_export_fbx_grp_list(self):
        from lib.maya.analysis.analyze_config import AnalyDatas
        import maya.cmds as cmds
        fbx_data = AnalyDatas(self._task_data, 'maya_fbx.json').get_datas()
        _grp_list = []

        if not fbx_data:
            return
        _export_fbx_grp_list = []
        for _fbx_data in fbx_data:
            for k, v in _fbx_data.items():
                if k == 'fbx_objs' and v:
                    _export_fbx_grp_list.extend(v)
        if _export_fbx_grp_list:
            _export_fbx_grp_list = list(set(_export_fbx_grp_list))
            for _grp in _export_fbx_grp_list:
                if _grp and cmds.objExists(_grp):
                    _grp_list.append(_grp)
        _grp_new = []
        if _grp_list:
            _grp_list = sorted(_grp_list, key=lambda x: x.lower())
            for _grp in _grp_list:
                _grp_new.append((str(_grp), str(_grp)))
        return _grp_new

    def _process_all(self):
        '''
		处理全部按钮槽函数
		:return:
		'''
        for obj in self._processwidgets:
            _widget = obj.keys()[0]
            _widget.doprocess()

    def _process_alllog(self):
        '''
		 打开全部log处理槽函数
		:return:
		'''
        try:
            os.startfile(self._exist_processlog(self._processlogfile((self._process_alllogname))))
        except:
            self._process_all()
            os.startfile(self._exist_processlog(self._processlogfile((self._process_alllogname))))

    def _get_user(self):
        u"""
        获取当前用户名
        @return:
        """
        return u'{}'.format(self._task_data.current_user_name)

    def _get_assigned_to(self):
        u"""
        获取任务assignedto 人员id
        @return:
        """
        _task_id = self._task_data.task_id
        return get_entity.TaskGetSgInfo(sg, _task_id).get_assigned_to_ids()

    def _get_ass_logins(self):
        u"""
        获取登录名
        :return:
        """
        _user_ids = self._get_assigned_to()
        if _user_ids:
            logins = [self._select_userid_login(_user_id).lower() for _user_id in _user_ids]
            if logins:
                return list(set(logins))

    def _select_userid_login(self, userid):
        u"""
        通过userid 获得user login 登录名
        :param userid:
        :return:
        """
        try:
            return user.select_user_user(sg, userid, user_fields=['login'])['login']
        except:
            return

    def _user_authentication(self):
        u"""

        @return:
        """
        _cur_user = self._get_user().lower()
        _assign = self._get_ass_logins()
        if (_cur_user and _assign and _cur_user in _assign) or _cur_user.lower() in [u'linhuan', u'mengya']:
            return True
        else:
            return False

    def _get_send_jenkins(self):

        if self._mbexistWidget.check_list:
            for _mbexist in self._mbexistWidget.check_list:
                if str(_mbexist.text()) == 'RigSendJenkins':
                    return _mbexist.isChecked()
        return False

    def _get_role_rbf_updata_model(self):
        if self._asset_type and ((self._asset_type.lower() == 'role' and self.__task_name == 'rbf') or (self._asset_type.lower() == 'hair' and self.__task_name == 'drama_rig')):
            check_name = self._role_rbf_updata_Widget._get_checkName()
            if check_name == u'DB修型迭代':
                return '2'
            elif check_name == u'模型迭代':
                return '1'
        return ''

    def _get_wbx(self):
        if self._mbexistWidget.check_list:
            for _mbexist in self._mbexistWidget.check_list:
                if str(_mbexist.text()) == 'Wbx':
                    return _mbexist.isChecked()
        return False

    def _get_mb_export(self):
        if self._mbexistWidget.check_list:
            for _mbexist in self._mbexistWidget.check_list:
                if str(_mbexist.text()) == 'RigExportMB':
                    return _mbexist.isChecked()
        return False

    # publish按钮
    def do_publish(self, ):
        # from lib.common.log import Logger
        # __log_file=r'D:\temp_info\publishInfo\publish.log'
        # __log = Logger(__log_file)

        infolist = []
        # 拖入的version的路径
        _version_src = self._publsih_tab._pictureWidget._get_picData()[0]
        # __log.info(u'publish version src:{}'.format(_version_src))
        # _status=self._statusWidget._get_checkName()
        #
        # if _status and True in _status and 'downstream' in _status[True]:
        # 	_statu='downstream'
        # else:
        # 	_statu=''
        # if not self._publsih_tab._descripWidget._get_desc():
        # 	_messagebox.msgview(u"未输入描述信息，请输入描述信息", 1)
        # 	raise Exception(u"未输入描述信息，请输入描述信息".encode('gbk'))
        # _user_authentication = self._user_authentication()
        # #
        # if not _user_authentication or _user_authentication != True:
        #     _messagebox.msgview(u"这个任务没有分配给你，请联系leader或PM", 1)
        #     raise Exception(u"这个任务没有分配给你，请联系leader或PM".encode('gbk'))

        if not self._statusWidget._get_checkName() or not self._publsih_tab._pictureWidget._get_picData() or not \
                self._publsih_tab._descripWidget._get_desc():
            _messagebox.msgview(u"输入信息不完整,请检查并补全", 1)
            raise Exception(u"输入信息不完整,请重新输入".encode('gbk'))

        self._special_process = self._mbexistWidget._get_checkName()


        # __log.info(u'publish special process:{}'.format(self._special_process))

        self._version_file = _version_src
        self._version_des = os.path.splitext(self._task_data.des_path)[0] + os.path.splitext(_version_src)[-1]

        self._mb_export = self._get_mb_export()
        # __log.info(u'publish mb export:{}'.format(self._mb_export))

        self._send_jenkins = self._get_send_jenkins()
        # __log.info(u'publish send jenkins:{}'.format(self._send_jenkins))

        self._wbx = self._get_wbx()

        self._rig_export_fbx_grp_list = self._get_rig_export_fbx_grps()
        self._role_rbf_udpate_model = self._get_role_rbf_updata_model()

        self.appendSignal = Append_Signal()
        # 获取version的字典
        # 处理缩略图字典
        _mediaprocess = _media.MediaProcess(task_data=self._task_data)

        # 检测视频
        check_result = _mediaprocess.check_media(_version_src)
        if isinstance(check_result, dict):
            if not check_result['status']:
                _messagebox.msgview(check_result['error_msg'], 0)
                raise Exception(check_result['error_msg'])

        # 处理视频
        _mediaprocess.process_media(_version_src)
        # 处理缩略图

        info1 = self._package_thumbnail(_version_src)
        if info1:
            infolist.append(info1)

        # 获取sub_widget传出的字典
        if self._analyse_data.get_publishdata()[3]:
            # sub_widget = self._get_widget(self._analyse_data.get_publishdata()[2])

            sub_dict = self.sub_widget.data()

            if sub_dict:
                if isinstance(sub_dict, dict):
                    for key, value in sub_dict.items():
                        if key == 'version':
                            for obj_dic in value:
                                infolist.append(_datapack.Pack.set_info(
                                    src_path=obj_dic[
                                        'src_path'] if 'src_path' in obj_dic.keys() else _version_src,
                                    des_path=obj_dic['des_path'] if 'des_path' in obj_dic.keys() else
                                    obj_dic[
                                        'des_dir'] + '/' + os.path.basename(_version_src),
                                    description=obj_dic[
                                        'description'] if 'description' in obj_dic.keys() else self._publsih_tab._descripWidget._get_desc(),
                                    status=obj_dic['status'] if 'status' in obj_dic.keys() else
                                    self._statusWidget._get_checkName(),
                                    task_type=obj_dic['task_type'],
                                    task_name=obj_dic['task_name'],
                                    entity_name=obj_dic['entity_name'],
                                    sequence_name=obj_dic[
                                        'sequence_name'] if 'sequence_name' in obj_dic.keys()
                                    else '',
                                    project_name=obj_dic[
                                        'project_name'] if 'project_name' in obj_dic.keys() else
                                    self._task_data.project_name,
                                    file_link_type='upload',
                                    tags='version',
                                    relationship=obj_dic['relationship']
                                ))

                        # elif key in ['publish', 'fbx']:
                        #     for obj_dic in value:
                        #         infolist.append(_datapack.Pack.set_info(
                        #             src_path=obj_dic['src_path'],
                        #             des_path=obj_dic['des_path'],
                        #             down_path=obj_dic['down_path'] if 'down_path' in obj_dic else '',
                        #
                        #             up_path=obj_dic['up_path'] if 'up_path' in obj_dic else '',
                        #             description=obj_dic[
                        #                 'description'] if 'description' in obj_dic.keys() else self._publsih_tab._descripWidget._get_desc(),
                        #             status=obj_dic['status'] if 'status' in obj_dic.keys() else
                        #             self._statusWidget._get_checkName(),
                        #             task_type=obj_dic[
                        #                 'task_type'] if 'task_type' in obj_dic.keys() else self._task_data.entity_type,
                        #             task_name=obj_dic['task_name'] if 'task_name' in obj_dic.keys() else
                        #             self._task_data.task_name,
                        #             entity_name=obj_dic[
                        #                 'entity_name'] if 'entity_name' in obj_dic.keys() else
                        #             self._task_data.entity_name,
                        #             sequence_name=obj_dic[
                        #                 'sequence_name'] if 'sequence_name' in obj_dic.keys() else
                        #             self._task_data.sequence_name,
                        #             project_name=obj_dic[
                        #                 'project_name'] if 'project_name' in obj_dic.keys() else
                        #             self._task_data.project_name,
                        #             tags=key,
                        #             relationship=obj_dic[
                        #                 'relationship'] if 'relationship' in obj_dic.keys() else 0
                        #         ))

                        elif key in ['publish', 'fbx', 'mbfbx', 'mbexfbx', 'mocap', 'ue', 'unityfbx', 'unityxml']:
                            for obj_dic in value:
                                infolist.append(_datapack.Pack.set_info(
                                    src_path=obj_dic['src_path'],
                                    des_path=obj_dic['des_path'],
                                    description=obj_dic[
                                        'description'] if 'description' in obj_dic.keys() else self._publsih_tab._descripWidget._get_desc(),

                                    down_path=obj_dic['down_path'] if 'down_path' in obj_dic else '',
                                    up_path=obj_dic['up_path'] if 'up_path' in obj_dic else '',

                                    status=obj_dic['status'] if 'status' in obj_dic.keys() else
                                    self._statusWidget._get_checkName(),
                                    task_type=obj_dic[
                                        'task_type'] if 'task_type' in obj_dic.keys() else self._task_data.entity_type,
                                    task_name=obj_dic['task_name'] if 'task_name' in obj_dic.keys() else
                                    self._task_data.task_name,
                                    entity_name=obj_dic['entity_name'] if 'entity_name' in obj_dic.keys() else
                                    self._task_data.entity_name,
                                    sequence_name=obj_dic['sequence_name'] if 'sequence_name' in obj_dic.keys() else
                                    self._task_data.sequence_name,
                                    project_name=obj_dic['project_name'] if 'project_name' in obj_dic.keys() else
                                    self._task_data.project_name,
                                    tags=key,
                                    relationship=obj_dic['relationship'] if 'relationship' in obj_dic.keys() else 0,
                                    dcc=self._task_launch_soft,
                                    thumbnail=info1['des_path'] if (
                                            info1 and 'thumbnail' in info1 and 'des_path' in info1) else '',
                                    work_file=obj_dic['work_file'] if 'work_file' in obj_dic.keys() else '',
                                    ref_info=obj_dic['ref_info'] if 'ref_info' in obj_dic.keys() else '',
                                    send_jenkins=self._send_jenkins,
                                    wbx=self._wbx,
                                    updata_model=self._role_rbf_udpate_model

                                ))
                        else:
                            for obj_dic in value:
                                infolist.append(_datapack.Pack.set_info(
                                    src_path=obj_dic['src_path'],
                                    des_path=obj_dic['des_path'],
                                    tags=key))

        # 处理version原图字典
        infolist.append(_datapack.Pack.set_info(
            # src_path = self._get_mediaInfo()[0]
            # des_path=self._get_mediaInfo()[1],
            src_path=_version_src,
            des_path=os.path.splitext(self._task_data.des_path)[0] + os.path.splitext(_version_src)[-1],
            description=self._publsih_tab._descripWidget._get_desc(),
            status=self._statusWidget._get_checkName(),
            task_type=self._task_data.entity_type,
            task_name=self._task_data.task_name,
            entity_name=self._task_data.entity_name,
            sequence_name=self._task_data.sequence_name,
            project_name=self._task_data.project_name,
            file_link_type='upload',
            tags='version',
            relationship=0,
        ))
        # 获取process的字典
        for script_obj in self._analyse_data.get_processcmds():
            _process_dict = self._do_processcmd(script_obj)
            if _process_dict:
                if isinstance(_process_dict, dict):
                    for key, value in _process_dict.items():
                        if key == 'version':
                            for obj_dic in value:
                                infolist.append(_datapack.Pack.set_info(
                                    src_path=obj_dic['src_path'] if 'src_path' in obj_dic.keys() else _version_src,
                                    des_path=obj_dic['des_path'] if 'des_path' in obj_dic.keys() else obj_dic[
                                                                                                          'des_dir'] + '/' + os.path.basename(
                                        _version_src),
                                    description=obj_dic[
                                        'description'] if 'description' in obj_dic.keys() else self._publsih_tab._descripWidget._get_desc(),
                                    status=obj_dic['status'] if 'status' in obj_dic.keys() else
                                    self._statusWidget._get_checkName(),
                                    task_type=obj_dic['task_type'],
                                    task_name=obj_dic['task_name'],
                                    entity_name=obj_dic['entity_name'],
                                    sequence_name=obj_dic['sequence_name'] if 'sequence_name' in obj_dic.keys()
                                    else '',
                                    project_name=obj_dic['project_name'] if 'project_name' in obj_dic.keys() else
                                    self._task_data.project_name,
                                    file_link_type='upload',
                                    tags='version',
                                    relationship=obj_dic['relationship']

                                ))

                        elif key in ['publish', 'fbx', 'mbfbx', 'mbexfbx', 'mocap', 'ue', 'unityfbx', 'unityxml']:
                            for obj_dic in value:
                                infolist.append(_datapack.Pack.set_info(
                                    src_path=obj_dic['src_path'],
                                    des_path=obj_dic['des_path'],
                                    description=obj_dic[
                                        'description'] if 'description' in obj_dic.keys() else self._publsih_tab._descripWidget._get_desc(),

                                    down_path=obj_dic['down_path'] if 'down_path' in obj_dic else '',
                                    up_path=obj_dic['up_path'] if 'up_path' in obj_dic else '',

                                    status=obj_dic['status'] if 'status' in obj_dic.keys() else
                                    self._statusWidget._get_checkName(),
                                    task_type=obj_dic[
                                        'task_type'] if 'task_type' in obj_dic.keys() else self._task_data.entity_type,
                                    task_name=obj_dic['task_name'] if 'task_name' in obj_dic.keys() else
                                    self._task_data.task_name,
                                    entity_name=obj_dic['entity_name'] if 'entity_name' in obj_dic.keys() else
                                    self._task_data.entity_name,
                                    sequence_name=obj_dic['sequence_name'] if 'sequence_name' in obj_dic.keys() else
                                    self._task_data.sequence_name,
                                    project_name=obj_dic['project_name'] if 'project_name' in obj_dic.keys() else
                                    self._task_data.project_name,
                                    tags=key,
                                    relationship=obj_dic['relationship'] if 'relationship' in obj_dic.keys() else 0,
                                    dcc=self._task_launch_soft,
                                    thumbnail=info1['des_path'] if (
                                            info1 and 'thumbnail' in info1 and 'des_path' in info1) else '',
                                    work_file=obj_dic['work_file'] if 'work_file' in obj_dic.keys() else '',
                                    ref_info=obj_dic['ref_info'] if 'ref_info' in obj_dic.keys() else '',
                                    send_jenkins=self._send_jenkins,
                                    wbx=self._wbx,
                                    updata_model=self._role_rbf_udpate_model

                                ))

                        elif key == 'publish_thumbnail':
                            for obj_dic in value:
                                infolist.append(_datapack.Pack.set_info(
                                    src_path=obj_dic['src_path'] if 'src_path' in obj_dic.keys() else info1[
                                        'src_path'],
                                    des_path=obj_dic['des_path'],
                                    tags='thumbnail'))

                        else:
                            for obj_dic in value:
                                infolist.append(_datapack.Pack.set_info(
                                    src_path=obj_dic['src_path'],
                                    des_path=obj_dic['des_path'],
                                    tags=key))

        # 运行

        print(_datapack.Pack.combine(infolist))
        if _datapack.Pack.combine(infolist):
            self.main_pub(_datapack.Pack.combine(infolist))

            self.main_info()

    def _screenshot_thumbnail(self):
        u"""
		截屏到缩略图
		:return:
		"""
        if self._task_launch_soft.lower() == 'maya':
            pass

    def _package_thumbnail(self, path):
        '''
		把拖入的媒体文件转缩略图并打包
		:param path: 媒体文件路径
		:return: 打包的元祖
		'''
        _name = u'{}.jpg'.format(self._entity_name)
        _thumbnall_local = self._get_loacalfile(self._task_data, _name, '/thumbnail')
        _thumbnail_src = ''
        try:
            import lib.common.image as _image
            _thumbnail_src = _image.resize_proportion(path, [0.5, 0.5], _thumbnall_local)
        except:
            try:
                _thumbnail_src = mediainfo.MediaCollect().get_image_from_mov(
                    seconds="1", frames="1", filepath=path,
                    output_name=(os.path.splitext(_thumbnall_local)[0] + '.jpg'))
            except:
                try:
                    import lib.maya.process.image_process as image_process
                    image_process.image_resize(path, None, dst=_thumbnall_local, imgform='jpg')
                    _thumbnail_src = _thumbnall_local
                except:
                    print(u'无法生成缩量图'.encode('gbk'))

        if _thumbnail_src:
            _thumbnail_publish_dir = task_path.SgTaskPath(self._task_data).get_publish_thumbnail()
            return (_datapack.Pack.set_info(
                src_path=_thumbnail_src,
                des_path=_thumbnail_publish_dir + '/' + os.path.basename(_thumbnail_src),
                tags='thumbnail'))
        else:
            return (None, None)

    def _get_loacalfile(self, TaskData, filename, addpath=''):
        '''
		获取存储到本地temp下的文件路径
		:param TaskData:
		:param filename: 文件名
		:param addpath: 补充路径 如 '/data/fbx'
		:return:返回本地的路径
		'''
        _tempdir = ''

        _project = TaskData.project_name
        _dcc = TaskData.task_launch_soft
        _task_type = TaskData.entity_type
        _entity_name = TaskData.entity_name
        _task_name = TaskData.task_name
        _asset_type = TaskData.asset_type
        _task_step = TaskData.step_name
        _shot_name = TaskData.shot_name
        _sequence_name = TaskData.sequence_name
        _entity_type = TaskData.entity_type
        # 本地基础路径
        if _entity_type.lower() == 'asset':
            _tempdir = '{}/assets/{}/{}/{}/{}/{}/work{}/'.format(projectinfo.ProjectInfo(_project).workpath(),
                                                                 _asset_type,
                                                                 _entity_name, _task_step, _task_name, _dcc, addpath)
        if _entity_type.lower() == 'shot':
            _tempdir = '{}/shots/{}/{}/{}/{}/{}/work{}/'.format(projectinfo.ProjectInfo(_project).workpath(),
                                                                _sequence_name, _entity_name,
                                                                _task_step,
                                                                _task_name, _dcc, addpath)

        _tempfile = r"{}{}".format(_tempdir, filename)
        if not os.path.exists(_tempdir):
            os.makedirs(_tempdir)
        return _tempfile

    def _get_publishthumbnail(self):
        '''
		获取publish路径下的缩略图
		:return: 缩略图路径
		'''

        _thumbnail_dir = self._task_data.publish_thubnail
        return self._get_mastername(_thumbnail_dir, '.jpg')

    def _get_mastername(self, _dir, suffix):
        '''
        :param suffix: 后缀，例如：.jpg,.png,.mb
        :return:
        '''
        return dircommon.get_laster_file(_dir, suffix)

    def _do_processcmd(self, cmd):
        if cmd and isinstance(cmd, str):
            _command = cmd.split(';')[-1]
            _getInfo = re.findall(r'[(](.*?)[)]', _command)[0]
            _command_new = _command.replace('TaskData_Class', 'self._task_data').replace('mb_export',
                                                                                         'self._mb_export').replace(
                'version_file', 'self._version_file').replace('export_fbx_grp_list', 'self._rig_export_fbx_grp_list')
            exec (cmd[0:len(cmd) - len(_command)])
            return eval(_command_new)

    def main_pub(self, _dict):
        t = threading.Thread(target=self._onProgress_pub, args=[_dict])
        t.start()

    def _onProgress_pub(self, _dict):
        _user = self._task_data.current_user_name

        serversg2.init_process(_dict, _user, self.time)

    # infowindow
    def main_info(self):
        self._clearInfo()
        threading.Thread(target=self._onProgress_info).start()
        self.appendSignal.Str_Signal.connect(self._ProcessInfo)

    def _ProcessInfo(self, addInfo):
        item = QListWidgetItem()
        item.setText(addInfo)
        if '++' in addInfo:
            item.setTextColor(QColor('red'))
            self._listwidget._listwidget.addItem(item)
        elif 'files to fileSystem is started' in addInfo:
            item.setTextColor(QColor('yellow'))
            self._listwidget._listwidget.addItem(item)
        elif addInfo.startswith('Result :') and re.findall(r"ErrFiles : (.+?) /", addInfo) != ['0']:
            item.setTextColor(QColor('red'))
            self._listwidget._listwidget.addItem(item)
        elif addInfo.startswith('Result :') and re.findall(r"ErrDirs : (.+?)", addInfo) != ['0']:
            item.setTextColor(QColor('red'))
            self._listwidget._listwidget.addItem(item)
        else:
            self._listwidget._listwidget.addItem(item)
        self._listwidget._listwidget.setCurrentRow(self._listwidget._listwidget.count() - 1)

    def _onProgress_info(self):
        logfile = _dir.get_localtemppath('publishInfo/') + 'publish_' + self.time + '.log'
        while True:
            if os.path.exists(logfile):
                if self._read_log(logfile):
                    break

    def _up_down_info(self):
        logfile = _dir.get_localtemppath('publishInfo/') + 'up_down_' + self.time + '.log'
        while True:
            if os.path.exists(logfile):
                if self._read_log(logfile):
                    break

    def _read_log(self, logfile):
        _line_list = []
        while True:
            for line in open(logfile):
                if line not in self._info_data:
                    self._info_data.append(line)
                    time.sleep(0.1)
                    self.appendSignal.Str_Signal.emit(line.decode('gbk'))
                    if line:
                        if '*Upload All infos to shotgun has failed*' in line.decode(
                                'gbk') or '*Upload All infos to shotgun has succeeded*' in line.decode(
                            'gbk'):
                            _line_list.append(line)
                            self.appendSignal.Str_Signal.emit(
                                u'"------------------------------*已上传信息,请注意查看*-------------------------------"')
                            return True

    def _clearInfo(self):
        self._listwidget._clear_info()


def messagebox(x=""):
    u"""
    弹出
    """
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Information)
    msg.setText("{}".format(x))
    msg.setInformativeText("messageb box")
    msg.setWindowTitle("info message")
    msg.exec_()


if __name__ == '__main__':
    import sys
    import method.shotgun.get_task as get_task

    _filename = 'PL008S.rbf.v008.ma'
    task_data = get_task.TaskInfo(_filename, 'X3', 'maya', 'publish')
    # task_data= get_task.TaskInfo('photostudio_kraftbag_001.drama_rig.v007.ma', 'X3', 'maya', 'publish')

    if QApplication.instance() is not None:
        app = QApplication.instance()
    else:
        app = QApplication(sys.argv)
    win = PublishWidget(task_data)

    win.show()

    # In Maya, the Qt event loop is already running; calling app.exec_() here can
    # block Maya and `sys.exit()` will raise SystemExit in the script editor.
    try:
        import maya.cmds as _maya_cmds  # noqa: F401

        _in_maya = True
    except Exception:
        _in_maya = False

    if not _in_maya:
        sys.exit(app.exec_())
# #
# # _dict={'publish': [{
# #                  'up_path': u'Y:/projects/X3/publish/assets/rolaccesory/tdtest_roleacce/mod/maya/tdtest_roleacce.drama_mdl.v015.ma',
# #                  u'des_path': u'Y:/projects/X3/publish/assets/rolaccesory/tdtest_roleacce/mod/maya/tdtest_roleacce.drama_mdl.v015.ma',
# #                  u'src_path': 'Y:/projects/X3/work/assets/rolaccesory/tdtest_roleacce/mod/maya/tdtest_roleacce.drama_mdl.v015.ma',
# #                  'down_path': u'Y:/projects/X3/publish/assets/rolaccesory/tdtest_roleacce/mod/maya/tdtest_roleacce.drama_mdl.v015.ma'}]}
#
# #    infolist=[{'des_path': u'Y:/projects/X3/publish/assets/npc/common_fish_001/rig/thumbnail/common_fish_001.drama_rig.v003.jpg',
# #  'src_path': 'D:/temp_info/X3/assets/npc/common_fish_001/rig/drama_rig/maya/work/thumbnail/common_fish_001.drama_rig.v003.jpg',
# #  'upload_type': 'thumbnail'},
# # {'dcc': None,
# #  'des_path': u'Y:/projects/X3/publish/assets/npc/common_fish_001/rig/maya/common_fish_001.drama_rig.v003.png',
# #  'description': u'test',
# #  'down_path': None,
# #  'entity_name': u'common_fish_001',
# #  'episode_name': None,
# #  'file_link_type': 'upload',
# #  'project_name': 'X3',
# #  'relationship': 0,
# #  'sequence_name': None,
# #  'src_path': u'Y:/projects/x3/publish/assets/npc/common_fish_001/rig/maya/common_fish_001.drama_rig.v002.png',
# #  'status': u'ip',
# #  'tags': 'version',
# #  'task_name': u'drama_rig',
# #  'task_thumbnail': None,
# #  'task_type': 'asset',
# #  'up_path': None,
# #  'upload_type': 'version'},
# # {'dcc': 'maya',
# #  'des_path': u'Y:/projects/X3/publish/assets/npc/common_fish_001/rig/maya/common_fish_001.drama_rig.ma',
# #  'description': u'test',
# #  'down_path': u'Y:/projects/X3/publish/assets/npc/common_fish_001/rig/maya/common_fish_001.drama_rig.ma',
# #  'entity_name': u'common_fish_001',
# #  'episode_name': None,
# #  'file_link_type': 'local',
# #  'project_name': 'X3',
# #  'publish_file_type': 'Maya Scene',
# #  'relationship': 0,
# #  'sequence_name': None,
# #  'src_path': 'Y:/projects/X3/work/assets/npc/common_fish_001/rig/maya/common_fish_001.drama_rig.ma',
# #  'status': u'ip',
# #  'tags': 'publish',
# #  'task_name': u'drama_rig',
# #  'task_thumbnail': None,
# #  'task_type': 'asset',
# #  'up_path': u'Y:/projects/X3/publish/assets/npc/common_fish_001/rig/maya/common_fish_001.drama_rig.ma',
# #  'upload_type': 'publish'}]
# #    _dict=_datapack.Pack.combine(infolist)
# #    print(_dict)
