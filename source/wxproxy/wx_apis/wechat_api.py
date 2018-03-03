#!/usr/bin/env python
# coding: utf-8

import logging
import re
from common_utils.emoji import emoji_formatter
from common_utils.other import get_r, get_js_r
from common_utils.http import post, get_base_request, get


special_users = [
    'newsapp', 'fmessage', 'filehelper', 'weibo', 'qqmail', 'fmessage',
    'tmessage', 'qmessage', 'qqsync', 'floatbottle', 'lbsapp', 'shakeapp',
    'medianote', 'qqfriend', 'readerapp', 'blogapp', 'facebookapp',
    'masssendapp', 'meishiapp', 'feedsapp', 'voip', 'blogappweixin', 'weixin',
    'brandsessionholder', 'weixinreminder', 'wxid_novlwrv3lqwv11',
    'gh_22b87fa7cb3c', 'officialaccounts', 'notification_messages',
    'wxid_novlwrv3lqwv11', 'gh_22b87fa7cb3c', 'wxitil', 'userexperience_alarm',
    'notification_messages'
]


def parse_contacts(contacts):
    public_users_list = []
    special_users_list = []
    contact_list = []
    group_list = []
    for contact in contacts:
        try:
            contact['NickName'] = emoji_formatter(contact['NickName'])
            contact['RemarkName'] = emoji_formatter(contact['RemarkName'])
            contact['Signature'] = emoji_formatter(contact['Signature'])
        except UnicodeDecodeError:
            logging.warning('ascii codec can\'t decode byte 0xe8 in position 0: %s ordinal not in range(128)'
                           % contact['NickName'])
        if contact['VerifyFlag'] & 8 != 0:  # 公众号/服务号
            public_users_list.append(contact)
        elif contact['UserName'] in special_users:  # 特殊账号
            special_users_list.append(contact)
        elif contact['UserName'].find('@@') != -1:  # 群聊
            group_list.append(contact)
        # elif contact['UserName'] == account['account_id']:  # 自己
        # 有的微信号，联系人里获取不到自己，如ivy
        # contact_list.append(contact)
        else:
            contact_list.append(contact)

    return {
        'public_users_list': public_users_list,
        'special_users_list': special_users_list,
        'contact_list': contact_list,
        'group_list': group_list,
    }


def get_contact(login_info):
    url = login_info[
              'base_uri'] + '/webwxgetcontact?pass_ticket=%s&skey=%s&r=%s' % (
              login_info['pass_ticket'], login_info['skey'], get_r())
    dic = post(url, {})
    if not dic or dic['BaseResponse']['Ret'] != 0:
        logging.error(dic)
        return False
    return dic


def batch_get_contacts(login_info, group_ids, encry_chatroom_id=""):
    if not group_ids:
        return []

    url = login_info['base_uri'] + \
          '/webwxbatchgetcontact?type=ex&r=%s&pass_ticket=%s' % (
              get_r(), login_info['pass_ticket'])
    params = {
        'BaseRequest': get_base_request(**login_info),
        "Count": len(group_ids),
        "List": [{"UserName": group_id,
                  "EncryChatRoomId": encry_chatroom_id} for group_id in group_ids]
    }
    dic = post(url, params)

    if not dic or dic['BaseResponse']['Ret'] != 0:
        logging.error(dic)
        return False

    return dic['ContactList']




