# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       : batch_check
# Describe   : 说明描述
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2023/12/30__18:04
# -------------------------------------------------------
import apps.publish.util.analyze_xml as _get_data
import lib.common.loginfo as info


def batch_check(task_data):
    check_data = _get_data.GetXLMData(task_data).get_checkdata()
    error_list = []
    ignore_error_list = []
    if check_data:
        for i in range(len(check_data)):
            if 'check_command' in check_data[i]:
                check_common = check_data[i]['check_command']
                _command = check_common.split(';')[-1]
                _command_new = _command.replace('TaskData_Class', 'task_data')
                exec (check_common[0:len(check_common) - len(_command)])

                _result, _info = eval(_command_new)
                # print(_result, _info)
                # print('type:', type(_info))

                # _info=unicode_to_chinese(_info)

                if _result is False:
                    if check_data[i].get('ignore') == "True":
                        ignore_error_list.append(_info)
                    else:
                        error_list.append(_info)
    if error_list:
        return False, error_list
    else:
        return True, ignore_error_list
def to_unicode(s):
    if isinstance(s, unicode):
        return s
    elif isinstance(s, str):
        return s.decode('utf-8', 'ignore')
    else:
        return unicode(s)

def unicode_to_chinese(text):
    if not text:
        return text
    try:
        if text.startswith("u'") or text.startswith('u"'):
            text = text[2:-1]
        return text.encode('utf-8').decode('unicode_escape')
    except Exception:
        return text
def batch_check_info(task_data):
    ok, result = batch_check(task_data)
    if ok == False and result:
        return False, result
    if ok and result:
        return True, result
    return ok, result


