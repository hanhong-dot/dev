# -*- coding: utf-8 -*-
# author: linhuan
# file: get_online_process_entity.py
# time: 2026/1/23 16:38
# description:

import requests
import json

SPREAD_ID = 'OS3KwWeuviHYoXkUafjc0efAnQw'


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
    print(get_bs_setting_entity_name(title_name=u'线上版本需处理资产'))
