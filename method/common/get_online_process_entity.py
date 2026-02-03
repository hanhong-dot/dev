# -*- coding: utf-8 -*-
# author: linhuan
# file: get_online_process_entity.py
# time: 2026/1/23 16:38
# description:

import requests
import json

SPREAD_ID = 'OS3KwWeuviHYoXkUafjc0efAnQw'
from method.common import judge_online_version_entity


def get_add_tangent_entity_name(title_name=u'线上版本需处理资产'):
    sheets = get_sheets(SPREAD_ID)
    sheet_data = get_sheet_data_by_title(sheets, title_name)
    sheet_id = sheet_data.get('sheet_id', None) if sheet_data else None
    if not sheet_id:
        return []
    range_data = get_range_data(SPREAD_ID, sheet_id, 'A2:A50')
    entity_names = []
    if not range_data or 'data' not in range_data:
        return entity_names
    values = range_data.get('data', []).get('valueRange', []).get("values", [])
    if not values:
        return entity_names
    for value in values:
        if value and len(value) > 0 and value[0]:
            entity_names.append(value[0])
    return entity_names


def get_bs_setting_entity_name(title_name=u'线上版本需处理资产'):
    sheets = get_sheets(SPREAD_ID)
    sheet_data = get_sheet_data_by_title(sheets, title_name)
    sheet_id = sheet_data.get('sheet_id', None) if sheet_data else None
    if not sheet_id:
        return []
    range_data = get_range_data(SPREAD_ID, sheet_id, 'B2:B50')
    entity_names = []
    if not range_data or 'data' not in range_data:
        return entity_names
    values = range_data.get('data', []).get('valueRange', []).get("values", [])
    if not values:
        return entity_names
    for value in values:
        if value and len(value) > 0 and value[0]:
            entity_names.append(value[0])
    return entity_names


def get_online_mod_change_assets():
    return judge_online_version_entity.get_all_online_mod_modify_assets()


def write_online_mod_change_assets_to_spreadsheet(assets, title_name=u'线上版本更新模型资产'):
    # assets= get_online_mod_change_assets()
    # if not assets:
    #     return
    __data = []
    if not assets:
        return
    assets_data = cover_assets_data(assets)
    if not assets_data:
        return
    sheets = get_sheets(SPREAD_ID)
    sheet_data = get_sheet_data_by_title(sheets, title_name)
    sheet_id = sheet_data.get('sheet_id', None) if sheet_data else None
    spread_data = get_spread_data_by_sheet_id(sheet_id, range='A2:B100')
    ___exist_assets_data = []
    if spread_data:
        for data in spread_data:
            if data and len(data) >= 2 and data[0]:
                ___exist_assets_data.append([data[0], data[1]])
    if not ___exist_assets_data:
        __data = assets_data
    else:
        __data = ___exist_assets_data
        for __asset in assets_data:
            if not __asset or len(__asset) < 2:
                continue
            __asset_name = __asset[0]
            __asset_entity_r = __asset[1]
            __is_exist = False
            for i in range(len(__data)):
                __exist_asset = __data[i]
                if not __exist_asset or len(__exist_asset) < 2:
                    continue
                __exist_asset_name = __exist_asset[0]
                if __asset_name == __exist_asset_name:
                    __data[i][1] = __asset_entity_r
                    __is_exist = True
                    break
            if not __is_exist:
                __data.append([__asset_name, __asset_entity_r])
    if ___exist_assets_data:
        end_index = int(len(___exist_assets_data)) + 1
        start_index = 2
        clear_sheet_data_by_rows(SPREAD_ID, sheet_id, start_index, end_index)
    if not __data:
        return
    row_num = len(__data) + 1
    add_sheet_row(SPREAD_ID, sheet_id, row_num)
    __data= __get_data_by_entity_r(__data)

    write_sheet_from_oline_chang_mod_data( SPREAD_ID, sheet_id, __data)


def __get_data_by_entity_r(__data):
    __new_data=[]
    if not __data:
        return __new_data
    for data in __data:
        __entity_r= data[1] if data and len(data)>=2 else ''
        if __entity_r:
            __num= judge_online_version_entity.get_entity_num_by_entity_r(__entity_r)
            if __num is not None:
                __new_data.append((__num, data))
    __new_data= sorted(__new_data, key=lambda x:x[0], reverse=True)
    __final_data=[]
    for item in __new_data:
        __final_data.append(item[1])
    return __final_data



