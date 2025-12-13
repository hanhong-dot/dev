# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       : s
# Describe   : 发送信息到多维表格
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2023/5/31__16:18
# -------------------------------------------------------
import requests
import json
import datetime

spread_id="DktksCVDchzyMztuPAPcVA4nneg"
# sheet_token="ONcQs5oQ5hRb3kt4CjucNGZYnLh"
# sheet_id='e6e389'
sheet_id="194e3f"

def ReadShotEvent(submitContent):
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal/"
    post_data = {"app_id": "cli_a2424674bdb8d00d", "app_secret": "G8OE1OxvgaMFw3vOcw1IKhx4fToYaMrs"}
    r = requests.post(url, data=post_data)
    tat = r.json()["tenant_access_token"]
    post_data = {
        "valueRange": {
            "range": "{}!A2:C2".format(sheet_id),
            "values": [
                [
                    submitContent,
                    datetime.datetime.now().strftime("%Y-%m-%d-%H:%M:%S")
                ]
            ]
        }
    }
    url = "https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/{}/values_append".format(spread_id)
    header = {"Content-Type": "application/json; charset=utf-8", "Authorization": "Bearer " + str(tat)}
    response = requests.post(url, data=json.dumps(post_data), headers=header)
    if response.status_code == 200:
        __info= response.json()
        if "code" not in __info or __info["code"] != 0:
            print("Error: " + __info.get("msg", "Unknown error"))
            return False, __info.get("msg", "Unknown error")
        elif "data" not in __info or not __info["data"]:
            return False, "No data returned from the API"
        print("Event successfully published to online spreadsheet!" + submitContent)
        return True, response.text
    else:
        print("Failed to publish event to online spreadsheet!" + submitContent)
        return False, response.text

# if __name__ == '__main__':
#     submitContent = {'files': ['M:/projects/X3/publish/assets/role/YS010S/rbf/maya/data/fbx/YS010S_HE_LD.fbx',
#                                'M:/projects/X3/publish/assets/role/YS010S/rbf/maya/data/fbx/YS010S_HD.fbx',
#                                'M:/projects/X3/publish/assets/role/YS010S/rbf/maya/data/fbx/YS010S_FA_HD.fbx',
#                                'M:/projects/X3/publish/assets/role/YS010S/rbf/maya/data/bs/YS010S_LD_Rig.json',
#                                'M:/projects/X3/publish/assets/role/YS010S/rbf/maya/data/fbx/YS010S_LD.fbx',
#                                'M:/projects/X3/publish/assets/role/YS010S/rbf/maya/data/bs/YS010S_HD_Rig.json',
#                                'M:/projects/X3/publish/assets/role/YS010S/rbf/maya/data/fbx/YS010S_HE_HD.fbx',
#                                'M:/projects/X3/publish/assets/role/YS010S/rbf/maya/data/bs/YS010S_HD_asis_Rig.json',
#                                'M:/projects/X3/publish/assets/role/YS010S/rbf/maya/data/fbx/YS010S_FA_LD.fbx'],
#                      'description': u'\u4feeDb\u7684BUG@Danny @\u5c0f\u6ee1 @\u5c0f\u675c @\u535a\u5ca9@\u4e50\u4e50\u5b50@\u806a\u806a@\u674e\u4e91\u9f99',
#                      'upstream_step': 'mod', 'asset_name': u'YS010S', 'person': u'v-xuqing', 'entity_R': u'obt-250925',
#                      'task_name': u'rbf', 'upstream_created_by': 'lihui@papegames.net'}
#     submitContent = str(submitContent)
#     ok, result = ReadShotEvent(submitContent)
#     print(ok, result)


