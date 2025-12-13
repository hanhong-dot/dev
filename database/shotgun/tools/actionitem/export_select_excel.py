# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       : export_excel
# Describe   : 选择导出excel表
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2022/5/29__13:33
# -------------------------------------------------------
import sys
import os


sys.path.append('Z:/dev')

import database.shotgun.core.sg_base as sg_base
import database.shotgun.tools.actionitem.action_item_server as action_item_server

defaultencoding = 'utf-8'
if sys.getdefaultencoding() != defaultencoding:
    reload(sys)
    sys.setdefaultencoding('utf-8')

STEP_ASSET = ['2d', 'rig', 'Art', 'wbx', 'outsource', 'mod', 'Rig', 'u3d', 'rbf', 'fight', 'wtg', 'out', 'ld', 'ue',
              'hair']
STEP_SHOT = ['ani', 'env', 'cfx', 'sfx', 'finalcheck', 'lgt', 'duang', 'layout', 'cts', 'fck']


import xlwt as ExcelWrite


EXCLUDE = STEP_ASSET + STEP_SHOT
import uuid
import datetime


# sys.path.append('')
class ExportExcel(object):
    def __init__(self):
        self.project = sys.argv[1]
        self.select_ids = sys.argv[2].split(',')
        self.entity_type = sys.argv[3]

        self.column_names = sys.argv[4].replace('...', ' ').split(',')
        self.column_ids = sys.argv[5].split(',')
        self.cols = sys.argv[6].split(',')

        self.sg = action_item_server.action_login()

    def write_to_excel(self):
        u"""
        写出到excel表格
        :return: excel 路径
        """
        # excel 文件
        print u'start write excel'
        print datetime.datetime.now()
        write_location = write_local()
        file_name = uuid.uuid4().get_hex()
        # 表头
        _excel_header = self._get_excel_header()
        # 内容
        _excel_info = self._get_info()

        print u'已读取数据,开始写入excel'
        print datetime.datetime.now()


        # if RE == 'openpyxl':
        #     excel_file = os.path.join(write_location, file_name + ".xlsx")
        #     excel_file = excel_file.replace('/', '\\')
        #     self._writ_excel_xlsx(excel_file, _excel_header, _excel_info)
        #
        # else:
        excel_file = os.path.join(write_location, file_name + ".xls")
        excel_file = excel_file.replace('/', '\\')
        self._writ_excel_xls(excel_file, _excel_header, _excel_info)

        print u'已完成写入excel'
        print datetime.datetime.now()

        for i in range(len(_excel_header)):
            if _excel_header[i] =='sg_sequence':
                print _excel_info[i]
        print u'end write excel'
        print datetime.datetime.now()

    def _writ_excel_xls(self, excel_file, _excel_header, _excel_info):
        u"""
        写出到excel表格
        :return: excel 路径
        """
        # 表头
        _excel_header = self._get_excel_header()
        # 内容
        _excel_info = self._get_info()

        #
        xls = ExcelWrite.Workbook(encoding='utf-8')
        # 增加sheet
        sheet = xls.add_sheet(self.entity_type)
        # 添加表头
        header_column = 0
        for header in _excel_header:
            sheet.write(0, header_column, header.replace(u'资产中文', u'资产中文名'))
            header_column += 1
        # 添加表行
        for i in range(len(_excel_info)):
            _column = i + 1
            _col_info = _excel_info[i]
            column = 0
            for j in range(len(_col_info)):
                sheet.write(_column, column, self._cover_code(_col_info[j]))
                column += 1

        try:
            xls.save(excel_file)
            print(u"表格已保存到\n{}".format(excel_file))
        except:
            print(u"表格没有导出成功,请检查")

    def _writ_excel_xlsx(self, excel_file, _excel_header, _excel_info):
        u"""
        导出xlsx文件
        :param excel_file: excel 文件
        :param _excel_header:表头
        :param _excel_info: 内容
        :return:
        """
        # 创建
        xls = openpyxl.Workbook()
        #
        # xls = ExcelWrite.Workbook(encoding='utf-8')
        # sheet 改名
        sheet = xls.active
        sheet.title=self.entity_type
        # 添加表头
        header_column = 1
        for header in _excel_header:
            sheet.cell(1, header_column, header.replace(u'资产中文', u'资产中文名'))
            header_column += 1
        # 添加表行
        for i in range(len(_excel_info)):
            _column = i + 2
            _col_info = _excel_info[i]
            column = 1
            for j in range(len(_col_info)):
                sheet.cell(_column, column, self._cover_code(_col_info[j]))
                column += 1
        # 保存excel
        try:
            xls.save(excel_file)
            print(u"表格已保存到\n{}".format(excel_file))
        except:
            print(u"表格没有导出成功,请检查")

    def _get_info(self):
        u"""
        获得信息
        :return:
        """
        _excel_info = []
        if self.select_ids:
            for i in range(len(self.select_ids)):
                _info_list = []
                for j in range(len(self.column_names)):
                    if self.column_names[j] not in EXCLUDE:
                        _info = self._find_info(self.select_ids[i], self.cols[j])

                        _info_list.append(_info)
                _info_list.insert(0, self.select_ids[i])
                _excel_info.append(_info_list)

        return _excel_info

    def _get_excel_header(self):
        u"""
        获得表头
        """
        _header = []
        if self.column_names:
            for i in range(len(self.column_names)):
                if self.column_names[i] not in EXCLUDE:
                    header_name = self._cover_code(self.column_names[i])
                    if '?' in header_name:
                        _header.extend(header_name.split('?'))
                    else:
                        _header.append(header_name)
        _header.insert(0, 'Id')
        return _header

    def _cover_code(self, _str):
        u"""
        转码(解决中文问题)
        :param _str:
        :return:
        """
        if _str and isinstance(_str, str) == True:
            # _str=(u'{}'.format(_str)).decode("utf8").encode('gbk')
            return _str.decode("utf8", errors='ignore')

    def _find_info(self, _select_id, field):
        u"""
        查找信息
        :param _select_id:
        :param field:
        :return:
        """
        _sg_info = sg_base.select_entity(self.sg, self.entity_type, int(_select_id), fields=[field])
        _info = ''
        if _sg_info and field in _sg_info:
            _info = _sg_info[field]
        if _info and isinstance(_info, list) == True:
            _infon = ''
            for i in range(len(_info)):
                _inf = ''
                if _info[i] and isinstance(_info[i], dict) and 'name' in _info[i]:
                    _inf = _info[i]['name']
                if _info[i] and isinstance(_info[i], str):
                    _inf = _info[i]
                if _inf:
                    if not _infon:
                        _infon = _inf
                    else:
                        _infon = '{},{}'.format(_infon, _inf)
            _info = _infon
        if _info and isinstance(_info, dict) == True:
            if 'name' in _info:
                _info = _info['name']
            if 'code' in _info:
                _info = _info['code']

        return _info


def write_local():
    '''
    获取写入位置
    :return: 返回可写入路径
    '''
    if os.path.exists("d:/"):
        # 查询写入路径
        if os.path.exists("d:/Info_Temp/temp"):
            return "d:/Info_Temp/temp"
        else:
            os.makedirs("d:/Info_Temp/temp")
            return "d:/Info_Temp/temp"

    elif os.path.exists("e:/"):
        # 查询写入路径
        if os.path.exists("e:/Info_Temp/temp"):
            return "e:/Info_Temp/temp"
        else:
            os.makedirs("e:/Info_Temp/temp")
            return "e:/Info_Temp/temp"

    elif os.path.exists("c:/"):
        # 查询写入路径
        if os.path.exists("c:/Info_Temp/temp"):
            return "c:/Info_Temp/temp"
        else:
            os.makedirs("c:/Info_Temp/temp")
            return "c:/Info_Temp/temp"


if __name__ == '__main__':

    ExportExcel().write_to_excel()