def write_sheet_from_oline_chang_mod_data(spread_id, sheet_id, data, add_num=2):
    if not data:
        return
    sheet_data = []
    for i in range(len(data)):
        if not data[i]:
            continue
        __data = {
            "valueRange": {
                "range": "{}!A{}:B{}".format(sheet_id, i + add_num, i + add_num),
                "values": [
                    data[i]
                ]
            }
        }
        result = write_sheet_data(spread_id, __data)
        sheet_data.append(result)
    return sheet_data


def write_sheet_data(spread_id, data):
    url = "https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/{}/values".format(spread_id)
    headers = {
        "Authorization": "Bearer {}".format(get_token()),
        "Content-Type": "application/json"
    }
    response = requests.request("PUT", url, headers=headers, data=json.dumps(data))
    return response.json()


def add_sheet_row(spread_id, sheet_id, row_num):
    _url = 'https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/{}/dimension_range'.format(spread_id)
    accet_token = get_token()
    headers = {
        "Authorization": "Bearer {}".format(accet_token),
        "Content-Type": "application/json"
    }

    payload = json.dumps(
        {
            "dimension": {
                "sheetId": sheet_id,
                "majorDimension": "ROWS",
                "length": row_num
            }
        }

    )
    response = requests.request("POST", _url, headers=headers, data=payload)
    return response.text


def clear_sheet_data_by_rows(spread_id, sheet_id, start_index, end_index):
    accet_token = get_token()
    _url = "https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/{}/dimension_range".format(spread_id)
    headers = {
        "Authorization": "Bearer {}".format(accet_token),
        "Content-Type": "application/json"
    }
    payload = json.dumps(
        {
            "dimension": {
                "sheetId": sheet_id,
                "majorDimension": "ROWS",
                "startIndex": start_index,
                "endIndex": end_index
            }
        }

    )
    response = requests.request("DELETE", _url, headers=headers, data=payload)
    return response.text


def cover_assets_data(assets):
    __data = []
    if not assets:
        return __data
    for asset in assets:
        __asset_name = asset.get('name', '')
        __entity_r = asset.get('entity_r', '')
        __data.append([__asset_name, __entity_r])
    return __data


def get_spread_data_by_sheet_id(sheet_id, range):
    range_data = get_range_data(SPREAD_ID, sheet_id, range)
    spread_data = []
    if not range_data or 'data' not in range_data:
        return spread_data

    values = range_data.get('data', []).get('valueRange', []).get("values", [])
    if not values:
        return spread_data
    for value in values:
        spread_data.append(value)
    return spread_data


def get_exit_assets_in_spreadsheet(sheet_id):
    exists_assets = []
    range_data = get_range_data(SPREAD_ID, sheet_id, 'A2:A100')
    if not range_data or 'data' not in range_data:
        return exists_assets
    values = range_data.get('data', []).get('valueRange', []).get("values", [])
    if not values:
        return exists_assets
    for value in values:
        if value and len(value) > 0 and value[0]:
            exists_assets.append(value[0])
    return exists_assets


def get_spreadshees_data(spread_id, url="https://open.feishu.cn/open-apis/sheets/v3/spreadsheets", payload=''):
    """
    获取电子表格数据
    :param api: api
    :param spread_id: 电子表格ID
    :return:
    """
    if not url:
        url = "https://open.feishu.cn/open-apis/sheets/v3/spreadsheets"

    _url = "{}/{}/sheets/query".format(url, spread_id)
    accet_token = get_token()
    headers = {
        "Authorization": "Bearer {}".format(accet_token),
        "Content-Type": "application/json"
    }
    response = requests.request("GET", _url, headers=headers, data=payload)
    try:
        return response.json()
    except:
        return None


def get_sheets(spread_id):
    info = get_spreadshees_data(spread_id)
    if info and 'data' in info:
        return info['data']['sheets']
    else:
        return None


def get_token():
    lark_host = "https://open.feishu.cn"
    app_id = "cli_a6a096fab475d00d"
    app_secret = "iWeM9kHoAUnEJeEm1YPrYfxKhHBQcwVv"
    url = "{}/open-apis/auth/v3/tenant_access_token/internal".format(lark_host)
    req = {"app_id": app_id, "app_secret": app_secret}
    payload = json.dumps(req)

    response = requests.request("POST", url, headers={"Content-Type": "application/json"}, data=payload)
    response.raise_for_status()
    return response.json().get('tenant_access_token')


