# -*- coding: utf-8 -*-
# -----------------------------------
# @File    : export_asset_select_thumbnail_excel.py
# @Author  : linhuan
# @Time    : 2025/7/4
# @Description : Export asset list with embedded thumbnail into Excel (xlsxwriter version)
# -----------------------------------
import sys
import os
import datetime
import uuid
from PIL import Image
import xlsxwriter

reload(sys)
sys.setdefaultencoding('utf-8')

sys.path.append('Z:/dev')
import database.shotgun.tools.actionitem.action_item_server as action_item_server
from database.shotgun.fun.get_entity import *


class ExportAssetSelectThumbnailExcel(object):
    def __init__(self):
        self.select_ids = sys.argv[2].split(',')
        self.entity_type = sys.argv[3]
        self.local_dir = get_local_thumbnail_dir('asset_excel_thumbnail')
        if not self.select_ids:
            return

    def export_asset_excel(self):
        print u'start write excel'
        print datetime.datetime.now()
        write_location = get_local_thumbnail_dir('asset_excel_with_thumbnail')
        file_name = uuid.uuid4().hex

        _excel_header = self.__get_excel_header()
        _excel_info = self.__get_info()

        print u'已读取数据, 开始写入excel'
        print datetime.datetime.now()

        excel_file = os.path.join(write_location, file_name + ".xlsx")
        excel_file = excel_file.replace('/', '\\')
        self.__write_excel_xlsx(excel_file, _excel_header, _excel_info)

        print u'已完成写入excel'
        print datetime.datetime.now()
        #需要暂停显示
        if sys.platform == 'win32':
            import ctypes
            ctypes.windll.user32.MessageBoxW(0, u"表格已保存到\n%s" % excel_file, u"提示", 0x40 | 0x1)

    def __get_info(self):
        _excel_info = []
        for entity_id in self.select_ids:
            entity_info = self.__get_info_from_id(entity_id)
            if entity_info:
                _excel_info.append(entity_info)
        return _excel_info

    def __write_excel_xlsx(self, excel_file, _excel_header, _excel_info):
        workbook = xlsxwriter.Workbook(excel_file)
        worksheet = workbook.add_worksheet(self.entity_type)

        center_format = workbook.add_format({
            'align': 'center',
            'valign': 'vcenter'
        })

        for col, header in enumerate(_excel_header):
            worksheet.write(0, col, header.replace(u'资产中文', u'资产中文名'), center_format)

        cell_width = 18.5
        cell_height = 80

        for row_idx, row_data in enumerate(_excel_info, start=1):
            for col_idx, value in enumerate(row_data):
                if col_idx == 2 and value and os.path.exists(value):
                    img_path = value
                    worksheet.set_column(col_idx, col_idx, cell_width)
                    worksheet.set_row(row_idx, cell_height, center_format)
                    with Image.open(img_path) as im:
                        img_width, img_height = im.size

                    target_width = cell_width * 7
                    target_height = cell_height * 0.75
                    scale_x = (float(target_width) / img_width)*1.5
                    scale_y = (float(target_height) / img_height)*1.5
                    scale = min(scale_x, scale_y)

                    x_offset = int((target_width - img_width * scale*0.83) / 2)
                    y_offset = int((target_height - img_height * scale*0.45) / 2)

                    worksheet.insert_image(row_idx, col_idx, img_path, {
                        'x_scale': scale,
                        'y_scale': scale,
                        'x_offset': x_offset,
                        'y_offset': y_offset
                    })
                else:
                    worksheet.set_column(col_idx, col_idx, 20)
                    worksheet.set_row(row_idx, cell_height, center_format)
                    worksheet.write(row_idx, col_idx, self.__cover_code(value), center_format)

        try:
            workbook.close()
            print u"表格已保存到\n%s" % (excel_file.decode('utf-8') if isinstance(excel_file, str) else excel_file)
        except Exception as e:
            print u"表格没有导出成功: %s" % unicode(e)

    def __cover_code(self, _str):
        if isinstance(_str, unicode):
            try:
                return _str.encode('utf-8')
            except:
                return u''
        elif isinstance(_str, str):
            try:
                return _str.decode('utf-8').encode('utf-8')
            except:
                return u''
        return _str

    def __get_info_from_id(self, entity_id):
        filter = [['id', 'is', int(entity_id)]]
        fields = ['id', 'code', 'description']
        entity_info = sg.find_one(self.entity_type, filter, fields)
        code = entity_info['code'] if entity_info else ''
        description = entity_info['description'] if entity_info else ''
        thumbnail = ''
        ok, thumbnail_path = self.__down_thumbnail(entity_id, self.entity_type)
        thumbnail = thumbnail_path if ok else ''
        return [entity_id, code, thumbnail, description]

    def __get_excel_header(self):
        return ['Id', 'Asset Name', 'Thumbnail', u'资产备注']

    def __down_thumbnail(self, entity_id, entity_type):
        sg_handler = BaseGetSgInfo(sg, int(entity_id), entity_type)
        entity_name = sg_handler.get_name()
        imagepath = '{}/{}.png'.format(self.local_dir, entity_name)
        output_path = '{}/{}.png'.format(self.local_dir, entity_name)
        try:
            _thumbnail = sg_handler.download_entity_thumbnail(imagepath)
            if not _thumbnail:
                return False, entity_name
            img = Image.open(_thumbnail).convert('RGB')
            padded = self.__resize_and_pad(img)
            padded.save(output_path)
            return True, output_path
        except:
            return False, entity_name

    def __resize_and_pad(self, img, target_size=(192, 130), bg_color=(200, 200, 200)):
        img = img.copy()
        img.thumbnail(target_size, Image.ANTIALIAS)
        return img


def get_local_thumbnail_dir(addpath=''):
    for drive in ['d:/', 'e:/', 'c:/']:
        path = os.path.join(drive, "Info_Temp", addpath)
        if os.path.exists(drive):
            if not os.path.exists(path):
                os.makedirs(path)
            return path


if __name__ == '__main__':
    sg = action_item_server.action_login()
    ExportAssetSelectThumbnailExcel().export_asset_excel()
