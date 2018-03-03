# coding: utf-8

import random
import time
import re
import sys
import json
import os
from common_utils.file import save_file
from common_utils.http import post, get, decode_dict
from common_utils.log import init_logging
from common_utils.other import get_r, str2qr, get_js_r
from common_utils.webweixin_exceptions import WeChatLoginException, WeChatOnlineException, PhoneExitException, \
    PhoneLogoutException, AnotherLoginException, SyncCheckException, RetCodeUnknownException
from wxproxy.wx_apis.wechat_api import get_contact, parse_contacts, batch_get_contacts
import xml.dom.minidom
from http.cookiejar import CookieJar
from urllib import parse, request
from wxproxy.handler.msg_handler import handle_msg

logger = init_logging('WeChat')


class WebWeChat:
    def __init__(self, tai_id, uin, name, status_obj=None, **kwargs):
        self.tai_id = tai_id
        self.uin = uin
        self.given_uin = uin
        self.name = name  # supposed to be a user specified webot name, not account's nick_name
        self.status_obj = status_obj
        self.exit_flag = False
        self.qr_fn = ''
        self.DEBUG = False
        self.uuid = ''
        self.base_uri = ''
        self.wx_server_domain = ''  # Eg.: https://wx2.qq.com  登录成功时获取
        self.sync_uri = ''  # 登录成功时获取
        self.file_uri = ''  # 登录成功时获取
        self.uin = ''  # 登录成功时获取
        self.sid = ''  # 登录成功时获取
        self.skey = ''  # 登录成功时获取
        self.pass_ticket = ''  # 登录成功时获取
        self.deviceid = 'e' + repr(random.random())[2:17]
        self.BaseRequest = {}  # 登录成功时获取
        self.synckey = ''
        self.SyncKey = []
        self.account = {}
        self.user_agent = 'Mozilla/5.0 (Macintosh; Intkwargsel Mac OS X 10_11_3) AppleWebKit/537.36 ' \
                          '(KHTML, like Gecko) Chrome/48.0.2564.109 Safari/537.36'
        self.appid = 'wx782c26e4c19acffb'
        self.lang = 'zh_CN'

        self.additional_kwargs = kwargs
        self.cookies = CookieJar()
        opener = request.build_opener(request.HTTPCookieProcessor(self.cookies))
        opener.addheaders = [('User-agent', self.user_agent)]
        request.install_opener(opener)

    def login(self):
        """
        steps : 1.获取UUID
                2.生成qrcode
                3.等待用户扫描qrcode
                4.获取请求所需的基本参数
        :return:
        """
        self.uuid = self.get_uuid()
        self.build_qr_code()
        redirect_uri = self.waiting_to_login()
        self.init_wx_login_page(redirect_uri)

    # 获取base_request
    def init_wx_login_page(self, redirect_uri):
        if not redirect_uri:
            raise WeChatLoginException('get the redirect url of wechat\'s login page error...')
        data = get(redirect_uri)
        if data == '':
            return False
        doc = xml.dom.minidom.parseString(data)
        root = doc.documentElement

        for node in root.childNodes:
            if node.nodeName == 'skey':
                self.skey = node.childNodes[0].data
            elif node.nodeName == 'wxsid':
                self.sid = node.childNodes[0].data
            elif node.nodeName == 'wxuin':
                self.uin = node.childNodes[0].data
            elif node.nodeName == 'pass_ticket':
                self.pass_ticket = node.childNodes[0].data

        if '' in (self.skey, self.sid, self.uin, self.pass_ticket):
            raise WeChatLoginException('get base_request params error ...')
        self.BaseRequest = {
            'Uin': int(self.uin),
            'Sid': self.sid,
            'Skey': self.skey,
            'DeviceID': self.deviceid,
        }
        return True

    # 获取UUID
    def get_uuid(self):
        url = 'https://login.weixin.qq.com/jslogin'
        params = {
            'appid': self.appid,
            'fun': 'new',
            'lang': self.lang,
            '_': get_r(),
        }
        data = post(url, params, False).decode()
        if data == '':
            return
        regx = r'window.QRLogin.code = (\d+); window.QRLogin.uuid = "(\S+?)"'
        pm = re.search(regx, data)
        if pm and pm.group(1) == '200':
            return pm.group(2)

    # todo  这块代码应该放在其他地方
    # 生成二维码
    def build_qr_code(self):
        # todo  how to send this qr_img to web client is a problem ?
        if not self.uuid:
            raise WeChatLoginException('get uuid failed ...')
        url = 'https://login.weixin.qq.com/qrcode/' + self.uuid
        str2qr(url)  # are you sure to print qrcode ?
        params = {'t': 'webwx', '_': get_r()}
        qr_img_data = post(url, params, False)
        self.qr_fn = '%s-%s.jpg' % (self.uuid, str(time.time()))
        file = save_file('/tmp', self.qr_fn, qr_img_data)
        if sys.platform.startswith('win'):
            os.startfile(file)

    def waiting_to_login(self, step=1):
        if step == 1:
            logger.info('waiting for WeChat to scan two dimensional code login...')
        else:
            logger.info('Wait for mobile phone confirmation...')
        url = 'https://login.weixin.qq.com/cgi-bin/mmwebwx-bin/login?tip=%s&uuid=%s&r=%s&_=%s' % (
            0, self.uuid, get_js_r(), get_r())
        data = str(get(url))
        logger.debug(data)
        pm = re.search(r'window.code=(\d+);', data)
        code = pm.group(1)

        # 如果返回码为201 表示还处于等待扫描状态
        if code == '201':
            return self.waiting_to_login()
        elif code == '200':
            pm = re.search(r'window.redirect_uri="(\S+?)";', data)
            r_uri = pm.group(1) + '&fun=new'
            self.base_uri = r_uri[:r_uri.rfind('/')]
            pm = re.search(r'([\S]+)/cgi-bin/', self.base_uri)
            self.wx_server_domain = pm.group(1)
            self.file_uri, self.sync_uri = get_wx_uri(self.base_uri)
            return r_uri
        elif code == '408':
            return self.waiting_to_login(step=2)
        else:
            # 大概12次超时后，登录异常 400
            logger.warning('login error ... %s' % code)
        return False

    def online(self):
        """
        steps:  1.获取登录用户信息
                2.拉取联系人
                3.拉取群
                4.todo  信息的存储
        :return:
        """
        user = self.init_user_info()
        logger.debug('user: %s' % user)
        login_info = {
            'base_uri': self.base_uri,
            'sid': self.sid,
            'uin': self.uin,
            'skey': self.skey,
            'pass_ticket': self.pass_ticket,
            'deviceid': self.deviceid
        }
        self.account['login_info'] = login_info
        self.account['account_id'] = user['UserName']
        contacts_data = get_contact(login_info)
        logger.debug(contacts_data)
        members = parse_contacts(contacts_data['MemberList'])
        logger.debug('user\' contacts list:  %s ' % members)
        public_users_list = members['public_users_list']
        special_users_list = members['special_users_list']
        contact_list = members['contact_list']
        group_list = members['group_list']
        logger.info('[*] all of %s contacts，get %d ' %
                    (contacts_data['MemberCount'], len(contacts_data['MemberList'])))
        logger.info('[*] all of %d group | %d contact | %d special_user ｜ %d public_user' %
                    (len(group_list), len(contact_list),
                     len(special_users_list), len(public_users_list)))

        def pull_contact_list(member_list):
            for member in member_list:
                logger.info('pull a member named: %s ' % member['NickName'])

        def handle_group(group):
            logger.info('try to pull the group named: %s' % group['NickName'])
            detailed_member_list = batch_get_contacts(login_info,
                                                      [member['UserName'] for member in group['MemberList']],
                                                      group.get('EncryChatRoomId', ''))
            pull_contact_list(detailed_member_list)

        pull_contact_list(special_users_list)
        pull_contact_list(contact_list)
        pull_contact_list(public_users_list)

        group_ids = {group['UserName'] for group in group_list}
        logger.debug('group_ids: %s' % group_ids)
        if group_ids:
            logger.debug('readying for pull group\'s information...')
            groups = batch_get_contacts(login_info, group_ids)
            if not groups:
                raise WeChatOnlineException('failed to pull group\'s contacts ...')
            for i, group in enumerate(groups, 1):
                handle_group(group)

    def init_user_info(self):
        url = self.base_uri + '/webwxinit?pass_ticket=%s&skey=%s&r=%s' % (
            self.pass_ticket, self.skey, get_js_r())
        params = {'BaseRequest': self.BaseRequest}
        dic = post(url, params)
        if not dic or dic['BaseResponse']['Ret'] != 0:
            raise WeChatOnlineException('get user dic failed...')
        self.SyncKey = dic['SyncKey']
        return dic['User']

    def running(self):
        count = 0
        while not self.exit_flag and count < 3:
            [retcode, selector] = self.sync_check()
            if retcode == '0':
                count = 0
                if selector == '0':
                    continue

                logger.info('retcode: %s, selector: %s' % (retcode, selector))
                r = self.web_wx_sync()
                if not r:
                    # 此时sync 失败，synccheck 会死循环 重新初始化 or login?
                    logger.warning('webwxsync 返回为空，尝试重新初始化...')
                    self.init_user_info()
                else:
                    # 不使用队列，同步
                    # handle_msg(self.account, r)

                    # 使用队列，异步
                    handle_msg(self.account, self.tai_id, r)
            else:
                if retcode == '1100':
                    raise PhoneLogoutException
                elif retcode == '1101':
                    raise AnotherLoginException
                elif retcode == '1102':
                    raise PhoneExitException
                elif retcode == -1:
                    raise SyncCheckException
                else:
                    raise RetCodeUnknownException(retcode, selector)

            count += 1
            time.sleep(count * 2)
            continue

    def sync_check(self):
        params = {
            'r': get_r(),
            'sid': self.sid,
            'uin': self.uin,
            'skey': self.skey,
            'deviceid': self.deviceid,
            'synckey': self.synckey,
            '_': get_r()
        }
        url = 'https://' + self.sync_uri + \
              '/cgi-bin/mmwebwx-bin/synccheck?' + parse.urlencode(params)
        data = str(get(url))
        logger.debug('get a data : %s:' % data)
        if data == '':
            return [-1, -1]
        pm = re.search(r'window.synccheck={retcode:"(\d+)",selector:"(\d+)"}', data)
        retcode = pm.group(1)
        selector = pm.group(2)
        return [retcode, selector]

    def web_wx_sync(self):
        url = self.base_uri + '/webwxsync?sid=%s&skey=%s&pass_ticket=%s' % (
            self.sid, self.skey, self.pass_ticket)
        params = {
            'BaseRequest': self.BaseRequest,
            'SyncKey': self.SyncKey,
            'rr': get_js_r()
        }
        dic = post(url, params)
        if not dic or dic['BaseResponse']['Ret'] != 0:
            logger.error(dic)
            return False

        self.SyncKey = dic['SyncKey']
        self.synckey = self.get_formate_sync_check_key(dic['SyncCheckKey'])
        return dic

    def get_formate_sync_check_key(self, SyncCheckKey):
        return '|'.join([
            str(keyVal['Key']) + '_' + str(keyVal['Val'])
            for keyVal in SyncCheckKey['List']
        ])


def get_wx_uri(base_uri):
    for indexUrl, detailedUrl in (
            ("wx2.qq.com", ("file.wx2.qq.com", "webpush.wx2.qq.com")),
            ("wx8.qq.com", ("file.wx8.qq.com", "webpush.wx8.qq.com")),
            ("qq.com", ("file.wx.qq.com", "webpush.wx.qq.com")), (
                    "web2.wechat.com",
                    ("file.web2.wechat.com", "webpush.web2.wechat.com")),
            ("wechat.com", ("file.web.wechat.com", "webpush.web.wechat.com"))):

        if indexUrl in base_uri:
            file_uri, sync_uri = detailedUrl
            break
    else:
        file_uri = sync_uri = base_uri

    return file_uri, sync_uri
