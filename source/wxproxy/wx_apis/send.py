#!/usr/bin/env python
# coding: utf-8
import json
import sys
import logging
import requests

from common_utils.other import get_r
from common_utils.http import get_base_request
from common_utils.control import retry


@retry(3)
def webwxsendmsg(account, content, to='filehelper'):
    login_info = account['login_info']
    url = login_info['base_uri'] + \
          '/webwxsendmsg?pass_ticket=%s' % (login_info['pass_ticket'])
    logging.debug("url : %s " % url)
    msgid = get_r()
    params = {
        'BaseRequest': get_base_request(**login_info),
        'Msg': {
            "Type": 1,
            "Content": content,
            "FromUserName": account['account_id'],
            "ToUserName": to,
            "LocalID": msgid,
            "ClientMsgId": msgid
        }
    }
    logging.debug('params: %s' % params)
    # print(params)
    headers = {'content-type': 'application/json; charset=UTF-8'}
    data = json.dumps(params, ensure_ascii=False).encode('utf8')
    r = requests.post(url, data=data, headers=headers, verify=False)
    return r.json()
