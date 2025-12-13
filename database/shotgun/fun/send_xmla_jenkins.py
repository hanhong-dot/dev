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
def ReadShotEvent(submitContent):
    url= "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal/"
    post_data = {"app_id": "cli_a2424674bdb8d00d", "app_secret": "G8OE1OxvgaMFw3vOcw1IKhx4fToYaMrs"}
    r = requests.post(url, data=post_data)
    tat = r.json()["tenant_access_token"]
    post_data = {
    "valueRange": {
        "range": "e6e389!A2:C2",
        "values": [
        [
            submitContent,
            datetime.datetime.now().strftime("%Y-%m-%d-%H:%M:%S")
        ]
        ]
    }
    }
    url = "https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/ONcQs5oQ5hRb3kt4CjucNGZYnLh/values_append"
    header = {"Content-Type": "application/json; charset=utf-8", "Authorization": "Bearer " + str(tat)}
    response = requests.post(url, data=json.dumps(post_data), headers=header)
    if response.status_code == 200:
       print("事件发布到在线表格成功！" + submitContent)
    else:
       print("事件发布在线表格失败！" + submitContent)

# if __name__ == '__main__':
#     submitContent={'files': u'M:\\projects\\X3\\publish\\assets\\role\\YS009S\\rig\\maya\\data\\fbx\\YS009S_H_LD.fbx', 'person': u'\u8fd0\u6c14', 'description': u'\u6839\u636e\u89e3\u7b97\u53cd\u9988\u4fee\u6539DB\u9aa8\u9abc\u548c\u6743\u91cd'}
#     submitContent=str(submitContent)
#     ReadShotEvent(submitContent)