def get_sheet_data_by_title(sheets, title_name):
    if not sheets:
        return None
    for sheet in sheets:
        __title = sheet['title'] if sheet and 'title' in sheet else None
        print(__title)
        if __title and __title == title_name:
            return sheet
    return None


def get_range_data(spread_id, sheet_id, range):
    payload = ""
    _access_token = get_token()

    _headers = {
        'Authorization': 'Bearer {}'.format(_access_token),
        'Content-Type': 'application/json;charset=utf-8'
    }
    url = 'https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/{}/values/{}!{}?valueRenderOption=ToString&dateTimeRenderOption=FormattedString'.format(
        spread_id, sheet_id, range)
    response = requests.request("GET", url, headers=_headers, data=payload)
    __data = response.json()
    return __data


if __name__ == '__main__':
    # print(get_add_tangent_entity_name(title_name=u'线上版本需处理资产'))

    assets = [{'id': 12652, 'entity_r': 'obt-251202', 'name': 'PL018C'},
              {'id': 12734, 'entity_r': 'obt-240311', 'name': 'PL004C'},
              {'id': 13964, 'entity_r': 'obt-241031', 'name': 'PL014S'},
              {'id': 23609, 'entity_r': 'obt-250608', 'name': 'PL017S'},
              {'id': 27986, 'entity_r': 'obt-251231', 'name': 'PL028C'},
              {'id': 28935, 'entity_r': 'obt-240805', 'name': 'YG020C'},
              {'id': 29471, 'entity_r': 'obt-240923', 'name': 'PL040C'},
              {'id': 29472, 'entity_r': 'obt-250812', 'name': 'PL041C'},
              {'id': 31498, 'entity_r': 'obt-250703', 'name': 'PL066C'},
              {'id': 31501, 'entity_r': 'obt-250703', 'name': 'PL069C'},
              {'id': 31502, 'entity_r': 'obt-250703', 'name': 'PL070C'},
              {'id': 31503, 'entity_r': 'obt-250703', 'name': 'PL071C'},
              {'id': 31557, 'entity_r': 'obt-240805', 'name': 'PL073C'},
              {'id': 31670, 'entity_r': 'obt-251030', 'name': 'PL075C'},
              {'id': 33093, 'entity_r': 'obt-240711', 'name': 'YS024C_studio'},
              {'id': 33632, 'entity_r': 'obt-250122', 'name': 'PL080C'},
              {'id': 34223, 'entity_r': 'obt-260210', 'name': 'RY012C_Avg'},
              {'id': 34997, 'entity_r': 'obt-240805', 'name': 'PL073C_Studio'},
              {'id': 35061, 'entity_r': 'obt-250430', 'name': 'PL091C'},
              {'id': 37086, 'entity_r': 'obt-250703', 'name': 'PL019S'},
              {'id': 37683, 'entity_r': 'obt-250703', 'name': 'PL071C_Card'},
              {'id': 38241, 'entity_r': 'obt-250210', 'name': 'PL083C_Card'},
              {'id': 38256, 'entity_r': 'obt-251202', 'name': 'PL020S'},
              {'id': 39689, 'entity_r': 'obt-250430', 'name': 'PL101C'},
              {'id': 39690, 'entity_r': 'obt-250430', 'name': 'PL102C'},
              {'id': 39691, 'entity_r': 'obt-250430', 'name': 'PL103C'},
              {'id': 39692, 'entity_r': 'obt-250430', 'name': 'PL104C'},
              {'id': 39836, 'entity_r': 'obt-250430', 'name': 'PL112C'},
              {'id': 40212, 'entity_r': 'obt-250812', 'name': 'PL604C'},
              {'id': 44007, 'entity_r': 'obt-260210', 'name': 'YG803C'},
              {'id': 44019, 'entity_r': 'obt-260210', 'name': 'PL814C'},
              {'id': 44020, 'entity_r': 'obt-260210', 'name': 'PL814C_Card'},
              {'id': 46990, 'entity_r': 'obt-260210', 'name': 'PL609C'},
              {'id': 46991, 'entity_r': 'obt-260210', 'name': 'ST609C'},
              {'id': 46993, 'entity_r': 'obt-260210', 'name': 'RY609C'},
              {'id': 46995, 'entity_r': 'obt-260210', 'name': 'YG609C'},
              {'id': 47666, 'entity_r': 'obt-260210', 'name': 'ST803C_H'},
              {'id': 57879, 'entity_r': 'obt-260210', 'name': 'PL007C_Studio'}]
    print(write_online_mod_change_assets_to_spreadsheet(assets))
